# Scriptorium 产品方向决议（Public Alpha 阶段宪法）

> 状态：已确认 v3 · 2026-07-23 · 本文件是 Public Alpha 阶段所有细化工作的依据。
> 演化（2026-06-22）：**R5「实时=自动·零手动」已换挡到「agent 原生·按需 pull」**——后台守护进程/无人值守摘要器全退役，改由用户/agent 在会话里按需驱动（可用的捕获钩子保留）。
> 演化（2026-07-15）：目标从仅作者自用扩展为面向外部技术型研究者的 Public Alpha；采用薄入口、分域 master、Codex + Claude Code 双宿主、可选集成，并明确 Engram 不属于官方运行组件。
> 演化（2026-07-23）：增加外部科研执行与断言证据层；`experiment-run/1.0` 只记录执行观察、绝不授权执行，`claim-evidence/1.0` 将证据状态与人工审核状态分离。
> 角色约定：Codex 与 Claude Code 均为受支持的 agent 宿主；对话中文、代码/标识符英文。
> 关联：[suite-entry-and-ownership.md](suite-entry-and-ownership.md)（入口、所有权与宿主 ADR）· [vault-layout.md](vault-layout.md)（Markdown workspace）· [trust-model.md](trust-model.md)（信任边界）。跨项目历史见 Provenance MCP。
> 标记：`[已确认]` = 用户已拍板；`[草案]` = PM 拟、待用户增补/否决。

## 0. 一句话
把 Scriptorium 打磨成面向技术型个人研究者的**本地优先、agent 原生研究工作流套件**：薄入口负责发现与编排，至少一个 Codex 或 Claude Code 宿主执行智能工作流，Markdown workspace 承载人机协作，Provenance 提供跨会话记忆与检索，Steward 治理文献，Lectern 作为可选出片边缘，组件通过开放文件契约协作。

## 1. 定位
- **R1 目标用户** `[已确认]` Public Alpha 首发用户是外部的、技术能力较强的个人研究者与 AI-heavy 知识工作者；本地必须至少已有 Codex 或 Claude Code 之一。必须提供可复现的合成数据 demo、源码安装说明和诚实的能力边界，但暂不承诺消费级开箱体验。
- **R2 产品身份** `[已确认]` Scriptorium 是薄入口 + agent 宿主 + 可独立使用的组件集合：核心文件契约统一，运行时保持松耦合；完整 Public Alpha 必须选择 Codex、Claude Code 或同时选择二者，二者一等支持；文献、Obsidian 体验与出片按可选 capability profile 组合，不做单体应用。

## 2. 架构
- **R3 分域 master** `[已确认]` 每类持久数据只有一个 master：Zotero（启用时）拥有文献源记录；Markdown 文件拥有人写项目事实与获批工件；host sync layer 拥有项目笔记中的自动 progress-log marker 区；外部计算执行器拥有原始执行输出及其 `experiment-run/1.x` 记录；显式人工审核工作流拥有 `claim-evidence/1.x` 的审核决定；Provenance 仅是权威的跨会话记忆/检索层；Steward 产出的契约文件和 Lectern 交付物各自保持文件级 master。薄入口不拥有业务数据。
- **R4 工作台与边界** `[已确认]` plain Markdown workspace = 核心人机工作台；Obsidian 是可选客户端而非运行时依赖。workspace 按 master 分区：**人写区**（用户拥有，摄取进 Provenance）/ **工具派生区**（生成工具拥有，可重建）。每条信息单一 master、视图永远派生。
- **R5 同步模型** `[已确认]` 捕获适配器可事件入队，处理统一为短生命周期、显式的 on-demand pull。Claude Code 可用 enqueue-only `SessionEnd` 钩子；Codex 可用本地日志扫描；两者在 pull 后进入同一 worker 与审批流。不得宣称所有宿主具有相同的自动钩子，也不做亚秒级常驻守护进程。

## 3. 机制
- **R6 会话写回（M1）** `[已确认]` 混合：已配置的 capture adapter 负责采集，on-demand pull 负责摄取；时间线可按幂等规则自动追加，状态/下一步/结论等高价值断言必须生成草稿 → 用户确认/微调 → 入库。
- **R7 项目笔记（M2）** `[已确认]` 一篇笔记两段：【手写区：计划/想法/下一步】+【自动进展日志：会话总结追加，append-only】。同文件、两 master 分段隔离。
- **R8 摄取范围（M3）** `[已确认]` Provenance 摄取从结构化 frontmatter 扩到自由文本想法/笔记。

