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
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import Question, Subject, Paper, Topic, Section
from .serializers import (
    QuestionListSerializer, QuestionDetailSerializer,
    QuestionCreateSerializer, QuestionBulkCreateSerializer
)
from .utils import success_response, error_response
from .exam_paper_template import _process_question_text

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
        
        # Optimized query: use select_related to fetch all related data in one query
        # This prevents N+1 query problem (1 query instead of 1 + 5*N queries)
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
    
    # Get questions by subject and creator
    by_subject_creator = Question.objects.filter(
        is_active=True
    ).select_related('subject', 'created_by').values(
        'subject__name',
        'created_by__id',
        'created_by__full_name'
    ).annotate(
        count=Count('id')
    ).order_by('subject__name', '-count')
    
    # Organize by subject with creator breakdown
    subject_breakdown = {}
    for item in by_subject_creator:
        subject_name = item['subject__name']
        if subject_name not in subject_breakdown:
            subject_breakdown[subject_name] = {
                'subjectName': subject_name,
                'total': 0,
                'creators': []
            }
        
        creator_name = item['created_by__full_name'] or 'Unknown'
        creator_id = item['created_by__id']
        question_count = item['count']
        
        subject_breakdown[subject_name]['total'] += question_count
        subject_breakdown[subject_name]['creators'].append({
            'creatorId': str(creator_id) if creator_id else None,
            'creatorName': creator_name,
            'count': question_count
        })
    
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
            ],
            'bySubjectWithCreators': list(subject_breakdown.values())
        }
    )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_creator_statistics(request):
    
    from django.db.models import Count, Q
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Get all active questions with creator info
    questions = Question.objects.filter(
        is_active=True
    ).select_related('created_by', 'subject')
    
    total_questions = questions.count()
    
    # Get all creators who have created questions
    creator_stats = questions.values(
        'created_by__id',
        'created_by__full_name',
        'created_by__phone_number'
    ).annotate(
        total_questions=Count('id')
    ).order_by('-total_questions')
    
    total_creators = creator_stats.count()
    average_per_creator = round(total_questions / total_creators, 2) if total_creators > 0 else 0
    
    # Build top contributors list
    top_contributors = []
    for idx, creator in enumerate(creator_stats, start=1):
        creator_id = creator['created_by__id']
        creator_name = creator['created_by__full_name'] or 'Unknown'
        creator_phone = creator['created_by__phone_number']
        question_count = creator['total_questions']
        percentage = round((question_count / total_questions * 100), 2) if total_questions > 0 else 0
        
        top_contributors.append({
            'rank': idx,
            'creatorId': str(creator_id) if creator_id else None,
            'creatorName': creator_name,
            'phoneNumber': creator_phone,
            'totalQuestions': question_count,
            'percentage': percentage
        })
    
    # Get subject breakdown per creator
    creator_subject_breakdown = questions.values(
        'created_by__id',
        'created_by__full_name',
        'subject__id',
        'subject__name'
    ).annotate(
        count=Count('id')
    ).order_by('created_by__full_name', 'subject__name')
    
    # Organize by creator
    creators_with_subjects = {}
    for item in creator_subject_breakdown:
        creator_id = str(item['created_by__id']) if item['created_by__id'] else 'unknown'
        creator_name = item['created_by__full_name'] or 'Unknown'
        
        if creator_id not in creators_with_subjects:
            creators_with_subjects[creator_id] = {
                'creatorId': creator_id if creator_id != 'unknown' else None,
                'creatorName': creator_name,
                'subjects': [],
                'totalQuestions': 0
            }
        
        creators_with_subjects[creator_id]['subjects'].append({
            'subjectId': str(item['subject__id']),
            'subjectName': item['subject__name'],
            'count': item['count']
        })
        creators_with_subjects[creator_id]['totalQuestions'] += item['count']
    
    # Sort by total questions descending
    subject_breakdown_per_creator = sorted(
        creators_with_subjects.values(),
        key=lambda x: x['totalQuestions'],
        reverse=True
    )
    
    # Get questions by subject
    questions_by_subject = questions.values(
        'subject__id',
        'subject__name'
    ).annotate(
        total_questions=Count('id'),
        unique_creators=Count('created_by__id', distinct=True)
    ).order_by('-total_questions')
    
    subjects_summary = []
    for subject in questions_by_subject:
        subject_id = str(subject['subject__id'])
        subject_name = subject['subject__name']
        question_count = subject['total_questions']
        creator_count = subject['unique_creators']
        percentage = round((question_count / total_questions * 100), 2) if total_questions > 0 else 0
        
        subjects_summary.append({
            'subjectId': subject_id,
            'subjectName': subject_name,
            'totalQuestions': question_count,
            'uniqueCreators': creator_count,
            'percentage': percentage
        })
    
    return success_response(
        'Creator statistics retrieved successfully',
        {
            'overallSummary': {
                'totalCreators': total_creators,
                'totalQuestions': total_questions,
                'averagePerCreator': average_per_creator,
                'generatedAt': timezone.now().isoformat()
            },
            'topContributors': top_contributors,
            'subjectBreakdownPerCreator': subject_breakdown_per_creator,
            'questionsBySubject': subjects_summary
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
    if mode not in ['essay', 'graph', 'regular1', 'regular2','map','regular3']:
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
    elif mode == 'map' :
        question.is_essay = False
        question.is_graph = False   
        question.is_map = True
    elif mode == 'regular3':
        question.is_essay = False
        question.is_graph = False
        question.is_map = False
        
    question.save()
    return success_response('Question mode updated successfully.', {
        'id': str(question.id),
        'is_essay': question.is_essay,
        'is_graph': question.is_graph
    })


# ==================== PRINTABLE TOPIC DOCUMENT VIEW ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_topic_printable_document(request):
    """
    Generate a printable document for questions in a topic or entire paper
    
    GET /api/topics/printable-document?subject_id=<uuid>&topic_id=<uuid>
    OR
    GET /api/topics/printable-document?subject_id=<uuid>&paper_id=<uuid>
    
    Returns HTML document with:
    - Topic/Paper name as title
    - Questions numbered sequentially
    - For paper-level: questions grouped by topic
    - Each question shows its paper name and topic
    - Answer follows each question
    - Images displayed inline
    """
    subject_id = request.query_params.get('subject_id')
    topic_id = request.query_params.get('topic_id')
    paper_id = request.query_params.get('paper_id')
    
    # Validate parameters
    if not subject_id:
        return error_response(
            'Missing required parameters',
            {'error': 'subject_id is required'},
            status.HTTP_400_BAD_REQUEST
        )
    
    if not topic_id and not paper_id:
        return error_response(
            'Missing required parameters',
            {'error': 'Either topic_id or paper_id is required'},
            status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Fetch subject
        subject = Subject.objects.get(id=subject_id)
        
        # Determine if we're generating for a topic or entire paper
        is_paper_level = bool(paper_id and not topic_id)
        
        if is_paper_level:
            # Paper-level document generation
            paper = Paper.objects.get(id=paper_id)
            
            # Verify paper belongs to subject
            if paper.subject_id != subject.id:
                return error_response(
                    'Invalid relationship',
                    {'error': 'Paper does not belong to the specified subject'},
                    status.HTTP_400_BAD_REQUEST
                )
            
            # Fetch all topics for this paper
            topics = Topic.objects.filter(paper_id=paper_id, is_active=True).order_by('name')
            
            if not topics.exists():
                return error_response(
                    'No topics found',
                    {'error': 'No active topics found for this paper'},
                    status.HTTP_404_NOT_FOUND
                )
            
            # Fetch all active questions for this paper, grouped by topic
            questions = Question.objects.filter(
                paper_id=paper_id,
                is_active=True
            ).select_related(
                'paper', 'section', 'subject', 'topic'
            ).order_by('topic__name', 'created_at')
            
            if not questions.exists():
                return error_response(
                    'No questions found',
                    {'error': 'No active questions found for this paper'},
                    status.HTTP_404_NOT_FOUND
                )
            
            # Group questions by topic
            from collections import defaultdict
            questions_by_topic = defaultdict(list)
            question_number = 1
            
            for question in questions:
                topic_name = question.topic.name if question.topic else 'Uncategorized'
                questions_by_topic[topic_name].append({
                    'number': question_number,
                    'question': question,
                    'paper_name': question.paper.name,
                    'topic_name': topic_name,
                    'section_name': question.section.name if question.section else None,
                    'marks': question.marks,
                })
                question_number += 1
            
            document_title = f"{paper.name}"
            total_questions = questions.count()
            
        else:
            # Topic-level document generation (original behavior)
            topic = Topic.objects.get(id=topic_id)
            
            # Verify topic belongs to subject
            if topic.paper.subject_id != subject.id:
                return error_response(
                    'Invalid relationship',
                    {'error': 'Topic does not belong to the specified subject'},
                    status.HTTP_400_BAD_REQUEST
                )
            
            # Fetch all active questions for this topic
            questions = Question.objects.filter(
                topic_id=topic_id,
                is_active=True
            ).select_related(
                'paper', 'section', 'subject', 'topic'
            ).order_by('created_at')
            
            if not questions.exists():
                return error_response(
                    'No questions found',
                    {'error': 'No active questions found for this topic'},
                    status.HTTP_404_NOT_FOUND
                )
            
            # Group as single topic
            questions_by_topic = {
                topic.name: [
                    {
                        'number': index,
                        'question': question,
                        'paper_name': question.paper.name,
                        'topic_name': topic.name,
                        'section_name': question.section.name if question.section else None,
                        'marks': question.marks,
                    }
                    for index, question in enumerate(questions, start=1)
                ]
            }
            
            document_title = topic.name
            total_questions = questions.count()
            document_title = topic.name
            total_questions = questions.count()
        
        # Create HTML content
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{document_title} - Questions and Answers</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                margin: 0;
                padding: 0;
            }}
            .page-break {{
                page-break-before: always;
            }}
            .no-print {{
                display: none;
            }}
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            line-height: 1.6;
            color: #333;
            max-width: 210mm;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #333;
            padding-bottom: 15px;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin: 10px 0;
            text-transform: uppercase;
        }}
        
        .header .subject-name {{
            font-size: 18px;
            color: #666;
            margin: 5px 0;
        }}
        
        .print-info {{
            text-align: right;
            font-size: 12px;
            color: #999;
            margin-bottom: 20px;
        }}
        
        .topic-section {{
            margin-top: 40px;
            margin-bottom: 30px;
        }}
        
        .topic-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .topic-header h2 {{
            margin: 0;
            font-size: 22px;
            font-weight: 600;
        }}
        
        .topic-header .topic-count {{
            font-size: 14px;
            margin-top: 5px;
            opacity: 0.9;
        }}
        
        .question-container {{
            margin-bottom: 40px;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
            background-color: #fafafa;
        }}
        
        .question-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ccc;
        }}
        
        .question-number {{
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .question-meta {{
            font-size: 14px;
            color: #666;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .paper-badge {{
            background-color: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
        }}
        
        .topic-badge {{
            background-color: #9b59b6;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
        }}
        
        .marks-badge {{
            background-color: #27ae60;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
        }}
        
        .question-section {{
            margin-bottom: 25px;
        }}
        
        .section-title {{
            font-weight: bold;
            font-size: 16px;
            color: #2c3e50;
            margin-bottom: 10px;
            padding: 8px;
            background-color: #ecf0f1;
            border-left: 4px solid #3498db;
        }}
        
        .question-text, .answer-text {{
            font-size: 14px;
            line-height: 1.8;
            white-space: pre-wrap;
            padding: 10px;
        }}
        
        .answer-section {{
            background-color: #e8f5e9;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin-top: 15px;
        }}
        
        .answer-section .section-title {{
            background-color: #c8e6c9;
            border-left-color: #27ae60;
        }}
        
        .inline-image {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 15px auto;
            border: 1px solid #ddd;
            padding: 5px;
            background-color: white;
        }}
        
        .positioned-image {{
            max-width: 300px;
            height: auto;
            margin: 10px;
            border: 1px solid #ddd;
            padding: 5px;
            background-color: white;
        }}
        
        .no-print {{
            margin: 20px 0;
            text-align: center;
        }}
        
        .print-button {{
            background-color: #3498db;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        
        .print-button:hover {{
            background-color: #2980b9;
        }}
        
        .total-questions {{
            text-align: center;
            font-size: 14px;
            color: #666;
            margin: 20px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
    </style>
</head>
<body>    
    <div class="header">
        <div class="subject-name">{subject.name}</div>
        <h1>{document_title}</h1>
        <div class="subject-name">Questions and Answers</div>
    </div>
    
    <div class="print-info no-print">
        Generated on: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}
    </div>
    
    <div class="total-questions">
        Total Questions: {total_questions}
    </div>
"""
        
        # Add questions grouped by topic
        for topic_name, questions_data in questions_by_topic.items():
            # Add topic header only for paper-level documents with multiple topics
            if is_paper_level and len(questions_by_topic) > 1:
                html_content += f"""
    <div class="topic-section">
        <div class="topic-header">
            <h2>{topic_name}</h2>
            <div class="topic-count">{len(questions_data)} question(s)</div>
        </div>
"""
            
            # Add each question in this topic
            for q_data in questions_data:
                question = q_data['question']
                
                # Prepare images for question text processing
                question_images_list = []
                if question.question_inline_images:
                    for idx, img_url in enumerate(question.question_inline_images):
                        question_images_list.append({
                            'id': idx + 1,
                            'url': img_url,
                            'name': f'Question image {idx + 1}'
                        })
                
                # Process question text with all formatting (images, fractions, tables, etc.)
                processed_question_text = _process_question_text(
                    question.question_text,
                    images=question_images_list,
                    answer_lines=None
                )
                
                # Prepare images for answer text processing
                answer_images_list = []
                if question.answer_inline_images:
                    for idx, img_url in enumerate(question.answer_inline_images):
                        answer_images_list.append({
                            'id': idx + 1,
                            'url': img_url,
                            'name': f'Answer image {idx + 1}'
                        })
                
                # Process answer text with all formatting
                processed_answer_text = _process_question_text(
                    question.answer_text,
                    images=answer_images_list,
                    answer_lines=None
                )
                
                html_content += f"""
    <div class="question-container">
        <div class="question-header">
            <span class="question-number">Question {q_data['number']}</span>
            <div class="question-meta">
                <span class="paper-badge">{q_data['paper_name']}</span>"""
                
                # Show topic badge for paper-level documents
                if is_paper_level:
                    html_content += f"""
                <span class="topic-badge">{q_data['topic_name']}</span>"""
                
                html_content += f"""
                <span class="marks-badge">{q_data['marks']} marks</span>
            </div>
        </div>
        
        <div class="question-section">
            <div class="section-title">Question</div>
            <div class="question-text">{processed_question_text}</div>
        </div>
        
        <div class="answer-section">
            <div class="section-title">Answer</div>
            <div class="answer-text">{processed_answer_text}</div>
        </div>
    </div>
"""
            
            # Close topic section for paper-level documents
            if is_paper_level and len(questions_by_topic) > 1:
                html_content += """
    </div>
"""
        
        # Close HTML
        html_content += """
</body>
</html>
"""
        
        # Return HTML response
        filename_safe = document_title.replace(" ", "_").replace("/", "-")
        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = f'inline; filename="{filename_safe}_Questions_Answers.html"'
        
        logger.info(f"Generated printable document for {document_title} ({total_questions} questions)")
        
        return response
        
    except Subject.DoesNotExist:
        return error_response(
            'Subject not found',
            {'error': 'Subject with the specified ID does not exist'},
            status.HTTP_404_NOT_FOUND
        )
    except Topic.DoesNotExist:
        return error_response(
            'Topic not found',
            {'error': 'Topic with the specified ID does not exist'},
            status.HTTP_404_NOT_FOUND
        )
    except Paper.DoesNotExist:
        return error_response(
            'Paper not found',
            {'error': 'Paper with the specified ID does not exist'},
            status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error generating printable document: {str(e)}")
        return error_response(
            'Server error',
            {'error': str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
