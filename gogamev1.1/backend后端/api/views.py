# api/views.py - 认证相关视图
import logging
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

logger = logging.getLogger('api')

# 刷新令牌的Cookie名称
COOKIE_NAME = 'refresh'

class RegisterView(generics.CreateAPIView):
    """
    用户注册视图 - 任何人都可以访问
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)  # 允许任何人访问
    serializer_class = RegisterSerializer

class ProtectedView(APIView):
    """
    受保护的视图 - 需要有效的访问令牌
    """
    permission_classes = [IsAuthenticated]  # 需要登录认证

    def get(self, request):
        content = {
            'message': f'你好, {request.user.username}! 这是一个受保护的端点，只有持有有效JWT访问令牌的用户才能访问。',
        }
        return Response(content)

class LogoutView(APIView):
    """用户登出视图 - 使刷新令牌失效"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        logger.info(f"Logout attempt for user: {request.user.username}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request cookies: {dict(request.COOKIES)}")

        # 从HttpOnly Cookie中读取刷新令牌（推荐使用Cookie-based流程）
        refresh_token = request.COOKIES.get(COOKIE_NAME)
        logger.info(f"Refresh token from cookie: {refresh_token[:20] if refresh_token else None}...")

        try:
            if not refresh_token:
                logger.warning(f"No refresh token found in cookies for user: {request.user.username}")
                return Response(
                    {'detail': '未提供刷新令牌'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info(f"Attempting to blacklist refresh token for user: {request.user.username}")
            token = RefreshToken(refresh_token)
            token.blacklist()  # 将令牌加入黑名单
            logger.info(f"Successfully blacklisted refresh token for user: {request.user.username}")

            # 在响应中删除Cookie
            resp = Response(status=status.HTTP_205_RESET_CONTENT)
            resp.delete_cookie(COOKIE_NAME, path='/', domain=None)
            logger.info(f"Logout completed successfully for user: {request.user.username}")
            return resp

        except Exception as e:
            logger.error(f"Logout failed for user {request.user.username}: {str(e)}", exc_info=True)
            return Response(
                {'detail': f'登出失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义令牌获取视图 - 在响应体中返回访问令牌，并将刷新令牌设置为HttpOnly Cookie"""

    def finalize_response(self, request, response, *args, **kwargs):
        # 首先调用父类的finalize方法
        return super().finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # 如果成功，将刷新令牌设置为HttpOnly Cookie
        if response.status_code == 200 and 'refresh' in response.data:
            refresh = response.data.pop('refresh')
            secure = not settings.DEBUG  # 非调试模式下启用安全Cookie
            
            # 设置Cookie属性：HttpOnly、非调试模式下Secure、SameSite Lax
            response.set_cookie(
                COOKIE_NAME,
                refresh,
                httponly=True,
                secure=secure,
                samesite='Lax',
                path='/'
            )
        return response


class CustomTokenRefreshView(APIView):
    """自定义令牌刷新视图 - 使用HttpOnly Cookie中的刷新令牌来获取新的访问令牌
    响应新的访问令牌（如果启用了轮换，也可能包含新的刷新令牌）并设置Cookie
    """

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # 从Cookie中读取刷新令牌
        refresh_token = request.COOKIES.get(COOKIE_NAME)

        if not refresh_token:
            return Response({'detail': '未提供刷新令牌'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'detail': '无效的刷新令牌'}, status=status.HTTP_401_UNAUTHORIZED)

        data = serializer.validated_data
        response = Response(data)
        # 如果启用了轮换，序列化器可能返回新的刷新令牌
        new_refresh = data.get('refresh')
        if new_refresh:
            secure = not settings.DEBUG
            response.set_cookie(
                COOKIE_NAME,
                new_refresh,
                httponly=True,
                secure=secure,
                samesite='Lax',
                path='/'
            )
            # 为安全起见从响应体中移除刷新令牌：客户端应该依赖Cookie
            response.data.pop('refresh', None)
            
        return response