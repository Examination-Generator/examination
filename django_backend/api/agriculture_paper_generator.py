"""
KCSE Agriculture Paper 1 & 2 Generator

Both papers use identical structure:
- Section A: Questions 1-15 (30 marks total - 2 marks each) - ALL COMPULSORY
- Section B: Questions 16-19 (20 marks total - 5 marks each) - ALL COMPULSORY
- Section C: Questions 20-22 (60 marks total - 20 marks each) - ANSWER ANY TWO

Total student marks: 30 + 20 + 40 = 90 marks
"""

import random
import time
from collections import defaultdict
from typing import List, Dict
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Paper, Topic, Question, Subject, GeneratedPaper
from .page_number_extrctor import extract_paper_number_from_name


class KCSEAgriculturePaperGenerator:
    """
    Agriculture Paper Generator (works for both Paper 1 and Paper 2)
    - Section A: 15 questions x 2 marks = 30 marks (ALL compulsory)
    - Section B: 4 questions x 5 marks = 20 marks (ALL compulsory)
    - Section C: 3 questions x 20 marks = 60 marks (Answer ANY TWO = 40 marks)
    Total student marks: 90 marks
    """
    
    SECTION_A_COUNT = 15
    SECTION_A_MARKS_EACH = 2
    SECTION_A_TOTAL = 30
    
    SECTION_B_COUNT = 4
    SECTION_B_MARKS_EACH = 5
    SECTION_B_TOTAL = 20
    
    SECTION_C_COUNT = 3
    SECTION_C_MARKS_EACH = 20
    SECTION_C_TOTAL = 60
    SECTION_C_STUDENT_ANSWERS = 2
    SECTION_C_STUDENT_MARKS = 40
    
    STUDENT_TOTAL_MARKS = 90
    
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
        
        # Question pools by section (based on marks)
        self.section_a_questions = []  # 2 marks questions
        self.section_b_questions = []  # 5 marks questions
        self.section_c_questions = []  # 20 marks questions
        
        # Selected questions
        self.selected_section_a = []  # 15 questions
        self.selected_section_b = []  # 4 questions
        self.selected_section_c = []  # 3 questions
        self.selected_question_ids = []
        
        # Statistics
        self.attempts = 0
        self.generation_start_time = None
    
    def load_data(self):
        """Load all questions from database for selected topics"""
        # Load paper and subject
        self.paper = Paper.objects.select_related('subject').get(
            id=self.paper_id,
            is_active=True
        )
        self.subject = self.paper.subject
        
        # Load selected topics
        self.topics = list(Topic.objects.filter(
            id__in=self.selected_topic_ids,
            paper=self.paper,
            is_active=True
        ))
        
        if not self.topics:
            raise ValueError("No valid topics found for the selected IDs")
        
        # Load ALL questions for selected topics
        self.all_questions = list(Question.objects.filter(
            subject=self.subject,
            paper=self.paper,
            topic__in=self.topics,
            is_active=True
        ).select_related('topic', 'section'))
        
        if not self.all_questions:
            raise ValueError("No questions found for selected topics")
        
        # Separate questions by marks (to determine section)
        for q in self.all_questions:
            if q.marks == self.SECTION_A_MARKS_EACH:
                self.section_a_questions.append(q)
            elif q.marks == self.SECTION_B_MARKS_EACH:
                self.section_b_questions.append(q)
            elif q.marks == self.SECTION_C_MARKS_EACH:
                self.section_c_questions.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.section_a_questions)
        random.shuffle(self.section_b_questions)
        random.shuffle(self.section_c_questions)
        
        print(f"\n[DATA LOADED - AGRICULTURE PAPER]")
        print(f"  Section A (2 marks): {len(self.section_a_questions)} questions")
        print(f"  Section B (5 marks): {len(self.section_b_questions)} questions")
        print(f"  Section C (20 marks): {len(self.section_c_questions)} questions")
        print(f"  Total topics: {len(self.topics)}")
        print(f"  Total questions: {len(self.all_questions)}")
        
        # Validate minimum requirements
        if len(self.section_a_questions) < self.SECTION_A_COUNT:
            raise ValueError(
                f"Need at least {self.SECTION_A_COUNT} questions worth {self.SECTION_A_MARKS_EACH} marks each "
                f"for Section A, have {len(self.section_a_questions)}"
            )
        
        if len(self.section_b_questions) < self.SECTION_B_COUNT:
            raise ValueError(
                f"Need at least {self.SECTION_B_COUNT} questions worth {self.SECTION_B_MARKS_EACH} marks each "
                f"for Section B, have {len(self.section_b_questions)}"
            )
        
        if len(self.section_c_questions) < self.SECTION_C_COUNT:
            raise ValueError(
                f"Need at least {self.SECTION_C_COUNT} questions worth {self.SECTION_C_MARKS_EACH} marks each "
                f"for Section C, have {len(self.section_c_questions)}"
            )
    
    def _select_questions(self) -> bool:
        """Select questions for all three sections"""
        
        # Section A: Select 15 questions (2 marks each)
        if len(self.section_a_questions) < self.SECTION_A_COUNT:
            print(f"  Section A FAILED: Need {self.SECTION_A_COUNT}, have {len(self.section_a_questions)}")
            return False
        self.selected_section_a = random.sample(self.section_a_questions, self.SECTION_A_COUNT)
        
        # Section B: Select 4 questions (5 marks each)
        if len(self.section_b_questions) < self.SECTION_B_COUNT:
            print(f"  Section B FAILED: Need {self.SECTION_B_COUNT}, have {len(self.section_b_questions)}")
            return False
        self.selected_section_b = random.sample(self.section_b_questions, self.SECTION_B_COUNT)
        
        # Section C: Select 3 questions (20 marks each, student answers 2)
        if len(self.section_c_questions) < self.SECTION_C_COUNT:
            print(f"  Section C FAILED: Need {self.SECTION_C_COUNT}, have {len(self.section_c_questions)}")
            return False
        self.selected_section_c = random.sample(self.section_c_questions, self.SECTION_C_COUNT)
        
        print(f"\n[ALL SECTIONS SELECTED]")
        print(f"  Section A: {len(self.selected_section_a)} questions x {self.SECTION_A_MARKS_EACH} marks = {self.SECTION_A_TOTAL} marks")
        print(f"  Section B: {len(self.selected_section_b)} questions x {self.SECTION_B_MARKS_EACH} marks = {self.SECTION_B_TOTAL} marks")
        print(f"  Section C: {len(self.selected_section_c)} questions x {self.SECTION_C_MARKS_EACH} marks = {self.SECTION_C_TOTAL} marks (Answer ANY TWO)")
        print(f"  Student total: {self.SECTION_A_TOTAL} + {self.SECTION_B_TOTAL} + {self.SECTION_C_STUDENT_MARKS} = {self.STUDENT_TOTAL_MARKS} marks")
        
        return True
    
    def generate(self) -> Dict:
        """Generate Agriculture Paper"""
        max_attempts = 10
        self.generation_start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE AGRICULTURE PAPER GENERATION")
        print(f"{'='*70}")
        print(f"Structure:")
        print(f"  Section A: Questions 1-15 (2 marks each) = 30 marks - ALL COMPULSORY")
        print(f"  Section B: Questions 16-19 (5 marks each) = 20 marks - ALL COMPULSORY")
        print(f"  Section C: Questions 20-22 (20 marks each) = 60 marks - ANSWER ANY TWO")
        print(f"  Student Total: 90 marks")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_section_a = []
            self.selected_section_b = []
            self.selected_section_c = []
            self.selected_question_ids = []
            
            # Select all sections
            if not self._select_questions():
                if attempt % 5 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at question selection")
                continue
            
            # Success!
            generation_time = time.time() - self.generation_start_time
            
            print(f"\n{'='*70}")
            print(f"SUCCESS! Generated in {attempt} attempts ({generation_time:.2f}s)")
            print(f"{'='*70}")
            
            return self._build_result(generation_time)
        
        # Failed
        raise Exception(
            f"Failed to generate paper after {max_attempts} attempts. "
            f"Available: Section A={len(self.section_a_questions)}, "
            f"Section B={len(self.section_b_questions)}, "
            f"Section C={len(self.section_c_questions)}"
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with paper structure"""
        
        # Combine all selected questions
        all_questions = self.selected_section_a + self.selected_section_b + self.selected_section_c
        
        # Build questions data
        questions_data = []
        question_number = 1
        
        # Section A: Questions 1-15
        for q in self.selected_section_a:
            self.selected_question_ids.append(str(q.id))
            questions_data.append({
                'id': str(q.id),
                'question_number': question_number,
                'section': 'A',
                'is_compulsory': True,
                'instruction': 'Answer ALL questions in this section',
                'question_text': q.question_text,
                'answer_text': q.answer_text,
                'marks': q.marks,
                'topic': {
                    'id': str(q.topic.id),
                    'name': q.topic.name
                },
                'section_info': {
                    'id': str(q.section.id),
                    'name': q.section.name,
                    'order': q.section.order
                } if q.section else None,
                'question_type': q.kcse_question_type,
                'difficulty': q.difficulty,
            })
            question_number += 1
        
        # Section B: Questions 16-19
        for q in self.selected_section_b:
            self.selected_question_ids.append(str(q.id))
            questions_data.append({
                'id': str(q.id),
                'question_number': question_number,
                'section': 'B',
                'is_compulsory': True,
                'instruction': 'Answer ALL questions in this section',
                'question_text': q.question_text,
                'answer_text': q.answer_text,
                'marks': q.marks,
                'topic': {
                    'id': str(q.topic.id),
                    'name': q.topic.name
                },
                'section_info': {
                    'id': str(q.section.id),
                    'name': q.section.name,
                    'order': q.section.order
                } if q.section else None,
                'question_type': q.kcse_question_type,
                'difficulty': q.difficulty,
            })
            question_number += 1
        
        # Section C: Questions 20-22
        for q in self.selected_section_c:
            self.selected_question_ids.append(str(q.id))
            questions_data.append({
                'id': str(q.id),
                'question_number': question_number,
                'section': 'C',
                'is_compulsory': False,
                'instruction': 'Answer ANY TWO questions from this section',
                'question_text': q.question_text,
                'answer_text': q.answer_text,
                'marks': q.marks,
                'topic': {
                    'id': str(q.topic.id),
                    'name': q.topic.name
                },
                'section_info': {
                    'id': str(q.section.id),
                    'name': q.section.name,
                    'order': q.section.order
                } if q.section else None,
                'question_type': q.kcse_question_type,
                'difficulty': q.difficulty,
            })
            question_number += 1
        
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
        
        # Build validation report
        validation_report = {
            'all_passed': True,
            'checks': {
                'section_a_count': len(self.selected_section_a) == self.SECTION_A_COUNT,
                'section_a_marks': all(q.marks == self.SECTION_A_MARKS_EACH for q in self.selected_section_a),
                'section_b_count': len(self.selected_section_b) == self.SECTION_B_COUNT,
                'section_b_marks': all(q.marks == self.SECTION_B_MARKS_EACH for q in self.selected_section_b),
                'section_c_count': len(self.selected_section_c) == self.SECTION_C_COUNT,
                'section_c_marks': all(q.marks == self.SECTION_C_MARKS_EACH for q in self.selected_section_c),
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
                'section_a': 'Answer ALL questions in Section A',
                'section_b': 'Answer ALL questions in Section B',
                'section_c': 'Answer ANY TWO questions from Section C'
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
                'total_questions_in_paper': len(all_questions),
                'student_max_marks': self.STUDENT_TOTAL_MARKS,
                'section_a': {
                    'questions': len(self.selected_section_a),
                    'marks_each': self.SECTION_A_MARKS_EACH,
                    'total_marks': self.SECTION_A_TOTAL,
                    'compulsory': True
                },
                'section_b': {
                    'questions': len(self.selected_section_b),
                    'marks_each': self.SECTION_B_MARKS_EACH,
                    'total_marks': self.SECTION_B_TOTAL,
                    'compulsory': True
                },
                'section_c': {
                    'questions': len(self.selected_section_c),
                    'marks_each': self.SECTION_C_MARKS_EACH,
                    'total_marks': self.SECTION_C_TOTAL,
                    'answer_any': self.SECTION_C_STUDENT_ANSWERS,
                    'student_marks': self.SECTION_C_STUDENT_MARKS,
                    'compulsory': False
                },
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': validation_report['checks']
            }
        }


# Django Views

@require_http_methods(["POST"])
def validate_agriculture_paper_pool(request):
    """Validate if there are enough questions to generate Agriculture paper"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('topic_ids', [])
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'can_generate': False,
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
        
        # Load paper and topics
        paper = Paper.objects.select_related('subject').get(
            id=paper_id,
            is_active=True
        )
        
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
        
        # Load all questions
        all_questions = list(Question.objects.filter(
            subject=paper.subject,
            paper=paper,
            topic__in=topics,
            is_active=True
        ).select_related('topic', 'section'))
        
        # Count questions by marks
        section_a_count = sum(1 for q in all_questions if q.marks == 2)
        section_b_count = sum(1 for q in all_questions if q.marks == 5)
        section_c_count = sum(1 for q in all_questions if q.marks == 20)
        
        # Check requirements
        can_generate = (
            section_a_count >= 15 and
            section_b_count >= 4 and
            section_c_count >= 3
        )
        
        issues = []
        if section_a_count < 15:
            issues.append(f"Need 15 questions worth 2 marks for Section A, have {section_a_count}")
        if section_b_count < 4:
            issues.append(f"Need 4 questions worth 5 marks for Section B, have {section_b_count}")
        if section_c_count < 3:
            issues.append(f"Need 3 questions worth 20 marks for Section C, have {section_c_count}")
        
        message = "Ready to generate Agriculture paper" if can_generate else "Insufficient questions: " + "; ".join(issues)
        
        return JsonResponse({
            'can_generate': can_generate,
            'available_counts': {
                'section_a_2_marks': section_a_count,
                'section_b_5_marks': section_b_count,
                'section_c_20_marks': section_c_count,
                'total_questions': len(all_questions),
            },
            'required_counts': {
                'section_a': 15,
                'section_b': 4,
                'section_c': 3,
            },
            'paper_structure': {
                'section_a': 'Questions 1-15 (2 marks each) = 30 marks - ALL COMPULSORY',
                'section_b': 'Questions 16-19 (5 marks each) = 20 marks - ALL COMPULSORY',
                'section_c': 'Questions 20-22 (20 marks each) = 60 marks - ANSWER ANY TWO',
                'student_total': '90 marks'
            },
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'can_generate': False,
            'message': f'Validation error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def generate_agriculture_paper(request):
    """Generate KCSE Agriculture Paper 1 or 2"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('topic_ids', [])
        
        if paper_id:
            paper_name = Paper.objects.get(id=paper_id).name
            paper_number = extract_paper_number_from_name(paper_name)
        
        
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
        
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Generate unique code
        timestamp = datetime.now().strftime('%y%m%d%H%M%S')
        unique_code = f"AGR{paper_number}-{timestamp}"
        
        # Initialize generator
        generator = KCSEAgriculturePaperGenerator(
            paper_id=paper_id,
            selected_topic_ids=selected_topic_ids,
            user=user
        )
        
        # Load data and generate
        generator.load_data()
        result = generator.generate()
        
        # Create GeneratedPaper record
        generated_paper = GeneratedPaper.objects.create(
            paper=generator.paper,
            unique_code=unique_code,
            status='validated',
            question_ids=result['question_ids'],
            selected_topics=selected_topic_ids,
            topic_adjustments={},
            total_marks=result['statistics']['student_max_marks'],
            total_questions=result['statistics']['total_questions_in_paper'],
            mark_distribution=result['mark_distribution'],
            topic_distribution=result['topic_distribution'],
            question_type_distribution=result['question_type_distribution'],
            validation_passed=result['validation_report']['all_passed'],
            validation_report=result['validation_report'],
            generation_attempts=generator.attempts,
            backtracking_count=0,
            generation_time_seconds=result['generation_time'],
            generated_by=user,
        )
        
        print(f"\n[DATABASE RECORD CREATED]")
        print(f"  Unique Code: {unique_code}")
        print(f"  Record ID: {generated_paper.id}")
        print(f"  Status: {generated_paper.status}")
        
        # Build response
        response = {
            'paper': result['paper'],
            'questions': result['questions'],
            'question_ids': result['question_ids'],
            'instructions': result['instructions'],
            'statistics': result['statistics'],
            'unique_code': unique_code,
            'generated_paper_id': str(generated_paper.id),
            'total_marks': result['statistics']['student_max_marks'],
            'total_questions': result['statistics']['total_questions_in_paper'],
            'status': generated_paper.status,
            'paper_id': str(generator.paper.id),
            'created_at': generated_paper.created_at.isoformat() if hasattr(generated_paper, 'created_at') else None,
        }
        
        return JsonResponse(response, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"\n[GENERATION ERROR]")
        print(error_details)
        return JsonResponse({
            'message': f'Generation error: {str(e)}'
        }, status=500)
