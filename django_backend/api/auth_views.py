import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from django.shortcuts import redirect

from .models import User, OTPLog
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    SendOTPSerializer, VerifyOTPSerializer, ResetPasswordSerializer
)
from .utils import generate_otp, send_sms, get_client_ip, success_response, error_response

logger = logging.getLogger(__name__)


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['phone_number'] = user.phone_number
    refresh['full_name'] = user.full_name
    refresh['user_id'] = str(user.id)
    return {
        'token': str(refresh.access_token),
        'refresh': str(refresh),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """
    Send OTP to phone number for registration or login
    POST /api/auth/send-otp
    """
    serializer = SendOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    purpose = serializer.validated_data.get('purpose', 'registration')
    
    logger.info(f"[AUTH] OTP request for {phone_number}, purpose: {purpose}")
    
    # Check if user exists
    existing_user = User.objects.filter(phone_number=phone_number).first()
    
    if purpose == 'registration' and existing_user:
        return error_response(
            'Phone number already registered. Please login.',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if purpose == 'login' and not existing_user:
        return error_response(
            'Phone number not registered. Please register first.',
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    # Save OTP log
    OTPLog.objects.create(
        phone_number=phone_number,
        otp=otp_code,
        purpose=purpose,
        expires_at=expires_at,
        ip_address=get_client_ip(request)
    )
    
    # Send OTP via SMS
    sms_message = f"Your verification code is: {otp_code}. Valid for 10 minutes."
    sms_result = send_sms(phone_number, sms_message)
    
    if not sms_result.get('success'):
        return error_response(
            'Failed to send OTP. Please try again.',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return success_response(
        'OTP sent successfully',
        {'expiresIn': 600}  # seconds
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP code
    POST /api/auth/verify-otp
    """
    serializer = VerifyOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    otp_code = serializer.validated_data['otp']
    
    logger.info(f"[AUTH] OTP verification for {phone_number}")
    
    # Find OTP log
    otp_log = OTPLog.objects.filter(
        phone_number=phone_number,
        otp=otp_code,
        status='sent',
        expires_at__gt=timezone.now()
    ).order_by('-created_at').first()
    
    if not otp_log:
        return error_response(
            'Invalid or expired OTP',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check attempts (max 5)
    if otp_log.attempts >= 5:
        return error_response(
            'Too many attempts. Please request a new OTP.',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update OTP log
    otp_log.status = 'verified'
    otp_log.verified_at = timezone.now()
    otp_log.save()
    
    # Check if user exists
    user_exists = User.objects.filter(phone_number=phone_number).exists()
    
    logger.info(f"[AUTH] OTP verified for {phone_number}, user exists: {user_exists}")
    
    return success_response(
        'OTP verified successfully',
        {'userExists': user_exists}
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Complete registration after OTP verification
    POST /api/auth/register
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    logger.info(f"[AUTH] Registration attempt for {phone_number}")
    
    # Check if user already exists
    if User.objects.filter(phone_number=phone_number).exists():
        return error_response(
            'Phone number already registered',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify that OTP was verified
    otp_log = OTPLog.objects.filter(
        phone_number=phone_number,
        status='verified',
        purpose='registration'
    ).order_by('-created_at').first()
    
    if not otp_log:
        return error_response(
            'Please verify OTP first',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create user
    user = serializer.save()
    
    # Generate tokens
    tokens = get_tokens_for_user(user)
    
    logger.info(f"[AUTH] User registered successfully: {phone_number}")
    
    return success_response(
        'Registration successful',
        {
            'token': tokens['token'],
            'user': {
                'id': str(user.id),
                'fullName': user.full_name,
                'phoneNumber': user.phone_number,
                'role': user.role
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login with phone number and password
    POST /api/auth/login
    """
    logger.info(f"[AUTH] Login request data: {request.data}")
    serializer = UserLoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error(f"[AUTH] Login validation failed: {serializer.errors}")
        return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    password = serializer.validated_data['password']
    
    logger.info(f"[AUTH] Login attempt for {phone_number}")
    
    # Find user
    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        logger.info(f"[AUTH] User not found: {phone_number}")
        return error_response(
            'Invalid credentials',
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if account is active
    if not user.is_active:
        logger.info(f"[AUTH] Account deactivated: {phone_number}")
        return error_response(
            'Account is deactivated. Please contact support.',
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Verify password
    if not user.check_password(password):
        logger.info(f"[AUTH] Invalid password for: {phone_number}")
        return error_response(
            'Invalid credentials',
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Update last login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # Generate tokens
    tokens = get_tokens_for_user(user)
    
    logger.info(f"[AUTH] Login successful: {phone_number}, Role: {user.role}")
    
    return success_response(
        'Login successful',
        {
            'token': tokens['token'],
            'user': {
                'id': str(user.id),
                'fullName': user.full_name,
                'phoneNumber': user.phone_number,
                'role': user.role
            }
        }
    )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    Logout endpoint that clears server-side session state.

    GET  /api/logout  -> clears session and redirects the browser
    POST /api/logout  -> clears session and returns JSON for SPA clients
    """
    redirect_url = (
        request.GET.get('next')
        or request.data.get('next')
        or '/login'
    )

    refresh_token = (
        request.data.get('refresh')
        or request.data.get('refreshToken')
        or request.GET.get('refresh')
        or request.GET.get('refreshToken')
    )

    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception as exc:
            logger.info(f"[AUTH] Refresh token blacklist skipped during logout: {exc}")

    try:
        django_logout(request)
    except Exception as exc:
        logger.info(f"[AUTH] Django logout skipped: {exc}")

    if hasattr(request, 'session'):
        try:
            request.session.flush()
        except Exception as exc:
            logger.info(f"[AUTH] Session flush skipped: {exc}")

    if request.method == 'GET':
        response = redirect(redirect_url)
        response.delete_cookie(settings.SESSION_COOKIE_NAME)
        return response

    response = success_response(
        'Logout successful',
        {
            'redirect_url': redirect_url,
            'session_cleared': True
        }
    )
    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Initiate password reset with OTP
    POST /api/auth/forgot-password
    """
    phone_number = request.data.get('phoneNumber')
    
    if not phone_number:
        return error_response(
            'Phone number is required',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Find user
    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return error_response(
            'Phone number not registered',
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    # Save OTP log
    OTPLog.objects.create(
        phone_number=phone_number,
        otp=otp_code,
        purpose='password_reset',
        expires_at=expires_at,
        ip_address=get_client_ip(request)
    )
    
    # Send OTP via SMS
    sms_message = f"Your password reset code is: {otp_code}. Valid for 10 minutes."
    send_sms(phone_number, sms_message)
    
    return success_response('Password reset OTP sent successfully')


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset password with verified OTP
    POST /api/auth/reset-password
    """
    serializer = ResetPasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    otp_code = serializer.validated_data['otp']
    new_password = serializer.validated_data['new_password']
    
    # Verify OTP
    otp_log = OTPLog.objects.filter(
        phone_number=phone_number,
        otp=otp_code,
        purpose='password_reset',
        status='sent',
        expires_at__gt=timezone.now()
    ).order_by('-created_at').first()
    
    if not otp_log:
        return error_response(
            'Invalid or expired OTP',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Find user
    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return error_response(
            'User not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update password
    user.set_password(new_password)
    user.save()
    
    # Update OTP log
    otp_log.status = 'verified'
    otp_log.verified_at = timezone.now()
    otp_log.save()
    
    return success_response('Password reset successful. Please login with your new password.')
