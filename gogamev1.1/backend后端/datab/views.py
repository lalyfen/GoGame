from django.db import models
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Game, Intersection
from .serializers import GameSerializer, IntersectionSerializer
from .permissions import IsGameParticipant, IsIntersectionGameParticipant
from .rate_limit import game_creation_limit, check_game_limits, move_creation_limit
from .logging_decorators import log_api_access, log_database_operation, get_client_ip

# 缓存相关导入
from core.cache_manager import (
    CacheKeyManager,
    CacheTimeouts,
    cache_result,
    invalidate_game_cache,
    invalidate_user_cache
)


class GameListCreateView(generics.ListCreateAPIView):
	"""游戏列表创建视图 - 提供游戏的列表查询和创建功能"""
	serializer_class = GameSerializer
	permission_classes = [IsAuthenticated]  # 需要登录认证

	def get_queryset(self):
		"""
		只返回当前用户参与的游戏（作为黑棋或白棋玩家）
		"""
		if not self.request.user.is_authenticated:
			return Game.objects.none()
		return Game.objects.filter(
			models.Q(player1=self.request.user) | models.Q(player2=self.request.user)
		).order_by('-created_at').distinct()  # 按创建时间降序排列，确保去重

	@log_api_access("游戏列表访问")
	@cache_result(
		key_func=lambda self: CacheKeyManager.game_list(
			user_id=self.request.user.id if self.request.user.is_authenticated else None,
			status=self.request.query_params.get('status', '')
		),
		timeout=CacheTimeouts.GAME_LIST
	)
	def get(self, request, *args, **kwargs):
		"""获取游戏列表"""
		return super().get(request, *args, **kwargs)

	@log_api_access("游戏创建")
	@log_database_operation("Game", "create")
	@game_creation_limit()
	@check_game_limits()
	def post(self, request, *args, **kwargs):
		"""创建新游戏"""
		# 创建成功后失效相关缓存
		response = super().post(request, *args, **kwargs)

		if response.status_code == status.HTTP_201_CREATED:
			# 失效用户游戏列表缓存
			if request.user.is_authenticated:
				invalidate_user_cache(request.user.id)

				# 失效游戏列表缓存
				from core.cache_manager import invalidate_cache_pattern
				invalidate_cache_pattern("games:list:*")

		return response


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
	"""游戏详情视图 - 提供单个游戏的查询、更新和删除功能"""
	queryset = Game.objects.all()
	serializer_class = GameSerializer
	permission_classes = [IsAuthenticated, IsGameParticipant]  # 需要登录认证且是游戏参与者

	@log_api_access("游戏详情访问")
	@log_database_operation("Game", "retrieve")
	@cache_result(
		key_func=lambda self, game_id: CacheKeyManager.game_detail(game_id),
		timeout=CacheTimeouts.GAME_DETAIL
	)
	def get(self, request, *args, **kwargs):
		"""获取游戏详情"""
		return super().get(request, *args, **kwargs)

	@log_api_access("游戏更新")
	@log_database_operation("Game", "update")
	def put(self, request, *args, **kwargs):
		"""完全更新游戏"""
		response = super().put(request, *args, **kwargs)
		if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
			# 更新成功后失效缓存
			game_id = kwargs.get('pk')
			if game_id:
				invalidate_game_cache(game_id)
		return response

	@log_api_access("游戏部分更新")
	@log_database_operation("Game", "update")
	def patch(self, request, *args, **kwargs):
		"""部分更新游戏"""
		response = super().patch(request, *args, **kwargs)
		if response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]:
			# 更新成功后失效缓存
			game_id = kwargs.get('pk')
			if game_id:
				invalidate_game_cache(game_id)
		return response

	@log_api_access("游戏删除")
	@log_database_operation("Game", "delete")
	def delete(self, request, *args, **kwargs):
		"""删除游戏"""
		game_id = kwargs.get('pk')
		# 先失效缓存再删除
		if game_id:
			invalidate_game_cache(game_id)
		return super().delete(request, *args, **kwargs)


