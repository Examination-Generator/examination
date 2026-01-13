"""
KCSE English Papers Generator Suite
Based on actual KCSE 2020 exam structure analysis

PAPER 1 (Functional Skills) - 50 marks, 2 hours:
- Question 1: Functional Writing (20 marks) - Job application letter
- Question 2: Cloze Test (10 marks) - 10 blanks to fill
- Question 3: Oral Skills (20 marks) - Riddles, homophones, word stress, discussions, telephone etiquette

PAPER 2 (Comprehension, Literary Appreciation & Grammar) - 80 marks, 2.5 hours:
- Question 1: Comprehension (20 marks) - 1 passage with sub-questions
- Question 2: Excerpt from Set Text (25 marks) - Literature analysis
- Question 3: Poetry (20 marks) - Poem analysis
- Question 4: Grammar (15 marks) - Various grammar exercises

PAPER 3 (Creative Composition & Essays on Set Texts) - 60 marks, 2.5 hours:
- Question 1: Creative Writing (20 marks) - Story or composition
- Question 2: Compulsory Set Text Essay (20 marks) - A Doll's House
- Question 3: Optional Set Text Essay (20 marks) - Choose one: Short story/Drama/Novel
"""

import random
import time
from typing import List, Dict, Optional

from .models import Paper, Topic, Question, Subject


