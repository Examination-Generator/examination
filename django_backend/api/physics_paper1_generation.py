"""
KCSE Physics Paper 1 Generation Algorithm with Proper Logging
"""

import random
import logging
from collections import defaultdict
from typing import List, Dict, Optional
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Paper, Topic, Section, Question, GeneratedPaper

# Set up logger
logger = logging.getLogger(__name__)


class PhysicsPaper1Validator:
    """Validates if question pool is sufficient for Physics Paper 1 generation"""
    
    @staticmethod
    def validate(paper_id: str, selected_topic_ids: List[str]) -> Dict:
        """
        Validate question availability before generation
        
        Returns:
            Dict with validation results and recommendations
        """
        logger.info(f"[VALIDATE] Starting validation for paper_id={paper_id}")
        logger.info(f"[VALIDATE] Selected topics: {len(selected_topic_ids)} topics")
        
        # Get sections
        section_a = Section.objects.filter(
            paper_id=paper_id,
            name__icontains='A',
            is_active=True
        ).first()
        
        section_b = Section.objects.filter(
            paper_id=paper_id,
            name__icontains='B',
            is_active=True
        ).first()
        
        logger.info(f"[VALIDATE] Section A found: {section_a is not None}")
        logger.info(f"[VALIDATE] Section B found: {section_b is not None}")
        
        # Section A questions
        one_mark_questions = 0
        two_mark_questions = 0
        three_mark_questions = 0
        
        if section_a:
            one_mark_questions = Question.objects.filter(
                paper_id=paper_id,
                topic_id__in=selected_topic_ids,
                section=section_a,
                marks=1,
                is_active=True
            ).count()
            
            two_mark_questions = Question.objects.filter(
                paper_id=paper_id,
                topic_id__in=selected_topic_ids,
                section=section_a,
                marks=2,
                is_active=True
            ).count()
            
            three_mark_questions = Question.objects.filter(
                paper_id=paper_id,
                topic_id__in=selected_topic_ids,
                section=section_a,
                marks=3,
                is_active=True
            ).count()
        
        # Section B questions (8-12 marks typically)
        section_b_questions = 0
        if section_b:
            section_b_questions = Question.objects.filter(
                paper_id=paper_id,
                topic_id__in=selected_topic_ids,
                section=section_b,
                marks__gte=8,
                marks__lte=12,
                is_active=True
            ).count()
        
        logger.info(f"[VALIDATE] Question counts:")
        logger.info(f"  - 1-mark: {one_mark_questions} (need 4)")
        logger.info(f"  - 2-mark: {two_mark_questions} (need 6)")
        logger.info(f"  - 3-mark: {three_mark_questions} (need 3)")
        logger.info(f"  - Section B (8-12 marks): {section_b_questions} (need 10)")
        
        # Validation
        issues = []
        recommendations = []
        
        if not section_a:
            issues.append("Section A not found in paper")
            recommendations.append("Create Section A for the paper")
        else:
            if one_mark_questions < 4:
                issues.append(f"Section A: {one_mark_questions} one-mark questions (need at least 4)")
                recommendations.append("Add more 1-mark questions to Section A")
            
            if two_mark_questions < 6:
                issues.append(f"Section A: {two_mark_questions} two-mark questions (need at least 6)")
                recommendations.append("Add more 2-mark questions to Section A")
            
            if three_mark_questions < 3:
                issues.append(f"Section A: {three_mark_questions} three-mark questions (need at least 3)")
                recommendations.append("Add more 3-mark questions to Section A")
        
        if not section_b:
            issues.append("Section B not found in paper")
            recommendations.append("Create Section B for the paper")
        elif section_b_questions < 10:
            issues.append(f"Section B: {section_b_questions} questions (need at least 10 questions of 8-12 marks)")
            recommendations.append("Add more 8-12 mark questions to Section B")
        
        is_valid = len(issues) == 0
        logger.info(f"[VALIDATE] Validation result: {'PASSED' if is_valid else 'FAILED'}")
        if not is_valid:
            logger.warning(f"[VALIDATE] Issues found: {issues}")
        
        return {
            'valid': is_valid,
            'statistics': {
                'section_a_1mark': one_mark_questions,
                'section_a_2mark': two_mark_questions,
                'section_a_3mark': three_mark_questions,
                'section_b_questions': section_b_questions
            },
            'issues': issues,
            'recommendations': recommendations
        }


