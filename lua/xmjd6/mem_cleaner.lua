-- 可释放缓存的全局注册表。
-- 各模块注册清理回调，在输入法实例结束或平台主动请求时统一释放缓存。

local M = { releasers = {} }

function M.register(fn)
    if type(fn) == "function" then
        M.releasers[fn] = true
    end
    return fn
end

function M.unregister(fn)
    if fn then
        M.releasers[fn] = nil
    end
end

function M.release_all()
    for fn in pairs(M.releasers) do
        pcall(fn)
    end
    collectgarbage("collect")
end

return M
