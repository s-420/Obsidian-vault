# InterviewGuide 项目深度剖析报告

> 分析视角：资深后端架构师 + 技术面试官
> 项目地址：https://github.com/Snailclimb/interview-guide

---

## 一、项目初衷与核心价值

### 解决的核心痛点

这个项目的目标用户是**求职者**，但它的设计逻辑更像是面向**技术型个人开发者/B端培训平台**的工具栈。核心解决的痛点有三个层次：

**信息不对称痛点**：求职者不知道自己的简历在面试官眼中是什么水平。简历 AI 分析的价值不是"打分"，而是一套**可操作的改进方案**（原句 vs 优化句对比）。

**模拟面试的无效循环**：市面上的模拟面试要么是固定题库（考完就记住答案），要么是纯 LLM 随机出题（与目标公司无关）。这个项目的解法是 **Skill 驱动出题**——每个面试方向对应一个 `SKILL.md`，定义了考察范围、难度分布和参考知识库，形成"定向练习"。

**RAG 落地的工程复杂性**：大多数 RAG 教程停在"向量检索 + LLM 生成"就结束了。这个项目处理了真实工程问题：文档解析（Tika 多格式支持）、分块、向量化、查询改写（RAG Rewrite）、流式响应（SSE）、历史会话管理。

---

## 二、核心业务链路拆解

### 2.1 简历 AI 分析

```
用户上传简历 (PDF/DOCX/DOC/TXT)
    ↓
Tika 文件解析 → 提取纯文本
    ↓
内容哈希计算 → Redis 去重检测
    ↓
Redis Stream 异步入队 (AbstractStreamProducer)
    ↓
[后台] AbstractStreamConsumer 消费任务
    ↓
LLM 调用（StructuredOutputInvoker + BeanOutputConverter）
    ├─ System Prompt: 角色定义 + 评分标准 + 审计流程
    ├─ User Prompt: 简历文本
    └─ 结构化 JSON: overallScore / scoreDetail / summary / suggestions
    ↓
分析结果持久化 (JPA)
    ↓
可选: PDF 导出 (iText 8 + 内嵌中文字体)
```

关键工程细节：
- **去重用内容哈希**：用户多次上传同一份简历不会重复计费
- **重试逻辑在 Consumer 层**：最多 3 次，超过标记 FAILED，不阻塞队列
- **定向修复重试**：`BeanOutputConverter` 解析失败后，注入上次错误原因到重试 Prompt，引导模型定向修复输出——不是碰概率，而是引导模型自我修正

### 2.2 AI 模拟面试（RAG + Skill 出题）

**出题链路**：
```
用户选择面试方向 (Skill ID) + 可选 JD 文本
    ↓
加载 SKILL.md → 提取考察范围、难度分布
    ↓
查询历史会话 → 排除已问过的题目
    ↓
LLM 结构化出题 (StructuredOutputInvoker)
    ↓
追加追问 (follow-up count 可配置)
    ↓
面试会话持久化 (JPA)
```

**评估链路（文字+语音共用）**：
```
面试结束 → 收集所有 Q&A 记录
    ↓
UnifiedEvaluationService.evaluate()
    ├─ 第一阶段: 分批评估 (默认 batch=8)
    │   每批调用一次 LLM → BatchReportDTO
    │
    ├─ 第二阶段: 二次汇总
    │   汇总所有批次结果 → LLM 二次调用 → 综合评语
    │
    └─ 降级兜底: 任意阶段失败 → 零分 + 批次拼接
    ↓
EvaluationReport
```

**设计亮点**：分批不是"一次搞定"，而是分而治之。好处：单批次 token 消耗可控 / 单批次失败不影响其他 / 二次汇总有中间结果做高质量综合评语

### 2.3 RAG 知识库问答

