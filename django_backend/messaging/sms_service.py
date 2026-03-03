"""
SMS Service for sending SMS messages via Africa's Talking
"""

import os
import logging
from typing import List, Dict, Any

import africastalking

logger = logging.getLogger(__name__)


class SMSService:
    """
    SMS service for sending SMS via Africa's Talking
    Supports mock mode for development/testing
    """
    
    def __init__(self):
        self.provider = os.getenv('SMS_PROVIDER', 'africastalking')
        self.username = os.getenv('SMS_USERNAME', 'sandbox')
        self.api_key = os.getenv('SMS_API_KEY', '')
        self.sender_id = os.getenv('SMS_SENDER_ID', 'speedstar')
        self.mock_mode = os.getenv('SMS_MOCK_MODE', 'true').lower() == 'true'
        
        if not self.mock_mode and self.api_key:
            try:
                import africastalking
                africastalking.initialize(
                    username=self.username,
                    api_key=self.api_key
                )
                self.sms = africastalking.SMS
                logger.info("Africa's Talking SMS service initialized")
            except ImportError:
                logger.warning("africastalking package not installed. Running in mock mode.")
                self.mock_mode = True
            except Exception as e:
                logger.error(f"Failed to initialize Africa's Talking: {e}")
                self.mock_mode = True
        else:
            logger.info("SMS service running in mock mode")
            self.mock_mode = True
    
    def send_sms(self, recipients: List[str], message: str) -> Dict[str, Any]:
        """
        Send SMS to multiple recipients
        
        Args:
            recipients: List of phone numbers in E.164 format
            message: SMS message text
        
        Returns:
            Dictionary with results:
            {
                'success': bool,
                'sent_count': int,
                'failed_count': int,
                'results': List[Dict]
            }
        """
        if self.mock_mode:
            return self._send_mock_sms(recipients, message)
        
        try:
            response = self.sms.send(
                message=message,
                recipients=recipients,
                sender_id=self.sender_id
            )
            
            return self._parse_response(response)
        
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return {
                'success': False,
                'sent_count': 0,
                'failed_count': len(recipients),
                'results': [
                    {
                        'phone': phone,
                        'status': 'failed',
                        'error': str(e),
                        'provider_id': None
                    }
                    for phone in recipients
                ],
                'error': str(e)
            }
    
    def _send_mock_sms(self, recipients: List[str], message: str) -> Dict[str, Any]:
        """
        Mock SMS sending for development/testing
        """
        logger.info(f"[MOCK SMS] Sending to {len(recipients)} recipients")
        logger.info(f"[MOCK SMS] Message: {message}")
        
        results = []
        for phone in recipients:
            mock_id = f"mock-{phone[-8:]}"
            results.append({
                'phone': phone,
                'status': 'sent',
                'provider_id': mock_id,
                'error': None
            })
            logger.info(f"[MOCK SMS] Sent to {phone} - ID: {mock_id}")
        
        return {
            'success': True,
            'sent_count': len(recipients),
            'failed_count': 0,
            'results': results
        }
    
    def _parse_response(self, response: Dict) -> Dict[str, Any]:
        """
        Parse Africa's Talking API response
        
        Response format:
        {
            'SMSMessageData': {
                'Message': 'Sent to 1/1 Total Cost: KES 0.8000',
                'Recipients': [
                    {
                        'statusCode': 101,
                        'number': '+254712345678',
                        'status': 'Success',
                        'cost': 'KES 0.8000',
                        'messageId': 'ATXid_...'
                    }
                ]
            }
        }
        """
        try:
            recipients_data = response.get('SMSMessageData', {}).get('Recipients', [])
            
            results = []
            sent_count = 0
            failed_count = 0
            
            for recipient in recipients_data:
                status_code = recipient.get('statusCode', 0)
                # Status codes: 101 = Success, 102 = Queued, others = Failed
                is_success = status_code in [101, 102]
                
                if is_success:
                    sent_count += 1
                else:
                    failed_count += 1
                
                results.append({
                    'phone': recipient.get('number'),
                    'status': 'sent' if is_success else 'failed',
                    'provider_id': recipient.get('messageId') if is_success else None,
                    'error': recipient.get('status') if not is_success else None
                })
            
            return {
                'success': sent_count > 0,
                'sent_count': sent_count,
                'failed_count': failed_count,
                'results': results
            }
        
        except Exception as e:
            logger.error(f"Failed to parse SMS response: {e}")
            return {
                'success': False,
                'sent_count': 0,
                'failed_count': 0,
                'results': [],
                'error': f"Failed to parse response: {str(e)}"
            }
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get SMS credit balance
        """
        if self.mock_mode:
            return {
                'success': True,
                'balance': 'Mock Mode - No balance check',
                'currency': 'KES'
            }
        
        try:
            application = africastalking.Application
            user_data = application.fetch_application_data()
            
            return {
                'success': True,
                'balance': user_data.get('UserData', {}).get('balance', 'Unknown'),
                'currency': 'KES'
            }
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
sms_service = SMSService()
