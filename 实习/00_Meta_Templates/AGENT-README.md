---
title: AGENT-README（给 AI Agent 的读取指南）
date: 2026-08-22
status: done
tags:
  - 实习/元数据
tech_stack:
  - Java
  - SpringBoot
ai_agent_context: "本文件是所有 AI Agent（Cline/OpenCode/MCP）读取实习知识库的入口：目录语义、frontmatter 字段语义、推荐读取顺序与协作协议"
---

# AGENT-README

> 本文件是 AI Agent 读取本知识库的**第一站**。读取顺序见下文。

## 一、目录语义

| 路径 | 内容 | Agent 用途 |
|------|------|-----------|
| `00_Meta_Templates/` | 模板、受控词表、本文件 | 理解数据结构与元数据规范 |
| `01_Methodology/` | 通用方法论（不绑定公司） | 通用经验检索 |
| `飞冰科技/00_INDEX.md` | 公司入口：背景/团队/项目 | 公司级上下文 |
| `飞冰科技/01_Daily_Logs/` | 每日日志 | 当日进展、踩坑、AI 协作 |
| `飞冰科技/02_Tech_DeepDive/` | 技术专题 | 技术方案细节与选型 |
| `飞冰科技/03_Business_Context/` | 业务逻辑与架构 | 数据流/实体/状态机 |
| `飞冰科技/04_Resume_Assets/` | STAR 简历资产 | 简历与面试 |
| `飞冰科技/draft/` | 草稿箱 | 未定稿内容，可信度低 |

## 二、Frontmatter 字段语义

| 字段 | 含义 | 取值来源 |
|------|------|---------|
| `title` | 笔记标题 | 自由 |
| `date` | 日期 YYYY-MM-DD | 创建日 |
| `status` | 三态：draft / processing / done | 定稿进度 |
| `tags` | 层级标签（公司/类型/文档/主题） | 见受控词表 |
| `tech_stack` | 技术栈列表 | 见受控词表 |
| `ai_agent_context` | 一句话语义提示：本篇能回答什么问题 | 创建时填写 |

## 三、推荐读取顺序

```
AGENT-README → 受控词表.md → 目标公司/00_INDEX.md → 按 frontmatter 过滤检索
```

## 四、协作协议

与用户对齐需求时，**必须**遵循：
1. 先给出你的理解
2. 对齐后再给建议
3. 确认后才出方案

> 用户的这一操作习惯已记录在 self-improving-agent（~/.agent-improvement/rules.yaml），本库不重复存放。

## 五、检索建议

- 按技术栈过滤：`tech_stack` 含 `Redis` 的笔记
- 按状态过滤：优先 `status: done` 的定稿内容
- 按类型过滤：`tags` 含 `BugFix` 的踩坑记录
- 业务问题优先查 `03_Business_Context`，技术实现查 `02_Tech_DeepDive`

## Changelog
- v1.0 (2026-08-22)：初始版本，基于实习知识库方案创建

