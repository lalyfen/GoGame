"""
日志装饰器模块 - 用于统一处理视图的访问日志和错误处理
"""
import logging
from functools import wraps
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

# 配置日志记录器
access_logger = logging.getLogger('datab.access')
error_logger = logging.getLogger('datab')
debug_logger = logging.getLogger('datab')

def log_api_access(operation_name):
    """
    API访问日志装饰器

    Args:
        operation_name (str): 操作名称，用于日志记录
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # 获取客户端IP
            client_ip = get_client_ip(request)

            # 记录访问开始
            access_logger.info(
                f"{operation_name} - 用户: {request.user.username}, "
                f"IP: {client_ip}, 参数: {dict(request.query_params)}"
            )

            try:
                # 记录调试信息
                debug_logger.debug(
                    f"{operation_name} - 请求详情: "
                    f"Method: {request.method}, "
                    f"Path: {request.path}, "
                    f"Data: {request.data if request.data else 'None'}"
                )

                # 执行原视图函数
                response = view_func(self, request, *args, **kwargs)

                # 记录成功响应
                if hasattr(response, 'data'):
                    access_logger.info(
                        f"{operation_name} - 成功完成 - "
                        f"用户: {request.user.username}, "
                        f"状态码: {response.status_code}, "
                        f"响应数据大小: {len(str(response.data)) if response.data else 0}"
                    )
                else:
                    access_logger.info(
                        f"{operation_name} - 成功完成 - "
                        f"用户: {request.user.username}, "
                        f"状态码: {response.status_code}"
                    )

                return response

            except Exception as e:
                # 记录错误信息
                error_logger.error(
                    f"{operation_name} - 执行失败 - "
                    f"用户: {request.user.username}, "
                    f"错误类型: {type(e).__name__}, "
                    f"错误信息: {str(e)}",
                    exc_info=True  # 记录完整的堆栈跟踪
                )

                # 返回统一错误响应
                return Response(
                    {'error': f'{operation_name}失败', 'detail': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return wrapper
    return decorator

def get_client_ip(request):
    """获取客户端真实IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_database_operation(model_name, operation):
    """
    数据库操作日志装饰器

    Args:
        model_name (str): 模型名称
        operation (str): 操作类型 (create, update, delete, retrieve)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            client_ip = get_client_ip(request)
            object_id = kwargs.get('pk', 'N/A')

            # 记录数据库操作开始
            access_logger.info(
                f"数据库操作 - {model_name} {operation} - "
                f"用户: {request.user.username}, "
                f"IP: {client_ip}, "
                f"对象ID: {object_id}"
            )

            try:
                response = view_func(self, request, *args, **kwargs)

                # 记录操作成功
                if operation == 'create' and hasattr(response, 'data'):
                    created_id = response.data.get('id', 'N/A')
                    access_logger.info(
                        f"数据库操作成功 - {model_name} {operation} - "
                        f"用户: {request.user.username}, "
                        f"创建对象ID: {created_id}"
                    )
                else:
                    access_logger.info(
                        f"数据库操作成功 - {model_name} {operation} - "
                        f"用户: {request.user.username}, "
                        f"对象ID: {object_id}"
                    )

                return response

            except Exception as e:
                error_logger.error(
                    f"数据库操作失败 - {model_name} {operation} - "
                    f"用户: {request.user.username}, "
                    f"对象ID: {object_id}, "
                    f"错误: {str(e)}",
                    exc_info=True
                )
                raise

        return wrapper
    return decorator