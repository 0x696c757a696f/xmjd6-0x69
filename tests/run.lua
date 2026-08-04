package.path = table.concat({
    "./lua/?.lua",
    "./lua/?/init.lua",
    package.path,
}, ";")

local tests = {}

local function test(name, fn)
    tests[#tests + 1] = { name = name, fn = fn }
end

local function assert_equal(actual, expected, message)
    if actual ~= expected then
        error((message or "values differ")
            .. ": expected " .. tostring(expected)
            .. ", got " .. tostring(actual), 2)
    end
end

local function unload(prefix)
    for name in pairs(package.loaded) do
        if name:sub(1, #prefix) == prefix then
            package.loaded[name] = nil
        end
    end
end

local function candidate(candidate_type, start_pos, end_pos, text, comment)
    return {
        type = candidate_type,
        start = start_pos,
        _end = end_pos,
        text = text,
        comment = comment or "",
    }
end

local function base_env(options)
    options = options or {}
    local properties = {}
    local context = {
        input = options.input or "",
        get_option = function(_, name)
            if name == "jisuanqi" then return true end
            if name == "completion" then return options.completion == true end
            return false
        end,
        get_property = function(_, name)
            return properties[name] or ""
        end,
        set_property = function(_, name, value)
            properties[name] = value
        end,
    }
    local config = {
        get_bool = function(_, path)
            if path == "translator/enable_sentence" then return false end
            return nil
        end,
        get_int = function() return nil end,
        get_string = function() return nil end,
        get_list = function() return nil end,
    }
    return {
        engine = {
            context = context,
            schema = {
                schema_id = "xmjd6",
                config = config,
            },
        },
    }
end

test("lazy translator loads namespaced calculator, time and history modules", function()
    unload("xmjd6")
    _G.Candidate = candidate
    local yielded = {}
    _G.yield = function(cand) yielded[#yielded + 1] = cand end

    local translator = require("xmjd6.xmjd6_core")
    local env = base_env()
    local seg = { start = 0, _end = 4 }

    translator.func("=1+1", seg, env)
    assert_equal(tostring(yielded[2] and yielded[2].text), "2", "calculator result")

    yielded = {}
    translator.func("rq", seg, env)
    if #yielded == 0 then error("time translator yielded no candidates") end

    translator.func("i", seg, env)

    unload("xmjd6")
    local saved_debug = debug
    _G.debug = nil
    local ok, err = pcall(function()
        local fallback = require("xmjd6.xmjd6_core")
        local fallback_env = base_env()
        fallback_env.engine.schema.schema_id = "custom_schema"
        fallback.func("rq", seg, fallback_env)
    end)
    _G.debug = saved_debug
    if not ok then error("loader fallback failed: " .. tostring(err)) end
end)

test("ZZC candidates stay ahead of ordinary multi-character candidates", function()
    unload("xmjd6.xmjd6_completion")
    package.loaded["xmjd6.zzc.xmjd6_zzc_core"] = {
        zzc_cover_for_input = function() return nil end,
        zzc_completion_rows_for_prefix = function() return nil end,
    }
    _G.Candidate = candidate

    local yielded = {}
    _G.yield = function(cand) yielded[#yielded + 1] = cand end
    local completion = require("xmjd6.xmjd6_completion")
    local env = base_env({ input = "adfytoceek" })
    completion.init(env)

    local candidates = {
        candidate("phrase", 0, 10, "普通多字词", "词组"),
        candidate("zzc_code_choice", 0, 10, "☯造词组合", "编码"),
    }
    local input = {
        iter = function()
            local index = 0
            return function()
                index = index + 1
                return candidates[index]
            end
        end,
    }

    completion.func(input, env)
    assert_equal(yielded[1] and yielded[1].type, "zzc_code_choice", "first candidate type")
    assert_equal(yielded[2] and yielded[2].type, "phrase", "second candidate type")
    completion.fini(env)
end)

test("ZZC state preserves an empty replacement buffer placeholder", function()
    unload("xmjd6.zzc.xmjd6_zzc_state")
    local state_module = require("xmjd6.zzc.xmjd6_zzc_state")
    local state = state_module.new()
    state.active = true
    state.stage = "collect"
    state.mode = "replace"
    state.target_code = "abcd"
    state.display_word = "原词"

    local properties = {}
    local ctx = {
        set_property = function(_, name, value) properties[name] = value end,
        get_property = function(_, name) return properties[name] or "" end,
    }
    local core = {
        set_state_items = function() end,
        set_current_stage = function() end,
        buffer_word = function() return "" end,
        serialize_items = function() return "" end,
        deserialize_items = function() return {} end,
        items_from_text = function(text) return { { text = text } } end,
    }

    state_module.sync(ctx, state, core)
    assert_equal(properties[state_module.fields.word], "", "replacement placeholder word")

    properties[state_module.fields.word] = "原词"
    properties[state_module.fields.display] = "原词"
    properties[state_module.fields.items] = ""
    local restored = state_module.new()
    if not state_module.restore_from_context(ctx, restored, core) then
        error("replacement state was not restored")
    end
    assert_equal(#restored.items, 0, "replacement placeholder items")
end)

test("typing statistics uses the shared cache registry", function()
    unload("xmjd6.typing_stats")
    unload("xmjd6.common.xmjd6_cache_registry")
    local registry = require("xmjd6.common.xmjd6_cache_registry")
    require("xmjd6.typing_stats")
    local found = false
    for _, name in ipairs(registry.names()) do
        if name == "typing_stats" then found = true end
    end
    if not found then error("typing_stats cleaner was not registered") end
end)

local failed = 0
for _, item in ipairs(tests) do
    local ok, err = xpcall(item.fn, debug.traceback)
    if ok then
        io.write("PASS ", item.name, "\n")
    else
        failed = failed + 1
        io.stderr:write("FAIL ", item.name, "\n", err, "\n")
    end
end

if failed > 0 then
    os.exit(1)
end

io.write(string.format("PASS %d tests\n", #tests))
