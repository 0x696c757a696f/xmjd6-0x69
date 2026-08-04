-- 打字统计：按天记录汉字数、击键数、上屏次数、退格数和活跃打字时长。
-- 输入 =tj 查看今日、近 7 天和累计统计。
-- 数据保存在 user_data_dir/typing_stats.txt，每天一行，最多保留两年。

local mem_cleaner = require("xmjd6.mem_cleaner")

local M = {}

local kNoop = 2
local STATS_FILE = "typing_stats.txt"
local MAX_DAYS = 730
local FLUSH_EVERY = 20
local FLUSH_IDLE = 60
local IDLE_GAP = 5
local MIN_SPEED_SECS = 30
local XK_BACKSPACE = 0xff08

local function state()
    if not _G.__typing_stats then
        _G.__typing_stats = {
            loaded = false,
            history = nil,
            today = nil,
            dirty = 0,
            last_flush = 0,
            last_key_time = nil,
        }
    end
    return _G.__typing_stats
end

local function stats_path()
    return rime_api.get_user_data_dir() .. "/" .. STATS_FILE
end

local function today_str()
    return os.date("%Y-%m-%d")
end

local function new_row(day)
    -- sent_chars 是旧格式保留列；新版本使用 active_secs/timed_chars 计算速度。
    return {
        day = day,
        chars = 0,
        keys = 0,
        commits = 0,
        backspaces = 0,
        sent_chars = 0,
        active_secs = 0,
        timed_chars = 0,
    }
end

