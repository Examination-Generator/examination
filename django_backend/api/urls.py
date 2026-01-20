from django.urls import path
from django.http import JsonResponse
from . import auth_views, physics_paper_generation, subject_views, question_views, database_views, paper_generation_views, georaphy_paper_generator,kiswahili_paper_generator, business_paper_generator,cre_paper_generator,agriculture_paper_generator

from . import biology_paper2_generation


# test route to check API status
def api_root(request):
    return JsonResponse({
        'status': 'online',
        'message': 'Examination System API',
        'version': '1.0',
        'endpoints': {
            'database': '/api/database/health',
            'auth': '/api/login',
            'subjects': '/api/subjects',
            'questions': '/api/questions',
            'papers': '/api/papers/generated'
        }
    })

urlpatterns = [
    # ROOT ENDPOINT 
    path('', api_root, name='api-root'),
    
    # DATABASE MANAGEMENT ROUTES 
    # These endpoints handle automatic database setup and migrations
    path('database/initialize', database_views.initialize_database, name='database-initialize'),
    path('database/health', database_views.database_health, name='database-health'),
    path('database/create-admin', database_views.create_superuser, name='create-admin'),
    path('database/create-defaults', database_views.create_default_users, name='create-defaults'),
    
    # specific question delete (hard delete)
    path('questions/hard-delete/<uuid:question_id>/', question_views.hard_delete_question),
    
    # setting question mode 
    path('questions/set-mode/<uuid:question_id>/', question_views.set_question_mode),
    
    # AUTHENTICATION ROUTES 
    # Auth endpoints without 'auth/' prefix to match frontend expectations
    path('send-otp', auth_views.send_otp, name='send-otp'),
    path('verify-otp', auth_views.verify_otp, name='verify-otp'),
    path('register', auth_views.register, name='register'),
    path('login', auth_views.login, name='login'),
    path('forgot-password', auth_views.forgot_password, name='forgot-password'),
    path('reset-password', auth_views.reset_password, name='reset-password'),
    
    # SUBJECT ROUTES 
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
    
    # QUESTION ROUTES 
    path('questions', question_views.questions_list_create, name='questions-list-create'),
    path('questions/<uuid:question_id>', question_views.question_detail, name='question-detail'),
    path('questions/search/similar', question_views.search_similar_questions, name='search-similar'),
    path('questions/search-similar/', question_views.search_similar_questions_post, name='search-similar-post'),
    path('questions/bulk', question_views.bulk_create_questions, name='bulk-create'),
    path('questions/stats/overview', question_views.get_question_stats, name='question-stats'),
    path('questions/creator-statistics/', question_views.get_creator_statistics, name='creator-statistics'),
    
    # PAPER GENERATION ROUTES 
    # KCSE Biology Paper 1 generation endpoints
    path('papers/generate', paper_generation_views.generate_paper, name='generate-paper'),
    path('papers/generated', paper_generation_views.list_generated_papers, name='list-generated-papers'),
    path('papers/generated/<uuid:paper_id>', paper_generation_views.get_generated_paper, name='get-generated-paper'),
    path('papers/generated/<uuid:paper_id>/view/', paper_generation_views.view_full_paper, name='view-full-paper'),
    path('papers/generated/<uuid:paper_id>/coverpage/', paper_generation_views.coverpage_data, name='coverpage-data'),
    path('papers/generated/<uuid:paper_id>/preview/', paper_generation_views.preview_full_exam, name='preview-full-exam'),
    path('papers/generated/<uuid:paper_id>/download/', paper_generation_views.download_paper, name='download-paper'),
    path('papers/generated/<uuid:paper_id>/status', paper_generation_views.update_paper_status, name='update-paper-status'),
    path('papers/<uuid:paper_id>/configuration', paper_generation_views.get_paper_configuration, name='get-paper-config'),
    path('papers/<uuid:paper_id>/configuration/update', paper_generation_views.update_paper_configuration, name='update-paper-config'),
    path('papers/<uuid:paper_id>/topics/statistics', paper_generation_views.get_topic_statistics, name='topic-statistics'),
    path('questions/<uuid:question_id>/check_graph_essay', paper_generation_views.check_question_graph_essay_status, name='check-graph-essay'),
    
    # BIOLOGY PAPER 2 GENERATION ROUTES 
    # KCSE Biology Paper 2 specific generation endpoints
    path('papers/biology-paper2/validate', biology_paper2_generation.validate_paper2_pool, name='validate-paper2-pool'),
    path('papers/biology-paper2/generate', biology_paper2_generation.generate_biology_paper2, name='generate-biology-paper2'),
    
    # PHYSICS GENERATION ROUTES 
    path('papers/physics-paper/validate', physics_paper_generation.validate_physics_paper_pool, name='validate-physics-paper'),
    path('papers/physics-paper/generate', physics_paper_generation.generate_physics_paper, name='generate-physics-paper'),


    # CHEMISTRY GENERATION ROUTES 
    path('papers/chemistry/validate', paper_generation_views.validate_chemistry_paper_pool, name='validate-chemistry-paper'),
    path('papers/chemistry/generate', paper_generation_views.generate_chemistry_paper, name='generate-chemistry-paper'),


    # MATHEMATICS GENERATION ROUTES 
    path('papers/mathematics-paper/validate', paper_generation_views.validate_mathematics_paper_pool, name='validate-mathematics-paper'),
    path('papers/mathematics-paper/generate', paper_generation_views.generate_mathematics_paper, name='generate-mathematics-paper'),
    # GEOGRAPHY GENERATION ROUTES 
    path('papers/geography-paper/validate', georaphy_paper_generator.validate_geography_paper_pool, name='validate-geography-paper'),
    path('papers/geography-paper/generate', georaphy_paper_generator.generate_geography_paper, name='generate-geography-paper'),

    # ENGLISH GENERATION ROUTES 
    path('papers/english-paper/validate', paper_generation_views.validate_english_paper_pool, name='validate-english-paper'),
    path('papers/english-paper/generate', paper_generation_views.generate_english_paper, name='generate-english-paper'),
    
    # KISWAHILI GENERATION ROUTES 
    path('papers/kiswahili-paper/validate', kiswahili_paper_generator.validate_kiswahili_paper_pool, name='validate-kiswahili-paper'),
    path('papers/kiswahili-paper/generate', kiswahili_paper_generator.generate_kiswahili_paper, name='generate-kiswahili-paper'),
    
    # BUSINESS STUDIES GENERATION ROUTES 
    path('papers/business-paper/validate', business_paper_generator.validate_business_paper_pool, name='validate-business-paper'),
    path('papers/business-paper/generate', business_paper_generator.generate_business_paper, name='generate-business-paper'),
    
    # CHRISTIAN RELIGIOUS EDUCATION GENERATION ROUTES 
    path('papers/cre-paper/validate', cre_paper_generator.validate_cre_paper_pool, name='validate-cre-paper'),
    path('papers/cre-paper/generate', cre_paper_generator.generate_cre_paper, name='generate-cre-paper'),
    
    # AGRICULTURE GENERATION ROUTES 
    path('papers/agriculture-paper/validate', agriculture_paper_generator.validate_agriculture_paper_pool, name='validate-agriculture-paper'),
    path('papers/agriculture-paper/generate', agriculture_paper_generator.generate_agriculture_paper, name='generate-agriculture-paper'),
]


    
        
