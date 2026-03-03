# Backend Requirements for Messaging Feature

This document outlines the backend API endpoints and database schema required to support the messaging feature implemented in the frontend.

## Overview

The messaging feature consists of two main modules:
1. **SMS Messaging** - Enables admins to send SMS to users via their phone numbers
2. **System Messaging** - Internal support messaging between users and admins

---

## Database Schema

### 1. System Messages Table

```sql
CREATE TABLE system_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sender_name VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    parent_message_id UUID REFERENCES system_messages(id) ON DELETE CASCADE,
    quoted_text TEXT,
    is_from_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

CREATE INDEX idx_system_messages_sender ON system_messages(sender_id);
CREATE INDEX idx_system_messages_parent ON system_messages(parent_message_id);
CREATE INDEX idx_system_messages_read ON system_messages(is_read);
CREATE INDEX idx_system_messages_created ON system_messages(created_at DESC);
```

### 2. SMS Messages Table

```sql
CREATE TABLE sms_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_phone VARCHAR(20) NOT NULL,
    recipient_name VARCHAR(255),
    message TEXT NOT NULL,
    direction VARCHAR(10) NOT NULL, -- 'outgoing' or 'incoming'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'failed'
    sms_provider_id VARCHAR(255), -- External SMS provider message ID
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sms_messages_sender ON sms_messages(sender_id);
CREATE INDEX idx_sms_messages_recipient ON sms_messages(recipient_phone);
CREATE INDEX idx_sms_messages_created ON sms_messages(created_at DESC);
```

### 3. User Contacts View

Create a view or query to search for user contacts by name or phone number:

```sql
-- Assuming you have a users table with phone numbers
CREATE VIEW user_contacts AS
SELECT 
    id,
    name,
    phone_number,
    email
FROM users
WHERE phone_number IS NOT NULL
ORDER BY name;
```

---

## API Endpoints

### SMS Messaging Endpoints

#### 1. Search Contacts
```
GET /api/messaging/contacts/search?q={query}

Description: Search for contacts by name or phone number
Auth Required: Yes (Admin only)
Query Parameters:
  - q: Search query (min 2 characters)

Response:
[
  {
    "id": "uuid",
    "name": "John Doe",
    "phone_number": "+254712345678",
    "email": "john@example.com"
  }
]
```

#### 2. Send SMS
```
POST /api/messaging/sms/send

Description: Send SMS to one or multiple recipients
Auth Required: Yes (Admin only)
Request Body:
{
  "recipients": ["+254712345678", "+254723456789"],
  "message": "Message text"
}

Response:
{
  "success": true,
  "sent_count": 2,
  "failed_count": 0,
  "message": "SMS sent successfully"
}
```

#### 3. Get SMS Conversation
```
GET /api/messaging/sms/conversation/{phone_number}

Description: Get SMS conversation history with a specific phone number
Auth Required: Yes (Admin only)
Path Parameters:
  - phone_number: URL-encoded phone number

Response:
[
  {
    "id": "uuid",
    "message": "Message text",
    "direction": "outgoing",
    "sent_at": "2026-03-03T10:30:00Z",
    "status": "delivered"
  }
]
```

#### 4. Get All SMS Conversations
```
GET /api/messaging/sms/conversations

Description: Get list of all SMS conversations with summary
Auth Required: Yes (Admin only)

Response:
[
  {
    "phone_number": "+254712345678",
    "name": "John Doe",
    "last_message": "Last message text",
    "last_message_at": "2026-03-03T10:30:00Z",
    "message_count": 10
  }
]
```

### System Messaging Endpoints

#### 1. Send System Message
```
POST /api/messaging/system/send

Description: Send a support message (user to admin)
Auth Required: Yes
Request Body:
{
  "subject": "Help with exam",
  "message": "Message text"
}

Response:
{
  "id": "uuid",
  "sender_id": "uuid",
  "sender_name": "User Name",
  "subject": "Help with exam",
  "message": "Message text",
  "is_read": false,
  "created_at": "2026-03-03T10:30:00Z"
}
```

