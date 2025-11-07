"""
Django Management Command: Create Default Users
Automatically creates admin and editor users if they don't exist
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import User
import sys


class Command(BaseCommand):
    help = 'Create default admin and editor users'

    def handle(self, *args, **options):
        """Create default users"""
        
        self.stdout.write('='*70)
        self.stdout.write(self.style.SUCCESS('Creating Default Users'))
        self.stdout.write('='*70)
        
        users_created = []
        users_existed = []
        
        # Define default users
        default_users = [
            {
                'phone_number': '0000000001',
                'full_name': 'System Admin',
                'password': '0000',
                'role': 'admin',
                'otp_verified': True,
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            },
            {
                'phone_number': '0000000002',
                'full_name': 'System Editor',
                'password': '0000',
                'role': 'editor',
                'otp_verified': True,
                'is_active': True
            }
        ]
        
        with transaction.atomic():
            for user_data in default_users:
                phone = user_data['phone_number']
                role = user_data['role']
                
                try:
                    # Check if user already exists
                    if User.objects.filter(phone_number=phone).exists():
                        existing_user = User.objects.get(phone_number=phone)
                        users_existed.append(f"{role.upper()}: {phone} ({existing_user.full_name})")
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠ {role.upper()} user already exists: {phone}'
                            )
                        )
                        continue
                    
                    # Create new user
                    password = user_data.pop('password')
                    user = User(**user_data)
                    user.set_password(password)
                    user.save()
                    
                    users_created.append(f"{role.upper()}: {phone} (Password: {password})")
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Created {role.upper()} user: {phone}'
                        )
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ Failed to create {role} user: {str(e)}'
                        )
                    )
        
        # Print summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('='*70)
        
        if users_created:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Created {len(users_created)} new user(s):'))
            for user_info in users_created:
                self.stdout.write(f'  • {user_info}')
        
        if users_existed:
            self.stdout.write(self.style.WARNING(f'\n⚠ {len(users_existed)} user(s) already existed:'))
            for user_info in users_existed:
                self.stdout.write(f'  • {user_info}')
        
        if not users_created and not users_existed:
            self.stdout.write(self.style.ERROR('\n✗ No users were created or found'))
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('DEFAULT USERS SETUP COMPLETE'))
        self.stdout.write('='*70)
        
        # Print login credentials
        if users_created:
            self.stdout.write('\n' + '='*70)
            self.stdout.write(self.style.SUCCESS('LOGIN CREDENTIALS'))
            self.stdout.write('='*70)
            self.stdout.write('\nADMIN USER:')
            self.stdout.write('  Phone: 0000000001')
            self.stdout.write('  Password: 0000')
            self.stdout.write('\nEDITOR USER:')
            self.stdout.write('  Phone: 0000000002')
            self.stdout.write('  Password: 0000')
            self.stdout.write('\n' + '='*70 + '\n')
