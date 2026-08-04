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

## 常用入口与快捷功能

| 输入或按键 | 功能 |
| --- | --- |
| `i` + 英文字母 | 英文词库；输入第二键后隐藏入口 `i` |
| `u` + 全拼 | 全拼反查，显示对应键道编码 |
| `v` + 二分编码 | 二分反查，用于不会读的字 |
| `o` + 编码 | GBK、繁体和生僻字扩展入口 |
| `\` | 自造词入口，详见 [`zzc/自造词使用教程.md`](zzc/自造词使用教程.md) |
| `;` + 编码 | 快符入口 |
| `=` + 表达式 | 计算器及工具入口 |
| `=tj` | 查看打字统计 |
| `rq` | 日期候选 |
| `F7` | 切换简体/繁体 |
| `Ctrl + \` | 切换 Emoji |

默认启用顶功、逐码补全、Emoji、快符、计算器和 630 提示；默认关闭流式整句输入。具体默认状态可在 [`xmjd6.custom.yaml`](xmjd6.custom.yaml) 中修改。

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

第三方来源、固定版本和许可证见 [`THIRD_PARTY.md`](THIRD_PARTY.md) 与 [`licenses/`](licenses/)。

## 维护与验证

本项目的 Python 工具统一建议使用 Pixi 环境中的解释器：

```powershell
$python = 'D:\Dev\pixi\bin\python.exe'

& $python -m unittest discover -s tests -p 'test_*.py' -v
& $python tools/validate_repo.py
& $python tools/clean_dictionary_quality.py --check
& $python tools/sync_upstream_dictionaries.py --check
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

本仓库包含来自多个上游项目的材料。Rime-Jiandao 单字数据使用 AGPL-3.0-or-later，Rime-Ice 词库使用 GPL-3.0；具体来源、固定 commit 和许可证文本以 [`THIRD_PARTY.md`](THIRD_PARTY.md) 为准。
