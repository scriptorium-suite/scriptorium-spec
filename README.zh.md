[English](README.md) | 中文

# Scriptorium Spec（数据契约）

> 让 Scriptorium 套件各工具彼此交换文件的共享数据契约。

> **产品状态：Public Alpha 契约基线。** Public Alpha 目标以 Windows
> 为首发平台，并要求至少选择一个 agent 宿主；Codex 与 Claude Code 是地位相同的一等
> 目标宿主；canonical installer 已实现，但 Claude Code 的 live `SessionEnd` golden
> path 对等验证仍是 release gap。用户的
> Markdown 工作区、PDF 与代码保持权威；Provenance 提供
> 本地捕获、搜索、append-only 写回与高价值记忆的人审门禁。Zotero、Obsidian 与 Lectern
> 均为可选能力，不是核心前置条件。

> 英文版为契约正本（canonical）；中英文 README 随同一版本维护，如有歧义以英文为准。

## 相关文档

本仓：[README](README.md) · [中文 README.zh](README.zh.md) · [CHANGELOG](CHANGELOG.md) · [specs/](specs/) · [schemas/](schemas/)

要查看这些契约如何在“真实公共接口 + 全合成数据”的纵向链路中运行，请阅读
[Scriptorium Public Alpha 产品案例](https://github.com/scriptorium-suite/scriptorium/blob/main/docs/case-study.zh-CN.md)。

**套件 / Suite:** [scriptorium-spec](https://github.com/scriptorium-suite/scriptorium-spec)（契约权威源） · [steward](https://github.com/scriptorium-suite/steward) · [Provenance](https://github.com/foxsplendid/Provenance) · [Academic-Slides-Agent / Lectern](https://github.com/foxsplendid/Academic-Slides-Agent) · [.github](https://github.com/scriptorium-suite/.github)

> 本仓=数据契约权威源（contract SSoT）；其余仓库镜像这些契约事实，不得各自分叉。
> 套件入口与组件所有权见
> [specs/suite-entry-and-ownership.md](specs/suite-entry-and-ownership.md)。

## 概述

Scriptorium Spec 规定了 **Scriptorium** 套件所用的文件格式——这是一套面向熟悉 GitHub、
计划在 Windows 上至少使用 Codex 或 Claude Code 之一的科研工作者的本地优先工作流。核心直接工作在
普通项目目录上：Markdown、PDF 与代码仍由用户持有并作为事实源；Provenance 通过审批流程
记录派生项目上下文和高价值断言；可选工具再提供文献库治理与幻灯片输出。本仓库包含
JSON Schema、约定文档、可用示例以及一个
小型校验器。套件内的工具互不调用内部接口，只通过**文件**交换数据；文件格式由本仓库
规定——任何工具、任何 agent、甚至你用文本编辑器，都可以等价地生产或消费这些文件。
本仓库是整个套件唯一的硬耦合点。

套件包含三个独立开发的工具：

| 工具 | 职责 |
|---|---|
| **Steward**（文献管家） | 可选的独立文献库产品：Zotero 备份 → 盘点 → 提案 → 人审 → 执行 → 回滚；KB 与可选 Obsidian 导出 |
| **Provenance**（来源/记忆） | 核心本地档案与审批式项目记忆账本：捕获 → 脱敏/假名化 → 搜索 → append-only 时间线 + 高价值断言人审 → 只读 MCP |
| **Lectern**（讲台） | 独立、可选的学术汇报产品：论文 PDF 或 `handoff/1.x` → 证据池 → 人审大纲 → 原生可编辑 `.pptx` |

所有权 ADR 将 Windows 配置、诊断、合成 demo 与 agent task 注册归于薄套件入口；
该入口本身不成为新的数据存储。本地 umbrella 候选版现已实现默认预览的 `init`、
`doctor`、`status`、仅盘点显式来源和元数据的 `inventory`、`demo`、`pull`、
canonical host installer 与 Windows CI；适配器级的人审迁移执行、正式发布的安装包
以及外部 beta 证据仍是 release gap。

## 特性

- **十种交换格式**，每种都是一份 JSON Schema（Draft 2020-12）：

  | 格式 | Schema | 生产者 | 消费者 |
  |---|---|---|---|
  | `library-kb/1.x` | [schemas/library-kb/v1.json](schemas/library-kb/v1.json) | Steward `export` | Provenance 文献摄取、Steward 工作流、agent |
  | `proposal/1.x` | [schemas/proposal/v1.json](schemas/proposal/v1.json) | LLM / agent / 人工（三方等价） | Steward `apply` |
  | `handoff/1.x` | [schemas/handoff/v1.json](schemas/handoff/v1.json) | Steward `pick`（1.0 单论文 / 1.1 多论文） | Lectern（可读两种形态） |
  | `project/1.x` | [schemas/project/v1.json](schemas/project/v1.json) | 人工 / agent / Markdown frontmatter 适配器 | Provenance 项目组合/上下文、可选看板 |
  | `note/1.x` | [schemas/note/v1.json](schemas/note/v1.json) | 宿主同步层或可选捕获适配器 | Provenance 受保护摄取/搜索 |
  | `session-summary/1.x` | [schemas/session-summary/v1.json](schemas/session-summary/v1.json) | Codex / Claude Code 宿主工作流 | Provenance 审批流、项目进展日志 |
  | `reading-note/1.x` | [schemas/reading-note/v1.json](schemas/reading-note/v1.json) | `read-paper` agent task | Steward 渲染器与文件型 agent 工作流；Provenance 摄取仍是 release gap |
  | `parsed-paper/1.x` | [schemas/parsed-paper/v1.json](schemas/parsed-paper/v1.json) | Steward `parse`（本地 GROBID） | `read-paper`、综述、Steward lineage |
  | `lineage-graph/1.x` | [schemas/lineage-graph/v1.json](schemas/lineage-graph/v1.json) | Steward `lineage` + agent 标注关系类型 | Steward 渲染器与文件型 agent 工作流；Provenance 摄取仍是 release gap |
  | `review/1.x` | [schemas/review/v1.json](schemas/review/v1.json) | `synthesize-direction` agent task | Markdown/文件输出与 agent 工作流；Provenance 摄取仍是 release gap |

Lectern 当前消费 `handoff/1.x`，**不会**直接消费 `library-kb/1.x`。Provenance 当前已实现
文献库、项目、笔记和会话数据的摄取；reading-note/review/lineage 摄取尚未发布，因此在上表
明确列为 Public Alpha release gap。

- **约定文档**：覆盖版本号规则、Markdown 项目组合、可选 Obsidian 导出/布局、config-root、事件/同步层（`sync-layer.md`）、产品方向（`product-direction.md`）、文献自动化（`literature-automation.md`）、套件入口/所有权与信任模型（`trust-model.md`）。
- **可用示例**：[`examples/`](examples) 下每种格式都有示例，并保持与 schema 一致有效。
  所有示例和无效测试夹具均属于刻意虚构的 XQ-17 演示世界；其中的人名、论文、标识符、路径、
  会话、日期与结果均不描述任何真实人物或科研工作。
- **零依赖校验器**（[`tools/validate.py`](tools/validate.py)）：仅校验承重约束，不依赖任何第三方库。
- **稳定的版本约定**：`schema_version` 写进数据文件本身；major=破坏性、minor=增量；消费者忽略并保留未知字段。

## 安装

无需安装或打包——本仓库是一组规范、示例和一个自包含脚本。克隆后阅读即可：

```
git clone https://github.com/scriptorium-suite/scriptorium-spec.git
cd scriptorium-spec
```

唯一可运行的产物 `tools/validate.py` 仅使用 Python 标准库（Python 3.x），无需安装任何依赖。

## 用法

在 Windows PowerShell 中校验全部示例：

```powershell
$exampleFiles = (Get-ChildItem -LiteralPath .\examples -Filter '*.json').FullName
python .\tools\validate.py $exampleFiles
```

每个文件会打印 `ok` 或 `INVALID`（含逐字段错误路径）；退出码 `0` 表示全部有效。
校验器按 `schema_version` 字段（如 `library-kb/1.0`）分派，刻意保持精简——
`schemas/` 下的 JSON Schema 才是权威定义。

要编写一份文件，复制对应示例、修改后再重新校验即可。

## 目录结构

```
scriptorium-spec/
├── schemas/                  # JSON Schema（格式的权威定义）
│   ├── library-kb/v1.json    # 文献库的规范化快照
│   ├── proposal/v1.json      # 离线、可人审的重组方案
│   ├── handoff/v1.json       # 待生成幻灯片的论文 PDF + 元数据（1.0 与 1.1 多论文）
│   ├── project/v1.json       # 科研项目记录（Markdown frontmatter 是一种适配形式）
│   ├── note/v1.json          # 自由文本捕获信封
│   ├── session-summary/v1.json # Codex/Claude Code 会话写回（timeline + 待批高价值断言）
│   ├── reading-note/v1.json   # 单篇论文分级解读（4 个可选阅读层级）
│   ├── parsed-paper/v1.json   # 论文 PDF 的规范化本地解析（章节 + 参考文献 + 图表）
│   ├── lineage-graph/v1.json  # 研究方向的引用脉络（节点 + 带类型的边）
│   └── review/v1.json         # 方向综述（叙事章节 + 对比表）
├── examples/                 # 每种格式的有效示例，含兼容性版本变体
├── specs/                    # 约定文档
│   ├── versioning.md         # schema_version 规则；忽略并保留未知字段
│   ├── obsidian-export.md    # 可选 Obsidian 投影 + Zotero extra 字段约定
│   ├── config-root.md        # ~/.config/scriptorium/<tool>/、优先级、密钥纪律
│   ├── project-portfolio.md  # Markdown 工作区项目记录 + 可选看板
│   ├── sync-layer.md         # 宿主捕获/审批层：单 worker、append-only
│   ├── vault-layout.md       # Markdown 工作区布局与所有权
│   ├── product-direction.md  # Public Alpha 产品决议
│   ├── suite-entry-and-ownership.md # 套件入口与组件边界
│   ├── literature-automation.md # 按需文献刷新（可选每周 opt-in）+ 库内新进展 digest
│   ├── literature-reading.md # 分阶段阅读 + 方向脉络综述
│   └── trust-model.md        # 套件安全/隐私保证（按主题）+ 诚实的边界说明
├── tools/
│   └── validate.py           # 零依赖、仅标准库的结构校验器
├── CHANGELOG.md              # 版本历史
└── LICENSE                   # Apache-2.0
```

### 当前包名与命令行名称

Steward 的源码包名为 `scriptorium-steward`，CLI 为 `steward`。Provenance 当前暴露
`prov-*` CLI。Lectern 是 workspace，headless CLI 为 `lectern`。统一套件安装包尚未发布；
入口所有权 ADR 定义了 Public Alpha 的发布边界。

## 状态

**Public Alpha 契约基线：v2.2.0。** 该基线以 Scriptorium v0.1.0 为兼容目标，
不表示所有组件 tag 已经发布。跨仓与 Windows CI golden path 已覆盖
`init`/`doctor`/`status`/`inventory`/`demo`/
`pull` 入口及 canonical host installer，但适配器级的人审迁移执行、套件安装包与
外部 beta 证据仍是产品缺口。事件/同步层契约
（`note/1.0`、`session-summary/1.0`）已在 Provenance 实现；parsed-paper/reading-note/
review/lineage 摄取尚未实现。

## License

[Apache-2.0](LICENSE)。
