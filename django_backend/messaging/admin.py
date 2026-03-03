"""
Admin configuration for Messaging module
"""

from django.contrib import admin
from .models import SystemMessage, SMSMessage


@admin.register(SystemMessage)
class SystemMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender_name', 'subject', 'is_read', 'is_from_admin', 'created_at']
    list_filter = ['is_read', 'is_from_admin', 'created_at']
    search_fields = ['sender_name', 'subject', 'message']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Message Info', {
            'fields': ('id', 'sender', 'sender_name', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'is_from_admin')
        }),
        ('Thread', {
            'fields': ('parent_message', 'quoted_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'deleted_at')
        }),
    )


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient_phone', 'recipient_name', 'status', 'direction', 'created_at']
    list_filter = ['status', 'direction', 'created_at']
    search_fields = ['recipient_phone', 'recipient_name', 'message']
    readonly_fields = ['id', 'created_at', 'updated_at', 'sent_at', 'delivered_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Message Info', {
            'fields': ('id', 'sender', 'recipient_phone', 'recipient_name', 'message')
        }),
        ('Status', {
            'fields': ('direction', 'status', 'sms_provider_id', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'sent_at', 'delivered_at')
        }),
    )
