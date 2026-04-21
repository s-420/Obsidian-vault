# AI Interview Platform DDD-Lite 架构分析

## 一、DDD-lite 核心概念映射

| DDD 概念 | 本项目实现 | 示例 |
|---------|-----------|------|
| **Bounded Context** (限界上下文) | `modules/` 包 | `resume`, `interview`, `knowledgebase` |
| **Aggregate** (聚合) | Entity + 关联 Entity | `InterviewSessionEntity` + `InterviewAnswerEntity` |
| **Entity** (实体) | `*Entity.java` | `ResumeEntity`, `InterviewSessionEntity` |
| **Value Object** (值对象) | `record` / `enum` | `AsyncTaskStatus`, `QueryRequest` |
| **Repository** (仓储) | `*Repository.java` | `ResumeRepository`, `InterviewSessionRepository` |
| **Domain Service** (领域服务) | `*Service.java` | `ResumeUploadService`, `InterviewGradingService` |
| **Application Service** (应用服务) | Controller | `ResumeController`, `InterviewController` |
| **Infrastructure** | `infrastructure/` 包 | `FileStorageService`, `RedisService` |

---

## 二、限界上下文划分

项目划分为 **5 个限界上下文**（Bounded Context）：

```
interview-guide/
└── modules/
    ├── resume/              # 简历管理上下文
    ├── interview/           # 模拟面试上下文
    ├── knowledgebase/       # 知识库上下文
    ├── interviewschedule/  # 面试日程上下文
    └── voiceinterview/      # 语音面试上下文
```

### 2.1 简历上下文 (Resume)

```
resume/
├── model/
│   ├── ResumeEntity           # 简历聚合根
│   ├── ResumeAnalysisEntity   # 分析结果（关联实体）
│   ├── ResumeListItemDTO      # 值对象
│   └── ResumeDetailDTO        # 值对象
├── repository/
│   ├── ResumeRepository        # 仓储
│   └── ResumeAnalysisRepository
├── service/
│   ├── ResumeUploadService     # 上传应用服务
│   ├── ResumeParseService      # 解析领域服务
│   ├── ResumeGradingService    # 评分领域服务
│   ├── ResumePersistenceService # 持久化服务
│   ├── ResumeHistoryService    # 历史查询服务
│   └── ResumeDeleteService     # 删除服务
└── listener/
    ├── AnalyzeStreamProducer   # 异步任务生产者
    └── AnalyzeStreamConsumer   # 异步任务消费者
```

### 2.2 面试上下文 (Interview)

```
interview/
├── model/
│   ├── InterviewSessionEntity  # 面试会话（聚合根）
│   ├── InterviewAnswerEntity   # 回答记录（关联实体）
│   ├── SessionStatus            # 值对象（枚举）
│   ├── CreateInterviewRequest   # 值对象（record）
│   └── InterviewDetailDTO      # 值对象
├── repository/
│   ├── InterviewSessionRepository
│   └── InterviewAnswerRepository
├── service/
│   ├── InterviewCreateService   # 创建会话
│   ├── InterviewChatService     # 问答处理
│   ├── InterviewEvaluateService # 评估服务
│   └── InterviewSessionService  # 会话管理
├── listener/
│   ├── EvaluateStreamProducer   # 评估任务生产者
│   └── EvaluateStreamConsumer   # 评估任务消费者
└── skill/
    └── *.md                     # Skill 驱动定义
```

### 2.3 知识库上下文 (KnowledgeBase)

```
knowledgebase/
├── model/
│   ├── KnowledgeBaseEntity      # 知识库聚合根
│   ├── RagChatSessionEntity     # RAG 聊天会话
│   ├── RagChatMessageEntity     # 聊天消息
│   ├── VectorStatus             # 值对象（枚举）
│   └── QueryRequest/Response    # 值对象
├── repository/
│   ├── KnowledgeBaseRepository
│   ├── VectorRepository         # pgvector 仓储
│   ├── RagChatSessionRepository
│   └── RagChatMessageRepository
├── service/
│   ├── KnowledgeBaseUploadService
│   ├── KnowledgeBaseParseService
│   ├── KnowledgeBaseListService
│   ├── KnowledgeBaseDeleteService
│   └── RagChatService           # RAG 问答
└── listener/
    ├── VectorizeStreamProducer
    └── VectorizeStreamConsumer
```

---

## 三、聚合根设计

### 3.1 聚合识别

| 聚合 | 聚合根 | 关联实体 | 聚合职责 |
|------|--------|---------|---------|
| 简历 | `ResumeEntity` | `ResumeAnalysisEntity` | 简历上传、解析、分析 |
| 面试会话 | `InterviewSessionEntity` | `InterviewAnswerEntity` | 面试流程、问答、评估 |
| 知识库 | `KnowledgeBaseEntity` | 无直接关联 | 文档上传、向量化、RAG |
| RAG 聊天 | `RagChatSessionEntity` | `RagChatMessageEntity` | 聊天会话管理 |
| 语音面试 | `VoiceInterviewSessionEntity` | `VoiceInterviewMessageEntity` | 实时语音面试 |
| 面试日程 | `InterviewScheduleEntity` | 无关联实体 | 日程管理 |

