# 实习知识库 Internship_KB 建设计划 v1.0

> 状态：用户已确认方案，进入执行准备。执行入口：`/start-work internship-kb`

## TL;DR

> **Quick Summary**: 在现有 Obsidian vault 的 `实习/` 目录下，以"公司为模块"建立一套既利于个人沉淀、又对 AI Agent（Cline/MCP/OpenCode）友好的结构化知识库。核心 = 标准化 YAML Frontmatter + 四层漏斗内容结构 + 日/周/月工作流 + 版本溯源机制（Git + Changelog）。
>
> **Deliverables**:
> - `实习/00_Meta_Templates/`：4 个模板（daily/tech/business/resume）+ 受控词表 + AGENT-README
> - `实习/01_Methodology/`：通用方法论区（空目录 + README 占位说明）
> - `实习/飞冰科技/`：00_INDEX.md + 01_Daily_Logs + 02_Tech_DeepDive + 03_Business_Context + 04_Resume_Assets
> - `实习/知识库管理指南.md`：给用户本人看的操作手册
> - 存量迁移：2 篇入职笔记 → `飞冰科技/draft/`
> - 协作习惯沉淀：经 self-improving-agent 写入 rules.yaml
>
> **Estimated Effort**: Short（约 3 波次 + 1 波终验）
> **Parallel Execution**: YES - 3 waves + final review wave
> **Critical Path**: 目录骨架 → 模板/词表 → 指南/索引 → 迁移/习惯 → 端到端验证

---

## Context

### Original Request
用户提供了一套实习知识库建设方案（目录骨架 00-04 + YAML Frontmatter + 日/周/月工作流 + AI Agent 联动），经多轮访谈对齐后确认执行。核心诉求：以实习公司为模块、每公司独立知识结构；通用方法论在实习根目录统一；每篇笔记带高度结构化元数据（frontmatter），便于 AI Agent 检索理解。

### Interview Summary — 已确认决策（全部经用户逐项确认）
1. 不新建独立 `Internship_KB` 根目录，融入现有 `实习/` 目录
2. 公司层不重复放模板；模板只存 `00_Meta_Templates/` 一份（单一来源）
3. `draft/` 保留为草稿箱（临时编写区），2 篇入职笔记迁入
4. 每日复盘打通（方案 A）：实习日记录进公司 `01_Daily_Logs/`，`每日复盘/当天.md` 只放一条链接，不重复记录
5. status 统一三态：`draft / processing / done`（无 emoji；旧 `笔记体系方案.md` 的 80%/100% 不动）
6. 命名：英文目录名（00_Meta_Templates / 01_Methodology / 01_Daily_Logs 等）
7. 版本溯源：Git 历史保全文 + 文件内 `## Changelog` 保演进逻辑；**不做** v1/v2 副本
8. 协作习惯沉淀：走既有 `self-improving-agent` 机制（rules.yaml → AGENTS.md），知识库内不放习惯记录
9. 实习根目录放《知识库管理指南.md》——给用户本人看（区别于 AGENT-README 给 Agent 看）

