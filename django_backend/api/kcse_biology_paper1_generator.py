"""
KCSE Biology Paper 1 Generator
Dynamic Algorithm with Flexible Question Count

REQUIREMENTS:
- Total marks: EXACTLY 80
- Nested questions: 10-18 questions (flexible), ~60 marks (55-65 range)
  * All nested questions have equal chance of selection
  * Count marks as we select to stay within target
- Standalone questions: Fill remaining marks to reach exactly 80
  * Priority: 2-mark and 3-mark questions
  * Use 1-mark only when needed to fill exact remaining marks
- Total questions: Flexible (typically 20-27 questions)
"""

import random
import time
from collections import defaultdict
from typing import List, Dict, Optional

from .models import Paper, Topic, Question, Subject


class KCSEBiologyPaper1Generator:
    """
    KCSE Biology Paper 1 Generator
    Dynamic algorithm: 10-18 nested (~60 marks) + standalone (fill to 80) = exactly 80 marks
    Question count is flexible (typically 20-27)
    """
    
    # Constants
    TOTAL_MARKS = 80
    MIN_NESTED_QUESTIONS = 10
    MAX_NESTED_QUESTIONS = 18
    TARGET_NESTED_MARKS = 60
    MIN_NESTED_MARKS = 55
    MAX_NESTED_MARKS = 65
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str]):
        """
        Initialize generator
        
        Args:
            paper_id: UUID of Biology Paper 1
            selected_topic_ids: List of topic UUIDs
        """
        self.paper_id = paper_id
        self.selected_topic_ids = selected_topic_ids
        
        # Data storage
        self.paper = None
        self.subject = None
        self.topics = []
        self.all_questions = []
        self.nested_questions = []
        self.standalone_1mark = []
        self.standalone_2mark = []
        self.standalone_3mark = []
        
        # Selection tracking
        self.selected_questions = []
        self.selected_question_ids = []  # List of IDs for paper generation
        self.used_ids = set()
        
        # Statistics
        self.nested_count = 0
        self.nested_marks = 0
        self.standalone_count = 0
        self.standalone_marks = 0
        self.total_marks = 0
        self.attempts = 0
    
    def load_data(self):
        """Load all questions from database for selected topics in Biology subject"""
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
        
        # Load ALL questions from Biology subject for selected topics
        self.all_questions = list(Question.objects.filter(
            subject=self.subject,
            paper=self.paper,
            topic__in=self.topics,
            is_active=True
        ).select_related('topic', 'section'))
        
        if not self.all_questions:
            raise ValueError("No questions found for selected topics")
        
        # Separate nested and standalone questions
        for q in self.all_questions:
            if q.is_nested:
                self.nested_questions.append(q)
            else:
                if q.marks == 1:
                    self.standalone_1mark.append(q)
                elif q.marks == 2:
                    self.standalone_2mark.append(q)
                elif q.marks == 3:
                    self.standalone_3mark.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.nested_questions)
        random.shuffle(self.standalone_1mark)
        random.shuffle(self.standalone_2mark)
        random.shuffle(self.standalone_3mark)
        
        print(f"\n[DATA LOADED]")
        print(f"  Nested questions: {len(self.nested_questions)}")
        print(f"  1-mark standalone: {len(self.standalone_1mark)}")
        print(f"  2-mark standalone: {len(self.standalone_2mark)}")
        print(f"  3-mark standalone: {len(self.standalone_3mark)}")
        
        # Validation
        if len(self.nested_questions) < self.MIN_NESTED_QUESTIONS:
            raise ValueError(f"Need at least {self.MIN_NESTED_QUESTIONS} nested questions, found {len(self.nested_questions)}")
    
    def _select_nested_questions(self) -> bool:
        """
        Select nested questions dynamically based on marks.
        Target: ~52 marks, aiming for close to 16 questions (but flexible: 10-18 range).
        All questions have equal chance of selection (shuffled).
        
        Returns:
            bool: True if successful (10-18 questions, 47-58 marks)
        """
        available = [q for q in self.nested_questions if q.id not in self.used_ids]
        
        if len(available) < 10:  # Need minimum 10 nested questions
            return False
        
        # Shuffle to give all questions equal chance
        random.shuffle(available)
        
        selected = []
        total_marks = 0
        target_marks = 52
        
        # Select questions one by one, counting marks as we go
        for question in available:
            current_count = len(selected)
            
            # Stop conditions:
            # 1. If we have 10+ questions and adding this would exceed 58 marks
            if current_count >= 10 and (total_marks + question.marks) > 58:
                break
            
            # 2. If we have 18 questions (maximum)
            if current_count >= 18:
                break
            
            # Add the question
            selected.append(question)
            total_marks += question.marks
            
            # 3. If we're in the sweet spot: 10-18 questions and 47-58 marks
            if current_count >= 10 and 47 <= total_marks <= 58:
                # We're good! Can stop here or continue if we're far from 16
                if current_count >= 14:  # Close enough to 16
                    break
        
        # Final validation: must have 10-18 questions and 47-58 marks
        question_count = len(selected)
        if not (10 <= question_count <= 18 and 47 <= total_marks <= 58):
            return False
        
        # Accept selection
        self.selected_questions.extend(selected)
        for q in selected:
            self.used_ids.add(q.id)
            self.selected_question_ids.append(str(q.id))
        
        self.nested_count = len(selected)
        self.nested_marks = total_marks
        self.total_marks = total_marks
        
        print(f"\n[NESTED SELECTION]")
        print(f"  Selected: {self.nested_count} questions (target: ~16)")
        print(f"  Total marks: {self.nested_marks} (target: ~52)")
        
        return True
    
    def _select_standalone_questions(self) -> bool:
        """
        Fill remaining marks with standalone questions to reach exactly 80 marks
        Priority: 2-mark and 3-mark questions
        Use 1-mark only when exactly 1 mark is needed
        
        Returns:
            bool: True if exactly 80 marks achieved
        """
        remaining_marks = self.TOTAL_MARKS - self.total_marks
        
        print(f"\n[STANDALONE SELECTION]")
        print(f"  Need: {remaining_marks} marks (flexible question count)")
        
        if remaining_marks <= 0:
            return self.total_marks == self.TOTAL_MARKS
        
        selected = []
        current_marks = 0
        max_questions = 15  # Safety limit to prevent infinite loops
        
        # Strategy: Use combination of 2-mark and 3-mark to get close
        # Then use 1-mark to fill exact remaining marks
        
        available_2mark = [q for q in self.standalone_2mark if q.id not in self.used_ids]
        available_3mark = [q for q in self.standalone_3mark if q.id not in self.used_ids]
        available_1mark = [q for q in self.standalone_1mark if q.id not in self.used_ids]
        
        # Shuffle for randomness
        random.shuffle(available_2mark)
        random.shuffle(available_3mark)
        random.shuffle(available_1mark)
        
        # Fill marks until we reach exactly the target
        while current_marks < remaining_marks and len(selected) < max_questions:
            marks_left = remaining_marks - current_marks
            
            # If exactly 1 mark left, use 1-mark question
            if marks_left == 1:
                if available_1mark:
                    q = available_1mark.pop(0)
                    selected.append(q)
                    current_marks += 1
                    break
                else:
                    return False  # Need 1-mark but none available
            
            # If exactly 2 marks left, use 2-mark question
            if marks_left == 2:
                if available_2mark:
                    q = available_2mark.pop(0)
                    selected.append(q)
                    current_marks += 2
                    break
                else:
                    return False
            
            # If 3+ marks left, prefer 2-mark or 3-mark
            # Use 3-mark if marks_left is odd or if we have many marks to fill
            if marks_left >= 3 and available_3mark and (marks_left % 2 == 1 or marks_left >= 9):
                q = available_3mark.pop(0)
                selected.append(q)
                current_marks += 3
            elif marks_left >= 2 and available_2mark:
                q = available_2mark.pop(0)
                selected.append(q)
                current_marks += 2
            elif marks_left >= 3 and available_3mark:
                q = available_3mark.pop(0)
                selected.append(q)
                current_marks += 3
            elif marks_left >= 1 and available_1mark:
                q = available_1mark.pop(0)
                selected.append(q)
                current_marks += 1
            else:
                return False  # Can't continue
        
        # Check if we hit exactly the target
        if current_marks == remaining_marks:
            self.selected_questions.extend(selected)
            for q in selected:
                self.used_ids.add(q.id)
                self.selected_question_ids.append(str(q.id))
            
            self.standalone_count = len(selected)
            self.standalone_marks = current_marks
            self.total_marks = self.nested_marks + self.standalone_marks
            
            print(f"  Selected: {self.standalone_count} standalone questions")
            print(f"  Marks breakdown:")
            marks_dist = defaultdict(int)
            for q in selected:
                marks_dist[q.marks] += 1
            for mark_value, count in sorted(marks_dist.items()):
                print(f"    {mark_value}-mark: {count} questions ({mark_value * count} marks)")
            
            return True
        
        return False
    
    def generate(self) -> Dict:
        """
        Generate Biology Paper 1
        
        Returns:
            Dict with paper data including question IDs list
        
        Raises:
            Exception if generation fails
        """
        max_attempts = 100
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE BIOLOGY PAPER 1 GENERATION")
        print(f"{'='*70}")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_questions = []
            self.selected_question_ids = []
            self.used_ids = set()
            self.nested_count = 0
            self.nested_marks = 0
            self.standalone_count = 0
            self.standalone_marks = 0
            self.total_marks = 0
            
            # Phase 1: Select 10-18 nested questions (~60 marks, flexible count)
            if not self._select_nested_questions():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at nested selection")
                continue
            
            # Phase 2: Fill remaining marks with standalone (2-mark, 3-mark, 1-mark)
            if not self._select_standalone_questions():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at standalone selection")
                continue
            
            # Success!
            generation_time = time.time() - start_time
            print(f"\n{'='*70}")
            print(f"SUCCESS! Generated in {attempt} attempts ({generation_time:.2f}s)")
            print(f"{'='*70}")
            
            return self._build_result(generation_time)
        
        # Failed
        raise Exception(
            f"Failed to generate paper after {max_attempts} attempts. "
            f"Available: Nested={len(self.nested_questions)}, "
            f"2-mark={len(self.standalone_2mark)}, "
            f"3-mark={len(self.standalone_3mark)}, "
            f"1-mark={len(self.standalone_1mark)}"
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with paper data and question IDs list"""
        
        # Build questions data
        questions_data = []
        for idx, question in enumerate(self.selected_questions, start=1):
            questions_data.append({
                'id': str(question.id),
                'question_number': idx,
                'question_text': question.question_text,
                'answer_text': question.answer_text,
                'marks': question.marks,
                'is_nested': question.is_nested,
                'nested_parts': question.nested_parts if question.is_nested else None,
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
        
        # Calculate distributions
        marks_distribution = defaultdict(int)
        topic_distribution = defaultdict(int)
        
        for q in self.selected_questions:
            marks_distribution[q.marks] += 1
            topic_distribution[str(q.topic.id)] += q.marks
        
        return {
            'paper': {
                'id': str(self.paper.id),
                'name': self.paper.name,
                'subject': {
                    'id': str(self.subject.id),
                    'name': self.subject.name
                }
            },
            'questions': questions_data,
            'question_ids': self.selected_question_ids,  # List of IDs for retrieval
            'statistics': {
                'total_questions': len(self.selected_questions),
                'total_marks': self.total_marks,
                'nested_count': self.nested_count,
                'nested_marks': self.nested_marks,
                'standalone_count': self.standalone_count,
                'standalone_marks': self.standalone_marks,
                'marks_distribution': dict(marks_distribution),
                'topic_distribution': dict(topic_distribution),
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': {
                    'total_marks_ok': self.total_marks == 80,
                    'total_questions_range_ok': 18 <= len(self.selected_questions) <= 27,
                    'nested_count_range_ok': 10 <= self.nested_count <= 18,
                    'nested_marks_range_ok': 55 <= self.nested_marks <= 65,
                    'standalone_marks_ok': self.standalone_marks == (80 - self.nested_marks),
                }
            }
        }