#### 2. Get System Messages
```
GET /api/messaging/system/messages?unreadOnly=true

Description: Get inbox messages (for admin, shows all user messages; for users, shows their own)
Auth Required: Yes
Query Parameters:
  - unreadOnly: (optional) Get only unread messages

Response:
[
  {
    "id": "uuid",
    "sender_id": "uuid",
    "sender_name": "User Name",
    "subject": "Help with exam",
    "message": "Message text",
    "is_read": false,
    "replies_count": 2,
    "created_at": "2026-03-03T10:30:00Z"
  }
]
```

#### 3. Get Message Conversation
```
GET /api/messaging/system/messages/{message_id}/conversation

Description: Get a message thread with all replies
Auth Required: Yes
Path Parameters:
  - message_id: Message UUID

Response:
{
  "id": "uuid",
  "sender_id": "uuid",
  "sender_name": "User Name",
  "subject": "Help with exam",
  "message": "Original message",
  "is_read": true,
  "created_at": "2026-03-03T10:30:00Z",
  "replies": [
    {
      "id": "uuid",
      "sender_id": "uuid",
      "sender_name": "Admin Name",
      "message": "Reply text",
      "quoted_text": "Part of original message",
      "is_from_admin": true,
      "created_at": "2026-03-03T11:00:00Z"
    }
  ]
}
```

#### 4. Reply to Message
```
POST /api/messaging/system/messages/{message_id}/reply

Description: Reply to a system message
Auth Required: Yes
Path Parameters:
  - message_id: Original message UUID
Request Body:
{
  "message": "Reply text",
  "quotedText": "Optional quoted text from original"
}

Response:
{
  "id": "uuid",
  "sender_id": "uuid",
  "sender_name": "Admin Name",
  "message": "Reply text",
  "quoted_text": "Quoted text",
  "is_from_admin": true,
  "parent_message_id": "uuid",
  "created_at": "2026-03-03T11:00:00Z"
}
```

#### 5. Mark Message as Read
```
PUT /api/messaging/system/messages/{message_id}/read

Description: Mark a message as read
Auth Required: Yes
Path Parameters:
  - message_id: Message UUID

Response:
{
  "id": "uuid",
  "is_read": true,
  "updated_at": "2026-03-03T11:00:00Z"
}
```

#### 6. Get Unread Count
```
GET /api/messaging/system/unread-count

Description: Get count of unread messages
Auth Required: Yes

Response:
{
  "count": 5
}
```

#### 7. Delete Message
```
DELETE /api/messaging/system/messages/{message_id}

Description: Soft delete a message
Auth Required: Yes
Path Parameters:
  - message_id: Message UUID

Response:
{
  "success": true,
  "message": "Message deleted successfully"
}
```

---

## SMS Integration

### Recommended SMS Provider: Africa's Talking

The SMS feature requires integration with an SMS provider. Africa's Talking is recommended for this implementation as it's widely used in Kenya and supports the required features.

### Setup Instructions:

1. **Sign up for Africa's Talking**
   - Visit: https://africastalking.com
   - Create an account and get API credentials

2. **Install SDK** (Python example)
   ```bash
   pip install africastalking
   ```

3. **Configuration**
   ```python
   import africastalking
   
   # Initialize SDK
   africastalking.initialize(
       username='YOUR_USERNAME',
       api_key='YOUR_API_KEY'
   )
   
   # Get SMS service
   sms = africastalking.SMS
   ```

4. **Sending SMS**
   ```python
   def send_sms(recipients, message):
       try:
           response = sms.send(
               message=message,
               recipients=recipients,
               sender_id="speedstar"  # Your approved sender ID
           )
           return response
       except Exception as e:
           print(f"Error: {e}")
           return None
   ```

