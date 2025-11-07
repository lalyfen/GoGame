"""
缓存管理模块

提供统一的缓存键命名和管理功能，以及缓存装饰器。
"""

import json
import logging
from functools import wraps
from typing import Any, Optional, Union, Callable
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Model
from datetime import timedelta

logger = logging.getLogger('cache')

class CacheKeyManager:
    """缓存键管理器"""

    PREFIX = "gogame"

    @classmethod
    def get_key(cls, *parts) -> str:
        """生成缓存键"""
        return f"{cls.PREFIX}:" + ":".join(str(part) for part in parts)

    @classmethod
    def game_list(cls, user_id: Optional[int] = None, status: Optional[str] = None) -> str:
        """游戏列表缓存键"""
        parts = ['games', 'list']
        if user_id:
            parts.append(f'user_{user_id}')
        if status:
            parts.append(f'status_{status}')
        return cls.get_key(*parts)

    @classmethod
    def game_detail(cls, game_id: int) -> str:
        """游戏详情缓存键"""
        return cls.get_key('game', 'detail', game_id)

    @classmethod
    def game_intersections(cls, game_id: int) -> str:
        """游戏棋子位置缓存键"""
        return cls.get_key('game', 'intersections', game_id)

    @classmethod
    def user_profile(cls, user_id: int) -> str:
        """用户资料缓存键"""
        return cls.get_key('user', 'profile', user_id)

    @classmethod
    def user_server(cls, user_id: int) -> str:
        """用户服务区缓存键"""
        return cls.get_key('user', 'server', user_id)

    @classmethod
    def user_stats(cls, user_id: int) -> str:
        """用户统计缓存键"""
        return cls.get_key('user', 'stats', user_id)

    @classmethod
    def invitations_sent(cls, user_id: int) -> str:
        """发出的邀请缓存键"""
        return cls.get_key('invitations', 'sent', user_id)

    @classmethod
    def invitations_received(cls, user_id: int) -> str:
        """收到的邀请缓存键"""
        return cls.get_key('invitations', 'received', user_id)

    @classmethod
    def search_users(cls, server: str, query: str) -> str:
        """用户搜索缓存键"""
        return cls.get_key('search', 'users', server, query.lower())

    @classmethod
    def latest_move(cls, game_id: int) -> str:
        """最新落子缓存键"""
        return cls.get_key('game', 'latest_move', game_id)

    @classmethod
    def player_color(cls, game_id: int, user_id: int) -> str:
        """玩家角色缓存键"""
        return cls.get_key('game', 'player_color', game_id, user_id)

class CacheTimeouts:
    """缓存超时时间配置（秒）"""

    # 游戏相关
    GAME_LIST = 15 * 60  # 15分钟
    GAME_DETAIL = 20 * 60  # 20分钟
    GAME_INTERSECTIONS = 15 * 60  # 15分钟
    LATEST_MOVE = 10 * 60  # 10分钟
    PLAYER_COLOR = 30 * 60  # 30分钟

    # 用户相关
    USER_PROFILE = 30 * 60  # 30分钟
    USER_SERVER = 30 * 60  # 30分钟
    USER_STATS = 25 * 60  # 25分钟

    # 邀请相关
    INVITATIONS = 10 * 60  # 10分钟
    SEARCH_USERS = 5 * 60  # 5分钟

