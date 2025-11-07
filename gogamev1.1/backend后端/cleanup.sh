#!/bin/bash

# GoGame后端环境清理脚本
# 用于完全清理Docker容器、镜像、卷和网络

set -e

echo "🧹 开始清理GoGame后端环境..."
echo "=================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，无需清理"
    exit 0
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，无需清理"
    exit 0
fi

# 停止并删除所有容器
echo "🛑 停止并删除所有容器..."
docker-compose down --remove-orphans 2>/dev/null || {
    echo "⚠️  docker-compose services未找到，尝试手动停止容器..."
    # 手动停止可能存在的容器
    docker stop gogame_backend gogame_postgres gogame_redis 2>/dev/null || true
    docker rm gogame_backend gogame_postgres gogame_redis 2>/dev/null || true
}

# 删除相关的Docker镜像
echo "🗑️  删除Docker镜像..."
docker rmi backend-backend 2>/dev/null || echo "⚠️  后端镜像不存在或已删除"

# 删除Docker卷（数据库数据）
echo "💾 删除Docker卷（数据库数据）..."
docker volume rm backend_postgres_data backend_redis_data backend_static_volume backend_media_volume 2>/dev/null || echo "⚠️  部分卷不存在或已删除"

# 删除Docker网络
echo "🌐 删除Docker网络..."
docker network rm backend_gogame_network 2>/dev/null || echo "⚠️  网络不存在或已删除"

# 清理未使用的Docker资源
echo "🧹 清理未使用的Docker资源..."
docker system prune -f

# 删除临时文件
echo "📁 删除临时文件..."
rm -f test_cookies.txt
rm -f .env 2>/dev/null || echo "⚠️  .env文件不存在或保留"

# 清理日志文件（可选）
read -p "是否删除日志文件？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf logs/ 2>/dev/null || echo "⚠️  日志目录不存在"
    rm -f *.log 2>/dev/null || echo "⚠️  日志文件不存在"
fi

# 清理静态文件（可选）
read -p "是否删除收集的静态文件？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf staticfiles/ 2>/dev/null || echo "⚠️  静态文件目录不存在"
fi

echo ""
echo "✅ 环境清理完成！"
echo "=================================="
echo "📋 已清理的内容："
echo "  - 所有Docker容器"
echo "  - Docker镜像"
echo "  - 数据库和缓存卷"
echo "  - Docker网络"
echo "  - 临时文件"
echo ""
echo "🔄 重新部署请运行："
echo "  ./deploy.sh"
echo ""
echo "⚠️  注意：数据库数据已永久删除！"