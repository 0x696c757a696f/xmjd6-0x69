# a-Shell 免费方案：iOS 快捷指令合并 xmjd6 自造词

适用于 iOS 16 或更新版本、a-Shell 和当前 `iOS_词库合并.py`。

## 准备文件

从 App Store 安装 a-Shell，并把下面两个文件放到 a-Shell 可以访问的同一目录，例如 `~/Documents/xmjd6-zzc/`：

- `iOS_词库合并.py`
- `Mac_词库合并`

也可以保留在方案目录的 `zzc/` 中，只要 a-Shell 能访问。

## 首次配置

在 a-Shell 进入脚本目录，然后用 `pickFolder` 选择最终要写入的方案目录：

```sh
cd ~/Documents/xmjd6-zzc
pickFolder
pwd
```

记住 `pwd` 显示的最终目录，再回到脚本目录保存配置：

```sh
root=$(pwd)
cd ~/Documents/xmjd6-zzc
python3 iOS_词库合并.py --root "$root" --default-state
```

目录选择规则：

- 使用 iCloud：选择 iCloud 中的 `RimeUserData` 或其中的 xmjd6 方案目录。
- 不使用 iCloud：选择输入法应用文件中的 `RimeUserData` 或 xmjd6 方案目录。
- 若选中 `RimeUserData`，脚本只向下查找一级；只有一个方案时自动进入，多个方案时应直接选具体方案目录。
- `--default-state` 让 `zzc_state/` 和正式词库保持在同一方案目录。

## 日常运行与快捷指令

日常命令：

```sh
cd ~/Documents/xmjd6-zzc
python3 iOS_词库合并.py
```

在“快捷指令”App 中添加 a-Shell 的“运行命令”，选择 `In App`，命令填写：

```sh
cd ~/Documents/xmjd6-zzc && python3 iOS_词库合并.py; open shortcuts://
```

若没有 a-Shell 原生动作，可用“打开 URL”运行：

```text
a-shell://?command=cd%20~/Documents/xmjd6-zzc%20%26%26%20python3%20iOS_%E8%AF%8D%E5%BA%93%E5%90%88%E5%B9%B6.py
```

更换目录时加 `--reset-config` 重新配置，或删除脚本旁的 `ios_zzc_merge_config.json`。

不要把正式词库放在 iCloud、却把 `zzc_state` 放在 a-Shell 本地，也不要反向混用。脚本目录只是程序位置，不应当作数据目录。
