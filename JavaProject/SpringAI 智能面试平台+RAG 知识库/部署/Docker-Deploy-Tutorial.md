# InterviewGuide Docker 部署全流程教程

> 适用场景：本地开发 / 云服务器部署 / 服务器迁移
> 目标读者：有 Docker 基础但希望掌握完整部署流程的开发者

---

## 前置知识：Docker Compose 架构总览

### 服务拓扑图

```
┌─────────────────────────────────────────────────────────┐
│                     用户浏览器                          │
│          localhost (前端) / localhost:8080 (后端)        │
└──────────┬──────────────────────────┬──────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────┐  ┌──────────────────────┐
│   frontend (Nginx)   │  │    app (Spring Boot)  │
│       端口: 80       │  │      端口: 8080       │
│  React 静态文件托管   │  │   处理业务逻辑 + LLM  │
│  反向代理 /api/ 到后端│  │                       │
└──────────┬───────────┘  └──────────┬───────────┘
           │                         │
           │         ┌───────────────┴───────────────┐
           │         ▼                               ▼
           │  ┌────────────┐  ┌──────────┐  ┌────────────┐
           │  │ postgres   │  │  redis   │  │   minio    │
           │  │  端口:5432 │  │ 端口:6379│  │  端口:9000 │
           │  │ pgvector   │  │  Stream  │  │  S3 兼容   │
           │  │ 向量存储   │  │  消息队列 │  │  文件存储   │
           │  └────────────┘  └──────────┘  └────────────┘
           │                                    │
           │  ┌─────────────────────────────────┘
           │  ▼
           │  ┌──────────────┐
           └──►│ createbuckets │
               │  一次性任务   │
               │ 创建 MinIO Bucket │
               └──────────────┘
```

### 6 个服务的职责

| 服务名 | 镜像 | 端口 | 职责 | 持久化 |
|--------|------|------|------|--------|
| `postgres` | `pgvector/pgvector:pg16` | 5432 | 业务数据 + 向量数据存储 | ✅ postgres_data 卷 |
| `redis` | `redis:7` | 6379 | 会话缓存 + Stream 消息队列 | ✅ redis_data 卷 |
| `minio` | `minio/minio` | 9000/9001 | 简历/文档对象存储 | ✅ minio_data 卷 |
| `createbuckets` | `minio/mc` | — | 一次性初始化任务：自动创建 Bucket | 无（任务完成即退出） |
| `app` | 本地构建 | 8080 | Spring Boot 后端，Java 21 运行时 | 无（无状态） |
| `frontend` | 本地构建 | 80 | Nginx 托管 React 静态文件 | 无（无状态） |

---

## 准备工作

### 1.1 安装 Docker 环境

**Windows/macOS**：下载安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
docker --version
docker compose version
```

**Linux (Ubuntu)**：
```bash
sudo apt update
sudo apt install docker.io docker-compose-plugin
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

### 1.2 克隆项目代码

```bash
git clone https://github.com/Snailclimb/interview-guide.git
cd interview-guide
```

### 1.3 申请阿里云百炼 API Key

这是**唯一必须申请的外部依赖**。项目使用阿里云 DashScope 作为 LLM/ASR/TTS 的统一后端。

1. 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 开通「百炼 API」服务
3. 在「API-KEY 管理」中创建新的 API-KEY
4. 复制保存（**仅显示一次**）

支持的模型：
- `qwen-plus`（默认，推荐，平衡性价比）
- `qwen-max`（更高智能，价格更贵）
- `qwen-long`（长上下文版）

---

## 方式一：一键部署（推荐）

适合：快速体验 / 云服务器全新部署 / 生产环境

### Step 1：配置环境变量

```bash
cp .env.example .env
nano .env
```

`.env` 中**必须填写**的字段：

```env
# 必需配置
AI_BAILIAN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx  # ← 填入你的 API Key

# 可选配置（使用默认值即可）
AI_MODEL=qwen-plus
POSTGRES_PASSWORD=password
APP_STORAGE_ACCESS_KEY=minioadmin
APP_STORAGE_SECRET_KEY=minioadmin
```

> ⚠️ **安全提醒**：`.env` 包含密钥，**不要提交到 Git**。

### Step 2：一键启动

```bash
docker compose up -d --build
```

启动顺序：
1. 构建 `app` 镜像（Multi-stage：Gradle 编译 → JRE 运行）
2. 构建 `frontend` 镜像（Multi-stage：Node 构建 → Nginx 托管）
3. 启动 `postgres` → 等待健康检查通过
4. 启动 `redis` → 等待健康检查通过
5. 启动 `minio` → 等待健康检查通过
6. 启动 `createbuckets` → 自动创建 `interview-guide` Bucket
7. 启动 `app` → 等待所有依赖服务就绪
8. 启动 `frontend` → Nginx 托管静态文件

**启动耗时**：首次约 5-10 分钟，后续重启约 30 秒。

### Step 3：验证服务状态

```bash
# 查看所有容器状态
docker compose ps

# 实时查看后端日志
docker compose logs -f app
```

**成功标志**：`Started App in X seconds`

### Step 4：访问应用

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端首页 | http://localhost | 用户访问入口 |
| 后端 API | http://localhost:8080 | RESTful API 根路径 |
| Swagger 文档 | http://localhost:8080/swagger-ui.html | API 接口文档 |
| MinIO 控制台 | http://localhost:9001 | 管理上传的文件 |
| MinIO API | http://localhost:9000 | S3 兼容接口 |

