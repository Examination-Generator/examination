"""
Database management views for automatic setup and migrations
"""
import logging
from django.core.management import call_command
from django.db import connection
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from io import StringIO

from .models import User
from .utils import success_response, error_response

logger = logging.getLogger(__name__)


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def initialize_database(request):
    """
    Initialize database with all required tables and migrations.
    This endpoint can be called to ensure the database is set up.
    
    GET /api/database/initialize - Check database status
    POST /api/database/initialize - Run migrations and setup
    """
    try:
        # Check if database is accessible
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        if request.method == 'GET':
            # Check database status
            try:
                # Try to query a table
                user_count = User.objects.count()
                
                return success_response(
                    'Database is accessible and initialized',
                    {
                        'status': 'ready',
                        'users_count': user_count,
                        'database_connected': True,
                        'tables_exist': True
                    }
                )
            except Exception as e:
                # Tables don't exist yet
                return success_response(
                    'Database is accessible but not initialized',
                    {
                        'status': 'needs_migration',
                        'database_connected': True,
                        'tables_exist': False,
                        'error': str(e)
                    }
                )
        
        elif request.method == 'POST':
            # Run migrations
            output = StringIO()
            
            try:
                logger.info("[DATABASE] Running migrations...")
                call_command('migrate', '--noinput', stdout=output, stderr=output)
                migration_output = output.getvalue()
                
                logger.info(f"[DATABASE] Migrations completed: {migration_output}")
                
                # Verify tables were created
                user_count = User.objects.count()
                
                return success_response(
                    'Database initialized successfully',
                    {
                        'status': 'initialized',
                        'migrations_applied': True,
                        'users_count': user_count,
                        'output': migration_output
                    },
                    status=status.HTTP_201_CREATED
                )
                
            except Exception as migration_error:
                logger.error(f"[DATABASE] Migration error: {migration_error}")
                return error_response(
                    f'Migration failed: {str(migration_error)}',
                    {'output': output.getvalue()},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    except Exception as e:
        logger.error(f"[DATABASE] Database connection error: {e}")
        return error_response(
            'Database connection failed',
            {'error': str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def database_health(request):
    """
    Check database health and connectivity.
    GET /api/database/health
    """
    health_data = {
        'database_connected': False,
        'tables_exist': False,
        'can_query': False,
        'migrations_needed': False
    }
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_data['database_connected'] = True
        
        # Test if tables exist and are queryable
        try:
            user_count = User.objects.count()
            health_data['tables_exist'] = True
            health_data['can_query'] = True
            health_data['user_count'] = user_count
        except Exception as table_error:
            health_data['migrations_needed'] = True
            health_data['error'] = str(table_error)
        
        # Check for pending migrations
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            health_data['migrations_needed'] = True
            health_data['pending_migrations'] = len(plan)
        
        overall_status = 'healthy' if (
            health_data['database_connected'] and 
            health_data['tables_exist'] and 
            not health_data['migrations_needed']
        ) else 'unhealthy'
        
        return success_response(
            f'Database status: {overall_status}',
            health_data
        )
        
    except Exception as e:
        logger.error(f"[DATABASE] Health check failed: {e}")
        health_data['error'] = str(e)
        return error_response(
            'Database health check failed',
            health_data,
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_superuser(request):
    """
    Create initial superuser/admin account.
    POST /api/database/create-admin
    Body: { "phoneNumber": "+254...", "fullName": "Admin", "password": "1234" }
    """
    phone_number = request.data.get('phoneNumber') or request.data.get('phone_number')
    full_name = request.data.get('fullName') or request.data.get('full_name', 'Admin')
    password = request.data.get('password', '1234')
    
    if not phone_number:
        return error_response(
            'Phone number is required',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Check if admin already exists
        if User.objects.filter(role='admin').exists():
            return error_response(
                'Admin user already exists',
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create admin user
        admin_user = User.objects.create_user(
            phone_number=phone_number,
            full_name=full_name,
            password=password,
            role='admin'
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.otp_verified = True
        admin_user.save()
        
        logger.info(f"[DATABASE] Admin user created: {phone_number}")
        
        return success_response(
            'Admin user created successfully',
            {
                'user_id': str(admin_user.id),
                'phone_number': admin_user.phone_number,
                'full_name': admin_user.full_name,
                'role': admin_user.role
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"[DATABASE] Failed to create admin: {e}")
        return error_response(
            f'Failed to create admin user: {str(e)}',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
