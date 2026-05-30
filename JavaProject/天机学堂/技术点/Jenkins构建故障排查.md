---
title: Jenkins 构建故障排查
tags: [Jenkins, Maven, 多模块构建, Docker, VM部署]
created: 2026-05-30
updated: 2026-05-30
status: completed
related: [[Maven依赖管理]], [[Docker部署]], [[Git工作流]]
---

# Jenkins 构建故障排查

## 1. 业务场景与核心诉求

天机学堂项目使用 Jenkins + Docker 部署在 VM 上，新增 `tj-learning` 模块后构建失败，需要排查并解决构建问题。

## 2. 最终落地方案 & 核心代码

### 2.1 问题1：依赖找不到

**错误信息：**
```
Could not find artifact com.tianji:tj-auth-resource-sdk:jar:1.0.0
Could not find artifact com.tianji:tj-api:jar:1.0.0
```

**原因：** Jenkins 只构建了 tj-learning，没有先构建依赖模块

**解决方案：**
```bash
# 先构建并安装依赖模块
cd /usr/local/src/jenkins/workspace/tjxt-dev-build
mvn clean install -pl tj-common,tj-auth/tj-auth-resource-sdk,tj-api -am -DskipTests
```

### 2.2 问题2：Maven 下载失败（网络问题）

**错误信息：**
```
Premature end of Content-Length delimited message body
Remote host terminated the handshake
```

**原因：** VM 网络不稳定，无法连接 Maven Central

**解决方案：** 配置阿里云镜像 `~/.m2/settings.xml`
```xml
<mirrors>
    <mirror>
        <id>aliyun</id>
        <mirrorOf>central</mirrorOf>
        <name>Aliyun Maven</name>
        <url>https://maven.aliyun.com/repository/public</url>
    </mirror>
</mirrors>
```

### 2.3 问题3：LearningLesson 实体类找不到

**错误信息：**
```
程序包com.tianji.learning.domain.po不存在
找不到符号: 类 LearningLesson
```

**原因：** `domain/po` 目录是未跟踪状态，没有提交到 git

**解决方案：**
```bash
cd D:\Code\JavaProjects\self\tjxt\tianji
git add tj-learning/src/main/java/com/tianji/learning/domain/po/
git commit -m "添加 LearningLesson 实体类"
git push origin dev
```

## 3. 原理剖析与踩坑记录

### 3.1 多模块项目构建顺序

Maven 多模块项目需要按依赖顺序构建：
1. tj-common（基础模块）
2. tj-auth/tj-auth-resource-sdk（认证SDK）
3. tj-api（API模块）
4. 其他业务模块（tj-learning 等）

### 3.2 踩坑记录

**坑1：Jenkins 只构建单个模块**
- 现象：依赖找不到
- 原因：没有先构建依赖模块
- 解决：使用 `-pl` 和 `-am` 参数指定模块

**坑2：网络不稳定导致下载失败**
- 现象：Premature end of Content-Length
- 原因：VM 网络不稳定
- 解决：配置国内镜像（阿里云）

**坑3：新文件未提交到 git**
- 现象：类找不到
- 原因：文件在本地但未 `git add`
- 解决：提交所有新文件

## 4. Jenkins 工作空间路径

- `/usr/local/src/jenkins/workspace/tj-learning` - 单独构建
- `/usr/local/src/jenkins/workspace/tjxt-dev-build` - 多模块构建

## 5. Maven 版本

- VM 上的 Maven 版本：3.9.16
