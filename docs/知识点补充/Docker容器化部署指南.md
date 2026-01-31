# Docker 容器化部署指南

## 📋 概述

Docker 是一个开源的容器化平台，可以将应用程序及其依赖打包成标准化的容器镜像，实现"一次构建，到处运行"。在 CampusFlow 项目中，Docker 用于简化部署流程、保证环境一致性和实现微服务架构。

### 为什么选择 Docker？

| 特性 | 说明 |
|------|------|
| **环境一致性** | 开发、测试、生产环境完全一致 |
| **快速部署** | 秒级启动容器，分钟级部署应用 |
| **资源隔离** | 每个容器独立运行，互不干扰 |
| **易于扩展** | 快速复制容器实例，实现水平扩展 |
| **版本控制** | 镜像版本管理，支持回滚 |
| **生态丰富** | Docker Hub 上有数百万预构建镜像 |

---

## 🚀 快速开始

### 1. 安装 Docker

#### Linux（Ubuntu/Debian）

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install ca-certificates curl gnupg lsb-release

# 添加 Docker GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加 Docker 软件源
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 验证安装
sudo docker --version
sudo docker compose version

# 免 sudo 使用（可选）
sudo usermod -aG docker $USER
newgrp docker
```

#### macOS

```bash
# 使用 Homebrew 安装
brew install --cask docker

# 或使用官方安装包
# https://docs.docker.com/desktop/install/mac-install/
```

#### Windows

```powershell
# 下载 Docker Desktop
# https://docs.docker.com/desktop/install/windows-install/

# 或使用 Chocolatey
choco install docker-desktop
```

### 2. 第一个 Docker 容器

```bash
# 运行 Hello World
docker run hello-world

# 运行 Nginx 服务器
docker run -d -p 8080:80 --name my-nginx nginx

# 访问测试
curl http://localhost:8080

# 停止并删除容器
docker stop my-nginx
docker rm my-nginx
```

---

## 📦 核心概念

### 1. 镜像（Image）

```dockerfile
# Dockerfile - 构建镜像的脚本
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**构建镜像：**

```bash
# 构建镜像
docker build -t campusflow-api:latest .

# 查看镜像列表
docker images

# 删除镜像
docker rmi campusflow-api:latest

# 给镜像打标签
docker tag campusflow-api:latest registry.example.com/campusflow-api:v1.0.0
```

### 2. 容器（Container）

```bash
# 运行容器
docker run -d \
  --name campusflow-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e DATABASE_URL=postgresql://user:pass@db:5432/campusflow \
  --network campusflow-network \
  campusflow-api:latest

# 常用参数说明
# -d: 后台运行
# --name: 容器名称
# -p: 端口映射（主机端口:容器端口）
# -v: 挂载卷（主机路径:容器路径）
# -e: 环境变量
# --network: 指定网络
```

**容器管理：**

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 停止容器
docker stop campusflow-api

# 启动容器
docker start campusflow-api

# 重启容器
docker restart campusflow-api

# 删除容器
docker rm campusflow-api

# 强制删除（运行中的）
docker rm -f campusflow-api

# 进入容器内部
docker exec -it campusflow-api /bin/bash

# 查看容器日志
docker logs -f campusflow-api

# 查看容器资源使用
docker stats campusflow-api
```

### 3. 网络（Network）

```bash
# 创建网络
docker network create campusflow-network

# 查看网络列表
docker network ls

# 查看网络详情
docker network inspect campusflow-network

# 连接容器到网络
docker network connect campusflow-network campusflow-api

# 断开容器网络
docker network disconnect campusflow-network campusflow-api

# 删除网络
docker network rm campusflow-network
```

### 4. 数据卷（Volume）

```bash
# 创建卷
docker volume create campusflow-data

# 查看卷列表
docker volume ls

# 查看卷详情
docker volume inspect campusflow-data

# 使用卷运行容器
docker run -d \
  --name campusflow-api \
  -v campusflow-data:/app/data \
  campusflow-api:latest