## 4. 约束（贯穿每条流）
- **R9 数据安全** `[已确认]` 自动写回一律 append-only、绝不覆盖人写区、写前可回滚；防误删为硬约束。
- **R10 隐私与联网** `[已确认]` 套件不做遥测；入口、spec 与 Provenance 默认无运行时出站。宿主模型、Zotero Web API、Lectern provider/parser 与未来 connector 是分别归属、显式启用的 egress，必须说明发送的数据与本地替代路径。原始敏感数据先脱敏；任何 `status`/`doctor`/日志不得打印 secret 值。

## 5. 范围
- **R11 出片** `[已确认]` Lectern = 官方但可选的 Slides profile，通过 `handoff/1.x` 消费文件；核心套件不依赖它，**不纳入 PPT-Agent**。
- **R12 可选集成** `[已确认]` Obsidian、Zotero、browser extension、Lectern、GROBID、Better BibTeX、PDF++、Dataview 均按能力 profile 启用；缺失时只降级对应能力，不得使 Public Alpha core 的其余能力失效。
- **R13 文献进展摘要** `[已确认]` Steward 已提供库内 review/reading/lineage 的契约与确定性投影；Public Alpha 只承诺已有 Zotero/本地文献链。RSS、OpenAlex、微信公众号等外部发现源留待未来，且只能产出候选或可审核 proposal。
- **R14 契约演进** `[已确认]` `note/1.0`、`session-summary/1.0`、`experiment-run/1.0`、`claim-evidence/1.0` 与 Markdown workspace 所有权约定已经落地；未来格式变化继续采用版本化、加性演进，破坏性变化才提升 major。
- **R19 研究执行与证据** `[已确认]` Python、Jupyter、容器、人工或领域软件等外部执行器负责实际运行与隔离；`experiment-run/1.x` 记录输入、代码/环境、有效参数、随机种子、状态、指标与产物哈希，是可追溯观察记录而非命令，成功指标也不会自动成为科研结论。agent 可生成 `claim-evidence/1.x` 草稿，但证据状态与审核状态必须分离，只有显式人工流程可以接受、拒绝或取代断言；入口、校验器和 Provenance 摄取都不得暗含执行或批准。

## 6. 执行
- **R15 薄入口** `[已确认]` 当前 umbrella repo 只负责 `init`/`doctor`/`status`/`inventory`/`pull`/`demo`、组件兼容清单、workspace 模板与宿主安装器；`inventory` 仅盘点显式来源并给出不含路径的分类级审阅路由，不读取文件正文、不持久化清单，也不执行迁移。入口只能调用公开 CLI/MCP/契约文件，不得 import 组件内部模块或复制业务逻辑。
- **R16 Public Alpha 顺序** `[已确认]` ① 所有权/信任 ADR → ② 合成 demo + Markdown workspace 模板 → ③ 薄入口与 doctor → ④ Codex/Claude Code 宿主适配 → ⑤ 跨仓契约/E2E → ⑥ 文档、视觉证据与版本发布。
- **R17 Public Alpha 不做** `[已确认]` 消费级桌面壳/安装器、云同步/团队协作、OpenAlex/RSS 实作、向量嵌入、远程控制/第三方自动化连接器、亚秒级守护进程。Engram 作为独立产品/UX 实验退出官方组件表；若未来替代 Provenance，必须另立迁移 ADR，不允许双 memory hub。

## 7. 可选外部提案源（R18 · 非核心兼容边界） `[已确认]`
**定位**：移动端捕获、消息入口或其他外部自动化系统可以通过公开契约或受控适配器提交候选提案，但不属于 Public Alpha 核心、官方组件注册表、quickstart 或发布验收。