### 3.2 聚合示例：InterviewSessionEntity

```java
@Entity
@Table(name = "interview_sessions")
public class InterviewSessionEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    // 聚合根 ID
    @Column(nullable = false, unique = true, length = 36)
    private String sessionId;
    
    // 关联实体（答案列表）
    @OneToMany(mappedBy = "session", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<InterviewAnswerEntity> answers = new ArrayList<>();
    
    // 聚合根方法
    public void addAnswer(InterviewAnswerEntity answer) {
        answers.add(answer);
        answer.setSession(this);  // 双向关系维护
    }
}
```

### 3.3 聚合设计特点

1. **聚合内强一致性**：聚合根负责管理其关联实体的生命周期
2. **跨聚合引用**：通过外键 ID（`resume_id`）而非对象引用
3. **JSON 列存储**：复杂数据（questionsJson、strengthsJson）使用 JSON 列

---

## 四、仓储模式

### 4.1 仓储接口（继承 JpaRepository）

```java
// Spring Data JPA 仓储
@Repository
public interface ResumeRepository extends JpaRepository<ResumeEntity, Long> {
    // 方法命名查询
    Optional<ResumeEntity> findByFileHash(String fileHash);
    
    // 自定义 @Query
    @Query("SELECT r FROM ResumeEntity r WHERE r.analyzeStatus = :status")
    List<ResumeEntity> findByAnalyzeStatus(@Param("status") AsyncTaskStatus status);
}

@Repository
public interface InterviewSessionRepository extends JpaRepository<InterviewSessionEntity, Long> {
    Optional<InterviewSessionEntity> findBySessionId(String sessionId);
    
    List<InterviewSessionEntity> findByResumeIdOrderByCreatedAtDesc(Long resumeId);
}
```

### 4.2 仓储特点

- **面向聚合根**：每个聚合根对应一个仓储
- **Spring Data JPA**：简化 CRUD 操作
- **自定义查询**：方法命名约定 + `@Query` 注解

---

## 五、Domain Service vs Application Service

### 5.1 Application Service（应用服务）

**职责**：编排领域服务，处理用例流程

```java
// ResumeUploadService - 应用服务
@Service
@RequiredArgsConstructor
public class ResumeUploadService {
    
    private final ResumeParseService parseService;        // 依赖领域服务
    private final FileStorageService storageService;     // 依赖基础设施
    private final ResumePersistenceService persistenceService;
    
    public Map<String, Object> uploadAndAnalyze(MultipartFile file) {
        // 1. 验证文件
        fileValidationService.validateFile(file, MAX_FILE_SIZE, "简历");
        
        // 2. 解析简历文本
        String resumeText = parseService.parseResume(file);
        
        // 3. 保存到 RustFS
        String fileKey = storageService.uploadResume(file);
        
        // 4. 持久化到数据库
        ResumeEntity savedResume = persistenceService.saveResume(...);
        
        // 5. 发送异步任务
        analyzeStreamProducer.sendAnalyzeTask(savedResume.getId(), resumeText);
        
        return Map.of(...);
    }
}
```

### 5.2 Domain Service（领域服务）

**职责**：封装领域逻辑，不持有状态

```java
// ResumeParseService - 领域服务
@Service
@RequiredArgsConstructor
public class ResumeParseService {
    
    private final DocumentParseService documentParseService;
    
    // 领域方法：解析简历
    public String parseResume(MultipartFile file) {
        String contentType = detectContentType(file);
        if (!isSupported(contentType)) {
            throw new BusinessException(ErrorCode.RESUME_UNSUPPORTED_TYPE);
        }
        return documentParseService.parseToText(file);
    }
    
    // 领域方法：检测内容类型
    public String detectContentType(MultipartFile file) {
        // ...
    }
}
```

### 5.3 区分原则

| 特征 | Application Service | Domain Service |
|------|-------------------|----------------|
| **职责** | 编排、事务边界 | 封装领域逻辑 |
| **依赖** | 多个 Domain Service | 只依赖基础设施 |
| **事务** | 通常有 `@Transactional` | 无事务注解 |
| **示例** | `ResumeUploadService` | `ResumeParseService` |

---

## 六、值对象设计

### 6.1 枚举值对象

```java
// 异步任务状态
public enum AsyncTaskStatus {
    PENDING,     // 待处理
    PROCESSING,  // 处理中
    COMPLETED,   // 完成
    FAILED       // 失败
}

// 面试会话状态
public enum SessionStatus {
    CREATED,      // 会话已创建
    IN_PROGRESS,  // 面试进行中
    COMPLETED,    // 面试已完成
    EVALUATED     // 已生成评估报告
}

// 向量化状态
public enum VectorStatus {
    PENDING,
    PROCESSING,
    COMPLETED,
    FAILED
}
```

### 6.2 Record 值对象

