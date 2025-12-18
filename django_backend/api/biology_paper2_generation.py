"""
KCSE Biology Paper 2 Generator - CORRECTED FORMAT
Section A: 5 questions x 8 marks = 40 marks (ALL COMPULSORY)
Section B: 3 questions x 20 marks = 60 marks (STUDENT CHOOSES 2, answers 40 marks)
Paper Total: 8 questions, 100 marks available, 80 marks answered

IMPORTANT: The paper must have 100 marks, but students only answer 80 marks
"""

import random
import time
from collections import defaultdict
from typing import List, Dict, Optional

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Paper, Topic, Question, Subject


class KCSEBiologyPaper2Generator:
    """
    KCSE Biology Paper 2 Generator - Correct Format
    Section A: 5 x 8-mark questions = 40 marks (all compulsory)
    Section B: 3 x 20-mark questions = 60 marks (choose 2, answer 40 marks)
    Paper Total: 100 marks available, 80 marks to be answered
    """
    
    # Section A Requirements (ALL COMPULSORY)
    SECTION_A_QUESTIONS = 5
    SECTION_A_MARKS_EACH = 8
    SECTION_A_TOTAL_MARKS = 40
    
    # Section B Requirements (CHOOSE 2 OUT OF 3)
    SECTION_B_QUESTIONS = 3
    SECTION_B_MARKS_EACH = 20
    SECTION_B_AVAILABLE_MARKS = 60  # Total marks available in Section B
    SECTION_B_ANSWERED_MARKS = 40   # Marks student will answer (2 × 20)
    
    # Paper Totals
    TOTAL_QUESTIONS = 8
    PAPER_TOTAL_MARKS = 100  # Total marks on paper
    STUDENT_ANSWERS_MARKS = 80  # Total marks student answers
    
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
            # Use is_graph field for graph questions
            is_graph = getattr(q, 'is_graph', False)
            
            # Section A: 8-mark questions
            if ("SECTION A" in section_name or "SECTION 1" in section_name) and q.marks == 8:
                self.section_a_8mark.append(q)
            # Section B: 20-mark questions (separate by is_graph field)
            elif ("SECTION B" in section_name or "SECTION 2" in section_name) and q.marks == 20:
                if is_graph:
                    self.section_b_20mark_graph.append(q)
                else:
                    self.section_b_20mark_essay.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.section_a_8mark)
        random.shuffle(self.section_b_20mark_graph)
        random.shuffle(self.section_b_20mark_essay)
        
        print(f"\n[DATA LOADED - BIOLOGY PAPER 2]")
        print(f"  Section A (All Compulsory):")
        print(f"    8-mark: {len(self.section_a_8mark)} available (need {self.SECTION_A_QUESTIONS})")
        print(f"  Section B (Choose 2 out of 3):")
        print(f"    20-mark (Graph): {len(self.section_b_20mark_graph)}")
        print(f"    20-mark (Essay): {len(self.section_b_20mark_essay)}")
        print(f"    Total 20-mark: {len(self.section_b_20mark_graph) + len(self.section_b_20mark_essay)} (need {self.SECTION_B_QUESTIONS})")
        
        # Check if we have enough questions
        total_20mark = len(self.section_b_20mark_graph) + len(self.section_b_20mark_essay)
        if len(self.section_a_8mark) < self.SECTION_A_QUESTIONS:
            raise ValueError(
                f"Insufficient Section A questions: have {len(self.section_a_8mark)}, need {self.SECTION_A_QUESTIONS}"
            )
        if total_20mark < self.SECTION_B_QUESTIONS:
            raise ValueError(
                f"Insufficient Section B questions: have {total_20mark}, need {self.SECTION_B_QUESTIONS}"
            )
    
    def _select_section_a(self) -> bool:
        """Select Section A questions: 5 x 8-mark (all compulsory)"""
        # Check availability
        available = [q for q in self.section_a_8mark if q.id not in self.used_ids]
        
        if len(available) < self.SECTION_A_QUESTIONS:
            return False
        
        # Select exactly 5 questions
        selected = available[:self.SECTION_A_QUESTIONS]
        
        # Verify total
        total_marks = sum(q.marks for q in selected)
        if len(selected) != self.SECTION_A_QUESTIONS or total_marks != self.SECTION_A_TOTAL_MARKS:
            print(f"  Section A validation failed: {len(selected)} questions, {total_marks} marks")
            return False
        
        # Accept selection
        self.selected_section_a = selected
        for q in selected:
            self.used_ids.add(q.id)
        
        print(f"\n[SECTION A SELECTED]")
        print(f"  Questions: {len(selected)} (all compulsory)")
        print(f"  Total marks: {total_marks}")
        
        return True
    
    def _select_section_b(self) -> bool:
        """
        Select Section B questions: 3 x 20-mark (student chooses 2)
        Structure: Prefer 1 Graph (Question 6) + 2 Essays (Questions 7-8)
        Fallback: Use 3 Essays if no graph available
        """
        # Get available questions
        available_graph = [q for q in self.section_b_20mark_graph if q.id not in self.used_ids]
        available_essay = [q for q in self.section_b_20mark_essay if q.id not in self.used_ids]
        
        selected = []
        
        # Strategy 1: Try to get 1 graph + 2 essays (PREFERRED)
        if len(available_graph) >= 1 and len(available_essay) >= 2:
            selected.append(available_graph[0])
            selected.extend(available_essay[:2])
            print(f"  Section B Strategy: 1 Graph (Q6) + 2 Essays (Q7, Q8)")
        
        # Strategy 2: Use 3 essays if no graph available (FALLBACK)
        elif len(available_essay) >= 3:
            selected.extend(available_essay[:3])
            print(f"  Section B Strategy: 3 Essays (Q6, Q7, Q8) - no graph available")
        
        # Strategy 3: Not enough questions
        else:
            print(f"  Section B FAILED: Need 3 questions, have {len(available_graph)} graphs + {len(available_essay)} essays")
            return False
        
        # Verify: must have exactly 3 questions, each worth 20 marks (total 60 marks)
        total_marks = sum(q.marks for q in selected)
        if len(selected) != self.SECTION_B_QUESTIONS:
            print(f"  Section B FAILED: Got {len(selected)} questions, need {self.SECTION_B_QUESTIONS}")
            return False
        
        if total_marks != self.SECTION_B_AVAILABLE_MARKS:
            print(f"  Section B FAILED: Got {total_marks} marks, need {self.SECTION_B_AVAILABLE_MARKS}")
            print(f"    Individual question marks: {[q.marks for q in selected]}")
            return False
        
        # Accept selection
        self.selected_section_b = selected
        for q in selected:
            self.used_ids.add(q.id)
        
        # Count question types
        graph_count = sum(1 for q in selected if q in self.section_b_20mark_graph)
        essay_count = sum(1 for q in selected if q in self.section_b_20mark_essay)
        
        print(f"\n[SECTION B SELECTED]")
        print(f"  Questions: {len(selected)} (student chooses 2)")
        print(f"    Question 6: {'Graph' if graph_count > 0 else 'Essay'}")
        print(f"    Questions 7-8: Essays")
        print(f"  Total marks available: {total_marks}")
        print(f"  Marks to be answered: {self.SECTION_B_ANSWERED_MARKS} (2 out of 3 questions)")
        
        return True
    
    def generate(self) -> Dict:
        """Generate Biology Paper 2"""
        max_attempts = 100
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE BIOLOGY PAPER 2 GENERATION")
        print(f"{'='*70}")
        print(f"Structure:")
        print(f"  Section A: 5 x 8 marks = 40 marks (ALL COMPULSORY)")
        print(f"  Section B: 3 x 20 marks = 60 marks (CHOOSE 2, ANSWER 40 marks)")
        print(f"  Paper Total: 100 marks available, 80 marks to be answered")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_section_a = []
            self.selected_section_b = []
            self.selected_question_ids = []
            self.used_ids = set()
            
            # Select Section A (5 × 8-mark, all compulsory)
            if not self._select_section_a():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section A selection")
                continue
            
            # Select Section B (3 × 20-mark, choose 2)
            if not self._select_section_b():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section B selection")
                continue
            
            # Success!
            generation_time = time.time() - start_time
            
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
            print(f"  Section A: {len(self.selected_section_a)} questions × 8 marks = {section_a_marks} marks")
            print(f"  Section B: {len(self.selected_section_b)} questions × 20 marks = {section_b_marks} marks")
            print(f"  Paper Total: {paper_total_marks} marks available")
            print(f"  Student Answers: {section_a_marks + self.SECTION_B_ANSWERED_MARKS} marks")
            
            # Validate paper structure
            if total_questions != self.TOTAL_QUESTIONS:
                print(f"\nERROR: Total questions is {total_questions}, expected {self.TOTAL_QUESTIONS}")
                continue
            
            if paper_total_marks != self.PAPER_TOTAL_MARKS:
                print(f"\nERROR: Paper total is {paper_total_marks} marks, expected {self.PAPER_TOTAL_MARKS}")
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
        
        # Combine sections in strict order: Section A (1-5), then Section B (6-8)
        all_questions = self.selected_section_a + self.selected_section_b
        
        # Build questions data with proper numbering
        questions_data = []
        for idx, question in enumerate(all_questions, start=1):
            self.selected_question_ids.append(str(question.id))
            
            # Determine section
            section_letter = "A" if idx <= 5 else "B"
            is_compulsory = idx <= 5  # Section A is all compulsory
            
            questions_data.append({
                'id': str(question.id),
                'question_number': idx,
                'section_letter': section_letter,
                'is_compulsory': is_compulsory,
                'instruction': 'Compulsory' if is_compulsory else 'Choose ANY TWO questions from this section',
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
        
        # Check if Question 6 is a graph
        has_graph_at_q6 = (len(self.selected_section_b) > 0 and 
                          self.selected_section_b[0] in self.section_b_20mark_graph)
        
        # Calculate marks
        section_a_marks = sum(q.marks for q in self.selected_section_a)
        section_b_marks = sum(q.marks for q in self.selected_section_b)
        
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
                'section_b': 'Answer ANY TWO questions from this section'
            },
            'questions': questions_data,
            'question_ids': self.selected_question_ids,
            'statistics': {
                'total_questions': len(all_questions),
                'paper_total_marks': section_a_marks + section_b_marks,
                'student_answers_marks': section_a_marks + self.SECTION_B_ANSWERED_MARKS,
                'section_a': {
                    'questions': len(self.selected_section_a),
                    'marks': section_a_marks,
                    'instruction': 'All compulsory'
                },
                'section_b': {
                    'questions': len(self.selected_section_b),
                    'available_marks': section_b_marks,
                    'answered_marks': self.SECTION_B_ANSWERED_MARKS,
                    'instruction': 'Choose 2 out of 3',
                    'graph_questions': section_b_graph_count,
                    'essay_questions': section_b_essay_count,
                    'question_6_is_graph': has_graph_at_q6,
                },
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': {
                    'section_a_ok': len(self.selected_section_a) == 5 and section_a_marks == 40,
                    'section_b_ok': len(self.selected_section_b) == 3 and section_b_marks == 60,
                    'total_questions_ok': len(all_questions) == 8,
                    'paper_total_marks_ok': (section_a_marks + section_b_marks) == 100,
                    'student_answers_marks_ok': (section_a_marks + self.SECTION_B_ANSWERED_MARKS) == 80,
                }
            }
        }


