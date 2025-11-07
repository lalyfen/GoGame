from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserServer(models.Model):
    """用户服务区模型 - 记录用户所在的服务区和用户名"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_server')
    username = models.CharField(max_length=150, db_index=True)
    server = models.CharField(
        max_length=1,
        choices=[('a', 'A区'), ('b', 'B区')],
        default='a',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invitation_userserver'  # 明确指定表名
        indexes = [
            models.Index(fields=['server', 'created_at']),  # 按服务区和创建时间查询
            models.Index(fields=['username']),  # 用户名索引
            models.Index(fields=['server']),  # 服务区索引
        ]
        constraints = [
			# 暂时注释掉约束，避免迁移问题
			# models.CheckConstraint(
			# 	check=models.Q(server__in=['a', 'b']),
			# 	name='valid_server_values'
			# ),
		]
        verbose_name = '用户服务区'
        verbose_name_plural = '用户服务区'

    def __str__(self):
        return f'{self.username} - {self.server}区'


class Invitation(models.Model):
    """邀请模型 - 记录邀请信息"""
    inviter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        db_index=True
    )
    inviter_username = models.CharField(max_length=150, db_index=True)
    invitee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_invitations',
        db_index=True
    )
    invitee_username = models.CharField(max_length=150, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_confirmed = models.BooleanField(default=False, db_index=True)

    # 添加确认时间字段
    confirmed_at = models.DateTimeField(null=True, blank=True, db_index=True)  # 确认时间

    class Meta:
        db_table = 'invitation_invitation'  # 明确指定表名
        indexes = [
            models.Index(fields=['inviter', 'created_at']),  # 发出邀请的时间索引
            models.Index(fields=['invitee', 'created_at']),  # 收到邀请的时间索引
            models.Index(fields=['inviter', 'is_confirmed']),  # 邀请者的确认状态
            models.Index(fields=['invitee', 'is_confirmed']),  # 被邀请者的确认状态
            models.Index(fields=['is_confirmed', 'created_at']),  # 按确认状态和时间查询
            models.Index(fields=['created_at']),  # 创建时间索引
        ]
        constraints = [
			# 暂时注释掉约束，避免迁移问题
			# models.CheckConstraint(
			# 	check=~models.Q(inviter=models.F('invitee')),  # 不能邀请自己
			# 	name='cannot_invite_self'
			# ),
		]
        verbose_name = '邀请'
        verbose_name_plural = '邀请'
        # 一个用户不能重复邀请同一个用户
        unique_together = ('inviter', 'invitee')

    def __str__(self):
        return f'{self.inviter_username} -> {self.invitee_username} ({self.created_at})'