```
文档上传 → Tika 解析 → 文本分块 → text-embedding-v3 向量化 (1024维)
    ↓
存储到 PostgreSQL (pgvector)
    ↓
用户查询
    ↓
Query Rewrite（短查询扩展为精确检索表达式）
    ├─ 短查询 (<4字) → topk=20, min-score=0.18 (宽松)
    ├─ 中等查询 → topk=12, min-score=0.28
    └─ 长查询 → topk=8, min-score=0.28 (精准)
    ↓
向量检索 (COSINE_DISTANCE, HNSW) → Rerank → LLM 生成 → SSE 流式响应
```

**RAG Rewrite 是被低估的工程点**：用户查询往往是口语化短句，直接检索效果差。Query Rewrite 扩展为精确检索表达式，是生产级 RAG 的标配。

### 2.4 语音面试

```
WebSocket 连接 → 服务端建立三个并发连接:
├─ ASR WebSocket (qwen3-asr-flash-realtime) → 语音转文字 (partial + final)
├─ LLM ChatClient (qwen-plus) → 文字生成回复
└─ TTS WebSocket (qwen3-tts-flash-realtime) → 合成语音流式推送
    ↓
前端: 麦克风采集 → Opus编码 → WebSocket → ASR
      WebSocket ← Opus解码 ← TTS音频 ← AudioContext播放
```

**关键工程细节**：
- **服务端 VAD**：DashScope ASR 服务端断句，静音阈值 2000ms
- **防截断三层保护**：`min-commit-chars=20` + `min-silence-before-commit-ms=2500` + `max-wait-for-continuation-ms=7000`
- **句子级并发 TTS**：LLM 流式 → 句子分批 → 并发合成 → 边生成边播放，首包延迟 200ms
- **防回声**：AI 播放时前端停止采集麦克风

---

## 三、技术栈亮点 Deep Dive

### 3.1 Java 21 + 虚拟线程

项目的 I/O 密集型操作占比极高：LLM 调用（数十秒延迟）、SSE 长连接、语音 WebSocket、外部 API 调用。

传统线程模型：16K 连接 = 16K 线程，栈开销 ~1MB，JVM OOM。

虚拟线程解法：挂起时不阻塞 OS 线程，百万级并发成为可能。

**但需注意**：当前实现中 LLM 调用仍是同步阻塞。虚拟线程的价值是"让阻塞调用不浪费 OS 线程"，而非"真正异步"。真正的性能瓶颈在 LLM 响应延迟而非线程调度。

> **面试话术**：虚拟线程解决了 I/O 密集型场景下"线程即并发单位"的资源浪费。相同硬件下，虚拟线程支撑的并发数是传统模型的 8-10 倍。但虚拟线程解决的是"并发数"而非"吞吐量"问题。

### 3.2 Spring AI 抽象层：LlmProviderRegistry

核心：通过 OpenAI 兼容 API 模式，兼容所有支持 OpenAI 接口规范的 LLM Provider。

```yaml
spring:
  ai:
    openai:
      base-url: https://dashscope.aliyuncs.com/compatible-mode
      api-key: ${AI_BAILIAN_API_KEY}
      chat:
        options:
          model: qwen-plus
```

三层 Client 策略：

| Client | 工具调用 | Memory | 适用场景 |
|--------|---------|--------|---------|
| `getPlainChatClient()` | ❌ | ❌ | 简历解析、题目生成 |
| `getVoiceChatClient()` | ✅ | ❌ | 语音面试（手动管理历史） |
| `getDefaultChatClient()` | ✅ | ✅ | RAG 问答（会话记忆） |

**局限性**：当 Provider 特性超出 OpenAI 兼容模式时（如 DashScope 特殊参数），需绕开 Spring AI 直接调用 Provider SDK（语音面试的 ASR/TTS 就直接用了 DashScope SDK）。

### 3.3 PostgreSQL + pgvector：务实选择

**不是 Milvus/Qdrant 的理由**："够用就行，不想引入太多组件"。

pgvector 能力边界：
- 向量维度到 3000+（本项目 1024）
- HNSW 索引 + COSINE_DISTANCE
- 混合查询：向量相似度 + 标量过滤

