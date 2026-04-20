# LLM 模型更换测试方案

## 测试目标

验证更换 LLM 模型后，项目核心功能能够正常运行。

---

## 一、测试范围

### 核心功能模块

| 模块 | 优先级 | 测试内容 |
|------|--------|----------|
| **LLM 配置与注册** | P0 | Provider 切换、模型配置 |
| **简历分析** | P0 | 简历上传 → AI 评分 → 结果返回 |
| **面试出题** | P0 | 题目生成（Skill 驱动） |
| **回答评估** | P0 | 答案评分 + 反馈生成 |
| **知识库 RAG** | P1 | 文档向量化 + 问答检索 |
| **PDF 导出** | P1 | 分析报告生成 |
| **语音面试** | P2 | 实时对话（可选） |

---

## 二、测试前准备

### 2.1 环境要求

```bash
# 1. 启动依赖服务
docker compose -f docker-compose.dev.yml up -d

# 2. 确保 Redis 和 PostgreSQL 运行中
docker compose ps

# 3. 配置有效的 API Key（修改 .env）
AI_BAILIAN_API_KEY=your_valid_api_key
```

### 2.2 模型配置

在 `application.yml` 中配置目标模型：

```yaml
app:
  ai:
    default-provider: dashscope
    providers:
      dashscope:
        base-url: https://dashscope.aliyuncs.com/compatible-mode
        api-key: ${AI_BAILIAN_API_KEY}
        model: qwen-plus      # 目标测试模型
```

---

## 三、测试用例

### 3.1 LLM 配置层测试 (P0)

#### TC-001: Provider 切换测试

```bash
# 验证不同 Provider 可以正常切换
./gradlew test --tests "*LlmProviderRegistryTest*"
```

**验证点**：
- [ ] `getChatClient("dashscope")` 返回非空 Client
- [ ] `getDefaultChatClient()` 返回默认 Provider 的 Client
- [ ] `getChatClientOrDefault(null)` 回退到默认 Provider
- [ ] 未知 Provider 抛出 `IllegalArgumentException`
- [ ] Client 缓存机制正常（多次调用返回同一实例）

#### TC-002: 配置绑定测试

```bash
./gradlew test --tests "*LlmProviderPropertiesTest*"
```

**验证点**：
- [ ] `app.ai.providers.dashscope.model` 正确绑定
- [ ] `app.ai.advisors.tool-call-enabled` 正确绑定
- [ ] 缺少配置时有默认值

---

### 3.2 简历分析测试 (P0)

#### TC-101: 简历上传与 AI 分析

```bash
# 启动应用后执行
curl -X POST http://localhost:8080/api/resumes/upload \
  -F "file=@/path/to/resume.pdf"
```

**验证点**：
| 检查项 | 预期结果 |
|--------|----------|
| 响应状态 | 200 OK |
| 返回结构 | `{resume: {id, analyzeStatus}, duplicate: false}` |
| `analyzeStatus` | 1-2 秒内变为 `COMPLETED` |
| `overallScore` | 0-100 的整数 |
| `strengths` | 非空列表 |
| `suggestions` | 非空列表 |

**示例响应**：
```json
{
  "code": 200,
  "data": {
    "resume": {
      "id": 1,
      "filename": "resume.pdf",
      "analyzeStatus": "COMPLETED"
    },
    "analysis": {
      "overallScore": 75,
      "scoreDetail": {
        "contentScore": 80,
        "structureScore": 70,
        "skillMatchScore": 75,
        "expressionScore": 75,
        "projectScore": 75
      },
      "summary": "简历整体不错...",
      "strengths": ["技术栈全面", "项目经验丰富"],
      "suggestions": [{"category": "改进", "priority": "中", "issue": "...", "recommendation": "..."}]
    },
    "duplicate": false
  }
}
```

#### TC-102: 重复简历检测

```bash
# 上传相同文件两次
curl -X POST http://localhost:8080/api/resumes/upload -F "file=@resume.pdf"
curl -X POST http://localhost:8080/api/resumes/upload -F "file=@resume.pdf"
```

**验证点**：
- [ ] 第二次返回 `duplicate: true`
- [ ] 返回历史分析结果（非重新分析）

#### TC-103: 简历分析失败处理

```bash
# 上传空文件或损坏的 PDF
curl -X POST http://localhost:8080/api/resumes/upload -F "file=@empty.pdf"
```

**验证点**：
- [ ] 返回合理的错误信息
- [ ] `analyzeStatus` 变为 `FAILED`
- [ ] `analyzeError` 记录错误原因

---

### 3.3 面试出题测试 (P0)

#### TC-201: 无简历通用面试出题

```bash
curl -X POST http://localhost:8080/api/interviews/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "skillId": "java-backend",
    "difficulty": "mid"
  }'
```

