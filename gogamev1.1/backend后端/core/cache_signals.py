"""
缓存信号处理器

使用Django信号在数据更新时自动失效相关缓存。
"""

import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from core.cache_manager import (
    invalidate_game_cache,
    invalidate_user_cache,
    invalidate_invitation_cache,
    CacheKeyManager,
    invalidate_cache_pattern
)
from datab.models import Game, Intersection
from invitation.models import UserServer, Invitation

logger = logging.getLogger('cache.signals')

# 游戏相关的信号处理

@receiver(post_save, sender=Game)
def game_post_save(sender, instance, created, **kwargs):
    """游戏保存后失效相关缓存"""
    try:
        # 失效游戏相关的缓存
        invalidate_game_cache(instance.id)

        # 失效玩家相关的缓存
        invalidate_user_cache(instance.player1_id)
        invalidate_user_cache(instance.player2_id)

        # 失效游戏列表缓存
        invalidate_cache_pattern("games:list:*")

        logger.info(f"Invalidated cache for game {instance.id} (created={created})")
    except Exception as e:
        logger.error(f"Failed to invalidate cache for game {instance.id}: {e}")

@receiver(pre_save, sender=Game)
def game_pre_save(sender, instance, **kwargs):
    """游戏保存前检查是否有状态变化"""
    try:
        if instance.pk:  # 如果是更新操作
            old_game = Game.objects.get(pk=instance.pk)

            # 检查游戏完成状态是否有变化
            old_completed = getattr(old_game, 'is_completed', False)
            new_completed = getattr(instance, 'is_completed', False)

            if old_completed != new_completed:
                # 游戏完成状态变化，额外失效游戏列表
                invalidate_cache_pattern("games:list:*")
                logger.info(f"Game {instance.id} completion status changed: {old_completed} -> {new_completed}")
    except Game.DoesNotExist:
        pass  # 新创建的游戏
    except Exception as e:
        logger.error(f"Error in game_pre_save: {e}")

# 落子相关的信号处理

@receiver(post_save, sender=Intersection)
def intersection_post_save(sender, instance, created, **kwargs):
    """落子保存后失效相关缓存"""
    try:
        game_id = instance.game_id

        # 失效游戏相关缓存
        invalidate_game_cache(game_id)

        # 失效落子位置缓存
        cache_key = CacheKeyManager.game_intersections(game_id)
        invalidate_cache_pattern(f"game:intersections:{game_id}")

        # 失效最新落子缓存
        cache_key = CacheKeyManager.latest_move(game_id)
        invalidate_cache_pattern(f"game:latest_move:{game_id}")

        logger.info(f"Invalidated cache for intersection in game {game_id} (created={created})")
    except Exception as e:
        logger.error(f"Failed to invalidate cache for intersection: {e}")

@receiver(post_delete, sender=Intersection)
def intersection_post_delete(sender, instance, **kwargs):
    """落子删除后失效相关缓存"""
    try:
        game_id = instance.game_id

        # 失效游戏相关缓存
        invalidate_game_cache(game_id)

        # 失效落子位置缓存
        invalidate_cache_pattern(f"game:intersections:{game_id}")

        # 失效最新落子缓存
        invalidate_cache_pattern(f"game:latest_move:{game_id}")

        logger.info(f"Invalidated cache for deleted intersection in game {game_id}")
    except Exception as e:
        logger.error(f"Failed to invalidate cache for deleted intersection: {e}")

# 用户相关的信号处理

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """用户保存后失效相关缓存"""
    try:
        user_id = instance.id

        # 失效用户相关缓存
        invalidate_user_cache(user_id)

        # 失效搜索用户缓存
        invalidate_cache_pattern("search:users:*")

        logger.info(f"Invalidated cache for user {user_id} (created={created})")
    except Exception as e:
        logger.error(f"Failed to invalidate cache for user {instance.id}: {e}")

# 用户服务区相关的信号处理

