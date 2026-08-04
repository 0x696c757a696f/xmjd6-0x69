# Pythonista：iOS 快捷指令合并 XMJD6 自造词

适用于 iOS 16 或更新版本、Pythonista 和当前 `iOS_词库合并.py`。

## 文件与首次运行

把 `iOS_词库合并.py` 和 `Mac_词库合并` 放在 Pythonista 同一目录，或保留在方案目录的 `zzc/` 中。前者负责 iOS 路径配置，真正合并仍由后者执行。

第一次在 Pythonista 内直接运行 `iOS_词库合并.py`：

- 使用 iCloud：选择 iCloud 中的 `RimeUserData` 或 XMJD6 方案目录。
- 不使用 iCloud：选择输入法应用文件中的 `RimeUserData` 或 XMJD6 方案目录。
- 若选择 `RimeUserData`，只有一个方案目录时会自动进入；多个方案时需直接选择具体方案目录。
- `zzc_state` 默认使用最终方案目录下的 `zzc_state/`，一般不要改到别处。

配置保存在脚本旁的 `ios_zzc_merge_config.json`，后续无需重复选择。

## 用 URL Scheme 建立快捷指令

1. 新建快捷指令，添加“URL”动作。
2. 填入：

   ```text
   pythonista3://iOS_%E8%AF%8D%E5%BA%93%E5%90%88%E5%B9%B6.py?action=run
   ```

3. 添加“打开 URL”动作并保存。

也可以使用 Pythonista 的 `Run Pythonista Script` 动作，选择 `iOS_词库合并.py`，开启 `Run in Pythonista`；如有需要再开启自动返回快捷指令。

要重新选择目录，可在 Pythonista 中用 `iOS_词库合并.py --configure`，或删除 `ios_zzc_merge_config.json` 后重新运行。

正式词库和 `zzc_state` 必须位于同一棵 iCloud 或应用文件目录中。不要把其中一项留在 Pythonista 本地；脚本所在目录只用于找合并核心和保存配置，不代表最终数据路径。