### Research Findings（已核实）
- Vault 根已有 `笔记体系方案.md`（八股文体系，status 用 draft/80%/100%）、`知识沉淀使用指南.md`（Obsidian MCP 指南）、`每日复盘/`、`.sisyphus/`
- `实习/飞冰科技/入职笔记/` 有 2 篇：`入职后初期注意事项.md`、`feibing-neo 初步了解.md`；`实习/飞冰科技/draft/` 为空目录
- `self-improving-agent` skill 位于 `C:\Users\施鸿福\.agents\skills\self-improving-agent\`，scripts/improve.py 管理 `~/.agent-improvement/rules.yaml`；rules.yaml 已有 1 条规则（中文回复，已升级全局 AGENTS.md）
- Obsidian Local REST API（端口 27123）+ mcp-obsidian 已配置；`knowledge-precipitation` skill 已存在——**均不重建，本计划不触碰**

### Metis Review
Metis 咨询被中止（工具调用中断）。已通过多轮用户访谈对齐 + 本计划自查补漏覆盖主要风险：双体系并存、status 语义冲突、词表漂移、模板单一来源、溯源方案、习惯沉淀通道、每日复盘重复记录。

---

## Work Objectives

### Core Objective
在 `实习/` 下建立以公司为模块、模板与内容分离、Agent 可结构化读取的实习知识库体系，配套给用户本人看的操作指南与改进溯源机制。

### Concrete Deliverables（全部文件清单）
| # | 路径 | 类型 |
|---|------|------|
| 1 | 实习/00_Meta_Templates/ | 目录 |
| 2 | 实习/00_Meta_Templates/daily-log-template.md | 模板 |
| 3 | 实习/00_Meta_Templates/tech-deepdive-template.md | 模板 |
| 4 | 实习/00_Meta_Templates/business-context-template.md | 模板 |
| 5 | 实习/00_Meta_Templates/resume-asset-template.md | 模板 |
| 6 | 实习/00_Meta_Templates/受控词表.md | 词表 |
| 7 | 实习/00_Meta_Templates/AGENT-README.md | Agent 指南 |
| 8 | 实习/01_Methodology/ | 目录（含 README.md 占位说明） |
| 9 | 实习/知识库管理指南.md | 用户指南 |
| 10 | 实习/飞冰科技/00_INDEX.md | 公司索引 |
| 11 | 实习/飞冰科技/01_Daily_Logs/ | 目录 |
| 12 | 实习/飞冰科技/02_Tech_DeepDive/ | 目录 |
| 13 | 实习/飞冰科技/03_Business_Context/ | 目录 |
| 14 | 实习/飞冰科技/04_Resume_Assets/ | 目录 |
| 15 | 迁移：入职笔记 2 篇 → 实习/飞冰科技/draft/ | 迁移 |

### Definition of Done
- [ ] 上述 15 项交付全部落地
- [ ] 每个模板文件头部含标准 YAML Frontmatter（title/date/status/tags/tech_stack/ai_agent_context 6 字段）
- [ ] 每个模板/指南文件底部含 `## Changelog` 小节
- [ ] 受控词表含 tech_stack 与 tags 的推荐枚举
- [ ] AGENT-README 与 知识库管理指南 内容完整、相互引用（职责区分清晰）
- [ ] 入职笔记已迁入 draft/，旧路径无残留
- [ ] rules.yaml 含新协作习惯规则
- [ ] 端到端验证通过（目录/字段/迁移/规则/禁止项全查）

### Must Have
- 模板与内容分离：模板只存在于 `00_Meta_Templates/`，公司层不复制
- 统一 status 三态：`draft / processing / done`
- 每个模板/指南文件底部含 `## Changelog` 小节
- 索引页 `飞冰科技/00_INDEX.md` 作为公司入口
- 协作习惯经 self-improving-agent 机制沉淀（不写入知识库 markdown）
- 每日复盘方案 A：`每日复盘/` 只放链接（本次不修改现有每日复盘文件，仅在指南中写明约定）

### Must NOT Have (Guardrails)
- 不创建 `Internship_KB` 独立根目录（避免双体系）
- 不创建 v1.md / v2.md 等版本副本
- 不修改 vault 根 `笔记体系方案.md` / `知识沉淀使用指南.md`
- 不改动 `八股/` 目录及旧体系 status 语义（80%/100%）
- 不重建/不修改 Obsidian MCP 配置、`knowledge-precipitation` skill 文件、`self-improving-agent` skill 文件本身
- 不把协作习惯记录写入知识库 markdown（只能写 rules.yaml）
- 不删除 `飞冰科技/入职笔记/` 中的原始文件内容（只移动位置）
- 不创建示例业务笔记（00_INDEX 内的示例片段除外）——避免编造业务内容

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: NO（知识库为 markdown 文件，无单元测试框架）
- **Automated tests**: None
- **Agent-Executed QA**: MANDATORY — Bash（Test-Path / Get-ChildItem / Select-String）+ grep + Read 验证文件存在性、frontmatter 字段、目录结构、迁移、规则

