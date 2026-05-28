---
title: ThreadLocal跨微服务用户上下文传递
tags: [微服务, ThreadLocal, Feign, 用户上下文]
created: 2026-05-28
updated: 2026-05-28
status: 100%
related: [[Springfox迁移OpenAPI3]]
---

# ThreadLocal 跨微服务用户上下文传递

## 1. 业务场景与核心诉求

在微服务架构中，用户登录后需要在整个请求链路中传递 userId，用于：
- 数据权限过滤（只查自己的数据）
- 审计日志记录（谁操作的）
- 业务逻辑依赖（根据用户做决策）

**核心问题**：ThreadLocal 是单线程的，跨服务调用时如何传递？

## 2. 最终落地方案 & 核心代码

### 2.1 整体架构

```
用户请求 → Gateway（解析JWT，放入Header）→ Service A（ThreadLocal）→ Feign调用 → Service B（ThreadLocal）
```

### 2.2 UserContext（ThreadLocal 存储）

```java
// tj-common 模块 - 每个服务都依赖
public class UserContext {
    private static final ThreadLocal<Long> TL = new ThreadLocal<>();
    
    public static void setUser(Long userId) { TL.set(userId); }
    public static Long getUser() { return TL.get(); }
    public static void removeUser() { TL.remove(); }
}
```

### 2.3 UserInfoInterceptor（HTTP Header → ThreadLocal）

```java
public class UserInfoInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, ...) {
        // 从 Header 中提取 userId
        String userIdStr = request.getHeader("user-info");
        if (userIdStr != null) {
            Long userId = Long.valueOf(userIdStr);
            UserContext.setUser(userId);  // 存入当前线程
        }
        return true;
    }

    @Override
    public void afterCompletion(...) {
        UserContext.removeUser();  // 请求结束清理
    }
}
```

### 2.4 FeignRelayUserInterceptor（ThreadLocal → HTTP Header）

```java
public class FeignRelayUserInterceptor implements RequestInterceptor {
    @Override
    public void apply(RequestTemplate template) {
        Long userId = UserContext.getUser();  // 从当前线程读取
        if (userId != null) {
            template.header("user-info", userId.toString());
        }
    }
}
```

## 3. 原理剖析与踩坑记录

### 3.1 为什么能跨服务工作？

| 场景 | 机制 |
|------|------|
| 同一服务内 | ThreadLocal 直接共享 |
| 跨服务调用 | Feign 拦截器通过 HTTP Header 传递 |
| 每个服务 | 都有独立的 ThreadLocal（依赖 tj-common） |

### 3.2 完整链路

```
1. 用户请求 → Gateway
2. Gateway 解析 JWT，提取 userId=12345
3. Gateway 转发，Header 添加 user-info: 12345
4. Service A 收到请求
   └─ UserInfoInterceptor: Header → ThreadLocal
5. Service A 通过 Feign 调用 Service B
   └─ FeignRelayUserInterceptor: ThreadLocal → Header
6. Service B 收到请求
   └─ UserInfoInterceptor: Header → ThreadLocal
7. 请求结束
   └─ afterCompletion: removeUser()
```

### 3.3 踩坑记录

**坑1：异步场景丢失**
- `@Async`、线程池会创建新线程，ThreadLocal 丢失
- 解决：使用 `InheritableThreadLocal` 或手动传递

**坑2：Feign 调用未配置拦截器**
- 需要在配置类中注册 `FeignRelayUserInterceptor`

**坑3：请求结束未清理**
- 必须在 `afterCompletion` 中调用 `removeUser()`
- 否则线程复用时会读到脏数据
