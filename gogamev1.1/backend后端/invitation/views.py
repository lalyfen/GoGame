from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import UserServer, Invitation
from .serializers import (
    UserServerSerializer,
    InvitationSerializer,
    CreateInvitationSerializer,
    SetServerSerializer,
    SearchUsersSerializer
)

# 缓存相关导入
from core.cache_manager import (
    CacheKeyManager,
    CacheTimeouts,
    cache_result,
    invalidate_user_cache,
    invalidate_invitation_cache
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_server(request):
    """设置用户服务区"""
    serializer = SetServerSerializer(data=request.data)
    if serializer.is_valid():
        server = serializer.validated_data['server']

        # 获取或创建用户服务区记录
        user_server, created = UserServer.objects.get_or_create(
            user=request.user,
            defaults={
                'username': request.user.username,
                'server': server
            }
        )

        # 如果记录已存在，更新服务区
        if not created:
            user_server.server = server
            user_server.save()

        response_serializer = UserServerSerializer(user_server)
        return Response({
            'success': True,
            'message': '服务区设置成功',
            'data': response_serializer.data
        })
    return Response({
        'success': False,
        'message': '数据验证失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_result(
    key_func=lambda request: CacheKeyManager.search_users(
        request.user.user_server.server if hasattr(request.user, 'user_server') else 'a',
        request.GET.get('keyword', '')
    ),
    timeout=CacheTimeouts.SEARCH_USERS
)
def search_users(request):
    """搜索同服务区用户"""
    # 检查并自动设置默认服务区
    user_server, created = UserServer.objects.get_or_create(
        user=request.user,
        defaults={
            'username': request.user.username,
            'server': 'a'
        }
    )

    # 如果未设置服务区且未指定，默认设为a区
    if not request.user.username == user_server.username:
        user_server.username = request.user.username
        user_server.save()

    keyword = request.GET.get('keyword', '')

    # 搜索同服务区的用户
    users = User.objects.filter(
        user_server__server=user_server.server
    ).exclude(id=request.user.id)

    if keyword:
        users = users.filter(username__icontains=keyword)

    # 准备响应数据
    user_list = []
    for user in users[:20]:  # 限制返回数量
        user_list.append({
            'id': user.id,
            'username': user.username,
        })

    response_serializer = UserServerSerializer(user_server)
    return Response({
        'success': True,
        'message': '搜索成功',
        'data': {
            'current_user_server': response_serializer.data,
            'users': user_list
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invitation(request):
    """创建邀请"""
    serializer = CreateInvitationSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        invitee_username = serializer.validated_data['invitee_username']

        try:
            invitee = User.objects.get(username=invitee_username)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': '被邀请用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 检查是否已存在邀请
        try:
            invitation = Invitation.objects.get(
                inviter=request.user,
                invitee=invitee
            )
            return Response({
                'success': False,
                'message': '已经邀请过该用户'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Invitation.DoesNotExist:
            pass

        # 创建邀请
        invitation = Invitation.objects.create(
            inviter=request.user,
            inviter_username=request.user.username,
            invitee=invitee,
            invitee_username=invitee.username
        )

        response_serializer = InvitationSerializer(invitation)
        return Response({
            'success': True,
            'message': '邀请创建成功',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'message': '创建邀请失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_invitation(request, invitation_id):
    """确认邀请"""
    # 首先检查邀请记录是否存在
    try:
        invitation = Invitation.objects.get(id=invitation_id)
    except Invitation.DoesNotExist:
        return Response({
            'success': False,
            'message': '邀请不存在或已被删除'
        }, status=status.HTTP_404_NOT_FOUND)

    # 检查当前用户是否为被邀请者
    if invitation.invitee != request.user:
        return Response({
            'success': False,
            'message': '您没有权限确认此邀请'
        }, status=status.HTTP_403_FORBIDDEN)

    if invitation.is_confirmed:
        return Response({
            'success': False,
            'message': '邀请已被确认'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 确认邀请
    invitation.is_confirmed = True
    invitation.save()

    response_serializer = InvitationSerializer(invitation)
    return Response({
        'success': True,
        'message': '邀请确认成功',
        'data': response_serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_invitation(request, invitation_id):
    """删除邀请（第一次落子后）- 邀请者和被邀请者都可以删除"""
    try:
        # 允许邀请者或被邀请者删除邀请
        invitation = Invitation.objects.get(
            Q(id=invitation_id) &
            (Q(inviter=request.user) | Q(invitee=request.user))
        )
    except Invitation.DoesNotExist:
        return Response({
            'success': False,
            'message': '邀请不存在或您没有权限删除此邀请'
        }, status=status.HTTP_404_NOT_FOUND)

    invitation.delete()

    return Response({
        'success': True,
        'message': '邀请已删除'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_result(
    key_func=lambda request: CacheKeyManager.invitations_sent(request.user.id),
    timeout=CacheTimeouts.INVITATIONS
)
def list_sent_invitations(request):
    """列出发出的邀请"""
    invitations = Invitation.objects.filter(
        inviter=request.user
    ).order_by('-created_at')

    serializer = InvitationSerializer(invitations, many=True)
    return Response({
        'success': True,
        'message': '获取成功',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_result(
    key_func=lambda request: CacheKeyManager.invitations_received(request.user.id),
    timeout=CacheTimeouts.INVITATIONS
)
def list_received_invitations(request):
    """列出收到的邀请"""
    invitations = Invitation.objects.filter(
        invitee=request.user
    ).order_by('-created_at')

    serializer = InvitationSerializer(invitations, many=True)
    return Response({
        'success': True,
        'message': '获取成功',
        'data': serializer.data
    })