默认账号：MinIO 控制台 `minioadmin` / `minioadmin`

---

## 方式二：仅启动依赖服务（本地开发）

适合：本地开发调试（后端用 `./gradlew bootRun` 启动，热重载）

### 与方式一的区别

```
方式一：6 个服务全部容器化（后端也在容器里）
方式二：仅启动 3 个基础设施（postgres/redis/minio）
       后端在宿主机本地运行（方便热重载调试）
```

### Step 1：启动基础设施

```bash
docker compose -f docker-compose.dev.yml up -d
```

### Step 2：修改后端配置

后端在宿主机运行，连接地址改为 `localhost`（不是容器内的服务名）：

```env
POSTGRES_HOST=localhost
REDIS_HOST=localhost
APP_STORAGE_ENDPOINT=http://localhost:9000
AI_BAILIAN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3：本地启动后端

```bash
./gradlew bootRun
# 访问 http://localhost:8080
```

### Step 4：本地启动前端

```bash
cd frontend
pnpm install
pnpm dev
# 访问 http://localhost:5173
```

---

## 日常运维命令

```bash
# 查看服务状态
docker compose ps

# 实时查看后端日志
docker compose logs -f app

# 重启单个服务
docker compose restart app

# 拉取新代码后重新部署（保留数据卷）
git pull
docker compose up -d --build

# 停止服务但保留数据
docker compose down

# 停止并删除数据（慎用！会清空数据库）
docker compose down -v

# 进入 PostgreSQL 容器
docker compose exec postgres psql -U postgres -d interview_guide

# 清理未使用镜像
docker image prune -f
```

---

## 生产环境部署注意事项

### 1. 修改默认密码

```env
POSTGRES_PASSWORD=<随机强密码>
APP_STORAGE_SECRET_KEY=<随机强密码>
```

### 2. 配置云厂商托管数据库

使用阿里云 RDS / AWS RDS 时，注释掉 `docker-compose.yml` 中的 `postgres` 服务：

```env
POSTGRES_HOST=<RDS内网地址>
POSTGRES_PORT=5432
POSTGRES_DB=interview_guide
POSTGRES_USER=<RDS账号>
POSTGRES_PASSWORD=<RDS密码>
```

> ⚠️ **注意**：云 RDS 需要手动执行 `CREATE EXTENSION vector;` 启用 pgvector。

### 3. 配置云对象存储（生产推荐）

```env
# 阿里云 OSS 示例
APP_STORAGE_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
APP_STORAGE_ACCESS_KEY=<AK>
APP_STORAGE_SECRET_KEY=<SK>
APP_STORAGE_BUCKET=interview-guide
APP_STORAGE_REGION=cn-hangzhou
```

### 4. Nginx 反向代理 + HTTPS

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:80;
    }

    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;  # AI 请求可能持续数十秒
    }

    location /ws/ {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

HTTPS 证书：`certbot --nginx -d your-domain.com`

### 5. 开机自启（systemd）

```ini
# /etc/systemd/system/interview-guide.service
[Unit]
Description=Interview Guide Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/interview-guide
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable interview-guide
sudo systemctl start interview-guide
```

---

## 常见问题排查

| 问题 | 排查命令 |
|------|---------|
| 前端无法访问 | `docker compose logs frontend` |
| 后端连接数据库失败 | `docker compose ps` 确认 postgres 健康，`docker compose exec app ping postgres` |
| 简历分析一直"分析中" | `docker compose logs app \| grep -i stream` 检查消费者 |
| 知识库检索无结果 | `docker compose exec postgres psql -U postgres -d interview_guide -c "SELECT * FROM pg_extension WHERE extname = 'vector';"` |
| AI 功能 401/403 | `docker compose exec app env \| grep AI_BAILIAN` 确认 Key 注入 |
| .env 修改不生效 | `docker compose down && docker compose up -d --build` |

---

## 架构设计知识点（面试可讲）

### Multi-stage Build（多阶段构建）

**后端**：`gradle:8.14-jdk21`（构建） → `eclipse-temurin:21-jre`（运行）
- 最终镜像只有 JRE，不包含 JDK/Gradle，体积从 ~800MB → ~200MB

**前端**：`node:20-alpine`（构建） → `nginx:alpine`（运行）
- 最终镜像只有 Nginx，不包含 Node.js，体积从 ~1GB → ~50MB

### Init Container Pattern（初始化容器）

`createbuckets` 服务使用 MinIO Client 自动创建 Bucket：
- 依赖 `minio` 健康检查通过（`condition: service_healthy`）
- 任务完成后 `exit 0`，容器自动退出
- 保证"基础设施就绪后再启动应用"

### 健康检查链（Health Check Chain）

```
postgres (pg_isready) → redis (redis-cli ping) → minio (curl health)
    ↓
createbuckets (service_completed_successfully)
    ↓
app (depends_on all above)
    ↓
frontend (depends_on app)
```

### Docker 卷持久化

```yaml
volumes:
  postgres_data:  # /var/lib/postgresql/data
  redis_data:    # /data
  minio_data:     # /data
```

- `docker compose down` **不删除**数据卷
- `docker compose down -v` **删除所有数据**，慎用