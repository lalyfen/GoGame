from django.contrib import admin
from .models import Game, Intersection


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'player1', 'player2', 'winner', 'score_black', 'score_white', 'komi', 'created_at', 'updated_at')
    list_filter = ('winner', 'created_at', 'player1', 'player2')
    search_fields = ('player1__username', 'player2__username', 'winner')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Game Information', {
            'fields': ('player1', 'player2', 'winner')
        }),
        ('Score Details', {
            'fields': ('score_black', 'score_white', 'komi')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Intersection)
class IntersectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'row', 'col', 'color', 'placed_at')
    list_filter = ('color', 'placed_at', 'game')
    search_fields = ('game__id', 'row', 'col')
    ordering = ('game', 'placed_at')
    readonly_fields = ('placed_at',)

    fieldsets = (
        ('Position Information', {
            'fields': ('game', 'row', 'col')
        }),
        ('Stone Details', {
            'fields': ('color',)
        }),
        ('Timestamp', {
            'fields': ('placed_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('game')