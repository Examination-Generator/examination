"""
KCSE Chemistry Papers Generator Suite - FIXED VERSION
Based on Chemistry exam structure analysis

PAPER 1 (Section A) - 80 marks, 2 hours:
- 77.8% nested questions (~62 marks) - Multi-part questions
- 22.2% standalone questions (~18 marks) - Fill remaining to exactly 80
- Flexible question count (typically 18-25 questions)

PAPER 2 (Section B) - 80 marks, 2 hours:
- EXACTLY 7 questions, all nested
- Each question: 10-13 marks (flexible combinations to reach 80)
- Common patterns: 2X10mk + 2X11mk + 2X13mk + 1X12mk = 80
- Minimum 6 questions, Maximum 8 questions allowed
- MUST total exactly 80 marks
"""

import random
import time
from collections import defaultdict
from typing import List, Dict, Optional

from .models import Paper, Topic, Question, Subject


class KCSEChemistryPaper1Generator:
    """
    KCSE Chemistry Paper 1 Generator
    Dynamic algorithm: Nested (~62 marks, 77.8%) + Standalone (~18 marks, 22.2%) = exactly 80 marks
    """
    
    # Constants
    TOTAL_MARKS = 80
    TARGET_NESTED_MARKS = 62
    TARGET_STANDALONE_MARKS = 18
    MIN_NESTED_MARKS = 58
    MAX_NESTED_MARKS = 66
    MIN_STANDALONE_MARKS = 14
    MAX_STANDALONE_MARKS = 22
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str]):
        """
        Initialize Paper 1 generator
        
        Args:
            paper_id: UUID of Chemistry Paper 1
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
        self.standalone_4mark = []
        
        # Selection tracking
        self.selected_questions = []
        self.selected_question_ids = []
        self.used_ids = set()
        
        # Statistics
        self.nested_count = 0
        self.nested_marks = 0
        self.standalone_count = 0
        self.standalone_marks = 0
        self.total_marks = 0
        self.attempts = 0
        self.use_standalone_only = False
    
    def load_data(self):
        """Load all questions from database for selected topics"""
        # Load paper and subject
        self.paper = Paper.objects.select_related('subject').get(
            id=self.paper_id,
            is_active=True
        )
        self.subject = self.paper.subject
        
        # Validate Chemistry Paper 1 - FIXED VERSION
        paper_name_lower = self.paper.name.lower()
        subject_name_lower = self.subject.name.lower()
        
        is_chemistry = 'chemistry' in subject_name_lower
        is_paper_1 = any(keyword in paper_name_lower for keyword in [
            'paper 1', 'paper i', 'paper one', 'paper  1'
        ])
        
        if not is_chemistry:
            raise ValueError(f"This generator requires a Chemistry paper. Received subject: '{self.subject.name}'")
        
        if not is_paper_1:
            raise ValueError(f"This generator is only for Chemistry Paper 1. Received paper: '{self.paper.name}'")
        
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
                elif q.marks == 4:
                    self.standalone_4mark.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.nested_questions)
        random.shuffle(self.standalone_1mark)
        random.shuffle(self.standalone_2mark)
        random.shuffle(self.standalone_3mark)
        random.shuffle(self.standalone_4mark)
        
        print(f"\n[CHEMISTRY PAPER 1 DATA LOADED]")
        print(f"  Subject: {self.subject.name}")
        print(f"  Paper: {self.paper.name}")
        print(f"  Nested questions: {len(self.nested_questions)}")
        print(f"  1-mark standalone: {len(self.standalone_1mark)}")
        print(f"  2-mark standalone: {len(self.standalone_2mark)}")
        print(f"  3-mark standalone: {len(self.standalone_3mark)}")
        print(f"  4-mark standalone: {len(self.standalone_4mark)}")
        
        # Check if we need standalone-only mode
        self.use_standalone_only = len(self.nested_questions) < 8
        if self.use_standalone_only:
            print(f"\n⚠️  WARNING: Not enough nested questions ({len(self.nested_questions)} < 8)")
            print(f"  → Using STANDALONE-ONLY mode")
    
    def _select_nested_questions(self) -> bool:
        """
        Select nested questions to reach target ~62 marks (77.8% of paper)
        Acceptable range: 58-66 marks
        
        Returns:
            bool: True if successful
        """
        available = [q for q in self.nested_questions if q.id not in self.used_ids]
        
        if len(available) < 8:
            return False
        
        random.shuffle(available)
        
        selected = []
        total_marks = 0
        target_marks = self.TARGET_NESTED_MARKS
        
        # Select questions aiming for ~62 marks
        for question in available:
            # Stop if we're in acceptable range and adding more would exceed max
            if self.MIN_NESTED_MARKS <= total_marks <= self.MAX_NESTED_MARKS:
                if (total_marks + question.marks) > self.MAX_NESTED_MARKS:
                    break
            
            # Add question
            selected.append(question)
            total_marks += question.marks
            
            # Break if we hit a good target
            if self.MIN_NESTED_MARKS <= total_marks <= self.MAX_NESTED_MARKS:
                # If we're close to target, stop
                if abs(total_marks - target_marks) <= 2:
                    break
        
        # Validate: must be in acceptable range
        if not (self.MIN_NESTED_MARKS <= total_marks <= self.MAX_NESTED_MARKS):
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
        print(f"  Selected: {self.nested_count} questions")
        print(f"  Total marks: {self.nested_marks} (target: ~62)")
        
        return True
    
    def _select_standalone_questions(self) -> bool:
        """
        Fill remaining marks with standalone questions to reach exactly 80 marks
        Target: ~18 marks (22.2% of paper)
        Priority: 3-mark > 2-mark > 4-mark > 1-mark
        
        Returns:
            bool: True if exactly 80 marks achieved
        """
        remaining_marks = self.TOTAL_MARKS - self.total_marks
        
        print(f"\n[STANDALONE SELECTION]")
        print(f"  Need: {remaining_marks} marks to reach 80")
        
        if remaining_marks <= 0:
            return self.total_marks == self.TOTAL_MARKS
        
        # Validate range
        if not (self.MIN_STANDALONE_MARKS <= remaining_marks <= self.MAX_STANDALONE_MARKS):
            return False
        
        selected = []
        current_marks = 0
        max_questions = 15
        
        # Available pools
        available_4mark = [q for q in self.standalone_4mark if q.id not in self.used_ids]
        available_3mark = [q for q in self.standalone_3mark if q.id not in self.used_ids]
        available_2mark = [q for q in self.standalone_2mark if q.id not in self.used_ids]
        available_1mark = [q for q in self.standalone_1mark if q.id not in self.used_ids]
        
        random.shuffle(available_4mark)
        random.shuffle(available_3mark)
        random.shuffle(available_2mark)
        random.shuffle(available_1mark)
        
        # Fill marks to exactly reach target
        while current_marks < remaining_marks and len(selected) < max_questions:
            marks_left = remaining_marks - current_marks
            
            # Exact matches
            if marks_left == 1 and available_1mark:
                q = available_1mark.pop(0)
                selected.append(q)
                current_marks += 1
                break
            elif marks_left == 2 and available_2mark:
                q = available_2mark.pop(0)
                selected.append(q)
                current_marks += 2
                break
            elif marks_left == 3 and available_3mark:
                q = available_3mark.pop(0)
                selected.append(q)
                current_marks += 3
                break
            elif marks_left == 4 and available_4mark:
                q = available_4mark.pop(0)
                selected.append(q)
                current_marks += 4
                break
            
            # For larger gaps, use priority: 3 > 2 > 4 > 1
            if marks_left >= 3 and available_3mark and (marks_left % 2 == 1 or marks_left >= 9):
                q = available_3mark.pop(0)
                selected.append(q)
                current_marks += 3
            elif marks_left >= 2 and available_2mark:
                q = available_2mark.pop(0)
                selected.append(q)
                current_marks += 2
            elif marks_left >= 4 and available_4mark:
                q = available_4mark.pop(0)
                selected.append(q)
                current_marks += 4
            elif marks_left >= 3 and available_3mark:
                q = available_3mark.pop(0)
                selected.append(q)
                current_marks += 3
            elif marks_left >= 1 and available_1mark:
                q = available_1mark.pop(0)
                selected.append(q)
                current_marks += 1
            else:
                return False
        
        # Verify exact target reached
        if current_marks == remaining_marks:
            self.selected_questions.extend(selected)
            for q in selected:
                self.used_ids.add(q.id)
                self.selected_question_ids.append(str(q.id))
            
            self.standalone_count = len(selected)
            self.standalone_marks = current_marks
            self.total_marks = self.nested_marks + self.standalone_marks
            
            print(f"  Selected: {self.standalone_count} questions")
            print(f"  Total standalone marks: {self.standalone_marks}")
            
            return True
        
        return False
    
    def _select_standalone_only(self) -> bool:
        """
        Fallback: Use only standalone questions if insufficient nested questions
        Similar to Biology's approach
        
        Returns:
            bool: True if exactly 80 marks achieved
        """
        print(f"\n[STANDALONE-ONLY MODE]")
        
        # Collect all available standalone
        all_standalone = []
        all_standalone.extend(self.standalone_1mark)
        all_standalone.extend(self.standalone_2mark)
        all_standalone.extend(self.standalone_3mark)
        all_standalone.extend(self.standalone_4mark)
        
        # Group by marks
        by_marks = defaultdict(list)
        for q in all_standalone:
            by_marks[q.marks].append(q)
        
        for questions in by_marks.values():
            random.shuffle(questions)
        
        pools = {mark: list(by_marks.get(mark, [])) for mark in [1, 2, 3, 4, 5, 6]}
        
        # Try to reach 80 using combinations
        selected = []
        current_marks = 0
        target = 80
        
        # Priority: larger marks first
        priority = [4, 3, 2, 1]
        
        while current_marks < target:
            marks_left = target - current_marks
            added = False
            
            for mark_value in priority:
                if mark_value <= marks_left and pools.get(mark_value):
                    q = pools[mark_value].pop(0)
                    selected.append(q)
                    current_marks += mark_value
                    added = True
                    break
            
            if not added:
                return False
        
        if current_marks == target:
            self.selected_questions = selected
            for q in selected:
                self.used_ids.add(q.id)
                self.selected_question_ids.append(str(q.id))
            
            self.nested_count = 0
            self.nested_marks = 0
            self.standalone_count = len(selected)
            self.standalone_marks = current_marks
            self.total_marks = current_marks
            
            print(f"  Selected: {self.standalone_count} questions, {self.total_marks} marks")
            return True
        
        return False
    
    def generate(self) -> Dict:
        """Generate Chemistry Paper 1"""
        max_attempts = 100
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE CHEMISTRY PAPER 1 GENERATION")
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
            
            if self.use_standalone_only:
                if not self._select_standalone_only():
                    if attempt % 10 == 0:
                        print(f"[ATTEMPT {attempt}] Failed at standalone-only")
                    continue
            else:
                # Phase 1: Nested (~62 marks)
                if not self._select_nested_questions():
                    if attempt % 10 == 0:
                        print(f"[ATTEMPT {attempt}] Failed at nested selection")
                    continue
                
                # Phase 2: Standalone (~18 marks)
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
        
        raise Exception(f"Failed to generate paper after {max_attempts} attempts")
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with paper data"""
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
                'difficulty': question.difficulty,
            })
        
        marks_distribution = defaultdict(int)
        for q in self.selected_questions:
            marks_distribution[q.marks] += 1
        
        return {
            'paper': {
                'id': str(self.paper.id),
                'name': self.paper.name,
                'subject': {'id': str(self.subject.id), 'name': self.subject.name}
            },
            'questions': questions_data,
            'question_ids': self.selected_question_ids,
            'statistics': {
                'total_questions': len(self.selected_questions),
                'total_marks': self.total_marks,
                'nested_count': self.nested_count,
                'nested_marks': self.nested_marks,
                'nested_percentage': round((self.nested_marks / 80) * 100, 1) if self.total_marks > 0 else 0,
                'standalone_count': self.standalone_count,
                'standalone_marks': self.standalone_marks,
                'standalone_percentage': round((self.standalone_marks / 80) * 100, 1) if self.total_marks > 0 else 0,
                'marks_distribution': dict(marks_distribution),
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': {
                    'total_marks_ok': self.total_marks == 80,
                    'nested_marks_in_range': 58 <= self.nested_marks <= 66 if not self.use_standalone_only else True,
                    'standalone_marks_in_range': 14 <= self.standalone_marks <= 22 if not self.use_standalone_only else True,
                }
            }
        }