### QA Policy
- **目录结构验证**：Bash `Test-Path` 逐项核对（见 Success Criteria 命令）
- **Frontmatter 验证**：grep `^ai_agent_context:` 及 6 字段逐一核对
- **Changelog 验证**：grep `## Changelog` 每个模板/指南文件
- **迁移验证**：旧路径 `入职笔记/` 为空或不存在；新路径 `draft/` 下有 2 个文件
- **规则验证**：`Select-String ~/.agent-improvement/rules.yaml -Pattern "<规则关键词>"`
- **禁止项验证**：全库 grep 确认无 `Internship_KB`、无 `-v1.` `-v2.` 文件
- 证据保存至 `.sisyphus/evidence/task-{N}-{slug}.txt`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - 目录骨架 + 模板 + 词表，MAX PARALLEL 6):
├── Task 1: 创建目录骨架 [quick]
├── Task 2: daily-log 模板 [quick]
├── Task 3: tech-deepdive 模板 [quick]
├── Task 4: business-context 模板 [quick]
├── Task 5: resume-asset 模板 [quick]
└── Task 6: 受控词表 [quick]

Wave 2 (After Wave 1 - 指南 + 索引 + 迁移):
├── Task 7: AGENT-README.md（依赖 2-6）[writing]
├── Task 8: 知识库管理指南.md（依赖 1, 2-6）[writing]
├── Task 9: 飞冰科技/00_INDEX.md（依赖 1）[quick]
└── Task 10: 迁移入职笔记 → draft/（依赖 1）[quick]

Wave 3 (After Wave 2 - 习惯沉淀 + 端到端验证):
├── Task 11: self-improving-agent 协作习惯记录（独立）[quick]
└── Task 12: 端到端验证（依赖 1-11）[unspecified-high]

Final Wave (ALL - 4 review agents in parallel):
├── F1: Plan Compliance Audit [oracle]
├── F2: Content Quality Review [unspecified-high]
├── F3: Real Manual QA [unspecified-high]
└── F4: Scope Fidelity Check [deep]
```

### Dependency Matrix
- **1**: 无 → blocks 8, 9, 10, 12
- **2-6**: 无 → block 7, 8, 12
- **7**: 2-6 → blocks 12
- **8**: 1, 2-6 → blocks 12
- **9**: 1 → blocks 12
- **10**: 1 → blocks 12
- **11**: 无 → blocks 12
- **12**: 1-11 → F1-F4

---

## TODOs

### Task 1: 创建目录骨架
- **Profile**: quick
- **Parallelization**: Wave 1，与 2-6 并行（目录先行，其余任务写文件时自动创建文件，不冲突）
- **References**: Context.Interview Summary #1, #2, #6
- **What to do**: 用 Bash `New-Item -ItemType Directory -Force` 创建：
  - `实习/00_Meta_Templates/`
  - `实习/01_Methodology/`（并在其中创建 `README.md` 占位，说明此区用途：通用方法论，不绑定公司）
  - `实习/飞冰科技/01_Daily_Logs/`
  - `实习/飞冰科技/02_Tech_DeepDive/`
  - `实习/飞冰科技/03_Business_Context/`
  - `实习/飞冰科技/04_Resume_Assets/`
  - 确认 `实习/飞冰科技/draft/` 已存在（存在则不动）
  - **不得**创建 `Internship_KB` 目录
- **Acceptance Criteria**: 上述 6+1 目录存在；无 Internship_KB
- **QA Scenarios**:
  - Q1.1: `Test-Path` 每个目录 → 全 True
  - Q1.2: `Test-Path 实习/Internship_KB` → False
  - Q1.3: `Test-Path 实习/01_Methodology/README.md` → True
- **Evidence**: `.sisyphus/evidence/task-1-dirs.txt`
- **Commit**: 与 2-6 合并 `docs(实习知识库): 创建目录骨架与四类模板及受控词表`

### Task 2: daily-log 模板
- **Profile**: quick
- **Parallelization**: Wave 1
- **References**: 方案"元数据规范"、方案"沉淀工作流·日维度"
- **What to do**: 创建 `实习/00_Meta_Templates/daily-log-template.md`：
  - YAML Frontmatter 6 字段：title / date / status(draft|processing|done) / tags(含 实习/飞冰科技 等层级标签) / tech_stack(列表) / ai_agent_context(一句话语义提示)
  - 正文骨架：`## 🎯 今日任务`（checkbox 列表，含需求/Ticket ID）、`## 🐛 踩坑与排查`（现象/报错日志/解决思路）、`## 🤖 AI 协作记录`（好用的 Prompt 记录）、`## 明日计划`
  - 底部 `## Changelog` 小节（版本号 + 日期 + 变更摘要 + 原因）
