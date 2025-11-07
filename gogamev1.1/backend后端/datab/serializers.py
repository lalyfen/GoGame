from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Game, Intersection


class IntersectionSerializer(serializers.ModelSerializer):
	"""棋子交叉点序列化器 - 用于处理棋子位置数据的序列化和反序列化"""
	class Meta:
		model = Intersection
		fields = ('id', 'game', 'row', 'col', 'color', 'placed_at')  # 包含ID、游戏、行列、颜色和落子时间
		read_only_fields = ('placed_at',)  # 落子时间为只读字段


class GameSerializer(serializers.ModelSerializer):
	"""游戏序列化器 - 用于处理游戏数据的序列化和反序列化"""
	intersections = IntersectionSerializer(many=True, read_only=True)  # 嵌套的棋子位置序列化器
	player1 = serializers.CharField(source='player1.username', read_only=True)  # 返回黑棋玩家用户名
	player2 = serializers.CharField(source='player2.username', read_only=True)  # 返回白棋玩家用户名

	# 添加用于接收用户名的字段，支持多种字段名
	player1_username = serializers.CharField(write_only=True, required=False)
	player2_username = serializers.CharField(write_only=True, required=False)

	class Meta:
		model = Game
		fields = ('id', 'player1', 'player2', 'player1_username', 'player2_username', 'winner', 'score_black', 'score_white', 'komi', 'created_at', 'updated_at', 'intersections')  # 包含游戏所有相关字段

	def validate_player1_username(self, value):
		"""验证黑棋玩家用户名是否存在"""
		try:
			user = User.objects.get(username=value)
			return user
		except User.DoesNotExist:
			raise serializers.ValidationError(f"用户 '{value}' 不存在")

	def validate_player2_username(self, value):
		"""验证白棋玩家用户名是否存在"""
		try:
			user = User.objects.get(username=value)
			return user
		except User.DoesNotExist:
			raise serializers.ValidationError(f"用户 '{value}' 不存在")

	def validate(self, data):
		"""验证两个玩家不能是同一个用户"""
		player1_user = data.get('player1_username')
		player2_user = data.get('player2_username')

		if player1_user and player2_user and player1_user.id == player2_user.id:
			raise serializers.ValidationError("黑棋玩家和白棋玩家不能是同一个用户")

		# 确保至少有一个玩家
		if not player1_user or not player2_user:
			raise serializers.ValidationError("必须提供两个玩家的用户名")

		return data

	def create(self, validated_data):
		"""创建游戏时将用户名转换为用户ID"""
		# 从validated_data中移除用户名字段，并获取用户对象
		player1_user = validated_data.pop('player1_username')
		player2_user = validated_data.pop('player2_username')

		# 创建游戏记录
		game = Game.objects.create(
			player1=player1_user,
			player2=player2_user,
			**validated_data
		)
		return game

	def to_internal_value(self, data):
		"""
		处理前端发送的数据，支持player1/player2和player1_username/player2_username两种格式
		"""
		# 如果前端发送的是player1和player2字段，转换为player1_username和player2_username
		if 'player1' in data and 'player1_username' not in data:
			data = data.copy()
			data['player1_username'] = data.pop('player1')

		if 'player2' in data and 'player2_username' not in data:
			data = data.copy()
			data['player2_username'] = data.pop('player2')

		return super().to_internal_value(data)
