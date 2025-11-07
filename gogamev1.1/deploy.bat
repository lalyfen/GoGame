@echo off
REM GoGame 围棋项目一键部署脚本 (Windows版本)
REM 支持前后端nginx代理的Docker Compose部署

setlocal enabledelayedexpansion

REM 设置颜色代码
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 日志函数
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM 显示帮助信息
:show_help
echo GoGame 围棋项目部署脚本 (Windows)
echo.
echo 用法: %~nx0 [命令] [选项]
echo.
echo 命令:
echo   start       启动所有服务
echo   stop        停止所有服务
echo   restart     重启所有服务
echo   logs        查看服务日志
echo   status      查看服务状态
echo   build       重新构建镜像
echo   clean       清理所有容器和镜像
echo   help        显示此帮助信息
echo.
echo 选项:
echo   --verbose   详细输出
echo   --force     强制执行操作
echo   --dev       开发环境模式
echo.
echo 示例:
echo   %~nx0 start                # 启动服务
echo   %~nx0 logs nginx           # 查看nginx日志
echo   %~nx0 build --force        # 强制重新构建
goto :eof

REM 检查Docker和Docker Compose是否安装
:check_dependencies
call :log_info "检查依赖..."

docker --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker未安装，请先安装Docker Desktop"
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        call :log_error "Docker Compose未安装，请先安装Docker Compose"
        exit /b 1
    )
)

call :log_success "依赖检查通过"
goto :eof

REM 检查项目文件
:check_project_files
call :log_info "检查项目文件..."

set "files[0]=docker-compose.yml"
set "files[1]=frontend前端\Dockerfile"
set "files[2]=frontend前端\package.json"
set "files[3]=backend后端\Dockerfile"
set "files[4]=nginx\default.conf"

for /l %%i in (0,1,4) do (
    if not exist "!files[%%i]!" (
        call :log_error "缺少必要文件: !files[%%i]!"
        exit /b 1
    )
)

call :log_success "项目文件检查通过"
goto :eof

REM 创建环境变量文件
:setup_environment
call :log_info "设置环境变量..."

if not exist ".env" (
    if exist "backend后端\.env.example" (
        copy "backend后端\.env.example" ".env" >nul
        call :log_info "已从.env.example创建.env文件"
    ) else (
        REM 创建基本的环境变量文件
        (
            echo # GoGame 环境配置
            echo COMPOSE_PROJECT_NAME=gogame
            echo.
            echo # 数据库配置
            echo POSTGRES_DB=gogame_db
            echo POSTGRES_USER=gogame_user
            echo POSTGRES_PASSWORD=gogame_password
            echo.
            echo # Redis配置
            echo REDIS_PASSWORD=
            echo.
            echo # Django配置
            echo SECRET_KEY=django-insecure-production-key-change-this
            echo DEBUG=False
            echo ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
            echo.
            echo # 超级用户配置
            echo DJANGO_SUPERUSER_USERNAME=admin
            echo DJANGO_SUPERUSER_EMAIL=admin@example.com
            echo DJANGO_SUPERUSER_PASSWORD=admin123
            echo.
            echo # CORS配置（nginx代理模式）
            echo CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
            echo.
            echo # Gunicorn配置
            echo GUNICORN_WORKERS=1
            echo GUNICORN_THREADS=4
            echo LOG_LEVEL=info
        ) > .env
        call :log_info "已创建基本.env文件"
    )
)

call :log_success "环境变量设置完成"
goto :eof

REM 启动服务
:start_services
call :log_info "启动GoGame服务..."

REM 检查端口是否被占用
netstat -an | findstr ":80" | findstr "LISTENING" >nul
if not errorlevel 1 (
    call :log_warning "端口80已被占用，请检查是否有其他服务在运行"
)

REM 启动服务
if "%VERBOSE%"=="true" (
    docker-compose up -d
) else (
    docker-compose up -d --quiet-pull
)

call :log_success "服务启动完成"

REM 等待服务启动
call :log_info "等待服务启动..."
timeout /t 10 /nobreak >nul

REM 检查服务状态
call :show_status
goto :eof

REM 停止服务
:stop_services
call :log_info "停止GoGame服务..."
docker-compose down
call :log_success "服务已停止"
goto :eof

