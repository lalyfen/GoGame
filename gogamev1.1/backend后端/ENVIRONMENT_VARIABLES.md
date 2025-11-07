# 环境变量配置详细说明

本文档详细说明了GoGame后端项目中的所有环境变量配置。

## 🔧 环境变量配置文件

### 主要配置文件

1. **`.env`** - 实际使用的环境变量文件（不提交到版本控制）
2. **`.env.example`** - 环境变量模板文件（可提交到版本控制）

### 配置文件结构

```bash
# 基础环境变量
DATABASE_NAME=...                    # 数据库名称
DATABASE_USER=...                    # 数据库用户名
DATABASE_PASSWORD=...                # 数据库密码
DATABASE_HOST=...                    # 数据库主机
DATABASE_PORT=...                    # 数据库端口

REDIS_HOST=...                       # Redis主机
REDIS_PORT=...                       # Redis端口
REDIS_DB=...                         # Redis数据库编号
REDIS_PASSWORD=...                   # Redis密码

# Django核心配置
SECRET_KEY=...                       # Django密钥
DEBUG=...                           # 调试模式
ALLOWED_HOSTS=...                    # 允许的主机

# 生产环境配置
DJANGO_SUPERUSER_USERNAME=...       # Django超级用户名
DJANGO_SUPERUSER_EMAIL=...          # Django超级用户邮箱
DJANGO_SUPERUSER_PASSWORD=...       # Django超级用户密码

# Gunicorn配置
GUNICORN_WORKERS=...                # Gunicorn工作进程数
GUNICORN_THREADS=...                 # Gunicorn线程数
LOG_LEVEL=...                       # 日志级别

# CORS配置
CORS_ALLOWED_ORIGINS=...             # 允许的跨域源
```

## 📋 详细配置说明

### 1. 数据库配置 (PostgreSQL)

```bash
# 数据库名称
DATABASE_NAME=gogame_db
# 说明: PostgreSQL数据库名称
# 默认值: gogame_db
# 生产环境建议: 使用具有描述性的数据库名称

# 数据库用户名
DATABASE_USER=gogame_user
# 说明: PostgreSQL数据库用户名
# 默认值: gogame_user
# 生产环境建议: 使用具有最小权限的用户

# 数据库密码
DATABASE_PASSWORD=gogame_password
# 说明: PostgreSQL数据库密码
# 默认值: gogame_password
# 生产环境建议: 使用强密码，长度至少12位，包含大小写字母、数字和特殊字符
# 示例: MySecureP@ssw0rd!2024

# 数据库主机
DATABASE_HOST=postgres
# 说明: 数据库服务器地址
# Docker环境: postgres (容器名)
# 本地环境: localhost 或 127.0.0.1
# 生产环境: 数据库服务器IP或域名

# 数据库端口
DATABASE_PORT=5432
# 说明: PostgreSQL数据库端口
# 默认值: 5432
# 生产环境建议: 使用默认端口，如有防火墙需开放相应端口
```

### 2. Redis缓存配置

```bash
# Redis主机
REDIS_HOST=redis
# 说明: Redis服务器地址
# Docker环境: redis (容器名)
# 本地环境: localhost 或 127.0.0.1
# 生产环境: Redis服务器IP或域名

# Redis端口
REDIS_PORT=6379
# 说明: Redis服务器端口
# 默认值: 6379
# 生产环境建议: 使用默认端口，如有防火墙需开放相应端口

# Redis数据库编号
REDIS_DB=0
# 说明: Redis数据库编号
# 默认值: 0
# 可选值: 0-15
# 生产环境建议: 使用不同的数据库编号区分不同环境

# Redis密码
REDIS_PASSWORD=
# 说明: Redis认证密码
# 默认值: 空（无密码）
# 生产环境建议: 设置强密码
# 示例: MyRedisP@ssw0rd!2024
```

### 3. Django核心配置

```bash
# Django密钥
SECRET_KEY=django-insecure-production-key-change-this
# 说明: Django加密密钥，用于签名和加密
# 默认值: 自动生成的字符串
# 生产环境建议: 使用随机生成的强密钥，至少50个字符
# 生成命令: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# 调试模式
DEBUG=False
# 说明: Django调试模式开关
# 默认值: False
# 开发环境: True
# 生产环境: False (必须设置为False)

# 允许的主机
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
# 说明: 允许访问Django应用的主机列表
# 格式: 逗号分隔的主机列表
# 开发环境: localhost,127.0.0.1,0.0.0.0
# 生产环境: 您的域名，如 example.com,www.example.com
# 示例: yourdomain.com,www.yourdomain.com,api.yourdomain.com
```

### 4. 生产环境特定配置

```bash
# Django超级用户名
DJANGO_SUPERUSER_USERNAME=admin
# 说明: Django超级管理员用户名
# 默认值: admin
# 生产环境建议: 使用具有描述性的用户名，避免使用常见的admin
# 示例: superuser,admin_gogame,root_user

# Django超级用户邮箱
DJANGO_SUPERUSER_EMAIL=admin@example.com
# 说明: Django超级管理员邮箱
# 默认值: admin@example.com
# 生产环境建议: 使用真实的邮箱地址，用于密码重置等功能
# 示例: admin@yourdomain.com

# Django超级用户密码
DJANGO_SUPERUSER_PASSWORD=admin123
# 说明: Django超级管理员密码
# 默认值: admin123
# 生产环境建议: 使用强密码，长度至少12位
# 示例: MySecureP@ssw0rd!2024
```

