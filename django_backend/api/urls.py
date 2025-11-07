"""
URL Configuration for API app
"""

from django.urls import path
from . import auth_views, subject_views, question_views, database_views

urlpatterns = [
    # ==================== DATABASE MANAGEMENT ROUTES ====================
    # These endpoints handle automatic database setup and migrations
    path('database/initialize', database_views.initialize_database, name='database-initialize'),
    path('database/health', database_views.database_health, name='database-health'),
    path('database/create-admin', database_views.create_superuser, name='create-admin'),
    path('database/create-defaults', database_views.create_default_users, name='create-defaults'),
    
    # ==================== AUTHENTICATION ROUTES ====================
    # Auth endpoints without 'auth/' prefix to match frontend expectations
    path('send-otp', auth_views.send_otp, name='send-otp'),
    path('verify-otp', auth_views.verify_otp, name='verify-otp'),
    path('register', auth_views.register, name='register'),
    path('login', auth_views.login, name='login'),
    path('forgot-password', auth_views.forgot_password, name='forgot-password'),
    path('reset-password', auth_views.reset_password, name='reset-password'),
    
    # ==================== SUBJECT ROUTES ====================
    path('subjects', subject_views.subjects_list_create, name='subjects-list-create'),
    path('subjects/<uuid:subject_id>', subject_views.subject_detail, name='subject-detail'),
    
    # Paper routes
    path('subjects/<uuid:subject_id>/papers', subject_views.add_paper, name='add-paper'),
    path('subjects/<uuid:subject_id>/papers/<uuid:paper_id>', subject_views.get_paper, name='get-paper'),
    
    # Section routes
    path('subjects/<uuid:subject_id>/papers/<uuid:paper_id>/sections', 
         subject_views.add_section, name='add-section'),
    
    # Topic routes
    path('subjects/<uuid:subject_id>/papers/<uuid:paper_id>/topics', 
         subject_views.add_topic, name='add-topic'),
    path('subjects/<uuid:subject_id>/papers/<uuid:paper_id>/topics', 
         subject_views.get_topics, name='get-topics'),
    path('subjects/topics/<uuid:topic_id>', subject_views.topic_detail, name='topic-detail'),
    
    # Section routes (individual)
    path('subjects/sections/<uuid:section_id>', subject_views.section_detail, name='section-detail'),
    
    # ==================== QUESTION ROUTES ====================
    path('questions', question_views.questions_list_create, name='questions-list-create'),
    path('questions/<uuid:question_id>', question_views.question_detail, name='question-detail'),
    path('questions/search/similar', question_views.search_similar_questions, name='search-similar'),
    path('questions/search-similar/', question_views.search_similar_questions_post, name='search-similar-post'),
    path('questions/bulk', question_views.bulk_create_questions, name='bulk-create'),
    path('questions/stats/overview', question_views.get_question_stats, name='question-stats'),
]
