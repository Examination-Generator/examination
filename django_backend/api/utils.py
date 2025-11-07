"""
Utility functions for the API
"""

import random
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_otp():
    """Generate random 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_sms(phone_number, message):
    """
    Send SMS via configured provider
    Currently mock implementation - integrate with real SMS provider
    (Twilio, Africa's Talking, AWS SNS, etc.)
    """
    logger.info(f"📱 Sending SMS to {phone_number}: {message}")
    
    # Mock implementation
    if settings.SMS_PROVIDER == 'mock':
        logger.info(f"[MOCK SMS] To: {phone_number}, Message: {message}")
        return {'success': True, 'provider': 'mock'}
    
    # TODO: Integrate with real SMS provider
    # Example for Twilio:
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # message = client.messages.create(
    #     body=message,
    #     from_=settings.TWILIO_PHONE_NUMBER,
    #     to=phone_number
    # )
    # return {'success': True, 'provider': 'twilio', 'sid': message.sid}
    
    return {'success': True, 'provider': settings.SMS_PROVIDER}


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def custom_exception_handler(exc, context):
    """
    Custom exception handler to return consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response format
        custom_response_data = {
            'success': False,
            'message': str(exc),
            'errors': response.data if isinstance(response.data, dict) else {'detail': response.data}
        }
        
        response.data = custom_response_data
    
    return response


def success_response(message, data=None, status=200):
    """
    Create standardized success response
    """
    response_data = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        if isinstance(data, list):
            response_data['count'] = len(data)
        response_data['data'] = data
    
    return Response(response_data, status=status)


def error_response(message, errors=None, status=400):
    """
    Create standardized error response
    """
    response_data = {
        'success': False,
        'message': message
    }
    
    if errors:
        response_data['errors'] = errors
    
    return Response(response_data, status=status)
