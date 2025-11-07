"""
Core应用配置
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        """应用准备就绪时注册信号"""
        import core.cache_signals  # noqa: F401