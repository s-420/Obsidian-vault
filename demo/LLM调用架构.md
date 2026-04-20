# AI Interview Platform LLM 调用架构

## 四层调用架构

```
配置绑定 → 实例化客户端 → 内部服务封装 → 外部调用
```

---

## 第一层：配置绑定

### `application.yml` 中的 AI 配置

```yaml
app:
  ai:
    default-provider: dashscope                    # 默认 provider
    providers:
      dashscope:
        base-url: https://dashscope.aliyuncs.com/compatible-mode
        api-key: ${AI_BAILIAN_API_KEY}            # 环境变量注入
        model: qwen-plus
      lmstudio:
        base-url: http://localhost:1234
        api-key: lm-studio
        model: qwen2.5-7b-instruct
    advisors:
      enabled: true
      tool-call-enabled: true                     # 启用 ToolCall
```

### `LlmProviderProperties` 绑定配置

```java
@Data
@Component
@ConfigurationProperties(prefix = "app.ai")  // ← 绑定 app.ai.* 配置
public class LlmProviderProperties {
    private String defaultProvider;
    private Map<String, ProviderConfig> providers;
    private AdvisorConfig advisors;
    
    @Data
    public static class ProviderConfig {
        private String baseUrl;
        private String apiKey;
        private String model;
    }
}
```

---

## 第二层：实例化客户端

### `LlmProviderRegistry` - ChatClient 工厂

```java
@Component
@Slf4j
public class LlmProviderRegistry {
    
    // 客户端缓存（线程安全）
    private final Map<String, ChatClient> clientCache = new ConcurrentHashMap<>();
    
    /**
     * 获取 ChatClient（懒加载 + 缓存）
     */
    public ChatClient getChatClient(String providerId) {
        return clientCache.computeIfAbsent(providerId, id -> createChatClient(id));
    }
    
    public ChatClient getDefaultChatClient() {
        return getChatClient(properties.getDefaultProvider());
    }
    
    /**
     * 创建 ChatClient
     */
    private ChatClient createChatClient(String providerId) {
        // 1. 构建 ChatModel
        OpenAiChatModel chatModel = buildChatModel(providerId);
        
        // 2. 构建 Builder
        ChatClient.Builder builder = ChatClient.builder(chatModel);
        
        // 3. 配置 ToolCallback（Agent 工具调用）
        if (interviewSkillsToolCallback != null) {
            builder.defaultToolCallbacks(interviewSkillsToolCallback);
        }
        
        // 4. 配置 Advisors（记忆、日志等）
        List<Advisor> advisors = buildDefaultAdvisors(providerId);
        if (!advisors.isEmpty()) {
            builder.defaultAdvisors(advisors.toArray(new Advisor[0]));
        }
        
        return builder.build();
    }
    
    /**
     * 构建 OpenAiChatModel
     */
    private OpenAiChatModel buildChatModel(String providerId) {
        ProviderConfig config = properties.getProviders().get(providerId);
        
        // OpenAI 兼容 API
        OpenAiApi openAiApi = OpenAiApi.builder()
            .baseUrl(config.getBaseUrl())
            .apiKey(config.getApiKey())
            .build();
        
        OpenAiChatOptions options = OpenAiChatOptions.builder()
            .model(config.getModel())
            .temperature(0.2)
            .build();
        
        return new OpenAiChatModel(openAiApi, options, ...);
    }
}
```

### 三种 ChatClient 类型

| 方法 | 用途 | 特点 |
|------|------|------|
| `getChatClient(providerId)` | 普通调用 | Tool + Advisors |
| `getPlainChatClient(providerId)` | 简单调用 | 无 Tool、无 Advisor |
| `getVoiceChatClient(providerId)` | 语音面试 | Tool + 流式 Advisor |

---

## 第三层：内部服务封装

### `StructuredOutputInvoker` - 结构化输出 + 重试

```java
@Component
public class StructuredOutputInvoker {
    
    /**
     * 通用结构化调用
     */
    public <T> T invoke(
        ChatClient chatClient,           // LLM 客户端
        String systemPromptWithFormat,   // 带格式要求的系统 prompt
        String userPrompt,               // 用户 prompt
        BeanOutputConverter<T> outputConverter, // 输出转换器
        ErrorCode errorCode,             // 错误码
        String errorPrefix,              // 错误前缀
        String logContext,               // 日志上下文
        Logger log
    ) {
        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                // 调用 LLM 并直接转换为目标类型
                return chatClient.prompt()
                    .system(systemPromptWithFormat)
                    .user(userPrompt)
                    .call()
                    .entity(outputConverter);  // ← 自动 JSON → Bean
                    
            } catch (Exception e) {
                lastError = e;
                if (attempt < maxAttempts) {
                    // 构建重试 Prompt（注入上次错误原因）
                    systemPromptWithFormat = buildRetrySystemPrompt(...);
                }
            }
        }
        throw new BusinessException(errorCode, errorPrefix + lastError.getMessage());
    }
}
```

### 封装能力

