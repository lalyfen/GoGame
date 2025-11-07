# 使用Python 3.11官方镜像作为基础镜像
FROM python:3.11-slim

# 设置标签信息
LABEL maintainer="GoGame Backend Team"
LABEL description="GoGame Backend with Django, PostgreSQL, Redis, and Gunicorn"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 创建非root用户
RUN groupadd -r django && useradd -r -g django django

# 复制项目文件
COPY . .

# 设置文件权限
RUN chown -R django:django /app
RUN chmod +x /app/docker-entrypoint.sh

# 切换到非root用户
USER django

# 收集静态文件
RUN python manage.py collectstatic --noinput --clear

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# 暴露端口
EXPOSE 8000

# 使用入口脚本
ENTRYPOINT ["/app/docker-entrypoint.sh"]