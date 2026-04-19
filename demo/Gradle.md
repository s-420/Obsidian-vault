## Gradle 介绍
----
运行在Jvm上的一个项目构建工具，用来帮助我们自动构建项目

主要作用：
- 构建项目
- 管理依赖
- 统一开发结构

Gradle构建脚本使用 **Groovy 或 Kotlin** 语言编写，表达能力强，足够灵活

## Groovy介绍
----
Groovy是运行在JVM上的脚本语言，是居于Java扩展的动态语言

基于JVM的语言比如Groovy，Kotlin，Java，Scala，最终都会编译成字节码文件并在JVM上运行

## Gradle VS Maven
----
构建项目，管理依赖，统一结构化 的区别：
![[{762133DB-73EF-4C7F-B556-D20B5D965320}.png]]

具体实现的区别：
![[{533CE39A-31BE-43B0-A9A8-1653D6B9CC84}.png]]

## Gradle 的实现（Gradle Wrapper）
---
Grandle 的结构
``` text
├── gradle
│   └── wrapper
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── gradlew
└── gradlew.bat
```
每个文件含义如下：
- grandle-wrapper.jar：包含了Gradle运行时的逻辑代码
- grandle-wrapper.properties：定义了Gradle的版本号和Gradle运行时的行为属性
- gradlew：Linux平台下，用于执行Gradle命令的包装器脚本
- gradlew.bat：Linux平台下，用于执行Gradle命令的包装器脚本

## Gradle 引入依赖
使用 Version Catalog（版本目录） 方式管理依赖。这是现代 Gradle 推荐的最佳实践。

项目依赖管理结构
├── gradle/libs.versions.toml   # ✅ 集中定义版本号和依赖别名
└── app/build.gradle           # 实际引用
引入依赖的方法
1. 添加新的依赖版本（在 gradle/libs.versions.toml 中）
[versions]
# 新增版本号
my-library = "1.2.3"
[versions]
spring-boot = "4.0.1"
springAi = "2.0.0-M4"
 # ... 其他已有版本
[libraries]
# 新增依赖（引用已定义的版本）
my-library = { module = "com.example:my-library", version.ref = "my-library" }
2. 在 app/build.gradle 中使用
dependencies {
    // 方式一：通过 libs 引用（推荐）
    implementation libs.my.library
    
    // 方式二：直接写坐标
    implementation 'com.example:my-library:1.2.3'
}
现有依赖引用示例
// 在 build.gradle 中
implementation libs.tika.core          // 引用 libs.versions.toml 中的定义
implementation "org.springframework.ai:spring-ai-starter-model-openai:${libs.versions.springAi.get()}"