class KCSEChemistryPaper2Generator:
    """
    KCSE Chemistry Paper 2 Generator
    EXACTLY 7 questions (flexible: 6-8), all nested, totaling EXACTLY 80 marks
    Each question: 10-13 marks
    Common pattern: 2X10 + 2X11 + 2X13 + 1X12 = 80
    """
    
    TOTAL_MARKS = 80
    TARGET_QUESTIONS = 7
    MIN_QUESTIONS = 6
    MAX_QUESTIONS = 8
    MIN_QUESTION_MARKS = 10
    MAX_QUESTION_MARKS = 13
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str]):
        """
        Initialize Paper 2 generator
        
        Args:
            paper_id: UUID of Chemistry Paper 2
            selected_topic_ids: List of topic UUIDs
        """
        self.paper_id = paper_id
        self.selected_topic_ids = selected_topic_ids
        
        # Data storage
        self.paper = None
        self.subject = None
        self.topics = []
        self.nested_questions = []
        
        # Selection tracking
        self.selected_questions = []
        self.selected_question_ids = []
        self.used_ids = set()
        
        # Statistics
        self.total_marks = 0
        self.attempts = 0
    
    def load_data(self):
        """Load nested questions from database"""
        # Load paper and subject
        self.paper = Paper.objects.select_related('subject').get(
            id=self.paper_id,
            is_active=True
        )
        self.subject = self.paper.subject
        
        # Validate Chemistry Paper 2 - FIXED VERSION
        paper_name_lower = self.paper.name.lower()
        subject_name_lower = self.subject.name.lower()
        
        is_chemistry = 'chemistry' in subject_name_lower
        is_paper_2 = any(keyword in paper_name_lower for keyword in [
            'paper 2', 'paper ii', 'paper two', 'paper  2'
        ])
        
        if not is_chemistry:
            raise ValueError(f"This generator requires a Chemistry paper. Received subject: '{self.subject.name}'")
        
        if not is_paper_2:
            raise ValueError(f"This generator is only for Chemistry Paper 2. Received paper: '{self.paper.name}'")
        
        # Load selected topics
        self.topics = list(Topic.objects.filter(
            id__in=self.selected_topic_ids,
            paper=self.paper,
            is_active=True
        ))
        
        if not self.topics:
            raise ValueError("No valid topics found for the selected IDs")
        
        # Load ONLY nested questions with marks between 10-13
        self.nested_questions = list(Question.objects.filter(
            subject=self.subject,
            paper=self.paper,
            topic__in=self.topics,
            is_nested=True,
            marks__gte=self.MIN_QUESTION_MARKS,
            marks__lte=self.MAX_QUESTION_MARKS,
            is_active=True
        ).select_related('topic', 'section'))
        
        if not self.nested_questions:
            raise ValueError("No nested questions (10-13 marks) found for selected topics")
        
        # Shuffle for randomness
        random.shuffle(self.nested_questions)
        
        print(f"\n[CHEMISTRY PAPER 2 DATA LOADED]")
        print(f"  Subject: {self.subject.name}")
        print(f"  Paper: {self.paper.name}")
        print(f"  Nested questions (10-13 marks): {len(self.nested_questions)}")
        
        # Show distribution by marks
        marks_dist = defaultdict(int)
        for q in self.nested_questions:
            marks_dist[q.marks] += 1
        
        print(f"  Distribution:")
        for marks in sorted(marks_dist.keys()):
            print(f"    {marks}-mark: {marks_dist[marks]} questions")
        
        # Validate minimum requirements
        if len(self.nested_questions) < self.MIN_QUESTIONS:
            raise ValueError(f"Need at least {self.MIN_QUESTIONS} nested questions (10-13 marks)")
    
    def _select_7_questions(self) -> bool:
        """
        Select exactly 7 questions (or 6-8) that sum to exactly 80 marks
        Uses recursive/backtracking approach to find valid combinations
        
        Returns:
            bool: True if successful
        """
        available = [q for q in self.nested_questions if q.id not in self.used_ids]
        
        if len(available) < self.MIN_QUESTIONS:
            return False
        
        # Try to find a combination that sums to 80
        # Target: 7 questions, but allow 6-8
        for target_count in [self.TARGET_QUESTIONS, 6, 8]:
            result = self._find_combination(available, target_count, self.TOTAL_MARKS)
            if result:
                selected = result
                total_marks = sum(q.marks for q in selected)
                
                if total_marks == self.TOTAL_MARKS and self.MIN_QUESTIONS <= len(selected) <= self.MAX_QUESTIONS:
                    # Accept selection
                    self.selected_questions = selected
                    for q in selected:
                        self.used_ids.add(q.id)
                        self.selected_question_ids.append(str(q.id))
                    
                    self.total_marks = total_marks
                    
                    print(f"\n[QUESTION SELECTION]")
                    print(f"  Selected: {len(selected)} questions")
                    print(f"  Total marks: {self.total_marks}")
                    print(f"  Breakdown:")
                    for idx, q in enumerate(selected, start=1):
                        print(f"    Q{idx}: {q.marks} marks - {q.topic.name}")
                    
                    return True
        
        return False
    
    def _find_combination(self, questions: List, target_count: int, target_marks: int, 
                         current: List = None, start_idx: int = 0) -> Optional[List]:
        """
        Recursive helper to find combination of questions summing to target marks
        
        Args:
            questions: Available questions
            target_count: Target number of questions
            target_marks: Target sum of marks
            current: Current selection (for recursion)
            start_idx: Start index (for recursion)
            
        Returns:
            List of questions if found, None otherwise
        """
        if current is None:
            current = []
        
        # Base case: if we have target_count questions
        if len(current) == target_count:
            if sum(q.marks for q in current) == target_marks:
                return current[:]
            return None
        
        # If we've exceeded target marks, stop
        if sum(q.marks for q in current) >= target_marks:
            return None
        
        # Try each remaining question
        for i in range(start_idx, len(questions)):
            current.append(questions[i])
            result = self._find_combination(questions, target_count, target_marks, current, i + 1)
            if result:
                return result
            current.pop()
        
        return None
    
    def generate(self) -> Dict:
        """Generate Chemistry Paper 2"""
        max_attempts = 200  # May need more attempts due to exact combination requirement
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE CHEMISTRY PAPER 2 GENERATION")
        print(f"{'='*70}")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_questions = []
            self.selected_question_ids = []
            self.used_ids = set()
            self.total_marks = 0
            
            # Shuffle available questions for variety
            random.shuffle(self.nested_questions)
            
            # Select 7 questions (or 6-8) summing to exactly 80
            if not self._select_7_questions():
                if attempt % 20 == 0:
                    print(f"[ATTEMPT {attempt}] Failed to find valid combination")
                continue
            
            # Success!
            generation_time = time.time() - start_time
            print(f"\n{'='*70}")
            print(f"SUCCESS! Generated in {attempt} attempts ({generation_time:.2f}s)")
            print(f"{'='*70}")
            
            return self._build_result(generation_time)
        
        raise Exception(
            f"Failed to generate paper after {max_attempts} attempts. "
            f"Try adding more questions or adjusting topic selection."
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with paper data"""
        questions_data = []
        for idx, question in enumerate(self.selected_questions, start=1):
            questions_data.append({
                'id': str(question.id),
                'question_number': idx,
                'question_text': question.question_text,
                'answer_text': question.answer_text,
                'marks': question.marks,
                'is_nested': question.is_nested,
                'nested_parts': question.nested_parts,
                'topic': {
                    'id': str(question.topic.id),
                    'name': question.topic.name
                },
                'difficulty': question.difficulty,
            })
        
        marks_distribution = defaultdict(int)
        topic_distribution = defaultdict(int)
        
        for q in self.selected_questions:
            marks_distribution[q.marks] += 1
            topic_distribution[str(q.topic.id)] += q.marks
        
        return {
            'paper': {
                'id': str(self.paper.id),
                'name': self.paper.name,
                'subject': {'id': str(self.subject.id), 'name': self.subject.name}
            },
            'questions': questions_data,
            'question_ids': self.selected_question_ids,
            'statistics': {
                'total_questions': len(self.selected_questions),
                'total_marks': self.total_marks,
                'marks_distribution': dict(marks_distribution),
                'topic_distribution': dict(topic_distribution),
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': {
                    'total_marks_ok': self.total_marks == 80,
                    'question_count_ok': self.MIN_QUESTIONS <= len(self.selected_questions) <= self.MAX_QUESTIONS,
                    'all_nested': all(q['is_nested'] for q in questions_data),
                    'marks_range_ok': all(10 <= q['marks'] <= 13 for q in questions_data),
                }
            }
        }