### 5. Gunicorn配置

```bash
# Gunicorn工作进程数
GUNICORN_WORKERS=1
# 说明: Gunicorn工作进程数量
# 默认值: 1 (单进程)
# 生产环境建议: 根据CPU核心数设置，通常为 CPU核心数 × 2 + 1
# 示例: 4核心CPU设置为9 (4×2+1)
# 性能考虑: 更多进程可以提高并发处理能力，但会增加内存使用

# Gunicorn线程数
GUNICORN_THREADS=4
# 说明: 每个工作进程的线程数量
# 默认值: 4
# 生产环境建议: 2-4个线程，适合I/O密集型应用
# 性能考虑: 线程适合处理I/O等待操作，如数据库查询、网络请求

# 日志级别
LOG_LEVEL=info
# 说明: 应用日志级别
# 可选值: debug, info, warning, error, critical
# 开发环境: debug
# 生产环境: info 或 warning
# 性能考虑: 日志级别越详细，性能影响越大
```

### 6. CORS配置

```bash
# 允许的跨域源
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
# 说明: 允许跨域访问的前端源列表
# 格式: 逗号分隔的URL列表
# 开发环境: http://localhost:3000,http://127.0.0.1:3000
# 生产环境: https://yourdomain.com,https://www.yourdomain.com
# 安全考虑: 生产环境应该指定具体的域名，避免使用通配符
```

## 🚀 环境配置示例

### 开发环境配置 (.env.dev)

```bash
# 数据库配置
DATABASE_NAME=gogame_dev
DATABASE_USER=gogame_user
DATABASE_PASSWORD=gogame_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Django配置
SECRET_KEY=django-insecure-dev-key-for-local-development-only
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# 超级用户配置
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@localhost
DJANGO_SUPERUSER_PASSWORD=admin123

# Gunicorn配置
GUNICORN_WORKERS=1
GUNICORN_THREADS=2
LOG_LEVEL=debug

# CORS配置
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 生产环境配置 (.env.prod)

```bash
# 数据库配置
DATABASE_NAME=gogame_production
DATABASE_USER=gogame_prod_user
DATABASE_PASSWORD=MySecureP@ssw0rd!2024
DATABASE_HOST=postgres
DATABASE_PORT=5432

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=1
REDIS_PASSWORD=MyRedisP@ssw0rd!2024

# Django配置
SECRET_KEY=your-generated-secret-key-here-50-characters-long-random-string
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com

# 超级用户配置
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=YourSecureP@ssw0rd!2024

# Gunicorn配置
GUNICORN_WORKERS=4
GUNICORN_THREADS=4
LOG_LEVEL=info

# CORS配置
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🔒 安全注意事项

### 1. 密钥管理
- **永远不要**将包含真实密码的`.env`文件提交到版本控制系统
- 使用`.env.example`作为模板，不包含敏感信息
- 在生产环境中使用强密码和随机密钥

### 2. 文件权限
```bash
# 设置环境变量文件权限
chmod 600 .env
```

### 3. 密码生成建议
- **数据库密码**: 至少12位，包含大小写字母、数字和特殊字符
- **Redis密码**: 至少12位，使用字母数字组合
- **Django密钥**: 使用Django提供的命令生成
- **超级用户密码**: 至少12位，复杂度要求同数据库密码

### 4. 生产环境安全检查清单
- [ ] `DEBUG=False`
- [ ] 使用强密码
- [ ] 配置正确的`ALLOWED_HOSTS`
- [ ] 设置适当的`CORS_ALLOWED_ORIGINS`
- [ ] 配置HTTPS（反向代理）
- [ ] 定期更新密码

## 🛠️ 配置验证

### 1. 检查配置加载
```python
# 在Django shell中验证
python manage.py shell
>>> import os
>>> print(f"Database: {os.getenv('DATABASE_NAME')}")
>>> print(f"Debug: {os.getenv('DEBUG')}")
```

### 2. 健康检查
```bash
# 检查服务健康状态
curl http://localhost:8000/api/health/
```

### 3. 日志检查
```bash
# 查看应用日志
docker-compose logs backend
```

## 📚 常见问题解决

### 1. 数据库连接失败
```bash
# 检查数据库服务状态
docker-compose ps postgres
docker-compose logs postgres
```

### 2. Redis连接失败
```bash
# 检查Redis服务状态
docker-compose ps redis
docker-compose exec redis redis-cli ping
```

### 3. 权限问题
```bash
# 检查文件权限
ls -la .env
chmod 600 .env
```

### 4. 环境变量未生效
```bash
# 重启服务使环境变量生效
docker-compose down
docker-compose up -d
```

---

**注意**: 请根据您的实际部署环境调整相应的配置值。生产环境请务必遵循安全最佳实践。