- **Acceptance Criteria**: 6 字段齐全；含 Changelog；结构与方案一致
- **QA Scenarios**:
  - Q2.1: grep `^ai_agent_context:` → 命中
  - Q2.2: grep `^status:` + 内容含 draft/processing/done 之一 → 命中
  - Q2.3: grep `## Changelog` → 命中
  - Q2.4: grep `## 🎯 今日任务` 与 `## 🤖 AI 协作记录` → 命中
- **Evidence**: `.sisyphus/evidence/task-2-daily-template.txt`
- **Commit**: 合并 commit 1

### Task 3: tech-deepdive 模板
- **Profile**: quick
- **Parallelization**: Wave 1
- **References**: 方案"沉淀工作流·周维度"
- **What to do**: 创建 `实习/00_Meta_Templates/tech-deepdive-template.md`：
  - YAML Frontmatter 6 字段
  - 正文骨架：`## 背景与动机`（从哪些日志提炼）、`## 架构/方案图解`（Mermaid 时序图/流程图占位）、`## 核心代码与规范`（最佳实践：公司封装方式 / 避坑指南：为什么不直接用常规写法）、`## 复盘结论`
  - 底部 `## Changelog`
- **Acceptance Criteria**: 6 字段齐全；含 Mermaid 代码块示例；含 Changelog
- **QA Scenarios**:
  - Q3.1: grep `^ai_agent_context:` → 命中
  - Q3.2: grep "```mermaid" → 命中
  - Q3.3: grep `## Changelog` → 命中
  - Q3.4: grep `## 避坑指南` → 命中
- **Evidence**: `.sisyphus/evidence/task-3-tech-template.txt`
- **Commit**: 合并 commit 1

### Task 4: business-context 模板
- **Profile**: quick
- **Parallelization**: Wave 1
- **References**: 方案"以公司为模块"、03_Business_Context 语义
- **What to do**: 创建 `实习/00_Meta_Templates/business-context-template.md`：
  - YAML Frontmatter 6 字段
  - 正文骨架：`## 业务模块概述`、`## 核心实体关系`（Mermaid erDiagram 占位）、`## 数据流`（Mermaid 流程图占位）、`## 状态机`（Mermaid stateDiagram 占位）、`## 与代码的对应关系`（提示：剥离代码只记结构与关系）
  - 底部 `## Changelog`
- **Acceptance Criteria**: 6 字段齐全；含 erDiagram/stateDiagram 占位；含 Changelog
- **QA Scenarios**:
  - Q4.1: grep `^ai_agent_context:` → 命中
  - Q4.2: grep "erDiagram" → 命中
  - Q4.3: grep "stateDiagram" → 命中
  - Q4.4: grep `## Changelog` → 命中
- **Evidence**: `.sisyphus/evidence/task-4-business-template.txt`
- **Commit**: 合并 commit 1

### Task 5: resume-asset 模板
- **Profile**: quick
- **Parallelization**: Wave 1
- **References**: 方案"沉淀工作流·月维度"（STAR）
- **What to do**: 创建 `实习/00_Meta_Templates/resume-asset-template.md`：
  - YAML Frontmatter 6 字段（tags 含 实习/飞冰科技 + 简历资产；tech_stack 含涉及技术）
  - 正文骨架：`## STAR` 下四小节：`**Situation**`、`**Task**`、`**Action**`、`**Result**`（含量化结果占位：接口响应时间降低 X%、代码提效 X%）、`## 面试追问准备`（可能被追问的问题）、`## 相关笔记链接`
  - 底部 `## Changelog`
- **Acceptance Criteria**: 6 字段齐全；含 STAR 四要素；含 Changelog
- **QA Scenarios**:
  - Q5.1: grep `^ai_agent_context:` → 命中
  - Q5.2: grep "Situation" / "Task" / "Action" / "Result" → 全部命中
  - Q5.3: grep `## Changelog` → 命中
