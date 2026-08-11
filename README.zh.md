# Scriptorium Spec

[![CI](https://github.com/scriptorium-suite/scriptorium-spec/actions/workflows/ci.yml/badge.svg)](https://github.com/scriptorium-suite/scriptorium-spec/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/scriptorium-suite/scriptorium-spec)](https://github.com/scriptorium-suite/scriptorium-spec/releases)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Scriptorium Spec 是 Scriptorium 套件的数据契约源头。它定义各组件交换项目、文献、证据、审阅和 handoff 数据时使用的版本化文件格式，让组件可以独立开发、独立使用，又能组合成一套系统。

![Scriptorium Spec 契约图](docs/assets/contract-map.svg)

## 为什么需要这个仓库

Scriptorium 不是单体应用，而是一组可以拆分的组件。要让这种组织方式成立，所有组件必须对“项目文件、笔记、审阅、handoff、证据 claim、实验 run”这些对象有共同理解。这个仓库把这些约定变成清晰、可测试、可版本化的契约。

核心规则是：组件交换文件，不互相调用私有内部 API。Steward 可以生产文献 handoff，Provenance 可以消费项目记忆，Scriptorium 可以调度流程，是因为它们都遵循这里定义的公开格式。

## 仓库内容

| 区域 | 内容 |
| --- | --- |
| `schemas/` | project、note、session summary、library KB、handoff、parsed paper、lineage graph、reading note、review、experiment run、claim evidence 等 JSON Schema。 |
| `examples/` | 每种公开格式的有效样例。 |
| `specs/` | 版本、vault 布局、同步层、信任模型、文献自动化、执行与证据记录等文字规范。 |
| `tools/validate.py` | 仅依赖标准库的验证器。 |
| `tests/` | 契约检查与发布一致性测试。 |

## 快速开始

```powershell
git clone https://github.com/scriptorium-suite/scriptorium-spec.git
cd scriptorium-spec
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe tools\validate.py examples\*.json
```

运行测试：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## 契约类型

| 契约 | 用途 |
| --- | --- |
| `project` | 稳定项目身份与 portfolio 元数据。 |
| `note` / `session-summary` | 同步层笔记与会话收尾摘要。 |
| `library-kb` / `parsed-paper` / `lineage-graph` | 文献来源、解析和引用关系记录。 |
| `reading-note` / `review` | 可读的阅读笔记与审阅结果。 |
| `proposal` / `handoff` | 从文献工作转入下游任务的结构化交接。 |
| `experiment-run` / `claim-evidence` | 开发中的执行事实与已审阅证据 claim 契约。 |

## 版本策略

Schema 是版本化的，并尽量采用向后兼容的增量演进。消费者应该根据 `schema_version` 分发处理逻辑；遇到未知或不兼容版本时应拒绝，而不是猜测。破坏性修改需要新版本和新样例。

## 与套件的关系

这个仓库不是运行时包，而是以下组件共同遵守的数据契约层：

- [scriptorium](https://github.com/scriptorium-suite/scriptorium)：套件入口和安装器。
- [steward](https://github.com/scriptorium-suite/steward)：文献与 handoff 产物生产者。
- [Provenance](https://github.com/foxsplendid/Provenance)：项目记忆与同步记录的消费者和生产者。
- [Academic-Slides-Agent](https://github.com/foxsplendid/Academic-Slides-Agent)：可选的展示材料下游消费者。

## 安全口径

这些契约明确区分原始来源、AI 生成草稿、执行事实和用户审阅过的 claim。一次 run 成功并不自动等于科学结论或项目结论；claim 只有经过对应规范和运行时实现定义的审阅流程后，才可以成为 accepted 状态。

## 许可证

Apache-2.0。见 [LICENSE](LICENSE)。
