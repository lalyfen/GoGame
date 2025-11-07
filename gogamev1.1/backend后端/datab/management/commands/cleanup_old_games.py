from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from datab.models import Game, Intersection


class Command(BaseCommand):
    help = '清理旧的未完成游戏和孤立的棋子数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='清理多少天前的未完成游戏（默认30天）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要清理的数据，不实际删除'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']

        cutoff_date = timezone.now() - timedelta(days=days)

        # 查找超过指定天数且未完成的游戏
        # 假设'draw'表示未完成，实际可能需要根据业务逻辑调整
        old_games = Game.objects.filter(
            created_at__lt=cutoff_date,
            winner='draw'  # 未完成的游戏
        )

        game_count = old_games.count()

        if dry_run:
            self.stdout.write(f'[DRY RUN] 将清理 {game_count} 个超过{days}天的未完成游戏')

            # 统计将要删除的棋子数量
            intersection_count = Intersection.objects.filter(game__in=old_games).count()
            self.stdout.write(f'[DRY RUN] 将清理 {intersection_count} 个相关棋子数据')
        else:
            if game_count > 0:
                # 先删除相关棋子
                deleted_intersections = Intersection.objects.filter(game__in=old_games).delete()
                # 再删除游戏
                deleted_games = old_games.delete()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'成功清理 {deleted_games[0]} 个游戏和 {deleted_intersections[0]} 个棋子数据'
                    )
                )
            else:
                self.stdout.write('没有找到需要清理的旧游戏数据')

        # 统计当前数据库状态
        total_games = Game.objects.count()
        total_intersections = Intersection.objects.count()

        self.stdout.write(f'数据库当前状态：')
        self.stdout.write(f'  总游戏数: {total_games}')
        self.stdout.write(f'  总棋子数: {total_intersections}')
        self.stdout.write(f'  未完成游戏数: {Game.objects.filter(winner="draw").count()}')