@require_http_methods(["POST"])
def validate_paper2_pool(request):
    """
    Validate if there are enough questions in the pool to generate Paper 2
    
    Returns validation for correct KCSE format:
    - Section A: 5 x 8 marks (all compulsory)
    - Section B: 3 x 20 marks (choose 2)
    """
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('selected_topics', [])
        
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
        
        # Count questions by type
        section_a_8mark_count = 0
        section_b_20mark_graph_count = 0
        section_b_20mark_essay_count = 0
        
        for q in all_questions:
            section_name = q.section.name.upper() if q.section else ""
            is_graph = getattr(q, 'is_graph', False)
            
            if ("SECTION A" in section_name or "SECTION 1" in section_name) and q.marks == 8:
                section_a_8mark_count += 1
            elif ("SECTION B" in section_name or "SECTION 2" in section_name) and q.marks == 20:
                if is_graph:
                    section_b_20mark_graph_count += 1
                else:
                    section_b_20mark_essay_count += 1
        
        # Validate
        section_b_20mark_total = section_b_20mark_graph_count + section_b_20mark_essay_count
        section_a_ok = section_a_8mark_count >= 5
        section_b_ok = section_b_20mark_total >= 3
        can_generate = section_a_ok and section_b_ok
        
        # Build message
        issues = []
        if not section_a_ok:
            issues.append(f"Section A: Need 5 x 8-mark, have {section_a_8mark_count}")
        if not section_b_ok:
            issues.append(f"Section B: Need 3 x 20-mark, have {section_b_20mark_total}")
        
        message = "Ready to generate Paper 2" if can_generate else "Insufficient questions: " + "; ".join(issues)
        
        return JsonResponse({
            'can_generate': can_generate,
            'available_counts': {
                'section_a_8mark': section_a_8mark_count,
                'section_b_20mark_graph': section_b_20mark_graph_count,
                'section_b_20mark_essay': section_b_20mark_essay_count,
                'section_b_20mark_total': section_b_20mark_total,
            },
            'required_counts': {
                'section_a_8mark': 5,
                'section_b_20mark': 3,
            },
            'paper_structure': {
                'section_a': '5 questions x 8 marks = 40 marks (ALL COMPULSORY)',
                'section_b': '3 questions x 20 marks = 60 marks (CHOOSE 2, ANSWER 40 marks)',
                'paper_total': '100 marks available',
                'student_answers': '80 marks'
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
def generate_biology_paper2(request):
    """Generate KCSE Biology Paper 2"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('selected_topics', [])
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
        
        # Initialize generator
        generator = KCSEBiologyPaper2Generator(
            paper_id=paper_id,
            selected_topic_ids=selected_topic_ids
        )
        
        # Load data and generate
        generator.load_data()
        result = generator.generate()
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        return JsonResponse({
            'message': f'Generation error: {str(e)}'
        }, status=500)