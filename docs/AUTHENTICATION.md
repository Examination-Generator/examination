# Authentication Guide

Understanding authentication and user management in the Examination System.

## Authentication Method

The system uses **phone number + password** authentication with JWT tokens.

- **Username:** Phone number (e.g., `0000000001`)
- **Password:** 4-digit PIN (e.g., `0000`)
- **Token:** JWT for API requests

## User Flow

### Current Flow (Default Users)

```
1. User visits login page
2. Enters phone number and 4-digit PIN
3. System validates credentials
4. System returns JWT token
5. Token used for subsequent requests
```

### Future Flow (With SMS OTP)

```
1. User requests registration
2. System sends OTP via SMS
3. User verifies OTP
4. User sets 4-digit PIN
5. Account created
6. User can login with phone + PIN
```

## Login Process

### Via Frontend

1. Navigate to login page
2. Enter credentials:
   - **Admin:** Phone: `0000000001`, Password: `0000`
   - **Editor:** Phone: `0000000002`, Password: `0000`
3. Click "Login"
4. Redirected to dashboard

### Via API

**Request:**
```http
POST /api/login
Content-Type: application/json

{
  "phoneNumber": "0000000001",
  "password": "0000"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid",
      "fullName": "System Admin",
      "phoneNumber": "0000000001",
      "role": "admin"
    }
  }
}
```

## Using Authentication Token

Include the token in the `Authorization` header for protected endpoints:

```http
GET /api/subjects
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**PowerShell Example:**
```powershell
$token = "your-jwt-token-here"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "https://examination-s3np.vercel.app/api/subjects" `
    -Headers $headers
```

**JavaScript Example:**
```javascript
const token = localStorage.getItem('authToken');
const response = await fetch('https://examination-s3np.vercel.app/api/subjects', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

## User Roles & Permissions

### User (Regular)
**Permissions:**
- View subjects, papers, topics
- View questions
- Read-only access

**Cannot:**
- Create or edit content
- Delete anything
- Access admin features

### Editor
**Permissions:**
- All User permissions
- Create subjects
- Create papers, topics, sections
- Create and edit questions
- Upload images
- Manage own content

**Cannot:**
- Delete subjects
- Manage other users
- Access admin settings

### Admin
**Permissions:**
- All Editor permissions
- Delete any content
- Manage all users
- Access all system features
- Full database access

## Password Requirements

- **Length:** Exactly 4 digits
- **Format:** Numbers only (0-9)
- **Examples:** `0000`, `1234`, `9876`
- **Invalid:** `abc`, `12`, `12345`, `12ab`

## Security Features

### Password Storage
- Passwords are hashed using **bcrypt**
- Never stored in plain text
- Salt automatically generated
- One-way encryption

### Token Security
- JWT tokens expire after 7 days
- Contains: user_id, token_type, expiry
- Signed with SECRET_KEY
- Cannot be modified without detection

### OTP Verification (Future)
- 6-digit codes
- Expires in 10 minutes (600 seconds)
- Max 3 attempts
- Purpose-specific (registration/login/reset)

## Default Users

Pre-configured accounts for immediate access:

| Role | Phone | Password | Purpose |
|------|-------|----------|---------|
| Admin | 0000000001 | 0000 | Full system access |
| Editor | 0000000002 | 0000 | Content creation |

See [Default Users](./DEFAULT_USERS.md) for details.

## API Endpoints

### Authentication Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/login` | POST | No | Login with phone + password |
| `/api/send-otp` | POST | No | Send OTP (future) |
| `/api/verify-otp` | POST | No | Verify OTP (future) |
| `/api/register` | POST | No | Register new user (future) |
| `/api/forgot-password` | POST | No | Request password reset (future) |
| `/api/reset-password` | POST | No | Reset password (future) |

### Protected Endpoints

All other endpoints require authentication:
- `/api/subjects` - Subject management
- `/api/questions` - Question management
- `/api/database/*` - Database operations (public for now)

## Common Issues

### Login Fails

**Check:**
1. Phone number is correct (e.g., `0000000001`)
2. Password is exactly 4 digits
3. No spaces before/after credentials
4. Backend is accessible

**Test:**
```bash
curl -X POST https://examination-s3np.vercel.app/api/login \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber":"0000000001","password":"0000"}'
```

### Token Expired

**Solution:**
- Login again to get a new token
- Tokens last 7 days
- Frontend should handle automatic re-login

### "Not authenticated" Error

**Causes:**
- Missing Authorization header
- Invalid token format
- Expired token
- Token not prefixed with "Bearer "

**Fix:**
```javascript
// Correct format:
headers: {
  'Authorization': 'Bearer ' + token  // Note the space after Bearer
}

// Wrong format:
headers: {
  'Authorization': token  // Missing "Bearer "
}
```

## Best Practices

### For Developers

1. **Store tokens securely:**
   ```javascript
   // In browser
   localStorage.setItem('authToken', token);
   
   // Read token
   const token = localStorage.getItem('authToken');
   ```

2. **Include token in all requests:**
   ```javascript
   // Create axios instance with default header
   const api = axios.create({
     baseURL: 'https://examination-s3np.vercel.app/api',
     headers: {
       'Authorization': `Bearer ${token}`
     }
   });
   ```

3. **Handle auth errors:**
   ```javascript
   try {
     const response = await api.get('/subjects');
   } catch (error) {
     if (error.response.status === 401) {
       // Redirect to login
       window.location.href = '/login';
     }
   }
   ```

### For Production

1. **Change default passwords immediately**
2. **Create your own admin account**
3. **Disable default accounts** once you have your own
4. **Enable HTTPS** (automatic on Vercel)
5. **Set up SMS OTP** when ready
6. **Monitor failed login attempts**
7. **Rotate SECRET_KEY** periodically

## Future Enhancements

### Planned Features
- ✅ Phone number authentication (implemented)
- ✅ JWT tokens (implemented)
- ✅ Role-based access (implemented)
- ⏳ SMS OTP verification (requires SMS service)
- ⏳ Password reset via OTP
- ⏳ Two-factor authentication
- ⏳ Session management
- ⏳ Login history tracking

### SMS Integration

To enable SMS OTP:

1. Subscribe to SMS service (Twilio, Africa's Talking, etc.)
2. Add credentials to Vercel environment variables
3. Update `api/auth_views.py` with SMS provider
4. Enable OTP verification in settings
5. Test OTP flow thoroughly

See deployment documentation for SMS setup details.
