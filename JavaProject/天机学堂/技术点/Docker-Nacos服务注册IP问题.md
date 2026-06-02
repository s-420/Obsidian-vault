---
title: Docker自定义网络下Nacos服务注册IP问题
tags: [Docker, Nacos, SpringCloud, 微服务, 网络]
created: 2026-06-02
updated: 2026-06-02
status: completed
related: [[Nacos服务发现]], [[Docker网络模式]]
---

# Docker自定义网络下Nacos服务注册IP问题

## 1. 业务场景与核心诉求

在微服务架构中，服务运行在Docker自定义网络中，注册到Nacos的IP是容器内部IP（如172.18.0.x），导致其他服务（尤其是本地开发环境）无法通过Nacos发现并调用该服务。

## 2. 最终落地方案 & 核心代码

### 2.1 配置Nacos注册指定宿主机IP

在`bootstrap-dev.yml`中添加`spring.cloud.nacos.discovery.ip`配置：

```yaml
spring:
  cloud:
    nacos:
      server-addr: 192.168.150.101:8848
      discovery:
        namespace: f923fb34-cb0a-4c06-8fca-ad61ea61a3f0
        group: DEFAULT_GROUP
        ip: 192.168.150.101  # 关键配置：指定注册IP
```

### 2.2 Jenkins构建流程说明

天机学堂的Jenkins构建流程：
```
git push → tjxt-dev-build (编译所有模块) → tj-course (复制JAR并部署Docker)
```

- `tjxt-dev-build`：负责编译代码，生成JAR包
- `tj-course`：从`tjxt-dev-build`工作空间复制JAR，构建Docker镜像并部署

## 3. 原理剖析与踩坑记录

### 3.1 原理

**Docker网络模式对服务注册的影响：**

| 网络模式 | 容器IP | 注册到Nacos的IP | 外部可访问性 |
|---------|--------|----------------|------------|
| `--network host` | 宿主机IP | 宿主机IP | ✅ 可访问 |
| 自定义网络(bridge) | 172.18.0.x | 172.18.0.x | ❌ 仅容器间可访问 |

当Docker使用自定义网络时，容器获得的IP是网桥分配的内部IP，这个IP只在Docker网络内部可达。服务注册到Nacos时默认使用容器检测到的IP，导致外部服务无法访问。

### 3.2 踩坑记录

**坑1：配置修改后不生效**

```yaml
# ❌ 错误理解：以为push代码就会生效
# 实际需要：tjxt-dev-build重新编译 → tj-course重新部署
```

**解决方案：**
1. 修改`bootstrap-dev.yml`后，需要`feature`分支合并到`dev`或cherry-pick到`dev`
2. 手动触发`tjxt-dev-build`构建
3. 再触发`tj-course`部署

**坑2：bootstrap.yml配置加载时机**

```yaml
# bootstrap.yml是启动时加载的，运行时修改不会生效
# 必须重启服务才能加载新配置
```

**坑3：Jenkins构建分支问题**

```yaml
# tjxt-dev-build默认构建dev分支
# feature分支的修改需要合并到dev才能被构建
# 临时方案：cherry-pick特定commit到dev

# 操作步骤：
git checkout dev
git cherry-pick <commit-hash>
git push

# 测试完成后revert：
git revert HEAD
git push
```

## 4. 排查命令速查

```bash
# 查看Docker容器网络模式
docker inspect <容器名> | grep -A 5 "NetworkMode"

# 查看容器环境变量
docker exec <容器名> env | grep -i spring

# 查看JAR包中的配置文件
docker exec <容器名> unzip -p /app/app.jar BOOT-INF/classes/bootstrap-dev.yml | grep ip

# 查看Nacos中的服务实例
curl -s "http://<nacos-ip>:8848/nacos/v1/ns/instance/list?serviceName=<服务名>&namespaceId=<namespace>"

# 查看容器启动时间
docker inspect <容器名> --format '{{.StartedAt}}'
```

## 5. 相关配置

- 配置文件位置：`bootstrap-dev.yml`
- 适用环境：Docker自定义网络 + Nacos服务发现
- 配置项：`spring.cloud.nacos.discovery.ip`
