## Apache TIka 简介
----
内容分析工具箱 从上千种不同格式的文件（如 pdf，office，音频，视频等）中，通过统一接口提取出文本和元数据
## 文件上传实例
ResumeUploadService::uploadAndAnalyze
代码详解[[简历文件上传]]
![[Pasted image 20260421154621.png]]
## Tika 架构概览
---
Tika本身并不直接处理每一种文件，而是充当一个“中间商”，封装了许多底层库（处理PDF的PDFBox，处理Office的POI）
### Tika 处理流程：
1. Detect（识别类型）
2. Parse（选择并解析）
3. Handle（输出内容）

~~~ java
/**  
 * 检测文件的 MIME 类型  
 * 使用 Tika 进行基于内容的检测，比 HTTP 头部更准确  
 *  
 * @param file MultipartFile 文件  
 * @return MIME 类型字符串  
 */  
public String detectContentType(MultipartFile file) {  
    try (InputStream inputStream = file.getInputStream()) {  
        return tika.detect(inputStream, file.getOriginalFilename());  
    } catch (IOException e) {  
        log.warn("无法检测文件类型，使用 Content-Type 头部: {}", e.getMessage());  
        return file.getContentType();  
    }  
}


/**  
 * 核心解析方法：使用显式 Parser + Context 方式解析文档  
 * <p>  
 * 优化点：  
 * 1. 使用 BodyContentHandler 只提取正文内容  
 * 2. 禁用 EmbeddedDocumentExtractor，不解析嵌入资源（图片、附件）  
 * 3. 配置 PDFParserConfig，关闭图片和注释提取  
 * 4. 显式指定 Parser 到 Context，增强健壮性  
 *  
 * @param inputStream 文件输入流  
 * @return 提取的文本内容  
 * @throws IOException     IO 异常  
 * @throws TikaException   Tika 解析异常  
 * @throws SAXException    SAX 解析异常  
 */  
private String parseContent(InputStream inputStream) throws IOException, TikaException, SAXException {  
    // 1. 创建自动检测解析器  
    AutoDetectParser parser = new AutoDetectParser();  
  
    // 2. 创建内容处理器，只接收正文，限制最大长度为 5MB    
    BodyContentHandler handler = new BodyContentHandler(MAX_TEXT_LENGTH);  
  
    // 3. 创建元数据对象  
    Metadata metadata = new Metadata();  
  
    // 4. 创建解析上下文  
    ParseContext context = new ParseContext();  
  
    // 5. 显式指定 Parser 到 Context（增强健壮性）  
    context.set(Parser.class, parser);  
  
    // 6. 禁用嵌入文档解析（关键：避免提取图片引用和临时文件路径）  
    context.set(
    EmbeddedDocumentExtractor.class, new NoOpEmbeddedDocumentExtractor());  
  
    // 7. PDF 专用配置：关闭图片提取，按位置排序文本  
    PDFParserConfig pdfConfig = new PDFParserConfig();  
    pdfConfig.setExtractInlineImages(false);  
    pdfConfig.setSortByPosition(true); // 按 x/y 坐标排序文本，改善多栏布局解析顺序  
    // 注意：Tika 2.9.2 中 setExtractAnnotations 方法可能不存在，关闭图片提取已足够  
    context.set(PDFParserConfig.class, pdfConfig);  
  
    // 8. 执行解析  
    parser.parse(inputStream, handler, metadata, context);  
  
    // 9. 返回提取的文本内容  
    return handler.toString();  
}
~~~

| 组件             | 作用                                                                                         | 理解                |
| -------------- | ------------------------------------------------------------------------------------------ | ----------------- |
| AutoDectParser | 结合 Detect 检测出的媒体类型（MIME），并委派给具体的Parser执行解析                                                 | 根据文件类型，自动生成对应的解析器 |
| ContentHandler | 以SAX（simple api for xml：解析文件时像流水线一样，读取一个文件就抛出一个“事务”，处理大文件时，保持内存占用平缓）并决定输出形式（纯文本/XHTML/限长等） | 承载内容，并决定内容形式      |
| Metadata       | 存放解析过程中提取的元信息（Content-Type、作者、标题、创建时间、页数等）                                                 | 存放元信息，就像照片的属性     |
| ParseContext   | 像解析器传递上下文对象与配置(例如 pdf解析策略、OCR配置、EmbeddedDocumentExtractor 等)                               | 传递 解析器对象 和 配置     |

context解析：
~~~ plain
	context 就像一个"工具箱"
    ↓
	往工具箱里放工具：
	    - 扳手（Parser）
	    - 螺丝刀（EmbeddedDocumentExtractor）
	    - 锤子（PDFParserConfig）
~~~

运作流程：
~~~ plain
1. 读取文件流
   InputStream inputStream = file.getInputStream();

2. 创建处理器（筛子）
   BodyContentHandler handler = new BodyContentHandler(MAX_TEXT_LENGTH);

3. 配置解析器
   - 禁用图片提取
   - 按位置排序文本

4. 执行解析
   parser.parse(inputStream, handler, metadata, context);

5. 获取文本
   String text = handler.toString();
   
   解析前：
┌─────────────┐
│ inputStream │  ← 文件输入流（只读）
├─────────────┤
│   handler   │  ← 空的处理器
├─────────────┤
│  metadata   │  ← 空的元数据
├─────────────┤
│   context   │  ← 解析配置（只读）
└─────────────┘
         ↓
    parser.parse()
         ↓
解析后：
┌─────────────┐
│ inputStream │  ← 不变
├─────────────┤
│   handler   │  ← 填充了文本内容 ✅
├─────────────┤
│  metadata   │  ← 填充了文件信息 ✅
├─────────────┤
│   context   │  ← 不变
└─────────────┘

~~~

## NoOpEmbeddedDocumentExtractor
---
> context.set(
    EmbeddedDocumentExtractor.class, new NoOpEmbeddedDocumentExtractor());  

解决嵌入资源污染的核心类
~~~ java

~~~