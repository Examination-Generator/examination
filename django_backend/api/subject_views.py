"""
Subject Management Views for Examination System
Equivalent to Node.js subjects routes
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Subject, Paper, Section, Topic
from .serializers import (
    SubjectSerializer, SubjectCreateSerializer, PaperSerializer,
    SectionSerializer, TopicSerializer
)
from .utils import success_response, error_response

logger = logging.getLogger(__name__)


# ==================== COMBINED VIEWS FOR REST API ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def subjects_list_create(request):
    """
    List all subjects (GET) or create new subject (POST)
    GET /api/subjects
    POST /api/subjects
    """
    if request.method == 'GET':
        # List subjects
        active = request.query_params.get('active')
        logger.info(f"[SUBJECT] Fetching all subjects, active filter: {active}")
        
        queryset = Subject.objects.all()
        if active is not None:
            queryset = queryset.filter(is_active=(active.lower() == 'true'))
        
        subjects = queryset.prefetch_related(
            'papers__sections',
            'papers__topics'
        ).order_by('name')
        
        logger.info(f"[SUBJECT] Found {subjects.count()} subjects")
        serializer = SubjectSerializer(subjects, many=True)
        
        return success_response(
            'Subjects retrieved successfully',
            serializer.data
        )
    
    elif request.method == 'POST':
        # Create subject
        logger.info(f"[SUBJECT] Creating subject by user {request.user.phone_number}")
        
        serializer = SubjectCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        name = serializer.validated_data['name']
        if Subject.objects.filter(name=name).exists():
            return error_response(
                'Subject already exists',
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            subject = serializer.save()
        
        complete_subject = Subject.objects.prefetch_related(
            'papers__sections',
            'papers__topics'
        ).get(id=subject.id)
        
        logger.info(f"[SUBJECT] Subject created successfully: {subject.name}")
        
        return success_response(
            'Subject created successfully',
            SubjectSerializer(complete_subject).data,
            status=status.HTTP_201_CREATED
        )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def subject_detail(request, subject_id):
    """
    Get, update, or delete a specific subject
    GET /api/subjects/<id>
    PUT /api/subjects/<id> - Full replacement
    PATCH /api/subjects/<id> - Partial update
    DELETE /api/subjects/<id>
    """
    try:
        subject = Subject.objects.prefetch_related(
            'papers__sections',
            'papers__topics'
        ).get(id=subject_id)
    except Subject.DoesNotExist:
        return error_response(
            'Subject not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = SubjectSerializer(subject)
        return success_response(
            'Subject retrieved successfully',
            serializer.data
        )
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = SubjectCreateSerializer(
            subject,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            serializer.save()
        
        # Fetch updated subject with all relations
        updated_subject = Subject.objects.prefetch_related(
            'papers__sections',
            'papers__topics'
        ).get(id=subject.id)
        
        return success_response(
            'Subject updated successfully',
            SubjectSerializer(updated_subject).data
        )
    
    elif request.method == 'DELETE':
        # Hard delete - actually remove from database
        subject.delete()
        
        return success_response('Subject deleted successfully')


# ==================== INDIVIDUAL VIEW FUNCTIONS (kept for reference) ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_subject(request):
    """
    Create new subject with papers, sections, and topics
    POST /api/subjects
    """
    logger.info(f"[SUBJECT] Creating subject by user {request.user.phone_number}")
    
    serializer = SubjectCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if not serializer.is_valid():
        return error_response('Validation error', serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    # Check if subject already exists
    name = serializer.validated_data['name']
    if Subject.objects.filter(name=name).exists():
        return error_response(
            'Subject already exists',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create subject
    subject = serializer.save()
    
    # Fetch complete subject with relations
    complete_subject = Subject.objects.prefetch_related(
        'papers__sections',
        'papers__topics'
    ).get(id=subject.id)
    
    logger.info(f"[SUBJECT] Subject created successfully: {subject.name}")
    
    return success_response(
        'Subject created successfully',
        SubjectSerializer(complete_subject).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_subjects(request):
    """
    Get all subjects with papers
    GET /api/subjects
    """
    active = request.query_params.get('active')
    
    logger.info(f"[SUBJECT] Fetching all subjects, active filter: {active}")
    
    # Build query
    queryset = Subject.objects.all()
    if active is not None:
        queryset = queryset.filter(is_active=(active.lower() == 'true'))
    
    # Prefetch related data
    subjects = queryset.prefetch_related(
        'papers__sections',
        'papers__topics'
    ).order_by('name')
    
    # Filter papers by active status if specified
    if active is not None:
        for subject in subjects:
            subject.papers.set(
                subject.papers.filter(is_active=(active.lower() == 'true'))
            )
    
    logger.info(f"[SUBJECT] Found {subjects.count()} subjects")
    
    serializer = SubjectSerializer(subjects, many=True)
    
    return success_response(
        'Subjects retrieved successfully',
        serializer.data
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subject(request, subject_id):
    """
    Get single subject with all details
    GET /api/subjects/:id
    """
    try:
        subject = Subject.objects.prefetch_related(
            'papers__sections',
            'papers__topics'
        ).get(id=subject_id)
    except Subject.DoesNotExist:
        return error_response(
            'Subject not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = SubjectSerializer(subject)
    
    return success_response(
        'Subject retrieved successfully',
        serializer.data
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_subject(request, subject_id):
    """
    Update subject
    PUT /api/subjects/:id
    """
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return error_response(
            'Subject not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update fields
    name = request.data.get('name')
    description = request.data.get('description')
    is_active = request.data.get('isActive')
    
    if name:
        subject.name = name
    if description is not None:
        subject.description = description
    if is_active is not None:
        subject.is_active = is_active
    
    subject.save()
    
    serializer = SubjectSerializer(subject)
    
    return success_response(
        'Subject updated successfully',
        serializer.data
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_subject(request, subject_id):
    """
    Delete subject (soft delete - set isActive to false)
    DELETE /api/subjects/:id
    """
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return error_response(
            'Subject not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Soft delete
    subject.is_active = False
    subject.save()
    
    return success_response('Subject deleted successfully')


# ==================== PAPER ROUTES ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_paper(request, subject_id):
    """
    Add paper to subject
    POST /api/subjects/:id/papers
    Expected payload:
    {
        "name": "Paper 1",
        "description": "Paper description",
        "duration_hours": 2,
        "duration_minutes": 30,
        "total_marks": 80,
        "time_allocation": 150
    }
    """
    try:
        subject = Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return error_response(
            'Subject not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    name = request.data.get('name')
    description = request.data.get('description', '')
    duration_hours = request.data.get('duration_hours', 2)
    duration_minutes = request.data.get('duration_minutes', 0)
    total_marks = request.data.get('total_marks', 80)
    time_allocation = request.data.get('time_allocation', 120)
    
    if not name:
        return error_response(
            'Paper name is required',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create paper
    paper = Paper.objects.create(
        name=name,
        description=description,
        subject=subject,
        created_by=request.user,
        duration_hours=duration_hours,
        duration_minutes=duration_minutes,
        total_marks=total_marks,
        time_allocation=time_allocation
    )
    
    serializer = PaperSerializer(paper)
    
    return success_response(
        'Paper added successfully',
        serializer.data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_paper(request, subject_id, paper_id):
    """
    Get, update, or delete a single paper with sections and topics
    GET /api/subjects/:subjectId/papers/:paperId
    PUT /api/subjects/:subjectId/papers/:paperId
    DELETE /api/subjects/:subjectId/papers/:paperId
    """
    try:
        paper = Paper.objects.prefetch_related(
            'sections',
            'topics'
        ).get(id=paper_id, subject_id=subject_id)
    except Paper.DoesNotExist:
        return error_response(
            'Paper not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = PaperSerializer(paper)
        return success_response(
            'Paper retrieved successfully',
            serializer.data
        )
    
    elif request.method == 'PUT':
        # Update paper name
        serializer = PaperSerializer(
            paper,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return error_response(
                'Validation error',
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        return success_response(
            'Paper updated successfully',
            serializer.data
        )
    
    elif request.method == 'DELETE':
        # Hard delete - actually remove from database
        paper.delete()
        
        return success_response('Paper deleted successfully')


# ==================== SECTION ROUTES ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_section(request, subject_id, paper_id):
    """
    Add section to paper
    POST /api/subjects/:subjectId/papers/:paperId/sections
    """
    try:
        paper = Paper.objects.get(id=paper_id, subject_id=subject_id)
    except Paper.DoesNotExist:
        return error_response(
            'Paper not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    name = request.data.get('name')
    description = request.data.get('description', '')
    
    if not name:
        return error_response(
            'Section name is required',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get next order number
    order = Section.objects.filter(paper=paper).count()
    
    # Create section
    section = Section.objects.create(
        name=name,
        description=description,
        paper=paper,
        order=order,
        created_by=request.user
    )
    
    serializer = SectionSerializer(section)
    
    return success_response(
        'Section added successfully',
        serializer.data,
        status=status.HTTP_201_CREATED
    )


# ==================== TOPIC ROUTES ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_topic(request, subject_id, paper_id):
    """
    Add topic to paper
    POST /api/subjects/:subjectId/papers/:paperId/topics
    """
    try:
        paper = Paper.objects.get(id=paper_id, subject_id=subject_id)
    except Paper.DoesNotExist:
        return error_response(
            'Paper not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    name = request.data.get('name')
    description = request.data.get('description', '')
    section_id = request.data.get('sectionId')
    
    if not name:
        return error_response(
            'Topic name is required',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify section if provided
    section = None
    if section_id:
        try:
            section = Section.objects.get(id=section_id, paper=paper)
        except Section.DoesNotExist:
            return error_response(
                'Invalid section',
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Create topic
    topic = Topic.objects.create(
        name=name,
        description=description,
        paper=paper,
        created_by=request.user
    )
    
    serializer = TopicSerializer(topic)
    
    return success_response(
        'Topic added successfully',
        serializer.data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def topic_detail(request, topic_id):
    """
    Get, update, or delete a specific topic
    GET /api/subjects/topics/<topic_id>
    PUT /api/subjects/topics/<topic_id>
    DELETE /api/subjects/topics/<topic_id>
    """
    try:
        topic = Topic.objects.get(id=topic_id)
    except Topic.DoesNotExist:
        return error_response(
            'Topic not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = TopicSerializer(topic)
        return success_response(
            'Topic retrieved successfully',
            serializer.data
        )
    
    elif request.method == 'PUT':
        serializer = TopicSerializer(
            topic,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return error_response(
                'Validation error',
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        return success_response(
            'Topic updated successfully',
            serializer.data
        )
    
    elif request.method == 'DELETE':
        # Hard delete - actually remove from database
        topic.delete()
        
        return success_response('Topic deleted successfully')


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def section_detail(request, section_id):
    """
    Get, update, or delete a specific section
    GET /api/subjects/sections/<section_id>
    PUT /api/subjects/sections/<section_id>
    DELETE /api/subjects/sections/<section_id>
    """
    try:
        section = Section.objects.get(id=section_id)
    except Section.DoesNotExist:
        return error_response(
            'Section not found',
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = SectionSerializer(section)
        return success_response(
            'Section retrieved successfully',
            serializer.data
        )
    
    elif request.method == 'PUT':
        serializer = SectionSerializer(
            section,
            data=request.data,
            partial=True
        )
        
        if not serializer.is_valid():
            return error_response(
                'Validation error',
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        
        return success_response(
            'Section updated successfully',
            serializer.data
        )
    
    elif request.method == 'DELETE':
        # Hard delete - actually remove from database
        section.delete()
        
        return success_response('Section deleted successfully')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_topics(request, subject_id, paper_id):
    """
    Get topics filtered by paper (and optionally by section)
    GET /api/subjects/:subjectId/papers/:paperId/topics
    """
    section_id = request.query_params.get('sectionId')
    
    # Build query
    query = {
        'paper_id': paper_id,
        'is_active': True
    }
    
    if section_id:
        query['section_id'] = section_id
    
    # Get topics
    topics = Topic.objects.filter(**query).order_by('name')
    
    serializer = TopicSerializer(topics, many=True)
    
    return success_response(
        'Topics retrieved successfully',
        serializer.data
    )
