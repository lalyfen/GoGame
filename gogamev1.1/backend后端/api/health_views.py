from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def health_check(request):
    """
    健康检查端点
    返回系统状态信息，用于容器健康检查
    """
    try:
        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    try:
        # 检查缓存连接
        cache.set("health_check", "ok", 10)
        cache_result = cache.get("health_check")
        cache_status = "healthy" if cache_result == "ok" else "unhealthy"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        cache_status = "unhealthy"

    # 计算系统状态
    overall_status = "healthy" if db_status == "healthy" and cache_status == "healthy" else "unhealthy"

    response_data = {
        "status": overall_status,
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": {
                "status": db_status,
                "type": "PostgreSQL"
            },
            "cache": {
                "status": cache_status,
                "type": "Redis"
            }
        },
        "application": {
            "name": "GoGame Backend",
            "environment": "production" if not getattr(settings, 'DEBUG', False) else "development"
        }
    }

    status_code = 200 if overall_status == "healthy" else 503
    return JsonResponse(response_data, status=status_code)