REM 重启服务
:restart_services
call :log_info "重启GoGame服务..."
call :stop_services
timeout /t 5 /nobreak >nul
call :start_services
goto :eof

REM 查看日志
:show_logs
set "service=%~1"
if "%service%"=="" (
    docker-compose logs -f --tail=100
) else (
    docker-compose logs -f --tail=100 %service%
)
goto :eof

REM 查看服务状态
:show_status
call :log_info "服务状态:"
echo.
docker-compose ps

echo.
call :log_info "服务访问地址:"
echo   前端应用: http://localhost
echo   API接口: http://localhost/api
echo   后端管理: http://localhost/admin
echo.

REM 检查服务健康状态
docker-compose ps | findstr "Up (healthy)" >nul
if not errorlevel 1 (
    call :log_success "所有服务运行正常"
) else (
    docker-compose ps | findstr "Up" >nul
    if not errorlevel 1 (
        call :log_warning "服务正在启动中，请稍等..."
    ) else (
        call :log_error "部分服务启动失败，请检查日志"
    )
)
goto :eof

REM 构建镜像
:build_images
call :log_info "构建Docker镜像..."

if "%FORCE%"=="true" (
    docker-compose build --no-cache
) else (
    docker-compose build
)

call :log_success "镜像构建完成"
goto :eof

REM 清理资源
:clean_resources
call :log_info "清理Docker资源..."

set /p confirm="确定要删除所有容器、镜像和数据卷吗？(y/N): "
if /i "%confirm%"=="y" (
    docker-compose down -v --rmi all
    docker system prune -f
    call :log_success "清理完成"
) else (
    call :log_info "取消清理操作"
)
goto :eof

REM 初始化项目
:init_project
call :log_info "初始化GoGame项目..."

call :check_dependencies
call :check_project_files
call :setup_environment

call :log_success "项目初始化完成"
call :log_info "运行 '%~nx0 start' 启动服务"
goto :eof

REM 主程序
:main
REM 设置默认值
set "VERBOSE=false"
set "FORCE=false"
set "DEV_MODE=false"
set "COMMAND="

REM 解析命令行参数
:parse_args
if "%~1"=="" goto :exec_command
if "%~1"=="--verbose" (
    set "VERBOSE=true"
    shift
    goto :parse_args
) else if "%~1"=="--force" (
    set "FORCE=true"
    shift
    goto :parse_args
) else if "%~1"=="--dev" (
    set "DEV_MODE=true"
    shift
    goto :parse_args
) else if "%~1"=="start" (
    set "COMMAND=start"
    shift
    goto :parse_args
) else if "%~1"=="stop" (
    set "COMMAND=stop"
    shift
    goto :parse_args
) else if "%~1"=="restart" (
    set "COMMAND=restart"
    shift
    goto :parse_args
) else if "%~1"=="logs" (
    set "COMMAND=logs"
    shift
    goto :parse_args
) else if "%~1"=="status" (
    set "COMMAND=status"
    shift
    goto :parse_args
) else if "%~1"=="build" (
    set "COMMAND=build"
    shift
    goto :parse_args
) else if "%~1"=="clean" (
    set "COMMAND=clean"
    shift
    goto :parse_args
) else if "%~1"=="help" (
    set "COMMAND=help"
    shift
    goto :parse_args
) else (
    if "%COMMAND%"=="" set "COMMAND=%~1"
    shift
    goto :parse_args
)

:exec_command
REM 处理命令
if "%COMMAND%"=="start" (
    call :init_project
    call :start_services
) else if "%COMMAND%"=="stop" (
    call :check_dependencies
    call :stop_services
) else if "%COMMAND%"=="restart" (
    call :check_dependencies
    call :restart_services
) else if "%COMMAND%"=="logs" (
    call :check_dependencies
    call :show_logs "%~1"
) else if "%COMMAND%"=="status" (
    call :check_dependencies
    call :show_status
) else if "%COMMAND%"=="build" (
    call :init_project
    call :build_images
) else if "%COMMAND%"=="clean" (
    call :check_dependencies
    call :clean_resources
) else if "%COMMAND%"=="help" (
    call :show_help
) else if "%COMMAND%"=="" (
    call :show_help
) else (
    call :log_error "未知命令: %COMMAND%"
    call :show_help
    exit /b 1
)

goto :eof

REM 调用主程序
call :main %*