# 删除卷
docker volume rm campusflow-data

# 清理未使用的卷
docker volume prune
```

---

## 🎯 Docker Compose 编排

### 1. 基础配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # FastAPI 后端服务
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: campusflow-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/campusflow
      - REDIS_URL=redis://redis:6379/0
      - NEO4J_URL=bolt://neo4j:7687
    volumes:
      - ./api:/app
      - /app/__pycache__
    depends_on:
      - db
      - redis
      - neo4j
    networks:
      - campusflow-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Gradio 前端服务
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: campusflow-frontend
    ports:
      - "7860:7860"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
    networks:
      - campusflow-network
    restart: unless-stopped

  # PostgreSQL 数据库
  db:
    image: postgres:15-alpine
    container_name: campusflow-db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=campusflow
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - campusflow-network
    restart: unless-stopped

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: campusflow-redis
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    networks:
      - campusflow-network
    restart: unless-stopped

  # Neo4j 图数据库
  neo4j:
    image: neo4j:5-community
    container_name: campusflow-neo4j
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j-data:/data
      - neo4j-logs:/logs
    ports:
      - "7474:7474"
      - "7687:7687"
    networks:
      - campusflow-network
    restart: unless-stopped

  # ChromaDB 向量数据库
  chromadb:
    image: chromadb/chroma:latest
    container_name: campusflow-chromadb
    volumes:
      - chroma-data:/chroma/chroma
    ports:
      - "8001:8000"
    networks:
      - campusflow-network
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:
  neo4j-data:
  neo4j-logs:
  chroma-data:

networks:
  campusflow-network:
    driver: bridge
```

### 2. Docker Compose 命令

```bash
# 启动所有服务
docker compose up -d

# 构建并启动
docker compose up -d --build

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f api

# 停止服务
docker compose stop

# 停止并删除容器
docker compose down

# 停止并删除容器和数据卷（慎用！）
docker compose down -v

# 重启服务
docker compose restart

# 扩展服务实例数
docker compose up -d --scale api=3

# 执行命令
docker compose exec api python manage.py migrate

# 进入容器
docker compose exec api bash
```

---

## 🐳 CampusFlow Docker 实战

### 1. API 服务 Dockerfile

```dockerfile
# api/Dockerfile
FROM python:3.11-slim as builder

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 生产镜像
FROM python:3.11-slim

# 复制依赖
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. 前端服务 Dockerfile

```dockerfile
# frontend/Dockerfile
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装依赖
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 7860

# 启动命令
CMD ["python", "app.py"]
```

### 3. 生产环境配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: registry.example.com/campusflow-api:${VERSION:-latest}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    networks:
      - traefik-public
      - internal
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.campusflow-api.rule=Host(`api.campusflow.com`)"
      - "traefik.http.routers.campusflow-api.tls.certresolver=letsencrypt"

  frontend:
    image: registry.example.com/campusflow-frontend:${VERSION:-latest}
    deploy:
      replicas: 2
    environment:
      - API_URL=https://api.campusflow.com
    networks:
      - traefik-public
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.campusflow-frontend.rule=Host(`campusflow.com`)"
      - "traefik.http.routers.campusflow-frontend.tls.certresolver=letsencrypt"

networks:
  traefik-public:
    external: true
  internal:
    external: false
```

### 4. 环境变量管理

```bash
# .env 文件示例
# 数据库配置
DATABASE_URL=postgresql://postgres:password@db:5432/campusflow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=campusflow

# Redis 配置
REDIS_URL=redis://redis:6379/0

# Neo4j 配置
NEO4J_AUTH=neo4j/password
NEO4J_URI=bolt://neo4j:7687

# API 配置
SECRET_KEY=your-secret-key-here
API_PORT=8000
DEBUG=false

# 前端配置
FRONTEND_PORT=7860
API_URL=http://api:8000
```

### 5. 部署脚本

