"""
KCSE Geography Paper 1 & 2 Generator
Both papers follow similar structure with key differences in Section B

PAPER 1:
- Section A: 5-6 questions totaling 25 marks (ALL COMPULSORY)
- Section B: 5 questions x 25 marks = 125 marks (Question 6 MUST be MAP if available)
- Paper Total: 10-11 questions, 150 marks

PAPER 2:
- Section A: 5-6 questions totaling 25 marks (ALL COMPULSORY)
- Section B: 5 questions x 25 marks = 125 marks (No map priority for Question 6)
- Paper Total: 10-11 questions, 150 marks
"""

import random
import time
from collections import defaultdict
from typing import List, Dict, Optional
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Paper, Topic, Question, Subject, GeneratedPaper


class KCSEGeographyPaperGenerator:
    """
    Base class for Geography Paper generation
    Handles common logic for both Paper 1 and Paper 2
    """
    
    # Section A Requirements (ALL COMPULSORY)
    SECTION_A_MIN_QUESTIONS = 5
    SECTION_A_MAX_QUESTIONS = 6
    SECTION_A_TOTAL_MARKS = 25
    
    # Section B Requirements (ALL COMPULSORY)
    SECTION_B_QUESTIONS = 5
    SECTION_B_MARKS_EACH = 25
    SECTION_B_TOTAL_MARKS = 125
    
    # Paper Totals
    PAPER_TOTAL_MARKS = 150
    
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
        self.section_a_questions = []  # Mixed marks questions for Section A
        self.section_b_25mark_map = []  # Map questions (25 marks)
        self.section_b_25mark_regular = []  # Regular 25-mark questions
        
        # Selection tracking
        self.selected_section_a = []
        self.selected_section_b = []
        self.selected_question_ids = []
        self.used_ids = set()
        
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
        
        # Separate questions by section and type
        for q in self.all_questions:
            section_name = q.section.name.upper() if q.section else ""
            is_map = getattr(q, 'is_map', False)
            
            # Section A: Questions with various marks (2-10 marks typically)
            if ("SECTION A" in section_name or "SECTION 1" in section_name):
                if q.marks < 25:  # Section A questions should be less than 25 marks
                    self.section_a_questions.append(q)
            
            # Section B: 25-mark questions
            elif ("SECTION B" in section_name or "SECTION 2" in section_name) and q.marks == 25:
                if is_map:
                    self.section_b_25mark_map.append(q)
                else:
                    self.section_b_25mark_regular.append(q)
        
        # Shuffle for randomness
        random.shuffle(self.section_a_questions)
        random.shuffle(self.section_b_25mark_map)
        random.shuffle(self.section_b_25mark_regular)
        
        print(f"\n[DATA LOADED - GEOGRAPHY PAPER {self.get_paper_number()}]")
        print(f"  Section A (All Compulsory):")
        print(f"    Mixed marks questions: {len(self.section_a_questions)} available")
        print(f"    (Need {self.SECTION_A_MIN_QUESTIONS}-{self.SECTION_A_MAX_QUESTIONS} questions totaling {self.SECTION_A_TOTAL_MARKS} marks)")
        print(f"  Section B (All Compulsory):")
        print(f"    25-mark (Map): {len(self.section_b_25mark_map)}")
        print(f"    25-mark (Regular): {len(self.section_b_25mark_regular)}")
        print(f"    (Need {self.SECTION_B_QUESTIONS} questions)")
        
        # Check if we have enough questions
        total_25mark = len(self.section_b_25mark_map) + len(self.section_b_25mark_regular)
        if len(self.section_a_questions) < self.SECTION_A_MIN_QUESTIONS:
            raise ValueError(
                f"Insufficient Section A questions: have {len(self.section_a_questions)}, "
                f"need at least {self.SECTION_A_MIN_QUESTIONS}"
            )
        if total_25mark < self.SECTION_B_QUESTIONS:
            raise ValueError(
                f"Insufficient Section B questions: have {total_25mark}, need {self.SECTION_B_QUESTIONS}"
            )
    
    def _select_section_a(self) -> bool:
        """
        Select Section A questions: 5-6 questions totaling exactly 25 marks
        Uses a combination approach to reach exactly 25 marks
        """
        available = [q for q in self.section_a_questions if q.id not in self.used_ids]
        
        if len(available) < self.SECTION_A_MIN_QUESTIONS:
            return False
        
        # Try to find a combination that sums to exactly 25 marks
        # with 5-6 questions
        for num_questions in range(self.SECTION_A_MIN_QUESTIONS, self.SECTION_A_MAX_QUESTIONS + 1):
            if len(available) < num_questions:
                continue
            
            # Try different combinations
            for attempt in range(50):  # Try 50 random combinations
                selected = random.sample(available, num_questions)
                total_marks = sum(q.marks for q in selected)
                
                if total_marks == self.SECTION_A_TOTAL_MARKS:
                    # Found valid combination!
                    self.selected_section_a = selected
                    for q in selected:
                        self.used_ids.add(q.id)
                    
                    print(f"\n[SECTION A SELECTED]")
                    print(f"  Questions: {len(selected)} (all compulsory)")
                    print(f"  Total marks: {total_marks}")
                    print(f"  Question marks: {[q.marks for q in selected]}")
                    
                    return True
        
        return False
    
    def _select_section_b(self) -> bool:
        """
        Select Section B questions - MUST be implemented by subclass
        Paper 1: Question 6 MUST be map (if available)
        Paper 2: Question 6 is selected randomly (no map priority)
        """
        raise NotImplementedError("Subclass must implement _select_section_b")
    
    def get_paper_number(self) -> int:
        """Return paper number (1 or 2) - to be implemented by subclass"""
        raise NotImplementedError("Subclass must implement get_paper_number")
    
    def generate(self) -> Dict:
        """Generate Geography Paper"""
        max_attempts = 100
        self.generation_start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE GEOGRAPHY PAPER {self.get_paper_number()} GENERATION")
        print(f"{'='*70}")
        print(f"Structure:")
        print(f"  Section A: 5-6 questions = 25 marks (ALL COMPULSORY)")
        print(f"  Section B: 5 questions X 25 marks = 125 marks (ALL COMPULSORY)")
        print(f"  Paper Total: 150 marks")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_section_a = []
            self.selected_section_b = []
            self.selected_question_ids = []
            self.used_ids = set()
            
            # Select Section A (5-6 questions, 25 marks total)
            if not self._select_section_a():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at Section A selection")
                continue
            
            # Select Section B (5 X 25-mark)
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
            print(f"  Section B: {len(self.selected_section_b)} questions X 25 marks = {section_b_marks} marks")
            print(f"  Paper Total: {paper_total_marks} marks")
            
            # Validate paper structure
            if section_a_marks != self.SECTION_A_TOTAL_MARKS:
                print(f"\nERROR: Section A marks is {section_a_marks}, expected {self.SECTION_A_TOTAL_MARKS}")
                continue
            
            if section_b_marks != self.SECTION_B_TOTAL_MARKS:
                print(f"\nERROR: Section B marks is {section_b_marks}, expected {self.SECTION_B_TOTAL_MARKS}")
                continue
            
            if paper_total_marks != self.PAPER_TOTAL_MARKS:
                print(f"\nERROR: Paper total is {paper_total_marks} marks, expected {self.PAPER_TOTAL_MARKS}")
                continue
            
            return self._build_result(generation_time)
        
        # Failed
        raise Exception(
            f"Failed to generate paper after {max_attempts} attempts. "
            f"Available: Section A={len(self.section_a_questions)}, "
            f"25-mark map={len(self.section_b_25mark_map)}, "
            f"25-mark regular={len(self.section_b_25mark_regular)}"
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with strictly ordered sections"""
        
        # Combine sections in strict order: Section A, then Section B
        all_questions = self.selected_section_a + self.selected_section_b
        
        # Build questions data with proper numbering
        questions_data = []
        section_a_count = len(self.selected_section_a)
        
        for idx, question in enumerate(all_questions, start=1):
            self.selected_question_ids.append(str(question.id))
            
            # Determine section
            section_letter = "A" if idx <= section_a_count else "B"
            is_compulsory = True  # All questions are compulsory in Geography
            
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
                'is_map': getattr(question, 'is_map', False),
            })
        
        # Count map questions in Section B
        section_b_map_count = sum(1 for q in self.selected_section_b 
                                  if q in self.section_b_25mark_map)
        
        # Check if Question 6 is a map (first question in Section B)
        has_map_at_q6 = (len(self.selected_section_b) > 0 and 
                        self.selected_section_b[0] in self.section_b_25mark_map)
        
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
        
        # Build validation report
        validation_report = {
            'all_passed': True,
            'checks': {
                'section_a_count': self.SECTION_A_MIN_QUESTIONS <= len(self.selected_section_a) <= self.SECTION_A_MAX_QUESTIONS,
                'section_a_marks': section_a_marks == self.SECTION_A_TOTAL_MARKS,
                'section_b_count': len(self.selected_section_b) == self.SECTION_B_QUESTIONS,
                'section_b_marks': section_b_marks == self.SECTION_B_TOTAL_MARKS,
                'paper_total_marks': (section_a_marks + section_b_marks) == self.PAPER_TOTAL_MARKS,
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
                    'question_marks': [q.marks for q in self.selected_section_a],
                    'instruction': 'All compulsory'
                },
                'section_b': {
                    'questions': len(self.selected_section_b),
                    'marks': section_b_marks,
                    'instruction': 'All compulsory',
                    'map_questions': section_b_map_count,
                    'question_6_is_map': has_map_at_q6,
                },
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': validation_report['checks']
            }
        }


class KCSEGeographyPaper1Generator(KCSEGeographyPaperGenerator):
    """
    Geography Paper 1 Generator
    Section B: Question 6 (first question) MUST be a MAP question if available
    """
    
    def get_paper_number(self) -> int:
        return 1
    
    def _select_section_b(self) -> bool:
        """
        Select Section B questions: 5 X 25-mark (all compulsory)
        CRITICAL: Question 6 (first question) MUST be MAP if available
        """
        available_map = [q for q in self.section_b_25mark_map if q.id not in self.used_ids]
        available_regular = [q for q in self.section_b_25mark_regular if q.id not in self.used_ids]
        
        selected = []
        
        # Strategy 1: MAP question as Question 6 + 4 regular questions (PREFERRED)
        if len(available_map) >= 1 and len(available_regular) >= 4:
            selected.append(available_map[0])  # Question 6 = MAP
            selected.extend(available_regular[:4])  # Questions 7-10 = Regular
            print(f"  Section B Strategy: 1 MAP (Q6) + 4 Regular (Q7-Q10)")
        
        # Strategy 2: Use 5 regular questions if no map available (FALLBACK)
        elif len(available_regular) >= 5:
            selected.extend(available_regular[:5])
            print(f"  Section B Strategy: 5 Regular (Q6-Q10) - no map available")
        
        # Strategy 3: Not enough questions
        else:
            print(f"  Section B FAILED: Need 5 questions, have {len(available_map)} maps + {len(available_regular)} regular")
            return False
        
        # Verify: must have exactly 5 questions, each worth 25 marks
        total_marks = sum(q.marks for q in selected)
        if len(selected) != self.SECTION_B_QUESTIONS:
            print(f"  Section B FAILED: Got {len(selected)} questions, need {self.SECTION_B_QUESTIONS}")
            return False
        
        if total_marks != self.SECTION_B_TOTAL_MARKS:
            print(f"  Section B FAILED: Got {total_marks} marks, need {self.SECTION_B_TOTAL_MARKS}")
            return False
        
        # Accept selection
        self.selected_section_b = selected
        for q in selected:
            self.used_ids.add(q.id)
        
        # Count question types
        map_count = sum(1 for q in selected if q in self.section_b_25mark_map)
        
        print(f"\n[SECTION B SELECTED]")
        print(f"  Questions: {len(selected)} (all compulsory)")
        print(f"    Question 6: {'MAP' if map_count > 0 and selected[0] in self.section_b_25mark_map else 'Regular'}")
        print(f"    Questions 7-10: Regular")
        print(f"  Total marks: {total_marks}")
        
        return True


class KCSEGeographyPaper2Generator(KCSEGeographyPaperGenerator):
    """
    Geography Paper 2 Generator
    Section B: NO map priority for Question 6 - all questions selected randomly
    """
    
    def get_paper_number(self) -> int:
        return 2
    
    def _select_section_b(self) -> bool:
        """
        Select Section B questions: 5 X 25-mark (all compulsory)
        NO MAP PRIORITY - Question 6 selected randomly like other questions
        """
        available_map = [q for q in self.section_b_25mark_map if q.id not in self.used_ids]
        available_regular = [q for q in self.section_b_25mark_regular if q.id not in self.used_ids]
        
        # Combine all available 25-mark questions (no priority)
        all_available = available_map + available_regular
        
        if len(all_available) < self.SECTION_B_QUESTIONS:
            print(f"  Section B FAILED: Need {self.SECTION_B_QUESTIONS} questions, have {len(all_available)}")
            return False
        
        # Select 5 questions randomly (no map priority)
        selected = all_available[:self.SECTION_B_QUESTIONS]
        
        # Verify: must have exactly 5 questions, each worth 25 marks
        total_marks = sum(q.marks for q in selected)
        if len(selected) != self.SECTION_B_QUESTIONS:
            print(f"  Section B FAILED: Got {len(selected)} questions, need {self.SECTION_B_QUESTIONS}")
            return False
        
        if total_marks != self.SECTION_B_TOTAL_MARKS:
            print(f"  Section B FAILED: Got {total_marks} marks, need {self.SECTION_B_TOTAL_MARKS}")
            return False
        
        # Accept selection
        self.selected_section_b = selected
        for q in selected:
            self.used_ids.add(q.id)
        
        # Count question types
        map_count = sum(1 for q in selected if q in self.section_b_25mark_map)
        
        print(f"\n[SECTION B SELECTED - PAPER 2]")
        print(f"  Questions: {len(selected)} (all compulsory)")
        print(f"  Map questions: {map_count}")
        print(f"  Regular questions: {len(selected) - map_count}")
        print(f"  Total marks: {total_marks}")
        print(f"  Note: No map priority for Question 6 in Paper 2")
        
        return True


# Django Views

@require_http_methods(["POST"])
def validate_geography_paper_pool(request):
    """Validate if there are enough questions to generate Geography paper"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('selected_topics', [])
        paper_number = data.get('paper_number', 1)  # 1 or 2
        
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
        section_a_count = 0
        section_b_25mark_map_count = 0
        section_b_25mark_regular_count = 0
        
        for q in all_questions:
            section_name = q.section.name.upper() if q.section else ""
            is_map = getattr(q, 'is_map', False)
            
            if ("SECTION A" in section_name or "SECTION 1" in section_name) and q.marks < 25:
                section_a_count += 1
            elif ("SECTION B" in section_name or "SECTION 2" in section_name) and q.marks == 25:
                if is_map:
                    section_b_25mark_map_count += 1
                else:
                    section_b_25mark_regular_count += 1
        
        # Validate
        section_b_25mark_total = section_b_25mark_map_count + section_b_25mark_regular_count
        section_a_ok = section_a_count >= 5
        section_b_ok = section_b_25mark_total >= 5
        can_generate = section_a_ok and section_b_ok
        
        # Build message
        issues = []
        if not section_a_ok:
            issues.append(f"Section A: Need 5-6 questions, have {section_a_count}")
        if not section_b_ok:
            issues.append(f"Section B: Need 5 X 25-mark, have {section_b_25mark_total}")
        
        message = f"Ready to generate Geography Paper {paper_number}" if can_generate else "Insufficient questions: " + "; ".join(issues)
        
        # Add paper-specific notes
        paper_notes = ""
        if paper_number == 1:
            paper_notes = "Note: Question 6 will be MAP question if available"
        else:
            paper_notes = "Note: No map priority for Question 6"
        
        return JsonResponse({
            'can_generate': can_generate,
            'available_counts': {
                'section_a_questions': section_a_count,
                'section_b_25mark_map': section_b_25mark_map_count,
                'section_b_25mark_regular': section_b_25mark_regular_count,
                'section_b_25mark_total': section_b_25mark_total,
            },
            'required_counts': {
                'section_a_questions': '5-6',
                'section_b_25mark': 5,
            },
            'paper_structure': {
                'section_a': '5-6 questions = 25 marks (ALL COMPULSORY)',
                'section_b': '5 questions X 25 marks = 125 marks (ALL COMPULSORY)',
                'paper_total': '150 marks',
                'paper_specific_note': paper_notes
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
def generate_geography_paper(request):
    """Generate KCSE Geography Paper 1 or 2"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('selected_topics', [])
        paper_number = data.get('paper_number', 1)  # 1 or 2
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
        
        if paper_number not in [1, 2]:
            return JsonResponse({
                'message': 'Invalid paper_number. Must be 1 or 2'
            }, status=400)
        
        # Get user from request if available
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Generate unique code
        timestamp = datetime.now().strftime('%y%m%d%H%M%S')
        unique_code = f"GEO{paper_number}-{timestamp}"
        
        # Initialize appropriate generator
        if paper_number == 1:
            generator = KCSEGeographyPaper1Generator(
                paper_id=paper_id,
                selected_topic_ids=selected_topic_ids,
                user=user
            )
        else:
            generator = KCSEGeographyPaper2Generator(
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
            'total_marks': result['statistics']['paper_total_marks'],
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