#!/bin/bash
set -e

# Django容器入口脚本

# 等待数据库和Redis服务启动
echo "等待数据库和Redis服务启动..."

# 等待PostgreSQL数据库启动
until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME"; do
    echo "PostgreSQL数据库未就绪，等待5秒..."
    sleep 5
done
echo "PostgreSQL数据库已就绪！"

# 等待Redis服务启动
python -c "
import redis
import time
import os

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_password = os.environ.get('REDIS_PASSWORD', '')

for i in range(30):  # 尝试30次，每次等待2秒
    try:
        r = redis.Redis(host=redis_host, port=redis_port, password=redis_password if redis_password else None, socket_connect_timeout=5)
        r.ping()
        print('Redis服务已就绪！')
        break
    except Exception as e:
        if i == 29:
            print('Redis服务连接失败，退出')
            exit(1)
        print(f'Redis服务未就绪，等待2秒... ({e})')
        time.sleep(2)
"

# 运行数据库迁移
echo "运行数据库迁移..."
python manage.py migrate --noinput

# 创建超级用户（如果不存在）
echo "检查超级用户..."
python manage.py shell << EOF
from django.contrib.auth.models import User
import os

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"超级用户 {username} 创建成功")
else:
    print(f"超级用户 {username} 已存在")
EOF

# 启动Gunicorn服务器
echo "启动Gunicorn服务器..."
if [ "$DEBUG" = "True" ]; then
    echo "调试模式：使用开发服务器"
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "生产模式：使用Gunicorn服务器"
    # 使用默认配置：单进程，多线程
    exec gunicorn core.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 1 \
        --threads 4 \
        --timeout 30 \
        --keep-alive 2 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level info
fi