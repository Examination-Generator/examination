"""
KCSE Biology Paper 2 Generator
Fixed to reach exactly 80 marks with proper section ordering

REQUIREMENTS:
- Section A: 5 questions × 8 marks = 40 marks (Questions 1-5)
- Section B: 3 questions × 20 marks = 40 marks (Questions 6-8)
  * Question 6: Graph question (priority), fallback to Essay if no graph
  * Questions 7-8: Essay questions (always)
- Total: 8 questions, exactly 80 marks
- Strict ordering: Section A first (1-5), then Section B (6-8)

ISSUE FIXED:
The previous generator was stopping at 73 marks because:
1. It was trying to select from a pool of 3-mark, 4-mark, 5-mark questions
2. No combination of these marks could reach exactly 80
3. The algorithm needs to target EXACTLY 8-mark and 20-mark questions

SOLUTION:
- Section A: Select exactly 5 × 8-mark questions
- Section B: Select exactly 3 × 20-mark questions
- Prioritize graph questions in Section B before falling back to essays
"""

import random
import time
from collections import defaultdict
from typing import List, Dict, Optional

from .models import Paper, Topic, Question, Subject


class KCSEBiologyPaper2Generator:
    """
    KCSE Biology Paper 2 Generator
    Section A: 5 × 8-mark questions = 40 marks
    Section B: 3 × 20-mark questions = 40 marks (graph priority, then essay)
    Total: 8 questions, 80 marks, strictly ordered
    """
    
    # Section A Requirements
    SECTION_A_8MARK_COUNT = 5
    SECTION_A_TOTAL = 5
    SECTION_A_MARKS = 40
    
    # Section B Requirements
    SECTION_B_20MARK_COUNT = 3
    SECTION_B_TOTAL = 3
    SECTION_B_MARKS = 40
    
    # Total
    TOTAL_QUESTIONS = 8
    TOTAL_MARKS = 80
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str]):
        """
        Initialize generator
        
        Args:
            paper_id: UUID of Biology Paper 2
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
        self.section_a_8mark = []
        self.section_b_20mark_graph = []  # Graph questions (priority)
        self.section_b_20mark_essay = []  # Essay questions (fallback)
        
        # Selection tracking
        self.selected_section_a = []
        self.selected_section_b = []
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
        
        # Separate questions by section, marks, and type
        for q in self.all_questions:
            section_name = q.section.name.upper() if q.section else ""
            question_type = q.kcse_question_type.upper() if q.kcse_question_type else ""
            
            # Section A: 8-mark questions
            if ("SECTION A" in section_name or "SECTION 1" in section_name) and q.marks == 8:
                self.section_a_8mark.append(q)
            
            # Section B: 20-mark questions (separate by type)
            elif ("SECTION B" in section_name or "SECTION 2" in section_name) and q.marks == 20:
                # Check if it's a graph question
                if "GRAPH" in question_type or "PLOT" in question_type or "CHART" in question_type:
                    self.section_b_20mark_graph.append(q)
                # Otherwise it's an essay
                else:
                    self.section_b_20mark_essay.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.section_a_8mark)
        random.shuffle(self.section_b_20mark_graph)
        random.shuffle(self.section_b_20mark_essay)
        
        print(f"\n[DATA LOADED - BIOLOGY PAPER 2]")
        print(f"  Section A:")
        print(f"    8-mark: {len(self.section_a_8mark)} (need {self.SECTION_A_8MARK_COUNT})")
        print(f"  Section B:")
        print(f"    20-mark (Graph): {len(self.section_b_20mark_graph)}")
        print(f"    20-mark (Essay): {len(self.section_b_20mark_essay)}")
        print(f"    Total 20-mark: {len(self.section_b_20mark_graph) + len(self.section_b_20mark_essay)} (need {self.SECTION_B_20MARK_COUNT})")
        
        # Check if we have enough questions
        total_20mark = len(self.section_b_20mark_graph) + len(self.section_b_20mark_essay)
        if len(self.section_a_8mark) < self.SECTION_A_8MARK_COUNT:
            print(f"\nWARNING: Not enough 8-mark questions for Section A!")
        if total_20mark < self.SECTION_B_20MARK_COUNT:
            print(f"\nWARNING: Not enough 20-mark questions for Section B!")
    
    def _select_section_a(self) -> bool:
        """Select Section A questions: 5 × 8-mark"""
        # Check availability
        available = [q for q in self.section_a_8mark if q.id not in self.used_ids]
        
        if len(available) < self.SECTION_A_8MARK_COUNT:
            return False
        
        # Select exactly 5 questions
        selected = available[:self.SECTION_A_8MARK_COUNT]
        
        # Verify total
        total_marks = sum(q.marks for q in selected)
        if len(selected) != self.SECTION_A_TOTAL or total_marks != self.SECTION_A_MARKS:
            return False
        
        # Accept selection
        self.selected_section_a = selected
        for q in selected:
            self.used_ids.add(q.id)
        
        print(f"\n[SECTION A SELECTED]")
        print(f"  Questions: {len(selected)}")
        print(f"  Total marks: {total_marks}")
        
        return True
    
    def _select_section_b(self) -> bool:
        """
        Select Section B questions: 3 × 20-mark
        Structure: 1 Graph (Question 6) + 2 Essays (Questions 7-8)
        """
        # Get available questions
        available_graph = [q for q in self.section_b_20mark_graph if q.id not in self.used_ids]
        available_essay = [q for q in self.section_b_20mark_essay if q.id not in self.used_ids]
        
        # We need: 1 graph + 2 essays = 3 questions
        # If no graph available, use 3 essays
        
        selected = []
        
        # Strategy: Try to get 1 graph question first, then 2 essays
        
        # Step 1: Try to get 1 graph question (for Question 6)
        if len(available_graph) >= 1:
            # Use 1 graph question as the first Section B question
            selected.append(available_graph[0])
            # Need 2 more essays
            if len(available_essay) < 2:
                return False
            selected.extend(available_essay[:2])
        else:
            # No graph available, use 3 essay questions
            if len(available_essay) < 3:
                return False
            selected.extend(available_essay[:3])
        
        # Verify total
        total_marks = sum(q.marks for q in selected)
        if len(selected) != self.SECTION_B_TOTAL or total_marks != self.SECTION_B_MARKS:
            return False
        
        # Accept selection
        self.selected_section_b = selected
        for q in selected:
            self.used_ids.add(q.id)
        
        # Count question types
        graph_count = sum(1 for q in selected if q in self.section_b_20mark_graph)
        essay_count = sum(1 for q in selected if q in self.section_b_20mark_essay)
        
        print(f"\n[SECTION B SELECTED]")
        print(f"  Questions: {len(selected)}")
        print(f"    Question 6 (Graph): {graph_count}")
        print(f"    Questions 7-8 (Essays): {essay_count}")
        print(f"  Total marks: {total_marks}")
        
        return True
    
    def generate(self) -> Dict:
        """Generate Biology Paper 2"""
        max_attempts = 100
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE BIOLOGY PAPER 2 GENERATION")
        print(f"{'='*70}")
        print(f"Target: Section A (5×8mk) + Section B (3×20mk) = 80 marks")
        print(f"Section B Structure: Q6=Graph (or Essay if no graph), Q7-8=Essays")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_section_a = []
            self.selected_section_b = []
            self.selected_question_ids = []
            self.used_ids = set()
            
            # Select Section A (5 × 8-mark)
            if not self._select_section_a():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section A selection")
                continue
            
            # Select Section B (3 × 20-mark, graph priority)
            if not self._select_section_b():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section B selection")
                continue
            
            # Success!
            generation_time = time.time() - start_time
            
            # Calculate final totals
            total_questions = len(self.selected_section_a) + len(self.selected_section_b)
            total_marks = sum(q.marks for q in self.selected_section_a) + sum(q.marks for q in self.selected_section_b)
            
            print(f"\n{'='*70}")
            print(f"SUCCESS! Generated in {attempt} attempts ({generation_time:.2f}s)")
            print(f"{'='*70}")
            print(f"Total Questions: {total_questions}")
            print(f"Total Marks: {total_marks}")
            
            if total_marks != self.TOTAL_MARKS:
                print(f"\nERROR: Total marks is {total_marks}, expected {self.TOTAL_MARKS}")
                continue
            
            return self._build_result(generation_time)
        
        # Failed
        raise Exception(
            f"Failed to generate paper after {max_attempts} attempts. "
            f"Available: 8-mark={len(self.section_a_8mark)}, "
            f"20-mark graph={len(self.section_b_20mark_graph)}, "
            f"20-mark essay={len(self.section_b_20mark_essay)}"
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with strictly ordered sections"""
        
        # Combine sections in strict order: Section A first (1-5), then Section B (6-8)
        all_questions = self.selected_section_a + self.selected_section_b
        
        # Build questions data with proper numbering
        questions_data = []
        for idx, question in enumerate(all_questions, start=1):
            self.selected_question_ids.append(str(question.id))
            
            # Determine which section this question belongs to
            section_letter = "A" if idx <= 5 else "B"
            
            questions_data.append({
                'id': str(question.id),
                'question_number': idx,
                'section_letter': section_letter,
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
        
        # Count graph vs essay in Section B
        section_b_graph_count = sum(1 for q in self.selected_section_b 
                                     if q in self.section_b_20mark_graph)
        section_b_essay_count = sum(1 for q in self.selected_section_b 
                                     if q in self.section_b_20mark_essay)
        
        # Identify which question is the graph (should be first in Section B = Question 6)
        has_graph_at_q6 = (len(self.selected_section_b) > 0 and 
                          self.selected_section_b[0] in self.section_b_20mark_graph)
        
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
                'total_marks': sum(q.marks for q in all_questions),
                'section_a_questions': len(self.selected_section_a),
                'section_a_marks': sum(q.marks for q in self.selected_section_a),
                'section_b_questions': len(self.selected_section_b),
                'section_b_marks': sum(q.marks for q in self.selected_section_b),
                'section_b_breakdown': {
                    'graph_questions': section_b_graph_count,
                    'essay_questions': section_b_essay_count,
                    'question_6_is_graph': has_graph_at_q6,
                },
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': {
                    'section_a_count_ok': len(self.selected_section_a) == 5,
                    'section_a_marks_ok': sum(q.marks for q in self.selected_section_a) == 40,
                    'section_b_count_ok': len(self.selected_section_b) == 3,
                    'section_b_marks_ok': sum(q.marks for q in self.selected_section_b) == 40,
                    'total_questions_ok': len(all_questions) == 8,
                    'total_marks_ok': sum(q.marks for q in all_questions) == 80,
                }
            }
        }