class KCSEEnglishPaper1Generator:
    """
    KCSE English Paper 1 - Functional Skills
    Q1: Functional Writing (20) + Q2: Cloze Test (10) + Q3: Oral Skills (30) = 60 marks
    """
    
    TOTAL_MARKS = 60
    Q1_FUNCTIONAL_WRITING_MARKS = 20
    Q2_CLOZE_TEST_MARKS = 10
    Q3_ORAL_SKILLS_MARKS = 30
    
    def __init__(self, paper_id: str, selections: Dict):
        """
        Initialize Paper 1 generator
        
        Args:
            paper_id: UUID of English Paper 1
            selections: Dict with optional filters for content variety
        """
        self.paper_id = paper_id
        self.selections = selections
        
        self.paper = None
        self.subject = None
        
        # Question pools
        self.functional_writing_tasks = []  # Job applications, letters, emails, memos
        self.cloze_test_passages = []       # Passages with blanks
        
        # Oral skills components
        self.riddles = []
        self.homophone_sets = []
        self.word_stress_sets = []
        self.discussion_scenarios = []
        self.telephone_scenarios = []
        
        # Alternative Question 3 formats (if no 30 marks combined sub-sections available)
        self.oral_30_marks_questions = []  # Single 30 marks oral skills question
        self.oral_20_marks_questions = []  # 20 marks oral questions (combine with 10)
        self.oral_15_marks_questions = []  # 15 marks oral questions (combine two)
        self.oral_10_marks_questions = []  # 10 marks oral questions (combine with 20)
        
        # Selected content
        self.selected_functional_task = None
        self.selected_cloze_passage = None
        self.selected_riddle = None
        self.selected_homophones = []
        self.selected_word_stress = []
        self.selected_discussion = None
        self.selected_telephone = None
        self.selected_oral_questions = []  # For alternative format
        
        self.attempts = 0
        self.total_marks = 0
    
    def load_data(self):
        """Load Paper 1 content from database"""
        self.paper = Paper.objects.select_related('subject').get(
            id=self.paper_id,
            is_active=True
        )
        self.subject = self.paper.subject
        
        # if 'English' not in self.subject.name or 'Paper 1' not in self.paper.name:
        #     raise ValueError("This generator is only for English Paper 1")
        
        # Get topic IDs from selections (if provided)
        selected_topic_ids = self.selections.get('topics', [])
        
        # Get topics - either from selections or all topics for this paper
        if selected_topic_ids:
            all_topics = Topic.objects.filter(
                id__in=selected_topic_ids,
                paper=self.paper,
                is_active=True
            )
        else:
            all_topics = Topic.objects.filter(
                paper=self.paper,
                is_active=True
            )
        
        # Categorize topics by checking their names
        functional_topics = []
        cloze_topics = []
        oral_topics = []
        
        # Sub-categories for oral skills (Question 3 sub-sections)
        riddle_topics = []
        homophone_topics = []
        word_stress_topics = []
        discussion_topics = []
        telephone_topics = []
        
        for topic in all_topics:
            topic_name_lower = topic.name.lower()
            
            # Main categories
            if 'functional' in topic_name_lower:
                functional_topics.append(topic)
            if 'cloze' in topic_name_lower:
                cloze_topics.append(topic)
            if 'oral' in topic_name_lower:
                oral_topics.append(topic)
            
            # Oral sub-categories (check for specific keywords)
            if 'riddle' in topic_name_lower:
                riddle_topics.append(topic)
            if 'homophone' in topic_name_lower:
                homophone_topics.append(topic)
            if 'stress' in topic_name_lower or 'word stress' in topic_name_lower:
                word_stress_topics.append(topic)
            if 'discussion' in topic_name_lower:
                discussion_topics.append(topic)
            if 'telephone' in topic_name_lower or 'phone' in topic_name_lower:
                telephone_topics.append(topic)
        
        # Q1: Functional Writing - select from functional topics
        functional_query = Question.objects.filter(
            paper=self.paper,
            is_active=True
        )
        if functional_topics:
            functional_query = functional_query.filter(topic__in=functional_topics)
        
        self.functional_writing_tasks = list(functional_query.select_related('topic'))
        
        # Q2: Cloze Test - select from cloze topics
        cloze_query = Question.objects.filter(
            paper=self.paper,
            is_active=True
        )
        if cloze_topics:
            cloze_query = cloze_query.filter(topic__in=cloze_topics)
        
        self.cloze_test_passages = list(cloze_query)
        
        # Q3a: Riddles - select from riddle topics (check topic name for 'riddle')
        riddles_query = Question.objects.filter(
            paper=self.paper,
            is_active=True
        )
        if riddle_topics:
            riddles_query = riddles_query.filter(topic__in=riddle_topics)
        elif oral_topics:
            # Fallback to general oral topics if no specific riddle topics
            riddles_query = riddles_query.filter(topic__in=oral_topics, question_type='riddle')
        
        self.riddles = list(riddles_query)
        
        # Q3b: Homophones - select from homophone topics (check topic name for 'homophone')
        homophones_query = Question.objects.filter(
            paper=self.paper,
            is_active=True
        )
        if homophone_topics:
            homophones_query = homophones_query.filter(topic__in=homophone_topics)
        elif oral_topics:
            # Fallback to general oral topics if no specific homophone topics
            homophones_query = homophones_query.filter(topic__in=oral_topics, question_type='homophones')
        
        self.homophone_sets = list(homophones_query)
        
        # Q3c: Word Stress - select from word stress topics (check topic name for 'stress')
        word_stress_query = Question.objects.filter(
            paper=self.paper,
            is_active=True
        )
        if word_stress_topics:
            word_stress_query = word_stress_query.filter(topic__in=word_stress_topics)
        elif oral_topics:
            # Fallback to general oral topics if no specific word stress topics
            word_stress_query = word_stress_query.filter(topic__in=oral_topics, question_type='word_stress')
        
        self.word_stress_sets = list(word_stress_query)
        
        # Q3d: Discussion Leadership - select from discussion topics (check topic name for 'discussion')
        discussion_query = Question.objects.filter(
            paper=self.paper,
            is_active=True
        )
        if discussion_topics:
            discussion_query = discussion_query.filter(topic__in=discussion_topics)
        elif oral_topics:
            # Fallback to general oral topics if no specific discussion topics
            discussion_query = discussion_query.filter(topic__in=oral_topics, question_type='discussion_skills')
        
        self.discussion_scenarios = list(discussion_query)
        
        # Q3e: Telephone Etiquette - select from telephone topics (check topic name for 'telephone'/'phone')
        telephone_query = Question.objects.filter(
            paper=self.paper,
            is_active=True
        )
        if telephone_topics:
            telephone_query = telephone_query.filter(topic__in=telephone_topics)
        elif oral_topics:
            # Fallback to general oral topics if no specific telephone topics
            telephone_query = telephone_query.filter(topic__in=oral_topics, question_type='telephone_etiquette')
        
        self.telephone_scenarios = list(telephone_query)
        
        # ALTERNATIVE Q3 FORMATS: Load standalone oral questions if sub-sections not available
        # 30 marks single questions
        oral_30_query = Question.objects.filter(
            paper=self.paper,
            marks=30,
            is_active=True
        )
        if oral_topics:
            oral_30_query = oral_30_query.filter(topic__in=oral_topics)
        self.oral_30_marks_questions = list(oral_30_query)
        
        # 20 marks oral questions (to combine with 10 marks)
        oral_20_query = Question.objects.filter(
            paper=self.paper,
            marks=20,
            is_active=True
        )
        if oral_topics:
            oral_20_query = oral_20_query.filter(topic__in=oral_topics)
        self.oral_20_marks_questions = list(oral_20_query)
        
        # 15 marks oral questions (to combine two of them)
        oral_15_query = Question.objects.filter(
            paper=self.paper,
            marks=15,
            is_active=True
        )
        if oral_topics:
            oral_15_query = oral_15_query.filter(topic__in=oral_topics)
        self.oral_15_marks_questions = list(oral_15_query)
        
        # 10 marks oral questions (to combine with 20 marks)
        oral_10_query = Question.objects.filter(
            paper=self.paper,
            marks=10,
            is_active=True
        )
        if oral_topics:
            oral_10_query = oral_10_query.filter(topic__in=oral_topics)
        self.oral_10_marks_questions = list(oral_10_query)
        
        # Shuffle all
        random.shuffle(self.functional_writing_tasks)
        random.shuffle(self.cloze_test_passages)
        random.shuffle(self.riddles)
        random.shuffle(self.homophone_sets)
        random.shuffle(self.word_stress_sets)
        random.shuffle(self.discussion_scenarios)
        random.shuffle(self.telephone_scenarios)
        random.shuffle(self.oral_30_marks_questions)
        random.shuffle(self.oral_20_marks_questions)
        random.shuffle(self.oral_15_marks_questions)
        random.shuffle(self.oral_10_marks_questions)
        
        print(f"\n[PAPER 1 DATA LOADED]")
        print(f"  SECTION 1 - Functional Skills (from 'functional' topics):")
        print(f"    Functional writing tasks: {len(self.functional_writing_tasks)}")
        print(f"  SECTION 2 - Cloze Test (from 'cloze' topics):")
        print(f"    Cloze test passages: {len(self.cloze_test_passages)}")
        print(f"  SECTION 3 - Oral Skills (from 'oral' topics):")
        print(f"    Sub-sections format:")
        print(f"      Riddles: {len(self.riddles)}")
        print(f"      Homophone sets: {len(self.homophone_sets)}")
        print(f"      Word stress sets: {len(self.word_stress_sets)}")
        print(f"      Discussion scenarios: {len(self.discussion_scenarios)}")
        print(f"      Telephone scenarios: {len(self.telephone_scenarios)}")
        print(f"    Alternative formats (if sub-sections insufficient):")
        print(f"      30 marks questions: {len(self.oral_30_marks_questions)}")
        print(f"      20 marks questions: {len(self.oral_20_marks_questions)}")
        print(f"      15 marks questions: {len(self.oral_15_marks_questions)}")
        print(f"      10 marks questions: {len(self.oral_10_marks_questions)}")
        
        # Validate minimum requirements - now more flexible
        if len(self.functional_writing_tasks) < 1:
            raise ValueError("Need at least 1 functional writing task from 'functional' topics")
        if len(self.cloze_test_passages) < 1:
            raise ValueError("Need at least 1 cloze test passage from 'cloze' topics")
        
        # For Question 3, check if we have EITHER sub-sections OR alternative formats
        has_subsections = (
            len(self.riddles) >= 1 and 
            len(self.homophone_sets) >= 1 and 
            len(self.word_stress_sets) >= 1 and 
            len(self.discussion_scenarios) >= 1 and 
            len(self.telephone_scenarios) >= 1
        )
        
        has_30_marks = len(self.oral_30_marks_questions) >= 1
        has_20_10_combo = len(self.oral_20_marks_questions) >= 1 and len(self.oral_10_marks_questions) >= 1
        has_15_15_combo = len(self.oral_15_marks_questions) >= 2
        
        if not (has_subsections or has_30_marks or has_20_10_combo or has_15_15_combo):
            raise ValueError(
                "Need at least ONE of the following for Question 3 (Oral Skills):\n"
                "  - Complete sub-sections (riddles, homophones, word stress, discussion, telephone)\n"
                "  - At least 1 question worth 30 marks\n"
                "  - At least 1 question worth 20 marks + 1 question worth 10 marks\n"
                "  - At least 2 questions worth 15 marks each"
            )
    
    def generate(self) -> Dict:
        """Generate English Paper 1"""
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE ENGLISH PAPER 1 GENERATION")
        print(f"{'='*70}")
        
        # Select questions (no complex algorithm needed - straightforward selection)
        self.selected_functional_task = random.choice(self.functional_writing_tasks)
        self.selected_cloze_passage = random.choice(self.cloze_test_passages)
        
        # Question 3: Select oral skills questions based on what's available
        # Priority: 1) Sub-sections, 2) Single 30 marks, 3) 20+10 combo, 4) 15+15 combo
        q3_marks = 0
        q3_format = None
        
        # Try sub-sections format first (riddles, homophones, word stress, discussion, telephone)
        if (len(self.riddles) >= 1 and len(self.homophone_sets) >= 1 and 
            len(self.word_stress_sets) >= 1 and len(self.discussion_scenarios) >= 1 and 
            len(self.telephone_scenarios) >= 1):
            
            self.selected_riddle = random.choice(self.riddles)
            self.selected_homophones = random.choice(self.homophone_sets)
            self.selected_word_stress = random.choice(self.word_stress_sets)
            self.selected_discussion = random.choice(self.discussion_scenarios)
            self.selected_telephone = random.choice(self.telephone_scenarios)
            
            q3_marks = (self.selected_riddle.marks + self.selected_homophones.marks + 
                       self.selected_word_stress.marks + self.selected_discussion.marks + 
                       self.selected_telephone.marks)
            q3_format = 'sub_sections'
            print(f"[Q3 FORMAT] Using sub-sections (riddles, homophones, etc.)")
        
        # Try single 30 marks question
        elif len(self.oral_30_marks_questions) >= 1:
            self.selected_oral_questions = [random.choice(self.oral_30_marks_questions)]
            q3_marks = 30
            q3_format = 'single_30'
            print(f"[Q3 FORMAT] Using single 30 marks question")
        
        # Try 20 marks + 10 marks combination
        elif len(self.oral_20_marks_questions) >= 1 and len(self.oral_10_marks_questions) >= 1:
            q_20 = random.choice(self.oral_20_marks_questions)
            q_10 = random.choice(self.oral_10_marks_questions)
            self.selected_oral_questions = [q_20, q_10]
            q3_marks = 30
            q3_format = 'combo_20_10'
            print(f"[Q3 FORMAT] Using 20 marks + 10 marks combination")
        
        # Try 15 marks + 15 marks combination
        elif len(self.oral_15_marks_questions) >= 2:
            self.selected_oral_questions = random.sample(self.oral_15_marks_questions, 2)
            q3_marks = 30
            q3_format = 'combo_15_15'
            print(f"[Q3 FORMAT] Using 15 marks + 15 marks combination")
        
        else:
            raise ValueError("No valid format available for Question 3 (Oral Skills)")
        
        # Calculate total marks
        self.total_marks = self.selected_functional_task.marks + self.selected_cloze_passage.marks + q3_marks
        
        generation_time = time.time() - start_time
        
        print(f"\n[Q1: FUNCTIONAL WRITING] {self.selected_functional_task.marks} marks")
        print(f"[Q2: CLOZE TEST] {self.selected_cloze_passage.marks} marks")
        print(f"[Q3: ORAL SKILLS] {q3_marks} marks")
        print(f"\nTotal: {self.total_marks}/{self.TOTAL_MARKS} marks")
        
        if self.total_marks != self.TOTAL_MARKS:
            raise Exception(f"Marks mismatch: {self.total_marks} != {self.TOTAL_MARKS}")
        
        print(f"\n{'='*70}")
        print(f"SUCCESS! Generated in {generation_time:.2f}s")
        print(f"{'='*70}")
        
        return self._build_result(generation_time, q3_format)
    
    def _build_result(self, generation_time: float, q3_format: str) -> Dict:
        """Build Paper 1 result"""
        result = {
            'paper': {
                'id': str(self.paper.id),
                'name': self.paper.name,
                'subject': {'id': str(self.subject.id), 'name': self.subject.name},
                'total_marks': self.TOTAL_MARKS,
                'time_allocation': '2 hours'
            },
            'questions': {
                'question_1': {
                    'type': 'functional_writing',
                    'marks': self.Q1_FUNCTIONAL_WRITING_MARKS,
                    'task': {
                        'id': str(self.selected_functional_task.id),
                        'text': self.selected_functional_task.question_text,
                        'answer_guide': self.selected_functional_task.answer_text
                    }
                },
                'question_2': {
                    'type': 'cloze_test',
                    'marks': self.Q2_CLOZE_TEST_MARKS,
                    'passage': {
                        'id': str(self.selected_cloze_passage.id),
                        'text': self.selected_cloze_passage.question_text,
                        'answers': self.selected_cloze_passage.answer_text
                    }
                },
                'question_3': {
                    'type': 'oral_skills',
                    'marks': self.Q3_ORAL_SKILLS_MARKS,
                    'format': q3_format
                }
            },
            'statistics': {
                'total_marks': self.total_marks,
                'generation_time_seconds': round(generation_time, 2)
            },
            'question_ids': {}
        }
        
        # Track all question IDs
        result['question_ids']['functional_task'] = str(self.selected_functional_task.id)
        result['question_ids']['cloze_passage'] = str(self.selected_cloze_passage.id)
        
        # Add Question 3 content based on format used
        if q3_format == 'sub_sections':
            result['questions']['question_3']['sub_sections'] = {
                'a_riddle': {
                    'id': str(self.selected_riddle.id),
                    'marks': self.selected_riddle.marks,
                    'text': self.selected_riddle.question_text,
                    'answers': self.selected_riddle.answer_text
                },
                'b_homophones': {
                    'id': str(self.selected_homophones.id),
                    'marks': self.selected_homophones.marks,
                    'text': self.selected_homophones.question_text,
                    'answers': self.selected_homophones.answer_text
                },
                'c_word_stress': {
                    'id': str(self.selected_word_stress.id),
                    'marks': self.selected_word_stress.marks,
                    'text': self.selected_word_stress.question_text,
                    'answers': self.selected_word_stress.answer_text
                },
                'd_discussion': {
                    'id': str(self.selected_discussion.id),
                    'marks': self.selected_discussion.marks,
                    'text': self.selected_discussion.question_text,
                    'answers': self.selected_discussion.answer_text
                },
                'e_telephone': {
                    'id': str(self.selected_telephone.id),
                    'marks': self.selected_telephone.marks,
                    'text': self.selected_telephone.question_text,
                    'answers': self.selected_telephone.answer_text
                }
            }
            # Add question IDs for sub-sections
            result['question_ids']['riddle'] = str(self.selected_riddle.id)
            result['question_ids']['homophones'] = str(self.selected_homophones.id)
            result['question_ids']['word_stress'] = str(self.selected_word_stress.id)
            result['question_ids']['discussion'] = str(self.selected_discussion.id)
            result['question_ids']['telephone'] = str(self.selected_telephone.id)
        elif q3_format == 'single_30':
            result['questions']['question_3']['questions'] = [{
                'id': str(self.selected_oral_questions[0].id),
                'marks': 30,
                'text': self.selected_oral_questions[0].question_text,
                'answers': self.selected_oral_questions[0].answer_text
            }]
            # Add question ID for single 30 marks question
            result['question_ids']['oral_30'] = str(self.selected_oral_questions[0].id)
        elif q3_format in ['combo_20_10', 'combo_15_15']:
            result['questions']['question_3']['questions'] = [
                {
                    'id': str(q.id),
                    'marks': q.marks,
                    'text': q.question_text,
                    'answers': q.answer_text
                }
                for q in self.selected_oral_questions
            ]
            # Add question IDs for combo questions
            result['question_ids']['oral_combo'] = [str(q.id) for q in self.selected_oral_questions]
        
        return result


