"""
Views for KCSE Paper Generation

This module contains all API endpoints for:
- Generating KCSE Biology Paper 1 
- Retrieving generated papers
- Listing generated papers
- Managing paper configurations
- Getting topic statistics

The actual paper generation logic is in kcse_biology_paper1_generator.py (KCSEBiologyPaper1Generator class)
which uses an intelligent dynamic algorithm:
- Nested questions: 10-18 questions (55-65 marks, flexible count)
  * All questions have equal chance of selection
  * Counts marks dynamically while selecting
- Standalone questions: Fill remaining marks to reach exactly 80 marks
  * Priority: 2-mark > 3-mark > 1-mark (for exact gaps)
- Total: 18-27 questions, exactly 80 marks
"""


import logging
import time
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from .models import (
    Paper, Topic, PaperConfiguration, GeneratedPaper, Question
)
from .mathematics_generator import KCSEMathematicsPaper1Generator, KCSEMathematicsPaper2Generator
from .chemistry_paper_generator import KCSEChemistryPaper1Generator, KCSEChemistryPaper2Generator
from .english_generator import KCSEEnglishPaper1Generator, KCSEEnglishPaper2Generator,KCSEEnglishPaper3Generator
from .georaphy_paper_generator import KCSEGeographyPaper1Generator, KCSEGeographyPaper2Generator, Paper, Topic, Question
from .kcse_biology_paper1_generator import KCSEBiologyPaper1Generator
from .coverpage_templates import (
    BiologyPaper1Coverpage, 
    BiologyPaper2Coverpage, 
    BiologyPaper2MarkingSchemeCoverpage,
    BiologyPaper3Coverpage,
    PhysicsPaper1Coverpage,
    PhysicsPaper2Coverpage,
    ChemistryPaper1Coverpage,
    ChemistryPaper2Coverpage,
    MarkingSchemeCoverpage, 
    format_time_allocation
)

logger = logging.getLogger(__name__)


class PaperGenerationException(Exception):
    """Exception raised when paper generation fails"""
    pass


