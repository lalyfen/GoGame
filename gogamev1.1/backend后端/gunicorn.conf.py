# Gunicorn配置文件
# gunicorn.conf.py

import multiprocessing
import os

# 服务器套接字
bind = "0.0.0.0:8000"
backlog = 2048

# 工作进程配置
# 默认配置：单进程，多线程
workers = int(os.environ.get('GUNICORN_WORKERS', 1))
threads = int(os.environ.get('GUNICORN_THREADS', 4))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 30
keepalive = 2

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = 'gogame-backend'

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 服务器机制
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None
logfile = '-'
disable_redirect_access_to_syslog = False

# SSL（如果需要）
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# 监控
statsd_host = None
statsd_prefix = ''

# 钩子
def when_ready(server):
    """服务器启动时执行"""
    server.log.info("Gunicorn服务器已就绪")

def worker_int(worker):
    """工作进程收到SIGINT信号时执行"""
    worker.log.info("工作进程收到中断信号")

def pre_fork(server, worker):
    """Fork工作进程前执行"""
    server.log.info("Worker即将fork: %s", worker.pid)

def post_fork(server, worker):
    """Fork工作进程后执行"""
    server.log.info("Worker已fork: %s", worker.pid)

def post_worker_init(worker):
    """工作进程初始化后执行"""
    worker.log.info("Worker初始化完成: %s", worker.pid)

def worker_abort(worker):
    """工作进程异常退出时执行"""
    worker.log.info("Worker异常退出: %s", worker.pid)

# 生产环境特定设置
if not os.environ.get('DEBUG', 'False').lower() == 'true':
    # 生产环境配置
    raw_env = [
        'DJANGO_SETTINGS_MODULE=core.settings',
    ]