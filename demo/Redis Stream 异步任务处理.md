![[{1D457EB6-8D37-40D0-AF3A-76CA8FE63CF8}.png]] 
## 简历上传业务的 Redis Stream 流式处理流程分析

基于提供的代码，我来详细分析整个异步处理流程。

---

## 一、整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    简历上传异步处理流程                        │
└─────────────────────────────────────────────────────────────────┘

用户上传简历
    ↓
┌─────────────────────────────────────────┐
│ 1. 同步处理（快速）                   │
│    - 验证文件                         │
│    - 解析文本                         │
│    - 保存文件                         │
│    - 保存数据库                       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 2. 发送任务到 Redis Stream          │
│    AnalyzeStreamProducer              │
└─────────────────────────────────────────┘
    ↓
    Redis Stream (消息队列）
    ↓
┌─────────────────────────────────────────┐
│ 3. 异步处理（后台）                   │
│    AnalyzeStreamConsumer              │
│    - 消费消息                         │
│    - AI 分析                         │
│    - 保存结果                         │
└─────────────────────────────────────────┘
    ↓
    更新数据库状态
```

---

## 二、详细流程分析

### 阶段 1：同步处理（上传流程）

#### 步骤 1.1：用户上传简历

```java
// ResumeUploadService.uploadAndAnalyze()
@PostMapping("/api/resumes/upload")
public Result<Map<String, Object>> uploadAndAnalyze(@RequestParam("file") MultipartFile file) {
    // 1. 验证文件
    fileValidationService.validateFile(file, MAX_FILE_SIZE, "简历");
    
    //2. 验证文件类型
    String contentType = parseService.detectContentType(file);
    
    //3. 检查去重
    Optional<ResumeEntity> existingResume = persistenceService.findExistingResume(file);
    if (existingResume.isPresent()) {
        return handleDuplicateResume(existingResume.get());
    }
    
    //4. 解析简历文本
    String resumeText = parseService.parseResume(file);
    
    //5. 保存到对象存储
    String fileKey = storageService.uploadResume(file);
    
    //6. 保存到数据库（状态为 PENDING）
    ResumeEntity savedResume = persistenceService.saveResume(file, resumeText, fileKey, fileUrl);
    
    //7. 发送分析任务到 Redis Stream ⭐
    analyzeStreamProducer.sendAnalyzeTask(savedResume.getId(), resumeText);
    
    //8. 返回结果（状态为 PENDING）
    return Map.of(...);
}
```

---

### 阶段 2：发送任务到 Redis Stream

#### 步骤 2.1：生产者发送任务

**位置**：[AnalyzeStreamProducer.sendAnalyzeTask()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\modules\resume\listener\AnalyzeStreamProducer.java#L36)

```java
public void sendAnalyzeTask(Long resumeId, String content) {
    sendTask(new AnalyzeTaskPayload(resumeId, content));
}
```

---

#### 步骤 2.2：基类处理发送

**位置**：[AbstractStreamProducer.sendTask()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\common\async\AbstractStreamProducer.java#L22)

```java
protected void sendTask(T payload) {
    try {
        // 1. 构建消息
        Map<String, String> message = buildMessage(payload);
        
        // 2. 发送到 Redis Stream
        String messageId = redisService.streamAdd(
            streamKey(),                    // Stream 键
            message,                       // 消息内容
            AsyncTaskStreamConstants.STREAM_MAX_LEN  // 最大长度
        );
        
        log.info("{}任务已发送到Stream: {}, messageId={}",
            taskDisplayName(), payloadIdentifier(payload), messageId);
    } catch (Exception e) {
        // 3. 发送失败处理
        log.error("发送{}任务失败: {}, error={}",
            taskDisplayName(), payloadIdentifier(payload), e.getMessage(), e);
        onSendFailed(payload, "任务入队失败: " + e.getMessage());
    }
}
```

---

#### 步骤 2.3：构建消息内容

**位置**：[AnalyzeStreamProducer.buildMessage()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\modules\resume\listener\AnalyzeStreamProducer.java#L52)

```java
@Override
protected Map<String, String> buildMessage(AnalyzeTaskPayload payload) {
    return Map.of(
        AsyncTaskStreamConstants.FIELD_RESUME_ID, payload.resumeId().toString(),
        AsyncTaskStreamConstants.FIELD_CONTENT, payload.content(),
        AsyncTaskStreamConstants.FIELD_RETRY_COUNT, "0"  // 初始重试次数为 0
    );
}
```

**消息结构**：
```json
{
  "resumeId": "123",
  "content": "张三，Java开发工程师...",
  "retryCount": "0"
}
```

---

#### 步骤 2.4：Redis 添加消息

**位置**：[RedisService.streamAdd()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\infrastructure\redis\RedisService.java#L243)

```java
public String streamAdd(String streamKey, Map<String, String> message, int maxLen) {
    RStream<String, String> stream = redissonClient.getStream(streamKey, StringCodec.INSTANCE);
    
    // 1. 构建参数
    StreamAddArgs<String, String> args = StreamAddArgs.entries(message);
    if (maxLen > 0) {
        args.trimNonStrict().maxLen(maxLen);  // 限制 Stream 长度
    }
    
    // 2. 添加消息
    StreamMessageId messageId = stream.add(args);
    
    log.debug("发送 Stream 消息: stream={}, messageId={}, maxLen={}", streamKey, messageId, maxLen);
    return messageId.toString();
}
```

---

### 阶段 3：消费者启动

#### 步骤 3.1：消费者初始化

**位置**：[AbstractStreamConsumer.init()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\common\async\AbstractStreamConsumer.java#L27)

```java
@PostConstruct
public void init() {
    // 1. 生成唯一消费者名称
    this.consumerName = consumerPrefix() + UUID.randomUUID().toString().substring(0, 8);
    
    // 2. 创建消费者组（如果不存在）
    try {
        redisService.createStreamGroup(streamKey(), groupName());
        log.info("Redis Stream 消费者组已创建或已存在: {}", groupName());
    } catch (Exception e) {
        log.warn("创建消费者组时发生异常（可能已存在）: {}", e.getMessage());
    }
    
    // 3. 创建线程池
    this.executorService = new ThreadPoolExecutor(
        1,  // 核心线程数
        1,  // 最大线程数
        0L,
        TimeUnit.MILLISECONDS,
        new LinkedBlockingQueue<>(),
        r -> {
            Thread t = new Thread(r, threadName());
            t.setDaemon(true);  // 守护线程
            return t;
        },
        new ThreadPoolExecutor.AbortPolicy()
    );
    
    // 4. 启动消费循环
    running.set(true);
    executorService.submit(this::consumeLoop);
    log.info("{}消费者已启动: consumerName={}", taskDisplayName(), consumerName);
}
```

---

#### 步骤 3.2：消费循环

**位置**：[AbstractStreamConsumer.consumeLoop()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\common\async\AbstractStreamConsumer.java#L56)

```java
private void consumeLoop() {
    while (running.get()) {  // 持续运行
        try {
            // 1. 从 Stream 读取消息（阻塞模式）
            redisService.streamConsumeMessages(
                streamKey(),
                groupName(),
                consumerName,
                AsyncTaskStreamConstants.BATCH_SIZE,      // 每次读取数量
                AsyncTaskStreamConstants.POLL_INTERVAL_MS,  // 阻塞超时时间
                this::processMessage  // 消息处理器
            );
        } catch (Exception e) {
            if (Thread.currentThread().isInterrupted()) {
                log.info("消费者线程被中断");
                break;
            }
            log.error("消费消息时发生错误: {}", e.getMessage(), e);
        }
    }
}
```

---

### 阶段 4：消费消息

#### 步骤 4.1：从 Stream 读取消息

**位置**：[RedisService.streamConsumeMessages()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\infrastructure\redis\RedisService.java#L207)

```java
public boolean streamConsumeMessages(
        String streamKey,
        String groupName,
        String consumerName,
        int count,
        long blockTimeoutMs,
        StreamMessageProcessor processor) {

    RStream<String, String> stream = redissonClient.getStream(streamKey, StringCodec.INSTANCE);

    // 1. 使用阻塞读取，让 Redis 服务端等待消息
    Map<StreamMessageId, Map<String, String>> messages;
    try {
        messages = stream.readGroup(
            groupName,
            consumerName,
            StreamReadGroupArgs.neverDelivered()
                .count(count)
                .timeout(Duration.ofMillis(blockTimeoutMs))  // 阻塞等待
        );
    } catch (ClassCastException e) {
        // Redisson 4.0.0 bug: 无消息时返回 EmptyList
        return false;
    }

    if (messages == null || messages.isEmpty()) {
        return false;  // 无消息
    }

    // 2. 处理每条消息
    for (Map.Entry<StreamMessageId, Map<String, String>> entry : messages.entrySet()) {
        processor.process(entry.getKey(), entry.getValue());
    }

    return true;
}
```

---

#### 步骤 4.2：处理消息

**位置**：[AbstractStreamConsumer.processMessage()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\common\async\AbstractStreamConsumer.java#L72)

```java
private void processMessage(StreamMessageId messageId, Map<String, String> data) {
    // 1. 解析消息内容
    T payload = parsePayload(messageId, data);
    if (payload == null) {
        ackMessage(messageId);  // 消息格式错误，直接 ACK
        return;
    }

    // 2. 获取重试次数
    int retryCount = parseRetryCount(data);
    
    log.info("开始处理{}任务: {}, messageId={}, retryCount={}",
        taskDisplayName(), payloadIdentifier(payload), messageId, retryCount);

    try {
        // 3. 标记为处理中
        markProcessing(payload);
        
        // 4. 执行业务逻辑
        processBusiness(payload);
        
        // 5. 标记为完成
        markCompleted(payload);
        
        // 6. 确认消息（ACK）
        ackMessage(messageId);
        
        log.info("{}任务完成: {}", taskDisplayName(), payloadIdentifier(payload));
    } catch (Exception e) {
        log.error("{}任务失败: {}, error={}", 
            taskDisplayName(), payloadIdentifier(payload), e.getMessage(), e);
        
        // 7. 失败处理
        if (retryCount < AsyncTaskStreamConstants.MAX_RETRY_COUNT) {
            // 重试：重新入队
            retryMessage(payload, retryCount + 1);
        } else {
            // 超过最大重试次数：标记为失败
            markFailed(payload, truncateError(
                taskDisplayName() + "失败(已重试" + retryCount + "次): " + e.getMessage()
            ));
        }
        
        // 8. 确认消息（ACK）
        ackMessage(messageId);
    }
}
```

---

### 阶段 5：业务处理

#### 步骤 5.1：标记处理中

**位置**：[AnalyzeStreamConsumer.markProcessing()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\modules\resume\listener\AnalyzeStreamConsumer.java#L68)

```java
@Override
protected void markProcessing(AnalyzePayload payload) {
    updateAnalyzeStatus(payload.resumeId(), AsyncTaskStatus.PROCESSING, null);
}

private void updateAnalyzeStatus(Long resumeId, AsyncTaskStatus status, String error) {
    try {
        resumeRepository.findById(resumeId).ifPresent(resume -> {
            resume.setAnalyzeStatus(status);
            resume.setAnalyzeError(error);
            resumeRepository.save(resume);
            log.debug("分析状态已更新: resumeId={}, status={}", resumeId, status);
        });
    } catch (Exception e) {
        log.error("更新分析状态失败: resumeId={}, status={}, error={}", 
            resumeId, status, e.getMessage(), e);
    }
}
```

---

#### 步骤 5.2：执行 AI 分析

**位置**：[AnalyzeStreamConsumer.processBusiness()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\modules\resume\listener\AnalyzeStreamConsumer.java#L73)

```java
@Override
protected void processBusiness(AnalyzePayload payload) {
    Long resumeId = payload.resumeId();
    
    // 1. 检查简历是否存在
    if (!resumeRepository.existsById(resumeId)) {
        log.warn("简历已被删除，跳过分析任务: resumeId={}", resumeId);
        return;
    }

    // 2. 调用 AI 分析服务
    ResumeAnalysisResponse analysis = gradingService.analyzeResume(payload.content());
    
    // 3. 获取简历实体
    ResumeEntity resume = resumeRepository.findById(resumeId).orElse(null);
    if (resume == null) {
        log.warn("简历在分析期间被删除，跳过保存结果: resumeId={}", resumeId);
        return;
    }
    
    // 4. 保存分析结果
    persistenceService.saveAnalysis(resume, analysis);
}
```

---

#### 步骤 5.3：标记完成

**位置**：[AnalyzeStreamConsumer.markCompleted()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\modules\resume\listener\AnalyzeStreamConsumer.java#L87)

```java
@Override
protected void markCompleted(AnalyzePayload payload) {
    updateAnalyzeStatus(payload.resumeId(), AsyncTaskStatus.COMPLETED, null);
}
```

---

### 阶段 6：失败处理

#### 步骤 6.1：重试消息

**位置**：[AnalyzeStreamConsumer.retryMessage()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\modules\resume\listener\AnalyzeStreamConsumer.java#L93)

```java
@Override
protected void retryMessage(AnalyzePayload payload, int retryCount) {
    Long resumeId = payload.resumeId();
    String content = payload.content();
    
    try {
        // 1. 构建重试消息
        Map<String, String> message = Map.of(
            AsyncTaskStreamConstants.FIELD_RESUME_ID, resumeId.toString(),
            AsyncTaskStreamConstants.FIELD_CONTENT, content,
            AsyncTaskStreamConstants.FIELD_RETRY_COUNT, String.valueOf(retryCount)
        );

        // 2. 重新入队
        redisService().streamAdd(
            AsyncTaskStreamConstants.RESUME_ANALYZE_STREAM_KEY,
            message,
            AsyncTaskStreamConstants.STREAM_MAX_LEN
        );
        
        log.info("简历分析任务已重新入队: resumeId={}, retryCount={}", resumeId, retryCount);

    } catch (Exception e) {
        log.error("重试入队失败: resumeId={}, error={}", resumeId, e.getMessage(), e);
        updateAnalyzeStatus(resumeId, AsyncTaskStatus.FAILED, 
            truncateError("重试入队失败: " + e.getMessage()));
    }
}
```

---

#### 步骤 6.2：标记失败

**位置**：[AnalyzeStreamConsumer.markFailed()](file:///D:\Code\JavaProjects\interview-guide\app\src\main\java\interview\guide\modules\resume\listener\AnalyzeStreamConsumer.java#L113)

```java
@Override
protected void markFailed(AnalyzePayload payload, String error) {
    updateAnalyzeStatus(payload.resumeId(), AsyncTaskStatus.FAILED, error);
}
```

---

## 三、完整流程时序图

```
用户                    上传服务              生产者              Redis              消费者              AI服务              数据库
 │                       │                    │                   │                   │                   │                   │
 │ 上传简历               │                    │                   │                   │                   │                   │
 ├──────────────────────>│                    │                   │                   │                   │                   │
 │                       │ 验证文件            │                   │                   │                   │                   │
 │                       │ 解析文本            │                   │                   │                   │                   │
 │                       │ 保存文件            │                   │                   │                   │                   │
 │                       │ 保存数据库          │                   │                   │                   │                   │
 │                       │                    │                   │                   │                   │                   │
 │                       │ 发送分析任务        │                   │                   │                   │                   │
 │                       ├───────────────────>│                   │                   │                   │                   │
 │                       │                    │ XADD              │                   │                   │                   │
 │                       │                    ├──────────────────>│                   │                   │                   │
 │                       │                    │                   │                   │                   │                   │
 │                       │ 返回 PENDING 状态   │                   │                   │                   │                   │
 │<──────────────────────┤                    │                   │                   │                   │                   │
 │                       │                    │                   │                   │                   │                   │
 │                       │                    │                   │ 消费循环            │                   │                   │
 │                       │                    │                   ├──────────────────>│                   │                   │
 │                       │                    │                   │ XREADGROUP        │                   │                   │
 │                       │                    │<──────────────────┤                   │                   │                   │
 │                       │                    │                   │                   │                   │                   │
 │                       │                    │                   │ 标记 PROCESSING    │                   │                   │
 │                       │                    │                   ├───────────────────────────────────────>│                   │
 │                       │                    │                   │                   │                   │                   │
 │                       │                    │                   │ 调用 AI 分析       │                   │                   │
 │                       │                    │                   ├──────────────────────────────────────────────>│
 │                       │                    │                   │                   │                   │                   │
 │                       │                    │                   │                   │ 分析完成            │                   │
 │                       │                    │                   │<───────────────────────────────────────┤
 │                       │                    │                   │                   │                   │                   │
 │                       │                    │                   │ 保存分析结果       │                   │                   │
 │                       │                    │                   ├──────────────────────────────────────────────────────>│
 │                       │                    │                   │                   │                   │                   │
 │                       │                    │                   │ 标记 COMPLETED     │                   │                   │
 │                       │                    │                   ├───────────────────────────────────────>│                   │
 │                       │                    │                   │                   │                   │                   │
 │                       │                    │                   │ ACK 消息          │                   │                   │
 │                       │                    │                   ├──────────────────>│                   │                   │
 │                       │                    │                   │                   │                   │                   │
 │                       │                    │                   │                   │                   │                   │
 │ 轮询状态               │                    │                   │                   │                   │                   │
 ├──────────────────────>│                    │                   │                   │                   │                   │
 │                       │ 查询数据库          │                   │                   │                   │                   │
 │                       ├──────────────────────────────────────────────────────────────────────────────────────>│
 │                       │<───────────────────────────────────────────────────────────────────────────────┤
 │                       │                    │                   │                   │                   │                   │
 │ 返回 COMPLETED         │                    │                   │                   │                   │                   │
 │<──────────────────────┤                    │                   │                   │                   │                   │
```

---

## 四、状态转换图

```
简历分析状态转换：

PENDING（等待中）
    ↓
发送任务到 Stream
    ↓
PROCESSING（处理中）
    ↓
    ├─ 成功 → COMPLETED（完成）
    │
    └─ 失败 → 重试
              ↓
         重试次数 < MAX_RETRY_COUNT
              ↓
         重新入队 → PROCESSING
              ↓
         重试次数 >= MAX_RETRY_COUNT
              ↓
         FAILED（失败）
```

---

## 五、关键设计点

### 1. 异步处理优势

| 优势 | 说明 |
|------|------|
| **快速响应** | 用户无需等待 AI 分析完成 |
| **提升吞吐量** | 可以并发处理多个分析任务 |
| **解耦系统** | 上传和分析分离，互不影响 |
| **容错能力** | 分析失败不影响上传 |

---

### 2. Redis Stream 优势

| 特性 | 说明 |
|------|------|
| **持久化** | 消息持久化到磁盘 |
| **消费者组** | 支持多消费者，负载均衡 |
| **ACK 机制** | 确保消息不丢失 |
| **阻塞读取** | 减少轮询，降低 CPU 消耗 |
| **消息重试** | 支持失败重试 |

---

### 3. 重试机制

```java
if (retryCount < AsyncTaskStreamConstants.MAX_RETRY_COUNT) {
    // 重试：重新入队
    retryMessage(payload, retryCount + 1);
} else {
    // 超过最大重试次数：标记为失败
    markFailed(payload, error);
}
```

**重试策略**：
- 最大重试次数：`MAX_RETRY_COUNT`
- 每次重试增加 `retryCount`
- 超过最大次数标记为失败

---

### 4. 状态管理

| 状态 | 含义 | 触发时机 |
|------|------|----------|
| **PENDING** | 等待分析 | 上传完成后 |
| **PROCESSING** | 分析中 | 消费者开始处理 |
| **COMPLETED** | 分析完成 | AI 分析成功 |
| **FAILED** | 分析失败 | 重试次数超限 |

---

## 六、总结

### 完整流程

```
1. 用户上传简历
   ↓
2. 同步处理（快速）
   - 验证文件
   - 解析文本
   - 保存文件
   - 保存数据库（状态：PENDING）
   ↓
3. 发送任务到 Redis Stream
   - 生产者构建消息
   - 添加到 Stream
   ↓
4. 消费者消费消息
   - 从 Stream 读取（阻塞模式）
   - 解析消息内容
   ↓
5. 执行业务逻辑
   - 标记状态：PROCESSING
   - 调用 AI 分析
   - 保存分析结果
   - 标记状态：COMPLETED
   ↓
6. 确认消息（ACK）
   ↓
7. 前端轮询获取结果
```

### 核心组件

| 组件 | 作用 |
|------|------|
| **AnalyzeStreamProducer** | 生产者，发送任务到 Stream |
| **AnalyzeStreamConsumer** | 消费者，处理分析任务 |
| **AbstractStreamProducer** | 生产者基类，统一发送逻辑 |
| **AbstractStreamConsumer** | 消费者基类，统一消费逻辑 |
| **RedisService** | Redis 操作封装 |

### 设计亮点

- ✅ **异步处理**：提升用户体验
- ✅ **消息队列**：解耦上传和分析
- ✅ **重试机制**：提高成功率
- ✅ **状态管理**：实时跟踪进度
- ✅ **容错能力**：失败不影响其他任务
        