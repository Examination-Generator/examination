"""
Management command to sync data from Vercel Postgres to cPanel PostgreSQL
Usage: python manage.py sync_vercel_to_cpanel --vercel-db-url="postgresql://..."
"""

import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.db import connections, transaction
from django.apps import apps
from django.conf import settings


class Command(BaseCommand):
    help = 'Sync all data from Vercel Postgres to cPanel PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--vercel-db-url',
            type=str,
            required=True,
            help='Vercel PostgreSQL connection URL (postgresql://user:pass@host:port/db)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be synced without making changes'
        )
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running migrations on target database'
        )

    def handle(self, *args, **options):
        vercel_db_url = options['vercel_db_url']
        dry_run = options['dry_run']
        skip_migrations = options['skip_migrations']

        self.stdout.write(self.style.WARNING('='*70))
        self.stdout.write(self.style.WARNING('DATABASE SYNC: Vercel → cPanel'))
        self.stdout.write(self.style.WARNING('='*70))
        
        if dry_run:
            self.stdout.write(self.style.NOTICE('DRY RUN MODE - No changes will be made'))
        
        # Setup Vercel database connection BEFORE any database operations
        self.stdout.write('\n📡 Setting up Vercel database connection...')
        db_config = self._parse_db_url(vercel_db_url)
        
        # Add Vercel database to settings
        from django.db import connections
        from django.db.utils import ConnectionHandler
        
        # Create a complete database config with all Django 4.2+ required settings
        vercel_db = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_config['NAME'],
            'USER': db_config['USER'],
            'PASSWORD': db_config['PASSWORD'],
            'HOST': db_config['HOST'],
            'PORT': db_config['PORT'],
            'CONN_MAX_AGE': 0,
            'CONN_HEALTH_CHECKS': False,
            'AUTOCOMMIT': True,
            'ATOMIC_REQUESTS': False,
            'TIME_ZONE': None,
            'OPTIONS': {},
            'TEST': {
                'CHARSET': None,
                'COLLATION': None,
                'NAME': None,
                'MIRROR': None,
            },
        }
        
        # Add to settings.DATABASES
        settings.DATABASES['vercel'] = vercel_db
        
        # Test connections
        try:
            self.stdout.write('🔍 Testing Vercel connection...')
            vercel_cursor = connections['vercel'].cursor()
            vercel_cursor.execute("SELECT version();")
            vercel_version = vercel_cursor.fetchone()[0]
            self.stdout.write(self.style.SUCCESS(f'✅ Vercel connected: {vercel_version[:50]}...'))
            
            self.stdout.write('🔍 Testing cPanel connection...')
            cpanel_cursor = connections['default'].cursor()
            cpanel_cursor.execute("SELECT version();")
            cpanel_version = cpanel_cursor.fetchone()[0]
            self.stdout.write(self.style.SUCCESS(f'✅ cPanel connected: {cpanel_version[:50]}...'))
        except Exception as e:
            raise CommandError(f'❌ Connection failed: {str(e)}')

        # Run migrations on cPanel if needed
        if not skip_migrations:
            self.stdout.write('\n🔧 Running migrations on cPanel database...')
            from django.core.management import call_command
            call_command('migrate', '--database=default', interactive=False)
            self.stdout.write(self.style.SUCCESS('✅ Migrations complete'))

        # Get all models from the api app
        self.stdout.write('\n📊 Analyzing models to sync...')
        api_models = apps.get_app_config('api').get_models()
        
        # Order models by dependencies (to handle foreign keys)
        ordered_models = self._order_models_by_dependency(api_models)
        
        self.stdout.write(f'Found {len(ordered_models)} models to sync:')
        for model in ordered_models:
            self.stdout.write(f'  - {model._meta.label}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN: Counting records only...'))
            self._dry_run_sync(ordered_models)
            return

        # Confirm before proceeding
        self.stdout.write(self.style.WARNING('\n⚠️  WARNING: This will REPLACE all data in cPanel database!'))
        confirm = input('Type "yes" to continue: ')
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('❌ Sync cancelled'))
            return

        # Perform the sync
        self.stdout.write('\n🚀 Starting data sync...\n')
        self._sync_data(ordered_models)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✅ SYNC COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write('Your cPanel database now has all data from Vercel.')
        self.stdout.write('Users can now continue using the cPanel production database.\n')

    def _parse_db_url(self, db_url):
        """Parse PostgreSQL URL into components"""
        from urllib.parse import urlparse
        
        parsed = urlparse(db_url)
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path[1:],  # Remove leading /
            'USER': parsed.username,
            'PASSWORD': parsed.password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or 5432,
        }

    def _order_models_by_dependency(self, models):
        """Order models to handle foreign key dependencies"""
        # Simple ordering: User first, then other models
        ordered = []
        user_model = None
        
        for model in models:
            if model.__name__ == 'User':
                user_model = model
            else:
                ordered.append(model)
        
        # Put User model first if it exists
        if user_model:
            ordered.insert(0, user_model)
        
        return ordered

    def _dry_run_sync(self, models):
        """Show what would be synced without making changes"""
        total_records = 0
        
        for model in models:
            vercel_count = model.objects.using('vercel').count()
            cpanel_count = model.objects.using('default').count()
            total_records += vercel_count
            
            status = '➕ NEW' if cpanel_count == 0 else f'🔄 REPLACE ({cpanel_count} existing)'
            self.stdout.write(
                f'  {model._meta.label:30} | Vercel: {vercel_count:5} | cPanel: {cpanel_count:5} | {status}'
            )
        
        self.stdout.write(f'\nTotal records to sync: {total_records}')

    def _sync_data(self, models):
        """Sync all data from Vercel to cPanel"""
        total_synced = 0
        
        for model in models:
            model_name = model._meta.label
            self.stdout.write(f'\n📦 Syncing {model_name}...')
            
            # Get all records from Vercel
            vercel_records = list(model.objects.using('vercel').all())
            vercel_count = len(vercel_records)
            
            if vercel_count == 0:
                self.stdout.write(self.style.WARNING(f'  ⚠️  No records found in Vercel'))
                continue
            
            try:
                with transaction.atomic(using='default'):
                    # Clear existing data in cPanel
                    cpanel_deleted = model.objects.using('default').all().delete()[0]
                    if cpanel_deleted > 0:
                        self.stdout.write(f'  🗑️  Deleted {cpanel_deleted} existing records')
                    
                    # Bulk create in cPanel
                    # We need to handle this carefully to preserve IDs and relationships
                    synced_count = 0
                    batch_size = 100
                    
                    for i in range(0, vercel_count, batch_size):
                        batch = vercel_records[i:i + batch_size]
                        
                        # Create records in cPanel with the same IDs
                        for record in batch:
                            # Get all field values including ID
                            field_values = {}
                            for field in model._meta.fields:
                                field_values[field.name] = getattr(record, field.name)
                            
                            # Create new instance in cPanel database
                            new_record = model(**field_values)
                            new_record.save(using='default', force_insert=True)
                            synced_count += 1
                        
                        # Show progress
                        progress = min(i + batch_size, vercel_count)
                        self.stdout.write(f'  ⏳ Progress: {progress}/{vercel_count}', ending='\r')
                        self.stdout.flush()
                    
                    # Reset sequence for auto-increment IDs
                    self._reset_sequence(model)
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✅ Synced {synced_count} {model_name} records' + ' '*20
                    ))
                    total_synced += synced_count
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error syncing {model_name}: {str(e)}'))
                raise CommandError(f'Sync failed at {model_name}')
        
        self.stdout.write(f'\n📊 Total records synced: {total_synced}')

    def _reset_sequence(self, model):
        """Reset the auto-increment sequence for a model's primary key"""
        try:
            from django.db import connection
            table_name = model._meta.db_table
            
            # Get the primary key field
            pk_field = model._meta.pk
            if pk_field.get_internal_type() in ['AutoField', 'BigAutoField']:
                with connection.cursor() as cursor:
                    # PostgreSQL sequence reset
                    sequence_name = f'{table_name}_{pk_field.column}_seq'
                    cursor.execute(
                        f"SELECT setval('{sequence_name}', "
                        f"COALESCE((SELECT MAX({pk_field.column}) FROM {table_name}), 1), true);"
                    )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  Could not reset sequence: {str(e)}')
            )