local function load(st)
    if st.loaded then return end

    st.history = {}
    st.today = nil
    local today = today_str()
    local file = io.open(stats_path(), "r")
    if file then
        for line in file:lines() do
            local day, chars, keys, commits, backspaces, sent_chars, active_secs, timed_chars =
                line:match("^(%d%d%d%d%-%d%d%-%d%d)\t(%d+)\t(%d+)\t(%d+)\t(%d+)\t(%d+)\t?(%d*)\t?(%d*)")
            if day then
                -- 旧 6/7 列记录没有成对的计速字数，不能用于速度计算。
                local timed = tonumber(timed_chars)
                local row = {
                    day = day,
                    chars = tonumber(chars) or 0,
                    keys = tonumber(keys) or 0,
                    commits = tonumber(commits) or 0,
                    backspaces = tonumber(backspaces) or 0,
                    sent_chars = tonumber(sent_chars) or 0,
                    active_secs = timed and (tonumber(active_secs) or 0) or 0,
                    timed_chars = timed or 0,
                }
                if day == today then
                    st.today = row
                else
                    st.history[#st.history + 1] = row
                end
            end
        end
        file:close()
    end

    st.today = st.today or new_row(today)
    st.loaded = true
end

local function flush(st)
    if not st.loaded then return end

    while #st.history >= MAX_DAYS do
        table.remove(st.history, 1)
    end

    local file = io.open(stats_path(), "w")
    if not file then return end

    local function write_row(row)
        file:write(
            row.day, "\t",
            row.chars, "\t",
            row.keys, "\t",
            row.commits, "\t",
            row.backspaces, "\t",
            row.sent_chars or 0, "\t",
            row.active_secs or 0, "\t",
            row.timed_chars or 0, "\n"
        )
    end

    for _, row in ipairs(st.history) do
        write_row(row)
    end
    write_row(st.today)
    file:close()

    st.dirty = 0
    st.last_flush = os.time()
end

local function roll_day(st)
    local today = today_str()
    if st.today.day ~= today then
        st.history[#st.history + 1] = st.today
        st.today = new_row(today)
        st.last_key_time = nil
        flush(st)
    end
end

local function count_han(text)
    local count = 0
    local ok = pcall(function()
        for _, codepoint in utf8.codes(text) do
            if (codepoint >= 0x4e00 and codepoint <= 0x9fff)
                or (codepoint >= 0x3400 and codepoint <= 0x4dbf) then
                count = count + 1
            end
        end
    end)
    return ok and count or 0
end

local function is_ascii_mode(env)
    local context = env and env.engine and env.engine.context
    if not context then return false end
    local ok, value = pcall(function()
        return context:get_option("ascii_mode")
    end)
    return ok and value == true
end

-- 计键 processor 始终透传；必须注册在所有可能吞键的 processor 之前。
function M.processor(key, env)
    if not key or key:release() or key:ctrl() or key:alt() or key:super() then
        return kNoop
    end
    if is_ascii_mode(env) then return kNoop end

    local code = tonumber(key.keycode or 0) or 0
    local is_backspace = code == XK_BACKSPACE
    if not is_backspace and not (code >= 0x20 and code < 0x7f) then
        return kNoop
    end

    local st = state()
    load(st)
    roll_day(st)

    local now = os.time()
    local gap = st.last_key_time and (now - st.last_key_time) or -1
    if gap >= 0 and gap <= IDLE_GAP then
        st.today.active_secs = st.today.active_secs + gap
    else
        st.today.active_secs = st.today.active_secs + 1
    end
    st.last_key_time = now

    if is_backspace then
        st.today.backspaces = st.today.backspaces + 1
    else
        st.today.keys = st.today.keys + 1
    end
    return kNoop
end

function M.on_commit(context)
    local st = state()
    if not st.loaded then return end

    local text = ""
    local ok, value = pcall(function()
        return context:get_commit_text()
    end)
    if ok then text = tostring(value or "") end
    if text == "" then return end

    roll_day(st)
    local han = count_han(text)
    st.today.commits = st.today.commits + 1
    st.today.chars = st.today.chars + han
    st.today.timed_chars = (st.today.timed_chars or 0) + han

    st.dirty = st.dirty + 1
    if st.dirty >= FLUSH_EVERY
        or os.time() - (st.last_flush or 0) >= FLUSH_IDLE then
        flush(st)
    end
end

local function release_stats_cache()
    local st = state()
    flush(st)
    st.loaded = false
    st.history = nil
    st.today = nil
    st.last_key_time = nil
end

function M.init_processor(env)
    local context = env and env.engine and env.engine.context
    if context and context.commit_notifier then
        env.commit_connection = context.commit_notifier:connect(function(current_context)
            pcall(M.on_commit, current_context)
        end)
    end

    -- env 级回调必须在 fini 注销，避免重新部署后持有失效的 env/closure。
    env.mem_release = mem_cleaner.register(release_stats_cache)
end

function M.fini_processor(env)
    if env.commit_connection then
        pcall(function()
            env.commit_connection:disconnect()
        end)
        env.commit_connection = nil
    end
    mem_cleaner.unregister(env.mem_release)
    env.mem_release = nil
    flush(state())
end

local function sum_rows(rows, from_day)
    local total = new_row("")
    for _, row in ipairs(rows) do
        if not from_day or row.day >= from_day then
            total.chars = total.chars + row.chars
            total.keys = total.keys + row.keys
            total.commits = total.commits + row.commits
            total.backspaces = total.backspaces + row.backspaces
            total.active_secs = total.active_secs + (row.active_secs or 0)
            total.timed_chars = total.timed_chars + (row.timed_chars or 0)
        end
    end
    return total
end

local function code_length(row)
    if row.chars == 0 then return "-" end
    return string.format("%.2f", row.keys / row.chars)
end

local function speed(row)
    local seconds = row.active_secs or 0
    local timed_chars = row.timed_chars or 0
    if seconds < MIN_SPEED_SECS or timed_chars == 0 then return "-" end

    local value = string.format(
        "约%d字/分",
        math.floor(timed_chars / seconds * 60 + 0.5)
    )
    if timed_chars < row.chars then
        value = value .. "（可能不准）"
    end
    return value
end

function M.translator(input, segment)
    if input ~= "=tj" then return end

    local st = state()
    load(st)
    roll_day(st)

    local all = {}
    for _, row in ipairs(st.history) do
        all[#all + 1] = row
    end
    all[#all + 1] = st.today

    local week_from = os.date("%Y-%m-%d", os.time() - 6 * 86400)
    local rows = {
        { "今日", st.today },
        { "近7天", sum_rows(all, week_from) },
        { "累计", sum_rows(all, nil) },
    }
    local first_day = st.history[1] and st.history[1].day or st.today.day

    for index, item in ipairs(rows) do
        local label, row = item[1], item[2]
        local text = string.format(
            "%s %d 字 · 码长 %s",
            label,
            row.chars,
            code_length(row)
        )
        local comment = string.format(
            "击键 %d · 上屏 %d · 退格 %d · 速度 %s",
            row.keys,
            row.commits,
            row.backspaces,
            speed(row)
        )
        if label == "累计" then
            comment = comment .. " · 自 " .. first_day
        end

        local candidate = Candidate(
            "stats",
            segment.start,
            segment._end,
            text,
            comment
        )
        candidate.quality = 600000 - index
        yield(candidate)
    end
end

return M
