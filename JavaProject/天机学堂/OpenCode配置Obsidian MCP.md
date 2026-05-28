---
title: OpenCode配置Obsidian MCP与知识沉淀Skill
tags: [OpenCode, Obsidian, MCP, Skill, 知识管理]
created: 2026-05-28
updated: 2026-05-28
status: 100%
related: [[Springfox迁移OpenAPI3]]
---

# OpenCode 配置 Obsidian MCP 与知识沉淀 Skill

## 1. 业务场景与核心诉求

在 OpenCode 中集成 Obsidian 知识库，实现：
- 对话中的技术知识自动沉淀到 Obsidian
- 通过 MCP 协议读写 Obsidian 笔记
- 封装为 Skill 实现标准化工作流

## 2. 最终落地方案 & 核心代码

### 2.1 Obsidian MCP Server 配置

**前置条件**：Obsidian 安装 "Local REST API" 插件

```json
// opencode.json
{
  "mcp": {
    "obsidian": {
      "command": ["npx", "-y", "mcp-obsidian"],
      "args": ["http://localhost:27123"],
      "env": {
        "OBSIDIAN_API_KEY": "Bearer {your-api-key}"
      },
      "enabled": true,
      "type": "local"
    }
  }
}
```

### 2.2 知识沉淀 Skill 结构

```
skills/
└── knowledge-precipitation/
    └── SKILL.md
```

**Skill 核心流程**：
1. 回顾对话，提取核心技术点
2. 搜索 Obsidian 检查是否已有相似笔记
3. 生成标准格式笔记（含 frontmatter）
4. 写入对应项目目录
5. 更新每日日记（只放链接）

### 2.3 目录结构设计

```
Obsidian-vault/
├── JavaProject/              # 项目相关
│   └── {项目名}/
│       ├── 技术点/           # 具体知识点
│       ├── 接口文档/         # 接口相关
│       └── 架构设计/         # 架构设计
│
├── 八股文/                   # 面试知识
│
├── 每日复盘/                 # 每日汇总（只放链接）
│   └── YYYY-MM-DD.md
│
└── _inbox/                   # 临时收件箱
```

### 2.4 笔记模板

```markdown
---
title: {标题}
tags: [{标签1}, {标签2}]
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
status: draft
related: [[相关笔记]]
---

# {标题}

## 1. 业务场景与核心诉求
{问题描述}

## 2. 最终落地方案 & 核心代码
{解决方案 + 代码}

## 3. 原理剖析与踩坑记录
{原理 + 踩坑}
```

## 3. 原理剖析与踩坑记录

### 3.1 MCP 工作原理

```
OpenCode ──stdio──► MCP Server ──HTTP──► Obsidian REST API ──► Vault
```

- MCP Server 是桥梁，将 AI 的工具调用转换为 HTTP 请求
- Obsidian Local REST API 插件提供 HTTP 接口
- 端口默认 27123

### 3.2 两种写入方式

| 方式 | 优点 | 缺点 |
|------|------|------|
| MCP Server | 搜索、链接解析、智能去重 | 需要重启 OpenCode |
| 直接文件写入 | 立即可用、无依赖 | 不能搜索已有笔记 |

### 3.3 踩坑记录

**坑1：MCP 配置后需要重启**
- 修改 `opencode.json` 后必须重启 OpenCode
- 不重启无法加载新的 MCP server

**坑2：Obsidian 必须保持运行**
- Local REST API 插件只在 Obsidian 运行时工作
- 关闭 Obsidian 后 MCP 调用会失败

**坑3：API Key 格式**
- 需要包含 "Bearer " 前缀
- 示例：`Bearer 906bf8759a0836ef...`

**坑4：Skill 不会自动触发**
- 设计为手动触发（说 "执行知识沉淀"）
- 避免产生大量碎片笔记
