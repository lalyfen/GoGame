# datab/urls.py - 数据相关URL配置
from django.urls import path
from .views import (
	GameListCreateView,
	GameDetailView,
	IntersectionListCreateView,
	IntersectionDetailView,
	IncompleteGamesView,
	CompletedGamesView,
	LatestMoveView,
	PlayerColorView,
	EndGameView,
	SetKomiView,
	ValidatedMoveView,
)

urlpatterns = [
	path('games/', GameListCreateView.as_view(), name='game-list-create'),  # 游戏列表创建
	path('games/<int:pk>/', GameDetailView.as_view(), name='game-detail'),  # 游戏详情
	path('games/incomplete/', IncompleteGamesView.as_view(), name='incomplete-games'),  # 未终局对局列表
	path('games/completed/', CompletedGamesView.as_view(), name='completed-games'),  # 已完棋局列表
	path('games/<int:game_id>/latest-move/', LatestMoveView.as_view(), name='latest-move'),  # 最新落子颜色查询
	path('games/<int:game_id>/player-color/', PlayerColorView.as_view(), name='player-color'),  # 玩家角色查询
	path('games/<int:game_id>/end-game/', EndGameView.as_view(), name='end-game'),  # 标记对局终局
	path('games/<int:game_id>/set-komi/', SetKomiView.as_view(), name='set-komi'),  # 设置贴目数
	path('games/validated-move/', ValidatedMoveView.as_view(), name='validated-move'),  # 验证落子创建
	path('intersections/', IntersectionListCreateView.as_view(), name='intersection-list-create'),  # 棋子位置列表创建
	path('intersections/<int:pk>/', IntersectionDetailView.as_view(), name='intersection-detail'),  # 棋子位置详情
]
