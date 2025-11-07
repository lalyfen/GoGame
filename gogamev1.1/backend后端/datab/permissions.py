from rest_framework import permissions


class IsGameParticipant(permissions.BasePermission):
    """
    自定义权限类，只允许游戏参与者（黑棋或白棋玩家）访问游戏信息
    """

    def has_object_permission(self, request, view, obj):
        # 必须是认证用户
        if not request.user or not request.user.is_authenticated:
            return False

        # 检查用户是否是游戏的参与者
        return obj.player1 == request.user or obj.player2 == request.user


class IsGameParticipantOrReadOnly(permissions.BasePermission):
    """
    自定义权限类，允许游戏参与者进行读写操作，其他用户只读（如果需要公开访问）
    注意：根据业务需求，可能不需要这个权限类，因为游戏信息通常是私有的
    """

    def has_object_permission(self, request, view, obj):
        # 必须是认证用户
        if not request.user or not request.user.is_authenticated:
            return False

        # 安全方法（GET, HEAD, OPTIONS）允许游戏参与者访问
        if request.method in permissions.SAFE_METHODS:
            return obj.player1 == request.user or obj.player2 == request.user

        # 写方法只允许游戏参与者
        return obj.player1 == request.user or obj.player2 == request.user


class IsIntersectionGameParticipant(permissions.BasePermission):
    """
    自定义权限类，只允许游戏参与者访问该游戏中的棋子信息
    """

    def has_object_permission(self, request, view, obj):
        # 必须是认证用户
        if not request.user or not request.user.is_authenticated:
            return False

        # 检查用户是否是棋子所属游戏的参与者
        game = obj.game
        return game.player1 == request.user or game.player2 == request.user