| 能力 | 说明 |
|------|------|
| **结构化输出** | `BeanOutputConverter` 自动将 JSON 转为 Java Bean |
| **自动重试** | 默认 2 次，失败原因注入 Prompt |
| **指标监控** | Micrometer 埋点（invocations、attempts、latency） |
| **错误规范化** | 日志上下文统一化 |

---

## 第四层：外部调用

### 业务 Service 使用示例

```java
@Service
public class ResumeGradingService {
    
    private final ChatClient chatClient;  // 注入默认 client
    private final StructuredOutputInvoker structuredOutputInvoker;
    
    public ResumeGradingService(
            ChatClient.Builder chatClientBuilder,  // ← 注入 ChatClient.Builder
            StructuredOutputInvoker structuredOutputInvoker,
            ...) {
        this.chatClient = chatClientBuilder.build();
        this.structuredOutputInvoker = structuredOutputInvoker;
    }
    
    public ResumeAnalysisResponse analyzeResume(String resumeText) {
        // 1. 构建 Prompt
        String systemPrompt = systemPromptTemplate.render();
        String userPrompt = userPromptTemplate.render(Map.of("resumeText", resumeText));
        
        // 2. 添加 JSON 格式要求
        String systemPromptWithFormat = systemPrompt + "\n\n" + outputConverter.getFormat();
        
        // 3. 调用（自动重试 + 结构化转换）
        ResumeAnalysisResponseDTO dto = structuredOutputInvoker.invoke(
            chatClient,
            systemPromptWithFormat,
            userPrompt,
            outputConverter,
            ErrorCode.RESUME_ANALYSIS_FAILED,
            "简历分析失败：",
            "简历分析",
            log
        );
        
        return convertToResponse(dto);
    }
}
```

### 多 Provider 调用示例

```java
@Service
public class InterviewQuestionService {
    
    private final LlmProviderRegistry llmProviderRegistry;
    
    public void someMethod() {
        // 指定 provider
        ChatClient dashscopeClient = llmProviderRegistry.getChatClient("dashscope");
        
        // 使用默认 provider
        ChatClient defaultClient = llmProviderRegistry.getDefaultChatClient();
        
        // 根据配置选择，无则用默认
        ChatClient client = llmProviderRegistry.getChatClientOrDefault("openai");
    }
}
```

---

## 完整调用链路图

```
┌─────────────────────────────────────────────────────────────────┐
│  application.yml                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ app.ai.default-provider: dashscope                       │   │
│  │ app.ai.providers.dashscope.base-url: https://...          │   │
│  │ app.ai.providers.dashscope.api-key: ${AI_BAILIAN_API_KEY} │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────┘
                                │ @ConfigurationProperties
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  LlmProviderProperties                                          │
│  ├── defaultProvider                                           │
│  ├── providers: {dashscope, lmstudio, ...}                    │
│  └── advisors: {toolCallEnabled, ...}                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │ 创建 / 获取
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  LlmProviderRegistry (ChatClient 工厂)                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ clientCache: ConcurrentHashMap<String, ChatClient>      │    │
│  │                                                          │    │
│  │ getChatClient(providerId) → 缓存未命中 → createClient()   │    │
│  │ getPlainChatClient()      → 无 Tool/Advisor              │    │
│  │ getVoiceChatClient()      → 语音面试专用                  │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────┘
                                │ 注入
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  StructuredOutputInvoker (封装层)                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ invoke()                                                 │    │
│  │   1. chatClient.prompt().system().user().call()        │    │
│  │   2. outputConverter.entity() → 自动 JSON→Bean          │    │
│  │   3. 失败 → 重试 + 错误注入 Prompt                       │    │
│  │   4. 埋点指标                                           │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────┘
                                │ 注入
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  业务 Service (调用层)                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ResumeGradingService                                    │    │
│  │ InterviewQuestionService                                │    │
│  │ AnswerEvaluationService                                 │    │
│  │ KnowledgeBaseQueryService                               │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 总结

| 层级 | 组件 | 职责 |
|------|------|------|
| **配置绑定** | `LlmProviderProperties` | 绑定 `app.ai.*` 配置 |
| **实例化** | `LlmProviderRegistry` | 工厂模式创建/缓存 ChatClient |
| **封装** | `StructuredOutputInvoker` | 结构化输出 + 重试 + 监控 |
| **调用** | `*GradingService`、`*QuestionService` | 业务逻辑使用 |

**核心设计模式**：工厂模式 + 策略模式 + 模板方法模式

---

## 相关组件

| 组件 | 路径 | 说明 |
|------|------|------|
| `LlmProviderProperties` | `common/config/` | 配置绑定类 |
| `LlmProviderRegistry` | `common/ai/` | ChatClient 工厂 |
| `StructuredOutputInvoker` | `common/ai/` | 结构化输出封装 |
| `ResumeGradingService` | `modules/resume/service/` | 简历评分调用示例 |
| `InterviewQuestionService` | `modules/interview/service/` | 面试出题调用示例 |