```java
// 请求 DTO（不可变）
public record QueryRequest(
    String query,
    String knowledgeBaseId,
    Integer topK,
    Double minScore
) {}

// 响应 DTO（不可变）
public record QueryResponse(
    String answer,
    List<ChunkResult> chunks
) {}
```

---

## 七、Infrastructure 层

### 7.1 基础设施职责

```
infrastructure/
├── file/           # 文件处理（RustFS、Tika）
├── redis/          # Redis 操作（缓存、Stream）
├── export/         # PDF 导出
└── mapper/         # MapStruct 映射
```

### 7.2 基础设施特点

- **不涉及业务逻辑**：纯技术能力封装
- **被 Domain Service 依赖**：通过依赖注入
- **可替换性**：未来可以替换存储实现（如 S3 → MinIO）

---

## 八、异步任务与 CQRS

### 8.1 读写分离

```
写入路径：
Controller → Application Service → Repository → Database
                ↓
        StreamProducer → Redis Stream

读取路径：
Controller → Application Service → Repository → Database
```

### 8.2 异步任务流程

```java
// 简历分析 - 写入后异步处理
public Map<String, Object> uploadAndAnalyze(MultipartFile file) {
    // 1. 同步保存简历
    ResumeEntity savedResume = persistenceService.saveResume(...);
    
    // 2. 发送异步任务（立即返回）
    analyzeStreamProducer.sendAnalyzeTask(savedResume.getId(), resumeText);
    
    return Map.of("status", "PENDING");
}

// AnalyzeStreamConsumer - 异步消费
@Component
public class AnalyzeStreamConsumer extends AbstractStreamConsumer<AnalyzeTaskPayload> {
    @Override
    protected void processMessage(AnalyzeTaskPayload payload) {
        // 1. 调用 AI 分析
        ResumeAnalysisResponse response = gradingService.gradeResume(...);
        
        // 2. 更新状态
        persistenceService.updateAnalysisResult(payload.resumeId(), response);
    }
}
```

---

## 九、Entity 与 DTO 映射

### 9.1 MapStruct 映射

```java
// Infrastructure 层 - Mapper
@Mapper(componentModel = "spring")
public interface ResumeMapper {
    ResumeListItemDTO toListItemDTO(ResumeEntity entity);
    ResumeDetailDTO toDetailDTO(ResumeEntity entity);
}
```

### 9.2 映射原则

| 场景 | 映射方式 |
|------|---------|
| Entity → DTO | MapStruct（自动） |
| DTO → Entity | 手动构建（明确转换逻辑） |
| 简单拷贝 | `BeanUtils.copyProperties` |

---

## 十、DDD-lite 实现总结

### 10.1 符合 DDD-lite 的设计

| 实践 | 符合度 | 说明 |
|------|--------|------|
| 限界上下文划分 | ✅ | 5 个业务模块，边界清晰 |
| 聚合根设计 | ✅ | 每个模块有聚合根 Entity |
| 仓储模式 | ✅ | Spring Data JPA Repository |
| 领域服务 | ✅ | `*ParseService`、`*GradingService` |
| 值对象 | ✅ | enum、record、DTO |
| 基础设施分离 | ✅ | `infrastructure/` 包 |

### 10.2 简化之处

| 简化 | 原因 |
|------|------|
| 无 Domain Event | 业务复杂度不需要 |
| 无 Specification 模式 | JPA 查询足够简单 |
| Entity 直接用 JPA | 无单独 Domain Model |
| 无 Application Service 接口 | Controller 直接调用 Domain Service |

### 10.3 架构分层

```
┌─────────────────────────────────────────────┐
│           Presentation Layer                │
│         (Controller + @RateLimit)           │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│          Application Layer                  │
│    (Application Service - 编排领域服务)     │
│    例：ResumeUploadService                  │
│        InterviewCreateService               │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│            Domain Layer                     │
│  (Domain Service - 领域逻辑，不持有状态)    │
│  例：ResumeParseService                     │
│      InterviewGradingService                │
│  ────────────────────────────────────────  │
│  (Entity - 聚合根，管理生命周期)            │
│  例：ResumeEntity                            │
│      InterviewSessionEntity                 │
│  ────────────────────────────────────────  │
│  (Value Object - 不可变值)                  │
│  例：AsyncTaskStatus, QueryRequest          │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│         Infrastructure Layer                 │
│  (技术能力封装，被 Domain Service 依赖)     │
│  例：FileStorageService (S3)                │
│      RedisService (Stream)                  │
│      DocumentParseService (Tika)            │
│      PdfExportService (iText)               │
└─────────────────────────────────────────────┘
```

---

## 十一、与传统三层架构对比

| 维度 | 传统三层 | 本项目 DDD-lite |
|------|---------|----------------|
| **Service 层** | 一个大类包揽所有业务 | 按职责拆分为多个小 Service |
| **依赖方向** | Controller → Service → DAO | Controller → 多 Service → Infrastructure |
| **聚合** | 无 | 每个模块有聚合根 |
| **异步处理** | 简单线程池 | Redis Stream + Producer/Consumer |
| **值对象** | 无 | enum + record |
| **Infrastructure** | 散落各 Service | 独立层统一封装 |
