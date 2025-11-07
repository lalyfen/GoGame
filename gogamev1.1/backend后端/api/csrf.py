# api/csrf.py - CSRF Token管理
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@ensure_csrf_cookie
@permission_classes([AllowAny])
def get_csrf_token(request):
    """
    返回CSRF token给前端

    双重提交CSRF机制：
    1. Django通过Set-Cookie响应头设置CSRF cookie
    2. 前端读取cookie并在请求头中发送
    3. Django验证cookie和请求头中的token是否匹配
    """
    # get_token()会确保CSRF cookie被设置
    token = get_token(request)

    return Response({
        'csrfToken': token,
        'message': 'CSRF token已设置'
    })