class KCSEEnglishPaper2Generator:
    """
    KCSE English Paper 2 - Comprehension, Literary Appreciation & Grammar
    Q1: Comprehension (20) + Q2: Literature (25) + Q3: Poetry (20) + Q4: Grammar (15) = 80 marks
    """
    
    TOTAL_MARKS = 80
    Q1_COMPREHENSION_MARKS = 20
    Q2_LITERATURE_MARKS = 25
    Q3_POETRY_MARKS = 20
    Q4_GRAMMAR_MARKS = 15
    
    def __init__(self, paper_id: str, selections: Dict):
        """Initialize Paper 2 generator"""
        self.paper_id = paper_id
        self.selections = selections
        
        self.paper = None
        self.subject = None
        
        # Main content (passages, excerpts, poems)
        self.comprehension_passages = []
        self.literature_excerpts = []
        self.poems = []
        
        # Sub-questions for each section
        self.comprehension_subquestions = []
        self.literature_subquestions = []
        self.poetry_subquestions = []
        
        # Grammar items
        self.grammar_items = {
            'transformation': [],
            'word_forms': [],
            'prepositions': [],
            'synonyms': [],
            'ambiguity': []
        }
        
        # Selected content
        self.selected_passage = None
        self.selected_excerpt = None
        self.selected_poem = None
        self.selected_grammar = {}
        
        self.q1_subquestions = []
        self.q2_subquestions = []
        self.q3_subquestions = []
        self.q4_subquestions = []
        
        self.attempts = 0
        self.total_marks = 0
    
    def load_data(self):
        """Load Paper 2 content from database"""
        self.paper = Paper.objects.select_related('subject').get(
            id=self.paper_id,
            is_active=True
        )
        self.subject = self.paper.subject
        
        if 'English' not in self.subject.name or 'Paper 2' not in self.paper.name:
            raise ValueError("This generator is only for English Paper 2")
        
        # Load comprehension passages and sub-questions
        comprehension_topics = self.selections.get('comprehension_topics', [])
        passage_filter = {
            'paper': self.paper,
            'question_type': 'comprehension_passage',
            'is_active': True,
        }
        if comprehension_topics:
            passage_filter['topic_id__in'] = comprehension_topics
        
        self.comprehension_passages = list(Question.objects.filter(
            **passage_filter
        ).select_related('topic'))
        
        # Comprehension sub-questions
        subq_filter = passage_filter.copy()
        subq_filter['question_type__in'] = [
            'factual_recall', 'inference', 'explanation', 
            'summary', 'description', 'grammar_transformation', 
            'vocabulary'
        ]
        self.comprehension_subquestions = list(Question.objects.filter(**subq_filter))
        
        # Load literature excerpts and sub-questions
        literature_topics = self.selections.get('literature_topics', [])
        excerpt_filter = {
            'paper': self.paper,
            'question_type': 'literature_excerpt',
            'is_active': True,
        }
        if literature_topics:
            excerpt_filter['topic_id__in'] = literature_topics
        
        self.literature_excerpts = list(Question.objects.filter(
            **excerpt_filter
        ).select_related('topic'))
        
        # Literature sub-questions
        lit_subq_filter = excerpt_filter.copy()
        lit_subq_filter['question_type__in'] = [
            'context_before', 'character_trait', 'theme',
            'character_analysis', 'stylistic_features', 
            'text_connection', 'context_after', 'vocabulary', 'message'
        ]
        self.literature_subquestions = list(Question.objects.filter(**lit_subq_filter))
        
        # Load poems and sub-questions
        poetry_topics = self.selections.get('poetry_topics', [])
        poem_filter = {
            'paper': self.paper,
            'question_type': 'poem',
            'is_active': True,
        }
        if poetry_topics:
            poem_filter['topic_id__in'] = poetry_topics
        
        self.poems = list(Question.objects.filter(**poem_filter).select_related('topic'))
        
        # Poetry sub-questions
        poetry_subq_filter = poem_filter.copy()
        poetry_subq_filter['question_type__in'] = [
            'theme', 'content_recall', 'stylistic_features',
            'interpretation', 'persona_traits', 'lesson', 'vocabulary'
        ]
        self.poetry_subquestions = list(Question.objects.filter(**poetry_subq_filter))
        
        # Load grammar items
        for grammar_type in self.grammar_items.keys():
            self.grammar_items[grammar_type] = list(Question.objects.filter(
                paper=self.paper,
                question_type=f'grammar_{grammar_type}',
                is_active=True
            ))
        
        # Shuffle all
        for pool in [self.comprehension_passages, self.comprehension_subquestions,
                     self.literature_excerpts, self.literature_subquestions,
                     self.poems, self.poetry_subquestions]:
            random.shuffle(pool)
        
        for items in self.grammar_items.values():
            random.shuffle(items)
        
        print(f"\n[PAPER 2 DATA LOADED]")
        print(f"  Comprehension: {len(self.comprehension_passages)} passages, {len(self.comprehension_subquestions)} sub-questions")
        print(f"  Literature: {len(self.literature_excerpts)} excerpts, {len(self.literature_subquestions)} sub-questions")
        print(f"  Poetry: {len(self.poems)} poems, {len(self.poetry_subquestions)} sub-questions")
        print(f"  Grammar items: {sum(len(items) for items in self.grammar_items.values())}")
        
        # Validate minimums
        if len(self.comprehension_passages) < 1 or len(self.comprehension_subquestions) < 5:
            raise ValueError("Insufficient comprehension content")
        if len(self.literature_excerpts) < 1 or len(self.literature_subquestions) < 6:
            raise ValueError("Insufficient literature content")
        if len(self.poems) < 1 or len(self.poetry_subquestions) < 5:
            raise ValueError("Insufficient poetry content")
        
        grammar_requirements = {'transformation': 4, 'word_forms': 3, 'prepositions': 3, 'synonyms': 3, 'ambiguity': 1}
        for grammar_type, min_required in grammar_requirements.items():
            if len(self.grammar_items[grammar_type]) < min_required:
                raise ValueError(f"Need at least {min_required} {grammar_type} items")
    
    def generate(self) -> Dict:
        """Generate English Paper 2"""
        max_attempts = 100
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE ENGLISH PAPER 2 GENERATION")
        print(f"{'='*70}")
        
        for attempt in range(1, max_attempts + 1):
            self.attempts = attempt
            
            # Reset
            self.q1_subquestions = []
            self.q2_subquestions = []
            self.q3_subquestions = []
            self.q4_subquestions = []
            self.total_marks = 0
            
            # Try to generate all 4 questions
            if not self._select_question1_comprehension():
                continue
            if not self._select_question2_literature():
                continue
            if not self._select_question3_poetry():
                continue
            if not self._select_question4_grammar():
                continue
            
            self.total_marks = sum([
                sum(sq['marks'] for sq in self.q1_subquestions),
                sum(sq['marks'] for sq in self.q2_subquestions),
                sum(sq['marks'] for sq in self.q3_subquestions),
                sum(sq['marks'] for sq in self.q4_subquestions)
            ])
            
            if self.total_marks != self.TOTAL_MARKS:
                continue
            
            generation_time = time.time() - start_time
            print(f"\n{'='*70}")
            print(f"SUCCESS! Generated in {attempt} attempts ({generation_time:.2f}s)")
            print(f"{'='*70}")
            
            return self._build_result(generation_time)
        
        raise Exception(f"Failed after {max_attempts} attempts")
    
    def _select_question1_comprehension(self) -> bool:
        """Select Q1: Comprehension (20 marks)"""
        if not self.comprehension_passages or not self.comprehension_subquestions:
            return False
        
        self.selected_passage = random.choice(self.comprehension_passages)
        selected = self._select_questions_for_target(
            self.comprehension_subquestions, 
            self.Q1_COMPREHENSION_MARKS,
            min_count=5,
            max_count=10
        )
        
        if not selected:
            return False
        
        self.q1_subquestions = [
            {
                'id': str(sq.id),
                'question_number': f"1{chr(97 + idx)}",
                'type': sq.question_type,
                'marks': sq.marks,
                'text': sq.question_text,
                'answer': sq.answer_text,
            }
            for idx, sq in enumerate(selected)
        ]
        
        return sum(sq['marks'] for sq in self.q1_subquestions) == self.Q1_COMPREHENSION_MARKS
    
    def _select_question2_literature(self) -> bool:
        """Select Q2: Literature (25 marks)"""
        if not self.literature_excerpts or not self.literature_subquestions:
            return False
        
        self.selected_excerpt = random.choice(self.literature_excerpts)
        selected = self._select_questions_for_target(
            self.literature_subquestions,
            self.Q2_LITERATURE_MARKS,
            min_count=6,
            max_count=12
        )
        
        if not selected:
            return False
        
        self.q2_subquestions = [
            {
                'id': str(sq.id),
                'question_number': f"2{chr(97 + idx)}",
                'type': sq.question_type,
                'marks': sq.marks,
                'text': sq.question_text,
                'answer': sq.answer_text,
            }
            for idx, sq in enumerate(selected)
        ]
        
        return sum(sq['marks'] for sq in self.q2_subquestions) == self.Q2_LITERATURE_MARKS
    
    def _select_question3_poetry(self) -> bool:
        """Select Q3: Poetry (20 marks)"""
        if not self.poems or not self.poetry_subquestions:
            return False
        
        self.selected_poem = random.choice(self.poems)
        selected = self._select_questions_for_target(
            self.poetry_subquestions,
            self.Q3_POETRY_MARKS,
            min_count=5,
            max_count=10
        )
        
        if not selected:
            return False
        
        self.q3_subquestions = [
            {
                'id': str(sq.id),
                'question_number': f"3{chr(97 + idx)}",
                'type': sq.question_type,
                'marks': sq.marks,
                'text': sq.question_text,
                'answer': sq.answer_text,
            }
            for idx, sq in enumerate(selected)
        ]
        
        return sum(sq['marks'] for sq in self.q3_subquestions) == self.Q3_POETRY_MARKS
    
    def _select_question4_grammar(self) -> bool:
        """Select Q4: Grammar (15 marks)"""
        grammar_requirements = {
            'transformation': {'count': 4, 'marks_each': 1},
            'word_forms': {'count': 3, 'marks_each': 1},
            'prepositions': {'count': 3, 'marks_each': 1},
            'synonyms': {'count': 3, 'marks_each': 1},
            'ambiguity': {'count': 1, 'marks_each': 2}
        }
        
        self.q4_subquestions = []
        self.selected_grammar = {}
        question_letter = ord('a')
        
        for grammar_type, requirements in grammar_requirements.items():
            items_needed = requirements['count']
            marks_each = requirements['marks_each']
            
            available = self.grammar_items[grammar_type]
            if len(available) < items_needed:
                return False
            
            selected_items = random.sample(available, items_needed)
            self.selected_grammar[grammar_type] = selected_items
            
            self.q4_subquestions.append({
                'question_number': f"4{chr(question_letter)}",
                'type': grammar_type,
                'marks': items_needed * marks_each,
                'items': [
                    {
                        'id': str(item.id),
                        'text': item.question_text,
                        'answer': item.answer_text,
                        'marks': marks_each
                    }
                    for item in selected_items
                ]
            })
            question_letter += 1
        
        return sum(sq['marks'] for sq in self.q4_subquestions) == self.Q4_GRAMMAR_MARKS
    
    def _select_questions_for_target(self, questions: List, target_marks: int, 
                                    min_count: int = 1, max_count: int = 20) -> Optional[List]:
        """Select questions that sum to target marks"""
        for _ in range(100):
            shuffled = questions.copy()
            random.shuffle(shuffled)
            
            selected = []
            current_sum = 0
            
            for q in shuffled:
                if current_sum + q.marks <= target_marks:
                    selected.append(q)
                    current_sum += q.marks
                    
                    if current_sum == target_marks and min_count <= len(selected) <= max_count:
                        return selected
            
            if current_sum == target_marks and min_count <= len(selected) <= max_count:
                return selected
        
        return None
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build Paper 2 result"""
        return {
            'paper': {
                'id': str(self.paper.id),
                'name': self.paper.name,
                'subject': {'id': str(self.subject.id), 'name': self.subject.name},
                'total_marks': self.TOTAL_MARKS,
                'time_allocation': '2 hours 30 minutes'
            },
            'questions': {
                'question_1': {
                    'type': 'comprehension',
                    'marks': self.Q1_COMPREHENSION_MARKS,
                    'passage': {
                        'id': str(self.selected_passage.id),
                        'text': self.selected_passage.question_text,
                        'topic': self.selected_passage.topic.name
                    },
                    'sub_questions': self.q1_subquestions
                },
                'question_2': {
                    'type': 'literature',
                    'marks': self.Q2_LITERATURE_MARKS,
                    'excerpt': {
                        'id': str(self.selected_excerpt.id),
                        'text': self.selected_excerpt.question_text,
                        'topic': self.selected_excerpt.topic.name
                    },
                    'sub_questions': self.q2_subquestions
                },
                'question_3': {
                    'type': 'poetry',
                    'marks': self.Q3_POETRY_MARKS,
                    'poem': {
                        'id': str(self.selected_poem.id),
                        'text': self.selected_poem.question_text,
                        'topic': self.selected_poem.topic.name
                    },
                    'sub_questions': self.q3_subquestions
                },
                'question_4': {
                    'type': 'grammar',
                    'marks': self.Q4_GRAMMAR_MARKS,
                    'sub_questions': self.q4_subquestions
                }
            },
            'statistics': {
                'total_marks': self.total_marks,
                'generation_attempts': self.attempts,
                'generation_time_seconds': round(generation_time, 2)
            }
        }


class KCSEEnglishPaper3Generator:
    """
    KCSE English Paper 3 - Creative Composition & Essays on Set Texts
    Q1: Creative Writing (20) + Q2: Compulsory Set Text (20) + Q3: Optional Set Text (20) = 60 marks
    
    Structure from 2020 exam:
    - Q1: Two choices - (a) Story ending with quote OR (b) Expository composition
    - Q2: Compulsory - Essay on "A Doll's House" by Henrik Ibsen
    - Q3: Optional - Choose ONE: (a) Short Story OR (b) Drama OR (c) Novel
    """
    
    TOTAL_MARKS = 60
    Q1_CREATIVE_MARKS = 20
    Q2_COMPULSORY_SET_TEXT_MARKS = 20
    Q3_OPTIONAL_SET_TEXT_MARKS = 20
    
    def __init__(self, paper_id: str, selections: Dict):
        """
        Initialize Paper 3 generator
        
        Args:
            paper_id: UUID of English Paper 3
            selections: Dict with:
                {
                    'compulsory_set_text_id': 'uuid',  # Usually "A Doll's House"
                    'optional_set_texts': ['uuid1', 'uuid2', 'uuid3']  # Short story, drama, novel
                }
        """
        self.paper_id = paper_id
        self.selections = selections
        
        self.paper = None
        self.subject = None
        
        # Question pools
        self.creative_story_prompts = []    # Story prompts with endings
        self.creative_composition_prompts = []  # Expository/composition topics
        self.compulsory_set_text_essays = []  # A Doll's House essay questions
        self.optional_short_story_essays = []  # Short story essay questions
        self.optional_drama_essays = []  # Drama essay questions
        self.optional_novel_essays = []  # Novel essay questions
        
        # Selected content
        self.selected_creative_story = None
        self.selected_creative_composition = None
        self.selected_compulsory_essay = None
        self.selected_optional_short_story = None
        self.selected_optional_drama = None
        self.selected_optional_novel = None
        
        self.attempts = 0
        self.total_marks = 0
    
    def load_data(self):
        """Load Paper 3 content from database"""
        self.paper = Paper.objects.select_related('subject').get(
            id=self.paper_id,
            is_active=True
        )
        self.subject = self.paper.subject
        
        if 'English' not in self.subject.name or 'Paper 3' not in self.paper.name:
            raise ValueError("This generator is only for English Paper 3")
        
        # Q1a: Creative Story (question_type: 'creative_story')
        self.creative_story_prompts = list(Question.objects.filter(
            paper=self.paper,
            question_type='creative_story',
            marks=self.Q1_CREATIVE_MARKS,
            is_active=True
        ))
        
        # Q1b: Creative Composition (question_type: 'creative_composition')
        self.creative_composition_prompts = list(Question.objects.filter(
            paper=self.paper,
            question_type='creative_composition',
            marks=self.Q1_CREATIVE_MARKS,
            is_active=True
        ))
        
        # Q2: Compulsory Set Text Essay (question_type: 'compulsory_set_text_essay')
        compulsory_text_id = self.selections.get('compulsory_set_text_id')
        compulsory_filter = {
            'paper': self.paper,
            'question_type': 'compulsory_set_text_essay',
            'marks': self.Q2_COMPULSORY_SET_TEXT_MARKS,
            'is_active': True
        }
        if compulsory_text_id:
            compulsory_filter['topic_id'] = compulsory_text_id
        
        self.compulsory_set_text_essays = list(Question.objects.filter(
            **compulsory_filter
        ).select_related('topic'))
        
        # Q3a: Optional Short Story Essay (question_type: 'optional_short_story_essay')
        optional_texts = self.selections.get('optional_set_texts', [])
        short_story_filter = {
            'paper': self.paper,
            'question_type': 'optional_short_story_essay',
            'marks': self.Q3_OPTIONAL_SET_TEXT_MARKS,
            'is_active': True
        }
        if optional_texts:
            short_story_filter['topic_id__in'] = optional_texts
        
        self.optional_short_story_essays = list(Question.objects.filter(
            **short_story_filter
        ).select_related('topic'))
        
        # Q3b: Optional Drama Essay (question_type: 'optional_drama_essay')
        drama_filter = short_story_filter.copy()
        drama_filter['question_type'] = 'optional_drama_essay'
        self.optional_drama_essays = list(Question.objects.filter(
            **drama_filter
        ).select_related('topic'))
        
        # Q3c: Optional Novel Essay (question_type: 'optional_novel_essay')
        novel_filter = short_story_filter.copy()
        novel_filter['question_type'] = 'optional_novel_essay'
        self.optional_novel_essays = list(Question.objects.filter(
            **novel_filter
        ).select_related('topic'))
        
        # Shuffle all
        random.shuffle(self.creative_story_prompts)
        random.shuffle(self.creative_composition_prompts)
        random.shuffle(self.compulsory_set_text_essays)
        random.shuffle(self.optional_short_story_essays)
        random.shuffle(self.optional_drama_essays)
        random.shuffle(self.optional_novel_essays)
        
        print(f"\n[PAPER 3 DATA LOADED]")
        print(f"  Creative story prompts: {len(self.creative_story_prompts)}")
        print(f"  Creative composition prompts: {len(self.creative_composition_prompts)}")
        print(f"  Compulsory set text essays: {len(self.compulsory_set_text_essays)}")
        print(f"  Optional short story essays: {len(self.optional_short_story_essays)}")
        print(f"  Optional drama essays: {len(self.optional_drama_essays)}")
        print(f"  Optional novel essays: {len(self.optional_novel_essays)}")
        
        # Validate minimum requirements
        if len(self.creative_story_prompts) < 1:
            raise ValueError("Need at least 1 creative story prompt")
        if len(self.creative_composition_prompts) < 1:
            raise ValueError("Need at least 1 creative composition prompt")
        if len(self.compulsory_set_text_essays) < 1:
            raise ValueError("Need at least 1 compulsory set text essay")
        if len(self.optional_short_story_essays) < 1:
            raise ValueError("Need at least 1 optional short story essay")
        if len(self.optional_drama_essays) < 1:
            raise ValueError("Need at least 1 optional drama essay")
        if len(self.optional_novel_essays) < 1:
            raise ValueError("Need at least 1 optional novel essay")
    
    def generate(self) -> Dict:
        """Generate English Paper 3"""
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"KCSE ENGLISH PAPER 3 GENERATION")
        print(f"{'='*70}")
        
        # Q1: Select one story prompt and one composition prompt (student chooses one)
        self.selected_creative_story = random.choice(self.creative_story_prompts)
        self.selected_creative_composition = random.choice(self.creative_composition_prompts)
        
        # Q2: Select one compulsory set text essay (usually A Doll's House)
        self.selected_compulsory_essay = random.choice(self.compulsory_set_text_essays)
        
        # Q3: Select one from each optional category (student chooses one)
        self.selected_optional_short_story = random.choice(self.optional_short_story_essays)
        self.selected_optional_drama = random.choice(self.optional_drama_essays)
        self.selected_optional_novel = random.choice(self.optional_novel_essays)
        
        # Calculate total marks (all questions are worth 20 marks each)
        self.total_marks = (
            self.selected_creative_story.marks +  # Q1 (either option)
            self.selected_compulsory_essay.marks +  # Q2
            self.selected_optional_short_story.marks  # Q3 (any option)
        )
        
        generation_time = time.time() - start_time
        
        print(f"\n[Q1: CREATIVE WRITING] 20 marks (2 options)")
        print(f"  Story: {self.selected_creative_story.question_text[:80]}...")
        print(f"  Composition: {self.selected_creative_composition.question_text[:80]}...")
        print(f"\n[Q2: COMPULSORY SET TEXT] 20 marks")
        print(f"  {self.selected_compulsory_essay.topic.name if hasattr(self.selected_compulsory_essay, 'topic') else 'Set Text'}")
        print(f"\n[Q3: OPTIONAL SET TEXT] 20 marks (3 options)")
        print(f"  Short Story, Drama, Novel")
        print(f"\nTotal: {self.total_marks}/{self.TOTAL_MARKS} marks")
        
        if self.total_marks != self.TOTAL_MARKS:
            raise Exception(f"Marks mismatch: {self.total_marks} != {self.TOTAL_MARKS}")
        
        print(f"\n{'='*70}")
        print(f"SUCCESS! Generated in {generation_time:.2f}s")
        print(f"{'='*70}")
        
        return self._build_result(generation_time)
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build Paper 3 result"""
        return {
            'paper': {
                'id': str(self.paper.id),
                'name': self.paper.name,
                'subject': {'id': str(self.subject.id), 'name': self.subject.name},
                'total_marks': self.TOTAL_MARKS,
                'time_allocation': '2 hours 30 minutes'
            },
            'instructions': {
                'answer_count': 'Answer THREE questions only',
                'compulsory': 'Questions 1 and 2 are compulsory',
                'optional': 'In question 3, choose only ONE of the optional set texts',
                'word_limit': 'Each essay must not exceed 450 words'
            },
            'questions': {
                'question_1': {
                    'type': 'creative_writing',
                    'marks': self.Q1_CREATIVE_MARKS,
                    'instruction': 'Either (a) or (b)',
                    'option_a': {
                        'id': str(self.selected_creative_story.id),
                        'type': 'story',
                        'text': self.selected_creative_story.question_text,
                        'marking_guide': self.selected_creative_story.answer_text
                    },
                    'option_b': {
                        'id': str(self.selected_creative_composition.id),
                        'type': 'composition',
                        'text': self.selected_creative_composition.question_text,
                        'marking_guide': self.selected_creative_composition.answer_text
                    }
                },
                'question_2': {
                    'type': 'compulsory_set_text',
                    'marks': self.Q2_COMPULSORY_SET_TEXT_MARKS,
                    'set_text': {
                        'id': str(self.selected_compulsory_essay.id),
                        'title': self.selected_compulsory_essay.topic.name if hasattr(self.selected_compulsory_essay, 'topic') else 'A Doll\'s House',
                        'text': self.selected_compulsory_essay.question_text,
                        'marking_guide': self.selected_compulsory_essay.answer_text
                    }
                },
                'question_3': {
                    'type': 'optional_set_text',
                    'marks': self.Q3_OPTIONAL_SET_TEXT_MARKS,
                    'instruction': 'Answer any ONE of the following three questions',
                    'option_a': {
                        'id': str(self.selected_optional_short_story.id),
                        'category': 'The Short Story',
                        'title': self.selected_optional_short_story.topic.name if hasattr(self.selected_optional_short_story, 'topic') else 'Short Story',
                        'text': self.selected_optional_short_story.question_text,
                        'marking_guide': self.selected_optional_short_story.answer_text
                    },
                    'option_b': {
                        'id': str(self.selected_optional_drama.id),
                        'category': 'Drama',
                        'title': self.selected_optional_drama.topic.name if hasattr(self.selected_optional_drama, 'topic') else 'Drama',
                        'text': self.selected_optional_drama.question_text,
                        'marking_guide': self.selected_optional_drama.answer_text
                    },
                    'option_c': {
                        'id': str(self.selected_optional_novel.id),
                        'category': 'The Novel',
                        'title': self.selected_optional_novel.topic.name if hasattr(self.selected_optional_novel, 'topic') else 'Novel',
                        'text': self.selected_optional_novel.question_text,
                        'marking_guide': self.selected_optional_novel.answer_text
                    }
                }
            },
            'statistics': {
                'total_marks': self.total_marks,
                'generation_time_seconds': round(generation_time, 2)
            },
            'question_ids': {
                'creative_story': str(self.selected_creative_story.id),
                'creative_composition': str(self.selected_creative_composition.id),
                'compulsory_essay': str(self.selected_compulsory_essay.id),
                'optional_short_story': str(self.selected_optional_short_story.id),
                'optional_drama': str(self.selected_optional_drama.id),
                'optional_novel': str(self.selected_optional_novel.id)
            }
        }


