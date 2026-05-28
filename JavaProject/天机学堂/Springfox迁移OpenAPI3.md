---
title: Springfox迁移SpringDoc OpenAPI3
tags: [SpringBoot, OpenAPI, Knife4j, 迁移]
created: 2026-05-28
updated: 2026-05-28
status: 100%
related: [[MyBatis-Plus分页查询]]
---

# Springfox 迁移 SpringDoc OpenAPI3

## 1. 业务场景与核心诉求

将 Spring Boot 2.7 项目中的 Swagger 从 **springfox (knife4j-spring-boot-starter 3.0.3)** 迁移到 **SpringDoc OpenAPI3 (knife4j-openapi3-spring-boot-starter 4.1.0)**，解决 springfox 停止维护、兼容性差的问题。

## 2. 最终落地方案 & 核心代码

### 2.1 POM 依赖变更

```xml
<!-- 旧依赖 -->
<dependency>
    <groupId>com.github.xiaoymin</groupId>
    <artifactId>knife4j-spring-boot-starter</artifactId>
    <version>3.0.3</version>
</dependency>

<!-- 新依赖 -->
<dependency>
    <groupId>com.github.xiaoymin</groupId>
    <artifactId>knife4j-openapi3-spring-boot-starter</artifactId>
    <version>4.1.0</version>
</dependency>
```

### 2.2 配置类重写

```java
@Configuration
@ConditionalOnProperty(prefix = "tj.swagger", name = "enable", havingValue = "true")
@EnableConfigurationProperties(SwaggerConfigProperties.class)
public class Knife4jConfiguration {

    @Resource
    private SwaggerConfigProperties swaggerConfigProperties;

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title(swaggerConfigProperties.getTitle())
                        .description(swaggerConfigProperties.getDescription())
                        .contact(new Contact()
                                .name(swaggerConfigProperties.getContactName())
                                .url(swaggerConfigProperties.getContactUrl())
                                .email(swaggerConfigProperties.getContactEmail()))
                        .version(swaggerConfigProperties.getVersion()));
    }
}
```

### 2.3 注解映射表

| 旧注解 (springfox) | 新注解 (OpenAPI3) |
|--------------------|--------------------|
| `@ApiModel(description = "...")` | `@Schema(description = "...")` |
| `@ApiModelProperty(value = "...")` | `@Schema(description = "...")` |
| `@Api(tags = "...")` | `@Tag(name = "...")` |
| `@ApiOperation("...")` | `@Operation(summary = "...")` |
| `@ApiParam("...")` | `@Parameter(description = "...")` |
| `@ApiImplicitParam` | `@Parameter(description = "...")` |
| `@ApiIgnore` | `@Hidden` |

### 2.4 application.yml 配置

```yaml
springdoc:
  swagger-ui:
    path: /swagger-ui.html
  api-docs:
    path: /v3/api-docs
  packages-to-scan: com.example.controller
```

## 3. 原理剖析与踩坑记录

### 3.1 关键区别

| 特性 | springfox | springdoc |
|------|-----------|-----------|
| 底层实现 | 自己解析注解 | 基于 OpenAPI 3.0 标准 |
| GroupedOpenApi | `Docket` 类 | `GroupedOpenApi` 类 |
| 包路径 | springfox.* | org.springdoc.* |
| API 文档路径 | /v2/api-docs | /v3/api-docs |

### 3.2 踩坑记录

**坑1：`@Schema` 没有 `value()` 属性**
```java
// ❌ 错误
@Schema("用户ID")

// ✅ 正确
@Schema(description = "用户ID")
```

**坑2：`@Tag` 用 `name` 不是 `tags`**
```java
// ❌ 错误
@Api(tags = "用户管理")

// ✅ 正确
@Tag(name = "用户管理")
```

**坑3：GroupedOpenApi bean 名称冲突**
- springdoc 自动配置会创建默认的 `GroupedOpenApi`
- 自定义配置不要用相同的 group 名

**坑4：springdoc 版本与 Spring Boot 兼容性**
- Spring Boot 2.x → springdoc 1.x（如 1.6.15）
- Spring Boot 3.x → springdoc 2.x

### 3.3 删除的文件

迁移到 springdoc 后，以下 springfox 专用文件不再需要：
- `BaseSwaggerResponseBuilderPlugin.java`
- `BaseSwaggerResponseModelPlugin.java`
- `SwaggerUtils.java`
