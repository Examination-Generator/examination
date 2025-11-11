# Default System Users

Default users are automatically created during deployment for immediate access to the system.

## 🔑 Pre-Configured Users

### Admin User
- **Phone Number:** `0000000001`
- **Password:** `0000`
- **Role:** Admin
- **Permissions:** Full system access - manage users, subjects, papers, questions

### Editor User
- **Phone Number:** `0000000002`
- **Password:** `0000`
- **Role:** Editor
- **Permissions:** Create and edit subjects, papers, topics, sections, and questions

## 🚀 Quick Login

### Frontend Login
1. Visit https://examination-frontend.vercel.app
2. Click **Login**
3. Enter phone: `0000000001` (admin) or `0000000002` (editor)
4. Enter password: `0000`
5. Click **Login**

### API Login

**PowerShell:**
```powershell
$body = @{
    phoneNumber = '0000000001'
    password = '0000'
} | ConvertTo-Json

Invoke-RestMethod -Uri 'https://examination-s3np.vercel.app/api/login' `
    -Method Post `
    -ContentType 'application/json' `
    -Body $body
```

**Curl:**
```bash
curl -X POST https://examination-s3np.vercel.app/api/login \
    -H 'Content-Type: application/json' \
    -d '{"phoneNumber":"0000000001","password":"0000"}'
```

## ⚙️ How It Works

Default users are created automatically during Vercel deployment:

1. **Build Script** (`build.sh`) runs during deployment
2. **Management Command** (`create_default_users`) executes
3. **Users Created** if they don't already exist
4. **OTP Bypassed** - these users have `otp_verified=True`

## 🔧 Manual Creation

If automatic creation fails, manually create the users:

### Local Development
```bash
cd django_backend
python manage.py create_default_users
```

### Verify Creation
```bash
# Check database health
curl https://examination-s3np.vercel.app/api/database/health

# Should show: "user_count": 2
```

## ⚠️ Security Recommendations

**IMPORTANT:** These are temporary accounts for initial setup.

### For Production:
1. ✅ **Login** with default admin account
2. ✅ **Create** your own admin account with a strong password
3. ✅ **Test** your new account works
4. ✅ **Disable** or delete default accounts
5. ✅ **Enable SMS OTP** when you subscribe to an SMS service

## 🛠️ Troubleshooting

### Cannot Login
- Verify password is exactly `0000` (four zeros)
- Check users exist: visit `/api/database/health`
- Ensure backend URL is correct
- Clear browser cache and try again

### Users Not Created
- Check Vercel deployment logs
- Run manually: `python manage.py create_default_users`
- Verify database connection is working

### Need to Reset Password
```bash
cd django_backend
python verify_default_users.py  # Resets passwords to 0000
```

## 📱 Future: SMS Integration

When you add SMS OTP (e.g., Twilio, Africa's Talking):

1. Update `api/auth_views.py` with SMS provider credentials
2. Add environment variables to Vercel
3. New users will receive OTP codes via SMS
4. Default users will remain for admin access

Until then, default users bypass OTP verification for convenience.