def cache_result(key_func: Callable, timeout: int = None, serialize: bool = True):
    """
    缓存结果装饰器

    Args:
        key_func: 生成缓存键的函数
        timeout: 缓存超时时间（秒）
        serialize: 是否序列化结果
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 生成缓存键
            cache_key = key_func(*args, **kwargs)

            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                if serialize:
                    try:
                        result = json.loads(result)
                    except (json.JSONDecodeError, TypeError):
                        pass
                return result

            # 缓存未命中，执行函数
            logger.debug(f"Cache miss for key: {cache_key}")
            result = func(*args, **kwargs)

            # 存储到缓存
            try:
                if timeout is None:
                    final_timeout = getattr(CacheTimeouts, func.__name__.upper(), 300)
                else:
                    final_timeout = timeout

                cache_value = json.dumps(result, default=str) if serialize else result
                cache.set(cache_key, cache_value, final_timeout)
                logger.debug(f"Cached result for key: {cache_key}, timeout: {final_timeout}s")
            except Exception as e:
                logger.error(f"Failed to cache result for key {cache_key}: {e}")

            return result

        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str) -> int:
    """
    根据模式失效缓存

    Args:
        pattern: 缓存键模式（支持通配符）

    Returns:
        失效的缓存键数量
    """
    try:
        if hasattr(cache, 'delete_pattern'):
            # Redis支持模式删除
            count = cache.delete_pattern(f"{CacheKeyManager.PREFIX}:{pattern}")
            logger.info(f"Invalidated {count} cache keys matching pattern: {pattern}")
            return count
        else:
            # 其他缓存后端，遍历所有键
            # 注意：这种方法效率较低，仅适用于本地开发
            logger.warning("Cache backend does not support pattern deletion")
            return 0
    except Exception as e:
        logger.error(f"Failed to invalidate cache pattern {pattern}: {e}")
        return 0

def invalidate_game_cache(game_id: int, user_id: int = None):
    """失效游戏相关的缓存"""
    patterns = [
        f"games:list:*",  # 游戏列表
        f"game:detail:{game_id}",  # 游戏详情
        f"game:intersections:{game_id}",  # 棋子位置
        f"game:latest_move:{game_id}",  # 最新落子
        f"game:player_color:{game_id}:*",  # 玩家角色
    ]

    if user_id:
        patterns.extend([
            f"user:stats:{user_id}",  # 用户统计
            f"games:list:user_{user_id}:*",  # 用户的游戏列表
        ])

    total_invalidated = 0
    for pattern in patterns:
        total_invalidated += invalidate_cache_pattern(pattern)

    logger.info(f"Invalidated {total_invalidated} game-related cache entries for game {game_id}")

def invalidate_user_cache(user_id: int):
    """失效用户相关的缓存"""
    patterns = [
        f"user:profile:{user_id}",  # 用户资料
        f"user:server:{user_id}",  # 用户服务区
        f"user:stats:{user_id}",  # 用户统计
        f"invitations:sent:{user_id}",  # 发出的邀请
        f"invitations:received:{user_id}",  # 收到的邀请
        f"games:list:user_{user_id}:*",  # 用户的游戏列表
    ]

    total_invalidated = 0
    for pattern in patterns:
        total_invalidated += invalidate_cache_pattern(pattern)

    logger.info(f"Invalidated {total_invalidated} user-related cache entries for user {user_id}")

def invalidate_invitation_cache(inviter_id: int, invitee_id: int):
    """失效邀请相关的缓存"""
    patterns = [
        f"invitations:sent:{inviter_id}",  # 发出的邀请
        f"invitations:received:{invitee_id}",  # 收到的邀请
    ]

    total_invalidated = 0
    for pattern in patterns:
        total_invalidated += invalidate_cache_pattern(pattern)

    logger.info(f"Invalidated {total_invalidated} invitation-related cache entries")

class CacheStats:
    """缓存统计"""

    @staticmethod
    def get_redis_info() -> dict:
        """获取Redis信息"""
        try:
            import redis
            redis_client = cache.client.get_client()
            info = redis_client.info()
            return {
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
            }
        except Exception as e:
            logger.error(f"Failed to get Redis info: {e}")
            return {}

    @staticmethod
    def get_hit_rate() -> float:
        """计算缓存命中率"""
        try:
            info = CacheStats.get_redis_info()
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            return (hits / total * 100) if total > 0 else 0.0
        except:
            return 0.0

# 缓存装饰器示例用法
@cache_result(
    key_func=lambda game_id: CacheKeyManager.game_detail(game_id),
    timeout=CacheTimeouts.GAME_DETAIL
)
def get_game_detail_cached(game_id: int):
    """获取游戏详情（缓存版本）"""
    from datab.models import Game
    try:
        game = Game.objects.select_related('player1', 'player2').get(id=game_id)
        return {
            'id': game.id,
            'player1': {'id': game.player1.id, 'username': game.player1.username},
            'player2': {'id': game.player2.id, 'username': game.player2.username},
            'winner': game.winner,
            'score_black': float(game.score_black),
            'score_white': float(game.score_white),
            'komi': float(game.komi),
            'is_completed': game.is_completed,
            'created_at': game.created_at.isoformat(),
            'updated_at': game.updated_at.isoformat(),
        }
    except Game.DoesNotExist:
        return None