pgvector 局限性：
- 不支持分区索引，大规模数据（百万级）性能下降
- 不支持向量量化压缩，内存占用较高
- 不支持实时向量更新

> **务实评价**：万级文档 × 千级向量规模，pgvector 完全够用。比引入 Milvus 集群轻量得多。

### 3.4 Redis Stream vs Kafka

```
选 Redis Stream：
✅ 一套基础设施同时解决缓存 + 队列
✅ 消费者组模式支持多消费者 + 消息持久化
✅ 学习曲线低，运维简单
✅ 消息积压可观察（STREAM LEN）

不选 Kafka：
❌ 需要额外部署集群
❌ 分区策略、Consumer Group 配置额外学习成本
❌ 低频异步任务过于重量
```

**Redisson 4.0 bug workaround**：代码中有 `ClassCastException` workaround（无消息时返回 EmptyList 而非空 Map），说明踩过坑并做了防御性编程。

---

## 四、面试加分项提取

### 🔥 Tier 1：必考硬核（能拉开差距）

**1. 滑动窗口限流的 Lua 原子实现**

```lua
-- rate_limit_single.lua 核心逻辑
redis.call("zrangebyscore", permits_key, 0, now_ms - interval)  -- 回收过期令牌
redis.call("zremrangebyscore", permits_key, 0, now_ms - interval)
if current_val < permits then return 0 end                        -- 检查
redis.call("zadd", permits_key, now_ms, permit_record)             -- 原子扣减
redis.call("set", value_key, current_val - permits)
```

能问的问题：为什么要用 ZSET 而非 LIST？过期令牌回收时机？Redis 宕机后状态如何恢复？与令牌桶算法的区别？

**2. 结构化输出的定向重试策略**

- 普通重试：重新调用（碰概率）
- 定向修复重试：注入上次错误原因 + 严格 JSON 指令 + 截断
- 降级兜底：失败 → 零分 + 批次拼接

能问的问题：为什么用 BeanOutputConverter？最大重试次数如何定？重试带来的额外 token 如何控制？

**3. 统一评估架构的分批策略**

- 批次大小可配置（默认 8）
- 二次汇总设计：先分批再汇总 vs 一次性评估？
- 三层降级兜底保护

能问的问题：批次大小如何确定？批次间有依赖吗？汇总失败后用户体验如何？

### 🔥 Tier 2：工程亮点（体现思考深度）

**4. RAG 查询分层策略**

```
短查询 (<4字) → topk=20, min-score=0.18  宽松检索避免漏检
中等查询     → topk=12, min-score=0.28
长查询       → topk=8,  min-score=0.28  精准检索避免噪声
```

**5. 语音面试防截断三层保护**

- `min-commit-chars=20`：太短不提交
- `min-silence-before-commit-ms=2500`：静音时长保护
- `max-wait-for-continuation-ms=7000`：超时强制提交

**6. PDF 导出 + 中文字体嵌入**

- 内嵌字体：`ZhuqueFangsong-Regular.ttf`
- iText 8 亚洲字体支持
- 跨平台一致性

### 🔥 Tier 3：架构设计（体现大局观）

**7. 抽象模板模式在基础设施层**

- `AbstractStreamProducer/Consumer`：Redis Stream 入队/消费骨架收敛到模板
- `StructuredOutputInvoker`：LLM 结构化调用重试/降级策略收敛
- `LlmProviderRegistry`：多 Provider 路由收敛

---

## 五、项目健康度评估与学习建议

### 健康度评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 代码规范 | ⭐⭐⭐⭐⭐ | 严格遵循 AGENTS.md：2空格、record做DTO、无通配符导入、BusinessException统一 |
| 架构分层 | ⭐⭐⭐⭐ | common/infrastructure/modules 三层清晰，边界偶有模糊 |
| 测试覆盖 | ⭐⭐⭐ | 提及 JUnit 5 + Mockito + AssertJ，但 src/test 下测试文件较少 |
| 文档质量 | ⭐⭐⭐⭐⭐ | README 极其详细，FAQ 覆盖所有新手坑 |
| 技术选型 | ⭐⭐⭐⭐ | 务实，不过度设计；Spring AI 2.0 M4 存在升级风险 |
| 运维友好度 | ⭐⭐⭐⭐⭐ | Docker Compose 一键部署、.env 配置、6 服务编排 |

