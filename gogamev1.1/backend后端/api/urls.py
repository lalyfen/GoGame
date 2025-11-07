# api/urls.py - 认证相关URL配置
from django.urls import path
from .views import CustomTokenObtainPairView, CustomTokenRefreshView
from .views import RegisterView, ProtectedView, LogoutView
from .csrf import get_csrf_token
from . import health_views

urlpatterns = [
    # 健康检查端点
    path('health/', health_views.health_check, name='health_check'),

    # CSRF Token端点 - 统一入口
    path('csrf/', get_csrf_token, name='get_csrf_token'),  # 获取CSRF token并设置cookie

    # 认证端点
    path('register/', RegisterView.as_view(), name='register'),  # 用户注册
    path('protected/', ProtectedView.as_view(), name='protected'),  # 受保护端点
    path('logout/', LogoutView.as_view(), name='logout'),  # 用户登出

    # 使用自定义令牌端点，设置/读取HttpOnly刷新Cookie
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # 获取令牌（设置刷新Cookie）
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),  # 刷新令牌（读取Cookie）
]