- **Evidence**: `.sisyphus/evidence/task-5-resume-template.txt`
- **Commit**: 合并 commit 1

### Task 6: 受控词表
- **Profile**: quick
- **Parallelization**: Wave 1
- **References**: 方案"元数据规范"、风险"词表漂移"
- **What to do**: 创建 `实习/00_Meta_Templates/受控词表.md`：
  - 说明：所有笔记的 tech_stack / tags 取值以此为准（写 SpringBoot 不写 spring boot）
  - `tech_stack` 推荐枚举：Java, SpringBoot, SpringCloud, MyBatis-Plus, MySQL, Redis, RocketMQ/Kafka, Docker, Git, 其他(补充时追加并标注日期)
  - `tags` 推荐枚举：公司层（实习/飞冰科技）、类型层（BugFix / Feature / 优化 / 调研）、主题层示例（实习/飞冰科技/订单、实习/飞冰科技/鉴权）
  - 追加规范：新增词 → 在此登记 + 加日期
  - 底部 `## Changelog`
- **Acceptance Criteria**: 含 tech_stack 与 tags 两组枚举；含追加规范；含 Changelog
- **QA Scenarios**:
  - Q6.1: grep "tech_stack" → 命中
  - Q6.2: grep "tags" → 命中
  - Q6.3: grep `## Changelog` → 命中
  - Q6.4: grep "SpringBoot" → 命中
- **Evidence**: `.sisyphus/evidence/task-6-vocab.txt`
- **Commit**: 合并 commit 1

### Task 7: AGENT-README（给 Agent 看的指南）
- **Profile**: writing
- **Parallelization**: Wave 2（依赖 2-6）
- **References**: 方案"Agent 协作协议"、Deliverables #7
- **What to do**: 创建 `实习/00_Meta_Templates/AGENT-README.md`：
  - 本库定位与数据结构说明（目录语义：00 模板/元数据、01 方法论、公司模块下 01-04 含义）
  - Frontmatter 字段语义表（title/date/status/tags/tech_stack/ai_agent_context 各自含义与取值来源）
  - **推荐读取顺序**：AGENT-README → 受控词表 → 目标公司 00_INDEX.md → 按 frontmatter 检索
  - **协作协议**（重要）：与用户对齐需求时遵循"先理解 → 对齐 → 建议 → 确认 → 方案"；用户操作习惯记录在 self-improving-agent（rules.yaml），本库不重复存
  - 检索建议：按 tech_stack / tags / status 过滤示例
  - 底部 `## Changelog`
- **Acceptance Criteria**: 含目录语义表、字段语义表、读取顺序、协作协议、Changelog
- **QA Scenarios**:
  - Q7.1: grep "ai_agent_context" → 命中（字段语义表内）
  - Q7.2: grep "读取顺序" 或 "read order" → 命中
  - Q7.3: grep "先理解" → 命中（协作协议）
  - Q7.4: grep `## Changelog` → 命中
- **Evidence**: `.sisyphus/evidence/task-7-agent-readme.txt`
- **Commit**: commit 2

### Task 8: 知识库管理指南（给用户本人看的）
- **Profile**: writing
- **Parallelization**: Wave 2（依赖 1, 2-6）
- **References**: 方案"知识库管理指南"、决策 #4/#7/#9
- **What to do**: 创建 `实习/知识库管理指南.md`：
  - 目录结构总览（含每个目录"放什么/不放什么"）
  - 日/周/月工作流说明（何时写、写哪、用哪个模板、耗时预期）
  - 每日复盘约定（方案 A：实习日记录写公司 01_Daily_Logs，每日复盘/当天只放链接）
  - **改进与溯源流程**：改模板 → 先复制到 draft/ 写新版 → 定稿替换正本 → 文件底部追加 Changelog 条目 → git commit（message 写清"改了啥、为什么"）；普通笔记只增不改
  - 溯源方法：旧版全文看 git log/show；演进逻辑看文件内 Changelog
  - 引用 AGENT-README（说明二者分工：本指南给人，AGENT-README 给 Agent）
  - 底部 `## Changelog`