class PhysicsPaper1Generator:
    """KCSE Physics Paper 1 Generation Algorithm"""
    
    # Paper constraints
    TOTAL_MARKS = 80
    SECTION_A_QUESTIONS = 13
    SECTION_A_TOTAL_MARKS = 25
    SECTION_B_TOTAL_MARKS = 55
    SECTION_B_MIN_QUESTIONS = 5
    SECTION_B_MAX_QUESTIONS = 5
    
    # Section A breakdown
    SECTION_A_1MARK_COUNT = 4
    SECTION_A_2MARK_COUNT = 6
    SECTION_A_3MARK_COUNT = 3
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str]):
        self.paper_id = paper_id
        self.selected_topic_ids = selected_topic_ids
        self.paper = None
        self.topics = []
        self.section_a = None
        self.section_b = None
        
        # Question pools
        self.one_mark_pool = []
        self.two_mark_pool = []
        self.three_mark_pool = []
        self.section_b_pool = []
        
        # Selected questions
        self.selected_section_a = []
        self.selected_section_b = []
        
        # Tracking
        self.used_question_ids = set()
        self.topic_distribution = defaultdict(int)
        
    def load_data(self):
        """Load paper, sections, topics, and questions"""
        logger.info("="*70)
        logger.info("LOADING DATA FOR PHYSICS PAPER 1 GENERATION")
        logger.info("="*70)
        
        # Load paper
        try:
            self.paper = Paper.objects.select_related('subject').get(
                id=self.paper_id,
                is_active=True
            )
            logger.info(f"✓ Paper loaded: {self.paper.name} ({self.paper.subject.name})")
        except Paper.DoesNotExist:
            logger.error(f"✗ Paper not found: {self.paper_id}")
            raise ValueError(f"Paper with id {self.paper_id} not found")
        
        # Load sections
        self.section_a = Section.objects.filter(
            paper=self.paper,
            name__icontains='A',
            is_active=True
        ).first()
        
        self.section_b = Section.objects.filter(
            paper=self.paper,
            name__icontains='B',
            is_active=True
        ).first()
        
        if not self.section_a:
            logger.error("✗ Section A not found")
            raise ValueError("Section A not found for this paper")
        if not self.section_b:
            logger.error("✗ Section B not found")
            raise ValueError("Section B not found for this paper")
        
        logger.info(f"✓ Section A: {self.section_a.name}")
        logger.info(f"✓ Section B: {self.section_b.name}")
        
        # Load topics
        self.topics = list(Topic.objects.filter(
            id__in=self.selected_topic_ids,
            paper=self.paper,
            is_active=True
        ))
        
        if not self.topics:
            logger.error("✗ No valid topics found")
            raise ValueError("No valid topics found for the selected IDs")
        
        logger.info(f"✓ Loaded {len(self.topics)} topics")
        for i, topic in enumerate(self.topics, 1):
            logger.info(f"  {i}. {topic.name}")
        
        # Load Section A questions
        self.one_mark_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_a,
            marks=1,
            is_active=True
        ).select_related('topic', 'section'))
        
        self.two_mark_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_a,
            marks=2,
            is_active=True
        ).select_related('topic', 'section'))
        
        self.three_mark_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_a,
            marks=3,
            is_active=True
        ).select_related('topic', 'section'))
        
        # Load Section B questions (8-12 marks)
        self.section_b_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_b,
            marks__gte=8,
            marks__lte=12,
            is_active=True
        ).select_related('topic', 'section').order_by('marks'))
        
        # Shuffle for randomness
        random.shuffle(self.one_mark_pool)
        random.shuffle(self.two_mark_pool)
        random.shuffle(self.three_mark_pool)
        random.shuffle(self.section_b_pool)
        
        logger.info("Question pools loaded:")
        logger.info(f"  - 1-mark: {len(self.one_mark_pool)} questions")
        logger.info(f"  - 2-mark: {len(self.two_mark_pool)} questions")
        logger.info(f"  - 3-mark: {len(self.three_mark_pool)} questions")
        logger.info(f"  - Section B (8-12 marks): {len(self.section_b_pool)} questions")
        
        # Validation
        if len(self.one_mark_pool) < self.SECTION_A_1MARK_COUNT:
            error_msg = f"Insufficient 1-mark questions: {len(self.one_mark_pool)} (need {self.SECTION_A_1MARK_COUNT})"
            logger.error(f"✗ {error_msg}")
            raise ValueError(error_msg)
        
        if len(self.two_mark_pool) < self.SECTION_A_2MARK_COUNT:
            error_msg = f"Insufficient 2-mark questions: {len(self.two_mark_pool)} (need {self.SECTION_A_2MARK_COUNT})"
            logger.error(f"✗ {error_msg}")
            raise ValueError(error_msg)
        
        if len(self.three_mark_pool) < self.SECTION_A_3MARK_COUNT:
            error_msg = f"Insufficient 3-mark questions: {len(self.three_mark_pool)} (need {self.SECTION_A_3MARK_COUNT})"
            logger.error(f"✗ {error_msg}")
            raise ValueError(error_msg)
        
        if len(self.section_b_pool) < 10:
            error_msg = f"Insufficient Section B questions: {len(self.section_b_pool)} (need 10)"
            logger.error(f"✗ {error_msg}")
            raise ValueError(error_msg)
        
        logger.info("✓ Data loaded successfully")
    
    def select_questions(self):
        """Select questions for the paper"""
        logger.info("="*70)
        logger.info("SELECTING QUESTIONS FOR PAPER")
        logger.info("="*70)
        
        # Select Section A questions
        logger.info(f"Section A: Selecting {self.SECTION_A_QUESTIONS} questions (25 marks total)")
        
        # Select questions
        selected_1mark = random.sample(self.one_mark_pool, self.SECTION_A_1MARK_COUNT)
        selected_2mark = random.sample(self.two_mark_pool, self.SECTION_A_2MARK_COUNT)
        selected_3mark = random.sample(self.three_mark_pool, self.SECTION_A_3MARK_COUNT)
        
        self.selected_section_a.extend(selected_1mark)
        self.selected_section_a.extend(selected_2mark)
        self.selected_section_a.extend(selected_3mark)
        
        # Shuffle Section A questions
        random.shuffle(self.selected_section_a)
        
        # Track used questions
        for q in self.selected_section_a:
            self.used_question_ids.add(str(q.id))
            self.topic_distribution[q.topic.name] += 1
        
        section_a_marks = sum(q.marks for q in self.selected_section_a)
        logger.info(f"✓ Section A: {len(self.selected_section_a)} questions ({section_a_marks} marks)")
        
        # Select Section B questions
        logger.info(f"Section B: Selecting questions to total {self.SECTION_B_TOTAL_MARKS} marks")
        self.selected_section_b = self._select_section_b_questions()
        
        # Track Section B questions
        for question in self.selected_section_b:
            self.used_question_ids.add(str(question.id))
            self.topic_distribution[question.topic.name] += 1
        
        section_b_marks = sum(q.marks for q in self.selected_section_b)
        logger.info(f"✓ Section B: {len(self.selected_section_b)} questions ({section_b_marks} marks)")
        
        total_questions = len(self.selected_section_a) + len(self.selected_section_b)
        total_marks = section_a_marks + section_b_marks
        logger.info(f"✓ Total: {total_questions} questions, {total_marks} marks")
    
    def _select_section_b_questions(self) -> List[Question]:
        """Select Section B questions to total exactly 55 marks"""
        target_marks = self.SECTION_B_TOTAL_MARKS
        max_questions = self.SECTION_B_MAX_QUESTIONS
        
        # Try to find combination that totals exactly 55 marks
        for num_questions in range(self.SECTION_B_MIN_QUESTIONS, max_questions + 1):
            result = self._find_combination(self.section_b_pool, target_marks, num_questions)
            if result:
                logger.info(f"  Found exact combination: {num_questions} questions = {target_marks} marks")
                return result
        
        # If exact match not found, get closest
        logger.warning(f"  Could not find exact {target_marks} marks. Finding closest match...")
        return self._find_closest_combination(self.section_b_pool, target_marks, max_questions)
    
    def _find_combination(self, questions: List[Question], target: int, num_q: int) -> Optional[List[Question]]:
        """Find combination of exactly num_q questions that total target marks"""
        from itertools import combinations
        
        for combo in combinations(questions, num_q):
            if sum(q.marks for q in combo) == target:
                return list(combo)
        
        return None
    
    def _find_closest_combination(self, questions: List[Question], target: int, max_q: int) -> List[Question]:
        """Find combination of questions (5-6) that gets closest to target marks"""
        from itertools import combinations
        
        best_combo = None
        best_diff = float('inf')
        
        for num_q in range(self.SECTION_B_MIN_QUESTIONS, max_q + 1):
            for combo in combinations(questions, num_q):
                total = sum(q.marks for q in combo)
                diff = abs(total - target)
                
                if diff < best_diff:
                    best_diff = diff
                    best_combo = combo
                
                if diff == 0:
                    return list(combo)
        
        actual_marks = sum(q.marks for q in best_combo) if best_combo else 0
        logger.warning(f"  Closest match: {len(best_combo)} questions = {actual_marks} marks (diff: {best_diff})")
        
        return list(best_combo) if best_combo else questions[:self.SECTION_B_MIN_QUESTIONS]
    
    def save_generated_paper(self) -> GeneratedPaper:
        """Save the generated paper to database"""
        logger.info("="*70)
        logger.info("SAVING GENERATED PAPER")
        logger.info("="*70)
        
        with transaction.atomic():
            all_questions = self.selected_section_a + self.selected_section_b
            total_marks = sum(q.marks for q in all_questions)
            section_a_marks = sum(q.marks for q in self.selected_section_a)
            section_b_marks = sum(q.marks for q in self.selected_section_b)
            
            # Calculate distributions
            mark_counts = defaultdict(int)
            for q in all_questions:
                mark_counts[str(q.marks)] += 1
            
            topic_marks_distribution = {}
            for question in all_questions:
                topic_name = question.topic.name
                if topic_name not in topic_marks_distribution:
                    topic_marks_distribution[topic_name] = 0
                topic_marks_distribution[topic_name] += question.marks
            
            # Generate unique code
            import time
            unique_code = f"PP1-{int(time.time() * 1000) % 1000000}"
            
            # Create GeneratedPaper
            generated_paper = GeneratedPaper.objects.create(
                paper=self.paper,
                unique_code=unique_code,
                total_questions=len(all_questions),
                total_marks=total_marks,
                question_ids=[str(q.id) for q in all_questions],
                selected_topics=[str(t.id) for t in self.topics],
                mark_distribution=dict(mark_counts),
                topic_distribution=topic_marks_distribution,
                question_type_distribution={
                    'section_a': len(self.selected_section_a),
                    'section_b': len(self.selected_section_b)
                },
                status='validated',
                validation_passed=True,
                metadata={
                    'paper_type': 'Paper 1',
                    'section_a_marks': section_a_marks,
                    'section_b_marks': section_b_marks,
                    'section_a_questions': len(self.selected_section_a),
                    'section_b_questions': len(self.selected_section_b)
                }
            )
            
            logger.info(f"✓ Paper saved: {unique_code}")
            logger.info(f"  - ID: {generated_paper.id}")
            logger.info(f"  - Questions: {len(all_questions)}")
            logger.info(f"  - Total Marks: {total_marks}")
            logger.info(f"  - Section A: {len(self.selected_section_a)} questions ({section_a_marks}m)")
            logger.info(f"  - Section B: {len(self.selected_section_b)} questions ({section_b_marks}m)")
            
            return generated_paper
    
    def generate(self) -> GeneratedPaper:
        """Main generation workflow"""
        self.load_data()
        self.select_questions()
        generated_paper = self.save_generated_paper()
        return generated_paper


