# 🚀 GoGame后端生产环境部署指南

## 📋 部署概述

本文档提供GoGame后端生产环境的完整部署指南，包括Docker容器化部署、Gunicorn配置、环境变量管理和安全最佳实践。

## 🏗️ 系统架构

```
生产环境架构
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   负载均衡器    │    │   Nginx/Apache  │    │   反向代理      │
│  (可选/推荐)    │◄──►│   (SSL终止)     │◄──►│   (生产推荐)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Docker容器集群  │    │   GoGame后端   │    │   GoGame后端   │
│  (多实例部署)   │◄──►│   Django+Gunicorn│◄──►│   Django+Gunicorn│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   PostgreSQL    │    │   PostgreSQL    │
│   (主数据库)     │◄──►│   (主数据库)     │◄──►│   (主数据库)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Redis      │    │      Redis      │    │      Redis      │
│    (缓存层)      │◄──►│    (缓存层)      │◄──►│    (缓存层)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 快速部署

### 1. 环境准备

```bash
# 检查Docker版本
docker --version
docker-compose --version

# 确保端口未被占用
netstat -an | grep :8000
netstat -an | grep :5432
netstat -an | grep :6379
```

### 2. 一键部署

```bash
# 克隆项目（如需要）
git clone <repository-url>
cd backend后端

# 运行部署脚本
./deploy.sh
```

### 3. 验证部署

```bash
# 检查服务状态
docker-compose ps

# 检查健康状态
curl http://localhost:8000/api/health/

# 查看日志
docker-compose logs -f
```

## 📁 项目文件结构

```
backend后端/
├── Dockerfile                 # Docker镜像配置
├── docker-compose.yml         # 容器编排配置
├── docker-entrypoint.sh       # 容器启动脚本
├── gunicorn.conf.py           # Gunicorn配置文件
├── .env.example              # 环境变量模板
├── deploy.sh                 # 部署脚本
├── requirements.txt           # Python依赖
├── manage.py                 # Django管理脚本
├── core/                     # Django核心应用
│   ├── settings.py           # Django配置
│   ├── cache_manager.py      # 缓存管理
│   └── cache_signals.py      # 缓存信号
├── api/                      # API应用
│   ├── views.py              # API视图
│   ├── health_views.py       # 健康检查
│   └── urls.py               # URL配置
├── datab/                    # 数据处理应用
└── invitation/               # 邀请系统应用
```

## 🔧 核心配置文件

### 1. Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建非root用户
RUN groupadd -r django && useradd -r -g django django
RUN chown -R django:django /app
USER django

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]
```

### 2. docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: gogame_db
      POSTGRES_USER: gogame_user
      POSTGRES_PASSWORD: gogame_password
    ports: ["5432:5432"]
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru

  backend:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_HOST: postgres
      REDIS_HOST: redis
      DEBUG: "False"
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
```

### 3. Gunicorn配置

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 1
threads = 4
timeout = 30
keepalive = 2
max_requests = 1000
preload_app = True
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

## 🔐 环境变量配置

### 基础配置

```bash
# 数据库配置
DATABASE_NAME=gogame_db
DATABASE_USER=gogame_user
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=postgres
DATABASE_PORT=5432

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password

# Django配置
SECRET_KEY=your-50-character-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Gunicorn配置
GUNICORN_WORKERS=1
GUNICORN_THREADS=4
LOG_LEVEL=info
```

### 安全配置

```bash
# 强密码示例
DATABASE_PASSWORD=MySecureP@ssw0rd!2024
REDIS_PASSWORD=MyRedisP@ssw0rd!2024
SECRET_KEY=your-50-character-random-secret-key-here

# 生产环境设置
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## 🚀 部署流程详解

### 步骤1：环境准备

```bash
# 1. 克隆代码
git clone <repository-url>
cd backend后端

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置正确的密码和域名

# 3. 设置文件权限
chmod 600 .env
chmod +x deploy.sh
```

### 步骤2：运行部署

```bash
# 运行部署脚本
./deploy.sh

# 脚本会自动执行：
# - 检查环境配置
# - 构建Docker镜像
# - 启动所有服务
# - 等待健康检查
# - 验证服务状态
```

### 步骤3：验证部署

