from django.urls import path
from . import views

urlpatterns = [
    # 设置用户服务区
    path('set-server/', views.set_server, name='set_server'),

    # 搜索同服务区用户
    path('search-users/', views.search_users, name='search_users'),

    # 创建邀请
    path('create/', views.create_invitation, name='create_invitation'),

    # 确认邀请
    path('confirm/<int:invitation_id>/', views.confirm_invitation, name='confirm_invitation'),

    # 删除邀请
    path('delete/<int:invitation_id>/', views.delete_invitation, name='delete_invitation'),

    # 列出发出的邀请
    path('sent-invitations/', views.list_sent_invitations, name='list_sent_invitations'),

    # 列出收到的邀请
    path('received-invitations/', views.list_received_invitations, name='list_received_invitations'),
]
