# 飞冰科技实习 — 项目长期约定

## 四个"记录类" skill 的分工（2026-09-07 明确，别再混）

| skill | 用途 | 落盘？ | 输出形态 |
|---|---|---|---|
| `daily-ledger` | 白天实时记账，原料层 | ✅ `D:\AgentRules\ledger\YYYY-MM-DD.md` | 每完成一个目标追加一条（时间/目标/agent/状态/产物/待办） |
| `write-daily-summary` | **知识型日志**，沉淀进 Obsidian | ✅ `01_Daily_Logs/YYYY-MM-DD/YYYY-MM-DD.md` | Markdown，含 frontmatter、今日任务、踩坑、总结、AI 协作、明日计划、相关文档、Changelog |
| `write-daily-report` | **公司日报**，提交给 mentor/领导 | ❌ **不生成任何文件** | 对话内纯文字，无 Markdown 标记 |
| `write-weekly-report` | **公司周报**，跨天合并成果主线 | 按 skill 要求 | 可直接提交的周报 |

关系：`daily-ledger`（原料）→ 晚上按需要分别喂给 `write-daily-summary`（知识沉淀）或 `write-daily-report`（公司汇报）。**"日志"和"日报"是两条线，不要混用。**

### write-daily-report（公司日报）硬规则

- **只在对话里输出纯文字，不生成任何文件**（用户 2026-09-07 明确指出；曾因落文件被纠正）。
- 不用 Markdown 标记（无 `#`、`**`、列表符号），可直接复制到日报系统。
- 模板：标题「工作日报 YYYY年M月D日」→ 姓名：施鸿福 → 日期 → 今日工作内容 → 今日总结 → 明日计划。
- 每条 = 小标题（体现"做成了/会了"，禁止"学习了/了解了/协助了"）+ 1-3 句含对象、做法、结果/验证。
- 今日总结含成果 + 具体不足 + 下一步；明日计划可执行可验收。
- 日报正文外不加前言、解释或结尾话术。

### write-daily-summary（知识日志）硬规则

- frontmatter 必填：title / date / status(draft|done) / tags / tech_stack / ai_agent_context。
- 固定章节：今日任务、踩坑与排查、今日总结、AI 协作记录、明日计划、相关文档、Changelog。
- 完成状态只认验收证据，文件存在或 agent 自述不算完成；状态不明标"待确认"。
- **不写手机号、Token、客户个人资料**等敏感信息；批量/删除/不可逆操作要写清二次确认、备份、影响范围与回滚条件。
- 相关文档链接用相对路径并逐个验证存在。

## 工作习惯

- 用户用中文沟通，回复用中文。
- 先对齐需求再动手；完成后汇报，确认后再进入下一项。
- 临时脚本写到 `C:\Users\施鸿福\AppData\Local\Temp\`，用完即删。
