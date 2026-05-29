---
title: Nacos服务注册IP配置导致Gateway路由404
tags: [Nacos, Gateway, 微服务, 踩坑]
created: 2026-05-28
updated: 2026-05-28
status: 100%
related: [[OpenCode配置Obsidian MCP]]
---

# Nacos 服务注册 IP 配置导致 Gateway 路由 404

## 1. 业务场景与核心诉求

前端通过 Gateway 调用 learning-service 接口时：
- **有时能用，有时 404**（不稳定）
- **Apifox 直接调用始终正常**
- 重启后可能短暂恢复

## 2. 最终落地方案 & 核心代码

### 2.1 问题配置（错误）

```yaml
# bootstrap-local.yml
spring:
  cloud:
    nacos:
      discovery:
        ip: 192.168.150.1  # ❌ 这是网关IP，不是本机IP
```

### 2.2 修复方案

```yaml
# bootstrap-local.yml
spring:
  cloud:
    nacos:
      discovery:
        # 删除 ip 配置，让 Nacos 自动检测本机IP
        namespace: xxx
        group: DEFAULT_GROUP
```

### 2.3 关键点

| 配置 | 说明 |
|------|------|
| `ip: 192.168.150.1` | ❌ 注册网关IP，Gateway无法路由 |
| `ip: 192.168.150.101` | ❌ 注册Nacos服务器IP，也不对 |
| 不配置 `ip` | ✅ Nacos自动检测本机IP |

## 3. 原理剖析与踩坑记录

### 3.1 完整链路分析

```
正常流程：
前端 → Gateway(10010) → Nacos查询实例 → 转发到本机IP:8090 ✅

异常流程：
前端 → Gateway(10010) → Nacos查询实例 → 转发到192.168.150.1:8090 ❌
                                            (网关IP，不是本机)
```

### 3.2 为什么时好时坏？

```
Nacos 中注册了多个实例：
├── 实例1: 192.168.150.1:8090  (错误 - 网关IP)
├── 实例2: 192.168.150.101:8090 (错误 - Nacos服务器IP)
└── 实例3: 192.168.1.100:8090  (正确 - 本机IP)

Gateway 负载均衡随机选择：
- 选到实例3 → 正常 ✅
- 选到实例1/2 → 404 ❌
```

### 3.3 为什么 Apifox 能用？

```
Apifox 直接调用：http://localhost:8090/lessons/page
                  ↓
            绕过 Gateway，直接访问本机
                  ↓
              始终正常 ✅
```

### 3.4 踩坑记录

**坑1：`ip` 配置误解**
- 以为 `ip` 是 Nacos 服务器地址
- 实际是**服务注册到 Nacos 的本机IP**

**坑2：虚拟机环境 IP 混乱**
- 虚拟机有多个网络接口
- Nacos 自动检测可能检测到错误的网卡
- 解决：明确配置正确的本机IP，或删除让系统自动检测

**坑3：旧实例残留**
- 重启服务后，旧的错误实例仍在 Nacos 中
- 解决：重启前清理 Nacos 中的旧实例

### 3.5 最佳实践

```yaml
# 开发环境：删除 ip 配置
spring:
  cloud:
    nacos:
      discovery:
        # 不配置 ip，让 Nacos 自动检测
        
# 生产环境：明确配置本机IP
spring:
  cloud:
    nacos:
      discovery:
        ip: 10.0.1.100  # 明确配置，避免自动检测错误
```

### 3.6 排查命令

```bash
# 1. 检查 Nacos 中注册的实例
curl "http://192.168.150.101:8848/nacos/v1/ns/instance/list?serviceName=learning-service"

# 2. 检查本机IP
ipconfig  # Windows
ifconfig  # Linux/Mac

# 3. 测试直连
curl http://localhost:8090/lessons/page

# 4. 测试 Gateway 路由
curl http://localhost:10010/ls/lessons/page
```