@receiver(post_save, sender=UserServer)
def user_server_post_save(sender, instance, created, **kwargs):
    """用户服务区保存后失效相关缓存"""
    try:
        user_id = instance.user_id

        # 失效用户服务区缓存
        cache_key = CacheKeyManager.user_server(user_id)
        cache_key_pattern = f"user:server:{user_id}"
        invalidate_cache_pattern(cache_key_pattern)

        # 失效搜索用户缓存
        invalidate_cache_pattern(f"search:users:{instance.server}:*")

        logger.info(f"Invalidated cache for user server {user_id} (created={created})")
    except Exception as e:
        logger.error(f"Failed to invalidate cache for user server: {e}")

@receiver(post_delete, sender=UserServer)
def user_server_post_delete(sender, instance, **kwargs):
    """用户服务区删除后失效相关缓存"""
    try:
        user_id = instance.user_id

        # 失效用户服务区缓存
        invalidate_cache_pattern(f"user:server:{user_id}")

        # 失效搜索用户缓存
        invalidate_cache_pattern(f"search:users:{instance.server}:*")

        logger.info(f"Invalidated cache for deleted user server {user_id}")
    except Exception as e:
        logger.error(f"Failed to invalidate cache for deleted user server: {e}")

# 邀请相关的信号处理

@receiver(post_save, sender=Invitation)
def invitation_post_save(sender, instance, created, **kwargs):
    """邀请保存后失效相关缓存"""
    try:
        inviter_id = instance.inviter_id
        invitee_id = instance.invitee_id

        # 失效邀请相关缓存
        invalidate_invitation_cache(inviter_id, invitee_id)

        logger.info(f"Invalidated cache for invitation {inviter_id} -> {invitee_id} (created={created})")
    except Exception as e:
        logger.error(f"Failed to invalidate cache for invitation: {e}")

@receiver(post_delete, sender=Invitation)
def invitation_post_delete(sender, instance, **kwargs):
    """邀请删除后失效相关缓存"""
    try:
        inviter_id = instance.inviter_id
        invitee_id = instance.invitee_id

        # 失效邀请相关缓存
        invalidate_invitation_cache(inviter_id, invitee_id)

        logger.info(f"Invalidated cache for deleted invitation {inviter_id} -> {invitee_id}")
    except Exception as e:
        logger.error(f"Failed to invalidate cache for deleted invitation: {e}")

# 批量操作缓存失效辅助函数

def invalidate_bulk_game_cache(game_ids):
    """批量失效游戏缓存"""
    try:
        for game_id in game_ids:
            invalidate_game_cache(game_id)

        # 同时失效游戏列表缓存
        invalidate_cache_pattern("games:list:*")

        logger.info(f"Invalidated cache for {len(game_ids)} games")
    except Exception as e:
        logger.error(f"Failed to invalidate bulk game cache: {e}")

def invalidate_bulk_user_cache(user_ids):
    """批量失效用户缓存"""
    try:
        for user_id in user_ids:
            invalidate_user_cache(user_id)

        # 同时失效搜索用户缓存
        invalidate_cache_pattern("search:users:*")

        logger.info(f"Invalidated cache for {len(user_ids)} users")
    except Exception as e:
        logger.error(f"Failed to invalidate bulk user cache: {e}")

# 缓存预热函数

def warm_up_game_cache(game_id):
    """预热游戏缓存"""
    try:
        from core.cache_manager import get_game_detail_cached

        # 预热游戏详情缓存
        get_game_detail_cached(game_id)

        logger.info(f"Warmed up cache for game {game_id}")
    except Exception as e:
        logger.error(f"Failed to warm up cache for game {game_id}: {e}")

def warm_up_user_cache(user_id):
    """预热用户缓存"""
    try:
        # 这里可以添加预热用户缓存的逻辑
        # 例如：预加载用户资料、用户统计等

        logger.info(f"Warmed up cache for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to warm up cache for user {user_id}: {e}")