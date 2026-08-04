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

默认启用键道顶功、逐码补全、Emoji、快符、计算器和 630 提示，默认关闭流式整句输入。若 Emoji 没出现，依次确认“表情展示”已开启、输入的是普通中文编码而不是 `u/v/o` 反查、文件已完整复制到 `opencc/xmjd6/`，然后重新部署。

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

Windows/Pixi 用户可以直接运行：

```powershell
& 'D:\Dev\pixi\bin\python.exe' zzc\Windows_词库合并.py
```

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
| `xmjd6.core.dict.yaml` | 921 | 630 规则、快符和核心候选 |
| `xmjd6.fjcy.dict.yaml` | 514,033 | 附加扩展词组 |
| `xmjd6.ice.dict.yaml` | 445,046 | Rime-Ice 中文词库转码结果 |
| `xmjd6.en.dict.yaml` | 23,610 | Rime-Ice 英文词库 |
| **合计** | **1,214,736** | 不含动态自造词和个人词库 |

`xmjd6.ice` 会先排除本地已有词，再按照 `base → ext → others` 和上游权重分配编码。低优先级重码词会被删减，合并后的中文重码率不会高于同步前的本地基准；新增词在同一码下最多保留 8 个候选。

### 词库加载顺序

[`xmjd6.extended.dict.yaml`](xmjd6.extended.dict.yaml) 控制词库导入。当前主要顺序为：

```text
user → zzc → danzi → cizu → catholicism → core → fjcy → ice → en
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

同步器不会盲目追踪浮动的 `main`/`master` 内容。锁文件保存已经整合的 Git commit 和生成文件 SHA-256；更新器比较“上次 commit → 当前 HEAD”，只有目标源文件变化时才按最新完整快照重建，避免长期累积补丁造成漂移。

Windows 下推荐使用 PowerShell 7：

```powershell
& 'D:\Program Files\PowerShell\7\pwsh.exe' -File tools/update_upstream_dictionaries.ps1
```

脚本会自动优先使用 `D:\Dev\pixi\bin\python.exe`。只验证锁定内容、不刷新上游：

```powershell
& 'D:\Program Files\PowerShell\7\pwsh.exe' -File tools/update_upstream_dictionaries.ps1 -CheckOnly
```

也可以直接使用 Python：

```powershell
& 'D:\Dev\pixi\bin\python.exe' tools/sync_upstream_dictionaries.py --check
& 'D:\Dev\pixi\bin\python.exe' tools/sync_upstream_dictionaries.py --refresh --write
```

`.github/workflows/sync-upstream-dictionaries.yml` 每周一 04:17 UTC 自动检查，有变化时运行测试并创建 PR。首次启用自动 PR 前，需要在仓库的 **Settings → Actions → General → Workflow permissions** 中允许 GitHub Actions 创建 Pull Request。

Lua 与自造词实现参考 [wzxmer/rime-txjx](https://github.com/wzxmer/rime-txjx)，已整合的 commit、审查目录和明确排除项记录在 [`tools/upstream_code.lock.json`](tools/upstream_code.lock.json)。这部分不能像纯词库一样无损自动重建，因为必须保留 xmjd6 的命名空间、英文 `i` 入口和顶功差异；因此每周检查只会创建待审查 Issue，不会盲目覆盖本地代码：

```powershell
& 'D:\Dev\pixi\bin\python.exe' tools/check_txjx_upstream.py
```

对应工作流是 `.github/workflows/check-txjx-upstream.yml`，不包含任何本机绝对仓库路径，在 GitHub Actions 的 checkout 目录中运行。

第三方来源、固定版本和许可证见 [`THIRD_PARTY.md`](THIRD_PARTY.md) 与 [`licenses/`](licenses/)。

## 维护与验证

本项目的 Python 工具统一建议使用 Pixi 环境中的解释器：

```powershell
$python = 'D:\Dev\pixi\bin\python.exe'

& $python -m unittest discover -s tests -p 'test_*.py' -v
& $python tools/validate_repo.py
& $python tools/clean_dictionary_quality.py --check
& $python tools/sync_upstream_dictionaries.py --check
& $python tools/check_txjx_upstream.py
git diff --check
```

主要维护命令：

```powershell
# 将 VERSION 和 YAML version 更新到指定日期
& $python tools/update_versions.py 2026-08-04

# 清理完全相同的词典记录
& $python tools/dedupe_dictionaries.py

# 检查或修复词库质量（单字表不在清理范围内）
& $python tools/clean_dictionary_quality.py --check

# 重新生成 Catholicism 扩展并整理分区
& $python tools/build_catholicism_expansion.py
& $python tools/organize_catholicism_legacy.py
```

仓库验证会检查 YAML、Lua、生成文件哈希、目录命名空间和关键配置。当前测试同时覆盖键道6词组编码、飞键规则、Catholicism 分类、词库质量、上游去重、重码上限、英文 `i` 命名空间及自动同步工作流。

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
