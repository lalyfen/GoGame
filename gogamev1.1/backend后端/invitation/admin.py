from django.contrib import admin
from .models import UserServer, Invitation


@admin.register(UserServer)
class UserServerAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'server', 'created_at', 'updated_at']
    list_filter = ['server', 'created_at']
    search_fields = ['username']


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['inviter', 'invitee', 'inviter_username', 'invitee_username', 'is_confirmed', 'created_at']
    list_filter = ['is_confirmed', 'created_at']
    search_fields = ['inviter_username', 'invitee_username']
    readonly_fields = ['created_at']
