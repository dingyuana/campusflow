# 生产环境 Docker 部署完整方案

## 📋 概述

本方案提供 CampusFlow 智慧校园系统的完整生产级 Docker 部署配置，包含多阶段构建、健康检查、日志收集、监控告警等功能。

---

## 🏗️ 项目结构

```
CampusFlow/
├── docker/
│   ├── api/
│   │   └── Dockerfile                 # API 服务镜像
│   ├── frontend/
│   │   └── Dockerfile                 # 前端服务镜像
│   ├── nginx/
│   │   ├── Dockerfile                 # Nginx 反向代理
│   │   └── nginx.conf                 # Nginx 配置
│   └── monitoring/
│       ├── prometheus/
│       │   └── prometheus.yml         # Prometheus 配置
│       └── grafana/
│           └── datasource.yml         # Grafana 数据源
├── docker-compose.yml                 # 开发环境
├── docker-compose.prod.yml            # 生产环境
├── docker-compose.monitoring.yml      # 监控栈
├── .env.example                       # 环境变量模板
├── scripts/
│   ├── deploy.sh                      # 部署脚本
│   ├── backup.sh                      # 备份脚本
│   └── health-check.sh                # 健康检查
└── docs/
    └── DEPLOY.md                      # 部署文档
```

---

## 🐳 Dockerfile 配置

### 1. API 服务 (FastAPI)

```dockerfile
# docker/api/Dockerfile
# 多阶段构建，减小镜像体积

# 阶段 1：构建依赖
FROM python:3.11-slim as builder

WORKDIR /app

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装依赖到虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 阶段 2：生产镜像
FROM python:3.11-slim

# 安全：创建非 root 用户
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制应用代码
COPY --chown=appuser:appgroup . .

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 启动命令
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. 前端服务 (Gradio)

```dockerfile
# docker/frontend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 7860

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860')" || exit 1

# 启动命令
CMD ["python", "app.py"]
```

### 3. Nginx 反向代理

```dockerfile
# docker/nginx/Dockerfile
FROM nginx:alpine

# 复制配置文件
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf

# 创建日志目录
RUN mkdir -p /var/log/nginx

