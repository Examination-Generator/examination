"""
Script to verify and reset default user passwords
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examination_system.settings')
django.setup()

from api.models import User

print("="*70)
print("VERIFYING DEFAULT USERS")
print("="*70)

# Check admin user
try:
    admin = User.objects.get(phone_number='0000000001')
    print(f"\n✓ Admin user found:")
    print(f"  ID: {admin.id}")
    print(f"  Name: {admin.full_name}")
    print(f"  Role: {admin.role}")
    print(f"  Active: {admin.is_active}")
    print(f"  OTP Verified: {admin.otp_verified}")
    
    # Reset password
    admin.set_password('0000')
    admin.save()
    print(f"  ✓ Password reset to: 0000")
    
    # Test password
    if admin.check_password('0000'):
        print(f"  ✓ Password verification: SUCCESS")
    else:
        print(f"  ✗ Password verification: FAILED")
    
except User.DoesNotExist:
    print("\n✗ Admin user NOT found!")

# Check editor user
try:
    editor = User.objects.get(phone_number='0000000002')
    print(f"\n✓ Editor user found:")
    print(f"  ID: {editor.id}")
    print(f"  Name: {editor.full_name}")
    print(f"  Role: {editor.role}")
    print(f"  Active: {editor.is_active}")
    print(f"  OTP Verified: {editor.otp_verified}")
    
    # Reset password
    editor.set_password('0000')
    editor.save()
    print(f"  ✓ Password reset to: 0000")
    
    # Test password
    if editor.check_password('0000'):
        print(f"  ✓ Password verification: SUCCESS")
    else:
        print(f"  ✗ Password verification: FAILED")
    
except User.DoesNotExist:
    print("\n✗ Editor user NOT found!")

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70)
print("\nYou can now login with:")
print("  Admin:  Phone: 0000000001, Password: 0000")
print("  Editor: Phone: 0000000002, Password: 0000")
print("="*70 + "\n")
