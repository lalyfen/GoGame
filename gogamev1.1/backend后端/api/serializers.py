# api/serializers.py - 认证相关序列化器
from django.contrib.auth.models import User
from rest_framework import serializers
from invitation.models import UserServer

class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器 - 用于处理用户注册数据的验证和创建"""
    class Meta:
        model = User
        fields = ('username', 'password', 'email')  # 包含用户名、密码和邮箱字段
        extra_kwargs = {
            'password': {'write_only': True},  # 密码字段只写，不返回
            'email': {'required': True}  # 邮箱字段为必填
        }

    def create(self, validated_data):
        """创建用户实例"""
        user = User.objects.create_user(
            validated_data['username'],  # 用户名
            validated_data['email'],     # 邮箱
            validated_data['password']   # 密码
        )

        # 自动创建用户服务区记录，默认为a区
        UserServer.objects.create(
            user=user,
            username=user.username,
            server='a'
        )

        return user