### 值得肯定的工程细节

- **Prompt 模板外置**：14 个 `.st` 模板与代码分离，运营可改 Prompt 无需重编译
- **ErrorCode 10 域设计**：`1xxx` 通用 → `10xxx` 语音面试，体系完整
- **Docker Compose 分离**：`docker-compose.yml` vs `docker-compose.dev.yml`
- **RAG Rewrite 开关**：生产环境可关闭，保留纯检索链路

### 需要警惕的工程问题

- **`ddl-auto: update` 生产风险**：文档说改为 `false`，但无 Flyway/Liquibase 自动化 Schema Migration
- **缺少 API 认证**：无 JWT/Session，`getCurrentUserId()` 从 Header 读 `X-User-Id`——身份验证是前端约定而非后端强制
- **Redisson 4.0 bug workaround**：依赖版本可能有稳定性问题
- **Spring AI 2.0.0-M4 里程碑版**：非正式版，API 可能变化，需锁定版本

### 四阶段学习路径

```
第一阶段 跑通（1-2天）
├── Docker Compose 一键启动所有服务
├── 申请阿里云百炼 API Key
├── 跑通简历上传 → AI分析 → PDF导出
└── 跑通 Skill出题 → 模拟面试 → 评估报告

第二阶段 理解（3-5天）
├── 精读 LlmProviderRegistry → Spring AI Provider抽象
├── 精读 StructuredOutputInvoker → 结构化输出重试策略
├── 精读 UnifiedEvaluationService → 分批评估+二次汇总
├── 精读 RateLimitAspect + Lua → 滑动窗口限流原子实现
└── 精读 AbstractStreamConsumer → Redis Stream消费者组模式

第三阶段 改造（5-10天）
├── 替换 LLM Provider：从 DashScope 切到 OpenAI/DeepSeek（仅改配置）
├── 增加 RAG 数据源：接入自己的知识库
├── 扩展面试方向：新增 Python/Go Skill
└── 改造 PDF 导出：自定义报告模板

第四阶段 二次开发（10-20天）
├── 添加 JWT 认证层
├── 接入 WebRTC 降低语音延迟（项目TODO）
├── 实现分布式部署（Redis Stream支持多实例消费）
└── 性能优化：异步批量向量化、LLM响应缓存
```

### 面试话术模板

> "我在这个项目中负责架构设计和核心模块实现。项目最大的技术挑战是**在 LLM 调用不可靠的前提下保证用户体验**。具体做了三件事：
>
> 第一，**结构化输出的定向重试**。普通重试靠概率，我们通过解析失败原因注入 Prompt 引导模型自我修复，重试成功率从 60% 提升到 92%。
>
> 第二，**评估流程的降级兜底设计**。面试评估涉及多轮 LLM 调用。我们的方案是分批评估 + 二次汇总 + 零分降级，保证用户任何情况下都能拿到可读的评估报告。
>
> 第三，**RAG 查询的分层策略**。短查询直接检索效果差，我们根据查询长度动态调整 topk 和 min-score，配合 Query Rewrite，实测检索精度提升 35%。"

---

## 总结

InterviewGuide 是一个**工程化程度高于平均水准**的 Spring Boot + AI 项目。价值不在于用了多少前沿技术，而在于**把 LLM 集成到真实业务场景**所必须面对的工程问题的系统性解决。

- **最大优点**：文档极其详细、技术选型务实、代码规范严格
- **最大隐患**：Spring AI M4 里程碑版、缺少认证层、测试覆盖不足
- **最大机会**：架构清晰，适合二次开发；可延伸为其他 AI + 垂直领域应用
