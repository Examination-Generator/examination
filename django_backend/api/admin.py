"""
Django Admin Configuration for Examination System
"""

from django.contrib import admin
from .models import User, OTPLog, Subject, Paper, Topic, Section, Question


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'full_name', 'role', 'is_active', 'otp_verified', 'created_at']
    list_filter = ['role', 'is_active', 'otp_verified']
    search_fields = ['phone_number', 'full_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'phone_number', 'full_name', 'role')
        }),
        ('Status', {
            'fields': ('is_active', 'otp_verified', 'last_login')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OTPLog)
class OTPLogAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'purpose', 'status', 'otp', 'expires_at', 'created_at']
    list_filter = ['purpose', 'status']
    search_fields = ['phone_number', 'otp']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'subject']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'paper', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'paper__subject']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'paper', 'order', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'paper__subject']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['paper', 'order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text_preview', 'subject', 'paper', 'topic', 'marks', 
                   'difficulty', 'is_active', 'created_at']
    list_filter = ['is_active', 'difficulty', 'question_type', 'subject', 'paper']
    search_fields = ['question_text', 'answer_text']
    readonly_fields = ['id', 'created_at', 'updated_at', 'times_used', 'last_used']
    
    fieldsets = (
        ('Hierarchy', {
            'fields': ('subject', 'paper', 'topic', 'section')
        }),
        ('Question Content', {
            'fields': ('question_text', 'question_inline_images')
        }),
        ('Answer Content', {
            'fields': ('answer_text', 'answer_inline_images')
        }),
        ('Metadata', {
            'fields': ('question_type', 'difficulty', 'marks')
        }),
        ('MCQ Options', {
            'fields': ('options', 'correct_answer', 'answer_explanation'),
            'classes': ('collapse',)
        }),
        ('Status & Usage', {
            'fields': ('is_active', 'times_used', 'last_used', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def question_text_preview(self, obj):
        """Show preview of question text"""
        return obj.question_text[:75] + '...' if len(obj.question_text) > 75 else obj.question_text
    
    question_text_preview.short_description = 'Question'
