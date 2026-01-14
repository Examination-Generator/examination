"""
KCSE Physics Paper 1 & 2 Generator
Both papers follow similar structure with different Section A distributions

PAPER 1:
- Section A: 13 questions = 25 marks (ALL COMPULSORY)
  Distribution: 6 x 2-mark, 4 x 1-mark, 3 x 3-mark
- Section B: 5 questions = 55 marks (ALL COMPULSORY, 8+ marks each)
- Paper Total: 18 questions, 80 marks

PAPER 2:
- Section A: 13 questions = 25 marks (ALL COMPULSORY)
  Distribution: 5 x 1-mark, 4 x 2-mark, 4 x 3-mark
- Section B: 5 questions = 55 marks (ALL COMPULSORY, 8+ marks each)
- Paper Total: 18 questions, 80 marks
"""

import random
import time
import logging
from collections import defaultdict
from typing import List, Dict, Optional
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction

from .models import Paper, Topic, Question, Section, Subject, GeneratedPaper
from .page_number_extrctor import extract_paper_number_from_name

# Set up logger
logger = logging.getLogger(__name__)


class KCSEPhysicsPaperGenerator:
    """
    Base class for Physics Paper generation
    Handles common logic for both Paper 1 and Paper 2
    """
    
    # Common constraints
    TOTAL_MARKS = 80
    SECTION_A_QUESTIONS = 13
    SECTION_A_TOTAL_MARKS = 25
    SECTION_B_QUESTIONS = 5
    SECTION_B_TOTAL_MARKS = 55
    SECTION_B_MIN_MARKS = 8  # Section B questions must be 8+ marks
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str], user=None):
        """Initialize generator"""
        self.paper_id = paper_id
        self.selected_topic_ids = selected_topic_ids
        self.user = user
        
        # Data storage
        self.paper = None
        self.subject = None
        self.topics = []
        self.all_questions = []
        self.section_a = None
        self.section_b = None
        
        # Question pools
        self.one_mark_pool = []
        self.two_mark_pool = []
        self.three_mark_pool = []
        self.section_b_pool = []  # 8+ marks questions
        
        # Selection tracking
        self.selected_section_a = []
        self.selected_section_b = []
        self.selected_question_ids = []
        self.used_ids = set()
        
        # Statistics
        self.attempts = 0
        self.generation_start_time = None
    
    def get_paper_number(self) -> int:
        """Return paper number (1 or 2) - to be implemented by subclass"""
        raise NotImplementedError("Subclass must implement get_paper_number")
    
    def get_section_a_distribution(self) -> Dict[int, int]:
        """
        Return Section A mark distribution - to be implemented by subclass
        Returns: {marks: count} e.g. {1: 4, 2: 6, 3: 3}
        """
        raise NotImplementedError("Subclass must implement get_section_a_distribution")
    
    def load_data(self):
        """Load all questions from database for selected topics"""
        logger.info("="*70)
        logger.info(f"LOADING DATA FOR PHYSICS PAPER {self.get_paper_number()} GENERATION")
        logger.info("="*70)
        
        # Load paper and subject
        try:
            self.paper = Paper.objects.select_related('subject').get(
                id=self.paper_id,
                is_active=True
            )
            self.subject = self.paper.subject
            logger.info(f"Paper loaded: {self.paper.name} ({self.subject.name})")
        except Paper.DoesNotExist:
            logger.error(f"Paper not found: {self.paper_id}")
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
        
        # Load selected topics
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
        
        # Load ALL questions for selected topics
        self.all_questions = list(Question.objects.filter(
            subject=self.subject,
            paper=self.paper,
            topic__in=self.topics,
            is_active=True
        ).select_related('topic', 'section'))
        
        if not self.all_questions:
            logger.error("✗ No questions found")
            raise ValueError("No questions found for selected topics")
        
        # Separate questions by section and marks
        for q in self.all_questions:
            if q.section == self.section_a:
                # Section A: 1, 2, 3 mark questions
                if q.marks == 1:
                    self.one_mark_pool.append(q)
                elif q.marks == 2:
                    self.two_mark_pool.append(q)
                elif q.marks == 3:
                    self.three_mark_pool.append(q)
            elif q.section == self.section_b:
                # Section B: 8+ marks questions
                if q.marks >= self.SECTION_B_MIN_MARKS:
                    self.section_b_pool.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.one_mark_pool)
        random.shuffle(self.two_mark_pool)
        random.shuffle(self.three_mark_pool)
        random.shuffle(self.section_b_pool)
        
        logger.info("Question pools loaded:")
        logger.info(f"  Section A:")
        logger.info(f"    - 1-mark: {len(self.one_mark_pool)} questions")
        logger.info(f"    - 2-mark: {len(self.two_mark_pool)} questions")
        logger.info(f"    - 3-mark: {len(self.three_mark_pool)} questions")
        logger.info(f"  Section B:")
        logger.info(f"    - 8+ marks: {len(self.section_b_pool)} questions")
        
        # Get required distribution
        distribution = self.get_section_a_distribution()
        
        # Validate question availability
        if len(self.one_mark_pool) < distribution.get(1, 0):
            raise ValueError(
                f"Insufficient 1-mark questions: have {len(self.one_mark_pool)}, "
                f"need {distribution.get(1, 0)}"
            )
        if len(self.two_mark_pool) < distribution.get(2, 0):
            raise ValueError(
                f"Insufficient 2-mark questions: have {len(self.two_mark_pool)}, "
                f"need {distribution.get(2, 0)}"
            )
        if len(self.three_mark_pool) < distribution.get(3, 0):
            raise ValueError(
                f"Insufficient 3-mark questions: have {len(self.three_mark_pool)}, "
                f"need {distribution.get(3, 0)}"
            )
        if len(self.section_b_pool) < 10:  # Need at least 10 for combinations
            raise ValueError(
                f"Insufficient Section B questions: have {len(self.section_b_pool)}, "
                f"need at least 10 questions with 8+ marks"
            )
        
        logger.info("✓ Data loaded and validated successfully")
    
    def _select_section_a(self) -> bool:
        """Select Section A questions based on paper-specific distribution"""
        distribution = self.get_section_a_distribution()
        
        # Get required counts
        one_mark_needed = distribution.get(1, 0)
        two_mark_needed = distribution.get(2, 0)
        three_mark_needed = distribution.get(3, 0)
        
        # Get available questions
        available_1mark = [q for q in self.one_mark_pool if q.id not in self.used_ids]
        available_2mark = [q for q in self.two_mark_pool if q.id not in self.used_ids]
        available_3mark = [q for q in self.three_mark_pool if q.id not in self.used_ids]
        
        # Check availability
        if (len(available_1mark) < one_mark_needed or 
            len(available_2mark) < two_mark_needed or 
            len(available_3mark) < three_mark_needed):
            return False
        
        # Select questions
        selected = []
        selected.extend(available_1mark[:one_mark_needed])
        selected.extend(available_2mark[:two_mark_needed])
        selected.extend(available_3mark[:three_mark_needed])
        
        # Verify counts and marks
        total_questions = len(selected)
        total_marks = sum(q.marks for q in selected)
        
        if total_questions != self.SECTION_A_QUESTIONS:
            logger.warning(f"Section A question count mismatch: {total_questions} != {self.SECTION_A_QUESTIONS}")
            return False
        
        if total_marks != self.SECTION_A_TOTAL_MARKS:
            logger.warning(f"Section A marks mismatch: {total_marks} != {self.SECTION_A_TOTAL_MARKS}")
            return False
        
        # Shuffle to randomize order
        random.shuffle(selected)
        
        # Accept selection
        self.selected_section_a = selected
        for q in selected:
            self.used_ids.add(q.id)
        
        logger.info(f"\n[SECTION A SELECTED]")
        logger.info(f"  Questions: {total_questions} (all compulsory)")
        logger.info(f"  Distribution: {one_mark_needed}x1-mark, {two_mark_needed}x2-mark, {three_mark_needed}x3-mark")
        logger.info(f"  Total marks: {total_marks}")
        
        return True
    
    def _select_section_b(self) -> bool:
        """Select Section B questions: 5 questions totaling exactly 55 marks"""
        available = [q for q in self.section_b_pool if q.id not in self.used_ids]
        
        if len(available) < self.SECTION_B_QUESTIONS:
            return False
        
        # Try to find combination of 5 questions that sum to exactly 55 marks
        from itertools import combinations
        
        for combo in combinations(available, self.SECTION_B_QUESTIONS):
            total_marks = sum(q.marks for q in combo)
            if total_marks == self.SECTION_B_TOTAL_MARKS:
                # Found exact match!
                self.selected_section_b = list(combo)
                for q in combo:
                    self.used_ids.add(q.id)
                
                logger.info(f"\n[SECTION B SELECTED]")
                logger.info(f"  Questions: {len(combo)} (all compulsory)")
                logger.info(f"  Question marks: {[q.marks for q in combo]}")
                logger.info(f"  Total marks: {total_marks}")
                
                return True
        
        # If no exact match, find closest
        logger.warning("No exact 55-mark combination found, trying closest match...")
        best_combo = None
        best_diff = float('inf')
        
        for combo in combinations(available, self.SECTION_B_QUESTIONS):
            total_marks = sum(q.marks for q in combo)
            diff = abs(total_marks - self.SECTION_B_TOTAL_MARKS)
            
            if diff < best_diff:
                best_diff = diff
                best_combo = combo
        
        if best_combo:
            self.selected_section_b = list(best_combo)
            for q in best_combo:
                self.used_ids.add(q.id)
            
            total_marks = sum(q.marks for q in best_combo)
            logger.warning(f"Using closest match: {total_marks} marks (diff: {best_diff})")
            
            return best_diff <= 2  # Accept if within 2 marks
        
        return False
    
    def generate(self) -> Dict:
        """Generate Physics Paper"""
        max_attempts = 100
        self.generation_start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE PHYSICS PAPER {self.get_paper_number()} GENERATION")
        print(f"{'='*70}")
        
        distribution = self.get_section_a_distribution()
        print(f"Structure:")
        print(f"  Section A: 13 questions = 25 marks (ALL COMPULSORY)")
        print(f"    Distribution: {distribution[1]}x1-mark, {distribution[2]}x2-mark, {distribution[3]}x3-mark")
        print(f"  Section B: 5 questions = 55 marks (ALL COMPULSORY, 8+ marks each)")
        print(f"  Paper Total: 80 marks")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_section_a = []
            self.selected_section_b = []
            self.selected_question_ids = []
            self.used_ids = set()
            
            # Select Section A (13 questions, 25 marks)
            if not self._select_section_a():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section A selection")
                continue
            
            # Select Section B (5 questions, 55 marks)
            if not self._select_section_b():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section B selection")
                continue
            
            # Success!
            generation_time = time.time() - self.generation_start_time
            
            # Calculate final totals
            total_questions = len(self.selected_section_a) + len(self.selected_section_b)
            section_a_marks = sum(q.marks for q in self.selected_section_a)
            section_b_marks = sum(q.marks for q in self.selected_section_b)
            paper_total_marks = section_a_marks + section_b_marks
            
            print(f"\n{'='*70}")
            print(f"SUCCESS! Generated in {attempt} attempts ({generation_time:.2f}s)")
            print(f"{'='*70}")
            print(f"Paper Structure:")
            print(f"  Total Questions: {total_questions}")
            print(f"  Section A: {len(self.selected_section_a)} questions = {section_a_marks} marks")
            print(f"  Section B: {len(self.selected_section_b)} questions = {section_b_marks} marks")
            print(f"  Paper Total: {paper_total_marks} marks")
            
            # Validate paper structure
            if total_questions != (self.SECTION_A_QUESTIONS + self.SECTION_B_QUESTIONS):
                print(f"\nERROR: Total questions is {total_questions}, expected {self.SECTION_A_QUESTIONS + self.SECTION_B_QUESTIONS}")
                continue
            
            if section_a_marks != self.SECTION_A_TOTAL_MARKS:
                print(f"\nERROR: Section A marks is {section_a_marks}, expected {self.SECTION_A_TOTAL_MARKS}")
                continue
            
            if section_b_marks != self.SECTION_B_TOTAL_MARKS:
                print(f"\nERROR: Section B marks is {section_b_marks}, expected {self.SECTION_B_TOTAL_MARKS}")
                continue
            
            if paper_total_marks != self.TOTAL_MARKS:
                print(f"\nERROR: Paper total is {paper_total_marks} marks, expected {self.TOTAL_MARKS}")
                continue
            
            return self._build_result(generation_time)
        
        # Failed
        raise Exception(
            f"Failed to generate paper after {max_attempts} attempts. "
            f"Available: 1-mark={len(self.one_mark_pool)}, "
            f"2-mark={len(self.two_mark_pool)}, "
            f"3-mark={len(self.three_mark_pool)}, "
            f"Section B (8+)={len(self.section_b_pool)}"
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with strictly ordered sections"""
        
        # Combine sections in strict order: Section A (1-13), then Section B (14-18)
        all_questions = self.selected_section_a + self.selected_section_b
        
        # Build questions data with proper numbering
        questions_data = []
        section_a_count = len(self.selected_section_a)
        
        for idx, question in enumerate(all_questions, start=1):
            self.selected_question_ids.append(str(question.id))
            
            # Determine section
            section_letter = "A" if idx <= section_a_count else "B"
            is_compulsory = True  # All questions are compulsory in Physics
            
            questions_data.append({
                'id': str(question.id),
                'question_number': idx,
                'section_letter': section_letter,
                'is_compulsory': is_compulsory,
                'instruction': 'Compulsory',
                'question_text': question.question_text,
                'answer_text': question.answer_text,
                'marks': question.marks,
                'topic': {
                    'id': str(question.topic.id),
                    'name': question.topic.name
                },
                'section': {
                    'id': str(question.section.id),
                    'name': question.section.name,
                    'order': question.section.order
                } if question.section else None,
                'question_type': question.kcse_question_type,
                'difficulty': question.difficulty,
            })
        
        # Calculate marks
        section_a_marks = sum(q.marks for q in self.selected_section_a)
        section_b_marks = sum(q.marks for q in self.selected_section_b)
        
        # Build mark distribution
        mark_distribution = defaultdict(int)
        for q in all_questions:
            mark_distribution[str(q.marks)] += 1
        
        # Build topic distribution
        topic_distribution = defaultdict(int)
        for q in all_questions:
            topic_distribution[str(q.topic.id)] += 1
        
        # Build question type distribution
        question_type_distribution = defaultdict(int)
        for q in all_questions:
            qtype = q.kcse_question_type or 'Unknown'
            question_type_distribution[qtype] += 1
        
        # Build Section A breakdown
        section_a_breakdown = defaultdict(int)
        for q in self.selected_section_a:
            section_a_breakdown[q.marks] += 1
        
        # Build validation report
        distribution = self.get_section_a_distribution()
        validation_report = {
            'all_passed': True,
            'checks': {
                'section_a_count': len(self.selected_section_a) == self.SECTION_A_QUESTIONS,
                'section_a_marks': section_a_marks == self.SECTION_A_TOTAL_MARKS,
                'section_a_1mark': section_a_breakdown[1] == distribution.get(1, 0),
                'section_a_2mark': section_a_breakdown[2] == distribution.get(2, 0),
                'section_a_3mark': section_a_breakdown[3] == distribution.get(3, 0),
                'section_b_count': len(self.selected_section_b) == self.SECTION_B_QUESTIONS,
                'section_b_marks': section_b_marks == self.SECTION_B_TOTAL_MARKS,
                'paper_total_marks': (section_a_marks + section_b_marks) == self.TOTAL_MARKS,
            }
        }
        validation_report['all_passed'] = all(validation_report['checks'].values())
        
        return {
            'paper': {
                'id': str(self.paper.id),
                'name': self.paper.name,
                'subject': {
                    'id': str(self.subject.id),
                    'name': self.subject.name
                }
            },
            'instructions': {
                'section_a': 'Answer ALL questions in this section',
                'section_b': 'Answer ALL questions in this section'
            },
            'questions': questions_data,
            'question_ids': self.selected_question_ids,
            'all_questions': all_questions,
            'mark_distribution': dict(mark_distribution),
            'topic_distribution': dict(topic_distribution),
            'question_type_distribution': dict(question_type_distribution),
            'validation_report': validation_report,
            'generation_time': generation_time,
            'statistics': {
                'total_questions': len(all_questions),
                'paper_total_marks': section_a_marks + section_b_marks,
                'section_a': {
                    'questions': len(self.selected_section_a),
                    'marks': section_a_marks,
                    'breakdown': {
                        '1_mark': section_a_breakdown[1],
                        '2_mark': section_a_breakdown[2],
                        '3_mark': section_a_breakdown[3],
                    },
                    'instruction': 'All compulsory'
                },
                'section_b': {
                    'questions': len(self.selected_section_b),
                    'marks': section_b_marks,
                    'question_marks': [q.marks for q in self.selected_section_b],
                    'instruction': 'All compulsory'
                },
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': validation_report['checks']
            }
        }


class KCSEPhysicsPaper1Generator(KCSEPhysicsPaperGenerator):
    """
    Physics Paper 1 Generator
    Section A: 6x2-mark, 4x1-mark, 3x3-mark = 25 marks
    """
    
    def get_paper_number(self) -> int:
        return 1
    
    def get_section_a_distribution(self) -> Dict[int, int]:
        """Paper 1: 6 two-mark, 4 one-mark, 3 three-mark"""
        return {
            1: 4,  # 4 one-mark questions
            2: 6,  # 6 two-mark questions (majority)
            3: 3   # 3 three-mark questions
        }


class KCSEPhysicsPaper2Generator(KCSEPhysicsPaperGenerator):
    """
    Physics Paper 2 Generator
    Section A: 5x1-mark, 4x2-mark, 4x3-mark = 25 marks
    """
    
    def get_paper_number(self) -> int:
        return 2
    
    def get_section_a_distribution(self) -> Dict[int, int]:
        """Paper 2: 5 one-mark, 4 two-mark, 4 three-mark"""
        return {
            1: 5,  # 5 one-mark questions (majority)
            2: 4,  # 4 two-mark questions
            3: 4   # 4 three-mark questions
        }


# Django Views

@require_http_methods(["POST"])
def validate_physics_paper_pool(request):
    """Validate if there are enough questions to generate Physics paper"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('topic_ids', [])
        paper_number = data.get('paper_number', 1)  # 1 or 2
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'can_generate': False,
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
        
        if paper_number not in [1, 2]:
            return JsonResponse({
                'can_generate': False,
                'message': 'Invalid paper_number. Must be 1 or 2'
            }, status=400)
        
        # Load paper and sections
        paper = Paper.objects.select_related('subject').get(
            id=paper_id,
            is_active=True
        )
        
        section_a = Section.objects.filter(
            paper=paper,
            name__icontains='A',
            is_active=True
        ).first()
        
        section_b = Section.objects.filter(
            paper=paper,
            name__icontains='B',
            is_active=True
        ).first()
        
        if not section_a or not section_b:
            return JsonResponse({
                'can_generate': False,
                'message': 'Section A or Section B not found for this paper'
            }, status=404)
        
        # Load topics
        topics = list(Topic.objects.filter(
            id__in=selected_topic_ids,
            paper=paper,
            is_active=True
        ))
        
        if not topics:
            return JsonResponse({
                'can_generate': False,
                'message': 'No valid topics found'
            }, status=404)
        
        # Count questions by type
        one_mark_count = Question.objects.filter(
            paper=paper,
            section=section_a,
            topic__in=topics,
            marks=1,
            is_active=True
        ).count()
        
        two_mark_count = Question.objects.filter(
            paper=paper,
            section=section_a,
            topic__in=topics,
            marks=2,
            is_active=True
        ).count()
        
        three_mark_count = Question.objects.filter(
            paper=paper,
            section=section_a,
            topic__in=topics,
            marks=3,
            is_active=True
        ).count()
        
        section_b_count = Question.objects.filter(
            paper=paper,
            section=section_b,
            topic__in=topics,
            marks__gte=8,
            is_active=True
        ).count()
        
        # Get required distribution based on paper number
        if paper_number == 1:
            required_1mark = 4
            required_2mark = 6
            required_3mark = 3
            distribution_text = "6x2-mark, 4x1-mark, 3x3-mark"
        else:  # Paper 2
            required_1mark = 5
            required_2mark = 4
            required_3mark = 4
            distribution_text = "5x1-mark, 4x2-mark, 4x3-mark"
        
        # Validate
        section_a_ok = (one_mark_count >= required_1mark and 
                       two_mark_count >= required_2mark and 
                       three_mark_count >= required_3mark)
        section_b_ok = section_b_count >= 10  # Need at least 10 for combinations
        can_generate = section_a_ok and section_b_ok
        
        # Build message
        issues = []
        if not section_a_ok:
            if one_mark_count < required_1mark:
                issues.append(f"1-mark: have {one_mark_count}, need {required_1mark}")
            if two_mark_count < required_2mark:
                issues.append(f"2-mark: have {two_mark_count}, need {required_2mark}")
            if three_mark_count < required_3mark:
                issues.append(f"3-mark: have {three_mark_count}, need {required_3mark}")
        if not section_b_ok:
            issues.append(f"Section B (8+ marks): have {section_b_count}, need at least 10")
        
        message = f"Ready to generate Physics Paper {paper_number}" if can_generate else "Insufficient questions: " + "; ".join(issues)
        
        return JsonResponse({
            'can_generate': can_generate,
            'available_counts': {
                'section_a_1mark': one_mark_count,
                'section_a_2mark': two_mark_count,
                'section_a_3mark': three_mark_count,
                'section_b_8plus': section_b_count,
            },
            'required_counts': {
                'section_a_1mark': required_1mark,
                'section_a_2mark': required_2mark,
                'section_a_3mark': required_3mark,
                'section_b_8plus': 10,
            },
            'paper_structure': {
                'section_a': f'13 questions = 25 marks ({distribution_text})',
                'section_b': '5 questions = 55 marks (8+ marks each)',
                'paper_total': '80 marks',
                'paper_number': paper_number
            },
            'validation': {
                'section_a_ok': section_a_ok,
                'section_b_ok': section_b_ok,
            },
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'can_generate': False,
            'message': f'Validation error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def generate_physics_paper(request):
    """Generate KCSE Physics Paper 1 or 2"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('topic_ids', [])
        if paper_id:
            paper_number = extract_paper_number_from_name(Paper.objects.get(id=paper_id).name) 
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
        
        if paper_number not in [1, 2 ,3]:
            return JsonResponse({
                'message': 'Invalid paper_number. Must be 1, 2, or 3'
            }, status=400)
        
        # Get user from request if available
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        
        
        logger.info(f"[GENERATE] Starting Physics Paper {paper_number} generation")
        logger.info(f"[GENERATE] User: {user}")
        logger.info(f"[GENERATE] Paper ID: {paper_id}")
        logger.info(f"[GENERATE] Topics: {len(selected_topic_ids)}")
        
        # Initialize appropriate generator
        if paper_number == 1:
            generator = KCSEPhysicsPaper1Generator(
                paper_id=paper_id,
                selected_topic_ids=selected_topic_ids,
                user=user
            )
        else:
            generator = KCSEPhysicsPaper2Generator(
                paper_id=paper_id,
                selected_topic_ids=selected_topic_ids,
                user=user
            )
        
        # Load data and generate
        generator.load_data()
        result = generator.generate()
        
        # Generate unique code
        current_year = datetime.now().year
        paper = generator.paper
        year_count = GeneratedPaper.objects.filter(
            paper=paper,
            created_at__year=current_year
        ).count()
        
        unique_code = f"PHY{paper_number}-{current_year}-{year_count + 1:03d}"
        
        # Create GeneratedPaper record
        with transaction.atomic():
            generated_paper = GeneratedPaper.objects.create(
                paper=generator.paper,
                unique_code=unique_code,
                status='validated',
                question_ids=result['question_ids'],
                selected_topics=selected_topic_ids,
                topic_adjustments={},
                total_marks=result['statistics']['paper_total_marks'],
                total_questions=result['statistics']['total_questions'],
                mark_distribution=result['mark_distribution'],
                topic_distribution=result['topic_distribution'],
                question_type_distribution=result['question_type_distribution'],
                validation_passed=result['validation_report']['all_passed'],
                validation_report=result['validation_report'],
                generation_attempts=generator.attempts,
                backtracking_count=0,
                generation_time_seconds=result['generation_time'],
                generated_by=user,
                metadata={
                    'paper_number': paper_number,
                    'paper_type': f'Paper {paper_number}',
                    'section_a_breakdown': result['statistics']['section_a']['breakdown'],
                    'section_b_question_marks': result['statistics']['section_b']['question_marks']
                }
            )
        
        logger.info(f"\n[DATABASE RECORD CREATED]")
        logger.info(f"  Unique Code: {unique_code}")
        logger.info(f"  Record ID: {generated_paper.id}")
        logger.info(f"  Status: {generated_paper.status}")
        logger.info(f"  Total Questions: {generated_paper.total_questions}")
        logger.info(f"  Total Marks: {generated_paper.total_marks}")
        
        # Build response with all required fields
        response = {
            'paper': result['paper'],
            'questions': result['questions'],
            'question_ids': result['question_ids'],
            'instructions': result['instructions'],
            'statistics': result['statistics'],
            'unique_code': unique_code,
            'generated_paper_id': str(generated_paper.id),
            'total_marks': result['statistics']['paper_total_marks'],
            'total_questions': result['statistics']['total_questions'],
            'status': generated_paper.status,
            'paper_id': str(generator.paper.id),
            'paper_number': paper_number,
            'created_at': generated_paper.created_at.isoformat() if hasattr(generated_paper, 'created_at') else None,
        }
        
        logger.info("[GENERATE] ✓ Paper generation completed successfully")
        
        return JsonResponse(response, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"\n[GENERATION ERROR]")
        logger.error(error_details)
        return JsonResponse({
            'message': f'Generation error: {str(e)}'
        }, status=500)