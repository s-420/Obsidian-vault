[[3.Spring Boot + RustFs 构建高性能 S3 兼容的对象存储服务.pdf]]
## RustFS 简介
----
`rustfs` 是一个使用 Rust 语言编写的轻量级、高性能分布式文件系统或对象存储服务（通常作为类似 MinIO 的简洁替代方案）。它充分利用了 Rust 的内存安全和并发特性，旨在提供极低延迟的文件读写能力，非常适合作为云原生环境下的后端存储组件。

## RestFS 安装
---
``` plain
拉取镜像：
docker pull rustfs/rustfs

启动容器：
docker run -d `
  --name rustfs_local `
  -p 9000:9000 `
  -p 9001:9001 `
  -v D:/Code/rustfs/data:/data `
  rustfs/rustfs:latest `
  /data
```
> ` -v D:/Code/rustfs/data:/data` 挂载数据卷，持久化支持

## RustFS 管理后台
----
在管理后台可以：
- 创建和管理存储桶（Bucket）
- 查看文件列表
- 配置访问策略
- 生成Access Key / Secret Key

## RestFS 在SpringBoot中的 整合
---
### **引入依赖**（依赖注入的方法 [[Gradle#Gradle 项目依赖管理指南]] ）
在 `build.gradle` 中添加以下代码 ：
``` Groovy
dependencies {
    // AWS S3 SDK for RustFS storage
    implementation 'software.amazon.awssdk:s3:2.25.27'
}
```
### 所有中间件都可以参照这个**整合模式**：
- 配置绑定
	- 配置属性：application.yml
	- 配置属性类：StorageConfigProperties（interview.guide.common.config）
- 实例化客户端
	- S3 客户端配置：S3Config（interview.guide.common.config）
- 内部服务封装
	- 服务类设计：FileStorageService（interview.guide.infrastructure.file）
- 外部业务调用（FileStorageService 中的方法，通过注入FileStorageService调用方法）
	- 文件上传
	- 文件下载
	- 文件删除
	- 确保存储桶存在

## 业务集成示例
---
### 简历上传分析流程