```bash
# 1. 检查容器状态
docker-compose ps

# 2. 检查健康状态
curl http://localhost:8000/api/health/

# 3. 测试API端点
curl http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123","email":"test@test.com"}'
```

## 📊 监控和日志

### 实时监控

```bash
# 查看容器状态
docker-compose ps

# 查看资源使用
docker stats

# 查看实时日志
docker-compose logs -f
```

### 日志管理

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看数据库日志
docker-compose logs -f postgres

# 查看Redis日志
docker-compose logs -f redis

# 保存日志到文件
docker-compose logs > deployment.log 2>&1
```

### 健康检查

```bash
# 基础健康检查
curl http://localhost:8000/api/health/

# 详细健康信息
curl http://localhost:8000/api/health/ | jq .

# 检查数据库连接
docker-compose exec postgres pg_isready -U gogame_user -d gogame_db

# 检查Redis连接
docker-compose exec redis redis-cli ping
```

## 🔧 运维操作

### 常用命令

```bash
# 重启服务
docker-compose restart

# 重启特定服务
docker-compose restart backend

# 重建服务
docker-compose up --build -d

# 停止服务
docker-compose down

# 更新服务
docker-compose pull
docker-compose up -d
```

### 数据库操作

```bash
# 进入数据库
docker-compose exec postgres psql -U gogame_user -d gogame_db

# 备份数据库
docker-compose exec postgres pg_dump -U gogame_user gogame_db > backup.sql

# 查看数据库连接数
docker-compose exec postgres psql -U gogame_user -d gogame_db -c "SELECT count(*) FROM pg_stat_activity;"
```

### 缓存操作

```bash
# 进入Redis
docker-compose exec redis redis-cli

# 查看缓存键
docker-compose exec redis redis-cli keys "*"

# 清空缓存
docker-compose exec redis redis-cli flushall

# 查看内存使用
docker-compose exec redis redis-cli info memory
```

## 🛡️ 安全最佳实践

### 1. 密钥管理

```bash
# 生成强密钥
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# 设置文件权限
chmod 600 .env
```

### 2. 网络安全

```bash
# 使用HTTPS（配置反向代理）
# 在Nginx/Apache中配置SSL证书
# 禁用Docker端口直接暴露到公网
```

### 3. 定期维护

```bash
# 更新Docker镜像
docker-compose pull
docker-compose up -d

# 清理未使用的镜像
docker image prune

# 监控磁盘空间
df -h
docker system df
```

## 📈 性能优化

### Gunicorn调优

```python
# 高负载环境配置
workers = 4  # CPU核心数 × 2 + 1
threads = 8  # 增加线程数
max_requests = 5000  # 增加请求数
preload_app = True  # 预加载应用
```

### 缓存优化

```python
# Redis配置优化
redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

### 数据库优化

```sql
-- 连接池配置
-- 在settings.py中设置
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'MAX_CONNS': 20,
        }
    }
}
```

## 🆘 故障排除

### 常见问题

**1. 容器启动失败**
```bash
# 查看日志
docker-compose logs backend

# 检查资源使用
docker stats

# 重新构建
docker-compose down
docker-compose up --build -d
```

**2. 数据库连接失败**
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U gogame_user -d gogame_db

# 查看数据库日志
docker-compose logs postgres

# 检查环境变量
docker-compose exec backend env | grep DATABASE
```

**3. Redis连接失败**
```bash
# 测试Redis连接
docker-compose exec redis redis-cli ping

# 查看Redis日志
docker-compose logs redis

# 重启Redis
docker-compose restart redis
```

**4. 健康检查失败**
```bash
# 检查后端日志
docker-compose logs backend

# 手动测试
docker-compose exec backend curl http://localhost:8000/api/health/

# 检查端口占用
netstat -an | grep :8000
```

## 📚 扩展部署

### 多实例部署

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  backend:
    build: .
    environment:
      - INSTANCE_ID=${INSTANCE_ID:-1}
    deploy:
      replicas: 3
```

### 负载均衡

```nginx
# nginx.conf示例
upstream backend {
    server backend:8000;
    server backend_2:8000;
    server backend_3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

**🎉 恭喜！您已经成功部署了GoGame后端生产环境！**

如需更多帮助，请查看相关文档或联系技术支持。