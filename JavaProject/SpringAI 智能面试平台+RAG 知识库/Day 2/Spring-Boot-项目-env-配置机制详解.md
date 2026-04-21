# Spring Boot 项目 .env 配置机制详解

## 概述

Spring Boot 项目中，敏感信息（如 API Key、数据库密码等）通常存储在 `.env` 文件中，通过环境变量注入的方式供应用读取。

## 项目结构

```
interview-guide/
├── .env                    # 敏感信息配置（不提交 Git）
├── docker-compose.yml       # Docker 编排配置
├── app/
│   ├── build.gradle         # Gradle 构建配置（含 .env 加载逻辑）
│   └── src/main/resources/
│       └── application.yml  # Spring Boot 主配置
└── ...
```

## 一、.env 文件

### 作用

存储敏感信息，**不提交到 Git 版本控制**。

### 示例内容

```bash
# 阿里云百炼 AI API Key
AI_BAILIAN_API_KEY=sk-65ec3847e9c84739b38d6ee7ba48d6c8

# 数据库配置
POSTGRES_PASSWORD=password

# MiniMax（可选）
MINIMAX_API_KEY=your_minimax_key
```

### 安全策略

`.gitignore` 通常会排除 `.env`：
```gitignore
.env
```

## 二、读取方式

### 方式 1：本地开发 - Gradle bootRun

**文件**：`app/build.gradle`

**核心逻辑**（第 115-133 行）：

```groovy
tasks.named('bootRun') {
    jvmArgs = [
        '-Dfile.encoding=UTF-8',
        '-Dconsole.encoding=UTF-8',
        '-Dstdout.encoding=UTF-8',
        '-Dstderr.encoding=UTF-8'
    ]

    // 加载 .env 文件
    def envFile = rootProject.file('.env')
    if (envFile.exists()) {
        envFile.eachLine { line ->
            def trimmed = line.trim()
            // 跳过空行和注释
            if (trimmed.isEmpty() || trimmed.startsWith('#')) {
                return
            }
            // 解析 KEY=value
            def eq = trimmed.indexOf('=')
            if (eq <= 0) {
                return
            }
            def key = trimmed.substring(0, eq).trim()
            def val = trimmed.substring(eq + 1).trim()
            // 去除引号
            if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
                val = val.substring(1, val.length() - 1)
            }
            // 注入为环境变量
            environment key, val
        }
    }
}
```

**流程**：
1. Gradle 启动 `bootRun` 任务
2. 检测项目根目录是否存在 `.env` 文件
3. 逐行解析 `KEY=value` 格式
4. 过滤空行和 `#` 注释
5. 去除引号包裹的值
6. 通过 `environment` 方法注入为进程环境变量

---

### 方式 2：Docker 容器 - docker-compose.yml

**核心逻辑**：

```yaml
services:
  app:
    build:
      context: .
      dockerfile: app/Dockerfile
    environment:
      # 直接引用宿主机环境变量或 .env 中的值
      AI_BAILIAN_API_KEY: ${AI_BAILIAN_API_KEY}
      AI_MODEL: ${AI_MODEL:-qwen-plus}  # 支持默认值
      POSTGRES_HOST: ${POSTGRES_HOST:-localhost}
```

**Docker Compose 自动读取 .env**：

Docker Compose 会自动加载同目录下的 `.env` 文件作为默认环境变量，无需手动导出。

**docker-compose 查找顺序**：
1. `docker-compose.yml` 中 `environment` 的 `${VAR}` 格式
2. 宿主机同名环境变量
3. `.env` 文件中的值
4. `docker-compose.yml` 中的默认值（如 `${VAR:-default}`）

---

### 方式 3：应用读取 - application.yml

**Spring Boot 配置**：

```yaml
spring:
  datasource:
    url: jdbc:postgresql://${POSTGRES_HOST:localhost}:${POSTGRES_PORT:5432}/${POSTGRES_DB:interview_guide}
    username: ${POSTGRES_USER:postgres}
    password: ${POSTGRES_PASSWORD:password}

ai:
  openai:
    api-key: ${AI_BAILIAN_API_KEY}  # 必填，无默认值
    base-url: ${AI_BASE_URL:-https://dashscope.aliyuncs.com/compatible-mode}
```

**语法**：
| 语法 | 含义 |
|------|------|
| `${VAR}` | 读取环境变量，不存在则报错 |
| `${VAR:-default}` | 读取环境变量，不存在则使用默认值 |
| `${VAR:-}` | 读取环境变量，不存在则使用空字符串 |

---

## 三、完整流程图

```
┌─────────────────────────────────────────────────────────────┐
│                      .env 文件                               │
│  AI_BAILIAN_API_KEY=sk-xxx                                  │
│  POSTGRES_PASSWORD=password                                 │
│  MINIMAX_API_KEY=xxx                                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────────┐                   ┌───────────────────────────┐
│  本地开发场景      │                   │    Docker 容器场景        │
│  ./gradlew bootRun│                   │    docker-compose up      │
├───────────────────┤                   ├───────────────────────────┤
│ build.gradle      │                   │ docker-compose.yml        │
│ 解析 .env 文件    │                   │ environment:              │
│ 注入环境变量      │                   │   KEY: ${KEY}            │
│                  │                   │                           │
│ 结果：            │                   │ 结果：                     │
│ JAVA进程环境变量   │                   │ 容器内环境变量             │
└───────────────────┘                   └───────────────────────────┘
        │                                           │
        └─────────────────────┬─────────────────────┘
                              ▼
              ┌───────────────────────────────┐
              │   Spring Boot 应用           │
              │   application.yml            │
              │   ${AI_BAILIAN_API_KEY}      │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   @Value 或 @Configuration   │
              │   Properties 注入            │
              └───────────────────────────────┘
```

## 四、实战示例

### 场景：添加新的 API Key

**Step 1**：在 `.env` 中添加
```bash
MY_NEW_API_KEY=sk-abc123xyz
```

**Step 2**：在 `docker-compose.yml` 中引用
```yaml
environment:
  MY_NEW_API_KEY: ${MY_NEW_API_KEY}
```

**Step 3**：在 `application.yml` 中使用
```yaml
my-service:
  api-key: ${MY_NEW_API_KEY}
```

**Step 4**（可选）：在 `build.gradle` 中加载（本地开发）
```groovy
// build.gradle 已自动加载所有 .env 变量
// 无需额外配置
```

### 场景：不同环境不同配置

```bash
# .env.development
AI_BAILIAN_API_KEY=dev_key
DEBUG=true

# .env.production (不提交)
AI_BAILIAN_API_KEY=prod_key
DEBUG=false
```

```yaml
# docker-compose.yml
environment:
  AI_BAILIAN_API_KEY: ${AI_BAILIAN_API_KEY}  # 自动读取当前环境的 .env
```

## 五、注意事项

| 注意点 | 说明 |
|--------|------|
| 不提交 .env | 确保 `.gitignore` 包含 `.env` |
| 勿泄露生产密钥 | 生产环境的 .env 绝不提交 |
| 引用时加引号 | 包含特殊字符的值需要引号包裹 |
| 默认值 | 使用 `${VAR:-default}` 防止未设置报错 |

---

*文档创建: 2026-04-20*
