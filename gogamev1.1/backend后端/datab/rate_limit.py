import time
import hashlib
from django.db import models
from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps
from rest_framework import status


class RateLimitExceeded(Exception):
    """频率限制异常"""
    pass


def rate_limit(max_requests=10, window_seconds=60, key_func=None):
    """
    频率限制装饰器

    Args:
        max_requests: 时间窗口内最大请求数
        window_seconds: 时间窗口（秒）
        key_func: 自定义key生成函数，默认使用用户ID
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # 生成缓存key
            if key_func:
                cache_key = key_func(request)
            else:
                # 默认使用用户ID作为key
                user_id = getattr(request.user, 'id', 'anonymous')
                view_name = f"{view_func.__module__}.{view_func.__name__}"
                cache_key = f"rate_limit:{hashlib.md5(f'{user_id}:{view_name}'.encode()).hexdigest()}"

            # 获取当前计数
            current_count = cache.get(cache_key, 0)

            # 检查是否超过限制
            if current_count >= max_requests:
                return JsonResponse({
                    "detail": f"请求过于频繁，请在{window_seconds}秒后再试",
                    "limit": max_requests,
                    "window": window_seconds
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # 增加计数
            cache.set(cache_key, current_count + 1, window_seconds)

            return view_func(request, *args, **kwargs)

        return wrapped_view
    return decorator


def game_creation_limit():
    """
    游戏创建频率限制
    每用户每分钟最多创建1个游戏，每小时最多创建5个游戏
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(self, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return view_func(self, request, *args, **kwargs)

            user_id = request.user.id

            # 每分钟限制
            minute_key = f"game_limit:minute:{user_id}"
            minute_count = cache.get(minute_key, 0)
            if minute_count >= 1:
                return JsonResponse({
                    "detail": "游戏创建过于频繁，请等待1分钟后再试",
                    "type": "minute_limit",
                    "limit": 1,
                    "window": 60
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # 每小时限制
            hour_key = f"game_limit:hour:{user_id}"
            hour_count = cache.get(hour_key, 0)
            if hour_count >= 5:
                return JsonResponse({
                    "detail": "游戏创建过于频繁，每小时最多创建5个游戏",
                    "type": "hour_limit",
                    "limit": 5,
                    "window": 3600
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # 设置计数
            cache.set(minute_key, minute_count + 1, 60)
            cache.set(hour_key, hour_count + 1, 3600)

            return view_func(self, request, *args, **kwargs)

        return wrapped_view
    return decorator


def move_creation_limit():
    """
    落子操作频率限制
    每游戏每秒最多1个操作
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(self, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return view_func(self, request, *args, **kwargs)

            # 从请求数据中获取游戏ID
            game_id = request.data.get('game')
            if not game_id:
                return JsonResponse({
                    "detail": "必须指定游戏ID"
                }, status=status.HTTP_400_BAD_REQUEST)

            user_id = request.user.id
            move_key = f"move_limit:{game_id}:{user_id}"

            # 检查最近操作
            last_move_time = cache.get(move_key)
            current_time = int(time.time())

            if last_move_time and current_time - last_move_time < 1:
                return JsonResponse({
                    "detail": "落子过于频繁，请稍后再试",
                    "type": "move_limit",
                    "min_interval": 1
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # 记录当前操作时间
            cache.set(move_key, current_time, 10)

            return view_func(self, request, *args, **kwargs)

        return wrapped_view
    return decorator


def check_game_limits():
    """
    检查用户游戏数量限制
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(self, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return view_func(self, request, *args, **kwargs)

            from .models import Game

            user = request.user

            # 检查总游戏数量限制（最多50个）
            total_games = Game.objects.filter(
                models.Q(player1=user) | models.Q(player2=user)
            ).distinct().count()

            if total_games >= 50:
                return JsonResponse({
                    "detail": "您已达到最大游戏数量限制（50个）",
                    "type": "total_limit",
                    "limit": 50
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # 检查进行中游戏数量限制（最多10个）
            active_games = Game.objects.filter(
                models.Q(player1=user) | models.Q(player2=user),
                winner__in=['black', 'white']  # 假设'draw'表示未结束，实际逻辑可能需要调整
            ).distinct().count()

            if active_games >= 10:
                return JsonResponse({
                    "detail": "您有太多进行中的游戏（最多10个）",
                    "type": "active_limit",
                    "limit": 10
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # 检查用户间对局冲突 - 确保相同两个用户间没有未完成的对局
            try:
                # 获取请求数据中的玩家信息
                player1_id = request.data.get('player1')
                player2_id = request.data.get('player2')

                if player1_id and player2_id:
                    # 检查这两个用户之间是否已有未完成的对局
                    # 未完成的对局判断标准：winner为空字符串或null
                    conflict_games = Game.objects.filter(
                        models.Q(player1_id=player1_id, player2_id=player2_id) |
                        models.Q(player1_id=player2_id, player2_id=player1_id)
                    ).filter(
                        models.Q(winner__isnull=True) | models.Q(winner='')
                    ).distinct()

                    if conflict_games.exists():
                        return JsonResponse({
                            "detail": "这两位用户之间已有未完成的对局，请先完成现有对局",
                            "type": "user_conflict",
                            "existing_game_id": conflict_games.first().id
                        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            except Exception as e:
                # 如果解析请求数据出错，记录日志但不阻止请求继续
                print(f"检查用户间对局冲突时出错: {e}")

            return view_func(self, request, *args, **kwargs)

        return wrapped_view
    return decorator