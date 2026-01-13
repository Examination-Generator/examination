"""
Django middleware to automatically run migrations on first request
This ensures database is always up-to-date
"""
import logging
from django.core.management import call_command
from django.db import connection
from threading import Lock

logger = logging.getLogger(__name__)

# Global flag to track if migrations have been run
_migrations_checked = False
_migrations_lock = Lock()


class AutoMigrateMiddleware:
    """
    Middleware that automatically runs pending migrations on the first request.
    This ensures the database is always initialized and up-to-date.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        global _migrations_checked
        
        # Only check migrations once per deployment
        if not _migrations_checked:
            with _migrations_lock:
                # Double-check inside lock to prevent race conditions
                if not _migrations_checked:
                    self._check_and_run_migrations()
                    _migrations_checked = True
        
        response = self.get_response(request)
        return response
    
    def _check_and_run_migrations(self):
        """Check for pending migrations and run them automatically"""
        try:
            # First, check if database is accessible
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            logger.info("[AUTO-MIGRATE] Database is accessible")
            
            # Check for pending migrations
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                logger.warning(f"[AUTO-MIGRATE] Found {len(plan)} pending migrations. Running them now...")
                
                # Run migrations
                call_command('migrate', '--noinput', verbosity=0)
                
                logger.info("[AUTO-MIGRATE]  Migrations completed successfully!")
            else:
                logger.info("[AUTO-MIGRATE]  No pending migrations. Database is up-to-date.")
            
            # Verify tables exist
            from api.models import User
            user_count = User.objects.count()
            logger.info(f"[AUTO-MIGRATE]  Database verified. Users: {user_count}")
            
        except Exception as e:
            logger.error(f"[AUTO-MIGRATE]  Error during auto-migration: {e}")
            # Don't raise exception - let the app continue
            # Users can manually run migrations via /api/database/initialize
