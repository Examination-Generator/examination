"""
Question Management Views for Examination System
Equivalent to Node.js questions routes
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone

from .models import Question, Subject, Paper, Topic, Section
from .serializers import (
    QuestionListSerializer, QuestionDetailSerializer,
    QuestionCreateSerializer, QuestionBulkCreateSerializer
)
from .utils import success_response, error_response

logger = logging.getLogger(__name__)


# ==================== COMBINED VIEWS FOR REST API ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def questions_list_create(request):
    """
    List all questions (GET) or create new question (POST)
    GET /api/questions
    POST /api/questions
    """
    if request.method == 'GET':
        # List questions with filters
        subject_id = request.query_params.get('subject')
        paper_id = request.query_params.get('paper')
        topic_id = request.query_params.get('topic')
        section_id = request.query_params.get('section')
        is_active = request.query_params.get('isActive')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 50))
        
        queryset = Question.objects.select_related(
            'subject', 'paper', 'topic', 'section', 'created_by'
        )
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if paper_id:
            queryset = queryset.filter(paper_id=paper_id)
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
        
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        questions = queryset.order_by('-created_at')[start:end]
        
        serializer = QuestionListSerializer(questions, many=True)
        
        # Log image data to debug
        if len(serializer.data) > 0:
            first_q = serializer.data[0]
            logger.info(f"[QUESTION] First question serialized data - ID: {first_q.get('id')}")
            logger.info(f"[QUESTION] question_inline_images: {first_q.get('question_inline_images')}")
            logger.info(f"[QUESTION] answer_inline_images: {first_q.get('answer_inline_images')}")
        
        return success_response(
            'Questions retrieved successfully',
            {
                'questions': serializer.data,
                'total': total,
                'page': page,
                'pages': (total + limit - 1) // limit
            }
        )
    
    elif request.method == 'POST':
        # Create question
        serializer = QuestionCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        question = serializer.save()
        detail_serializer = QuestionDetailSerializer(question)
        
        return success_response(
            'Question created successfully',
            detail_serializer.data,
            status=status.HTTP_201_CREATED
        )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def question_detail(request, question_id):
    """
    Get, update, or delete a specific question
    GET /api/questions/<id>
    PUT /api/questions/<id>
    DELETE /api/questions/<id>
    """
    try:
        question = Question.objects.select_related(
            'subject', 'paper', 'topic', 'section', 'created_by'
        ).get(id=question_id)
    except Question.DoesNotExist:
        return error_response(
            'Question not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = QuestionDetailSerializer(question)
        return success_response(
            'Question retrieved successfully',
            serializer.data
        )
    
    elif request.method == 'PUT':
        serializer = QuestionCreateSerializer(
            question,
            data=request.data,
            context={'request': request},
            partial=True
        )
        
        if not serializer.is_valid():
            return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        question = serializer.save()
        detail_serializer = QuestionDetailSerializer(question)
        
        return success_response(
            'Question updated successfully',
            detail_serializer.data
        )
    
    elif request.method == 'DELETE':
        question.is_active = False
        question.save()
        
        return success_response('Question deleted successfully')


# ==================== INDIVIDUAL VIEW FUNCTIONS (kept for reference) ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_question(request):
    """
    Create new question with inline images
    POST /api/questions
    """
    serializer = QuestionCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if not serializer.is_valid():
        return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    # Create question
    question = serializer.save()
    
    # Return detailed view
    detail_serializer = QuestionDetailSerializer(question)
    
    return success_response(
        'Question created successfully',
        detail_serializer.data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_questions(request):
    """
    Get all questions with filters
    GET /api/questions
    """
    # Get filter parameters
    subject_id = request.query_params.get('subject')
    paper_id = request.query_params.get('paper')
    topic_id = request.query_params.get('topic')
    section_id = request.query_params.get('section')
    is_active = request.query_params.get('isActive')
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 10000))
    
    # Build query
    queryset = Question.objects.select_related(
        'subject', 'paper', 'topic', 'section', 'created_by'
    )
    
    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)
    if paper_id:
        queryset = queryset.filter(paper_id=paper_id)
    if topic_id:
        queryset = queryset.filter(topic_id=topic_id)
    if section_id:
        queryset = queryset.filter(section_id=section_id)
    if is_active is not None:
        queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
    
    # Get total count
    total = queryset.count()
    
    # Apply pagination
    start = (page - 1) * limit
    end = start + limit
    questions = queryset.order_by('-created_at')[start:end]
    
    serializer = QuestionListSerializer(questions, many=True)
    
    return success_response(
        'Questions retrieved successfully',
        {
            'questions': serializer.data,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit  # Ceiling division
        }
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question(request, question_id):
    """
    Get single question
    GET /api/questions/:id
    """
    try:
        question = Question.objects.select_related(
            'subject', 'paper', 'topic', 'section', 'created_by'
        ).get(id=question_id)
    except Question.DoesNotExist:
        return error_response(
            'Question not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = QuestionDetailSerializer(question)
    
    return success_response(
        'Question retrieved successfully',
        serializer.data
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_question(request, question_id):
    """
    Update question
    PUT /api/questions/:id
    """
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(
            'Question not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = QuestionCreateSerializer(
        question,
        data=request.data,
        context={'request': request},
        partial=True
    )
    
    if not serializer.is_valid():
        return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    # Update question
    question = serializer.save()
    
    # Return detailed view
    detail_serializer = QuestionDetailSerializer(question)
    
    return success_response(
        'Question updated successfully',
        detail_serializer.data
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_question(request, question_id):
    """
    Delete question (hard delete)
    DELETE /api/questions/:id
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🗑️ DELETE request received for question ID: {question_id}")
    
    try:
        question = Question.objects.get(id=question_id)
        logger.info(f"🗑️ Found question: {question.question_text[:50]}...")
    except Question.DoesNotExist:
        logger.error(f"🗑️ Question not found: {question_id}")
        return error_response(
            'Question not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Hard delete - permanently remove from database
    question_id_before = question.id
    question.delete()
    
    logger.info(f"🗑️ Question {question_id_before} deleted successfully from database")
    
    # Verify deletion
    try:
        Question.objects.get(id=question_id_before)
        logger.error(f"🗑️ ERROR: Question still exists after delete!")
    except Question.DoesNotExist:
        logger.info(f"🗑️ Verified: Question {question_id_before} no longer exists in database")
    
    return success_response('Question deleted successfully')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_similar_questions(request):
    """
    Search for similar questions based on text and subject
    GET /api/questions/search/similar?text=...&subject=...&limit=10
    """
    text = request.query_params.get('text')
    subject_id = request.query_params.get('subject')
    paper_id = request.query_params.get('paper')
    topic_id = request.query_params.get('topic')
    limit = int(request.query_params.get('limit', 10))
    
    if not text or len(text) < 10:
        return error_response(
            'Search text must be at least 10 characters',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Build query with text search
    queryset = Question.objects.filter(
        Q(question_text__icontains=text) | Q(answer_text__icontains=text),
        is_active=True
    )
    
    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)
    if paper_id:
        queryset = queryset.filter(paper_id=paper_id)
    if topic_id:
        queryset = queryset.filter(topic_id=topic_id)
    
    # Get questions
    questions = queryset.select_related(
        'subject', 'paper', 'topic'
    ).order_by('-created_at')[:limit]
    
    serializer = QuestionListSerializer(questions, many=True)
    
    return success_response(
        'Similar questions retrieved',
        serializer.data
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_similar_questions_post(request):
    """
    Search for similar questions using POST method (better for longer text)
    POST /api/questions/search-similar/
    Body: { "question_text": "...", "subject": "subject_id", "limit": 5 }
    """
    text = request.data.get('question_text', '')
    subject_name = request.data.get('subject', '')
    limit = request.data.get('limit', 5)
    
    if not text or len(text) < 15:
        return success_response(
            'No search performed - text too short',
            {'similar_questions': []}
        )
    
    if not subject_name:
        return error_response(
            'Subject is required',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Find subject by name
    try:
        subject = Subject.objects.get(name=subject_name)
    except Subject.DoesNotExist:
        return success_response(
            'Subject not found',
            {'similar_questions': []}
        )
    
    # Split text into words for better matching
    words = [word.strip().lower() for word in text.split() if len(word.strip()) > 3]
    
    logger.info(f'[SIMILAR] Searching for similar questions in subject: {subject_name}')
    logger.info(f'[SIMILAR] Search text: {text[:100]}...')
    logger.info(f'[SIMILAR] Extracted keywords: {words[:10]}')
    
    if not words:
        return success_response(
            'No significant words found',
            {'similar_questions': []}
        )
    
    # Build query - search for questions containing multiple keywords
    query = Q()
    for word in words[:10]:  # Limit to first 10 significant words
        query |= Q(question_text__icontains=word)
    
    # Filter by subject and active status
    queryset = Question.objects.filter(
        query,
        subject=subject,
        is_active=True
    ).select_related(
        'subject', 'paper', 'topic', 'section'
    ).distinct()
    
    # Calculate similarity score (simple keyword matching)
    results = []
    for question in queryset[:limit * 2]:  # Get more and filter later
        question_words = set(question.question_text.lower().split())
        matching_words = sum(1 for word in words if any(word in qword for qword in question_words))
        similarity_score = (matching_words / len(words)) * 100 if words else 0
        
        if similarity_score > 10:  # Only include if >10% similarity (lowered from 20%)
            results.append({
                'id': question.id,
                'question_text': question.question_text,
                'question_inline_images': question.question_inline_images,
                'question_image_positions': question.question_image_positions,
                'question_answer_lines': question.question_answer_lines,
                'answer_text': question.answer_text,
                'answer_inline_images': question.answer_inline_images,
                'answer_image_positions': question.answer_image_positions,
                'answer_answer_lines': question.answer_answer_lines,
                'topic': question.topic.name if question.topic else 'N/A',
                'paper': question.paper.name if question.paper else 'N/A',
                'section': question.section.name if question.section else 'N/A',
                'marks': question.marks,
                'status': 'Active' if question.is_active else 'Inactive',
                'similarity_score': round(similarity_score, 1),
                'timestamp': question.created_at.isoformat()
            })
    
    # Sort by similarity score and limit results
    results.sort(key=lambda x: x['similarity_score'], reverse=True)
    results = results[:limit]
    
    logger.info(f'[SIMILAR] Found {len(results)} similar questions with >10% similarity')
    if results:
        logger.info(f'[SIMILAR] Top match: {results[0]["similarity_score"]}% - {results[0]["question_text"][:50]}')
    
    return success_response(
        f'Found {len(results)} similar question(s)',
        {'similar_questions': results}
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_questions(request):
    """
    Create multiple questions at once
    POST /api/questions/bulk
    """
    questions_data = request.data.get('questions', [])
    
    if not isinstance(questions_data, list) or len(questions_data) == 0:
        return error_response(
            'Questions array is required',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = QuestionBulkCreateSerializer(
        data={'questions': questions_data},
        context={'request': request}
    )
    
    if not serializer.is_valid():
        return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    # Create questions
    questions = serializer.save()
    
    return success_response(
        f'{len(questions)} questions created successfully',
        {'count': len(questions)},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question_stats(request):
    """
    Get question statistics
    GET /api/questions/stats/overview
    """
    subject_id = request.query_params.get('subject')
    paper_id = request.query_params.get('paper')
    
    # Build query for all questions (not just active)
    queryset = Question.objects.all()
    
    if subject_id:
        queryset = queryset.filter(subject_id=subject_id)
    if paper_id:
        queryset = queryset.filter(paper_id=paper_id)
    
    # Get total counts
    total_questions = queryset.count()
    active_questions = queryset.filter(is_active=True).count()
    inactive_questions = queryset.filter(is_active=False).count()
    
    # Get overview statistics for active questions only
    overview = queryset.filter(is_active=True).aggregate(
        total_marks=Sum('marks'),
        avg_marks=Avg('marks'),
        total_usage=Sum('times_used')
    )
    
    # Get questions by subject
    by_subject = Question.objects.filter(
        is_active=True
    ).values(
        'subject__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    return success_response(
        'Statistics retrieved successfully',
        {
            # Frontend expects these keys
            'total': total_questions,
            'active': active_questions,
            'inactive': inactive_questions,
            'unknownTopics': 0,  # Can be calculated later if needed
            
            # Additional overview data
            'overview': {
                'totalQuestions': total_questions,
                'activeQuestions': active_questions,
                'inactiveQuestions': inactive_questions,
                'totalMarks': overview['total_marks'] or 0,
                'avgMarks': round(overview['avg_marks'], 2) if overview['avg_marks'] else 0,
                'totalUsage': overview['total_usage'] or 0
            },
            'bySubject': [
                {
                    'subjectName': item['subject__name'],
                    'count': item['count']
                }
                for item in by_subject
            ]
        }
    )



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def hard_delete_question(request, question_id):
    """
    Hard delete a question from the database
    DELETE /api/questions/hard-delete/<id>
    """
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(
            'Question not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    question.delete()
    
    response_data = {
        'message': 'Question permanently deleted',
        'status': status.HTTP_200_OK,
        'statusText': 'OK'
    }
    
    return success_response(
        response_data.get('message'),
        data=response_data,
        status=response_data.get('status')
    )
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_question_mode(request, question_id):
    """
    Set question mode (essay, graph, or regular) by updating is_essay and is_graph fields.
    POST /api/questions/set-mode/<question_id>/
    Body: { "mode": "essay" | "graph" | "regular" }
    """
    from .models import Question
    mode = request.data.get('mode')
    if mode not in ['essay', 'graph', 'regular1', 'regular2']:
        return error_response('Invalid mode. Must be one of: essay, graph, regular.')
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response('Question not found.', status=404)
    if mode == 'essay':
        question.is_essay = True
        question.is_graph = False
    elif mode == 'graph':
        question.is_essay = False
        question.is_graph = True
    elif mode == 'regular1' : 
        question.is_essay = False
    elif mode == 'regular2' :
        question.is_graph = False
        
    question.save()
    return success_response('Question mode updated successfully.', {
        'id': str(question.id),
        'is_essay': question.is_essay,
        'is_graph': question.is_graph
    })
