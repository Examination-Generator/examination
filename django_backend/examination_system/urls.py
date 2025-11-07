"""
URL configuration for examination_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Simple home view
def home_view(request):
    """API home endpoint showing available routes"""
    return JsonResponse({
        'status': 'success',
        'message': 'Examination System API is running on Vercel! 🚀',
        'version': 'v1',
        'endpoints': {
            'api': '/api/',
            'admin': '/admin/',
            'docs_swagger': '/swagger/',
            'docs_redoc': '/redoc/',
            'authentication': {
                'send_otp': '/api/send-otp',
                'verify_otp': '/api/verify-otp',
                'register': '/api/register',
                'login': '/api/login',
                'forgot_password': '/api/forgot-password',
                'reset_password': '/api/reset-password',
            },
            'subjects': '/api/subjects',
            'questions': '/api/questions',
        },
        'database': 'Vercel Postgres',
        'deployment': 'Vercel Serverless',
    })

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Examination System API",
        default_version='v1',
        description="API documentation for Examination System with PostgreSQL backend",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@examsystem.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', home_view, name='home'),  # Home endpoint
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