def _select_coverpage_class_and_default(generated_paper, paper, is_marking_scheme=False):
    """
    Select the most appropriate coverpage/marking-scheme class and default data
    for a given generated paper. This centralizes logic and makes the selection
    robust (case-insensitive, checks both metadata and paper name).

    Returns: (CoverpageClass, default_data_dict)
    """
    metadata = getattr(generated_paper, 'metadata', {}) or {}
    paper_type = (metadata.get('paper_type') or '').upper()
    subject_name = (paper.subject.name or '').upper()
    paper_name = (paper.name or '').upper()

    def is_paper1():
        return any(k in paper_type or k in paper_name for k in ('PAPER 1', 'PAPER I'))

    def is_paper2():
        return any(k in paper_type or k in paper_name for k in ('PAPER 2', 'PAPER II'))

    def is_paper3():
        return any(k in paper_type or k in paper_name for k in ('PAPER 3', 'PAPER III'))

    # Prefer subject-specific classes first
    try:
        if is_marking_scheme:
            # Marking scheme selection
            if subject_name == 'BIOLOGY' and is_paper2():
                return BiologyPaper2MarkingSchemeCoverpage, BiologyPaper2MarkingSchemeCoverpage.generate_default_data(generated_paper, paper)
            if subject_name == 'BIOLOGY' and is_paper3():
                # No separate Paper 3 marking scheme class exists; reuse Paper 2 marking scheme structure
                return BiologyPaper2MarkingSchemeCoverpage, BiologyPaper2MarkingSchemeCoverpage.generate_default_data(generated_paper, paper)
            # Generic marking scheme class fallback
            return MarkingSchemeCoverpage, MarkingSchemeCoverpage.generate_default_data(generated_paper, paper)

        # Question paper coverpage selection
        if subject_name == 'PHYSICS':
            if is_paper1():
                return PhysicsPaper1Coverpage, PhysicsPaper1Coverpage.generate_default_coverpage_data(generated_paper, paper)
            return PhysicsPaper2Coverpage, PhysicsPaper2Coverpage.generate_default_coverpage_data(generated_paper, paper)
        

        if subject_name == 'CHEMISTRY':
            if is_paper2():
                return ChemistryPaper2Coverpage, ChemistryPaper2Coverpage.generate_default_coverpage_data(generated_paper, paper)
            # default to paper1 if not explicit
            return ChemistryPaper1Coverpage, ChemistryPaper1Coverpage.generate_default_coverpage_data(generated_paper, paper)

        # If it's explicitly a Paper 3 (and subject biology), prefer Biology Paper3
        if subject_name == 'BIOLOGY' and is_paper3():
            return BiologyPaper3Coverpage, BiologyPaper3Coverpage.generate_default_coverpage_data(generated_paper, paper)

        # If it's explicitly a Paper 2 (and not chemistry/physics), prefer Biology Paper2
        if is_paper2():
            return BiologyPaper2Coverpage, BiologyPaper2Coverpage.generate_default_coverpage_data(generated_paper, paper)

        # Fallback: if subject is biology use Biology Paper 1, otherwise fallback below
        if subject_name == 'BIOLOGY':
            return BiologyPaper1Coverpage, BiologyPaper1Coverpage.generate_default_coverpage_data(generated_paper, paper)

    except Exception:
        # If any class doesn't expose expected helper, fallback to a safe default
        try:
            return BiologyPaper1Coverpage, BiologyPaper1Coverpage.generate_default_coverpage_data(generated_paper, paper)
        except Exception:
            # Last resort: return MarkingSchemeCoverpage default
            return MarkingSchemeCoverpage, MarkingSchemeCoverpage.generate_default_data(generated_paper, paper)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_paper(request):
    """
    Generate a KCSE Biology Paper 1
    
    POST /api/papers/generate
    {
        "paper_id": "uuid",
        "selected_topics": ["topic_uuid1", "topic_uuid2", ...]
    }
    """
    try:
        paper_id = request.data.get('paper_id')
        selected_topic_ids = request.data.get('selected_topics', [])
        
        if not paper_id:
            return Response(
                {'error': 'paper_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not selected_topic_ids:
            return Response(
                {'error': 'At least one topic must be selected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate paper exists
        paper = get_object_or_404(Paper, id=paper_id, is_active=True)
        
        # Validate topics exist
        valid_topics = Topic.objects.filter(
            id__in=selected_topic_ids,
            paper=paper,
            is_active=True
        )
        
        if valid_topics.count() != len(selected_topic_ids):
            return Response(
                {'error': 'Some selected topics are invalid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if enough questions exist
        question_count = Question.objects.filter(
            paper=paper,
            topic__in=valid_topics,
            is_active=True
        ).count()
        
        if question_count < 25:
            return Response(
                {
                    'error': 'Insufficient questions in database',
                    'details': f'Found {question_count} questions, need at least 25'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"[GENERATE] User {request.user.full_name} generating {paper.name} "
                   f"with {len(selected_topic_ids)} topics")
        
        # Initialize generator with new KCSE algorithm
        generator = KCSEBiologyPaper1Generator(
            paper_id=str(paper_id),
            selected_topic_ids=[str(tid) for tid in selected_topic_ids]
        )
        
        # Load data
        generator.load_data()
        
        # Generate paper
        result = generator.generate()
        
        # Create GeneratedPaper record from result
        from datetime import datetime
        current_year = datetime.now().year
        year_count = GeneratedPaper.objects.filter(
            paper=paper, 
            created_at__year=current_year
        ).count()
        unique_code = f"{paper.subject.name[:2].upper()}-{current_year}-{year_count + 1:03d}"
        
        generated_paper = GeneratedPaper.objects.create(
            paper=paper,
            unique_code=unique_code,
            status='draft',
            question_ids=result['question_ids'],  # Use the question_ids list from generator
            selected_topics=[str(tid) for tid in selected_topic_ids],
            total_marks=result['statistics']['total_marks'],
            total_questions=result['statistics']['total_questions'],
            mark_distribution=result['statistics']['marks_distribution'],
            topic_distribution=result['statistics']['topic_distribution'],
            question_type_distribution={},  # Can be calculated later if needed
            generation_attempts=result['statistics']['generation_attempts'],
            backtracking_count=0,  # New algorithm doesn't use backtracking
            generation_time_seconds=result['statistics']['generation_time_seconds'],
            generated_by=request.user,
            validation_passed=all(result['statistics']['validation'].values()),
            validation_report=result['statistics']['validation']
        )
        
        # Return success with generated paper details
        return Response({
            'success': True,
            'message': 'Paper generated successfully',
            'generated_paper': {
                'id': str(generated_paper.id),
                'unique_code': generated_paper.unique_code,
                'status': generated_paper.status,
                'total_marks': generated_paper.total_marks,
                'total_questions': generated_paper.total_questions,
                'nested_count': result['statistics']['nested_count'],
                'nested_marks': result['statistics']['nested_marks'],
                'standalone_count': result['statistics']['standalone_count'],
                'standalone_marks': result['statistics']['standalone_marks'],
                'mark_distribution': generated_paper.mark_distribution,
                'topic_distribution': generated_paper.topic_distribution,
                'validation_passed': generated_paper.validation_passed,
                'validation_report': generated_paper.validation_report,
                'generation_time_seconds': generated_paper.generation_time_seconds,
                'generation_attempts': generated_paper.generation_attempts,
                'created_at': generated_paper.created_at,
            }
        }, status=status.HTTP_201_CREATED)
        
    except PaperGenerationException as e:
        logger.error(f"[GENERATE] Generation failed: {str(e)}")
        return Response(
            {
                'error': 'Paper generation failed',
                'details': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        logger.error(f"[GENERATE] Unexpected error: {str(e)}", exc_info=True)
        return Response(
            {
                'error': 'Internal server error',
                'details': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_generated_paper(request, paper_id):
    """
    Retrieve a generated paper with full question details
    Questions and answers are retrieved from database using stored question IDs
    
    GET /api/papers/generated/{paper_id}
    
    Returns:
        - Paper metadata
        - Questions (for paper)
        - Answers (for marking scheme)
    """
    try:
        generated_paper = get_object_or_404(GeneratedPaper, id=paper_id)
        
        # Load all questions in order using the stored question_ids list
        question_ids = generated_paper.question_ids
        questions = Question.objects.filter(id__in=question_ids).select_related(
            'topic', 'section'
        )
        
        # Create ordered list maintaining the sequence from generation
        question_map = {str(q.id): q for q in questions}
        ordered_questions = []
        marking_scheme = []
        
        for idx, qid in enumerate(question_ids, start=1):
            question = question_map.get(qid)
            if question:
                # Question data for paper
                question_data = {
                    'id': str(question.id),
                    'question_number': idx,
                    'question_text': question.question_text,
                    'question_inline_images': question.question_inline_images,
                    'question_image_positions': question.question_image_positions,
                    'question_answer_lines': question.question_answer_lines,
                    'marks': question.marks,
                    'is_nested': question.is_nested,
                    'nested_parts': question.nested_parts if question.is_nested else None,
                    'question_type': question.question_type,
                    'kcse_question_type': question.kcse_question_type,
                    'difficulty': question.difficulty,
                    'topic': {
                        'id': str(question.topic.id),
                        'name': question.topic.name
                    },
                    'section': {
                        'id': str(question.section.id),
                        'name': question.section.name,
                        'order': question.section.order
                    } if question.section else None,
                }
                ordered_questions.append(question_data)
                
                # Answer data for marking scheme
                answer_data = {
                    'question_number': idx,
                    'question_id': str(question.id),
                    'question_text_preview': question.question_text[:100] + '...' if len(question.question_text) > 100 else question.question_text,
                    'answer_text': question.answer_text,
                    'answer_inline_images': question.answer_inline_images,
                    'answer_image_positions': question.answer_image_positions,
                    'answer_answer_lines': question.answer_answer_lines,
                    'marks': question.marks,
                    'is_nested': question.is_nested,
                    'marking_points': question.nested_parts if question.is_nested else None,
                }
                marking_scheme.append(answer_data)
        
        return Response({
            'id': str(generated_paper.id),
            'unique_code': generated_paper.unique_code,
            'status': generated_paper.status,
            'paper': {
                'id': str(generated_paper.paper.id),
                'name': generated_paper.paper.name,
                'subject_name': generated_paper.paper.subject.name,
                'total_marks': generated_paper.paper.total_marks,
                'time_allocation': generated_paper.paper.time_allocation,
            },
            'total_marks': generated_paper.total_marks,
            'total_questions': generated_paper.total_questions,
            'mark_distribution': generated_paper.mark_distribution,
            'topic_distribution': generated_paper.topic_distribution,
            'validation_passed': generated_paper.validation_passed,
            'validation_report': generated_paper.validation_report,
            'generation_statistics': {
                'generation_time_seconds': generated_paper.generation_time_seconds,
                'generation_attempts': generated_paper.generation_attempts,
            },
            'questions': ordered_questions,  # For paper generation
            'marking_scheme': marking_scheme,  # For marking scheme generation
            'created_at': generated_paper.created_at,
            'generated_by': {
                'id': str(generated_paper.generated_by.id),
                'full_name': generated_paper.generated_by.full_name,
            } if generated_paper.generated_by else None,
        })
        
    except Exception as e:
        logger.error(f"[GET_PAPER] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_generated_papers(request):
    """
    List generated papers from the last 30 days with filtering
    
    GET /api/papers/generated?paper_id=uuid&status=validated&user_only=true
    
    Note: Papers older than 30 days are automatically archived/hidden
    """
    try:
        from datetime import timedelta
        from django.utils import timezone
        
        # Calculate 30 days ago
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        queryset = GeneratedPaper.objects.select_related(
            'paper__subject',
            'generated_by'
        ).filter(
            created_at__gte=thirty_days_ago  # Only papers from last 30 days
        ).order_by('-created_at')
        
        # Filters
        paper_status = request.query_params.get('status')
        user_only = request.query_params.get('user_only', 'false').lower() == 'true'
        
        if paper_status:
            queryset = queryset.filter(status=paper_status)
        
        # Filter by current user if requested
        if user_only:
            queryset = queryset.filter(generated_by=request.user)
        
        papers = []
        for gp in queryset[:100]:  # Limit to 100 recent papers (increased from 50)
            # Get paper type from metadata
            paper_type = None
            if hasattr(gp, 'metadata') and gp.metadata:
                paper_type = gp.metadata.get('paper_type')
            
            papers.append({
                'id': str(gp.id),
                'unique_code': gp.unique_code,
                'status': gp.status,
                'paper_name': gp.paper.name,
                'paper_type': paper_type,  # Add paper type to response
                'subject_name': gp.paper.subject.name,
                'total_marks': gp.total_marks,
                'total_questions': gp.total_questions,
                'validation_passed': gp.validation_passed,
                'generated_by': gp.generated_by.full_name if gp.generated_by else None,
                'created_at': gp.created_at,
                'days_remaining': (gp.created_at + timedelta(days=30) - timezone.now()).days,
            })
        
        return Response({
            'count': len(papers),
            'generated_papers': papers,  # Changed from 'papers' to 'generated_papers' for consistency
            'retention_days': 30,
            'oldest_date': thirty_days_ago.isoformat(),
        })
        
    except Exception as e:
        logger.error(f"[LIST_PAPERS] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_paper_configuration(request, paper_id):
    """
    Get or create paper configuration
    
    GET /api/papers/{paper_id}/configuration
    """
    try:
        paper = get_object_or_404(Paper, id=paper_id)
        config, created = PaperConfiguration.objects.get_or_create(paper=paper)
        
        return Response({
            'paper_id': str(paper.id),
            'paper_name': paper.name,
            'total_marks': paper.total_marks,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'configuration': {
                'mark_distribution': {
                    'one_mark': {
                        'min_percent': config.one_mark_min_percent,
                        'max_percent': config.one_mark_max_percent,
                    },
                    'two_mark': {
                        'min_percent': config.two_mark_min_percent,
                        'max_percent': config.two_mark_max_percent,
                    },
                    'three_mark': {
                        'min_percent': config.three_mark_min_percent,
                        'max_percent': config.three_mark_max_percent,
                    },
                    'four_mark': {
                        'min_percent': config.four_mark_min_percent,
                        'max_percent': config.four_mark_max_percent,
                    },
                },
                'question_type_distribution': {
                    'name_identify': {
                        'min_percent': config.name_identify_min_percent,
                        'max_percent': config.name_identify_max_percent,
                    },
                    'state_reasons': {
                        'min_percent': config.state_reasons_min_percent,
                        'max_percent': config.state_reasons_max_percent,
                    },
                    'distinguish': {
                        'min_percent': config.distinguish_min_percent,
                        'max_percent': config.distinguish_max_percent,
                    },
                    'explain': {
                        'min_percent': config.explain_min_percent,
                        'max_percent': config.explain_max_percent,
                    },
                    'describe': {
                        'min_percent': config.describe_min_percent,
                        'max_percent': config.describe_max_percent,
                    },
                    'calculate': {
                        'min_percent': config.calculate_min_percent,
                        'max_percent': config.calculate_max_percent,
                    },
                },
                'question_count': {
                    'min': config.min_questions,
                    'max': config.max_questions,
                },
                'instructions': config.instructions,
            },
            'created': created,
        })
        
    except Exception as e:
        logger.error(f"[GET_CONFIG] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_paper_configuration(request, paper_id):
    """
    Update paper configuration
    
    PATCH /api/papers/{paper_id}/configuration
    """
    try:
        paper = get_object_or_404(Paper, id=paper_id)
        config, _ = PaperConfiguration.objects.get_or_create(paper=paper)
        
        # Update fields if provided
        config_data = request.data
        
        # Mark distribution
        if 'mark_distribution' in config_data:
            md = config_data['mark_distribution']
            if 'one_mark' in md:
                if 'min_percent' in md['one_mark']:
                    config.one_mark_min_percent = md['one_mark']['min_percent']
                if 'max_percent' in md['one_mark']:
                    config.one_mark_max_percent = md['one_mark']['max_percent']
            
            # Similar for two_mark, three_mark, four_mark...
            # (Abbreviated for brevity - full implementation would handle all)
        
        # Question type distribution
        if 'question_type_distribution' in config_data:
            qtd = config_data['question_type_distribution']
            # Handle updates...
        
        # Question count
        if 'question_count' in config_data:
            qc = config_data['question_count']
            if 'min' in qc:
                config.min_questions = qc['min']
            if 'max' in qc:
                config.max_questions = qc['max']
        
        # Instructions
        if 'instructions' in config_data:
            config.instructions = config_data['instructions']
        
        config.save()
        
        return Response({
            'success': True,
            'message': 'Configuration updated successfully'
        })
        
    except Exception as e:
        logger.error(f"[UPDATE_CONFIG] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_topic_statistics(request, paper_id):
    """
    Get statistics about available questions per topic
    Shows nested and standalone question counts
    
    GET /api/papers/{paper_id}/topics/statistics
    """
    try:
        paper = get_object_or_404(Paper, id=paper_id)
        topics = Topic.objects.filter(paper=paper, is_active=True)
        
        topic_stats = []
        
        for topic in topics:
            # Count nested questions
            nested_questions = Question.objects.filter(
                topic=topic,
                is_active=True,
                is_nested=True
            )
            nested_by_mark = nested_questions.values('marks').annotate(count=Count('id'))
            nested_counts = {}
            for item in nested_by_mark:
                nested_counts[item['marks']] = item['count']
            
            # Count standalone questions by mark value
            standalone_questions = Question.objects.filter(
                topic=topic,
                is_active=True,
                is_nested=False
            )
            standalone_by_mark = standalone_questions.values('marks').annotate(count=Count('id'))
            
            standalone_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            for item in standalone_by_mark:
                if item['marks'] <= 6:
                    standalone_counts[item['marks']] = item['count']
            
            total_nested = nested_questions.count()
            total_standalone = standalone_questions.count()
            total_questions = total_nested + total_standalone
            
            # Combine nested and standalone counts into questions_by_marks (1-6 marks)
            questions_by_marks = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            for mark_value in range(1, 7):
                nested_count = nested_counts.get(mark_value, 0)
                standalone_count = standalone_counts.get(mark_value, 0)
                questions_by_marks[mark_value] = nested_count + standalone_count
            
            topic_stats.append({
                'id': str(topic.id),
                'name': topic.name,
                'min_marks': topic.min_marks,
                'max_marks': topic.max_marks,
                'total_questions': total_questions,
                'questions_by_marks': questions_by_marks,
                'nested_questions': {
                    'count': total_nested,
                    'by_marks': nested_counts,
                },
                'standalone_questions': {
                    'count': total_standalone,
                    'by_marks': standalone_counts,
                },
                'sufficient': total_nested >= 2 and total_standalone >= 5,  # Rule of thumb
            })
        
        return Response({
            'paper_id': str(paper.id),
            'paper_name': paper.name,
            'topics': topic_stats,
            'total_topics': len(topic_stats),
        })
        
    except Exception as e:
        logger.error(f"[TOPIC_STATS] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_full_paper(request, paper_id):
    """
    View full paper with all selected questions
    This is the preview before proceeding to coverpage
    
    GET /api/papers/generated/{paper_id}/view
    
    Returns:
        - Paper metadata
        - All questions in order (without answers)
        - Statistics
    """
    try:
        generated_paper = get_object_or_404(GeneratedPaper, id=paper_id)
        
        # Load all questions in order using the stored question_ids list
        question_ids = generated_paper.question_ids
        questions = Question.objects.filter(id__in=question_ids).select_related(
            'topic', 'section'
        )
        
        # Create ordered list maintaining the sequence from generation
        question_map = {str(q.id): q for q in questions}
        ordered_questions = []
        marking_scheme = []
        
        for idx, qid in enumerate(question_ids, start=1):
            question = question_map.get(qid)
            if question:
                # Question data for paper preview (no answers)
                question_data = {
                    'id': str(question.id),
                    'question_number': idx,
                    'question_text': question.question_text,
                    'question_inline_images': question.question_inline_images,
                    'question_image_positions': question.question_image_positions,
                    'question_answer_lines': question.question_answer_lines,
                    'marks': question.marks,
                    'is_nested': question.is_nested,
                    'nested_parts': question.nested_parts if question.is_nested else None,
                    'question_type': question.question_type,
                    'kcse_question_type': question.kcse_question_type,
                    'difficulty': question.difficulty,
                    'topic': {
                        'id': str(question.topic.id),
                        'name': question.topic.name
                    },
                    'section': {
                        'id': str(question.section.id),
                        'name': question.section.name,
                        'order': question.section.order
                    } if question.section else None,
                }
                ordered_questions.append(question_data)
                
                # Answer data for marking scheme preview
                answer_data = {
                    'question_number': idx,
                    'question_id': str(question.id),
                    'question_text_preview': question.question_text[:100] + '...' if len(question.question_text) > 100 else question.question_text,
                    'answer_text': question.answer_text,
                    'answer_inline_images': question.answer_inline_images,
                    'answer_image_positions': question.answer_image_positions,
                    'answer_answer_lines': question.answer_answer_lines,
                    'marks': question.marks,
                    'is_nested': question.is_nested,
                    'marking_points': question.nested_parts if question.is_nested else None,
                }
                marking_scheme.append(answer_data)
        
        # Calculate question statistics
        nested_count = sum(1 for q in ordered_questions if q['is_nested'])
        standalone_count = len(ordered_questions) - nested_count
        
        return Response({
            'id': str(generated_paper.id),
            'unique_code': generated_paper.unique_code,
            'status': generated_paper.status,
            'paper': {
                'id': str(generated_paper.paper.id),
                'name': generated_paper.paper.name,
                'subject_name': generated_paper.paper.subject.name,
                'total_marks': generated_paper.paper.total_marks,
                'time_allocation': format_time_allocation(generated_paper.paper.time_allocation),
            },
            'statistics': {
                'total_questions': generated_paper.total_questions,
                'total_marks': generated_paper.total_marks,
                'nested_count': nested_count,
                'standalone_count': standalone_count,
                'mark_distribution': generated_paper.mark_distribution,
                'topic_distribution': generated_paper.topic_distribution,
            },
            'questions': ordered_questions,
            'marking_scheme': marking_scheme,
            'created_at': generated_paper.created_at,
            'generated_by': {
                'id': str(generated_paper.generated_by.id),
                'full_name': generated_paper.generated_by.full_name,
            } if generated_paper.generated_by else None,
        })
        
    except Exception as e:
        logger.error(f"[VIEW_PAPER] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def coverpage_data(request, paper_id):
    """
    Get or update coverpage data for a generated paper
    
    GET /api/papers/generated/{paper_id}/coverpage?output=json|html
    - Returns current coverpage data or defaults
    - If output=html, returns rendered HTML coverpage
    - If output=json, returns JSON data
    - Authentication required for all requests
    
    POST /api/papers/generated/{paper_id}/coverpage
    - Updates coverpage data
    - Authentication required
    
    Coverpage fields:
    - school_name
    - school_logo (optional)
    - logo_position (left, center, right)
    - exam_title (e.g., "END TERM 3 EXAMINATION 2025")
    - paper_name (e.g., "BIOLOGY PAPER 1")
    - instructions (list of instructions)
    - time_allocation
    - total_marks
    - total_questions (auto-filled)
    - candidate_name_field (bool)
    - candidate_number_field (bool)
    - date_field (bool)
    """
    try:
        # Use 'output' instead of 'format' to avoid DRF content negotiation conflicts
        output_format = request.GET.get('output', 'json') if request.method == 'GET' else 'json'
        
        generated_paper = get_object_or_404(GeneratedPaper, id=paper_id)
        
        if request.method == 'GET':
            # Get coverpage data (stored in generated_paper or use defaults)
            coverpage = getattr(generated_paper, 'coverpage_data', None) or {}
            
            # Select Coverpage class and default data robustly
            CoverpageClass, default_coverpage = _select_coverpage_class_and_default(generated_paper, generated_paper.paper, is_marking_scheme=False)
            
            # Merge with saved data
            coverpage_data = {**default_coverpage, **coverpage}
            
            # Ensure paper_type is included in coverpage data
            paper_type = getattr(generated_paper, 'metadata', {}).get('paper_type', '')
            if 'paper_type' not in coverpage_data:
                coverpage_data['paper_type'] = paper_type
            
            # Ensure time_allocation is always formatted (in case old data has numeric value)
            if isinstance(coverpage_data.get('time_allocation'), int):
                coverpage_data['time_allocation'] = format_time_allocation(coverpage_data['time_allocation'])
            
            if output_format == 'html':
                # Generate HTML coverpage
                html_content = CoverpageClass.generate_html(coverpage_data)
                
                from django.http import HttpResponse
                return HttpResponse(html_content, content_type='text/html')
            
            # Return JSON by default
            return Response({
                'paper_id': str(generated_paper.id),
                'unique_code': generated_paper.unique_code,
                'coverpage': coverpage_data,
            })
        
        elif request.method == 'POST':
            # Update coverpage data
            coverpage_data = request.data.get('coverpage', {})
            
            # Store in generated_paper
            if not hasattr(generated_paper, 'coverpage_data') or generated_paper.coverpage_data is None:
                generated_paper.coverpage_data = {}
            
            # Update fields
            allowed_fields = [
                'school_name', 'school_logo', 'logo_position', 'class_name', 'exam_title', 'paper_name',
                'instructions', 'time_allocation', 'total_marks',
                'candidate_name_field', 'candidate_number_field', 'date_field',
                'paper_type', 'section_a_questions', 'section_a_marks', 'section_b_questions', 'section_b_marks'
            ]
            
            for field in allowed_fields:
                if field in coverpage_data:
                    generated_paper.coverpage_data[field] = coverpage_data[field]
            
            # Auto-fill total_questions from generated paper
            generated_paper.coverpage_data['total_questions'] = generated_paper.total_questions
            
            generated_paper.save()
            
            return Response({
                'success': True,
                'message': 'Coverpage updated successfully',
                'coverpage': generated_paper.coverpage_data,
            })
        
    except Exception as e:
        logger.error(f"[COVERPAGE] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_paper(request, paper_id):
    """
    Download or print paper (with coverpage)
    
    GET /api/papers/generated/{paper_id}/download?format=pdf&include_answers=false
    
    Query params:
    - format: 'pdf' or 'docx' (default: pdf)
    - include_answers: 'true' or 'false' (default: false)
    - include_coverpage: 'true' or 'false' (default: true)
    
    Returns:
        Complete paper data formatted for printing/download
    """
    try:
        generated_paper = get_object_or_404(GeneratedPaper, id=paper_id)
        
        # Query params
        format_type = request.query_params.get('format', 'pdf')
        include_answers = request.query_params.get('include_answers', 'false').lower() == 'true'
        include_coverpage = request.query_params.get('include_coverpage', 'true').lower() == 'true'
        
        # Load questions
        question_ids = generated_paper.question_ids
        questions = Question.objects.filter(id__in=question_ids).select_related(
            'topic', 'section'
        )
        question_map = {str(q.id): q for q in questions}
        
        # Build questions list
        ordered_questions = []
        for idx, qid in enumerate(question_ids, start=1):
            question = question_map.get(qid)
            if question:
                question_data = {
                    'question_number': idx,
                    'question_text': question.question_text,
                    'question_inline_images': question.question_inline_images,
                    'marks': question.marks,
                    'is_nested': question.is_nested,
                    'nested_parts': question.nested_parts if question.is_nested else None,
                }
                
                # Include answers if requested
                if include_answers:
                    question_data['answer_text'] = question.answer_text
                    question_data['answer_inline_images'] = question.answer_inline_images
                
                ordered_questions.append(question_data)
        
        # Get coverpage data
        coverpage_data = None
        if include_coverpage:
            coverpage = getattr(generated_paper, 'coverpage_data', None) or {}
            coverpage_data = {
                'school_name': coverpage.get('school_name', ''),
                'school_logo': coverpage.get('school_logo'),
                'exam_title': coverpage.get('exam_title', 'END TERM EXAMINATION 2025'),
                'paper_name': coverpage.get('paper_name', f"{generated_paper.paper.subject.name.upper()} {generated_paper.paper.name.upper()}"),
                'instructions': coverpage.get('instructions', [
                    'Write your name and admission number in the spaces provided.',
                    'Answer ALL questions in the spaces provided.',
                ]),
                'time_allocation': coverpage.get('time_allocation', format_time_allocation(generated_paper.paper.time_allocation)),
                'total_marks': coverpage.get('total_marks', generated_paper.total_marks),
                'candidate_name_field': coverpage.get('candidate_name_field', True),
                'candidate_number_field': coverpage.get('candidate_number_field', True),
                'date_field': coverpage.get('date_field', True),
            }
        
        return Response({
            'unique_code': generated_paper.unique_code,
            'format': format_type,
            'include_answers': include_answers,
            'include_coverpage': include_coverpage,
            'coverpage': coverpage_data,
            'questions': ordered_questions,
            'statistics': {
                'total_questions': generated_paper.total_questions,
                'total_marks': generated_paper.total_marks,
            },
            'generated_at': generated_paper.created_at,
        })
        
    except Exception as e:
        logger.error(f"[DOWNLOAD] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_paper_status(request, paper_id):
    """
    Update paper status
    
    PATCH /api/papers/generated/{paper_id}/status
    {
        "status": "draft" | "review" | "published" | "archived"
    }
    """
    try:
        generated_paper = get_object_or_404(GeneratedPaper, id=paper_id)
        
        new_status = request.data.get('status')
        if new_status not in ['draft', 'review', 'published', 'archived']:
            return Response(
                {'error': 'Invalid status. Must be one of: draft, review, published, archived'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        generated_paper.status = new_status
        generated_paper.save()
        
        return Response({
            'success': True,
            'message': f'Paper status updated to {new_status}',
            'paper': {
                'id': str(generated_paper.id),
                'unique_code': generated_paper.unique_code,
                'status': generated_paper.status,
            }
        })
        
    except Exception as e:
        logger.error(f"[UPDATE_STATUS] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_full_exam(request, paper_id):
    """
    Preview the full exam paper or marking scheme
    
    GET /api/papers/generated/{paper_id}/preview/?output=html&view=questions|marking_scheme
    
    Returns:
    - If view=questions (default): Complete exam paper with coverpage and all questions
    - If view=marking_scheme: Complete marking scheme with coverpage and all answers
    """
    try:
        from django.http import HttpResponse
        
        output_format = request.GET.get('output', 'json')
        view_type = request.GET.get('view', 'questions')  # 'questions' or 'marking_scheme'
        generated_paper = get_object_or_404(GeneratedPaper, id=paper_id)
        
        if view_type == 'marking_scheme':
            # Generate marking scheme preview
            # Detect paper type for correct marking scheme coverpage
            paper_type = generated_paper.metadata.get('paper_type', '')
            subject_name = generated_paper.paper.subject.name.upper()
            paper_name = generated_paper.paper.name.upper()
            
            # Select Marking Scheme class and default data robustly
            MarkingSchemeClass, marking_scheme_coverpage = _select_coverpage_class_and_default(generated_paper, generated_paper.paper, is_marking_scheme=True)
            
            # Get all questions in order with answers
            question_ids = generated_paper.question_ids
            questions = Question.objects.filter(id__in=question_ids).select_related(
                'topic', 'section'
            )
            
            # Create ordered marking scheme
            question_map = {str(q.id): q for q in questions}
            marking_scheme_items = []
            
            for idx, qid in enumerate(question_ids, start=1):
                question = question_map.get(qid)
                if question:
                    marking_scheme_items.append({
                        'number': idx,
                        'question_preview': question.question_text[:100] + '...' if len(question.question_text) > 100 else question.question_text,
                        'answer': question.answer_text,
                        'answer_inline_images': question.answer_inline_images,
                        'answer_image_positions': question.answer_image_positions,
                        'marks': question.marks,
                        'is_nested': question.is_nested,
                        'marking_points': question.nested_parts if question.is_nested else None,
                    })
            
            if output_format == 'html':
                # Generate marking scheme HTML
                from .marking_scheme_template import generate_marking_scheme_html
                html_content = generate_marking_scheme_html(
                    marking_scheme_coverpage, 
                    marking_scheme_items,
                    coverpage_class=MarkingSchemeClass
                )
                return HttpResponse(html_content, content_type='text/html')
            
            return Response({
                'coverpage': marking_scheme_coverpage,
                'marking_scheme': marking_scheme_items
            })
        
        else:
            # Generate questions preview (default)
            # Get coverpage data
            coverpage_data_dict = getattr(generated_paper, 'coverpage_data', None) or {}
            
            # Detect paper type and use appropriate coverpage template
            paper_type = generated_paper.metadata.get('paper_type', '')
            subject_name = generated_paper.paper.subject.name.upper()
            paper_name = generated_paper.paper.name.upper()
            
            # Select Coverpage class and default data robustly
            CoverpageClass, default_coverpage = _select_coverpage_class_and_default(generated_paper, generated_paper.paper, is_marking_scheme=False)

            coverpage_data = {**default_coverpage, **coverpage_data_dict}
            
            # Get all questions in order
            question_ids = generated_paper.question_ids
            questions = Question.objects.filter(id__in=question_ids).select_related(
                'topic', 'section'
            )
            
            # Create ordered list
            question_map = {str(q.id): q for q in questions}
            ordered_questions = []
            
            for idx, qid in enumerate(question_ids, start=1):
                question = question_map.get(qid)
                if question:
                    ordered_questions.append({
                        'number': idx,
                        'text': question.question_text,
                        'question_inline_images': question.question_inline_images,
                        'question_image_positions': question.question_image_positions,
                        'question_answer_lines': question.question_answer_lines,
                        'marks': question.marks,
                        'is_nested': question.is_nested,
                        'nested_parts': question.nested_parts if question.is_nested else None,
                        'topic': question.topic.name,
                        'section': {
                            'id': str(question.section.id),
                            'name': question.section.name,
                            'order': question.section.order
                        } if question.section else None
                    })
            
            if output_format == 'html':
                # Generate complete exam HTML
                from .exam_paper_template import generate_full_exam_html
                html_content = generate_full_exam_html(
                    coverpage_data, 
                    ordered_questions,
                    coverpage_class=CoverpageClass
                )
                return HttpResponse(html_content, content_type='text/html')
        
        # Return JSON
        return Response({
            'paper_id': str(generated_paper.id),
            'coverpage': coverpage_data,
            'questions': ordered_questions,
            'total_pages': len(ordered_questions) // 3 + 2  # Rough estimate
        })
        
    except Exception as e:
        logger.error(f"[PREVIEW_FULL_EXAM] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# view to chech uestion grph nd essy sttus
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_question_graph_essay_status(request, question_id):
    """
    Check if a question has graph or essay components
    
    GET /api/questions/{question_id}/check_graph_essay
    """
    try:
        question = get_object_or_404(Question, id=question_id)
        
        has_graph = 'graph' in (question.question_type or '').lower()
        has_essay = 'essay' in (question.question_type or '').lower()
        
        return Response({
            'question_id': str(question.id),
            'has_graph': has_graph,
            'has_essay': has_essay,
        })
        
    except Exception as e:
        logger.error(f"[CHECK_GRAPH_ESSAY] Error: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

# Geography Paper 1 Pool Validation (DRF version)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def validate_geography_paper_pool(request):
    """
    Validate if the selected Geography Paper 1 pool can generate a valid paper.
    POST /api/papers/geography/validate-pool
    Body: { "paper_id": ..., "selected_topic_ids": [...], "paper_number": 1 }
    """
    try:
        paper_id = request.data.get("paper_id")
        selected_topic_ids = request.data.get("topic_ids", [])
        paper_number = int(request.data.get("paper_number", 1))
        if not paper_id or not selected_topic_ids:
            return Response({"can_generate": False, "message": "Missing paper_id or selected_topic_ids"}, status=status.HTTP_400_BAD_REQUEST)

        paper = Paper.objects.select_related('subject').get(id=paper_id, is_active=True)
        topics = list(Topic.objects.filter(id__in=selected_topic_ids, paper=paper, is_active=True))
        if not topics:
            return Response({
                'can_generate': False,
                'message': 'No valid topics found'
            }, status=status.HTTP_404_NOT_FOUND)
        all_questions = list(Question.objects.filter(
            subject=paper.subject,
            paper=paper,
            topic__in=topics,
            is_active=True
        ).select_related('topic', 'section'))
        section_a_count = 0
        section_b_25mark_map_count = 0
        section_b_25mark_regular_count = 0
        for q in all_questions:
            section_name = q.section.name.upper() if q.section else ""
            is_map = getattr(q, 'is_map', False)
            if ("SECTION A" in section_name or "SECTION 1" in section_name) and q.marks < 25:
                section_a_count += 1
            elif ("SECTION B" in section_name or "SECTION 2" in section_name) and q.marks == 25:
                if is_map:
                    section_b_25mark_map_count += 1
                else:
                    section_b_25mark_regular_count += 1
        section_b_25mark_total = section_b_25mark_map_count + section_b_25mark_regular_count
        section_a_ok = section_a_count >= 5
        section_b_ok = section_b_25mark_total >= 5
        can_generate = section_a_ok and section_b_ok
        issues = []
        if not section_a_ok:
            issues.append(f"Section A: Need 5-6 questions, have {section_a_count}")
        if not section_b_ok:
            issues.append(f"Section B: Need 5 X 25-mark, have {section_b_25mark_total}")
        message = f"Ready to generate Geography Paper {paper_number}" if can_generate else "Insufficient questions: " + "; ".join(issues)
        paper_notes = "Note: Question 6 will be MAP question if available" if paper_number == 1 else "Note: No map priority for Question 6"
        return Response({
            'can_generate': can_generate,
            'available_counts': {
                'section_a_questions': section_a_count,
                'section_b_25mark_map': section_b_25mark_map_count,
                'section_b_25mark_regular': section_b_25mark_regular_count,
                'section_b_25mark_total': section_b_25mark_total,
            },
            'required_counts': {
                'section_a_questions': '5-6',
                'section_b_25mark': 5,
            },
            'paper_structure': {
                'section_a': '5-6 questions = 25 marks (ALL COMPULSORY)',
                'section_b': '5 questions X 25 marks = 125 marks (ALL COMPULSORY)',
                'paper_total': '150 marks',
                'paper_specific_note': paper_notes
            },
            'validation': {
                'section_a_ok': section_a_ok,
                'section_b_ok': section_b_ok,
            },
            'message': message
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.getLogger(__name__).error(f"[GEOGRAPHY VALIDATE POOL ERROR] {error_details}")
        return Response({
            'can_generate': False,
            'message': f'Validation error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Geography Paper 1 Generation (DRF version)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_geography_paper(request):
    """
    Generate Geography Paper 1 using selected topics.
    POST /api/papers/geography/generate
    Body: { "paper_id": ..., "selected_topic_ids": [...], "paper_number": 1 }
    """
    try:
        paper_id = request.data.get("paper_id")
        selected_topic_ids = request.data.get("topic_ids", [])
        paper_number = int(request.data.get("paper_number", 1))
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        if not paper_id or not selected_topic_ids:
            return Response({
                'success': False,
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=status.HTTP_400_BAD_REQUEST)
        if paper_number not in [1, 2]:
            return Response({
                'success': False,
                'message': 'Invalid paper_number. Must be 1 or 2'
            }, status=status.HTTP_400_BAD_REQUEST)
        if paper_number == 1:
            generator = KCSEGeographyPaper1Generator(
                paper_id=paper_id,
                selected_topic_ids=selected_topic_ids,
                user=user
            )
        else:
            generator = KCSEGeographyPaper2Generator(
                paper_id=paper_id,
                selected_topic_ids=selected_topic_ids,
                user=user
            )
        generator.load_data()
        result = generator.generate()
        from datetime import datetime
        current_year = datetime.now().year
        paper = generator.paper
        year_count = GeneratedPaper.objects.filter(
            paper=paper,
            created_at__year=current_year
        ).count()
        unique_code = f"GEO{paper_number}-{current_year}-{year_count + 1:03d}"
        generated_paper = GeneratedPaper.objects.create(
            paper=paper,
            unique_code=unique_code,
            status='draft',
            question_ids=result['question_ids'],
            selected_topics=[str(tid) for tid in selected_topic_ids],
            total_marks=result['statistics']['paper_total_marks'],
            total_questions=result['statistics']['total_questions'],
            mark_distribution=result.get('mark_distribution', {}),
            topic_distribution=result.get('topic_distribution', {}),
            question_type_distribution=result.get('question_type_distribution', {}),
            generation_attempts=generator.attempts,
            backtracking_count=0,
            generation_time_seconds=result.get('generation_time', 0),
            generated_by=user,
            validation_passed=result.get('validation_report', {}).get('all_passed', True),
            validation_report=result.get('validation_report', {}),
        )
        return Response({
            'success': True,
            'message': 'Paper generated successfully',
            'generated_paper': {
                'id': str(generated_paper.id),
                'unique_code': generated_paper.unique_code,
                'status': generated_paper.status,
                'total_marks': generated_paper.total_marks,
                'total_questions': generated_paper.total_questions,
                'mark_distribution': generated_paper.mark_distribution,
                'topic_distribution': generated_paper.topic_distribution,
                'validation_passed': generated_paper.validation_passed,
                'validation_report': generated_paper.validation_report,
                'generation_time_seconds': generated_paper.generation_time_seconds,
                'generation_attempts': generated_paper.generation_attempts,
                'created_at': generated_paper.created_at,
            },
            'questions': result.get('questions', []),
            'instructions': result.get('instructions', []),
            'statistics': result.get('statistics', {}),
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.getLogger(__name__).error(f"[GEOGRAPHY GENERATE ERROR] {error_details}")
        return Response({
            'success': False,
            'message': f'Generation error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_english_paper(request):
    """
    Generate any English paper (1, 2, or 3) based on paper_number.
    POST /api/papers/english/generate
    Body: { "paper_id": ..., "paper_number": 1|2|3, "selections": {...} }
    """
    try:
        paper_id = request.data.get("paper_id")
        paper_number = int(request.data.get("paper_number", 1))
        selections = request.data.get("selections", {})
        if not paper_id:
            return Response({"success": False, "message": "Missing paper_id"}, status=status.HTTP_400_BAD_REQUEST)
        if paper_number == 1:
            from .english_generator import KCSEEnglishPaper1Generator
            generator = KCSEEnglishPaper1Generator(paper_id=str(paper_id), selections=selections)
        elif paper_number == 2:
            from .english_generator import KCSEEnglishPaper2Generator
            generator = KCSEEnglishPaper2Generator(paper_id=str(paper_id), selections=selections)
        elif paper_number == 3:
            from .english_generator import KCSEEnglishPaper3Generator
            generator = KCSEEnglishPaper3Generator(paper_id=str(paper_id), selections=selections)
        else:
            return Response({"success": False, "message": "Invalid paper_number for English (must be 1, 2, or 3)"}, status=status.HTTP_400_BAD_REQUEST)
        generator.load_data()
        result = generator.generate()
        from datetime import datetime
        current_year = datetime.now().year
        paper = generator.paper
        year_count = GeneratedPaper.objects.filter(paper=paper, created_at__year=current_year).count()
        unique_code = f"EN{paper_number}-{current_year}-{year_count + 1:03d}"
        generated_paper = GeneratedPaper.objects.create(
            paper=paper,
            unique_code=unique_code,
            status='draft',
            question_ids=result['question_ids'],
            selected_topics=[],
            total_marks=result['statistics']['total_marks'],
            total_questions=result['statistics']['total_questions'],
            mark_distribution=result.get('marks_distribution', {}),
            topic_distribution=result.get('topic_distribution', {}),
            question_type_distribution={},
            generation_attempts=result['statistics'].get('generation_attempts', 1),
            backtracking_count=0,
            generation_time_seconds=result['statistics'].get('generation_time_seconds', 0),
            generated_by=request.user,
            validation_passed=True,
            validation_report={},
        )
        return Response({
            'success': True,
            'message': 'Paper generated successfully',
            'generated_paper': {
                'id': str(generated_paper.id),
                'unique_code': generated_paper.unique_code,
                'status': generated_paper.status,
                'total_marks': generated_paper.total_marks,
                'total_questions': generated_paper.total_questions,
                'mark_distribution': generated_paper.mark_distribution,
                'topic_distribution': generated_paper.topic_distribution,
                'validation_passed': generated_paper.validation_passed,
                'validation_report': generated_paper.validation_report,
                'generation_time_seconds': generated_paper.generation_time_seconds,
                'generation_attempts': generated_paper.generation_attempts,
                'created_at': generated_paper.created_at,
            },
            'questions': result.get('questions', []),
            'instructions': result.get('instructions', []),
            'statistics': result.get('statistics', {}),
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"[ENGLISH GENERATE ERROR] {error_details}")
        return Response({'success': False, 'message': f'Generation error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

# Mathematics Paper Generation (both papers)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_mathematics_paper(request):
    """
    Generate Mathematics Paper 1 or 2 based on paper_number.
    POST /api/papers/mathematics/generate
    Body: { "paper_id": ..., "paper_number": 1|2, "selected_topic_ids": [...] }
    """
    try:
        paper_id = request.data.get("paper_id")
        paper_number = int(request.data.get("paper_number", 1))
        selected_topic_ids = request.data.get("topic_ids", [])
        if not paper_id or not selected_topic_ids:
            return Response({"success": False, "message": "Missing paper_id or selected_topic_ids"}, status=status.HTTP_400_BAD_REQUEST)
        if paper_number == 1:
            from .mathematics_generator import KCSEMathematicsPaper1Generator
            generator = KCSEMathematicsPaper1Generator(paper_id=str(paper_id), selected_topic_ids=[str(tid) for tid in selected_topic_ids])
        elif paper_number == 2:
            from .mathematics_generator import KCSEMathematicsPaper2Generator
            generator = KCSEMathematicsPaper2Generator(paper_id=str(paper_id), selected_topic_ids=[str(tid) for tid in selected_topic_ids])
        else:
            return Response({"success": False, "message": "Invalid paper_number for Mathematics (must be 1 or 2)"}, status=status.HTTP_400_BAD_REQUEST)
        generator.load_data()
        result = generator.generate()
        from datetime import datetime
        current_year = datetime.now().year
        paper = generator.paper
        year_count = GeneratedPaper.objects.filter(paper=paper, created_at__year=current_year).count()
        unique_code = f"MA{paper_number}-{current_year}-{year_count + 1:03d}"
        generated_paper = GeneratedPaper.objects.create(
            paper=paper,
            unique_code=unique_code,
            status='draft',
            question_ids=result['question_ids'],
            selected_topics=[str(tid) for tid in selected_topic_ids],
            total_marks=result['statistics']['total_marks'],
            total_questions=result['statistics']['total_questions'],
            mark_distribution=result.get('marks_distribution', {}),
            topic_distribution=result.get('topic_distribution', {}),
            question_type_distribution={},
            generation_attempts=result['statistics'].get('generation_attempts', 1),
            backtracking_count=0,
            generation_time_seconds=result['statistics'].get('generation_time_seconds', 0),
            generated_by=request.user,
            validation_passed=True,
            validation_report={},
        )
        return Response({
            'success': True,
            'message': 'Paper generated successfully',
            'generated_paper': {
                'id': str(generated_paper.id),
                'unique_code': generated_paper.unique_code,
                'status': generated_paper.status,
                'total_marks': generated_paper.total_marks,
                'total_questions': generated_paper.total_questions,
                'mark_distribution': generated_paper.mark_distribution,
                'topic_distribution': generated_paper.topic_distribution,
                'validation_passed': generated_paper.validation_passed,
                'validation_report': generated_paper.validation_report,
                'generation_time_seconds': generated_paper.generation_time_seconds,
                'generation_attempts': generated_paper.generation_attempts,
                'created_at': generated_paper.created_at,
            },
            'questions': result.get('questions', []),
            'instructions': result.get('instructions', []),
            'statistics': result.get('statistics', {}),
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"[MATHEMATICS GENERATE ERROR] {error_details}")
        return Response({'success': False, 'message': f'Generation error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

# Chemistry Paper Generation (both papers)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_chemistry_paper(request):
    """
    Generate Chemistry Paper 1 or 2 based on paper_number.
    POST /api/papers/chemistry/generate
    Body: { "paper_id": ..., "paper_number": 1|2, "selected_topic_ids": [...] }
    """
    try:
        paper_id = request.data.get("paper_id")
        paper_name = int(request.data.get("paper_name", ""))
        chemistry_paper1_titles = ['chemistry paper 1', 'chemistry paper i', 'chemistry paper I']
        chemistry_paper2_titles = ['chemistry paper 2', 'chemistry paper ii', 'chemistry paper II']
        selected_topic_ids = request.data.get("topic_ids", [])
        if not paper_id or not selected_topic_ids:
            return Response({"success": False, "message": "Missing paper_id or selected_topic_ids"}, status=status.HTTP_400_BAD_REQUEST)
        
        if paper_name.lower() in chemistry_paper1_titles:
           paper_number = 1
        elif paper_name.lower() in chemistry_paper2_titles:
           paper_number = 2
        
        if paper_number == 1:
            from .chemistry_paper_generator import KCSEChemistryPaper1Generator
            generator = KCSEChemistryPaper1Generator(paper_id=str(paper_id), selected_topic_ids=[str(tid) for tid in selected_topic_ids])
        elif paper_number == 2:
            from .chemistry_paper_generator import KCSEChemistryPaper2Generator
            generator = KCSEChemistryPaper2Generator(paper_id=str(paper_id), selected_topic_ids=[str(tid) for tid in selected_topic_ids])
        else:
            return Response({"success": False, "message": "Invalid paper_number for Chemistry (must be 1 or 2)"}, status=status.HTTP_400_BAD_REQUEST)
        generator.load_data()
        result = generator.generate()
        from datetime import datetime
        current_year = datetime.now().year
        paper = generator.paper
        year_count = GeneratedPaper.objects.filter(paper=paper, created_at__year=current_year).count()
        unique_code = f"CH{paper_number}-{current_year}-{year_count + 1:03d}"
        generated_paper = GeneratedPaper.objects.create(
            paper=paper,
            unique_code=unique_code,
            status='draft',
            question_ids=result['question_ids'],
            selected_topics=[str(tid) for tid in selected_topic_ids],
            total_marks=result['statistics']['total_marks'],
            total_questions=result['statistics']['total_questions'],
            mark_distribution=result.get('marks_distribution', {}),
            topic_distribution=result.get('topic_distribution', {}),
            question_type_distribution={},
            generation_attempts=result['statistics'].get('generation_attempts', 1),
            backtracking_count=0,
            generation_time_seconds=result['statistics'].get('generation_time_seconds', 0),
            generated_by=request.user,
            validation_passed=True,
            validation_report={},
        )
        return Response({
            'success': True,
            'message': 'Paper generated successfully',
            'generated_paper': {
                'id': str(generated_paper.id),
                'unique_code': generated_paper.unique_code,
                'status': generated_paper.status,
                'total_marks': generated_paper.total_marks,
                'total_questions': generated_paper.total_questions,
                'mark_distribution': generated_paper.mark_distribution,
                'topic_distribution': generated_paper.topic_distribution,
                'validation_passed': generated_paper.validation_passed,
                'validation_report': generated_paper.validation_report,
                'generation_time_seconds': generated_paper.generation_time_seconds,
                'generation_attempts': generated_paper.generation_attempts,
                'created_at': generated_paper.created_at,
            },
            'questions': result.get('questions', []),
            'instructions': result.get('instructions', []),
            'statistics': result.get('statistics', {}),
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"[CHEMISTRY GENERATE ERROR] {error_details}")
        return Response({'success': False, 'message': f'Generation error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def validate_chemistry_paper_pool(request):
    """
    Validate if the selected Chemistry paper pool can generate a valid paper (1 or 2).
    POST /api/papers/chemistry/validate
    Body: { "paper_id": ..., "paper_number": 1|2, "selected_topic_ids": [...] }
    """
    paper_id = request.data.get("paper_id")
    # Accept both 'selected_topic_ids' and 'topic_ids' for compatibility
    selected_topic_ids = request.data.get("selected_topic_ids")
    if selected_topic_ids is None:
        selected_topic_ids = request.data.get("topic_ids", [])
    paper_number = request.data.get("paper_number")
    paper_name = request.data.get("paper_name", "")
    chemistry_paper1_titles = ['chemistry paper 1', 'chemistry paper i', 'chemistry paper I']
    chemistry_paper2_titles = ['chemistry paper 2', 'chemistry paper ii', 'chemistry paper II']

    if not paper_id or not selected_topic_ids:
        return Response({"can_generate": False, "message": "Missing paper_id or selected_topic_ids"}, status=status.HTTP_400_BAD_REQUEST)

    # Determine paper_number from paper_name if not provided
    if not paper_number:
        if paper_name and paper_name.lower() in chemistry_paper1_titles:
            paper_number = 1
        elif paper_name and paper_name.lower() in chemistry_paper2_titles:
            paper_number = 2
        else:
            paper_number = 1  # Default to 1 if not specified (legacy behavior)
    else:
        try:
            paper_number = int(paper_number)
        except Exception:
            paper_number = 1

    try:
        if paper_number == 1:
            from .chemistry_paper_generator import KCSEChemistryPaper1Generator
            generator = KCSEChemistryPaper1Generator(paper_id=str(paper_id), selected_topic_ids=[str(tid) for tid in selected_topic_ids])
        elif paper_number == 2:
            from .chemistry_paper_generator import KCSEChemistryPaper2Generator
            generator = KCSEChemistryPaper2Generator(paper_id=str(paper_id), selected_topic_ids=[str(tid) for tid in selected_topic_ids])
        else:
            return Response({"can_generate": False, "message": "Invalid paper_number for Chemistry (must be 1 or 2)"}, status=status.HTTP_400_BAD_REQUEST)
        generator.load_data()
        valid_nested = generator._select_nested_questions()
        valid_standalone = generator._select_standalone_questions()
        can_generate = valid_nested and valid_standalone
        return Response({
            "can_generate": can_generate,
            "nested_count": len(getattr(generator, "nested_questions", [])),
            "standalone_count": sum(len(getattr(generator, f"standalone_{m}mark", [])) for m in range(1, 5)),
            "message": "Pool is valid" if can_generate else "Pool is insufficient for Chemistry Paper generation"
        })
    except Exception as e:
        return Response({"can_generate": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def validate_english_paper_pool(request):
    """
    Validate if the selected English paper pool can generate a valid paper (1, 2, or 3).
    POST /api/papers/english/validate
    Body: { "paper_id": ..., "paper_number": 1|2|3, "selections": {...} }
    """
    paper_id = request.data.get("paper_id")
    paper_number = int(request.data.get("paper_number", 1))
    selections = request.data.get("selections", {})
    if not paper_id:
        return Response({"can_generate": False, "message": "Missing paper_id"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        if paper_number == 1:
            from .english_generator import KCSEEnglishPaper1Generator
            generator = KCSEEnglishPaper1Generator(paper_id=str(paper_id), selections=selections)
        elif paper_number == 2:
            from .english_generator import KCSEEnglishPaper2Generator
            generator = KCSEEnglishPaper2Generator(paper_id=str(paper_id), selections=selections)
        elif paper_number == 3:
            from .english_generator import KCSEEnglishPaper3Generator
            generator = KCSEEnglishPaper3Generator(paper_id=str(paper_id), selections=selections)
        else:
            return Response({"can_generate": False, "message": "Invalid paper_number for English (must be 1, 2, or 3)"}, status=status.HTTP_400_BAD_REQUEST)
        generator.load_data()
        try:
            generator.generate()
            can_generate = True
            message = f"Pool is valid for English Paper {paper_number} generation."
        except Exception as e:
            can_generate = False
            message = f"Pool is insufficient: {str(e)}"
        return Response({"can_generate": can_generate, "message": message})
    except Exception as e:
        return Response({"can_generate": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def validate_mathematics_paper_pool(request):
    """
    Validate if the selected Mathematics paper pool can generate a valid paper (1 or 2).
    POST /api/papers/mathematics/validate
    Body: { "paper_id": ..., "paper_number": 1|2, "selected_topic_ids": [...] }
    """
    paper_id = request.data.get("paper_id")
    paper_number = int(request.data.get("paper_number", 1))
    selected_topic_ids = request.data.get("topic_ids", [])
    if not paper_id or not selected_topic_ids:
        return Response({"can_generate": False, "message": "Missing paper_id or selected_topic_ids"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        if paper_number == 1:
            from .mathematics_generator import KCSEMathematicsPaper1Generator
            generator = KCSEMathematicsPaper1Generator(paper_id=str(paper_id), selected_topic_ids=[str(tid) for tid in selected_topic_ids])
        elif paper_number == 2:
            from .mathematics_generator import KCSEMathematicsPaper2Generator
            generator = KCSEMathematicsPaper2Generator(paper_id=str(paper_id), selected_topic_ids=[str(tid) for tid in selected_topic_ids])
        else:
            return Response({"can_generate": False, "message": "Invalid paper_number for Mathematics (must be 1 or 2)"}, status=status.HTTP_400_BAD_REQUEST)
        generator.load_data()
        valid_nested = generator._select_nested_questions()
        valid_standalone = generator._select_standalone_questions()
        can_generate = valid_nested and valid_standalone
        return Response({
            "can_generate": can_generate,
            "nested_count": len(getattr(generator, "nested_questions", [])),
            "standalone_count": sum(len(getattr(generator, f"standalone_{m}mark", [])) for m in range(1, 5)),
            "message": "Pool is valid" if can_generate else "Pool is insufficient for Mathematics Paper generation"
        })
    except Exception as e:
        return Response({"can_generate": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def validate_f_paper_pool(request):
    """
    Validate if the selected Chemistry paper pool can generate a valid paper (1 or 2).
    POST /api/papers/chemistry/validate
    Body: { "paper_id": ..., "paper_number": 1|2, "selected_topic_ids": [...] }
    """
    paper_id = request.data.get("paper_id")
    # Accept both 'selected_topic_ids' and 'topic_ids' for compatibility
    selected_topic_ids = request.data.get("selected_topic_ids")
    if selected_topic_ids is None:
        selected_topic_ids = request.data.get("topic_ids", [])
    paper_number = request.data.get("paper_number")
    paper_name = request.data.get("name", "")
    chemistry_paper1_titles = ['chemistry paper 1', 'chemistry paper i', 'chemistry paper I']
    chemistry_paper2_titles = ['chemistry paper 2', 'chemistry paper ii', 'chemistry paper II']

    if not paper_id or not selected_topic_ids:
        return Response({"can_generate": False, "message": "Missing paper_id or selected_topic_ids"}, status=status.HTTP_400_BAD_REQUEST)

    # Determine paper_number from paper_name if not provided
    if not paper_number:
        if paper_name and paper_name.lower() in chemistry_paper1_titles:
            paper_number = 1
        elif paper_name and paper_name.lower() in chemistry_paper2_titles:
            paper_number = 2
        else:
            paper_number = 1  # Default to 1 if not specified (legacy behavior)
    else:
        try:
            paper_number = int(paper_number)
        except Exception:
            paper_number = 1

    try:
        if paper_number == 1:
            from .chemistry_paper_generator import KCSEChemistryPaper1Generator
            generator = KCSEChemistryPaper1Generator(paper_id=str(paper_id), selected_topic_ids=[str(tid) for tid in selected_topic_ids])
        elif paper_number == 2:
            from .chemistry_paper_generator import KCSEChemistryPaper2Generator
            generator = KCSEChemistryPaper2Generator(paper_id=str(paper_id), selected_topic_ids=[str(tid) for tid in selected_topic_ids])
        else:
            return Response({"can_generate": False, "message": "Invalid paper_number for Chemistry (must be 1 or 2)"}, status=status.HTTP_400_BAD_REQUEST)
        generator.load_data()
        valid_nested = generator._select_nested_questions()
        valid_standalone = generator._select_standalone_questions()
        can_generate = valid_nested and valid_standalone
        return Response({
            "can_generate": can_generate,
            "nested_count": len(getattr(generator, "nested_questions", [])),
            "standalone_count": sum(len(getattr(generator, f"standalone_{m}mark", [])) for m in range(1, 5)),
            "message": "Pool is valid" if can_generate else "Pool is insufficient for Chemistry Paper generation"
        })
    except Exception as e:
        return Response({"can_generate": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)