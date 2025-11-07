# Default System Users

This document describes the default users that are automatically created during deployment.

## Automatic Creation

Default users are automatically created during the Vercel build process via the `create_default_users` Django management command in `build.sh`.

## Default User Credentials

### 🔑 Admin User
- **Phone Number:** `0000000001`
- **Password:** `0000`
- **Role:** `admin`
- **Permissions:** Full system access, can create/edit/delete all content

### ✏️ Editor User
- **Phone Number:** `0000000002`
- **Password:** `0000`
- **Role:** `editor`
- **Permissions:** Can create and edit content (subjects, papers, questions)

## How to Login

### Using the Frontend
1. Go to your frontend application
2. Click on Login
3. Enter phone number: `0000000001` (admin) or `0000000002` (editor)
4. Enter password: `0000`
5. Click Login

### Using the API Directly

```bash
# PowerShell
$body = @{
    phoneNumber = '0000000001'
    password = '0000'
} | ConvertTo-Json

Invoke-RestMethod -Uri 'https://examination-s3np.vercel.app/api/login' `
    -Method Post `
    -ContentType 'application/json' `
    -Body $body
```

```bash
# Curl
curl -X POST https://examination-s3np.vercel.app/api/login \
    -H 'Content-Type: application/json' \
    -d '{"phoneNumber":"0000000001","password":"0000"}'
```

## Security Notes

⚠️ **IMPORTANT:** These are default system accounts for initial setup and testing.

### Production Recommendations:
1. **Change Default Passwords:** After first login, change the passwords for these accounts
2. **Create Personal Accounts:** Create your own admin/editor accounts with strong passwords
3. **Disable Default Accounts:** Consider disabling these accounts once you have your own
4. **Enable SMS OTP:** Once you subscribe to an SMS API service, enable OTP verification for all users

## Manual Creation (If Needed)

If automatic creation fails, you can manually create these users:

### Option 1: Django Management Command
```bash
python manage.py create_default_users
```

### Option 2: SQL Script
Execute the SQL script in your Vercel Postgres database:
```bash
psql $POSTGRES_URL -f insert_default_users.sql
```

### Option 3: Python Script
```bash
python register_editor.py
# Follow the interactive prompts
```

## Verification

To verify the users were created, check the database:

```sql
SELECT phone_number, full_name, role, is_active 
FROM users 
WHERE phone_number IN ('0000000001', '0000000002');
```

Or use the API health endpoint:
```bash
curl https://examination-s3np.vercel.app/api/database/health
```

## Troubleshooting

### Users Not Created
1. Check Vercel deployment logs for the build.sh output
2. Verify database connection is working
3. Run the management command manually: `python manage.py create_default_users`

### Cannot Login
1. Verify users exist in database
2. Check that `otp_verified` is `true` for these users
3. Ensure `is_active` is `true`
4. Verify the backend URL is correct

### Password Issues
The password is exactly 4 digits: `0000` (four zeros)
- Make sure you're not adding extra characters
- Password is case-insensitive (all numbers)

## Future SMS Integration

Once you subscribe to an SMS API service (e.g., Twilio, Africa's Talking):

1. Update the OTP service in `api/auth_views.py`
2. Configure SMS credentials in Vercel environment variables
3. Enable OTP verification for all new registrations
4. Regular users will receive SMS OTP codes for login/registration

For now, these default users bypass OTP verification (`otp_verified=True`).