- **Acceptance Criteria**: 含工作流、改进/溯源流程、与 AGENT-README 的互引、Changelog
- **QA Scenarios**:
  - Q8.1: grep "工作流" → 命中
  - Q8.2: grep "Changelog" → 命中（改进流程中）
  - Q8.3: grep "AGENT-README" → 命中（互引）
  - Q8.4: grep "git" → 命中（溯源流程）
  - Q8.5: grep `## Changelog` → 命中
- **Evidence**: `.sisyphus/evidence/task-8-user-guide.txt`
- **Commit**: commit 2

### Task 9: 飞冰科技/00_INDEX.md（公司入口）
- **Profile**: quick
- **Parallelization**: Wave 2（依赖 1）
- **References**: 方案"公司模块"、Context 现状
- **What to do**: 创建 `实习/飞冰科技/00_INDEX.md`：
  - YAML Frontmatter 6 字段（status: done，ai_agent_context 描述公司入口定位）
  - 正文：公司背景占位、入职时间、团队/项目总览占位、**子目录索引链接**（[[01_Daily_Logs]]、[[02_Tech_DeepDive]]、[[03_Business_Context]]、[[04_Resume_Assets]]、[[draft]]）、指向 `00_Meta_Templates/受控词表` 的说明
  - 底部 `## Changelog`
  - **不得**编造具体业务内容（全部占位符标注"待补充"）
- **Acceptance Criteria**: 6 字段齐全；含子目录索引链接；含 Changelog；无编造业务
- **QA Scenarios**:
  - Q9.1: grep `^ai_agent_context:` → 命中
  - Q9.2: grep "01_Daily_Logs" / "03_Business_Context" → 命中
  - Q9.3: grep `## Changelog` → 命中
- **Evidence**: `.sisyphus/evidence/task-9-company-index.txt`
- **Commit**: commit 2

### Task 10: 迁移入职笔记 → draft/
- **Profile**: quick
- **Parallelization**: Wave 2（依赖 1）
- **References**: 决策 #3、Research Findings
- **What to do**: 用 Bash `Move-Item` 迁移：
  - `实习/飞冰科技/入职笔记/入职后初期注意事项.md` → `实习/飞冰科技/draft/`
  - `实习/飞冰科技/入职笔记/feibing-neo 初步了解.md` → `实习/飞冰科技/draft/`
  - 迁移后删除空的 `入职笔记/` 目录（`Remove-Item` 仅当为空）
  - **不得**修改文件内容、**不得**删除文件
- **Acceptance Criteria**: draft/ 下 2 个文件存在；入职笔记/ 目录不存在或为空
- **QA Scenarios**:
  - Q10.1: `Test-Path 实习/飞冰科技/draft/入职后初期注意事项.md` → True
  - Q10.2: `Test-Path 实习/飞冰科技/draft/feibing-neo 初步了解.md` → True
  - Q10.3: `Test-Path 实习/飞冰科技/入职笔记` → False（或目录为空）
  - Q10.4: 两文件内容未变（对比大小或哈希，至少确认仍含原文件名标题）
- **Evidence**: `.sisyphus/evidence/task-10-migration.txt`
- **Commit**: commit 3

### Task 11: self-improving-agent 协作习惯记录
- **Profile**: quick
- **Parallelization**: Wave 3（独立，可与 12 并行；但建议先于 12 便于验证）
- **References**: 决策 #8、Research Findings（skill 路径、improve.py 用法）
- **What to do**: 运行（workdir 任意，用 uv）：
  ```
  uv run C:\Users\施鸿福\.agents\skills\self-improving-agent\scripts\improve.py observe "When aligning requirements with the user, first present your understanding, wait for the user's alignment before giving suggestions, and only produce the plan after explicit confirmation" --project opencode-setup --domain communication --context "user's fixed operational habit: 先理解→对齐→建议→确认→方案; confirmed during internship KB planning 2026-08-22"
  ```
  - **不得**手工编辑 rules.yaml（让 improve.py 写入）
  - **不得**将规则写入知识库 markdown
- **Acceptance Criteria**: `~/.agent-improvement/rules.yaml` 含新规则（含关键词"alignment"或"先理解"或"confirmation"）
- **QA Scenarios**:
  - Q11.1: `Select-String -Path ~/.agent-improvement/rules.yaml -Pattern "understanding|先理解|confirmation"` → 命中
  - Q11.2: rules.yaml 可解析（YAML 结构未被破坏，可再跑一次 `uv run improve.py observe` 查看无报错，或读文件头部）
