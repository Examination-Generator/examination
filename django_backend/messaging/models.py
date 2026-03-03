"""
Messaging System Models
Includes System Messages and SMS Messages
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class SystemMessage(models.Model):
    """
    Internal support messaging between users and admins
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        db_index=True
    )
    sender_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=500, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        db_index=True
    )
    quoted_text = models.TextField(null=True, blank=True)
    is_from_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'system_messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender_name}: {self.subject or 'No Subject'}"
    
    def soft_delete(self):
        """Soft delete the message"""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read', 'updated_at'])
    
    @property
    def replies_count(self):
        """Count of replies to this message"""
        return self.replies.filter(deleted_at__isnull=True).count()


class SMSMessage(models.Model):
    """
    SMS messages sent to users via phone numbers
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    
    DIRECTION_CHOICES = [
        ('outgoing', 'Outgoing'),
        ('incoming', 'Incoming'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_sms',
        db_index=True
    )
    recipient_phone = models.CharField(max_length=20, db_index=True)
    recipient_name = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField()
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        default='outgoing'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    sms_provider_id = models.CharField(max_length=255, null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sms_messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['recipient_phone', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"SMS to {self.recipient_phone}: {self.message[:50]}"
    
    def mark_as_sent(self, provider_id=None):
        """Mark SMS as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if provider_id:
            self.sms_provider_id = provider_id
        self.save(update_fields=['status', 'sent_at', 'sms_provider_id', 'updated_at'])
    
    def mark_as_delivered(self):
        """Mark SMS as delivered"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at', 'updated_at'])
    
    def mark_as_failed(self, error_message=None):
        """Mark SMS as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])
