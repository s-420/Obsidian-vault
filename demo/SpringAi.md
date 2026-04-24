## 项目配置依赖
采用SpringBoot 4.0 +Java 21+Spring AI 2.0 技术栈，使用阿里云dashscope作为大模型服务提供商
## 添加依赖
---
~~~ java
// build.gradle
dependencies{
	// Spring AI 2.0 - OpenAI兼容模式 (阿里云DashScope)  
	implementation "org.springframework.ai:spring-ai-starter-model-openai:${libs.versions.springAi.get()}"  
	// Spring AI 2.0 - PostgreSQL Vector Store (pgvector)  
	implementation "org.springframework.ai:spring-ai-starter-vector-store-pgvector:${libs.versions.springAi.get()}"
}
~~~
**版本说明**：
- spring-ai-starter-model-openai：提供 ChatClient 和 EmbeddingModel
- spring-ai-starter-vector-store-pgvector：提供 VectorStore 对接PostgreSQL+pgvector
## 配置属性
---
~~~ xml
spring：
	# Spring AI - 阿里云DashScope (OpenAI兼容模式)  
	ai:  
	  openai:  
	    base-url: https://dashscope.aliyuncs.com/compatible-mode  
	    api-key: ${AI_BAILIAN_API_KEY}  
	    chat:  
	      options:  
	        model: ${AI_MODEL:qwen-plus}  
	        temperature: 0.2  
	    # Embedding模型配置 - 使用text-embedding-v3  
	    embedding:  
	      options:  
	        model: text-embedding-v3  
	  # 禁用自动重试机制，让异常立即返回  
	  retry:  
	    max-attempts: 1  # 不重试，失败立即返回  
	    on-client-errors: false
	    
	    
# Application custom configuration  
app:  
  ai:  
    default-provider: dashscope  
    agent-utils:  
      skills-root: ${APP_AI_AGENT_UTILS_SKILLS_ROOT:classpath:skills}  
    providers:  
      dashscope:  
        base-url: https://dashscope.aliyuncs.com/compatible-mode  
        api-key: ${AI_BAILIAN_API_KEY}  
        model: qwen-plus  
      lmstudio:  
        base-url: http://localhost:1234  
        api-key: lm-studio  
        model: qwen2.5-7b-instruct
~~~