# ==================== API ENDPOINTS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_physics_paper1(request):
    """Validate Physics Paper 1 generation prerequisites"""
    logger.info("="*70)
    logger.info("[VALIDATE] Physics Paper 1 Validation Request")
    logger.info("="*70)
    logger.info(f"[VALIDATE] User: {request.user}")
    logger.info(f"[VALIDATE] Request data: {request.data}")
    
    try:
        paper_id = request.data.get('paper_id')
        selected_topic_ids = request.data.get('topic_ids', [])
        
        logger.info(f"[VALIDATE] paper_id: {paper_id}")
        logger.info(f"[VALIDATE] topic_ids count: {len(selected_topic_ids)}")
        
        if not paper_id:
            logger.warning("[VALIDATE] Missing paper_id")
            return Response(
                {'error': 'paper_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not selected_topic_ids:
            logger.warning("[VALIDATE] Missing topic_ids")
            return Response(
                {'error': 'topic_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate
        validation_result = PhysicsPaper1Validator.validate(paper_id, selected_topic_ids)
        
        logger.info(f"[VALIDATE] Validation complete: {validation_result['valid']}")
        return Response(validation_result)
        
    except Exception as e:
        logger.error(f"[VALIDATE] Error: {str(e)}")
        logger.error(f"[VALIDATE] Traceback:", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_physics_paper1(request):
    """Generate Physics Paper 1"""
    logger.info("="*70)
    logger.info("[GENERATE] Physics Paper 1 Generation Request")
    logger.info("="*70)
    logger.info(f"[GENERATE] User: {request.user}")
    logger.info(f"[GENERATE] Request method: {request.method}")
    logger.info(f"[GENERATE] Request data: {request.data}")
    
    try:
        paper_id = request.data.get('paper_id')
        selected_topic_ids = request.data.get('topic_ids', [])
        
        logger.info(f"[GENERATE] Extracted paper_id: {paper_id}")
        logger.info(f"[GENERATE] Extracted topic_ids: {selected_topic_ids}")
        logger.info(f"[GENERATE] Topic count: {len(selected_topic_ids)}")
        
        if not paper_id:
            logger.warning("[GENERATE] Missing paper_id")
            return Response(
                {'error': 'paper_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not selected_topic_ids:
            logger.warning("[GENERATE] Missing or empty topic_ids")
            return Response(
                {'error': 'topic_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info("[GENERATE] Starting paper generation...")
        
        # Generate paper
        generator = PhysicsPaper1Generator(paper_id, selected_topic_ids)
        generated_paper = generator.generate()
        
        logger.info("[GENERATE] ✓ Paper generation completed successfully")
        logger.info(f"[GENERATE] Generated paper ID: {generated_paper.id}")
        logger.info(f"[GENERATE] Unique code: {generated_paper.unique_code}")
        
        return Response({
            'success': True,
            'message': 'Physics Paper 1 generated successfully',
            'paper_id': str(generated_paper.id),
            'generated_paper_id': str(generated_paper.id),
            'unique_code': generated_paper.unique_code,
            'total_questions': generated_paper.total_questions,
            'total_marks': generated_paper.total_marks,
            'section_a_questions': len(generator.selected_section_a),
            'section_b_questions': len(generator.selected_section_b),
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"[GENERATE]  Generation failed: {str(e)}")
        logger.error("[GENERATE] Full traceback:", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )