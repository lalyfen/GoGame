# GoGame 围棋项目部署指南

基于Nginx代理的前后端一体化Docker部署方案

## 📋 目录

- [项目概述](#项目概述)
- [架构设计](#架构设计)
- [部署要求](#部署要求)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [部署管理](#部署管理)
- [故障排除](#故障排除)
- [安全配置](#安全配置)

## 🎯 项目概述

GoGame是一个围棋项目，采用前后端分离架构：

- **前端**: Vue 3 + Vite + Pinia 多页面应用
- **后端**: Django + Django REST Framework + JWT认证
- **数据库**: PostgreSQL
- **缓存**: Redis
- **Web服务器**: Nginx (反向代理 + 静态文件服务)

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────┐
│                 用户浏览器                        │
└─────────────────────────┬───────────────────────┘
                          │ HTTP/HTTPS
                          ▼
┌─────────────────────────────────────────────────┐
│                  Nginx (80/443)                 │
│  ┌─────────────────┬─────────────────────────┐   │
│  │  静态文件服务     │     API反向代理          │   │
│  │ (Vue应用文件)     │   (/api/* → 后端)        │   │
│  └─────────────────┴─────────────────────────┘   │
└─────────────────────────┬───────────────────────┘
                          │ Docker内部网络
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Frontend   │  │   Backend   │  │  Database   │
│  (Nginx)    │  │  (Django)   │  │(PostgreSQL) │
│             │  │             │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │    Redis    │
                   │   (缓存)     │
                   └─────────────┘
```

## ⚙️ 部署要求

### 系统要求
- **操作系统**: Linux, macOS, Windows 10/11
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **内存**: 最少2GB RAM
- **磁盘**: 最少10GB可用空间

### 端口要求
- **80**: HTTP服务 (Nginx)
- **5432**: PostgreSQL (仅内部访问)
- **6379**: Redis (仅内部访问)
- **8000**: Django后端 (仅内部访问)

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <项目地址>
cd gogamev1.1
```

### 2. 一键启动 (推荐)
```bash
# Linux/macOS
./deploy.sh start

# Windows
deploy.bat start

# 或者直接使用docker-compose
docker-compose up -d
```

### 3. 访问应用
- **前端应用**: http://localhost
- **API接口**: http://localhost/api
- **后端管理**: http://localhost/admin

### 4. 验证部署
```bash
# 检查服务状态
./deploy.sh status

# 查看日志
./deploy.sh logs
```

## 📋 完整容器管理指令

### 🔧 一键脚本命令

```bash
# 部署管理
./deploy.sh start          # 启动所有服务
./deploy.sh stop           # 停止所有服务
./deploy.sh restart        # 重启所有服务
./deploy.sh logs           # 查看所有服务日志
./deploy.sh logs nginx     # 查看特定服务日志
./deploy.sh status         # 查看服务状态
./deploy.sh build          # 重新构建镜像
./deploy.sh build --force  # 强制重新构建
./deploy.sh clean          # 清理所有资源

# Windows用户使用deploy.bat
```

### 🛠️ Docker Compose命令

#### 运行容器（部署）
```bash
# 🌟 一键启动（推荐）
docker-compose up -d

# 构建并启动（如果镜像不存在）
docker-compose up -d --build

# 强制重新构建并启动
docker-compose up -d --build --no-cache

# 后台启动并查看日志
docker-compose up -d && docker-compose logs -f
```

#### 停止容器
```bash
# 🛑 停止所有服务
docker-compose down

# 停止并删除数据卷（注意：会丢失数据）
docker-compose down -v

# 停止并删除镜像
docker-compose down --rmi all

# 停止并删除所有相关资源
docker-compose down -v --rmi all --remove-orphans
```

#### 清空容器（完全清理）
```bash
# 🧹 完全清理（谨慎使用）
docker-compose down -v --rmi all
docker system prune -a -f
docker volume prune -f
docker network prune -f

# 极限清理（删除所有Docker资源）
docker system prune -a -f --volumes
```

#### 查看状态和日志
```bash
# 📊 查看所有服务状态
docker-compose ps

# 📜 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f nginx
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis

# 查看最近100行日志
docker-compose logs -f --tail=100

# 🏥 检查服务健康状态
docker-compose exec nginx curl -f http://localhost/health
docker-compose exec backend curl -f http://localhost:8000/api/health/
```

#### 更新和维护
```bash
# 🆕 更新应用
git pull
docker-compose up -d --build

# 滚动更新（零停机）
docker-compose up -d --no-deps backend

# 💾 备份数据库
docker-compose exec postgres pg_dump -U gogame_user gogame_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
docker-compose exec -T postgres psql -U gogame_user gogame_db < backup_file.sql
```

#### 调试和故障排除
```bash
# 🔍 进入容器调试
docker-compose exec backend bash
docker-compose exec postgres psql -U gogame_user -d gogame_db
docker-compose exec redis redis-cli
docker-compose exec nginx sh

# 🔄 重启单个服务
docker-compose restart nginx
docker-compose restart backend

# 重新创建特定服务
docker-compose up -d --no-deps nginx
```

### 📱 快速命令参考

```bash
# 🚀 快速启动
docker-compose up -d && sleep 10 && docker-compose ps

# 📊 查看状态
docker-compose ps && docker-compose logs --tail=10

# 🔄 快速重启
docker-compose restart

# 🛑 快速停止
docker-compose down

# 🧹 快速清理
docker-compose down && docker system prune -f
```

## 🔧 详细配置

### 环境变量配置

项目启动时会自动创建`.env`文件，包含以下配置：

```bash
# 项目名称
COMPOSE_PROJECT_NAME=gogame

# 数据库配置
POSTGRES_DB=gogame_db
POSTGRES_USER=gogame_user
POSTGRES_PASSWORD=gogame_password

# Redis配置
REDIS_PASSWORD=

# Django配置
SECRET_KEY=django-insecure-production-key-change-this
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# 超级用户配置
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123

# CORS配置（nginx代理模式）
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1

# Gunicorn配置
GUNICORN_WORKERS=1
GUNICORN_THREADS=4
LOG_LEVEL=info
```

### 生产环境配置

对于生产环境，请修改`.env`文件：

```bash
# 修改为安全的密钥
SECRET_KEY=your-very-secure-secret-key-here

# 关闭调试模式
DEBUG=False

# 设置允许的主机
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 设置强密码
POSTGRES_PASSWORD=secure-database-password
DJANGO_SUPERUSER_PASSWORD=secure-admin-password

# 配置CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 📦 部署管理

### 部署脚本使用

#### Linux/macOS (deploy.sh)
```bash
# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看日志
./deploy.sh logs

# 查看特定服务日志
./deploy.sh logs nginx
./deploy.sh logs backend

# 查看服务状态
./deploy.sh status

# 重新构建镜像
./deploy.sh build

# 强制重新构建
./deploy.sh build --force

# 清理所有资源
./deploy.sh clean
```

#### Windows (deploy.bat)
```batch
REM 启动服务
deploy.bat start

REM 停止服务
deploy.bat stop

REM 重启服务
deploy.bat restart

REM 查看日志
deploy.bat logs

REM 查看服务状态
deploy.bat status

REM 重新构建镜像
deploy.bat build

REM 清理所有资源
deploy.bat clean
```

### Docker Compose 命令

也可以直接使用Docker Compose命令：

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重新构建并启动
docker-compose up -d --build

# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres psql -U gogame_user -d gogame_db

# 备份数据库
docker-compose exec postgres pg_dump -U gogame_user gogame_db > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U gogame_user gogame_db < backup.sql
```

### 数据持久化

以下数据会自动持久化：

- **数据库数据**: `postgres_data` volume
- **Redis数据**: `redis_data` volume
- **静态文件**: `static_volume` volume
- **媒体文件**: `media_volume` volume

### 日志管理

日志文件位置：
- **Nginx日志**: 容器内 `/var/log/nginx/`
- **Django日志**: 容器内 `/app/logs/`
- **数据库日志**: PostgreSQL容器日志

查看实时日志：
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f nginx
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

## 🔍 故障排除

### 常见问题

#### 1. 端口80被占用
```bash
# Linux/macOS
sudo lsof -ti:80 | xargs sudo kill -9

# Windows
netstat -ano | findstr :80
taskkill /PID <进程ID> /F
```

#### 2. 容器启动失败
```bash
# 查看详细错误信息
docker-compose logs

# 重新构建镜像
docker-compose build --no-cache

# 清理并重启
docker-compose down -v
docker-compose up -d
```

#### 3. 数据库连接失败
```bash
# 检查数据库容器状态
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres

# 重启数据库服务
docker-compose restart postgres
```

#### 4. 前端无法访问API
```bash
# 检查nginx配置
docker-compose exec nginx nginx -t

# 重新加载nginx配置
docker-compose exec nginx nginx -s reload

# 查看nginx日志
docker-compose logs nginx
```

#### 5. 内存不足
```bash
# 监控资源使用情况
docker stats

# 清理未使用的资源
docker system prune -a
```

### 健康检查

所有服务都配置了健康检查：

```bash
# 检查服务健康状态
docker-compose ps

# 查看健康检查日志
docker inspect gogame_nginx | grep Health -A 10
docker inspect gogame_backend | grep Health -A 10
```

### 性能监控

```bash
# 查看资源使用情况
docker stats

# 查看容器详细信息
docker inspect gogame_backend
```

## 🔒 安全配置

### 生产环境安全建议

#### 1. 更改默认密码
```bash
# 修改数据库密码
POSTGRES_PASSWORD=your-secure-password

# 修改管理员密码
DJANGO_SUPERUSER_PASSWORD=your-secure-admin-password

# 修改Django密钥
SECRET_KEY=your-very-secure-secret-key
```

#### 2. 配置HTTPS
1. 获取SSL证书
2. 修改nginx配置启用HTTPS
3. 更新环境变量和CORS配置

#### 3. 网络安全
- 数据库和Redis仅内部访问
- 配置防火墙规则
- 使用强密码策略

#### 4. 定期备份
```bash
# 备份数据库
docker-compose exec postgres pg_dump -U gogame_user gogame_db > backup_$(date +%Y%m%d).sql

# 备份媒体文件
docker run --rm -v gogame_media_volume:/data -v $(pwd):/backup alpine tar czf /backup/media_$(date +%Y%m%d).tar.gz -C /data .
```

### 更新和维护

#### 更新应用
```bash
# 拉取最新代码
git pull

# 重新构建并部署
./deploy.sh build --force
./deploy.sh restart
```

#### 滚动更新
```bash
# 零停机更新
docker-compose up -d --no-deps backend
```

## 📚 附录

### 目录结构
```
gogamev1.1/
├── docker-compose.yml          # 主部署文件
├── deploy.sh                   # Linux/macOS部署脚本
├── deploy.bat                  # Windows部署脚本
├── .env                        # 环境变量配置
├── nginx/                      # Nginx配置
│   └── default.conf           # 站点配置
├── frontend前端/               # 前端代码
│   ├── Dockerfile              # 前端构建文件
│   ├── package.json            # 前端依赖
│   ├── .env.production         # 生产环境配置
│   └── dist/                   # 构建输出
└── backend后端/                # 后端代码
    ├── Dockerfile              # 后端构建文件
    ├── docker-entrypoint.sh    # 启动脚本
    ├── core/                   # Django核心配置
    └── ...                     # 其他Django应用
```

### 版本信息
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.11
- **Node.js**: 18-alpine
- **PostgreSQL**: 15-alpine
- **Redis**: 7-alpine
- **Nginx**: 1.25-alpine

### 支持和帮助

如遇到问题，请：
1. 查看本文档的故障排除部分
2. 检查服务日志：`./deploy.sh logs`
3. 查看服务状态：`./deploy.sh status`
4. 重启服务：`./deploy.sh restart`