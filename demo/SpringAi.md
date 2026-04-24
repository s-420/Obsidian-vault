## 项目配置依赖
采用SpringBoot 4.0 +Java 21+Spring AI 2.0 技术栈，使用阿里云dashscope作为大模型服务提供商
### 添加依赖
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
### 配置属性
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
	# PostgreSQL Vector Store配置  
	vectorstore:  
	  pgvector:  
	    index-type: HNSW  
	    distance-type: COSINE_DISTANCE  
	    dimensions: 1024  # text-embedding-v3实际生成的向量维度  
	    initialize-schema: true # 开发环境设置为 true，方便快速启动。生产环境设置为 false，手动管理数据库 schema，避免意外变更。  
	    remove-existing-vector-store-table: false  # 保留现有表和数据
	    
	    
# Application custom configuration  
app:  
  ai:   
    advisors：
	    # 结构化输出重试次数（用于 BeanOutputConverter 解析失败时的业务层重试）  
		structured-max-attempts: ${APP_AI_STRUCTURED_MAX_ATTEMPTS:2}  
		# 重试时是否将上次错误原因注入提示词，帮助模型定向修复输出  
		structured-include-last-error: ${APP_AI_STRUCTURED_INCLUDE_LAST_ERROR:true}
~~~
### 关键配置说明：

| **配置项**                                | **说明**                                  |
| -------------------------------------- | --------------------------------------- |
| `base-url`                             | 阿里云 DashScope的OpenAI兼容端点                |
| `api-key`                              | 通过环境变量注入（.env），生产环境 **严禁硬编码**           |
| `temperature`                          | 控制输出随机（0-1），本项目使用 0.2 （更利于结构化输出 **稳定**） |
| `dimensions`                           | text-embedding-v3 的向量维度为1024            |
| `initialize-schema`                    | 开发环境设为 ture 自动创建表，生产环境设为false           |
| `app.ai.structured-max-attempts`       | 业务层结构话输出重试次数（默认2）                       |
| `app.ai.structured-include-last-error` | 重试时是否注入上次失败的原因（默认ture）                  |