```bash
#!/bin/bash
# deploy.sh - 部署脚本

set -e

# 变量
VERSION=${1:-latest}
REGISTRY="registry.example.com"
STACK_NAME="campusflow"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}开始部署 CampusFlow ${VERSION}...${NC}"

# 拉取最新镜像
echo "拉取镜像..."
docker pull ${REGISTRY}/campusflow-api:${VERSION}
docker pull ${REGISTRY}/campusflow-frontend:${VERSION}

# 部署服务
echo "部署服务..."
export VERSION=${VERSION}
docker stack deploy -c docker-compose.prod.yml ${STACK_NAME}

# 验证部署
echo "验证部署..."
sleep 10

if docker service ls | grep -q "${STACK_NAME}_api"; then
    echo -e "${GREEN}部署成功！${NC}"
    docker service ls | grep ${STACK_NAME}
else
    echo -e "${RED}部署失败，请检查日志${NC}"
    exit 1
fi

# 清理旧镜像
echo "清理旧镜像..."
docker image prune -af --filter "until=168h"

echo -e "${GREEN}部署完成！${NC}"
```

---

## 🔧 运维管理

### 1. 日志收集

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  # 使用 Fluentd 收集日志
  fluentd:
    image: fluent/fluentd:v1.16
    volumes:
      - ./fluentd/conf:/fluentd/etc
    ports:
      - "24224:24224"
    networks:
      - campusflow-network

  api:
    logging:
      driver: fluentd
      options:
        fluentd-address: localhost:24224
        tag: docker.campusflow.api
```

### 2. 监控告警

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  # Prometheus 监控
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - campusflow-network

  # Grafana 可视化
  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - campusflow-network

  # cAdvisor 容器监控
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"
    networks:
      - campusflow-network

volumes:
  prometheus-data:
  grafana-data:

networks:
  campusflow-network:
    external: true
```

### 3. 备份策略

```bash
#!/bin/bash
# backup.sh - 备份脚本

BACKUP_DIR="/backup/campusflow"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 备份 PostgreSQL
echo "备份 PostgreSQL..."
docker exec campusflow-db pg_dump -U postgres campusflow > ${BACKUP_DIR}/db_${DATE}.sql

# 备份 Redis
echo "备份 Redis..."
docker exec campusflow-redis redis-cli BGSAVE
sleep 5
docker cp campusflow-redis:/data/dump.rdb ${BACKUP_DIR}/redis_${DATE}.rdb

# 备份 Neo4j
echo "备份 Neo4j..."
docker exec campusflow-neo4j neo4j-admin database dump --to-path=/tmp neo4j
docker cp campusflow-neo4j:/tmp/neo4j.dump ${BACKUP_DIR}/neo4j_${DATE}.dump

# 备份向量数据库
echo "备份 ChromaDB..."
docker run --rm -v campusflow_chroma-data:/data -v ${BACKUP_DIR}:/backup alpine \
    tar czf /backup/chroma_${DATE}.tar.gz -C /data .

# 压缩并清理旧备份
tar czf ${BACKUP_DIR}/full_backup_${DATE}.tar.gz ${BACKUP_DIR}/*_${DATE}*
rm ${BACKUP_DIR}/*_${DATE}.*

# 保留最近 7 天的备份
find ${BACKUP_DIR} -name "full_backup_*.tar.gz" -mtime +7 -delete

echo "备份完成: ${BACKUP_DIR}/full_backup_${DATE}.tar.gz"
```

---

## 📚 学习资源

### 官方文档
- Docker 官方文档：https://docs.docker.com/
- Docker Compose 文档：https://docs.docker.com/compose/
- Dockerfile 参考：https://docs.docker.com/engine/reference/builder/

### 推荐阅读
- 《Docker 实战》
- 《Docker 容器化技术详解》
- 《Kubernetes 权威指南》（进阶）

### 实践项目
1. **单机部署**：使用 Docker Compose 部署完整应用栈
2. **多机部署**：使用 Docker Swarm 或 Kubernetes
3. **CI/CD 集成**：GitHub Actions + Docker 自动构建部署

---

**文档创建时间**：2026-01-30
**文档维护者**：CampusFlow 项目组
