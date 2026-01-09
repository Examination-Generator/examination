"""
KCSE Christian Religious Education (CRE) Paper 1 & 2 Generator

PAPER 1 & PAPER 2:
- 6 questions available
- Student answers 5 out of 6
- Each question: 20 marks
- Total: 100 marks

SELECTION LOGIC:
1. HIGH PRIORITY: If 6 topics selected -> Pick ONE question from EACH topic (maximum diversity)
2. FALLBACK: If fewer topics selected -> Distribute 6 questions across available topics
   - 1 topic -> All 6 questions from same topic
   - 2-5 topics -> Spread questions across topics (may reuse topics)
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
from .page_number_extrctor import extract_paper_number_from_name

class KCSECREPaperGenerator:
    """
    CRE Paper 1 & 2 Generator (same logic for both papers)
    - 6 questions total
    - Each question: 20 marks
    - Student answers 5 out of 6
    - Total: 100 marks
    
    Selection Logic:
    - If 6 topics selected: Pick ONE question from EACH topic (high priority)
    - If fewer topics: Distribute 6 questions across available topics
    """
    
    QUESTIONS_NEEDED = 6
    MARKS_PER_QUESTION = 20
    STUDENT_ANSWERS = 5
    TOTAL_MARKS = 100
    
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
        
        # Question pools by topic
        self.questions_by_topic = {}  # topic_id -> [questions]
        
        # Topic ordering map (populated during load_data)
        self.topic_order_map = {}  # topic_id -> order_index
        
        # Selection tracking
        self.selected_questions = []
        self.selected_question_ids = []
        self.used_topic_ids = []
        
        # Statistics
        self.attempts = 0
        self.generation_start_time = None
        self.selection_strategy = None
    
    def _get_topic_order(self, topic) -> int:
        """Get the order index for a topic from the topic_order_map.
        Uses the topic's ID to look up its order.
        Returns the mapped order or 999 if not found.
        """
        topic_id = str(topic.id)
        return self.topic_order_map.get(topic_id, 999)
    
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
        
        # Build topic order map based on topic names (fixed order for CRE Paper 1)
        # Order: Bible/Creation -> Abraham/Moses -> Kingship/Elijah -> 
        #        Amos/Prophetic -> Nehemiah/Jeremiah -> African Culture
        topic_order_keywords = [
            ['bible', 'creation'],           # 1. Bible/Creation
            ['abraham', 'moses'],            # 2. Abraham/Moses
            ['kingship', 'elijah'],          # 3. Kingship/Elijah
            ['amos', 'prophetic'],           # 4. Amos/Prophetic messages
            ['nehemiah', 'jeremiah'],        # 5. Nehemiah/Jeremiah
            ['african', 'culture']           # 6. African culture
        ]
        
        for topic in self.topics:
            topic_lower = topic.name.lower()
            topic_id = str(topic.id)
            
            # Find matching order based on keywords
            order_found = False
            for order_index, keywords in enumerate(topic_order_keywords):
                if any(keyword in topic_lower for keyword in keywords):
                    self.topic_order_map[topic_id] = order_index
                    order_found = True
                    break
            
            # If no match, assign high number to place at end
            if not order_found:
                self.topic_order_map[topic_id] = 999
        
        # Load ALL questions for selected topics
        self.all_questions = list(Question.objects.filter(
            subject=self.subject,
            paper=self.paper,
            topic__in=self.topics,
            is_active=True
        ).select_related('topic', 'section'))
        
        if not self.all_questions:
            raise ValueError("No questions found for selected topics")
        
        # Group questions by topic
        for q in self.all_questions:
            topic_id = str(q.topic_id)
            if topic_id not in self.questions_by_topic:
                self.questions_by_topic[topic_id] = []
            self.questions_by_topic[topic_id].append(q)
        
        # Shuffle questions within each topic
        for topic_id in self.questions_by_topic:
            random.shuffle(self.questions_by_topic[topic_id])
        
        print(f"\n[DATA LOADED - CRE PAPER]")
        print(f"  Topics selected: {len(self.topics)}")
        print(f"  Total questions: {len(self.all_questions)}")
        print(f"  Questions by topic:")
        for topic in self.topics:
            topic_id = str(topic.id)
            count = len(self.questions_by_topic.get(topic_id, []))
            print(f"    - {topic.name}: {count} questions")
    
    def _select_questions(self) -> bool:
        """
        Select 6 questions based on available topics
        
        Strategy:
        1. If 6 topics: Pick ONE question from EACH topic (high priority)
        2. If fewer topics: Distribute 6 questions across available topics
        """
        num_topics = len(self.topics)
        
        if num_topics == 6:
            # HIGH PRIORITY: One question per topic for maximum diversity
            self.selection_strategy = "one_per_topic"
            return self._select_one_per_topic()
        
        elif num_topics >= 1:
            # FALLBACK: Distribute questions across available topics
            self.selection_strategy = f"distributed_across_{num_topics}_topics"
            return self._select_distributed()
        
        else:
            print(f"  Selection FAILED: No topics available")
            return False
    
    def _select_one_per_topic(self) -> bool:
        """
        Select ONE question from EACH of the 6 topics
        High priority scenario for maximum topic diversity
        """
        selected = []
        
        # Shuffle topics for randomness
        shuffled_topics = list(self.topics)
        random.shuffle(shuffled_topics)
        
        for topic in shuffled_topics:
            topic_id = str(topic.id)
            available_questions = self.questions_by_topic.get(topic_id, [])
            
            if not available_questions:
                print(f"  Selection FAILED: No questions available for topic '{topic.name}'")
                return False
            
            # Pick one random question from this topic
            question = random.choice(available_questions)
            selected.append(question)
            self.used_topic_ids.append(topic_id)
        
        if len(selected) == self.QUESTIONS_NEEDED:
            self.selected_questions = selected
            print(f"\n[SELECTION STRATEGY: ONE PER TOPIC]")
            print(f"  Selected {len(selected)} questions from {len(self.topics)} different topics")
            for idx, q in enumerate(selected, start=1):
                print(f"    Q{idx}: Topic='{q.topic.name}', Marks={q.marks}")
            return True
        
        return False
    
    def _select_distributed(self) -> bool:
        """
        Distribute 6 questions across available topics
        May reuse topics if fewer than 6 topics are selected
        """
        selected = []
        num_topics = len(self.topics)
        
        # Calculate how many questions per topic (roughly equal distribution)
        questions_per_topic = self.QUESTIONS_NEEDED // num_topics
        remaining_questions = self.QUESTIONS_NEEDED % num_topics
        
        # Shuffle topics for randomness
        shuffled_topics = list(self.topics)
        random.shuffle(shuffled_topics)
        
        # Distribute questions
        for idx, topic in enumerate(shuffled_topics):
            topic_id = str(topic.id)
            available_questions = self.questions_by_topic.get(topic_id, [])
            
            if not available_questions:
                print(f"  Selection FAILED: No questions available for topic '{topic.name}'")
                return False
            
            # Calculate how many questions to pick from this topic
            num_to_pick = questions_per_topic
            if idx < remaining_questions:
                num_to_pick += 1  # Distribute remaining questions to first few topics
            
            # Ensure we don't exceed available questions
            num_to_pick = min(num_to_pick, len(available_questions))
            
            # Pick questions from this topic
            topic_questions = random.sample(available_questions, num_to_pick)
            selected.extend(topic_questions)
            self.used_topic_ids.extend([topic_id] * num_to_pick)
            
            if len(selected) >= self.QUESTIONS_NEEDED:
                break
        
        # If we still need more questions, pick from any topic with available questions
        while len(selected) < self.QUESTIONS_NEEDED:
            for topic in shuffled_topics:
                topic_id = str(topic.id)
                available = self.questions_by_topic.get(topic_id, [])
                used_from_topic = sum(1 for q in selected if str(q.topic_id) == topic_id)
                
                if used_from_topic < len(available):
                    # Pick another question from this topic
                    unused = [q for q in available if q not in selected]
                    if unused:
                        question = random.choice(unused)
                        selected.append(question)
                        self.used_topic_ids.append(topic_id)
                        
                        if len(selected) >= self.QUESTIONS_NEEDED:
                            break
        
        if len(selected) == self.QUESTIONS_NEEDED:
            self.selected_questions = selected
            
            # Count questions per topic for reporting
            topic_counts = defaultdict(int)
            for q in selected:
                topic_counts[q.topic.name] += 1
            
            print(f"\n[SELECTION STRATEGY: DISTRIBUTED ACROSS {num_topics} TOPICS]")
            print(f"  Selected {len(selected)} questions distributed as:")
            for topic_name, count in topic_counts.items():
                print(f"    - {topic_name}: {count} questions")
            return True
        
        print(f"  Selection FAILED: Could only select {len(selected)} questions, need {self.QUESTIONS_NEEDED}")
        return False
    
    def generate(self) -> Dict:
        """Generate CRE Paper"""
        max_attempts = 100
        self.generation_start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE CRE PAPER GENERATION")
        print(f"{'='*70}")
        print(f"Structure:")
        print(f"  6 questions available")
        print(f"  Student answers 5 out of 6")
        print(f"  Each question: 20 marks")
        print(f"  Total: 100 marks")
        print(f"\nSelection Strategy:")
        print(f"  - If 6 topics selected > Pick ONE from EACH topic (high priority)")
        print(f"  - If fewer topics > Distribute 6 questions across available topics")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset state
            self.selected_questions = []
            self.selected_question_ids = []
            self.used_topic_ids = []
            
            # Select 6 questions
            if not self._select_questions():
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Failed at question selection")
                continue
            
            # Verify all questions are 20 marks
            if not all(q.marks == self.MARKS_PER_QUESTION for q in self.selected_questions):
                if attempt % 10 == 0:
                    print(f"[ATTEMPT {attempt}] Not all questions are {self.MARKS_PER_QUESTION} marks")
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
            f"Topics: {len(self.topics)}, Questions: {len(self.all_questions)}"
        )
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build result with paper structure"""
        
        # Sort questions by topic order (using topic_order_map)
        # Order: Bible/Creation -> Abraham/Moses -> Kingship/Elijah -> 
        #        Amos/Prophetic -> Nehemiah/Jeremiah -> African Culture
        self.selected_questions.sort(key=lambda q: self._get_topic_order(q.topic))
        
        # Build questions data
        questions_data = []
        
        for idx, q in enumerate(self.selected_questions, start=1):
            self.selected_question_ids.append(str(q.id))
            questions_data.append({
                'id': str(q.id),
                'question_number': idx,
                'is_compulsory': False,  # All questions are optional (answer 5 out of 6)
                'instruction': 'Answer any five questions',
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
        
        # Build validation report
        validation_report = {
            'all_passed': True,
            'checks': {
                'total_questions': len(self.selected_questions) == self.QUESTIONS_NEEDED,
                'all_20_marks': all(q.marks == self.MARKS_PER_QUESTION for q in self.selected_questions),
                'student_max_marks': self.STUDENT_ANSWERS * self.MARKS_PER_QUESTION == self.TOTAL_MARKS,
                'selection_strategy': self.selection_strategy,
            }
        }
        validation_report['all_passed'] = all(
            v for k, v in validation_report['checks'].items() if k != 'selection_strategy'
        )
        
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
                'main': f'Answer any {self.STUDENT_ANSWERS} questions',
                'details': f'All {self.QUESTIONS_NEEDED} questions carry equal marks ({self.MARKS_PER_QUESTION} marks each)'
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
                'total_questions_available': self.QUESTIONS_NEEDED,
                'student_answers': self.STUDENT_ANSWERS,
                'student_max_marks': self.TOTAL_MARKS,
                'marks_per_question': self.MARKS_PER_QUESTION,
                'topics_selected': len(self.topics),
                'selection_strategy': self.selection_strategy,
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2),
                'validation': validation_report['checks']
            }
        }


