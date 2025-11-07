# core/urls.py - 项目核心URL配置
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Django管理后台
    path('api/', include('api.urls')),  # 认证相关API
    # 为降低耦合，直接在核心路由挂载datab应用
    path('api/datab/', include('datab.urls')),  # 数据相关API
    # 邀请系统API
    path('api/invitation/', include('invitation.urls')),  # 邀请系统API
]

# 生产环境中静态文件服务（通过nginx代理时需要）
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)