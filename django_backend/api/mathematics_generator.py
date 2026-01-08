"""
KCSE Mathematics Paper 1 & 2 Generator
Dynamic Algorithm with Strict Section Requirements

MATHEMATICS PAPER 1:
- Section I: 16 questions, 50 marks
  * 12 x 3-mark questions = 36 marks
  * 3 x 4-mark questions = 12 marks
  * 1 x 2-mark question = 2 marks
- Section II: 8 x 10-mark questions (student selects 5)
  * Questions numbered 17-24
  * Total available: 80 marks (student does 50 marks)
- Total: 24 questions, Section I must appear first, then Section II

MATHEMATICS PAPER 2:
- Section I: 16 questions, 50 marks
  * 12 x 3-mark questions = 36 marks
  * 3 x 2-mark questions = 6 marks
  * 2 x 4-mark questions = 8 marks
- Section II: 8 x 10-mark questions (student selects 5)
  * Questions numbered 17-24
  * Total available: 80 marks (student does 50 marks)
- Total: 24 questions, Section I must appear first, then Section II
"""

import random
import time
from collections import defaultdict
from typing import List, Dict, Optional

from .models import Paper, Topic, Question, Subject


class KCSEMathematicsPaper1Generator:
    """
    KCSE Mathematics Paper 1 Generator
    Section I: Flexible distribution totaling 50 marks
      - 3-mark questions form the majority (at least 12)
      - At least 2 questions of 4 marks
      - At least 2 questions of 2 marks
      - Total must equal 50 marks
    Section II: 8 questions (8x10mk, student selects 5) = 50 marks done
    Total questions vary based on Section I distribution
    """
    
    # Section I Requirements (KCSE Standard: 16 questions = 50 marks)
    SECTION_I_2MARK_COUNT = 1   # 1×2mk = 2 marks
    SECTION_I_3MARK_COUNT = 12  # 12×3mk = 36 marks (majority)
    SECTION_I_4MARK_COUNT = 3   # 3×4mk = 12 marks
    SECTION_I_TOTAL = 16        # Total: 16 questions
    SECTION_I_MARKS = 50        # Total: 50 marks
    
    # Section II Requirements
    SECTION_II_10MARK_COUNT = 8
    SECTION_II_TOTAL = 8
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str]):
        """
        Initialize generator
        
        Args:
            paper_id: UUID of Mathematics Paper 1
            selected_topic_ids: List of topic UUIDs
        """
        self.paper_id = paper_id
        self.selected_topic_ids = selected_topic_ids
        
        # Data storage
        self.paper = None
        self.subject = None
        self.topics = []
        self.all_questions = []
        
        # Question pools by section and marks
        self.section_i_2mark = []
        self.section_i_3mark = []
        self.section_i_4mark = []
        self.section_ii_10mark = []
        
        # Selection tracking
        self.selected_section_i = []
        self.selected_section_ii = []
        self.selected_question_ids = []
        self.used_ids = set()
        
        # Statistics
        self.attempts = 0
    
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
        
        # Separate questions by section and marks
        for q in self.all_questions:
            section_name = q.section.name.upper() if q.section else ""
            
            if "SECTION I" in section_name or "SECTION 1" in section_name:
                if q.marks == 2:
                    self.section_i_2mark.append(q)
                elif q.marks == 3:
                    self.section_i_3mark.append(q)
                elif q.marks == 4:
                    self.section_i_4mark.append(q)
            elif "SECTION II" in section_name or "SECTION 2" in section_name:
                if q.marks == 10:
                    self.section_ii_10mark.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.section_i_2mark)
        random.shuffle(self.section_i_3mark)
        random.shuffle(self.section_i_4mark)
        random.shuffle(self.section_ii_10mark)
        
        print(f"\n[DATA LOADED - MATHEMATICS PAPER 1]")
        print(f"  Section I:")
        print(f"    2-mark: {len(self.section_i_2mark)} (need {self.SECTION_I_2MARK_COUNT})")
        print(f"    3-mark: {len(self.section_i_3mark)} (need {self.SECTION_I_3MARK_COUNT}, majority)")
        print(f"    4-mark: {len(self.section_i_4mark)} (need {self.SECTION_I_4MARK_COUNT})")
        print(f"  Section II:")
        print(f"    10-mark: {len(self.section_ii_10mark)} (need {self.SECTION_II_10MARK_COUNT})")
    
    def _select_section_i(self) -> bool:
        """
        Select Section I questions: 1×2mk + 12×3mk + 3×4mk = 16 questions, 50 marks
        """
        # Check availability
        if (len(self.section_i_2mark) < self.SECTION_I_2MARK_COUNT or
            len(self.section_i_3mark) < self.SECTION_I_3MARK_COUNT or
            len(self.section_i_4mark) < self.SECTION_I_4MARK_COUNT):
            return False
        
        available_2 = [q for q in self.section_i_2mark if q.id not in self.used_ids]
        available_3 = [q for q in self.section_i_3mark if q.id not in self.used_ids]
        available_4 = [q for q in self.section_i_4mark if q.id not in self.used_ids]
        
        if (len(available_2) < self.SECTION_I_2MARK_COUNT or
            len(available_3) < self.SECTION_I_3MARK_COUNT or
            len(available_4) < self.SECTION_I_4MARK_COUNT):
            return False
        
        # Select exact counts needed
        selected = []
        
        # Add 1 × 2-mark
        for i in range(self.SECTION_I_2MARK_COUNT):
            selected.append(available_2[i])
        
        # Add 12 × 3-mark
        for i in range(self.SECTION_I_3MARK_COUNT):
            selected.append(available_3[i])
        
        # Add 3 × 4-mark
        for i in range(self.SECTION_I_4MARK_COUNT):
            selected.append(available_4[i])
        
        # Verify totals
        total_marks = (self.SECTION_I_2MARK_COUNT * 2) + (self.SECTION_I_3MARK_COUNT * 3) + (self.SECTION_I_4MARK_COUNT * 4)
        
        if len(selected) == self.SECTION_I_TOTAL and total_marks == self.SECTION_I_MARKS:
            self.selected_section_i = selected
            for q in selected:
                self.used_ids.add(q.id)
            
            print(f"\n[SECTION I SELECTED - PAPER 1]")
            print(f"  2-mark: {self.SECTION_I_2MARK_COUNT}, 3-mark: {self.SECTION_I_3MARK_COUNT} (majority), 4-mark: {self.SECTION_I_4MARK_COUNT}")
            print(f"  Total: {len(selected)} questions, {total_marks} marks")
            return True
        
        return False
    
    def _select_section_ii(self) -> bool:
        """Select Section II questions: 8x10mk
        Section II (10-mark) is independent from Section I (2,3,4-mark) - no overlap possible"""
        # Check availability
        if len(self.section_ii_10mark) < self.SECTION_II_10MARK_COUNT:
            return False
        
        # Select 8 x 10-mark directly (no used_ids check - different mark pool)
        selected = self.section_ii_10mark[:self.SECTION_II_10MARK_COUNT]
        
        # Accept selection
        self.selected_section_ii = selected
        for q in selected:
            self.used_ids.add(q.id)
        
        print(f"\n[SECTION II SELECTED - PAPER 1]")
        print(f"  Questions: {len(selected)}")
        print(f"  Total marks: {sum(q.marks for q in selected)}")
        
        return True
    
    def generate(self) -> Dict:
        """Generate Mathematics Paper 1"""
        max_attempts = 100
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE MATHEMATICS PAPER 1 GENERATION")
        print(f"{'='*70}")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_section_i = []
            self.selected_section_ii = []
            self.selected_question_ids = []
            self.used_ids = set()
            
            # Select Section I
            if not self._select_section_i():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section I selection")
                continue
            
            # Select Section II
            if not self._select_section_ii():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section II selection")
                continue
            
            # Success!
            generation_time = time.time() - start_time
            print(f"\n{'='*70}")
            print(f"SUCCESS! Generated in {attempt} attempts ({generation_time:.2f}s)")
            print(f"{'='*70}")
            
            return self._build_result(generation_time)
        
        # Failed
        raise Exception(f"Failed to generate paper after {max_attempts} attempts")
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with strictly ordered sections"""
        
        # Combine sections in strict order: Section I first, then Section II
        all_questions = self.selected_section_i + self.selected_section_ii
        
        # Build questions data with proper numbering
        questions_data = []
        for idx, question in enumerate(all_questions, start=1):
            self.selected_question_ids.append(str(question.id))
            questions_data.append({
                'id': str(question.id),
                'question_number': idx,
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
            'question_ids': self.selected_question_ids,
            'statistics': {
                'total_questions': len(all_questions),
                'section_i_questions': len(self.selected_section_i),
                'section_i_marks': sum(q.marks for q in self.selected_section_i),
                'section_ii_questions': len(self.selected_section_ii),
                'section_ii_marks': sum(q.marks for q in self.selected_section_ii),
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': {
                    'section_i_marks_ok': sum(q.marks for q in self.selected_section_i) == 50,
                    'section_ii_count_ok': len(self.selected_section_ii) == 8,
                    'section_ii_marks_ok': sum(q.marks for q in self.selected_section_ii) == 80,
                }
            }
        }


class KCSEMathematicsPaper2Generator:
    """
    KCSE Mathematics Paper 2 Generator
    Section I: 17 questions (3×2mk + 12×3mk + 2×4mk) = 50 marks
    Section II: 8 questions (8×10mk, student selects 5) = 50 marks done
    Total: 25 questions, strictly ordered by section
    """
    
    # Section I Requirements
    SECTION_I_3MARK_COUNT = 12  # 3-mark questions form majority
    SECTION_I_2MARK_COUNT = 3   # 3 questions of 2 marks
    SECTION_I_4MARK_COUNT = 2   # 2 questions of 4 marks
    SECTION_I_MARKS = 50
    
    # Section II Requirements
    SECTION_II_10MARK_COUNT = 8
    SECTION_II_TOTAL = 8
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str]):
        """
        Initialize generator
        
        Args:
            paper_id: UUID of Mathematics Paper 2
            selected_topic_ids: List of topic UUIDs
        """
        self.paper_id = paper_id
        self.selected_topic_ids = selected_topic_ids
        
        # Data storage
        self.paper = None
        self.subject = None
        self.topics = []
        self.all_questions = []
        
        # Question pools by section and marks
        self.section_i_2mark = []
        self.section_i_3mark = []
        self.section_i_4mark = []
        self.section_ii_10mark = []
        
        # Selection tracking
        self.selected_section_i = []
        self.selected_section_ii = []
        self.selected_question_ids = []
        self.used_ids = set()
        
        # Statistics
        self.attempts = 0
    
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
        
        # Separate questions by section and marks
        for q in self.all_questions:
            section_name = q.section.name.upper() if q.section else ""
            
            if "SECTION I" in section_name or "SECTION 1" in section_name:
                if q.marks == 2:
                    self.section_i_2mark.append(q)
                elif q.marks == 3:
                    self.section_i_3mark.append(q)
                elif q.marks == 4:
                    self.section_i_4mark.append(q)
            elif "SECTION II" in section_name or "SECTION 2" in section_name:
                if q.marks == 10:
                    self.section_ii_10mark.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.section_i_2mark)
        random.shuffle(self.section_i_3mark)
        random.shuffle(self.section_i_4mark)
        random.shuffle(self.section_ii_10mark)
        
        print(f"\n[DATA LOADED - MATHEMATICS PAPER 2]")
        print(f"  Section I:")
        print(f"    2-mark: {len(self.section_i_2mark)} (need {self.SECTION_I_2MARK_COUNT})")
        print(f"    3-mark: {len(self.section_i_3mark)} (need {self.SECTION_I_3MARK_COUNT})")
        print(f"    4-mark: {len(self.section_i_4mark)} (need {self.SECTION_I_4MARK_COUNT})")
        print(f"  Section II:")
        print(f"    10-mark: {len(self.section_ii_10mark)} (need {self.SECTION_II_10MARK_COUNT})")
    
    def _select_section_i(self) -> bool:
        """
        Select Section I questions for Paper 2.
        Paper 2: 3×2mk + 2×4mk + 12×3mk = 6+8+36 = 50 marks exactly
        """
        # Check minimum availability
        if (len(self.section_i_2mark) < self.SECTION_I_2MARK_COUNT or
            len(self.section_i_3mark) < self.SECTION_I_3MARK_COUNT or
            len(self.section_i_4mark) < self.SECTION_I_4MARK_COUNT):
            return False
        
        available_2 = [q for q in self.section_i_2mark if q.id not in self.used_ids]
        available_3 = [q for q in self.section_i_3mark if q.id not in self.used_ids]
        available_4 = [q for q in self.section_i_4mark if q.id not in self.used_ids]
        
        if (len(available_2) < self.SECTION_I_2MARK_COUNT or
            len(available_3) < self.SECTION_I_3MARK_COUNT or
            len(available_4) < self.SECTION_I_4MARK_COUNT):
            return False
        
        # Select exactly the required counts (Paper 2 needs no additional questions)
        selected = []
        
        # Add 3 × 2-mark
        for i in range(self.SECTION_I_2MARK_COUNT):
            selected.append(available_2[i])
        
        # Add 2 × 4-mark
        for i in range(self.SECTION_I_4MARK_COUNT):
            selected.append(available_4[i])
        
        # Add 12 × 3-mark
        for i in range(self.SECTION_I_3MARK_COUNT):
            selected.append(available_3[i])
        
        # Verify total (should be exactly 50)
        total_marks = (self.SECTION_I_2MARK_COUNT * 2) + (self.SECTION_I_3MARK_COUNT * 3) + (self.SECTION_I_4MARK_COUNT * 4)
        
        if total_marks == self.SECTION_I_MARKS:
            self.selected_section_i = selected
            for q in selected:
                self.used_ids.add(q.id)
            
            print(f"\n[SECTION I SELECTED - PAPER 2]")
            print(f"  2-mark: {self.SECTION_I_2MARK_COUNT}, 3-mark: {self.SECTION_I_3MARK_COUNT} (majority), 4-mark: {self.SECTION_I_4MARK_COUNT}")
            print(f"  Total: {len(selected)} questions, {total_marks} marks")
            return True
        
        return False
    
    def _select_section_ii(self) -> bool:
        """Select Section II questions: 8x10mk"""
        # Check availability
        if len(self.section_ii_10mark) < self.SECTION_II_10MARK_COUNT:
            return False
        
        # Select 8 x 10-mark (no used_ids check needed - Section II questions are separate from Section I)
        selected = self.section_ii_10mark[:self.SECTION_II_10MARK_COUNT]
        
        # Accept selection
        self.selected_section_ii = selected
        for q in selected:
            self.used_ids.add(q.id)
        
        print(f"\n[SECTION II SELECTED]")
        print(f"  Questions: {len(selected)}")
        print(f"  Total marks: {sum(q.marks for q in selected)}")
        
        return True
    
    def generate(self) -> Dict:
        """Generate Mathematics Paper 2"""
        max_attempts = 100
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE MATHEMATICS PAPER 2 GENERATION")
        print(f"{'='*70}")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_section_i = []
            self.selected_section_ii = []
            self.selected_question_ids = []
            self.used_ids = set()
            
            # Select Section I
            if not self._select_section_i():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section I selection")
                continue
            
            # Select Section II
            if not self._select_section_ii():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section II selection")
                continue
            
            # Success!
            generation_time = time.time() - start_time
            print(f"\n{'='*70}")
            print(f"SUCCESS! Generated in {attempt} attempts ({generation_time:.2f}s)")
            print(f"{'='*70}")
            
            return self._build_result(generation_time)
        
        # Failed
        raise Exception(f"Failed to generate paper after {max_attempts} attempts")
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with strictly ordered sections"""
        
        # Combine sections in strict order: Section I first, then Section II
        all_questions = self.selected_section_i + self.selected_section_ii
        
        # Build questions data with proper numbering
        questions_data = []
        for idx, question in enumerate(all_questions, start=1):
            self.selected_question_ids.append(str(question.id))
            questions_data.append({
                'id': str(question.id),
                'question_number': idx,
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
            'question_ids': self.selected_question_ids,
            'statistics': {
                'total_questions': len(all_questions),
                'section_i_questions': len(self.selected_section_i),
                'section_i_marks': sum(q.marks for q in self.selected_section_i),
                'section_ii_questions': len(self.selected_section_ii),
                'section_ii_marks': sum(q.marks for q in self.selected_section_ii),
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': {
                    'section_i_marks_ok': sum(q.marks for q in self.selected_section_i) == 50,
                    'section_ii_count_ok': len(self.selected_section_ii) == 8,
                    'section_ii_marks_ok': sum(q.marks for q in self.selected_section_ii) == 80,
                }
            }
        }