#!/bin/bash

# GoGame 围棋项目一键部署脚本
# 支持前后端nginx代理的Docker Compose部署

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "GoGame 围棋项目部署脚本"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start       启动所有服务"
    echo "  stop        停止所有服务"
    echo "  restart     重启所有服务"
    echo "  logs        查看服务日志"
    echo "  status      查看服务状态"
    echo "  build       重新构建镜像"
    echo "  clean       清理所有容器和镜像"
    echo "  help        显示此帮助信息"
    echo ""
    echo "选项:"
    echo "  -v, --verbose    详细输出"
    echo "  -f, --force      强制执行操作"
    echo "  --dev           开发环境模式"
    echo ""
    echo "示例:"
    echo "  $0 start                # 启动服务"
    echo "  $0 logs nginx           # 查看nginx日志"
    echo "  $0 build --force        # 强制重新构建"
}

# 检查Docker和Docker Compose是否安装
check_dependencies() {
    log_info "检查依赖..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi

    log_success "依赖检查通过"
}

# 检查项目文件
check_project_files() {
    log_info "检查项目文件..."

    required_files=(
        "docker-compose.yml"
        "frontend前端/Dockerfile"
        "frontend前端/package.json"
        "backend后端/Dockerfile"
        "nginx/default.conf"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "缺少必要文件: $file"
            exit 1
        fi
    done

    log_success "项目文件检查通过"
}

# 创建环境变量文件
setup_environment() {
    log_info "设置环境变量..."

    # 如果.env文件不存在，则从示例文件创建
    if [ ! -f ".env" ]; then
        if [ -f "backend后端/.env.example" ]; then
            cp backend后端/.env.example .env
            log_info "已从.env.example创建.env文件"
        else
            # 创建基本的环境变量文件
            cat > .env << EOF
# GoGame 环境配置
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
EOF
            log_info "已创建基本.env文件"
        fi
    fi

    log_success "环境变量设置完成"
}

# 启动服务
start_services() {
    log_info "启动GoGame服务..."

    # 检查端口是否被占用
    if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null ; then
        log_warning "端口80已被占用，尝试停止现有服务..."
        sudo lsof -ti:80 | xargs sudo kill -9 2>/dev/null || true
    fi

    # 启动服务
    if [ "$VERBOSE" = true ]; then
        docker-compose up -d
    else
        docker-compose up -d --quiet-pull
    fi

    log_success "服务启动完成"

    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10

    # 检查服务状态
    show_status
}

# 停止服务
stop_services() {
    log_info "停止GoGame服务..."
    docker-compose down
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启GoGame服务..."
    stop_services
    sleep 5
    start_services
}

# 查看日志
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f --tail=100
    else
        docker-compose logs -f --tail=100 "$service"
    fi
}

# 查看服务状态
show_status() {
    log_info "服务状态:"
    echo ""
    docker-compose ps

    echo ""
    log_info "服务访问地址:"
    echo "  前端应用: http://localhost"
    echo "  后端API: http://localhost/backend/"
    echo "  管理后台: http://localhost/admin (自动重定向到/backend/admin/)"
    echo ""

    # 检查服务健康状态
    if docker-compose ps | grep -q "Up (healthy)"; then
        log_success "所有服务运行正常"
    elif docker-compose ps | grep -q "Up"; then
        log_warning "服务正在启动中，请稍等..."
    else
        log_error "部分服务启动失败，请检查日志"
    fi
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."

    if [ "$FORCE" = true ]; then
        docker-compose build --no-cache
    else
        docker-compose build
    fi

    log_success "镜像构建完成"
}

# 清理资源
clean_resources() {
    log_info "清理Docker资源..."

    read -p "确定要删除所有容器、镜像和数据卷吗？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all
        docker system prune -f
        log_success "清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 初始化项目
init_project() {
    log_info "初始化GoGame项目..."

    check_dependencies
    check_project_files
    setup_environment

    log_success "项目初始化完成"
    log_info "运行 '$0 start' 启动服务"
}

# 主函数
main() {
    # 解析命令行参数
    VERBOSE=false
    FORCE=false
    DEV_MODE=false
    COMMAND=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            --dev)
                DEV_MODE=true
                shift
                ;;
            start|stop|restart|logs|status|build|clean|help)
                COMMAND="$1"
                shift
                ;;
            *)
                if [ -z "$COMMAND" ]; then
                    COMMAND="$1"
                fi
                shift
                ;;
        esac
    done

    # 切换到脚本所在目录
    cd "$(dirname "$0")"

    # 处理命令
    case $COMMAND in
        start)
            init_project
            start_services
            ;;
        stop)
            check_dependencies
            stop_services
            ;;
        restart)
            check_dependencies
            restart_services
            ;;
        logs)
            check_dependencies
            show_logs "$1"
            ;;
        status)
            check_dependencies
            show_status
            ;;
        build)
            init_project
            build_images
            ;;
        clean)
            check_dependencies
            clean_resources
            ;;
        help|"")
            show_help
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"