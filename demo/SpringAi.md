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
spring
~~~