# Alias for Paper 1 and Paper 2 (same logic)
KCSECREPaper1Generator = KCSECREPaperGenerator
KCSECREPaper2Generator = KCSECREPaperGenerator


# Django Views

@require_http_methods(["POST"])
def validate_cre_paper_pool(request):
    """Validate if there are enough questions to generate CRE paper"""
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
        
        # Count questions by topic
        questions_by_topic = defaultdict(int)
        for q in all_questions:
            questions_by_topic[str(q.topic_id)] += 1
        
        # Check if we can generate
        num_topics = len(topics)
        total_questions = len(all_questions)
        
        # Need at least 6 questions total
        can_generate = total_questions >= 6
        
        # Build message
        if can_generate:
            if num_topics == 6:
                message = "Ready to generate CRE paper (HIGH PRIORITY: One question per topic)"
            elif num_topics == 1:
                message = f"Ready to generate CRE paper (All 6 questions from same topic)"
            else:
                message = f"Ready to generate CRE paper (6 questions distributed across {num_topics} topics)"
        else:
            message = f"Insufficient questions: Need at least 6 questions, have {total_questions}"
        
        return JsonResponse({
            'can_generate': can_generate,
            'available_counts': {
                'topics_selected': num_topics,
                'total_questions': total_questions,
                'questions_by_topic': dict(questions_by_topic),
            },
            'required_counts': {
                'questions_needed': 6,
            },
            'paper_structure': {
                'total_questions': 6,
                'student_answers': 5,
                'marks_per_question': 20,
                'total_marks': 100,
            },
            'selection_strategy': {
                'high_priority': 'If 6 topics selected > Pick ONE from EACH topic',
                'fallback': 'If fewer topics > Distribute 6 questions across available topics',
                'current': f'{num_topics} topics selected',
            },
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'can_generate': False,
            'message': f'Validation error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def generate_cre_paper(request):
    """Generate KCSE CRE Paper 1 or 2"""
    try:
        import json
        data = json.loads(request.body)
        
        paper_id = data.get('paper_id')
        selected_topic_ids = data.get('topic_ids', [])
        
        if not paper_id or not selected_topic_ids:
            return JsonResponse({
                'message': 'Missing paper_id or selected_topic_ids'
            }, status=400)
        
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Get paper name for unique code
        paper = Paper.objects.get(id=paper_id)
        paper_name = paper.name.upper()
        
        # Determine paper number (1 or 2)
        paper_number = extract_paper_number_from_name(paper_name)
        
        # Generate unique code
        timestamp = datetime.now().strftime('%y%m%d%H%M%S')
        unique_code = f"CRE{paper_number}-{timestamp}"
        
        # Initialize generator (same logic for Paper 1 and Paper 2)
        generator = KCSECREPaperGenerator(
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
            total_questions=result['statistics']['total_questions_available'],
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
            'total_questions': result['statistics']['total_questions_available'],
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
