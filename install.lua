local M = {}

function M.xmjd6(ctx)

    ctx:download_file("xmjd6.schema.yaml", "xmjd6.schema.yaml")
    

    ctx:download_dir("lua", "lua")


    ctx:download_dir("opencc", "opencc")


    local dicts = {
       "xmjd6.extended.dict.yaml", 
       "xmjd6.cx.dict.yaml",
       "xmjd6.gbk.dict.yaml",
       "liangfen.dict.yaml",
       "xmjd6.Y.dict.yaml",
       "xmjd6.Z.dict.yaml",
       "xmjd6.W.dict.yaml",
       "pinyin_simp.dict.yaml",
       "pinyin_simp.schema.yaml"
    }
    for _, d in ipairs(dicts) do
       ctx:download_file(d, d)
    end
    
    ctx:download_file("xmjd6.symbols.yaml", "xmjd6.symbols.yaml")

end

return M
