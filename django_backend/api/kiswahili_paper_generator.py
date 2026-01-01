"""
KCSE Kiswahili Paper 1 & 2 Generator

PAPER 1:
- Question 1: COMPULSORY (from is_step=True topics)
- Questions 2-4: Student selects ONE from these three (from different topics)
- Total: 4 questions structured

PAPER 2:
- Section 1: Ufhamu (15 marks)
- Section 2: Ufupisho (15 marks)
- Section 3: Matumizi ya Lugha (40 marks)
- Section 4: Isimu Jamii (10 marks)
- Total: 80 marks
"""

import random
import re
import time
from collections import defaultdict
from typing import List, Dict, Optional
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Paper, Topic, Question, Subject, GeneratedPaper


class KCSEKiswahiliPaper1Generator:
    """
    Kiswahili Paper 1 Generator
    - Question 1: Compulsory (from is_step=True topics)
    - Questions 2-4: Choose ONE from three (different topics)
    """
    
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
        
        # Question pools
        self.is_step_topics = []  # Topics with is_step=True
        self.regular_topics = []  # Topics with is_step=False
        self.is_step_questions = []  # Questions from is_step topics
        self.regular_questions = []  # Questions from regular topics
        
        # Selection tracking
        self.selected_question_1 = None  # Compulsory question
        self.selected_questions_2_4 = []  # Optional questions (choose 1 from 3)
        self.selected_question_ids = []
        self.used_topic_ids = set()
        
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
        
        # Separate topics by is_step field
        for topic in self.topics:
            is_step = getattr(topic, 'is_step', False)
            if is_step:
                self.is_step_topics.append(topic)
            else:
                self.regular_topics.append(topic)
        
        if not self.is_step_topics:
            raise ValueError("No is_step topics found. At least one topic with is_step=True is required for Question 1.")
        
        # Load ALL questions for selected topics
        self.all_questions = list(Question.objects.filter(
            subject=self.subject,
            paper=self.paper,
            topic__in=self.topics,
            is_active=True
        ).select_related('topic', 'section'))
        
        if not self.all_questions:
            raise ValueError("No questions found for selected topics")
        
        # Separate questions by topic type
        is_step_topic_ids = {topic.id for topic in self.is_step_topics}
        for q in self.all_questions:
            if q.topic_id in is_step_topic_ids:
                self.is_step_questions.append(q)
            else:
                self.regular_questions.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.is_step_topics)
        random.shuffle(self.is_step_questions)
        random.shuffle(self.regular_topics)
        random.shuffle(self.regular_questions)
        
        print(f"\n[DATA LOADED - KISWAHILI PAPER 1]")
        print(f"  is_step topics: {len(self.is_step_topics)}")
        print(f"  Regular topics: {len(self.regular_topics)}")
        print(f"  is_step questions: {len(self.is_step_questions)}")
        print(f"  Regular questions: {len(self.regular_questions)}")
        print(f"  Total topics: {len(self.topics)}")
        print(f"  Total questions: {len(self.all_questions)}")
    
    def _select_question_1(self) -> bool:
        """
        Select Question 1 (Compulsory)
        Must be from a topic where is_step=True
        If multiple is_step topics exist, randomly pick one topic then pick one question from it
        """
        if not self.is_step_topics:
            print(f"  Question 1 FAILED: No is_step topics available")
            return False
        
        # Randomly select one is_step topic
        selected_topic = random.choice(self.is_step_topics)
        
        # Get questions from this topic
        topic_questions = [q for q in self.is_step_questions if q.topic_id == selected_topic.id]
        
        if not topic_questions:
            print(f"  Question 1 FAILED: No questions in selected is_step topic '{selected_topic.name}'")
            return False
        
        # Randomly select one question from this topic
        self.selected_question_1 = random.choice(topic_questions)
        self.used_topic_ids.add(selected_topic.id)
        
        print(f"\n[QUESTION 1 SELECTED - COMPULSORY]")
        print(f"  Topic: {selected_topic.name} (is_step=True)")
        print(f"  Question ID: {self.selected_question_1.id}")
        print(f"  Marks: {self.selected_question_1.marks}")
        
        return True
    
    def _select_questions_2_4(self) -> bool:
        """
        Select Questions 2-4 (Choose ONE from three)
        Each question must be from a different topic
        Must not be from the same topic as Question 1
        """
        # Get all questions excluding the topic used in Question 1
        available_questions = [
            q for q in self.all_questions 
            if q.topic_id not in self.used_topic_ids
        ]
        
        if len(available_questions) < 3:
            print(f"  Questions 2-4 FAILED: Need 3 questions from different topics, have {len(available_questions)}")
            return False
        
        # Try to select 3 questions from different topics
        selected = []
        used_topics_for_2_4 = set()
        
        for q in available_questions:
            if q.topic_id not in used_topics_for_2_4:
                selected.append(q)
                used_topics_for_2_4.add(q.topic_id)
                
                if len(selected) == 3:
                    break
        
        if len(selected) < 3:
            print(f"  Questions 2-4 FAILED: Could only select {len(selected)} questions from different topics")
            return False
        
        self.selected_questions_2_4 = selected
        
        print(f"\n[QUESTIONS 2-4 SELECTED - CHOOSE ONE]")
        for idx, q in enumerate(selected, start=2):
            print(f"  Question {idx}: Topic='{q.topic.name}', Marks={q.marks}")
        
        return True
    
    def generate(self) -> Dict:
        """Generate Kiswahili Paper 1"""
        max_attempts = 100
        self.generation_start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE KISWAHILI PAPER 1 GENERATION")
        print(f"{'='*70}")
        print(f"Structure:")
        print(f"  Question 1: COMPULSORY (from is_step=True topics)")
        print(f"  Questions 2-4: Choose ONE from three (different topics)")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_question_1 = None
            self.selected_questions_2_4 = []
            self.selected_question_ids = []
            self.used_topic_ids = set()
            
            # Select Question 1 (Compulsory from is_step topics)
            if not self._select_question_1():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Question 1 selection")
                continue
            
            # Select Questions 2-4 (Choose ONE from three)
            if not self._select_questions_2_4():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Questions 2-4 selection")
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
            f"Available: is_step questions={len(self.is_step_questions)}, "
            f"regular questions={len(self.regular_questions)}"
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with paper structure"""
        
        # Combine all questions: Question 1 + Questions 2-4
        all_questions = [self.selected_question_1] + self.selected_questions_2_4
        
        # Build questions data
        questions_data = []
        
        # Question 1 - Compulsory
        q1 = self.selected_question_1
        self.selected_question_ids.append(str(q1.id))
        questions_data.append({
            'id': str(q1.id),
            'question_number': 1,
            'is_compulsory': True,
            'instruction': 'Compulsory - Answer this question',
            'question_text': q1.question_text,
            'answer_text': q1.answer_text,
            'marks': q1.marks,
            'topic': {
                'id': str(q1.topic.id),
                'name': q1.topic.name,
                'is_step': getattr(q1.topic, 'is_step', False)
            },
            'section': {
                'id': str(q1.section.id),
                'name': q1.section.name,
                'order': q1.section.order
            } if q1.section else None,
            'question_type': q1.kcse_question_type,
            'difficulty': q1.difficulty,
        })
        
        # Questions 2-4 - Choose ONE
        for idx, q in enumerate(self.selected_questions_2_4, start=2):
            self.selected_question_ids.append(str(q.id))
            questions_data.append({
                'id': str(q.id),
                'question_number': idx,
                'is_compulsory': False,
                'instruction': 'Choose ONE from Questions 2, 3, and 4',
                'question_text': q.question_text,
                'answer_text': q.answer_text,
                'marks': q.marks,
                'topic': {
                    'id': str(q.topic.id),
                    'name': q.topic.name,
                    'is_step': getattr(q.topic, 'is_step', False)
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
        
        # Calculate total marks (student answers Q1 + ONE from Q2-4)
        q1_marks = self.selected_question_1.marks
        optional_marks = max(q.marks for q in self.selected_questions_2_4)
        student_max_marks = q1_marks + optional_marks
        
        # Build validation report
        validation_report = {
            'all_passed': True,
            'checks': {
                'question_1_from_is_step': True,
                'questions_2_4_from_different_topics': len(set(q.topic_id for q in self.selected_questions_2_4)) == 3,
                'no_topic_reuse': self.selected_question_1.topic_id not in {q.topic_id for q in self.selected_questions_2_4},
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
                'question_1': 'Answer Question 1 (Compulsory)',
                'questions_2_4': 'Choose ONE question from Questions 2, 3, and 4'
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
                'total_questions_available': len(all_questions),
                'student_answers': 2,  # Q1 + ONE from Q2-4
                'student_max_marks': student_max_marks,
                'question_1': {
                    'compulsory': True,
                    'marks': q1_marks,
                    'from_is_step_topic': True
                },
                'questions_2_4': {
                    'choose_one_from': 3,
                    'marks_options': [q.marks for q in self.selected_questions_2_4],
                    'max_marks': optional_marks
                },
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': validation_report['checks']
            }
        }


class KCSEKiswahiliPaper2Generator:
    """
    Kiswahili Paper 2 Generator
    Four sections based on topic boolean fields:
    1. Ufhamu (Reading Comprehension) - from topics with is_comprehension=True
    2. Ufupisho (Summary) - from topics with is_summary=True
    3. Matumizi ya Lugha (Language Use) - from topics with is_lugha=True
    4. Isimu Jamii (Social Linguistics) - from topics with is_isimu=True
    Total: 80 marks (15 + 15 + 40 + 10)
    """
    
    # Section requirements
    SECTION_UFHAMU_MARKS = 15
    SECTION_UFUPISHO_MARKS = 15
    SECTION_MATUMIZI_MARKS = 40
    SECTION_ISIMU_JAMII_MARKS = 10
    PAPER_TOTAL_MARKS = 80
    
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
        
        # Topics by category (based on boolean fields)
        self.comprehension_topics = []  # is_comprehension=True
        self.summary_topics = []  # is_summary=True
        self.lugha_topics = []  # is_lugha=True
        self.isimu_topics = []  # is_isimu=True
        
        # Question pools by section
        self.ufhamu_questions = []
        self.ufupisho_questions = []
        self.matumizi_questions = []
        self.isimu_jamii_questions = []
        
        # Selection tracking
        self.selected_ufhamu = None
        self.selected_ufupisho = None
        self.selected_matumizi = None
        self.selected_isimu_jamii = None
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
        
        # Separate topics by boolean fields
        for topic in self.topics:
            if getattr(topic, 'is_comprehension', False):
                self.comprehension_topics.append(topic)
            if getattr(topic, 'is_summary', False):
                self.summary_topics.append(topic)
            if getattr(topic, 'is_lugha', False):
                self.lugha_topics.append(topic)
            if getattr(topic, 'is_isimu', False):
                self.isimu_topics.append(topic)
        
        # Load ALL questions for selected topics
        self.all_questions = list(Question.objects.filter(
            subject=self.subject,
            paper=self.paper,
            topic__in=self.topics,
            is_active=True
        ).select_related('topic', 'section'))
        
        if not self.all_questions:
            raise ValueError("No questions found for selected topics")
        
        # Separate questions by topic category
        comprehension_topic_ids = {t.id for t in self.comprehension_topics}
        summary_topic_ids = {t.id for t in self.summary_topics}
        lugha_topic_ids = {t.id for t in self.lugha_topics}
        isimu_topic_ids = {t.id for t in self.isimu_topics}
        
        for q in self.all_questions:
            if q.topic_id in comprehension_topic_ids:
                self.ufhamu_questions.append(q)
            if q.topic_id in summary_topic_ids:
                self.ufupisho_questions.append(q)
            if q.topic_id in lugha_topic_ids:
                self.matumizi_questions.append(q)
            if q.topic_id in isimu_topic_ids:
                self.isimu_jamii_questions.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.ufhamu_questions)
        random.shuffle(self.ufupisho_questions)
        random.shuffle(self.matumizi_questions)
        random.shuffle(self.isimu_jamii_questions)
        
        print(f"\n[DATA LOADED - KISWAHILI PAPER 2]")
        print(f"  Topics by category:")
        print(f"    is_comprehension=True: {len(self.comprehension_topics)} topics")
        print(f"    is_summary=True: {len(self.summary_topics)} topics")
        print(f"    is_lugha=True: {len(self.lugha_topics)} topics")
        print(f"    is_isimu=True: {len(self.isimu_topics)} topics")
        print(f"  Questions by section:")
        print(f"    Ufhamu: {len(self.ufhamu_questions)} questions")
        print(f"    Ufupisho: {len(self.ufupisho_questions)} questions")
        print(f"    Matumizi ya Lugha: {len(self.matumizi_questions)} questions")
        print(f"    Isimu Jamii: {len(self.isimu_jamii_questions)} questions")
        
        # Check if we have enough questions
        if not self.comprehension_topics:
            raise ValueError("No topics with is_comprehension=True found")
        if not self.ufhamu_questions:
            raise ValueError("No questions found in is_comprehension topics")
        
        if not self.summary_topics:
            raise ValueError("No topics with is_summary=True found")
        if not self.ufupisho_questions:
            raise ValueError("No questions found in is_summary topics")
        
        if not self.lugha_topics:
            raise ValueError("No topics with is_lugha=True found")
        if not self.matumizi_questions:
            raise ValueError("No questions found in is_lugha topics")
        
        if not self.isimu_topics:
            raise ValueError("No topics with is_isimu=True found")
        if not self.isimu_jamii_questions:
            raise ValueError("No questions found in is_isimu topics")
    
    def _select_sections(self) -> bool:
        """Select one question from each section based on topic boolean fields"""
        
        # Section 1: Ufhamu - from topics with is_comprehension=True
        if not self.ufhamu_questions:
            print(f"  Section 1 (Ufhamu) FAILED: No questions from is_comprehension topics")
            return False
        self.selected_ufhamu = random.choice(self.ufhamu_questions)
        
        # Section 2: Ufupisho - from topics with is_summary=True
        if not self.ufupisho_questions:
            print(f"  Section 2 (Ufupisho) FAILED: No questions from is_summary topics")
            return False
        self.selected_ufupisho = random.choice(self.ufupisho_questions)
        
        # Section 3: Matumizi ya Lugha - from topics with is_lugha=True
        if not self.matumizi_questions:
            print(f"  Section 3 (Matumizi) FAILED: No questions from is_lugha topics")
            return False
        self.selected_matumizi = random.choice(self.matumizi_questions)
        
        # Section 4: Isimu Jamii - from topics with is_isimu=True
        if not self.isimu_jamii_questions:
            print(f"  Section 4 (Isimu Jamii) FAILED: No questions from is_isimu topics")
            return False
        self.selected_isimu_jamii = random.choice(self.isimu_jamii_questions)
        
        print(f"\n[ALL SECTIONS SELECTED]")
        print(f"  Section 1 - Ufhamu: {self.selected_ufhamu.marks} marks (from is_comprehension topic)")
        print(f"  Section 2 - Ufupisho: {self.selected_ufupisho.marks} marks (from is_summary topic)")
        print(f"  Section 3 - Matumizi ya Lugha: {self.selected_matumizi.marks} marks (from is_lugha topic)")
        print(f"  Section 4 - Isimu Jamii: {self.selected_isimu_jamii.marks} marks (from is_isimu topic)")
        print(f"  Total: {self.selected_ufhamu.marks + self.selected_ufupisho.marks + self.selected_matumizi.marks + self.selected_isimu_jamii.marks} marks")
        
        return True
    
    def generate(self) -> Dict:
        """Generate Kiswahili Paper 2"""
        max_attempts = 10
        self.generation_start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE KISWAHILI PAPER 2 GENERATION")
        print(f"{'='*70}")
        print(f"Structure:")
        print(f"  Section 1: Ufhamu - 15 marks")
        print(f"  Section 2: Ufupisho - 15 marks")
        print(f"  Section 3: Matumizi ya Lugha - 40 marks")
        print(f"  Section 4: Isimu Jamii - 10 marks")
        print(f"  Total: 80 marks")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_ufhamu = None
            self.selected_ufupisho = None
            self.selected_matumizi = None
            self.selected_isimu_jamii = None
            self.selected_question_ids = []
            
            # Select all sections
            if not self._select_sections():
                if attempt % 5 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at section selection")
                continue
            
            # Success!
            generation_time = time.time() - self.generation_start_time
            
            # Verify total marks
            total_marks = (self.selected_ufhamu.marks + self.selected_ufupisho.marks + 
                          self.selected_matumizi.marks + self.selected_isimu_jamii.marks)
            
            if total_marks != self.PAPER_TOTAL_MARKS:
                print(f"[ATTEMPT {attempt}] Mark total mismatch: {total_marks} != {self.PAPER_TOTAL_MARKS}")
                continue
            
            print(f"\n{'='*70}")
            print(f"SUCCESS! Generated in {attempt} attempts ({generation_time:.2f}s)")
            print(f"{'='*70}")
            
            return self._build_result(generation_time)
        
        # Failed
        raise Exception(
            f"Failed to generate paper after {max_attempts} attempts. "
            f"Available: Ufhamu={len(self.ufhamu_questions)}, "
            f"Ufupisho={len(self.ufupisho_questions)}, "
            f"Matumizi={len(self.matumizi_questions)}, "
            f"Isimu Jamii={len(self.isimu_jamii_questions)}"
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with paper structure"""
        
        # Collect all selected questions
        all_questions = [
            self.selected_ufhamu,
            self.selected_ufupisho,
            self.selected_matumizi,
            self.selected_isimu_jamii
        ]
        
        # Build questions data
        questions_data = []
        section_names = ['Ufhamu', 'Ufupisho', 'Matumizi ya Lugha', 'Isimu Jamii']
        
        for idx, (q, section_name) in enumerate(zip(all_questions, section_names), start=1):
            self.selected_question_ids.append(str(q.id))
            questions_data.append({
                'id': str(q.id),
                'question_number': idx,
                'section_name': section_name,
                'is_compulsory': True,
                'instruction': 'Compulsory',
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
        
        # Calculate total marks
        total_marks = sum(q.marks for q in all_questions)
        
        # Build validation report
        validation_report = {
            'all_passed': True,
            'checks': {
                'ufhamu_marks': self.selected_ufhamu.marks == self.SECTION_UFHAMU_MARKS,
                'ufupisho_marks': self.selected_ufupisho.marks == self.SECTION_UFUPISHO_MARKS,
                'matumizi_marks': self.selected_matumizi.marks == self.SECTION_MATUMIZI_MARKS,
                'isimu_jamii_marks': self.selected_isimu_jamii.marks == self.SECTION_ISIMU_JAMII_MARKS,
                'total_marks': total_marks == self.PAPER_TOTAL_MARKS,
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
                'all_sections': 'Answer ALL sections'
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
                'paper_total_marks': total_marks,
                'student_max_marks': total_marks,
                'sections': {
                    'ufhamu': {
                        'marks': self.selected_ufhamu.marks,
                        'compulsory': True
                    },
                    'ufupisho': {
                        'marks': self.selected_ufupisho.marks,
                        'compulsory': True
                    },
                    'matumizi_ya_lugha': {
                        'marks': self.selected_matumizi.marks,
                        'compulsory': True
                    },
                    'isimu_jamii': {
                        'marks': self.selected_isimu_jamii.marks,
                        'compulsory': True
                    }
                },
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': validation_report['checks']
            }
        }


# Django Views

@require_http_methods(["POST"])
def validate_kiswahili_paper_pool(request):
    """Validate if there are enough questions to generate Kiswahili paper"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('topic_ids', [])
        # paper_number = data.get('paper_number', 1)  # 1 or 2
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'can_generate': False,
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
            
        # get paper name from  db
        paper_name = Paper.objects.filter(id=paper_id).values_list('name', flat=True).first()
        
        # check for text to determine if it's paper 1 or 2 
        # for paper one has "kwanza" in the name, paper two has "pili" , paper three has "tatu"
        if paper_name and 'pili' in paper_name.lower():
            paper_number = 2
        elif paper_name and 'tatu' in paper_name.lower():
            paper_number = 3
        elif paper_name and 'kwanza' in paper_name.lower():
            paper_number = 1
        
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
            # Count is_step topics and questions
            is_step_topic_count = sum(1 for t in topics if getattr(t, 'is_step', False))
            is_step_topic_ids = {t.id for t in topics if getattr(t, 'is_step', False)}
            is_step_question_count = sum(1 for q in all_questions if q.topic_id in is_step_topic_ids)
            regular_question_count = len(all_questions) - is_step_question_count
            
            # Need: 1+ is_step questions, 3+ regular questions from different topics
            can_generate = (is_step_topic_count >= 1 and 
                           is_step_question_count >= 1 and 
                           regular_question_count >= 3)
            
            issues = []
            if is_step_topic_count < 1:
                issues.append(f"Need at least 1 is_step topic, have {is_step_topic_count}")
            if is_step_question_count < 1:
                issues.append(f"Need at least 1 question from is_step topics, have {is_step_question_count}")
            if regular_question_count < 3:
                issues.append(f"Need at least 3 questions from other topics, have {regular_question_count}")
            
            message = "Ready to generate Kiswahili Paper 1" if can_generate else "Insufficient questions: " + "; ".join(issues)
            
            return JsonResponse({
                'can_generate': can_generate,
                'available_counts': {
                    'is_step_topics': is_step_topic_count,
                    'is_step_questions': is_step_question_count,
                    'regular_questions': regular_question_count,
                    'total_questions': len(all_questions),
                },
                'required_counts': {
                    'is_step_questions': 1,
                    'regular_questions': 3,
                },
                'paper_structure': {
                    'question_1': 'Compulsory (from is_step topics)',
                    'questions_2_4': 'Choose ONE from three (different topics)',
                },
                'message': message
            })
        
        else:  # Paper 2
            # Categorize topics by boolean fields
            comprehension_topics = [t for t in topics if getattr(t, 'is_comprehension', False)]
            summary_topics = [t for t in topics if getattr(t, 'is_summary', False)]
            lugha_topics = [t for t in topics if getattr(t, 'is_lugha', False)]
            isimu_topics = [t for t in topics if getattr(t, 'is_isimu', False)]
            
            comprehension_topic_ids = {t.id for t in comprehension_topics}
            summary_topic_ids = {t.id for t in summary_topics}
            lugha_topic_ids = {t.id for t in lugha_topics}
            isimu_topic_ids = {t.id for t in isimu_topics}
            
            # Count questions by topic category
            ufhamu_count = sum(1 for q in all_questions if q.topic_id in comprehension_topic_ids)
            ufupisho_count = sum(1 for q in all_questions if q.topic_id in summary_topic_ids)
            matumizi_count = sum(1 for q in all_questions if q.topic_id in lugha_topic_ids)
            isimu_jamii_count = sum(1 for q in all_questions if q.topic_id in isimu_topic_ids)
            
            # Need: 1+ of each section type
            can_generate = (ufhamu_count >= 1 and 
                           ufupisho_count >= 1 and 
                           matumizi_count >= 1 and 
                           isimu_jamii_count >= 1)
            
            issues = []
            if not comprehension_topics:
                issues.append(f"Need topics with is_comprehension=True")
            elif ufhamu_count < 1:
                issues.append(f"Need 1 Ufhamu question from is_comprehension topics, have {ufhamu_count}")
            
            if not summary_topics:
                issues.append(f"Need topics with is_summary=True")
            elif ufupisho_count < 1:
                issues.append(f"Need 1 Ufupisho question from is_summary topics, have {ufupisho_count}")
            
            if not lugha_topics:
                issues.append(f"Need topics with is_lugha=True")
            elif matumizi_count < 1:
                issues.append(f"Need 1 Matumizi ya Lugha question from is_lugha topics, have {matumizi_count}")
            
            if not isimu_topics:
                issues.append(f"Need topics with is_isimu=True")
            elif isimu_jamii_count < 1:
                issues.append(f"Need 1 Isimu Jamii question from is_isimu topics, have {isimu_jamii_count}")
            
            message = "Ready to generate Kiswahili Paper 2" if can_generate else "Insufficient questions: " + "; ".join(issues)
            
            return JsonResponse({
                'can_generate': can_generate,
                'available_counts': {
                    'comprehension_topics': len(comprehension_topics),
                    'ufhamu_questions': ufhamu_count,
                    'summary_topics': len(summary_topics),
                    'ufupisho_questions': ufupisho_count,
                    'lugha_topics': len(lugha_topics),
                    'matumizi_questions': matumizi_count,
                    'isimu_topics': len(isimu_topics),
                    'isimu_jamii_questions': isimu_jamii_count,
                },
                'required_counts': {
                    'ufhamu': 1,
                    'ufupisho': 1,
                    'matumizi': 1,
                    'isimu_jamii': 1,
                },
                'paper_structure': {
                    'section_1': 'Ufhamu (from is_comprehension topics)',
                    'section_2': 'Ufupisho (from is_summary topics)',
                    'section_3': 'Matumizi ya Lugha (from is_lugha topics)',
                    'section_4': 'Isimu Jamii (from is_isimu topics)',
                    'total': '80 marks'
                },
                'message': message
            })
        
    except Exception as e:
        return JsonResponse({
            'can_generate': False,
            'message': f'Validation error: {str(e)}'
        }, status=500)


def extract_paper_number_from_name(paper_name: str) -> int:
    """Extract paper number from paper name"""
    paper_name_upper = paper_name.upper()

    # Check for "PAPER II" first (most specific)
    if re.search(r'PAPER\s+II\b', paper_name_upper):
        return 2
    # Check for standalone "II" (most specific)
    if re.search(r'\bII\b', paper_name_upper):
        return 2
    
    # Check for "PAPER I" (but not "PAPER II")
    if re.search(r'PAPER\s+I\b', paper_name_upper):
        return 1
    
    # Check for standalone "I" (but NOT part of "II")
    if re.search(r'\bI\b(?!I)', paper_name_upper):
        return 1
    
    # Check for numeric "2"
    if re.search(r'\b2\b', paper_name_upper):
        return 2
    
    # Check for numeric "1"
    if re.search(r'\b1\b', paper_name_upper):
        return 1
    
    raise ValueError(f"Could not extract paper number from '{paper_name}'")


@require_http_methods(["POST"])
def generate_kiswahili_paper(request):
    """Generate KCSE Kiswahili Paper 1 or 2"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('topic_ids', [])
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
        
        # Retrieve paper name to determine paper number
        paper_name = Paper.objects.get(id=paper_id).name
        
        if paper_name and 'kwanza' in paper_name.lower():
            paper_number = 1
        elif paper_name and 'pili' in paper_name.lower():
            paper_number = 2
        elif paper_name and 'tatu' in paper_name.lower():
            paper_number = 3
        
        if paper_number not in [1, 2, 3]:
            return JsonResponse({
                'message': f'Invalid paper_number {paper_number}. Must be 1, 2, or 3. paper_name: {paper_name}'
            }, status=400)
        
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Generate unique code
        timestamp = datetime.now().strftime('%y%m%d%H%M%S')
        unique_code = f"KIS{paper_number}-{timestamp}"
        
        # Initialize appropriate generator
        if paper_number == 1:
            generator = KCSEKiswahiliPaper1Generator(
                paper_id=paper_id,
                selected_topic_ids=selected_topic_ids,
                user=user
            )
        else:
            generator = KCSEKiswahiliPaper2Generator(
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
            total_questions=result['statistics'].get('total_questions_available', result['statistics'].get('total_questions')),
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
            'total_questions': result['statistics'].get('total_questions_available', result['statistics'].get('total_questions')),
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