### Alternative Providers:
- **Twilio** - https://www.twilio.com
- **AWS SNS** - https://aws.amazon.com/sns/
- **Vonage (Nexmo)** - https://www.vonage.com

---

## Security Considerations

1. **Authentication & Authorization**
   - All endpoints require authentication
   - SMS endpoints require admin role
   - Users can only see their own messages (except admins)

2. **Input Validation**
   - Validate phone numbers (E.164 format recommended)
   - Sanitize all text inputs to prevent XSS
   - Limit message length (SMS: 160 chars, System: 5000 chars)

3. **Rate Limiting**
   - Implement rate limiting on SMS endpoints
   - Suggested: 10 SMS per minute per admin
   - System messages: 5 per minute per user

4. **Data Privacy**
   - Store phone numbers securely
   - Implement soft delete for messages
   - Add message retention policy

5. **SMS Credits**
   - Monitor SMS credit usage
   - Add warning system for low credits
   - Implement cost tracking per admin

---

## Environment Variables

Add these to your `.env` file:

```bash
# SMS Provider Configuration
SMS_PROVIDER=africastalking
SMS_USERNAME=your_username
SMS_API_KEY=your_api_key
SMS_SENDER_ID=speedstar

# Messaging Configuration
MAX_SMS_PER_MINUTE=10
MAX_SYSTEM_MESSAGES_PER_MINUTE=5
MESSAGE_MAX_LENGTH=5000
SMS_MAX_LENGTH=160
```

---

## Testing

### Test Data Setup

```sql
-- Insert test users with phone numbers
INSERT INTO users (id, name, email, phone_number, role) VALUES
('uuid1', 'Test User 1', 'user1@test.com', '+254712345678', 'user'),
('uuid2', 'Test User 2', 'user2@test.com', '+254723456789', 'user'),
('uuid3', 'Admin User', 'admin@test.com', '+254734567890', 'admin');

-- Insert test system messages
INSERT INTO system_messages (sender_id, sender_name, subject, message, is_from_admin) VALUES
('uuid1', 'Test User 1', 'Test Support Request', 'I need help with exams', false);
```

### API Testing with cURL

```bash
# Send SMS
curl -X POST http://localhost:8000/api/messaging/sms/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["+254712345678"],
    "message": "Test message from Speedstar Exam"
  }'

# Send System Message
curl -X POST http://localhost:8000/api/messaging/system/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test Support",
    "message": "This is a test message"
  }'
```

---

## Implementation Checklist

- [ ] Create database tables and indexes
- [ ] Set up SMS provider account (Africa's Talking recommended)
- [ ] Implement contact search endpoint
- [ ] Implement SMS sending endpoint with provider integration
- [ ] Implement SMS conversation retrieval
- [ ] Implement system message CRUD operations
- [ ] Implement message reply functionality
- [ ] Implement unread count tracking
- [ ] Add authentication middleware
- [ ] Add authorization checks (admin-only for SMS)
- [ ] Implement rate limiting
- [ ] Add input validation and sanitization
- [ ] Set up error handling and logging
- [ ] Add unit tests for all endpoints
- [ ] Add integration tests with mock SMS provider
- [ ] Document API in Swagger/OpenAPI
- [ ] Set up monitoring for SMS usage and costs

---

## Future Enhancements

1. **Real-time Updates**
   - Implement WebSocket for instant message notifications
   - Add push notifications for mobile apps

2. **Message Analytics**
   - Track message open/read rates
   - SMS delivery statistics
   - Response time metrics

3. **Advanced Features**
   - Message templates for common responses
   - Scheduled SMS sending
   - Bulk import contacts from CSV
   - Message categories/tags
   - Message attachments

4. **Multi-language Support**
   - Support for messages in multiple languages
   - Auto-translation features

---

## Support

For questions or issues with the messaging implementation, contact the development team or refer to:
- Africa's Talking Documentation: https://developers.africastalking.com
- Project GitHub Repository: [Your repo URL]
