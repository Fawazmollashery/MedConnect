from django.contrib import admin
from .models import Chat, Profile

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'response', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'message', 'response')
    ordering = ('-created_at',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')
