from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from invitation.models import Invitation


class Command(BaseCommand):
    help = '清理超过1小时的邀请记录'

    def handle(self, *args, **options):
        # 计算1小时前的时间
        one_hour_ago = timezone.now() - timedelta(hours=1)

        # 查询超过1小时的邀请记录
        old_invitations = Invitation.objects.filter(
            created_at__lt=one_hour_ago
        )

        count = old_invitations.count()

        if count > 0:
            # 删除记录
            old_invitations.delete()
            self.stdout.write(
                self.style.SUCCESS(f'成功删除 {count} 条超过1小时的邀请记录')
            )
        else:
            self.stdout.write('没有需要清理的邀请记录')