**验证点**：
| 检查项 | 预期结果 |
|--------|----------|
| 响应状态 | 200 OK |
| 返回结构 | `{sessionId, questions: [...]}` |
| `questions` 数量 | 3-5 道题 |
| 每题包含 | `question`, `type`, `category`, `followUps` |
| `followUps` | 每题 1-2 道追问 |

**示例响应**：
```json
{
  "code": 200,
  "data": {
    "sessionId": "uuid-xxx",
    "skillId": "java-backend",
    "questions": [
      {
        "question": "请描述 HashMap 的扩容机制",
        "type": "TECH",
        "category": "Java 集合",
        "topicSummary": "HashMap 底层实现",
        "followUps": ["扩容因子为什么是 0.75？"]
      }
    ]
  }
}
```

#### TC-202: 有简历面试出题

```bash
# 先上传简历获取 resumeId
# 再创建面试会话
curl -X POST http://localhost:8080/api/interviews/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "resumeId": 1,
    "skillId": "java-backend",
    "difficulty": "mid"
  }'
```

**验证点**：
- [ ] 返回题目中包含简历相关的问题
- [ ] `questions` 包含 `RESUME` 类型题目

#### TC-203: 多 Skill 出题测试

```bash
# 测试不同 Skill
for skill in "java-backend" "python" "frontend" "algorithm"; do
  curl -X POST http://localhost:8080/api/interviews/sessions \
    -H "Content-Type: application/json" \
    -d "{\"skillId\": \"$skill\", \"difficulty\": \"mid\"}"
done
```

**验证点**：
- [ ] 各 Skill 均能正常出题
- [ ] 题目内容符合 Skill 方向

---

### 3.4 回答评估测试 (P0)

#### TC-301: 提交回答并获取评估

```bash
# 先创建会话
SESSION_ID=$(curl -s http://localhost:8080/api/interviews/sessions \
  -H "Content-Type: application/json" \
  -d '{"skillId": "java-backend", "difficulty": "mid"}' | jq -r '.data.sessionId')

# 获取第一个问题
QUESTION=$(curl -s "http://localhost:8080/api/interviews/sessions/$SESSION_ID/next-question")

# 提交回答
curl -X POST "http://localhost:8080/api/interviews/sessions/$SESSION_ID/answers" \
  -H "Content-Type: application/json" \
  -d '{"questionIndex": 0, "answer": "HashMap底层是数组+链表..."}'
```

**验证点**：
| 检查项 | 预期结果 |
|--------|----------|
| 响应状态 | 200 OK |
| 返回结构 | `{score, feedback, strengths, improvements}` |
| `score` | 0-100 的整数 |
| `feedback` | 非空字符串（评估意见） |

**示例响应**：
```json
{
  "code": 200,
  "data": {
    "score": 75,
    "feedback": "回答较为完整...",
    "strengths": ["提到了数组和链表", "提到了扰动函数"],
    "improvements": ["未说明扩容触发条件"]
  }
}
```

#### TC-302: 批量评估测试

```bash
# 提交多个回答
for i in {0..4}; do
  curl -X POST "http://localhost:8080/api/interviews/sessions/$SESSION_ID/answers" \
    -H "Content-Type: application/json" \
    -d "{\"questionIndex\": $i, \"answer\": \"测试回答内容...\"}"
done
```

**验证点**：
- [ ] 所有回答均被正确记录
- [ ] 可以正常获取面试报告

#### TC-303: 面试报告生成

```bash
# 完成面试后获取报告
curl -X POST "http://localhost:8080/api/interviews/sessions/$SESSION_ID/complete"
curl -X GET "http://localhost:8080/api/interviews/sessions/$SESSION_ID/report"
```

**验证点**：
- [ ] `overallScore` 非空
- [ ] `overallFeedback` 非空
- [ ] `strengths` 和 `improvements` 非空

---

### 3.5 知识库 RAG 测试 (P1)

#### TC-401: 文档上传与向量化

```bash
curl -X POST http://localhost:8080/api/knowledge-bases/upload \
  -F "file=@/path/to/document.pdf" \
  -F "name=Java面试题库" \
  -F "category=面试资料"
```

**验证点**：
| 检查项 | 预期结果 |
|--------|----------|
| 响应状态 | 200 OK |
| `vectorStatus` | 最终变为 `COMPLETED` |
| `chunkCount` | > 0 |

#### TC-402: RAG 问答检索

```bash
curl -X POST http://localhost:8080/api/rag/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "HashMap 面试题", "knowledgeBaseId": 1}'
```

**验证点**：
| 检查项 | 预期结果 |
|--------|----------|
| 响应状态 | 200 OK |
| `answer` | 非空字符串 |
| `chunks` | 包含相关文档片段 |
| 回答与文档相关 | 是 |

**示例响应**：
```json
{
  "code": 200,
  "data": {
    "answer": "关于 HashMap 的面试题...",
    "chunks": [
      {"content": "HashMap 底层实现...", "score": 0.85},
      {"content": "ConcurrentHashMap...", "score": 0.72}
    ]
  }
}
```

