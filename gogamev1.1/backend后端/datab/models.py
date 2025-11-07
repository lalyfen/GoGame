from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Game(models.Model):
	"""游戏模型，存储围棋游戏的基本信息"""
	player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_black', db_index=True)  # 黑棋玩家
	player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_white', db_index=True)  # 白棋玩家
	winner = models.CharField(max_length=10, choices=[('black', 'Black'), ('white', 'White'), ('draw', 'Draw')], db_index=True, null=True, blank=True)  # 获胜方
	score_black = models.DecimalField(max_digits=5, decimal_places=2)  # 黑棋得分
	score_white = models.DecimalField(max_digits=5, decimal_places=2)  # 白棋得分
	komi = models.DecimalField(max_digits=4, decimal_places=2)  # 贴目
	created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # 创建时间
	updated_at = models.DateTimeField(auto_now=True)  # 更新时间

	# 添加游戏状态字段
	is_completed = models.BooleanField(default=False, db_index=True)  # 游戏是否结束

	class Meta:
		db_table = 'datab_game'  # 明确指定表名，避免与应用名冲突
		indexes = [
			models.Index(fields=['player1', 'player2']),  # 玩家组合索引
			models.Index(fields=['created_at']),  # 创建时间索引
			models.Index(fields=['player1', 'created_at']),  # 玩家游戏历史索引
			models.Index(fields=['player2', 'created_at']),  # 玩家游戏历史索引
			models.Index(fields=['is_completed', 'created_at']),  # 按完成状态和时间查询
			models.Index(fields=['winner', 'created_at']),  # 按获胜者查询
		]
		constraints = [
			# 暂时注释掉约束，避免迁移问题
			# models.CheckConstraint(
			# 	check=models.Q(score_black__gte=0) & models.Q(score_white__gte=0),
			# 	name='non_negative_scores'
			# ),
			# models.CheckConstraint(
			# 	check=models.Q(komi__gte=0) & models.Q(komi__lte=20),
			# 	name='valid_komi_range'
			# ),
			# models.CheckConstraint(
			# 	check=models.Q(winner__in=['black', 'white', 'draw', '']) | models.Q(winner__isnull=True),
			# 	name='valid_winner_values'
			# ),
		]
		verbose_name = '游戏'
		verbose_name_plural = '游戏'

	def __str__(self):
		return f'Game {self.id}: {self.player1.username} vs {self.player2.username}'


class Intersection(models.Model):
	"""棋盘交叉点模型，存储每一步棋的位置信息"""
	game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='intersections', db_index=True)  # 关联游戏
	row = models.PositiveSmallIntegerField(db_index=True)  # 行坐标 (1-19)
	col = models.PositiveSmallIntegerField(db_index=True)  # 列坐标 (1-19)
	color = models.CharField(max_length=10, choices=[('black', 'Black'), ('white', 'White'), ('empty', 'Empty')], default='empty')  # 棋子颜色
	# 落子时间，用于完整复盘
	placed_at = models.DateTimeField(default=timezone.now, db_index=True, editable=False)  # 落子时间

	# 添加手数字段，用于记录第几手
	move_number = models.PositiveIntegerField(db_index=True, default=1)  # 手数

	class Meta:
		db_table = 'datab_intersection'  # 明确指定表名
		unique_together = ('game', 'row', 'col')  # 确保同一游戏中位置唯一
		indexes = [
			models.Index(fields=['game', 'row', 'col']),  # 游戏位置复合索引
			models.Index(fields=['game', 'placed_at']),  # 游戏时间索引
			models.Index(fields=['game', 'move_number']),  # 游戏手数索引
			models.Index(fields=['color', 'placed_at']),  # 按颜色查询
		]
		constraints = [
			# 暂时注释掉约束，避免迁移问题
			# models.CheckConstraint(
			# 	check=models.Q(row__gte=1) & models.Q(row__lte=19),
			# 	name='valid_row_range'
			# ),
			# models.CheckConstraint(
			# 	check=models.Q(col__gte=1) & models.Q(col__lte=19),
			# 	name='valid_col_range'
			# ),
			# models.CheckConstraint(
			# 	check=models.Q(color__in=['black', 'white', 'empty']),
			# 	name='valid_color_values'
			# ),
			# models.CheckConstraint(
			# 	check=models.Q(move_number__gte=1),
			# 	name='valid_move_number'
			# ),
		]
		verbose_name = '落子位置'
		verbose_name_plural = '落子位置'

	def __str__(self):
		return f'Game {self.game.id} - {self.color} at ({self.row}, {self.col})'
