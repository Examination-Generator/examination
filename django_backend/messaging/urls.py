"""
URL Configuration for Messaging Module
"""

from django.urls import path
from . import views, sms_views

app_name = 'messaging'

urlpatterns = [
    # System Messaging Endpoints
    path('system/send', views.send_system_message, name='send_system_message'),
    path('system/messages', views.get_system_messages, name='get_system_messages'),
    path('system/messages/<uuid:message_id>/conversation', views.get_message_conversation, name='get_message_conversation'),
    path('system/messages/<uuid:message_id>/reply', views.reply_to_message, name='reply_to_message'),
    path('system/messages/<uuid:message_id>/read', views.mark_message_as_read, name='mark_message_as_read'),
    path('system/messages/<uuid:message_id>', views.delete_message, name='delete_message'),
    path('system/unread-count', views.get_unread_count, name='get_unread_count'),
    
    # SMS Messaging Endpoints (Admin only)
    path('contacts/search', sms_views.search_contacts, name='search_contacts'),
    path('sms/send', sms_views.send_sms, name='send_sms'),
    path('sms/conversation/<str:phone_number>', sms_views.get_sms_conversation, name='get_sms_conversation'),
    path('sms/conversations', sms_views.get_all_sms_conversations, name='get_all_sms_conversations'),
    path('sms/balance', sms_views.get_sms_balance, name='get_sms_balance'),
]