---

### 3.6 PDF 导出测试 (P1)

#### TC-501: 简历分析报告导出

```bash
curl -X GET http://localhost:8080/api/resumes/1/export \
  -o resume_report.pdf

# 验证文件
file resume_report.pdf
head -c 100 resume_report.pdf | xxd | head -1
```

**验证点**：
- [ ] Content-Type: application/pdf
- [ ] 文件大小 > 1KB
- [ ] 文件头为 `%PDF`（PDF 格式正确）
- [ ] 中文显示正常

#### TC-502: 面试报告导出

```bash
curl -X GET http://localhost:8080/api/interviews/sessions/$SESSION_ID/export \
  -o interview_report.pdf
```

**验证点**：
- [ ] PDF 格式正确
- [ ] 包含评估分数和建议

---

### 3.7 语音面试测试 (P2 - 可选)

#### TC-601: WebSocket 连接测试

```bash
# 需要真实的麦克风输入
# 使用测试脚本或 Postman WebSocket 客户端
```

**验证点**：
- [ ] WebSocket 连接建立成功
- [ ] 音频流正常传输
- [ ] TTS 语音正常播放
- [ ] ASR 识别正常

---

## 四、测试执行清单

### 阶段一：配置验证 (5 分钟)

```bash
# 1. 验证配置文件语法
./gradlew bootRun --dry-run

# 2. 运行配置绑定测试
./gradlew test --tests "*LlmProviderRegistryTest*"
```

### 阶段二：核心功能验证 (30 分钟)

```bash
# 3. 简历分析测试
curl -s -X POST http://localhost:8080/api/resumes/upload \
  -F "file=@test/resume.pdf" | jq .

# 4. 面试出题测试
curl -s -X POST http://localhost:8080/api/interviews/sessions \
  -H "Content-Type: application/json" \
  -d '{"skillId": "java-backend", "difficulty": "mid"}' | jq .

# 5. 回答评估测试
# (执行 TC-301)

# 6. RAG 问答测试
# (执行 TC-402)
```

### 阶段三：集成验证 (20 分钟)

```bash
# 7. 完整面试流程
./scripts/test_interview_flow.sh

# 8. PDF 导出验证
./scripts/test_pdf_export.sh

# 9. 错误场景测试
./scripts/test_error_handling.sh
```

---

## 五、测试脚本模板

### test_llm_config.sh

```bash
#!/bin/bash
# LLM 配置测试脚本

API_KEY=${AI_BAILIAN_API_KEY}
BASE_URL=${BASE_URL:-http://localhost:8080}

echo "=== LLM 模型测试 ==="
echo "API Key: ${API_KEY:0:10}..."
echo "Base URL: $BASE_URL"
echo ""

# 测试 1: 健康检查
echo "1. 健康检查..."
curl -s "$BASE_URL/api/resumes/health" | jq .

# 测试 2: 简历分析
echo ""
echo "2. 简历分析..."
curl -s -X POST "$BASE_URL/api/resumes/upload" \
  -F "file=@test_resume.pdf" | jq .

# 测试 3: 面试出题
echo ""
echo "3. 面试出题..."
curl -s -X POST "$BASE_URL/api/interviews/sessions" \
  -H "Content-Type: application/json" \
  -d '{"skillId": "java-backend", "difficulty": "mid"}' | jq .

echo ""
echo "=== 测试完成 ==="
```

---

## 六、预期结果

### 通过标准

| 模块 | 通过条件 |
|------|----------|
| LLM 配置 | 所有 Provider 配置正确加载 |
| 简历分析 | 分析成功，分数合理 (10-95) |
| 面试出题 | 题目生成成功，内容相关 |
| 回答评估 | 评估返回，分数波动正常 |
| RAG 问答 | 检索相关回答，无幻觉 |
| PDF 导出 | 格式正确，中文正常 |

### 常见失败处理

| 错误 | 可能原因 | 解决方案 |
|------|----------|----------|
| `401 Unauthorized` | API Key 无效 | 检查 `AI_BAILIAN_API_KEY` |
| `429 Rate Limit` | 请求超限 | 降低测试频率 |
| `connection timeout` | 网络问题 | 检查 base-url 配置 |
| `模型不支持` | 模型名称错误 | 确认模型名称正确 |
| `JSON 解析失败` | 模型输出格式问题 | 检查 `StructuredOutputInvoker` 重试 |

---

## 七、回归测试

更换模型后，建议运行以下回归测试：

```bash
# 1. 运行所有单元测试
./gradlew test

# 2. 运行集成测试
./gradlew test --tests "*IntegrationTest"

# 3. 运行 API 测试
./gradlew test --tests "*ControllerTest"
```

**回归测试通过标准**：所有测试用例通过率 100%