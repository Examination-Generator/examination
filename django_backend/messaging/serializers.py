"""
Serializers for Messaging System
"""

import os
from rest_framework import serializers
from .models import SystemMessage, SMSMessage
from api.models import User


ALLOWED_ATTACHMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'}
MAX_ATTACHMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_attachment_file(file_obj):
    if not file_obj:
        return file_obj

    ext = os.path.splitext(file_obj.name or '')[1].lower()
    if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise serializers.ValidationError(
            'Unsupported file type. Allowed: PDF, DOC, DOCX, TXT, RTF, ODT.'
        )

    if file_obj.size > MAX_ATTACHMENT_SIZE_BYTES:
        raise serializers.ValidationError('Attachment too large. Max size is 10MB.')

    return file_obj


def build_attachment_url(serializer_instance, obj):
    if not obj.attachment:
        return None

    url = obj.attachment.url
    if not url.startswith('/'):
        url = f'/{url}'

    request = serializer_instance.context.get('request')
    if request:
        return request.build_absolute_uri(url)

    return url


class UserContactSerializer(serializers.ModelSerializer):
    """Serializer for user contacts"""
    name = serializers.CharField(source='full_name')
    
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number']


class SystemMessageSerializer(serializers.ModelSerializer):
    """Serializer for system messages"""
    replies_count = serializers.IntegerField(read_only=True)
    unread_replies_count = serializers.IntegerField(read_only=True)
    sender_phone_number = serializers.CharField(source='sender.phone_number', read_only=True)
    attachment_url = serializers.SerializerMethodField()
    has_attachment = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemMessage
        fields = [
            'id', 'sender_id', 'sender_name', 'subject', 'message',
            'is_read', 'is_from_admin', 'created_at', 'updated_at',
            'parent_message_id', 'quoted_text', 'replies_count', 'unread_replies_count',
            'sender_phone_number', 'attachment_name', 'attachment_content_type',
            'attachment_url', 'has_attachment'
        ]
        read_only_fields = ['id', 'sender_id', 'sender_name', 'created_at', 'updated_at', 'is_from_admin']

    def get_attachment_url(self, obj):
        return build_attachment_url(self, obj)

    def get_has_attachment(self, obj):
        return bool(obj.attachment)
    
    def create(self, validated_data):
        # Auto-set sender info from request user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['sender'] = request.user
            validated_data['sender_name'] = request.user.full_name
            role = (getattr(request.user, 'role', '') or '').strip().lower()
            validated_data['is_from_admin'] = role in ('admin', 'editor')
        return super().create(validated_data)


class SystemMessageReplySerializer(serializers.ModelSerializer):
    """Serializer for message replies"""
    sender_phone_number = serializers.CharField(source='sender.phone_number', read_only=True)
    attachment_url = serializers.SerializerMethodField()
    has_attachment = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemMessage
        fields = [
            'id', 'sender_id', 'sender_name', 'message',
            'quoted_text', 'is_from_admin', 'is_read', 'created_at', 'sender_phone_number',
            'attachment_name', 'attachment_content_type', 'attachment_url', 'has_attachment'
        ]
        read_only_fields = ['id', 'sender_id', 'sender_name', 'created_at', 'is_from_admin', 'is_read']

    def get_attachment_url(self, obj):
        return build_attachment_url(self, obj)

    def get_has_attachment(self, obj):
        return bool(obj.attachment)


class SystemMessageConversationSerializer(serializers.ModelSerializer):
    """Serializer for message conversation with replies"""
    replies = SystemMessageReplySerializer(many=True, read_only=True)
    sender_phone_number = serializers.CharField(source='sender.phone_number', read_only=True)
    attachment_url = serializers.SerializerMethodField()
    has_attachment = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemMessage
        fields = [
            'id', 'sender_id', 'sender_name', 'subject', 'message',
            'is_read', 'is_from_admin', 'created_at', 'replies', 'sender_phone_number',
            'attachment_name', 'attachment_content_type', 'attachment_url', 'has_attachment'
        ]
        read_only_fields = ['id', 'sender_id', 'sender_name', 'created_at', 'is_from_admin']

    def get_attachment_url(self, obj):
        return build_attachment_url(self, obj)

    def get_has_attachment(self, obj):
        return bool(obj.attachment)


class SMSMessageSerializer(serializers.ModelSerializer):
    """Serializer for SMS messages"""
    
    class Meta:
        model = SMSMessage
        fields = [
            'id', 'recipient_phone', 'recipient_name', 'message',
            'direction', 'status', 'sent_at', 'delivered_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'sent_at', 'delivered_at',
            'created_at', 'updated_at'
        ]


class SendSMSSerializer(serializers.Serializer):
    """Serializer for sending SMS"""
    recipients = serializers.ListField(
        child=serializers.CharField(max_length=20),
        min_length=1,
        help_text="List of phone numbers"
    )
    message = serializers.CharField(
        max_length=160,
        help_text="SMS message text (max 160 characters)"
    )
    
    def validate_recipients(self, value):
        """Validate phone numbers"""
        if not value:
            raise serializers.ValidationError("At least one recipient is required")
        
        # Basic validation for phone numbers
        for phone in value:
            if not phone.startswith('+'):
                raise serializers.ValidationError(f"Invalid phone number format: {phone}. Use E.164 format (+254...)")
            if len(phone) < 10:
                raise serializers.ValidationError(f"Phone number too short: {phone}")
        
        return value
    
    def validate_message(self, value):
        """Validate message"""
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class SendSystemMessageSerializer(serializers.Serializer):
    """Serializer for sending system message"""
    subject = serializers.CharField(max_length=500, required=False, allow_blank=True)
    message = serializers.CharField(
        max_length=5000,
        required=False,
        allow_blank=True,
        help_text="Message text (max 5000 characters)"
    )
    attachment = serializers.FileField(required=False, allow_null=True)
    
    def validate_message(self, value):
        """Validate message"""
        return (value or '').strip()

    def validate_attachment(self, value):
        return validate_attachment_file(value)

    def validate(self, attrs):
        message = (attrs.get('message') or '').strip()
        attachment = attrs.get('attachment')

        if not message and not attachment:
            raise serializers.ValidationError('Provide a message or an attachment.')

        attrs['message'] = message
        return attrs


class ReplyMessageSerializer(serializers.Serializer):
    """Serializer for replying to a message"""
    message = serializers.CharField(
        max_length=5000,
        required=False,
        allow_blank=True,
        help_text="Reply message text (max 5000 characters)"
    )
    quoted_text = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        help_text="Quoted text from original message"
    )
    attachment = serializers.FileField(required=False, allow_null=True)
    
    def validate_message(self, value):
        """Validate message"""
        return (value or '').strip()

    def validate_attachment(self, value):
        return validate_attachment_file(value)

    def validate(self, attrs):
        message = (attrs.get('message') or '').strip()
        attachment = attrs.get('attachment')

        if not message and not attachment:
            raise serializers.ValidationError('Provide a message or an attachment.')

        attrs['message'] = message
        return attrs