class IntersectionListCreateView(generics.ListCreateAPIView):
	"""棋子交叉点列表创建视图 - 提供棋子位置的列表查询和创建功能"""
	serializer_class = IntersectionSerializer
	permission_classes = [IsAuthenticated]  # 需要登录认证

	def get_queryset(self):
		"""
		获取查询集，只返回用户参与的游戏中的棋子
		支持按游戏ID过滤，但只允许访问用户参与的游戏
		"""
		if not self.request.user.is_authenticated:
			return Intersection.objects.none()

		# 获取用户参与的游戏
		user_games = Game.objects.filter(
			models.Q(player1=self.request.user) | models.Q(player2=self.request.user)
		).distinct()

		qs = Intersection.objects.filter(game__in=user_games).order_by('placed_at', 'row', 'col')

		# 如果指定了游戏ID，进一步过滤并验证权限
		game_id = self.request.query_params.get('game')
		if game_id:
			# 验证用户是否有权访问该游戏
			try:
				game = Game.objects.get(
					models.Q(id=game_id) & (models.Q(player1=self.request.user) | models.Q(player2=self.request.user))
				)
				qs = qs.filter(game=game)
			except Game.DoesNotExist:
				# 如果用户无权访问该游戏，返回空查询集
				qs = Intersection.objects.none()

		return qs

	@log_api_access("棋子交叉点列表访问")
	@cache_result(
		key_func=lambda self: CacheKeyManager.game_intersections(
			self.request.query_params.get('game', 'all')
		),
		timeout=CacheTimeouts.GAME_INTERSECTIONS
	)
	def get(self, request, *args, **kwargs):
		"""获取棋子交叉点列表"""
		return super().get(request, *args, **kwargs)

	@log_api_access("棋子交叉点创建")
	@log_database_operation("Intersection", "create")
	@move_creation_limit()
	def post(self, request, *args, **kwargs):
		"""创建棋子交叉点"""
		# 验证用户是否有权在指定游戏中放置棋子
		game_id = request.data.get('game')
		if game_id:
			try:
				game = Game.objects.get(
					models.Q(id=game_id) & (models.Q(player1=self.request.user) | models.Q(player2=self.request.user))
				)
			except Game.DoesNotExist:
				return Response(
					{"detail": "您无权在该游戏中放置棋子。"},
					status=status.HTTP_403_FORBIDDEN
				)
		else:
			return Response(
				{"detail": "必须指定游戏ID。"},
				status=status.HTTP_400_BAD_REQUEST
			)

		# 创建落子并失效相关缓存
		response = super().post(request, *args, **kwargs)

		if response.status_code == status.HTTP_201_CREATED:
			# 失效游戏相关缓存
			invalidate_game_cache(game_id)

		return response


class IntersectionDetailView(generics.RetrieveUpdateDestroyAPIView):
	"""棋子交叉点详情视图 - 提供单个棋子位置的查询、更新和删除功能"""
	queryset = Intersection.objects.all()
	serializer_class = IntersectionSerializer
	permission_classes = [IsAuthenticated, IsIntersectionGameParticipant]  # 需要登录认证且是游戏参与者

	@log_api_access("棋子交叉点详情访问")
	@log_database_operation("Intersection", "retrieve")
	def get(self, request, *args, **kwargs):
		"""获取棋子交叉点详情"""
		return super().get(request, *args, **kwargs)

	@log_api_access("棋子交叉点更新")
	@log_database_operation("Intersection", "update")
	def put(self, request, *args, **kwargs):
		"""完全更新棋子交叉点"""
		return super().put(request, *args, **kwargs)

	@log_api_access("棋子交叉点部分更新")
	@log_database_operation("Intersection", "update")
	def patch(self, request, *args, **kwargs):
		"""部分更新棋子交叉点"""
		return super().patch(request, *args, **kwargs)

	@log_api_access("棋子交叉点删除")
	@log_database_operation("Intersection", "delete")
	def delete(self, request, *args, **kwargs):
		"""删除棋子交叉点"""
		return super().delete(request, *args, **kwargs)


class IncompleteGamesView(generics.ListAPIView):
	"""未终局对局列表视图 - 返回用户参与但未标记终局的对局"""
	serializer_class = GameSerializer
	permission_classes = [IsAuthenticated]  # 需要登录认证

	def get_queryset(self):
		"""
		只返回当前用户参与且未终局的对局（winner为null）
		"""
		if not self.request.user.is_authenticated:
			return Game.objects.none()
		return Game.objects.filter(
			models.Q(player1=self.request.user) | models.Q(player2=self.request.user),
			models.Q(winner__isnull=True) | models.Q(winner='')  # winner为null或空字符串表示未终局
		).order_by('-created_at').distinct()

	@log_api_access("未终局对局列表访问")
	def get(self, request, *args, **kwargs):
		"""获取未终局对局列表"""
		return super().get(request, *args, **kwargs)


