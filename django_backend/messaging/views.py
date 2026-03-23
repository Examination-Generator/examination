"""
API Views for Messaging System
System Messages and SMS Management
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count, Max, Prefetch, F
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import SystemMessage, SMSMessage
from .serializers import (
    SystemMessageSerializer,
    SystemMessageConversationSerializer,
    SystemMessageReplySerializer,
    SendSystemMessageSerializer,
    ReplyMessageSerializer,
    SMSMessageSerializer,
    SendSMSSerializer,
    UserContactSerializer
)
from .sms_service import sms_service
from api.models import User

import logging

logger = logging.getLogger(__name__)


# ==================== SYSTEM MESSAGING ENDPOINTS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_system_message(request):
    """
    Send a system message (support message)
    Users send to admins, admins can send to anyone
    """
    serializer = SendSystemMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create message
        message = SystemMessage.objects.create(
            sender=request.user,
            sender_name=request.user.full_name,
            subject=serializer.validated_data.get('subject', ''),
            message=serializer.validated_data['message'],
            is_from_admin=request.user.role == 'admin'
        )
        
        result_serializer = SystemMessageSerializer(message)
        
        return Response(
            result_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        logger.error(f"Failed to send system message: {e}")
        return Response(
            {'error': 'Failed to send message'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_messages(request):
    """
    Get system messages
    - Admins see all messages from users
    - Users see their own messages
    Query params:
    - unreadOnly: true/false
    """
    unread_only = request.GET.get('unreadOnly', 'false').lower() == 'true'
    
    try:
        # Base query - exclude deleted and replies
        queryset = SystemMessage.objects.filter(
            deleted_at__isnull=True,
            parent_message__isnull=True  # Only root messages
        )
        
        # Filter based on user role
        if request.user.role == 'admin':
            # Admins see all messages
            pass
        else:
            # Users see only their own messages
            queryset = queryset.filter(sender=request.user)
        
        # Annotate reply counts and unread incoming replies for conversation-level inbox behavior
        if request.user.role == 'admin':
            queryset = queryset.annotate(
                unread_replies_count=Count(
                    'replies',
                    filter=Q(
                        replies__deleted_at__isnull=True,
                        replies__is_read=False,
                        replies__is_from_admin=False
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                unread_replies_count=Count(
                    'replies',
                    filter=Q(
                        replies__deleted_at__isnull=True,
                        replies__is_read=False,
                        replies__is_from_admin=True
                    )
                )
            )

        # Filter for unread only at conversation level
        if unread_only:
            if request.user.role == 'admin':
                queryset = queryset.filter(
                    Q(is_read=False, is_from_admin=False) |
                    Q(unread_replies_count__gt=0)
                )
            else:
                queryset = queryset.filter(unread_replies_count__gt=0)
        
        # Annotate with reply count
        queryset = queryset.annotate(
            replies_count=Count('replies', filter=Q(replies__deleted_at__isnull=True)),
            last_activity_at=Coalesce(Max('replies__created_at'), F('created_at'))
        )
        
        # Order by most recent activity in the thread
        queryset = queryset.order_by('-last_activity_at')
        
        serializer = SystemMessageSerializer(queryset, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Failed to get system messages: {e}")
        return Response(
            {'error': 'Failed to retrieve messages'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_message_conversation(request, message_id):
    """
    Get a message thread with all replies
    """
    try:
        # Get the root message
        message = get_object_or_404(
            SystemMessage,
            id=message_id,
            deleted_at__isnull=True,
            parent_message__isnull=True  # Ensure it's a root message
        )
        
        # Check permissions
        if request.user.role != 'admin' and message.sender != request.user:
            return Response(
                {'error': 'You do not have permission to view this message'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mark incoming messages in this thread as read for the current viewer.
        if request.user.role == 'admin':
            if not message.is_from_admin and not message.is_read:
                message.mark_as_read()

            SystemMessage.objects.filter(
                parent_message=message,
                deleted_at__isnull=True,
                is_read=False,
                is_from_admin=False
            ).update(is_read=True, updated_at=timezone.now())
        else:
            if message.sender == request.user and message.is_from_admin and not message.is_read:
                message.mark_as_read()

            SystemMessage.objects.filter(
                parent_message=message,
                deleted_at__isnull=True,
                is_read=False,
                is_from_admin=True
            ).update(is_read=True, updated_at=timezone.now())
        
        # Prefetch replies
        message = SystemMessage.objects.prefetch_related(
            Prefetch(
                'replies',
                queryset=SystemMessage.objects.filter(deleted_at__isnull=True).order_by('created_at')
            )
        ).get(id=message_id)
        
        serializer = SystemMessageConversationSerializer(message)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except SystemMessage.DoesNotExist:
        return Response(
            {'error': 'Message not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to get message conversation: {e}")
        return Response(
            {'error': 'Failed to retrieve conversation'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reply_to_message(request, message_id):
    """
    Reply to a message
    """
    serializer = ReplyMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get the parent message
        parent_message = get_object_or_404(
            SystemMessage,
            id=message_id,
            deleted_at__isnull=True
        )
        
        # Get the root message (in case replying to a reply)
        root_message = parent_message
        if parent_message.parent_message:
            root_message = parent_message.parent_message
        
        # Check permissions
        if request.user.role != 'admin' and root_message.sender != request.user:
            return Response(
                {'error': 'You do not have permission to reply to this message'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create reply
        reply = SystemMessage.objects.create(
            sender=request.user,
            sender_name=request.user.full_name,
            message=serializer.validated_data['message'],
            quoted_text=serializer.validated_data.get('quoted_text', ''),
            is_from_admin=request.user.role == 'admin',
            parent_message=root_message,
            subject=root_message.subject
        )
        
        result_serializer = SystemMessageReplySerializer(reply)
        
        return Response(
            result_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    except SystemMessage.DoesNotExist:
        return Response(
            {'error': 'Message not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to reply to message: {e}")
        return Response(
            {'error': 'Failed to send reply'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_message_as_read(request, message_id):
    """
    Mark a message as read
    """
    try:
        message = get_object_or_404(
            SystemMessage,
            id=message_id,
            deleted_at__isnull=True
        )
        
        # Check permissions by recipient perspective (read receipts)
        root_message = message.parent_message if message.parent_message else message

        if request.user.role == 'admin':
            # Admin can only mark user-originated messages as read
            if message.is_from_admin:
                return Response(
                    {'error': 'You do not have permission to modify this message'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            # User can only mark admin-originated messages in their own thread as read
            if root_message.sender != request.user or not message.is_from_admin:
                return Response(
                    {'error': 'You do not have permission to modify this message'},
                    status=status.HTTP_403_FORBIDDEN
                )

        message.mark_as_read()
        
        return Response(
            {
                'id': str(message.id),
                'is_read': message.is_read,
                'updated_at': message.updated_at
            },
            status=status.HTTP_200_OK
        )
    
    except SystemMessage.DoesNotExist:
        return Response(
            {'error': 'Message not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to mark message as read: {e}")
        return Response(
            {'error': 'Failed to update message'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    """
    Get count of unread messages
    """
    try:
        if request.user.role == 'admin':
            unread_root_ids = set(
                SystemMessage.objects.filter(
                    deleted_at__isnull=True,
                    parent_message__isnull=True,
                    is_read=False,
                    is_from_admin=False
                ).values_list('id', flat=True)
            )
            unread_reply_root_ids = set(
                SystemMessage.objects.filter(
                    deleted_at__isnull=True,
                    parent_message__isnull=False,
                    is_read=False,
                    is_from_admin=False
                ).values_list('parent_message_id', flat=True)
            )
            count = len(unread_root_ids.union(unread_reply_root_ids))
        else:
            unread_reply_root_ids = set(
                SystemMessage.objects.filter(
                    deleted_at__isnull=True,
                    parent_message__isnull=False,
                    is_read=False,
                    is_from_admin=True,
                    parent_message__sender=request.user,
                    parent_message__deleted_at__isnull=True
                ).values_list('parent_message_id', flat=True)
            )
            count = len(unread_reply_root_ids)
        
        return Response(
            {'count': count},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"Failed to get unread count: {e}")
        return Response(
            {'error': 'Failed to get unread count'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_message(request, message_id):
    """
    Soft delete a message
    """
    try:
        message = get_object_or_404(
            SystemMessage,
            id=message_id,
            deleted_at__isnull=True
        )
        
        # Check permissions
        if request.user.role != 'admin' and message.sender != request.user:
            return Response(
                {'error': 'You do not have permission to delete this message'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.soft_delete()
        
        return Response(
            {
                'success': True,
                'message': 'Message deleted successfully'
            },
            status=status.HTTP_200_OK
        )
    
    except SystemMessage.DoesNotExist:
        return Response(
            {'error': 'Message not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")
        return Response(
            {'error': 'Failed to delete message'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
