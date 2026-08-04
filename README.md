# 星猫键道6（xmjd6-0x69）

星猫键道6是基于星空键道6.2持续整理和扩展的 Rime 音形输入方案，兼顾常用词短码、单字精确定位、生僻字反查和可维护的大型词库。本方案已获得相关授权，适用于 Windows、macOS、Linux、Android 和 iOS 上支持 Rime/Lua 的输入法前端。

- 当前维护仓库：[0x696c757a696f/xmjd6-0x69](https://github.com/0x696c757a696f/xmjd6-0x69)
- 发行包：[Releases](https://github.com/0x696c757a696f/xmjd6-0x69/releases/)
- 上游方案：[hugh7007/xmjd6-rere](https://github.com/hugh7007/xmjd6-rere)
- 使用笔记：[星猫键道6飞书笔记](https://hu0w1jn4xq.feishu.cn/docx/ZgQ8deGPlozhWCxOyeucBvHJnPe)

## 主要特点

- 约 121 万条内置码表记录，覆盖单字、常用词、扩展词、Catholicism 专题词和英文词汇。
- 保留键道6的短码、顶功、飞键和首笔辅助码规则，常用词优先使用较短编码。
- `i` 键直接进入英文输入，不需要切换到单独的英文方案。
- `u`、`v`、`o` 分别提供全拼、二分和 GBK/生僻字入口。
- 支持自造词、逐码补全、630 提示、计算器、日期时间、打字统计、Emoji、简繁和火星文转换。
- Lua 文件集中在 `lua/xmjd6/`，OpenCC 数据集中在 `opencc/xmjd6/`，避免污染用户目录的公共命名空间。
- 上游词库使用 Git commit 锁定，可增量检测、确定性重建、定期验证并自动提交更新 PR。

## 快速安装

### 标准 Rime 安装

1. 下载最新版 [`xmjd6.zip`](https://github.com/0x696c757a696f/xmjd6-0x69/releases/latest/download/xmjd6.zip)。
2. 解压到 Rime 用户文件夹；保留压缩包内的目录结构。
3. 重新部署 Rime。
4. 在方案选单中选择“星猫键道”。

本方案包含 Lua 处理器，所用 Rime 前端需要带有 `librime-lua` 支持。建议使用 librime 1.9.0 或更新版本。

| 平台 | 常见前端 | 默认用户目录 |
| --- | --- | --- |
| Windows | [小狼毫 Weasel](https://github.com/rime/weasel/releases/latest) | `%APPDATA%\Rime` |
| macOS | [鼠须管 Squirrel](https://github.com/rime/squirrel/releases/latest) | `~/Library/Rime` |
| Linux | [Fcitx5](https://github.com/fcitx/fcitx5) + `fcitx5-rime` + `librime-lua` | `~/.local/share/fcitx5/rime/` |
| Android | [同文 Trime](https://github.com/osfans/trime/releases/latest) | `/storage/emulated/0/rime/` |
| Android | [Fcitx5 for Android](https://github.com/fcitx5-android/fcitx5-android) | 应用数据中的 `data/rime/` |
| iOS | [仓输入法](https://apps.apple.com/app/id6446617683)、[元书输入法](https://apps.apple.com/app/id6744464701) | 使用应用内方案导入功能 |

部署失败或更新后仍显示旧候选时，请先确认文件放在正确的用户目录，再从输入法菜单执行一次“重新部署”。

### 东风破（plum）安装与更新

仓库根目录提供了 `recipe.yaml`，可由东风破直接安装或更新。Linux、macOS 以及带 Bash 的环境可执行：

```bash
curl -fsSL https://raw.githubusercontent.com/rime/plum/master/rime-install | bash -s -- 0x696c757a696f/xmjd6-0x69
```

Windows 可从小狼毫菜单打开“输入法设定／获取更多输入方案”，输入：

```text
0x696c757a696f/xmjd6-0x69
```

也可以在已经安装东风破的命令行中运行 `rime-install 0x696c757a696f/xmjd6-0x69`。安装完成后仍需重新部署。配方只复制 Rime 运行所需的 YAML、`lua/xmjd6/`、`opencc/xmjd6/` 和必要的自造词部件表；它通过东风破补丁把 `xmjd6` 安全加入现有方案列表，不直接覆盖用户的 `*.custom.yaml`。仓库测试、构建脚本、EXE、`xmjd6_user.txt`、`*.userdb` 和自造词运行记录都不会被安装或覆盖。

### 中州韵助手（rimetool）兼容性

本方案已补齐中州韵助手用于识别和编辑方案的主要结构：`default.yaml` 与 `default.custom.yaml` 都列出 `xmjd6`，schema 内有方案名、完整开关状态及显式 `reset`、本方案快捷键和 `menu/page_size`；各词典也都有明确的 `text`、`code` 等列和实际编码。

可以用中州韵助手调整 schema、候选数、开关和客户端外观。不过，本仓库为了让宗派词库及大型词库仍可人工审阅，在部分码表正文保留了分类注释；中州韵助手的兼容约定不建议正文注释，因此不建议在其中对这些大型码表执行“全库重写”。正常浏览、Rime 编译和输入不受影响。`melt_eng`、`custom_phrase` 是雾凇方案专用的节点，本方案的英文入口和用户词功能实现不同，不添加无效的同名占位配置。

### 便携发行包

- Windows 小小输入法：[yong-xmjd6-full.zip](https://github.com/0x696c757a696f/xmjd6-0x69/releases/latest/download/yong-xmjd6-full.zip)
- 玉兔毫：[Rabbit-xmjd6.zip](https://github.com/0x696c757a696f/xmjd6-0x69/releases/latest/download/Rabbit-xmjd6.zip)

玉兔毫便携版建议解压到不含空格的路径。小小输入法版默认使用 `Ctrl + Space` 激活。

## 键道6编码概要

键道6以音码为主体，以首笔画作为辅助筛选码：

| 笔画 | 横 | 竖 | 撇 | 捺/点 | 折/钩 |
| --- | --- | --- | --- | --- | --- |
| 按键 | `v` | `i` | `u` | `o` | `a` |

词组编码规则以当前生成器和单字表为准：

- 两字词：两个字各取两位音码形成四码；需要区分时，第 5、6 位依次取第一、第二个字的首笔画。
- 三字词：三个字各取音码首键形成三码；第 4、5、6 位依次取三个字的首笔画。
- 四字及以上：取前三字和末字的音码首键形成四码；需要区分时再取前两个字的首笔画。
- 同音词按本地词库、来源优先级和词频排序；常用词先占短码，较低优先级词追加笔画码。

例如：

```text
赞主曲      zqquo
婚姻圣召    hyefa
```

这里的 `i` 同时也是“竖”的辅助码；只有当它位于输入开头时，才作为英文入口。

## 如何使用

### 各客户端安装、导入与更新

所有标准 Rime 客户端都使用同一份 [`xmjd6.zip`](https://github.com/0x696c757a696f/xmjd6-0x69/releases/latest/download/xmjd6.zip)。区别只在用户文件夹位置和客户端的导入方式：

| 平台 | 推荐客户端 | 安装方式 | 更新后必须做的操作 |
| --- | --- | --- | --- |
| Windows | 小狼毫、玉兔毫、小小输入法 | 解压到用户目录，或下载对应便携包 | 重新部署；便携版按说明启动 |
| macOS | 鼠须管、Fcitx5 macOS | 解压到对应 Rime 用户目录 | 重新部署 |
| Linux | Fcitx5 + Rime + librime-lua | 安装组件后解压到 Fcitx5 Rime 目录 | 重启 Fcitx5 并重新部署 |
| Android | 同文、Fcitx5 for Android | 通过应用配置管理或系统文件选择器导入 | 在应用内重新部署 |
| iOS | 元书、仓输入法 | 使用应用内下载方案或在线方案导入 | 切换到新方案目录并重新部署 |

无论使用哪个客户端，都不要只复制根目录的 YAML 文件：`lua/xmjd6/` 和 `opencc/xmjd6/` 也必须保持原目录结构一起导入，否则顶功、自造词、英文、Emoji 和简繁转换可能不完整。

#### Windows

**小狼毫 Weasel**

1. 安装[小狼毫正式版](https://github.com/rime/weasel/releases/latest)或[小狼毫测试版](https://github.com/rime/weasel/releases/tag/latest)。也可使用[水龙月 Fork 版](https://github.com/Techince/weasel/releases/latest)；从原版切换到 Fork 版时，建议先卸载原版并重启系统。
2. 从 Release 下载 `xmjd6.zip`，解压后把压缩包内的文件和目录复制到 `%APPDATA%\Rime`。
3. 在小狼毫菜单中执行“重新部署”。
4. 打开方案选单，选择“星猫键道”。
5. 更新方案时覆盖同名方案文件即可；个人词汇应放在 `xmjd6.user.dict.yaml`，个人配置写在 `*.custom.yaml`，然后重新部署。

**小小输入法便携版**

1. 下载 [`yong-xmjd6-full.zip`](https://github.com/0x696c757a696f/xmjd6-0x69/releases/latest/download/yong-xmjd6-full.zip)。
2. 解压后运行包内的小小输入法，不需要另外导入 Rime 方案。
3. 默认使用 `Ctrl + Space` 激活输入法。
4. `yong-xmjd6.zip` 只包含配置和码表，适合已经安装小小输入法的用户；`yong-xmjd6-full.zip` 才包含完整便携程序。

**玉兔毫 Rabbit**

1. 下载 [`Rabbit-xmjd6.zip`](https://github.com/0x696c757a696f/xmjd6-0x69/releases/latest/download/Rabbit-xmjd6.zip)。
2. 解压到路径中不含空格的目录。
3. 运行玉兔毫并选择星猫键道；该包已经带入方案文件，不需要再复制 `xmjd6.zip`。

#### macOS

**鼠须管 Squirrel**

1. 安装[鼠须管正式版](https://github.com/rime/squirrel/releases/latest)或[测试版](https://github.com/rime/squirrel/releases/tag/latest)。
2. 下载并解压 `xmjd6.zip`，把全部内容复制到 `~/Library/Rime`。
3. 从鼠须管菜单执行“重新部署”，再在方案选单中选择“星猫键道”。

**Fcitx5 macOS**

1. 安装[小企鹅输入法 macOS 版（中州韵版）](https://github.com/fcitx-contrib/fcitx5-macos-installer/blob/master/README.zh-CN.md)。
2. 把方案完整复制到 `~/.local/share/fcitx5/rime/`。
3. 重启 Fcitx5 或重新部署 Rime。

#### Linux：Fcitx5 + Rime

需要同时安装 Fcitx5、Rime 插件和 Lua 支持。不同发行版的软件包名称可能略有差异，下面是常见安装命令：

| 发行版 | 安装命令或说明 |
| --- | --- |
| Arch / Manjaro / EndeavourOS | `sudo pacman -S fcitx5-im fcitx5-rime fcitx5-configtool librime-lua` |
| Ubuntu / Debian / Linux Mint | `sudo apt install fcitx5 fcitx5-rime librime-lua` |
| Fedora | `sudo dnf install fcitx5 fcitx5-rime librime-lua` |
| RHEL / AlmaLinux / Rocky Linux | 先启用 EPEL；RHEL/Rocky 9 再启用 CRB，然后安装 `fcitx5 fcitx5-rime librime-lua` |
| Deepin / UOS | 如仍使用 Fcitx4，先卸载旧组件，再安装 `fcitx5 fcitx5-rime librime-lua` |
| Flatpak | `flatpak install org.fcitx.Fcitx5 org.fcitx.Fcitx5.Addon.Rime` |

安装方案：

1. 将 `xmjd6.zip` 完整解压到 `~/.local/share/fcitx5/rime/`。
2. Flatpak 版通常使用 `~/.var/app/org.fcitx.Fcitx5/data/fcitx5/rime/`。
3. 打开 Fcitx5 配置工具，添加“中州韵”或 Rime 输入法。
4. 重启 Fcitx5，并从 Rime 菜单执行重新部署。

桌面环境配置需要按实际会话选择：

**KDE Plasma / Wayland**

1. 打开“系统设置 → 虚拟键盘”，选择 Fcitx 5。
2. 可在 `/etc/environment` 中补充：

   ```text
   XMODIFIERS=@im=fcitx
   GLFW_IM_MODULE=fcitx
   CLUTTER_IM_MODULE=fcitx
   ECORE_IMF_MODULE=fcitx
   QT_IM_MODULES="wayland;fcitx;ibus"
   ```

3. Wayland 会话下不建议通过任务栏菜单反复“重启”输入法；修改环境变量后注销并重新登录更可靠。

**GNOME / Budgie / Debian 系桌面**

1. 运行 `im-config -n fcitx5`。
2. GNOME/Budgie 如未正确使用 Fcitx5，可运行：

   ```bash
   gsettings set org.gnome.settings-daemon.plugins.xsettings overrides "{'Gtk/IMModule':<'fcitx'>}"
   ```

3. 必要时在 `/etc/environment` 中加入：

   ```text
   GTK_IM_MODULE=fcitx
   QT_IM_MODULE=fcitx
   XMODIFIERS=@im=fcitx
   SDL_IM_MODULE=fcitx
   GLFW_IM_MODULE=fcitx
   CLUTTER_IM_MODULE=fcitx
   ECORE_IMF_MODULE=fcitx
   QT_IM_MODULES="wayland;fcitx;ibus"
   ```

**Xfce / LXQt / LXDE / MATE 等 X11 桌面**

1. 确认 Fcitx5 随桌面会话自动启动；LXQt 可在“会话设置 → 自动启动”中添加，其他桌面可在“会话和启动”中添加 `fcitx5`。
2. 在 `/etc/environment` 或用户级 `~/.xprofile` 中设置上面的输入法环境变量。

**i3wm / awesome / bspwm 等平铺窗口管理器**

在 `~/.xprofile` 中加入：

```bash
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
export SDL_IM_MODULE=fcitx
export GLFW_IM_MODULE=fcitx
export CLUTTER_IM_MODULE=fcitx
export ECORE_IMF_MODULE=fcitx
export QT_IM_MODULES="wayland;fcitx;ibus"
```

然后为窗口管理器添加自动启动：

| 窗口管理器 | 配置示例 |
| --- | --- |
| i3wm | 在 `~/.config/i3/config` 加入 `exec --no-startup-id fcitx5 -d` |
| awesome | 在 `~/.config/awesome/rc.lua` 加入 `awful.spawn.with_shell("fcitx5 -d")` |
| bspwm | 在 `~/.config/bspwm/bspwmrc` 加入 `fcitx5 -d &` |

**Electron / Chrome / VS Code**

- XWayland 模式通常最稳，不额外添加启动参数，让应用读取 `GTK_IM_MODULE` 或 `XMODIFIERS`。
- 必须使用原生 Wayland 时，KDE/KWin 可尝试：

  ```text
  --enable-features=UseOzonePlatform --ozone-platform=wayland --enable-wayland-ime --wayland-text-input-version=1
  ```

- GNOME 或其他桌面可尝试将最后一项改成 `--wayland-text-input-version=3`。

#### Android

**同文输入法 Trime**

1. 安装[同文输入法](https://github.com/osfans/trime/releases/latest)。
2. 在应用设置中打开“配置管理 → 用户文件夹”。
3. 先选择或初始化默认用户文件夹，再把 `xmjd6.zip` 的完整内容导入 `/storage/emulated/0/rime/`。
4. 返回配置管理执行部署，然后选择星猫键道。

**Fcitx5 for Android**

1. 安装[Fcitx5 for Android](https://github.com/fcitx5-android/fcitx5-android)及 Rime 插件；需要测试构建时可使用[主程序构建](https://jenkins.fcitx-im.org/job/android/job/fcitx5-android/)、[Rime 插件构建](https://jenkins.fcitx-im.org/job/android/job/fcitx5-android-plugin-rime/)和[更新器](https://jenkins.fcitx-im.org/job/android/job/fcitx5-android-updater/)。
2. 在小企鹅输入法中添加中州韵后，Rime 数据目录通常位于应用数据中的 `files/data/rime/`。
3. 推荐通过 Android 系统 DocumentsUI 管理文件：打开系统文件选择器，在侧边栏选择“小企鹅输入法5”，进入其数据目录后复制完整方案，不需要 root 或 ADB。
4. 返回应用重新部署 Rime。

#### iOS

**元书输入法**

1. 在“输入方案”中选择“下载方案”。
2. 使用以下任一地址：

   - 原始地址：<https://github.com/0x696c757a696f/xmjd6-0x69/releases/latest/download/xmjd6.zip>
   - 国内网络可用代理地址：<https://gh-proxy.com/https://github.com/0x696c757a696f/xmjd6-0x69/releases/latest/download/xmjd6.zip>

3. 下载完成后进入“方案目录切换”，在 `RimeUserData` 中选择刚导入的方案目录，点击右上角“打开”。
4. 后续更新时重新下载方案，再回到“方案目录切换”选择更新后的目录并重新部署。
5. 使用 iCloud 联动和自造词合并时，继续阅读[自造词使用教程](zzc/自造词使用教程.md)。

**仓输入法**

1. 安装[仓输入法](https://apps.apple.com/app/id6446617683)。
2. 使用应用内在线方案下载功能导入星猫键道。
3. 导入或更新后重新部署，并在应用中切换到对应方案。

#### 客户端更新与排错

| 现象 | 优先检查 |
| --- | --- |
| 方案选单里没有星猫键道 | `xmjd6.schema.yaml` 是否位于当前客户端真正使用的 Rime 用户目录；是否执行重新部署 |
| 中文能输入，但顶功、自造词或计算器失效 | `lua/xmjd6/` 是否完整，客户端是否带 `librime-lua` |
| 没有 Emoji、简繁或火星文 | `opencc/xmjd6/` 是否完整，功能开关是否开启，是否重新部署 |
| 更新后仍出现旧候选 | 确认没有导入到另一个用户目录；重新部署，必要时退出并重启客户端 |
| 个人词或设置被覆盖 | 个人内容应写入 `xmjd6.user.dict.yaml` 和 `*.custom.yaml`，不要直接改自动生成词典 |

### 基础输入与反查入口

| 想做什么 | 输入方式 | 示例或说明 |
| --- | --- | --- |
| 输入中文 | 直接输入键道6编码 | 空格上屏首选，数字选择对应候选；达到顶功条件时自动上屏 |
| 输入英文 | `i` + 英文字母 | `ihello` 的预编辑和候选均显示 `hello`，第二键开始隐藏入口 `i` |
| 用全拼查键道码 | `u` + 全拼 | 适合知道读音、忘记键道编码时使用；候选注释显示键道码 |
| 拆字查不会读的字 | `v` + 二分编码 | 使用二分反查定位汉字，并显示键道码 |
| 查繁体和生僻字 | `o` + 编码 | 进入 GBK/扩展单字词典；此入口不追加 Emoji |
| 输入快符 | `;` + 字母编码 | 开启“快符开”后使用；叶节点可直接上屏，行为可在 custom 文件中调整 |
| 使用计算器 | `=` + 表达式 | 未显示候选菜单时输入，例如 `=1+2*3`；有候选菜单时 `=` 是下一页 |
| 查看打字统计 | `=tj` | 显示累计字数、速度等本地统计信息 |
| 输入日期时间 | 输入 `rq` 等日期码 | 日期、时间候选由 Lua 动态生成 |
| 使用自造词 | `\` 进入指令模式 | 详见[自造词使用教程](zzc/自造词使用教程.md) |

`u`、`v`、`o` 是反查专用入口，不参与 Emoji 转换；普通中文编码才会在开启 Emoji 后附加表情候选。`i` 只有位于输入开头时才是英文入口，在中文编码的第 2～6 位仍按“竖”笔画码处理。

### 候选、翻页和方案切换

| 按键 | 条件 | 行为 |
| --- | --- | --- |
| `Space` | 有候选 | 上屏当前选中候选 |
| `1`～`5` | 有候选 | 选择本页对应序号；候选页大小默认是 5 |
| `Tab` | 有候选 | 选择第 2 个候选 |
| `-` | 有候选 | 上一页 |
| `=` | 有候选 | 下一页；没有候选时可作为计算器入口 |
| `F6` | 任意状态 | 切换到下一个输入方案 |
| `F7` | 任意状态 | 切换简体/繁体输出 |
| `Ctrl + \` | 任意状态 | 开启或关闭 Emoji 候选 |

### 功能开关和默认状态

重新部署后，方案选单中的开关状态由 [`xmjd6.custom.yaml`](xmjd6.custom.yaml) 控制：

| 开关 | 默认 | 作用 |
| --- | :---: | --- |
| 中文/英文 | 中文 | 整体 ASCII 模式；平时输英文无需切换，直接使用 `i` 入口 |
| 简体/繁體 | 简体 | OpenCC 简繁转换，也可按 `F7` 切换 |
| 简约/逐码展示 | 逐码展示 | 是否显示逐码补全候选 |
| 简约/表情展示 | 表情展示 | 是否给普通中文候选追加 Emoji |
| 快符关/快符开 | 快符开 | 是否启用 `;` 快符入口 |
| `;` 次选 | 关闭 | 是否把分号用作次选键；与快符习惯有关 |
| 计算关/计算开 | 计算开 | 是否启用 `=` 计算器和工具入口 |
| 空顶关/空顶开 | 关闭 | 是否启用空码顶功 |
| 简约/630提示 | 630提示 | 是否显示 630 规则辅助提示 |
| 地球文/火星文 | 地球文 | 是否启用火星文转换 |
| 半角/全角 | 半角 | 标点和字符宽度 |

默认启用键道顶功、逐码补全、Emoji、快符、计算器和 630 提示，默认关闭流式整句输入。Emoji 使用 Lua 懒加载：保留原有 txjx 映射，并追加 2,516 个来自 Rime-Ice 的不重复关键词，涵盖更多情绪别名、手势、人物、动物、食物、交通、旗帜和新版 Emoji。若 Emoji 没出现，依次确认“表情展示”已开启、输入的是普通中文编码而不是 `u/v/o` 反查、文件已完整复制到 `opencc/xmjd6/`，然后重新部署。

### 自造词指令速查

| 指令 | 作用 |
| --- | --- |
| `编码\自造词\` | 空码时新增；已有首选时替换首选，并把原词递归顺延到更长编码 |
| `\自造词3`～`\自造词6` | 指定 3～6 码造词，达到码长后自动结束 |
| `编码\+自造词\` | 追加为当前编码的重码候选 |
| `编码\-数字\` | 删除指定序号候选；省略数字时删除首选 |
| `编码\数字\` | 将指定序号候选置顶或前移 |
| `编码\<\` | 把当前候选前移一码，并递归整理被占用的编码 |
| `编码\++数字\` | 从可恢复候选列表恢复指定项 |
| `\--\` | 撤回最近一次尚未合并的自造词操作 |
| `\!!!\` | 清空全部尚未合并的自造词操作 |

输入法会在会话结束时把运行时操作安全追加到 `xmjd6.zzc.dict.yaml`；要永久整理进正式词库，再运行 `zzc/` 中对应平台的合并脚本。完整的保存、跨设备同步、合并和撤回流程见[自造词使用教程](zzc/自造词使用教程.md)和[合并脚本说明](zzc/README.md)。

Windows 用户可以在仓库根目录运行：

```powershell
python .\zzc\Windows_词库合并.py
```

没有 Python 时可以直接双击 `zzc/Win_词库合并.exe`，需要撤回最近一次合并时双击 `zzc/Win_撤回合并.exe`。两个 EXE 均由当前 xmjd6 共享 Python 核心构建；`package-main` 和正式 Release 会先在 Windows Runner 上使用 Python 3.14.6 + PyInstaller 6.21.0 重新构建并实际执行合并、撤回测试，再把通过测试的 CI 产物交给最终打包，避免发布旧版或损坏的可执行文件。构建和校验方法见[合并脚本说明](zzc/README.md#重新构建-windows-exe)。

## 英文输入

英文词典直接导入主词典，不需要 `xmjd6.en.schema.yaml`，也不需要切换方案。

```text
实际输入：ihello
预编辑区：hello
候选输出：hello
```

- 单独按下 `i` 时仍显示入口字符；继续输入后才隐藏开头的 `i`。
- 英文长码不会触发中文的 4～6 码顶功。
- 支持大小写输出和常见技术词别名，例如 `C++ → icpp`、`C# → icsharp`、`.NET → idotnet`。
- 英文编码统一为 `i[a-z]+`，生成时会排除与现有中文码冲突的条目。
- 英文词库来自 Rime-Ice 的 `en.dict.yaml` 与 `en_ext.dict.yaml`，当前生成 23,610 条记录。

## 词库组成

以下为 2026-08-04 版本的内置记录数；自造词和个人用户词库不计入统计。

| 词库 | 记录数 | 用途 |
| --- | ---: | --- |
| `xmjd6.danzi.dict.yaml` | 36,214 | 上游键道单字表 |
| `xmjd6.cizu.dict.yaml` | 191,398 | 本地基础词组 |
| `xmjd6.catholicism.dict.yaml` | 3,514 | Catholicism、礼仪、神学与东方礼词汇 |
| `xmjd6.protestantism.dict.yaml` | 219 | 新教信条、宗派神学及《和合本》词汇 |
| `xmjd6.orthodoxy.dict.yaml` | 88 | 东正教礼仪、圣像、灵修与教会制度专有词汇 |
| `xmjd6.oriental.dict.yaml` | 68 | 东方正统教会、合性论传统与成员教会专有词汇 |
| `xmjd6.assyrian.dict.yaml` | 71 | 东方亚述教会、东叙利亚礼与景教史专有词汇 |
| `xmjd6.core.dict.yaml` | 921 | 630 规则、快符和核心候选 |
| `xmjd6.fjcy.dict.yaml` | 514,033 | 附加扩展词组 |
| `xmjd6.ice.dict.yaml` | 373,902 | Rime-Ice 中文精简补充词库 |
| `xmjd6.en.dict.yaml` | 23,610 | Rime-Ice 英文词库 |
| **合计** | **1,144,038** | 不含动态自造词和个人词库 |

四个非天主教传统词库以具有宗派辨识度的信条、礼仪、制度、正式教会名称和历史术语为主体，不靠“祷告”“教会”“基督徒”等泛用词凑量。`xmjd6.protestantism` 另收经审核的《和合本》书卷名、人地名和固定译语，以《和合本》的“马太、约翰、使徒行传、启示录”等新教译名为准，不混入《思高本》译名。东正教、东方正统教会、东方亚述教会和东方礼天主教会分别维护，避免把相近的叙利亚礼、圣像或牧首制度词汇混错归属；东方正统部分不用不准确的“一性论”作为自称。多段人名使用间隔号显示，例如“马丁·路德”，编码时不计间隔号。核对来源和授权边界见 [`tools/christian_traditions_sources.md`](tools/christian_traditions_sources.md)。

这些专题词由 [`tools/christian_traditions_2026.txt`](tools/christian_traditions_2026.txt) 审核，生成器依次尝试键道六码的基础码和首笔辅助码。固定本地词典没有空闲合法码时通常不收录；专题词确定后再重建低优先级 `xmjd6.ice`，让 ICE 词移到更长的合法码或按既有重码预算淘汰。唯一例外是“哥林多后书”“帖撒罗尼迦后书”“雅各书”三卷《和合本》正式书名：前两组的前书与后书在标准规则下拥有完全相同的全部候选，后一卷的全部候选已被固定旧词占用，因此人工审核后使用最终六码并保持专题词优先。除此三项外，四个专题词库没有新增异词同码。

`xmjd6.ice` 定位为本地词库之后的精简补充库。同步过滤器不会直接删除 2～3 字词；它会排除上游低权重长尾、批量数字/年份模板、8 字以上 `ext` 整句及 12 字以上超长词，当前比未精简版本减少 71,144 条。药品名称是例外：片、胶囊、颗粒、注射液、口服液、滴眼液、喷雾剂等剂型词不会因词频低或名称过长被过滤，并在重码预算中优先保留。编码时短词优先占用基础码，长词和低频同码词尽量追加笔画码；随后再按照 `base → ext → others` 和上游权重排序。低优先级重码词会被删减，合并后的中文重码率不会高于同步前的本地基准；新增词在同一码下最多保留 8 个候选。这些过滤规则写在同步器中，因此以后拉取上游时不会重新混入。

### 词库加载顺序

[`xmjd6.extended.dict.yaml`](xmjd6.extended.dict.yaml) 控制词库导入。当前主要顺序为：

```text
user → zzc → danzi → cizu → catholicism → protestantism → orthodoxy → oriental → assyrian → core → fjcy → ice → en
```

本地词库优先于自动生成的上游词库。`xmjd6.user.dict.yaml` 权限最高，适合保存个人常用词；加入大量通用词前应优先考虑对应的专题或基础词库。

## 配置文件

| 文件 | 作用 |
| --- | --- |
| `xmjd6.schema.yaml` | 主方案、引擎、翻译器、反查和快捷键 |
| `xmjd6.custom.yaml` | 用户推荐修改的开关、候选数和流式输入配置 |
| `xmjd6.extended.dict.yaml` | 词库导入顺序与开关 |
| `default.custom.yaml` | 默认方案列表及全局选项 |
| `xmjd6.symbols.yaml` | 标点与符号 |
| `xmjd6.core.dict.yaml` | 630、快符和核心码表 |
| `xmjd6.user.dict.yaml` | 个人高优先级补充词库 |
| `lua/xmjd6/` | 方案 Lua 模块 |
| `opencc/xmjd6/` | 简繁、Emoji、火星文数据 |

修改 YAML 后必须重新部署。升级仓库时，个人配置尽量写入 `*.custom.yaml` 或 `xmjd6.user.dict.yaml`，不要直接修改自动生成的 `xmjd6.danzi`、`xmjd6.ice` 和 `xmjd6.en`。

### 流式输入

默认使用键道顶功。需要整句流式输入时，可在 `xmjd6.custom.yaml` 中启用：

```yaml
patch:
  translator/enable_sentence: true
  translator/enable_user_dict: true
```

启用 `enable_sentence` 后，中文顶功会自动停用，分号和单引号改作分隔符。详细说明和相关按键覆盖已写在 `xmjd6.custom.yaml` 的注释中。

## 上游来源与自动同步

生成文件和来源 commit 记录在 [`tools/upstream_dictionaries.lock.json`](tools/upstream_dictionaries.lock.json)：

| 上游 | 源文件 | 生成文件 |
| --- | --- | --- |
| [amorphobia/rime-jiandao](https://github.com/amorphobia/rime-jiandao) | `dicts/01.danzi.txt` | `xmjd6.danzi.dict.yaml` |
| [iDvel/rime-ice](https://github.com/iDvel/rime-ice) | `cn_dicts/base`、`ext`、`others` | `xmjd6.ice.dict.yaml` |
| [iDvel/rime-ice](https://github.com/iDvel/rime-ice) | `en_dicts/en`、`en_ext` | `xmjd6.en.dict.yaml` |
| [iDvel/rime-ice](https://github.com/iDvel/rime-ice) | `opencc/emoji.txt` | `opencc/xmjd6/xmjd6_emoji_extra_*` |

同步器不会盲目追踪浮动的 `main`/`master` 内容。锁文件保存已经整合的 Git commit 和生成文件 SHA-256；更新器比较“上次 commit → 当前 HEAD”，只有目标源文件变化时才按最新完整快照重建，避免长期累积补丁造成漂移。

Windows 下推荐使用 PowerShell 7：

```powershell
pwsh -File .\tools\update_upstream_dictionaries.ps1
```

脚本默认使用当前 `PATH` 中的 Python；也可以通过 `-Python` 传入自己的解释器。只验证锁定内容、不刷新上游：

```powershell
pwsh -File .\tools\update_upstream_dictionaries.ps1 -CheckOnly
pwsh -File .\tools\update_upstream_dictionaries.ps1 -Python .\.venv\Scripts\python.exe
```

也可以直接使用 Python：

```powershell
python .\tools\sync_upstream_dictionaries.py --check
python .\tools\sync_upstream_dictionaries.py --refresh --write
```

`.github/workflows/sync-upstream-dictionaries.yml` 每周一 04:17 UTC 自动检查，有变化时运行测试并创建 PR。首次启用自动 PR 前，需要在仓库的 **Settings → Actions → General → Workflow permissions** 中允许 GitHub Actions 创建 Pull Request。

Lua 与自造词实现参考 [wzxmer/rime-txjx](https://github.com/wzxmer/rime-txjx)，已整合的 commit、审查目录和明确排除项记录在 [`tools/upstream_code.lock.json`](tools/upstream_code.lock.json)。这部分不能像纯词库一样无损自动重建，因为必须保留 xmjd6 的命名空间、英文 `i` 入口和顶功差异；因此每周检查只会创建待审查 Issue，不会盲目覆盖本地代码：

```powershell
python .\tools\check_txjx_upstream.py
```

对应工作流是 `.github/workflows/check-txjx-upstream.yml`，不包含任何本机绝对仓库路径，在 GitHub Actions 的 checkout 目录中运行。

第三方来源、固定版本和许可证见 [`THIRD_PARTY.md`](THIRD_PARTY.md) 与 [`licenses/`](licenses/)。

## 维护与验证

本项目的 Python 工具需要 Python 3.11 或更新版本。可以使用系统 Python、虚拟环境或 Pixi；先激活相应环境，再在仓库根目录执行：

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
python .\tools\validate_repo.py
python .\tools\clean_dictionary_quality.py --check
python .\tools\sync_upstream_dictionaries.py --check
python .\tools\check_txjx_upstream.py
git diff --check
```

主要维护命令：

```powershell
# 将 VERSION 和 YAML version 更新到指定日期
python .\tools\update_versions.py 2026-08-04

# 清理完全相同的词典记录
python .\tools\dedupe_dictionaries.py

# 检查或修复词库质量（单字表不在清理范围内）
python .\tools\clean_dictionary_quality.py --check

# 重新生成 Catholicism 扩展并整理分区
python .\tools\build_catholicism_expansion.py --write
python .\tools\organize_catholicism_legacy.py

# 重建四个基督宗派专题词库；随后重建 ICE 以重新避让本地码位
python .\tools\build_christian_traditions.py --write
python .\tools\sync_upstream_dictionaries.py --write
```

仓库验证会检查 YAML、Lua、生成文件哈希、目录命名空间和关键配置。当前测试同时覆盖键道6词组编码、飞键规则、Catholicism 分类、四个基督宗派专题词库、专题词跨库零重码、词库质量、上游去重、重码上限、英文 `i` 命名空间及自动同步工作流。

## 项目结构

```text
.
├─ xmjd6.schema.yaml                 主方案
├─ xmjd6.extended.dict.yaml          词库入口
├─ xmjd6.*.dict.yaml                 本地与生成词库
├─ lua/xmjd6/                        Lua 处理器、翻译器和过滤器
│  ├─ input/                         模块化按键、顶功、标点和快符处理
│  └─ zzc/                           自造词运行时、候选和操作链
├─ opencc/xmjd6/                     OpenCC 命名空间数据
├─ tools/                             生成、同步、清理和验证工具
├─ tests/                             Python 与 Lua 回归测试
├─ licenses/                          第三方许可证副本
├─ THIRD_PARTY.md                    第三方来源说明
└─ .github/workflows/                发布和定期同步工作流
```

## 为什么选择键道6

键道6以音码提供低学习成本和词组输入效率，又通过首笔辅助码减少纯音码的重码。遇到不会读的字时，可使用二分或 GBK 扩展入口；遇到同音候选时，可继续补首笔精确定位。它不是依赖云端大模型的整句输入法，而是一套编码稳定、结果可解释、词库可以自行维护的本地方案。

本仓库的目标是在不破坏键道手感和飞键规则的前提下，持续改善词库质量、重码控制、跨平台可部署性和维护自动化。

## 致谢与授权

- 方案溯源：星空键道6.2 → 星猫键道6。
- 方案及词库维护相关贡献者：吅吅大山、Proud丶Cat、热热、浮生、千年蟲等。
- 键道参考：[xkinput/Rime_JD](https://github.com/xkinput/Rime_JD)
- 天行键参考：[wzxmer/rime-txjx](https://github.com/wzxmer/rime-txjx)
- 当前方案上游：[hugh7007/xmjd6-rere](https://github.com/hugh7007/xmjd6-rere)

本仓库包含来自多个上游项目的材料。Rime-Jiandao 单字数据使用 AGPL-3.0-or-later，Rime-Ice 词库使用 GPL-3.0，rime-txjx 参考实现使用 MIT；具体来源、固定 commit 和许可证文本以 [`THIRD_PARTY.md`](THIRD_PARTY.md) 为准。
