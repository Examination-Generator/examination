"""
KCSE Business Studies Paper 1 & 2 Generator

PAPER 1:
- Fixed 25 questions
- Total: 100 marks
- Primarily 4-mark questions (to ensure 25 questions exactly)
- May include some 3-mark or 5-mark questions, but total must be 25 questions

PAPER 2:
- 6 questions, each 20 marks
- Each question has two parts (a and b) from different topics:
  * Part a: 12 marks
  * Part b: 8 marks
- Students answer 5 questions out of 6
"""

import random
import time
from collections import defaultdict
from typing import List, Dict, Optional
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Paper, Topic, Question, Subject, GeneratedPaper
from .page_number_extrctor import extract_paper_number_from_name


class KCSEBusinessPaper1Generator:
    """
    Business Studies Paper 1 Generator
    - Fixed 25 questions
    - Total: 100 marks
    - Primarily 4-mark questions (25 questions x 4 marks = 100 marks)
    """
    
    REQUIRED_QUESTIONS = 25
    TOTAL_MARKS = 100
    PREFERRED_MARKS = 4  # Primarily select 4-mark questions
    
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
        
        # Question pools by marks
        self.questions_4_marks = []  # Preferred
        self.questions_3_marks = []  # Optional
        self.questions_5_marks = []  # Optional
        self.questions_other_marks = []  # Other marks
        
        # Selection tracking
        self.selected_questions = []
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
        
        # Separate questions by marks
        for q in self.all_questions:
            if q.marks == 4:
                self.questions_4_marks.append(q)
            elif q.marks == 3:
                self.questions_3_marks.append(q)
            elif q.marks == 5:
                self.questions_5_marks.append(q)
            else:
                self.questions_other_marks.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.questions_4_marks)
        random.shuffle(self.questions_3_marks)
        random.shuffle(self.questions_5_marks)
        random.shuffle(self.questions_other_marks)
        
        print(f"\n[DATA LOADED - BUSINESS PAPER 1]")
        print(f"  Total topics: {len(self.topics)}")
        print(f"  Total questions: {len(self.all_questions)}")
        print(f"  4-mark questions: {len(self.questions_4_marks)}")
        print(f"  3-mark questions: {len(self.questions_3_marks)}")
        print(f"  5-mark questions: {len(self.questions_5_marks)}")
        print(f"  Other marks: {len(self.questions_other_marks)}")
        
        # Check if we have enough 4-mark questions
        if len(self.questions_4_marks) < self.REQUIRED_QUESTIONS:
            print(f"\n[WARNING] Insufficient 4-mark questions!")
            print(f"  Required: {self.REQUIRED_QUESTIONS}")
            print(f"  Available: {len(self.questions_4_marks)}")
            print(f"  Will attempt to fill with 3-mark and 5-mark questions if needed")
    
    def _select_25_questions(self) -> bool:
        """
        Select exactly 25 questions totaling 100 marks
        Prioritize 4-mark questions
        """
        selected = []
        current_marks = 0
        
        # First, try to select 25 questions of 4 marks each (ideal case)
        if len(self.questions_4_marks) >= self.REQUIRED_QUESTIONS:
            selected = random.sample(self.questions_4_marks, self.REQUIRED_QUESTIONS)
            current_marks = sum(q.marks for q in selected)
            
            if current_marks == self.TOTAL_MARKS and len(selected) == self.REQUIRED_QUESTIONS:
                self.selected_questions = selected
                return True
        
        # If not enough 4-mark questions, mix with 3-mark and 5-mark
        # Strategy: Use as many 4-mark questions as possible, then fill gaps
        available_4_marks = self.questions_4_marks.copy()
        available_3_marks = self.questions_3_marks.copy()
        available_5_marks = self.questions_5_marks.copy()
        
        # Try different combinations
        for num_4_marks in range(len(available_4_marks), -1, -1):
            if num_4_marks > len(available_4_marks):
                continue
            
            remaining_questions = self.REQUIRED_QUESTIONS - num_4_marks
            remaining_marks = self.TOTAL_MARKS - (num_4_marks * 4)
            
            # Try to fill remaining with 3-mark and 5-mark questions
            for num_5_marks in range(min(remaining_questions, len(available_5_marks)), -1, -1):
                num_3_marks = remaining_questions - num_5_marks
                
                if num_3_marks > len(available_3_marks):
                    continue
                
                if num_3_marks < 0:
                    continue
                
                # Check if marks total is correct
                total_marks_check = (num_4_marks * 4) + (num_3_marks * 3) + (num_5_marks * 5)
                
                if total_marks_check == self.TOTAL_MARKS:
                    # Found valid combination!
                    selected = []
                    
                    if num_4_marks > 0:
                        selected.extend(random.sample(available_4_marks, num_4_marks))
                    
                    if num_3_marks > 0:
                        selected.extend(random.sample(available_3_marks, num_3_marks))
                    
                    if num_5_marks > 0:
                        selected.extend(random.sample(available_5_marks, num_5_marks))
                    
                    random.shuffle(selected)
                    self.selected_questions = selected
                    
                    print(f"\n[QUESTION SELECTION SUCCESSFUL]")
                    print(f"  4-mark questions: {num_4_marks}")
                    print(f"  3-mark questions: {num_3_marks}")
                    print(f"  5-mark questions: {num_5_marks}")
                    print(f"  Total questions: {len(selected)}")
                    print(f"  Total marks: {sum(q.marks for q in selected)}")
                    
                    return True
        
        return False
    
    def generate(self) -> Dict:
        """Generate Business Studies Paper 1"""
        max_attempts = 100
        self.generation_start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE BUSINESS STUDIES PAPER 1 GENERATION")
        print(f"{'='*70}")
        print(f"Requirements:")
        print(f"  Total Questions: {self.REQUIRED_QUESTIONS} (FIXED)")
        print(f"  Total Marks: {self.TOTAL_MARKS}")
        print(f"  Average Marks: {self.TOTAL_MARKS / self.REQUIRED_QUESTIONS} marks/question")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_questions = []
            self.selected_question_ids = []
            
            # Select 25 questions totaling 100 marks
            if not self._select_25_questions():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed to select 25 questions totaling 100 marks")
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
            f"Available: 4-mark={len(self.questions_4_marks)}, "
            f"3-mark={len(self.questions_3_marks)}, "
            f"5-mark={len(self.questions_5_marks)}"
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with paper structure"""
        
        # Build questions data
        questions_data = []
        
        for idx, q in enumerate(self.selected_questions, start=1):
            self.selected_question_ids.append(str(q.id))
            questions_data.append({
                'id': str(q.id),
                'question_number': idx,
                'is_compulsory': True,
                'instruction': 'Answer ALL questions',
                'question_text': q.question_text,
                'answer_text': q.answer_text,
                'marks': q.marks,
                'topic': {
                    'id': str(q.topic.id),
                    'name': q.topic.name
                },
                'section': {
                    'id': str(q.section.id),
                    'name': q.section.name,
                    'order': q.section.order
                } if q.section else None,
                'question_type': q.kcse_question_type,
                'difficulty': q.difficulty,
            })
        
        # Build mark distribution
        mark_distribution = defaultdict(int)
        for q in self.selected_questions:
            mark_distribution[str(q.marks)] += 1
        
        # Build topic distribution
        topic_distribution = defaultdict(int)
        for q in self.selected_questions:
            topic_distribution[str(q.topic.id)] += 1
        
        # Build question type distribution
        question_type_distribution = defaultdict(int)
        for q in self.selected_questions:
            qtype = q.kcse_question_type or 'Unknown'
            question_type_distribution[qtype] += 1
        
        # Calculate total marks
        total_marks = sum(q.marks for q in self.selected_questions)
        
        # Build validation report
        validation_report = {
            'all_passed': True,
            'checks': {
                'correct_question_count': len(self.selected_questions) == self.REQUIRED_QUESTIONS,
                'correct_total_marks': total_marks == self.TOTAL_MARKS,
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
                'all_questions': 'Answer ALL 25 questions'
            },
            'questions': questions_data,
            'question_ids': self.selected_question_ids,
            'all_questions': self.selected_questions,
            'mark_distribution': dict(mark_distribution),
            'topic_distribution': dict(topic_distribution),
            'question_type_distribution': dict(question_type_distribution),
            'validation_report': validation_report,
            'generation_time': generation_time,
            'statistics': {
                'total_questions': len(self.selected_questions),
                'total_marks': total_marks,
                'student_max_marks': total_marks,
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': validation_report['checks']
            }
        }


class KCSEBusinessPaper2Generator:
    """
    Business Studies Paper 2 Generator
    - 6 questions, each 20 marks (student answers 5 = 100 marks)
    - Each question has two parts totaling 20 marks:
      * Question Type 1: part (a) 12 marks + part (b) 8 marks = 20 marks
      * Question Type 2: part (a) 10 marks + part (b) 10 marks = 20 marks
    - Strategy: Prioritize (12+8) structure, use (10+10) when needed
    """
    
    REQUIRED_QUESTIONS = 6
    MARKS_PER_QUESTION = 20
    TOTAL_MARKS = REQUIRED_QUESTIONS * MARKS_PER_QUESTION  # 120 marks total
    STUDENT_ANSWERS = 5  # Choose 5 out of 6
    STUDENT_MAX_MARKS = STUDENT_ANSWERS * MARKS_PER_QUESTION  # 100 marks
    
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
        
        # Question pools by marks
        self.questions_12_marks = []  # For part a of (12+8) questions
        self.questions_8_marks = []   # For part b of (12+8) questions
        self.questions_10_marks = []  # For both parts of (10+10) questions
        
        # Selection tracking
        self.selected_questions = []  # List of combined questions
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
        
        # Separate questions by marks
        for q in self.all_questions:
            if q.marks == 12:
                self.questions_12_marks.append(q)
            elif q.marks == 8:
                self.questions_8_marks.append(q)
            elif q.marks == 10:
                self.questions_10_marks.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.questions_12_marks)
        random.shuffle(self.questions_8_marks)
        random.shuffle(self.questions_10_marks)
        
        print(f"\n[DATA LOADED - BUSINESS PAPER 2]")
        print(f"  Total topics: {len(self.topics)}")
        print(f"  Total questions: {len(self.all_questions)}")
        print(f"  12-mark questions: {len(self.questions_12_marks)} (for part a)")
        print(f"  8-mark questions: {len(self.questions_8_marks)} (for part b)")
        print(f"  10-mark questions: {len(self.questions_10_marks)} (for both parts)")
        print(f"  Question types: (12+8)=20 OR (10+10)=20")

    
    def _select_6_combined_questions(self) -> bool:
        """
        Select 6 combined questions, each totaling 20 marks:
        - Type 1: part (a) 12 marks + part (b) 8 marks = 20 marks
        - Type 2: part (a) 10 marks + part (b) 10 marks = 20 marks
        
        Strategy:
        1. Create as many (12+8) questions as possible (equal counts needed)
        2. Fill remaining with (10+10) questions (need even count of 10-marks)
        """
        combined_questions = []
        used_12_ids = set()
        used_8_ids = set()
        used_10_ids = set()
        
        # Step 1: Create (12mk + 8mk) questions
        # Need equal number of 12-mark and 8-mark questions for pairing
        available_12 = [q for q in self.questions_12_marks if q.id not in used_12_ids]
        available_8 = [q for q in self.questions_8_marks if q.id not in used_8_ids]
        
        questions_12_8 = min(len(available_12), len(available_8))
        
        for i in range(questions_12_8):
            q_12 = available_12[i]
            q_8 = available_8[i]
            
            combined_questions.append({
                'part_a': q_12,
                'part_b': q_8,
                'total_marks': q_12.marks + q_8.marks,
                'question_type': '12+8'
            })
            used_12_ids.add(q_12.id)
            used_8_ids.add(q_8.id)
        
        # Step 2: If we need more questions, use (10mk + 10mk)
        questions_needed = self.REQUIRED_QUESTIONS - len(combined_questions)
        
        if questions_needed > 0:
            available_10 = [q for q in self.questions_10_marks if q.id not in used_10_ids]
            # Need even number of 10-marks (2 per question)
            questions_10_10 = min(questions_needed, len(available_10) // 2)
            
            for i in range(questions_10_10):
                part_a = available_10[i * 2]
                part_b = available_10[i * 2 + 1]
                
                combined_questions.append({
                    'part_a': part_a,
                    'part_b': part_b,
                    'total_marks': part_a.marks + part_b.marks,
                    'question_type': '10+10'
                })
                used_10_ids.add(part_a.id)
                used_10_ids.add(part_b.id)
        
        # Check if we have exactly 6 questions
        if len(combined_questions) != self.REQUIRED_QUESTIONS:
            print(f"  [FAILED] Need {self.REQUIRED_QUESTIONS} questions, created {len(combined_questions)}")
            print(f"    Available: 12mk={len(available_12)}, 8mk={len(available_8)}, 10mk={len(self.questions_10_marks)}")
            return False
        
        self.selected_questions = combined_questions
        
        # Show question structure
        type_12_8 = sum(1 for q in combined_questions if q['question_type'] == '12+8')
        type_10_10 = sum(1 for q in combined_questions if q['question_type'] == '10+10')
        
        print(f"\n[6 COMBINED QUESTIONS SELECTED]")
        print(f"  Question types: (12+8)={type_12_8}, (10+10)={type_10_10}")
        for idx, cq in enumerate(combined_questions, start=1):
            print(f"  Question {idx} [{cq['question_type']}]:")
            print(f"    Part a ({cq['part_a'].marks} marks): Topic '{cq['part_a'].topic.name}'")
            print(f"    Part b ({cq['part_b'].marks} marks): Topic '{cq['part_b'].topic.name}'")
        
        return True
    
    def generate(self) -> Dict:
        """Generate Business Studies Paper 2"""
        max_attempts = 100
        self.generation_start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE BUSINESS STUDIES PAPER 2 GENERATION")
        print(f"{'='*70}")
        print(f"Requirements:")
        print(f"  Total Questions: {self.REQUIRED_QUESTIONS}")
        print(f"  Marks per Question: {self.MARKS_PER_QUESTION} [(12+8) OR (10+10)]")
        print(f"  Student Answers: {self.STUDENT_ANSWERS} out of {self.REQUIRED_QUESTIONS}")
        print(f"  Student Max Marks: {self.STUDENT_MAX_MARKS}")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_questions = []
            self.selected_question_ids = []
            
            # Select 6 combined questions
            if not self._select_6_combined_questions():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed to create 6 questions")
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
            f"Available: 12-mark={len(self.questions_12_marks)}, "
            f"8-mark={len(self.questions_8_marks)}, "
            f"10-mark={len(self.questions_10_marks)}"
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with paper structure"""
        
        # Build questions data
        questions_data = []
        
        for idx, combined_q in enumerate(self.selected_questions, start=1):
            q_a = combined_q['part_a']
            q_b = combined_q['part_b']
            
            # Add both question IDs
            self.selected_question_ids.append(str(q_a.id))
            self.selected_question_ids.append(str(q_b.id))
            
            questions_data.append({
                'question_number': idx,
                'total_marks': self.MARKS_PER_QUESTION,
                'is_compulsory': False,
                'instruction': f'Choose {self.STUDENT_ANSWERS} out of {self.REQUIRED_QUESTIONS} questions',
                'part_a': {
                    'id': str(q_a.id),
                    'part_label': 'a',
                    'marks': q_a.marks,
                    'question_text': q_a.question_text,
                    'answer_text': q_a.answer_text,
                    'topic': {
                        'id': str(q_a.topic.id),
                        'name': q_a.topic.name
                    },
                    'section': {
                        'id': str(q_a.section.id),
                        'name': q_a.section.name,
                        'order': q_a.section.order
                    } if q_a.section else None,
                    'question_type': q_a.kcse_question_type,
                    'difficulty': q_a.difficulty,
                },
                'part_b': {
                    'id': str(q_b.id),
                    'part_label': 'b',
                    'marks': q_b.marks,
                    'question_text': q_b.question_text,
                    'answer_text': q_b.answer_text,
                    'topic': {
                        'id': str(q_b.topic.id),
                        'name': q_b.topic.name
                    },
                    'section': {
                        'id': str(q_b.section.id),
                        'name': q_b.section.name,
                        'order': q_b.section.order
                    } if q_b.section else None,
                    'question_type': q_b.kcse_question_type,
                    'difficulty': q_b.difficulty,
                }
            })
        
        # Build mark distribution
        mark_distribution = {
            '12': self.REQUIRED_QUESTIONS,  # 6 questions with 12 marks each (part a)
            '8': self.REQUIRED_QUESTIONS,   # 6 questions with 8 marks each (part b)
            '20': self.REQUIRED_QUESTIONS   # 6 combined questions of 20 marks each
        }
        
        # Build topic distribution
        topic_distribution = defaultdict(int)
        for cq in self.selected_questions:
            topic_distribution[str(cq['part_a'].topic.id)] += 1
            topic_distribution[str(cq['part_b'].topic.id)] += 1
        
        # Build question type distribution
        question_type_distribution = defaultdict(int)
        for cq in self.selected_questions:
            qtype_a = cq['part_a'].kcse_question_type or 'Unknown'
            qtype_b = cq['part_b'].kcse_question_type or 'Unknown'
            question_type_distribution[qtype_a] += 1
            question_type_distribution[qtype_b] += 1
        
        # Build validation report
        validation_report = {
            'all_passed': True,
            'checks': {
                'correct_question_count': len(self.selected_questions) == self.REQUIRED_QUESTIONS,
                'all_questions_20_marks': all(cq['total_marks'] == 20 for cq in self.selected_questions),
                'different_topics_in_parts': all(
                    cq['part_a'].topic_id != cq['part_b'].topic_id 
                    for cq in self.selected_questions
                ),
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
                'main': f'Choose {self.STUDENT_ANSWERS} out of {self.REQUIRED_QUESTIONS} questions',
                'note': 'Each question has two parts (a and b) from different topics'
            },
            'questions': questions_data,
            'question_ids': self.selected_question_ids,
            'all_questions': self.selected_questions,
            'mark_distribution': dict(mark_distribution),
            'topic_distribution': dict(topic_distribution),
            'question_type_distribution': dict(question_type_distribution),
            'validation_report': validation_report,
            'generation_time': generation_time,
            'statistics': {
                'total_questions': len(self.selected_questions),
                'total_marks_available': self.TOTAL_MARKS,
                'student_answers': self.STUDENT_ANSWERS,
                'student_max_marks': self.STUDENT_MAX_MARKS,
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': validation_report['checks']
            }
        }


