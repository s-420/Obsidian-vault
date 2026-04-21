## Apache TIka 简介
----
内容分析工具箱 从上千种不同格式的文件（如 pdf，office，音频，视频等）中，通过统一接口提取出文本和元数据
## 文件上传实例
ResumeUploadService::uploadAndAnalyze[[简历文件上传]]
![[Pasted image 20260421154621.png]]

~~~ java
/**  
 * 上传并分析简历（异步）  
 *  
 * @param file 简历文件  
 * @return 上传结果（分析将异步进行）  
 */  
public Map<String, Object> uploadAndAnalyze(org.springframework.web.multipart.MultipartFile file) {  
    long startTime = System.currentTimeMillis();  
  
    // 1. 验证文件  
    // fileValidationService.validateFile（非空、限制大小）  
    fileValidationService.validateFile(file, MAX_FILE_SIZE, "简历");  
  
    String fileName = file.getOriginalFilename();  
    long fileSize = file.getSize();  
    log.info("收到简历上传请求: {}, 大小: {} bytes ({}), 上传开始处理",  
        fileName, fileSize, formatFileSize(fileSize));  
  
    // 2. 验证(简历)文件类型  
    // parseService.detectContentType  
    //      (contentTypeDetectionService.detectContentType    //          (tika.detect(file)))（检测文件MIME类型）  
    String contentType = parseService.detectContentType(file);  
    validateContentType(contentType);  
  
    // 3. 检查简历是否已存在（去重）  
    // persistenceService.findExistingResume(  
    //      (fileHashService.calculateHash)(计算文件hash值）  
    //      (resumeRepository.findByFileHash)(通过文件hash值找到文件，重复，access++))  
    Optional<ResumeEntity> existingResume = persistenceService.findExistingResume(file);  
    if (existingResume.isPresent()) {  
        log.info("简历上传处理完成（重复）: {} - 耗时: {}ms",  
            fileName, System.currentTimeMillis() - startTime);  
        return handleDuplicateResume(existingResume.get());  
    }  
  
    // 4. 解析简历文本  
    long parseStart = System.currentTimeMillis();  
    // parseService.parseResume(文件)(  
    //      (documentParseService.parseContent(文件)(  
    //          (parseContent(文件输入流))(使用显式 Parser(tika) + Context 方式解析文档，解析内容)  
    //          (textCleaningService.cleanText(解析内容))(语义过滤，规范格式化)))  
    String resumeText = parseService.parseResume(file);  
    if (resumeText == null || resumeText.trim().isEmpty()) {  
        throw new BusinessException(ErrorCode.RESUME_PARSE_FAILED, "无法从文件中提取文本内容，请确保文件不是扫描版PDF");  
    }  
    log.info("简历文本解析完成: {} - 解析耗时: {}ms, 文本长度: {} 字符",  
        fileName, System.currentTimeMillis() - parseStart, resumeText.length());  
  
    // 5. 保存简历到RustFS  
    long storageStart = System.currentTimeMillis();  
    //storageService.uploadResume(  
    //      (uploadFile(文件, "resumes"(存储键前缀))  
    //          (s3Client.putObject(s3客户端上传put))))  
    String fileKey = storageService.uploadResume(file);  
    String fileUrl = storageService.getFileUrl(fileKey);  
    log.info("简历已存储到RustFS: {} - 存储耗时: {}ms",  
        fileKey, System.currentTimeMillis() - storageStart);  
  
    // 6. 保存简历到数据库（状态为 PENDING）  
    //persistenceService.saveResume(file 文件，resumeText 文件内容，fileKey 文件key，fileUrl 文件路径)(  
    //      resumeRepository.save(简历对象)  
    ResumeEntity savedResume = persistenceService.saveResume(file, resumeText, fileKey, fileUrl);  
  
    // 7. 发送分析任务到 Redis Stream（异步处理）  
    // analyzeStreamProducer.sendAnalyzeTask(已保存简历id, 简历内容)  
    //      sendTask(AnalyzeTaskPayload对象：用于构建redisService.streamAdd的message)(  
    //          redisService.streamAdd(streamKey stream键，message 消息内容，maxlen stream最大)  
    analyzeStreamProducer.sendAnalyzeTask(savedResume.getId(), resumeText);  
  
    long totalTime = System.currentTimeMillis() - startTime;  
    log.info("简历上传处理完成: {}, resumeId={} - 总耗时: {}ms (解析+存储+入库)",  
        fileName, savedResume.getId(), totalTime);  
  
    // 8. 返回结果（状态为 PENDING，前端可轮询获取最新状态）  
    return Map.of(  
        "resume", Map.of(  
            "id", savedResume.getId(),  
            "filename", savedResume.getOriginalFilename(),  
            "analyzeStatus", AsyncTaskStatus.PENDING.name()  
        ),  
        "storage", Map.of(  
            "fileKey", fileKey,  
            "fileUrl", fileUrl,  
            "resumeId", savedResume.getId()  
        ),  
        "duplicate", false  
    );  
}
~~~