class CompletedGamesView(generics.ListAPIView):
	"""已完棋局列表视图 - 返回用户参与且已结束的对局"""
	serializer_class = GameSerializer
	permission_classes = [IsAuthenticated]  # 需要登录认证

	def get_queryset(self):
		"""
		只返回当前用户参与且已终局的对局（winner不为null且不为空）
		"""
		if not self.request.user.is_authenticated:
			return Game.objects.none()
		return Game.objects.filter(
			models.Q(player1=self.request.user) | models.Q(player2=self.request.user),
			models.Q(winner__isnull=False) & ~models.Q(winner='')  # winner不为null且不为空字符串表示已终局
		).order_by('-updated_at').distinct()

	@log_api_access("已完棋局列表访问")
	def get(self, request, *args, **kwargs):
		"""获取已完棋局列表"""
		return super().get(request, *args, **kwargs)


class LatestMoveView(generics.GenericAPIView):
	"""最新落子颜色查询视图 - 查询某一对局中最新落子的颜色"""
	permission_classes = [IsAuthenticated, IsGameParticipant]  # 需要登录认证且是游戏参与者

	@log_api_access("最新落子查询")
	@cache_result(
		key_func=lambda self, game_id: CacheKeyManager.latest_move(game_id),
		timeout=CacheTimeouts.LATEST_MOVE
	)
	def get(self, request, *args, **kwargs):
		"""获取指定对局中最新落子的颜色"""
		game_id = self.kwargs.get('game_id')

		# 获取指定游戏的最新落子
		latest_intersection = Intersection.objects.filter(
			game_id=game_id
		).order_by('-placed_at').first()

		# 如果没有落子，返回白色；如果有落子，返回最新落子的颜色
		if latest_intersection:
			color = latest_intersection.color
			# 如果最新落子是空（理论上不应出现），返回白色
			if color == 'empty':
				color = 'white'
			return Response({"color": color})
		else:
			# 没有落子时返回白色
			return Response({"color": "white"})


class PlayerColorView(generics.GenericAPIView):
	"""玩家角色查询视图 - 查询用户在某一对局中是黑棋还是白棋玩家"""
	permission_classes = [IsAuthenticated, IsGameParticipant]  # 需要登录认证且是游戏参与者

	@log_api_access("玩家角色查询")
	@cache_result(
		key_func=lambda self, game_id: CacheKeyManager.player_color(
			game_id, self.request.user.id if self.request.user.is_authenticated else 0
		),
		timeout=CacheTimeouts.PLAYER_COLOR
	)
	def get(self, request, *args, **kwargs):
		"""获取当前用户在指定对局中的角色（黑棋或白棋）"""
		game_id = self.kwargs.get('game_id')

		try:
			game = Game.objects.get(id=game_id)
		except Game.DoesNotExist:
			return Response(
				{"detail": "游戏不存在。"},
				status=status.HTTP_404_NOT_FOUND
			)

		# 判断当前用户是黑棋（player1）还是白棋（player2）
		if game.player1 == request.user:
			color = 'black'
		elif game.player2 == request.user:
			color = 'white'
		else:
			return Response(
				{"detail": "您不是此游戏的参与者。"},
				status=status.HTTP_403_FORBIDDEN
			)

		return Response({"color": color})


class EndGameView(generics.GenericAPIView):
	"""对局终局标记视图 - 标记对局结束并设置获胜者"""
	permission_classes = [IsAuthenticated, IsGameParticipant]  # 需要登录认证且是游戏参与者
	http_method_names = ['put']  # 只允许PUT请求

	@log_api_access("标记对局终局")
	@log_database_operation("Game", "end_game")
	def put(self, request, *args, **kwargs):
		"""标记对局结束并设置获胜者"""
		game_id = self.kwargs.get('game_id')
		winner = request.data.get('winner')  # 从请求数据中获取获胜者

		# 验证winner参数
		if winner not in ['black', 'white', 'draw']:
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": "无效的获胜者值。必须是 'black'、'white' 或 'draw'。"},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			game = Game.objects.get(id=game_id)
		except Game.DoesNotExist:
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": "游戏不存在。"},
				status=status.HTTP_404_NOT_FOUND
			)

		# 更新游戏的winner字段
		game.winner = winner
		game.save()

		from rest_framework.response import Response
		return Response({
			"message": "对局已标记为终局",
			"winner": winner
		})


