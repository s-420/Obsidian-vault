# AI Interview Platform - MiniMax 集成总结

## 背景目标

将 AI 面试平台的 LLM 提供商从 DashScope 切换到 MiniMax，并验证功能正常。

## 问题诊断

### 根本原因分析

1. **环境变量映射错误**（已修复）
   - `docker-compose.yml` 将 `MINIMAX_API_KEY` 错误映射为 `AI_BAILIAN_API_KEY`

2. **MiniMax API 404 错误**
   - Spring AI 的 `OpenAiApi` 会调用 `/v1/models` 端点进行验证
   - MiniMax 不支持此端点，返回 404
   - 直接调用 `/v1/chat/completions` 端点没问题

### 方案 A - 添加 MiniMax-Group-ID header（失败，已回滚）

- 修改 `LlmProviderRegistry.java` 添加 `MiniMax-Group-ID` header
- 添加 `MINIMAX_GROUP_ID` 环境变量
- **结果**：仍然 404，已回滚

### 方案 B - Spring AI 原生 MiniMax 配置（遇到冲突，未完成）

1. 添加 `spring-ai-starter-model-minimax` 依赖
2. 修改 `application.yml` 添加 `spring.ai.minimax.*` 配置
3. 修改 `LlmProviderRegistry.java` 使用 `MiniMaxChatModel`
4. 遇到 Spring AI 自动配置冲突问题

### 问题详情

Spring AI 自动配置同时创建了两个 ChatModel bean：
- `miniMaxChatModel` (MiniMaxChatAutoConfiguration)
- `openAiChatModel` (OpenAiChatAutoConfiguration)

导致 `ChatClientAutoConfiguration` 注入时产生冲突：

```
No qualifying bean of type 'org.springframework.ai.chat.model.ChatModel' available: 
expected single matching bean but found 2: miniMaxChatModel,openAiChatModel
```

## 最终结果

**已回滚所有修改**，保持原始 DashScope 配置正常运行。

## 敏感信息配置机制

项目使用 `.env` 文件存储敏感信息，通过以下方式读取：

### 1. 存储位置

```bash
# .env 文件
AI_BAILIAN_API_KEY=sk-xxx
```

### 2. 读取方式

**本地开发 (`./gradlew bootRun`)**：

`build.gradle` 第 115-133 行实现 .env 加载：

```groovy
def envFile = rootProject.file('.env')
if (envFile.exists()) {
    envFile.eachLine { line ->
        def key = trimmed.substring(0, eq).trim()
        def val = trimmed.substring(eq + 1).trim()
        environment key, val  // 注入为环境变量
    }
}
```

**Docker Compose**：

`docker-compose.yml`：
```yaml
environment:
  AI_BAILIAN_API_KEY: ${AI_BAILIAN_API_KEY}  # 从宿主机环境变量读取
```

### 3. 应用读取

`application.yml` 使用 `${VAR_NAME:-默认值}` 语法：

```yaml
ai:
  openai:
    api-key: ${AI_BAILIAN_API_KEY}
```

### 流程图

```
.env 文件 → bootRun (build.gradle) → 环境变量
          → docker-compose.yml → 容器环境变量
          → Spring Boot application.yml → 应用配置
```

## 当前状态

- ✅ AI 配置正常（DashScope）
- ✅ App 启动成功
- ✅ TTS/ASR 服务正常
- ❌ MiniMax 集成未完成

## 下次尝试建议

1. 只排除 `MiniMaxChatAutoConfiguration`，保留 `ChatClientAutoConfiguration`
2. 或手动管理所有 ChatModel bean 的创建
3. 使用 Spring AI 原生 `MiniMaxApi` 和 `MiniMaxChatModel`

---

*最后更新: 2026-04-20*
