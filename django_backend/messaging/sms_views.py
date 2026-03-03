"""
SMS Messaging Views
Admin-only endpoints for SMS management
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count, Max
from django.shortcuts import get_object_or_404

from .models import SMSMessage
from .serializers import (
    SMSMessageSerializer,
    SendSMSSerializer,
    UserContactSerializer
)
from .sms_service import sms_service
from api.models import User

import logging

logger = logging.getLogger(__name__)


def check_admin_permission(user):
    """Check if user is admin"""
    return user.role == 'admin'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_contacts(request):
    """
    Search for contacts by name or phone number
    Admin only
    Query params:
    - q: Search query (min 2 characters)
    """
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return Response(
            {'error': 'Search query must be at least 2 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Search users by name or phone number
        users = User.objects.filter(
            Q(full_name__icontains=query) | Q(phone_number__icontains=query),
            phone_number__isnull=False
        ).exclude(phone_number='').order_by('full_name')[:20]
        
        serializer = UserContactSerializer(users, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Failed to search contacts: {e}")
        return Response(
            {'error': 'Failed to search contacts'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_sms(request):
    """
    Send SMS to one or multiple recipients
    Admin only
    """
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = SendSMSSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    recipients = serializer.validated_data['recipients']
    message = serializer.validated_data['message']
    
    try:
        # Send SMS via service
        result = sms_service.send_sms(recipients, message)
        
        # Store SMS records in database
        for sms_result in result.get('results', []):
            phone = sms_result['phone']
            
            # Get recipient name if exists
            recipient_name = ''
            try:
                user = User.objects.filter(phone_number=phone).first()
                if user:
                    recipient_name = user.full_name
            except:
                pass
            
            # Create SMS record
            sms_message = SMSMessage.objects.create(
                sender=request.user,
                recipient_phone=phone,
                recipient_name=recipient_name,
                message=message,
                direction='outgoing',
                status=sms_result['status']
            )
            
            # Update status if sent successfully
            if sms_result['status'] == 'sent':
                sms_message.mark_as_sent(sms_result.get('provider_id'))
            elif sms_result['status'] == 'failed':
                sms_message.mark_as_failed(sms_result.get('error'))
        
        return Response(
            {
                'success': result['success'],
                'sent_count': result['sent_count'],
                'failed_count': result['failed_count'],
                'message': f"SMS sent successfully to {result['sent_count']} recipient(s)"
            },
            status=status.HTTP_200_OK if result['success'] else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        return Response(
            {'error': 'Failed to send SMS', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sms_conversation(request, phone_number):
    """
    Get SMS conversation history with a specific phone number
    Admin only
    """
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Get all SMS messages for this phone number
        messages = SMSMessage.objects.filter(
            recipient_phone=phone_number
        ).order_by('created_at')
        
        serializer = SMSMessageSerializer(messages, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Failed to get SMS conversation: {e}")
        return Response(
            {'error': 'Failed to retrieve conversation'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_sms_conversations(request):
    """
    Get list of all SMS conversations with summary
    Admin only
    """
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Get all unique phone numbers with their latest message
        conversations = SMSMessage.objects.values('recipient_phone', 'recipient_name').annotate(
            last_message_at=Max('created_at'),
            message_count=Count('id')
        ).order_by('-last_message_at')
        
        # Get last message text for each conversation
        result = []
        for conv in conversations:
            last_message = SMSMessage.objects.filter(
                recipient_phone=conv['recipient_phone']
            ).order_by('-created_at').first()
            
            result.append({
                'phone_number': conv['recipient_phone'],
                'name': conv['recipient_name'] or 'Unknown',
                'last_message': last_message.message if last_message else '',
                'last_message_at': conv['last_message_at'],
                'message_count': conv['message_count']
            })
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Failed to get SMS conversations: {e}")
        return Response(
            {'error': 'Failed to retrieve conversations'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sms_balance(request):
    """
    Get SMS credit balance
    Admin only
    """
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin permission required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        balance_info = sms_service.get_balance()
        return Response(balance_info, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Failed to get SMS balance: {e}")
        return Response(
            {'error': 'Failed to get balance'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
