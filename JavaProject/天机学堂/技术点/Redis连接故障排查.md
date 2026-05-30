---
title: Spring Boot Redis 连接故障排查
tags: [Redis, Redisson, Spring Boot, Docker, 连接失败]
created: 2026-05-30
updated: 2026-05-30
status: completed
related: [[Jenkins构建故障排查]], [Redisson配置]]
---

# Spring Boot Redis 连接故障排查

## 1. 业务场景与核心诉求

天机学堂 `tj-learning` 服务启动后报 Redis 连接错误，无法正常提供服务。

## 2. 最终落地方案 & 核心代码

### 2.1 错误信息

```
Caused by: org.springframework.beans.BeanInstantiationException: 
Failed to instantiate [org.redisson.api.RedissonClient]: 
Factory method 'redissonClient' threw exception; 
nested exception is org.redisson.client.RedisConnectionException: 
Unable to connect to Redis server: /192.168.150.101:6379
```

### 2.2 原因分析

1. Redis 部署方式：Docker 容器运行在 VM 上
2. VM IP：192.168.150.101
3. Redis 端口：6379（已映射到主机）
4. 问题：服务启动时 Redis 连接不稳定

### 2.3 解决方案

**重启 learning 服务即可解决**

```bash
# 重启服务
docker restart tj-learning
# 或
systemctl restart tj-learning
```

## 3. 原理剖析与踩坑记录

### 3.1 可能的根因

1. **服务启动顺序问题** - Redis 还未完全就绪时服务尝试连接
2. **网络波动** - VM 网络短暂不稳定
3. **连接池耗尽** - 之前的连接未正确释放

### 3.2 Redis 配置（Nacos shared-redis.yaml）

```yaml
spring:
  redis:
    host: ${tj.redis.host:192.168.150.101}
    password: ${tj.redis.password:123321}
    lettuce:
      pool:
        max-active: ${tj.redis.pool.max-active:8}
        max-idle: ${tj.redis.pool.max-idle:8}
        min-idle: ${tj.redis.pool.min-idle:1}
        max-wait: ${tj.redis.pool.max-wait:300}
```

### 3.3 Redisson 配置类

项目使用 `tj-common` 中的 `RedissonConfig` 自动配置：

```java
@Bean
@ConditionalOnMissingBean
public RedissonClient redissonClient(RedisProperties properties) {
    // 根据配置自动创建 RedissonClient
    // 支持单机、集群、哨兵模式
}
```

### 3.4 排查命令清单

```bash
# 检查 Redis 容器状态
docker ps | grep redis

# 检查容器 IP
docker inspect redis | grep IPAddress

# 测试 Redis 连接（需要 redis-cli）
docker exec redis redis-cli -h 127.0.0.1 -p 6379 -a 123321 ping

# 检查 VM IP
ip addr show | grep "inet " | grep -v 127.0.0.1

# 检查服务是否在 Docker 中运行
docker ps | grep learning
```

## 4. 预防措施

1. **添加健康检查** - 在 application.yml 中配置 Redis 健康检查
2. **增加重试机制** - 配置连接重试次数
3. **服务依赖管理** - 确保 Redis 在应用之前启动

```yaml
# 建议添加的配置
spring:
  redis:
    timeout: 5000ms
    lettuce:
      shutdown-timeout: 200ms
```

## 5. 相关配置路径

- Nacos 配置：`shared-redis.yaml`
- 配置类：`tj-common/.../redisson/RedissonConfig.java`
- 依赖模块：`tj-common`