class ValidatedMoveView(generics.CreateAPIView):
	"""验证落子视图 - 提供严格的落子验证，包括轮次检查"""
	serializer_class = IntersectionSerializer
	permission_classes = [IsAuthenticated]  # 需要登录认证

	@log_api_access("验证落子创建")
	@log_database_operation("Intersection", "validated_create")
	@move_creation_limit()
	def post(self, request, *args, **kwargs):
		"""创建经过验证的落子"""
		game_id = request.data.get('game')
		row = request.data.get('row')
		col = request.data.get('col')
		color = request.data.get('color')

		# 基本参数验证
		if not all([game_id, row is not None, col is not None, color]):
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": "必须提供游戏ID、行、列和颜色参数。"},
				status=status.HTTP_400_BAD_REQUEST
			)

		# 验证颜色参数
		if color not in ['black', 'white']:
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": "颜色必须是 'black' 或 'white'。"},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			game = Game.objects.get(
				models.Q(id=game_id) & (models.Q(player1=self.request.user) | models.Q(player2=self.request.user))
			)
		except Game.DoesNotExist:
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": "您无权在该游戏中落子或游戏不存在。"},
				status=status.HTTP_403_FORBIDDEN
			)

		# 验证用户落子颜色是否匹配其玩家身份
		user_color = self._get_user_color(request.user, game)
		if user_color != color:
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": f"您是{user_color}棋玩家，只能下{user_color}棋。"},
				status=status.HTTP_400_BAD_REQUEST
			)

		# 验证是否是用户的回合
		latest_move = Intersection.objects.filter(game_id=game_id).order_by('-placed_at').first()
		if latest_move and latest_move.color == color:
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": f"轮次错误：上一步已是{color}棋，请等待对手落子。"},
				status=status.HTTP_400_BAD_REQUEST
			)

		# 验证位置是否已有棋子
		existing_move = Intersection.objects.filter(
			game_id=game_id, row=row, col=col
		).first()
		if existing_move and existing_move.color != 'empty':
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": f"位置 ({row}, {col}) 已有棋子。"},
				status=status.HTTP_400_BAD_REQUEST
			)

		# 所有验证通过，创建落子
		return super().post(request, *args, **kwargs)

	def _get_user_color(self, user, game):
		"""获取用户在指定游戏中的棋子颜色"""
		if game.player1 == user:
			return 'black'
		elif game.player2 == user:
			return 'white'
		else:
			return None


class SetKomiView(generics.GenericAPIView):
	"""贴目数设置视图 - 设置对局的贴目数（若已有落子则不执行）"""
	permission_classes = [IsAuthenticated, IsGameParticipant]  # 需要登录认证且是游戏参与者
	http_method_names = ['put']  # 只允许PUT请求

	@log_api_access("设置贴目数")
	@log_database_operation("Game", "set_komi")
	def put(self, request, *args, **kwargs):
		"""设置对局的贴目数，如果已有落子则不执行"""
		game_id = self.kwargs.get('game_id')
		komi = request.data.get('komi')  # 从请求数据中获取贴目数

		# 验证komi参数
		if komi is None:
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": "必须提供贴目数。"},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			# 转换为浮点数验证格式
			komi_value = float(komi)
		except (ValueError, TypeError):
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": "贴目数必须是有效数字。"},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			game = Game.objects.get(id=game_id)
		except Game.DoesNotExist:
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": "游戏不存在。"},
				status=status.HTTP_404_NOT_FOUND
			)

		# 检查该游戏是否已有落子
		intersection_count = Intersection.objects.filter(game_id=game_id).count()

		if intersection_count > 0:
			from rest_framework.response import Response
			from rest_framework import status
			return Response(
				{"detail": "该游戏已有落子，无法更改贴目数。"},
				status=status.HTTP_400_BAD_REQUEST
			)

		# 更新游戏的komi字段
		game.komi = komi_value
		game.save()

		from rest_framework.response import Response
		return Response({
			"message": "贴目数设置成功",
			"komi": komi_value
		})