**最低信任原则：外部输入始终是不可信候选，不能直接修改权威研究状态。**
- **写面最小化**：连接器只能写入隔离的暂存边界或调用公开的提案入口，不得直接写项目文件、代码、Provenance 记忆或同步状态。
- **读面最小化**：默认不授予原始研究资料、个人画像、凭据或内部路径的读取权限；确需读取时必须由用户显式选择范围并由连接器说明数据流向。
- **宿主侧校验**：可信同步层负责规范化、限额、项目解析和主机生成标识；项目未解析时保持待处理或拒绝，不得生成 `project: null` 的 `session-summary/1.0`。
- **人工门禁**：合法提案也只能成为待审草稿；创建项目、执行代码、批准高价值结论与权威写回分别授权，互不隐含。

> 连接器的身份认证、网络拓扑、运行隔离和凭据管理由其自身安全文档负责。核心套件只承诺进入宿主适配器后的最低信任边界，不为任何特定供应商或部署方式背书。

## 8. Markdown workspace 结构（Obsidian 可选）
历史 vault 曾被当作记忆全量镜像，导致人写项目脊柱被工具产物淹没并产生双份事实。修复原则：**workspace 只放用户要读/写的和少量精选派生视图；Provenance 保存全部可查记忆；workspace 不做记忆 1:1 镜像**。普通文本编辑器必须可完成核心流程，Obsidian 与插件只增强体验。

| 区 | 文件夹 | 处置 | master |
|---|---|---|---|
| 人写区 | `Projects/`(脊柱·R7 两段) · `Inbox/` · `_planning/` | 保留/强化；按审批规则摄取 | 用户的 Markdown 文件；Provenance 仅索引/记忆 |
| 权威契约实例 | `reading-notes/*.json` · 放入 `Reviews/` 的 review/lineage JSON | 保留；派生视图清理不得删除 | 产出该实例的 agent 工作流或 Steward |
| 精选派生视图 | `Dashboard` · `Reviews/*.md` · `reading-notes/*.md` · `_index.md` · `Home.md` | 保留少量；静态视图不得依赖插件 | 声明的渲染工具 |
| 审批队列 | `Approvals.md` | 保留待批项与用户编辑；提交后可再生成 | host sync layer 维护结构，用户拥有勾选/修改决定 |
| 工作区外部源 | agent 日志/导出 · PDF/附件 · 代码仓 · 可选 Zotero 数据 | 不做全量镜像；按需导入/引用（移出≠删除、先备份、绝不 hard-delete 唯一副本） | 原 agent 宿主/文件路径/代码仓/Zotero |
| Provenance 受保护层 | 获批记忆 · 搜索索引 · profile · `sync-state/` | 不镜像进工作区；通过 MCP/搜索按需访问 | Provenance |

注：可选外部提案源使用的暂存位置与权限由连接器自行声明，不属于 Public Alpha 核心布局。Dataview、Bases、PDF++ 或 AI 输入插件均不得成为基础验收条件。

## 9. 数据流（见架构图）
Markdown 人写区与 capture adapters（Codex 扫描 / Claude Code enqueue / 可选 browser import）→ on-demand pull → 单 worker（混合审核、append-only）→ **Provenance 权威记忆/检索层** → MCP 回喂与派生视图。启用 Literature profile 时，Zotero → Steward → `library-kb`/reading/lineage 契约 → Provenance/Markdown；进行科研执行时，外部执行器 → `experiment-run` → agent 提议 `claim-evidence` 草稿 → 人工审核 → 后续记忆/交付；启用 Slides profile 时，Steward `handoff` → Lectern → 用户拥有的 `.pptx`。薄入口只编排，不进入数据面。

## 10. 下一步（按 R16）
1. 在 Provenance MCP 之上增加项目级 context-capsule/resume 入口，并与不暴露内容的控制面 `status` 分开。
2. 在分类级 `inventory` 之后，增加适配器级、必须显式人审的迁移清单与执行路径。
3. 建立 canonical schema 驱动的跨仓 E2E，补齐 Steward handoff→Lectern 交付链。
4. 用干净 Windows 环境完成源码首装、配置回退、离线 demo 与真实项目路径验收。
5. 以 CI、验收记录和截图为证据，统一 README、版本与 Public Alpha 发布说明。
6. 在不引入内置执行器的前提下，为 `experiment-run/1.0` 与 `claim-evidence/1.0` 增加 Provenance 摄取、审批及合成跨仓 E2E。