- **Evidence**: `.sisyphus/evidence/task-11-habit.txt`
- **Commit**: commit 4

### Task 12: 端到端验证
- **Profile**: unspecified-high
- **Parallelization**: Wave 3（依赖 1-11）
- **References**: Verification Strategy、Success Criteria
- **What to do**: 执行全部 QA 场景复核（Success Criteria 的命令 + 每个 Task 的关键 QA），汇总结果，保存证据到 `.sisyphus/evidence/task-12-e2e.txt`。逐项：
  - 目录结构 6+1 存在、无 Internship_KB
  - 4 模板 + 受控词表 + AGENT-README + 知识库管理指南 + 00_INDEX：frontmatter 6 字段、Changelog 存在
  - 迁移完成（旧路径无残留）
  - rules.yaml 新规则存在
  - 禁止项扫描：无 v1/v2 副本、未触碰 笔记体系方案.md / 知识沉淀使用指南.md（用 git status/diff 核对改动文件清单）
- **Acceptance Criteria**: 全部通过；输出核对清单
- **QA Scenarios**: 见 Success Criteria Verification Commands（全部执行）
- **Evidence**: `.sisyphus/evidence/task-12-e2e.txt`
- **Commit**: 无需（纯验证，若有修复则随修复 commit）

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing. Do NOT auto-proceed after verification.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  通读计划，逐条核对 Must Have / Must NOT Have 的实际实现（Read 文件 + grep 禁止项），检查 evidence 文件存在性。输出：`Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT`

- [ ] F2. **Content Quality Review** — `unspecified-high`
  读取全部新文件。检查：frontmatter 6 字段齐全、Changelog 存在、无 AI-slop（空泛命名、过度注释）、4 模板风格一致、AGENT-README 与知识库管理指南互引正确、受控词表可用。输出：`Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  执行每个 Task 的 QA 场景（含最终验证命令），捕获证据到 `.sisyphus/evidence/final-qa/`。输出：`Scenarios [N/N pass] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  逐 Task 核对 spec vs 实际 diff（git log/diff），确认无遗漏、无越界、无跨任务污染、Must NOT do 合规。输出：`Tasks [N/N compliant] | Contamination [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

- **1-6**: `docs(实习知识库): 创建目录骨架与四类模板及受控词表`
- **7-9**: `docs(实习知识库): 添加 AGENT 指南、用户指南与公司索引`
- **10**: `docs(实习知识库): 迁移入职笔记至 draft 草稿箱`
- **11**: `chore(habits): 记录协作习惯到 self-improving-agent 规则`

---

## Success Criteria

### Verification Commands
```bash
# 目录结构
Test-Path 实习/00_Meta_Templates, 实习/01_Methodology
Test-Path 实习/飞冰科技/01_Daily_Logs, 实习/飞冰科技/02_Tech_DeepDive
Test-Path 实习/飞冰科技/03_Business_Context, 实习/飞冰科技/04_Resume_Assets
Test-Path 实习/飞冰科技/draft
# Frontmatter 字段（4 模板 + 00_INDEX 均应命中 ai_agent_context）
grep -l "^ai_agent_context:" 实习/00_Meta_Templates/*.md 实习/飞冰科技/00_INDEX.md
# Changelog 全覆盖
grep -l "## Changelog" 实习/00_Meta_Templates/*.md 实习/知识库管理指南.md 实习/飞冰科技/00_INDEX.md
# 迁移完成
Test-Path 实习/飞冰科技/draft/入职后初期注意事项.md
Test-Path 实习/飞冰科技/draft/feibing-neo 初步了解.md
# 规则已记录
Select-String -Path "$HOME/.agent-improvement/rules.yaml" -Pattern "confirmation|先理解"
# 禁止项扫描
Test-Path 实习/Internship_KB   # 应为 False
```

### Final Checklist
- [ ] 所有 Must Have 满足
- [ ] 所有 Must NOT Have 未违反
- [ ] 全部 QA 场景通过、证据存在
- [ ] 用户对最终结果给出明确 "okay"
