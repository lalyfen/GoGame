from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserServer, Invitation


class UserServerSerializer(serializers.ModelSerializer):
    """用户服务区序列化器"""
    class Meta:
        model = UserServer
        fields = ['username', 'server', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class InvitationSerializer(serializers.ModelSerializer):
    """邀请序列化器"""
    inviter_username = serializers.CharField(source='inviter.username', read_only=True)
    invitee_username = serializers.CharField(source='invitee.username', read_only=True)

    class Meta:
        model = Invitation
        fields = [
            'id',
            'inviter',
            'inviter_username',
            'invitee',
            'invitee_username',
            'created_at',
            'is_confirmed'
        ]
        read_only_fields = ['id', 'inviter', 'inviter_username', 'invitee', 'invitee_username', 'created_at', 'is_confirmed']


class CreateInvitationSerializer(serializers.Serializer):
    """创建邀请序列化器"""
    invitee_username = serializers.CharField(max_length=150)

    def validate_invitee_username(self, value):
        """验证被邀请者用户名是否存在"""
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("用户不存在")
        return value

    def validate(self, data):
        """验证邀请者不能邀请自己"""
        inviter_username = self.context['request'].user.username
        invitee_username = data['invitee_username']
        if inviter_username == invitee_username:
            raise serializers.ValidationError("不能邀请自己")
        return data


class SetServerSerializer(serializers.Serializer):
    """设置服务区序列化器"""
    server = serializers.CharField(max_length=1)

    def validate_server(self, value):
        """验证服务区是否为a或b"""
        if value not in ['a', 'b']:
            raise serializers.ValidationError("服务区只能为 'a' 或 'b'")
        return value


class SearchUsersSerializer(serializers.Serializer):
    """搜索用户序列化器"""
    keyword = serializers.CharField(max_length=150, required=False, allow_blank=True)