# Django Views

@require_http_methods(["POST"])
def validate_business_paper_pool(request):
    """Validate if there are enough questions to generate Business Studies paper"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('topic_ids', [])
        paper_number = None
        
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'can_generate': False,
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
        
        if paper_id :
            paper = Paper.objects.get(id=paper_id)
            paper_name = paper.name.lower()
            paper_number = extract_paper_number_from_name(paper_name)
        
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
        
        if paper_number == 1:
            # Count questions by marks
            count_4_marks = sum(1 for q in all_questions if q.marks == 4)
            count_3_marks = sum(1 for q in all_questions if q.marks == 3)
            count_5_marks = sum(1 for q in all_questions if q.marks == 5)
            
            # Need 25 questions totaling 100 marks
            # Ideal: 25 x 4-mark questions
            # Can mix 3-mark and 5-mark to reach 100 marks
            
            can_generate = count_4_marks >= 25 or (
                count_4_marks + count_3_marks + count_5_marks >= 25
            )
            
            issues = []
            if count_4_marks < 25:
                issues.append(
                    f"Ideal: 25 x 4-mark questions. Have {count_4_marks} 4-mark questions. "
                    f"Will attempt to mix with {count_3_marks} 3-mark and {count_5_marks} 5-mark questions."
                )
            
            message = "Ready to generate Business Studies Paper 1" if can_generate else "Insufficient questions: " + "; ".join(issues)
            
            return JsonResponse({
                'can_generate': can_generate,
                'available_counts': {
                    '4_mark_questions': count_4_marks,
                    '3_mark_questions': count_3_marks,
                    '5_mark_questions': count_5_marks,
                    'total_questions': len(all_questions),
                },
                'required_counts': {
                    'total_questions': 25,
                    'total_marks': 100,
                    'preferred': '25 x 4-mark questions'
                },
                'paper_structure': {
                    'questions': 25,
                    'marks': 100,
                    'compulsory': 'Answer ALL questions'
                },
                'message': message
            })
        
        else:  # Paper 2
            # Count questions by marks
            count_12_marks = sum(1 for q in all_questions if q.marks == 12)
            count_8_marks = sum(1 for q in all_questions if q.marks == 8)
            
            # Need 6 x 12-mark and 6 x 8-mark questions
            can_generate = count_12_marks >= 6 and count_8_marks >= 6
            
            issues = []
            if count_12_marks < 6:
                issues.append(f"Need 6 x 12-mark questions, have {count_12_marks}")
            if count_8_marks < 6:
                issues.append(f"Need 6 x 8-mark questions, have {count_8_marks}")
            
            message = "Ready to generate Business Studies Paper 2" if can_generate else "Insufficient questions: " + "; ".join(issues)
            
            return JsonResponse({
                'can_generate': can_generate,
                'available_counts': {
                    '12_mark_questions': count_12_marks,
                    '8_mark_questions': count_8_marks,
                    'total_questions': len(all_questions),
                },
                'required_counts': {
                    '12_mark_questions': 6,
                    '8_mark_questions': 6,
                },
                'paper_structure': {
                    'questions': 6,
                    'marks_per_question': 20,
                    'structure': 'Each question: Part a (12 marks) + Part b (8 marks) from different topics',
                    'student_answers': 'Choose 5 out of 6 questions'
                },
                'message': message
            })
        
    except Exception as e:
        return JsonResponse({
            'can_generate': False,
            'message': f'Validation error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def generate_business_paper(request):
    """Generate KCSE Business Studies Paper 1 or 2"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('topic_ids', [])
        paper_number = None
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
        
        if paper_id :
            paper = Paper.objects.get(id=paper_id)
            paper_name = paper.name.lower()
            paper_number = extract_paper_number_from_name(paper_name)
        
        if paper_number not in [1, 2]:
            return JsonResponse({
                'message': f'Invalid paper_number {paper_number}. Must be 1 or 2.'
            }, status=400)
        
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Generate unique code
        timestamp = datetime.now().strftime('%y%m%d%H%M%S')
        unique_code = f"BUS{paper_number}-{timestamp}"
        
        # Initialize appropriate generator
        if paper_number == 1:
            generator = KCSEBusinessPaper1Generator(
                paper_id=paper_id,
                selected_topic_ids=selected_topic_ids,
                user=user
            )
        else:  # paper_number == 2
            generator = KCSEBusinessPaper2Generator(
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
            'total_questions': result['statistics']['total_questions'],
            'status': generated_paper.status,
            'paper_id': str(generator.paper.id),
            'paper_number': paper_number,
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
