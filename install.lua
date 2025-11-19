local M = {}

function M.xmjd6(ctx)
    ctx:register_schema("xmjd6")
    ctx:download_file("rime.lua", "rime.lua")
    ctx:download_file("xmjd6.symbols.yaml", "xmjd6.symbols.yaml")
    ctx:download_dir("xmjd6", "xmjd6")
    -- ctx:download_dir("opencc", "opencc") 
    local dict_files = {
        "xmjd6.extended.dict.yaml",
        "xmjd6.cx.dict.yaml",    
        "xmjd6.gbk.dict.yaml",
        "liangfen.dict.yaml",
        "xmjd6.Y.dict.yaml",
        "xmjd6.Z.dict.yaml",
        "xmjd6.W.dict.yaml",
    }

    for _, file in ipairs(dict_files) do
        ctx:download_file(file, file)
    end

    local dep_schemas = {
        "pinyin_simp.schema.yaml",
        "pinyin_simp.dict.yaml"
    }
    for _, file in ipairs(dep_schemas) do
        ctx:download_file(file, file)
    end
end

return M