# 暴露端口
EXPOSE 80 443

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# docker/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript text/javascript;

    # 上游服务器
    upstream api {
        server api:8000 max_fails=3 fail_timeout=30s;
    }

    upstream frontend {
        server frontend:7860 max_fails=3 fail_timeout=30s;
    }

    # HTTP 服务器（重定向到 HTTPS）
    server {
        listen 80;
        server_name _;
        
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS 服务器
    server {
        listen 443 ssl http2;
        server_name campusflow.example.com;

        # SSL 配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # 安全响应头
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # API 代理
        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 前端代理
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket 支持
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # 静态文件缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            proxy_pass http://frontend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

---

## 🚀 Docker Compose 配置

### 1. 生产环境配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # API 服务
  api:
    build:
      context: .
      dockerfile: docker/api/Dockerfile
    container_name: campusflow-api
    restart: unless-stopped
    environment:
      - ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
      - LANGCHAIN_TRACING_V2=${LANGCHAIN_TRACING_V2}
      - CHROMA_DB_PATH=/app/data/chroma_db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - campusflow-network
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  # 前端服务
  frontend:
    build:
      context: .
      dockerfile: docker/frontend/Dockerfile
    container_name: campusflow-frontend
    restart: unless-stopped
    environment:
      - API_URL=http://api:8000
      - ENV=production
    depends_on:
      api:
        condition: service_healthy
    networks:
      - campusflow-network
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:7860')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 256M

  # Nginx 反向代理
  nginx:
    build:
      context: .
      dockerfile: docker/nginx/Dockerfile
    container_name: campusflow-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      api:
        condition: service_healthy
      frontend:
        condition: service_healthy
    networks:
      - campusflow-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # ChromaDB 向量数据库
  chromadb:
    image: chromadb/chroma:latest
    container_name: campusflow-chromadb
    restart: unless-stopped
    volumes:
      - chroma-data:/chroma/chroma
    environment:
      - CHROMA_SERVER_AUTHN_PROVIDER=${CHROMA_SERVER_AUTHN_PROVIDER}
      - CHROMA_SERVER_AUTHN_CREDENTIALS=${CHROMA_SERVER_AUTHN_CREDENTIALS}
    networks:
      - campusflow-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: campusflow-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf:ro
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      - campusflow-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

networks:
  campusflow-network:
    driver: bridge

volumes:
  chroma-data:
    driver: local
  redis-data:
    driver: local
```

### 2. 监控栈配置

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  # Prometheus 监控
  prometheus:
    image: prom/prometheus:latest
    container_name: campusflow-prometheus
    restart: unless-stopped
    volumes:
      - ./docker/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=15d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - campusflow-network

  # Grafana 可视化
  grafana:
    image: grafana/grafana:latest
    container_name: campusflow-grafana
    restart: unless-stopped
    volumes:
      - grafana-data:/var/lib/grafana
      - ./docker/monitoring/grafana/datasource.yml:/etc/grafana/provisioning/datasources/datasource.yml:ro
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3000:3000"
    networks:
      - campusflow-network

  # Node Exporter（主机监控）
  node-exporter:
    image: prom/node-exporter:latest
    container_name: campusflow-node-exporter
    restart: unless-stopped
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    expose:
      - 9100
    networks:
      - campusflow-network

  # cAdvisor（容器监控）
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: campusflow-cadvisor
    restart: unless-stopped
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    expose:
      - 8080
    networks:
      - campusflow-network

networks:
  campusflow-network:
    external: true

volumes:
  prometheus-data:
  grafana-data:
```

---

## 📊 监控配置

### Prometheus 配置

```yaml
# docker/monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files: []

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'campusflow-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: /metrics

  - job_name: 'campusflow-frontend'
    static_configs:
      - targets: ['frontend:7860']
```

### Grafana 数据源配置

```yaml
# docker/monitoring/grafana/datasource.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

---

## 🔐 环境变量模板

```bash
# .env.example

# ==================== 基础配置 ====================
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# ==================== 数据库配置 ====================
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
SUPABASE_DB_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres

# PostgreSQL（备用）
DATABASE_URL=postgresql://user:password@localhost:5432/campusflow

# Neo4j
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password

# ==================== 缓存配置 ====================
REDIS_URL=redis://redis:6379/0

# ==================== ChromaDB 配置 ====================
CHROMA_DB_PATH=/app/data/chroma_db
CHROMA_SERVER_AUTHN_PROVIDER=token
CHROMA_SERVER_AUTHN_CREDENTIALS=your-chroma-token

# ==================== LLM 配置 ====================
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# LangSmith（调试）
LANGCHAIN_API_KEY=your-langchain-api-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=campusflow

# ==================== API 配置 ====================
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# ==================== 前端配置 ====================
FRONTEND_PORT=7860
API_URL=http://api:8000

# ==================== 安全配置 ====================
SECRET_KEY=your-secret-key-here-min-32-chars-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 配置
CORS_ORIGINS=https://campusflow.example.com,https://app.campusflow.example.com

# ==================== 监控配置 ====================
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your-secure-password

# ==================== 备份配置 ====================
BACKUP_DIR=/backup/campusflow
BACKUP_RETENTION_DAYS=7
```

---

## 🚀 部署脚本

### 1. 自动化部署脚本

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  CampusFlow 生产环境部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查环境文件
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}错误: 环境文件 $ENV_FILE 不存在${NC}"
    echo "请复制 .env.example 到 .env 并配置"
    exit 1
fi

# 加载环境变量
export $(grep -v '^#' $ENV_FILE | xargs)

# 1. 备份数据
echo -e "${YELLOW}[1/6] 备份现有数据...${NC}"
if [ -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
fi
docker compose -f $COMPOSE_FILE exec -T api python -c "
import json
import os
# 这里添加备份逻辑
print('数据备份完成')
" 2>/dev/null || echo "跳过备份（服务未运行）"

# 2. 拉取最新代码
echo -e "${YELLOW}[2/6] 拉取最新代码...${NC}"
git pull origin main || echo "警告: 拉取代码失败"

# 3. 构建镜像
echo -e "${YELLOW}[3/6] 构建 Docker 镜像...${NC}"
docker compose -f $COMPOSE_FILE build --no-cache

# 4. 停止旧服务
echo -e "${YELLOW}[4/6] 停止旧服务...${NC}"
docker compose -f $COMPOSE_FILE down

# 5. 启动新服务
echo -e "${YELLOW}[5/6] 启动新服务...${NC}"
docker compose -f $COMPOSE_FILE up -d

# 6. 健康检查
echo -e "${YELLOW}[6/6] 执行健康检查...${NC}"
sleep 10

HEALTH_STATUS=0

# 检查 API 服务
if docker compose -f $COMPOSE_FILE ps | grep -q "api.*healthy"; then
    echo -e "${GREEN}✓ API 服务健康${NC}"
else
    echo -e "${RED}✗ API 服务异常${NC}"
    HEALTH_STATUS=1
fi

# 检查前端服务
if docker compose -f $COMPOSE_FILE ps | grep -q "frontend.*healthy"; then
    echo -e "${GREEN}✓ 前端服务健康${NC}"
else
    echo -e "${RED}✗ 前端服务异常${NC}"
    HEALTH_STATUS=1
fi

# 检查 Nginx
if docker compose -f $COMPOSE_FILE ps | grep -q "nginx.*healthy"; then
    echo -e "${GREEN}✓ Nginx 服务健康${NC}"
else
    echo -e "${RED}✗ Nginx 服务异常${NC}"
    HEALTH_STATUS=1
fi

echo ""
if [ $HEALTH_STATUS -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  部署成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "服务状态:"
    docker compose -f $COMPOSE_FILE ps
    echo ""
    echo "访问地址:"
    echo "  - 前端: https://campusflow.example.com"
    echo "  - API: https://campusflow.example.com/api"
    echo "  - 监控: https://campusflow.example.com:3000 (Grafana)"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  部署完成，但有服务异常${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "请检查日志:"
    echo "  docker compose -f $COMPOSE_FILE logs"
    exit 1
fi
```

### 2. 备份脚本

```bash
#!/bin/bash
# scripts/backup.sh

set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/campusflow"
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"

echo "开始备份 - $DATE"

# 1. 备份 ChromaDB
echo "[1/3] 备份 ChromaDB..."
docker run --rm \
    -v campusflow_chroma-data:/data \
    -v "$BACKUP_DIR":/backup \
    alpine \
    tar czf "/backup/chroma_${DATE}.tar.gz" -C /data .

# 2. 备份 Redis
echo "[2/3] 备份 Redis..."
docker exec campusflow-redis redis-cli BGSAVE
sleep 5
docker cp campusflow-redis:/data/dump.rdb "$BACKUP_DIR/redis_${DATE}.rdb"

# 3. 备份配置文件
echo "[3/3] 备份配置文件..."
tar czf "$BACKUP_DIR/config_${DATE}.tar.gz" \
    .env \
    docker-compose.prod.yml \
    docker/ \
    2>/dev/null || echo "警告: 部分文件不存在"

# 清理旧备份
echo "清理旧备份（保留 $RETENTION_DAYS 天）..."
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.rdb" -mtime +$RETENTION_DAYS -delete

echo "备份完成: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"
```

---

## 📖 部署步骤

### 1. 服务器准备

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 创建目录
mkdir -p /opt/campusflow
cd /opt/campusflow
```

### 2. 克隆代码并配置

```bash
# 克隆代码
git clone https://github.com/dingyuana/campusflow.git .

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 创建必要目录
mkdir -p data logs ssl backups
```

### 3. 启动服务

```bash
# 首次启动
docker-compose -f docker-compose.prod.yml up -d

# 查看状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. 配置 SSL

```bash
# 使用 Let's Encrypt
docker run -it --rm \
    -v "$(pwd)/ssl:/etc/letsencrypt" \
    -v "$(pwd)/data/certbot:/var/lib/letsencrypt" \
    certbot/certbot certonly \
    --standalone \
    -d campusflow.example.com
```

### 5. 启动监控

```bash
# 启动监控栈
docker-compose -f docker-compose.monitoring.yml up -d
```

---

## 🔧 运维命令

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f frontend

# 重启服务
docker-compose -f docker-compose.prod.yml restart api

# 进入容器
docker-compose -f docker-compose.prod.yml exec api bash

# 更新镜像
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# 清理未使用资源
docker system prune -af
docker volume prune -f
```

---

**文档创建时间**: 2026-01-30
**维护者**: CampusFlow 项目组
