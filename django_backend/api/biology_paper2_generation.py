# -*- coding: utf-8 -*-
"""
KCSE Biology Paper 2 Generation Algorithm
Biology Paper 2 has a distinct structure with sections A and B

PAPER STRUCTURE:
- 80 marks total
- 8 questions total
- Section A: 5 questions x 8 marks each = 40 marks
- Section B: 3 questions x 20 marks each = 40 marks
  - Question 6: MUST be a graph question (compulsory, 20 marks)
  - Question 7 & 8: Essay questions (student chooses one, 20 marks each)
- 4 pages of lines after question 8 for answers

SECTION B REQUIREMENTS:
- Question 6: Must have 'graph' tag/keyword in question text or metadata
- Questions 7-8: Essay-type questions (20 marks each)
- Questions must be marked as section B questions
"""

import random
from collections import defaultdict
from typing import List, Dict, Optional
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Paper, Topic, Section, Question, GeneratedPaper


class BiologyPaper2Validator:
    """Validates if question pool is sufficient for Biology Paper 2 generation"""
    
    @staticmethod
    def validate(paper_id: str, selected_topic_ids: List[str]) -> Dict:
        """
        Validate question availability before generation
        
        Returns:
            Dict with validation results and recommendations
        """
        # Get section A and B
        section_a = Section.objects.filter(
            paper_id=paper_id,
            name__icontains='A',
            is_active=True
        ).first()
        
        section_b = Section.objects.filter(
            paper_id=paper_id,
            name__icontains='B',
            is_active=True
        ).first()
        
        # Section A questions (8 marks each)
        section_a_questions = Question.objects.filter(
            paper_id=paper_id,
            topic_id__in=selected_topic_ids,
            section=section_a,
            marks=8,
            is_active=True
        ).count() if section_a else 0
        
        # Section B questions
        if section_b:
            # Graph questions for question 6 (20 marks, contains 'graph' keyword)
            graph_questions = Question.objects.filter(
                paper_id=paper_id,
                topic_id__in=selected_topic_ids,
                section=section_b,
                marks=20,
                is_active=True,
                question_text__icontains='graph'
            ).count()
            
            # Essay questions for 7 & 8 (20 marks, not graph questions)
            essay_questions = Question.objects.filter(
                paper_id=paper_id,
                topic_id__in=selected_topic_ids,
                section=section_b,
                marks=20,
                is_active=True
            ).exclude(
                question_text__icontains='graph'
            ).count()
            
            total_section_b = graph_questions + essay_questions
        else:
            graph_questions = 0
            essay_questions = 0
            total_section_b = 0
        
        # Validation
        issues = []
        recommendations = []
        
        if not section_a:
            issues.append("Section A not found in paper")
            recommendations.append("Create Section A for the paper")
        elif section_a_questions < 10:
            issues.append(f"Section A: {section_a_questions} questions (need at least 10 questions of 8 marks)")
            recommendations.append("Add more 8-mark questions to Section A")
        
        if not section_b:
            issues.append("Section B not found in paper")
            recommendations.append("Create Section B for the paper")
        else:
            # Total Section B questions (graph + essay)
            if total_section_b < 10:
                issues.append(f"Section B total: {total_section_b} questions (need at least 10 questions of 20 marks)")
                recommendations.append("Add more 20-mark questions to Section B")
            
            # Warning for graph questions (not critical)
            if graph_questions < 3:
                recommendations.append(f"Only {graph_questions} graph questions found. Consider adding more graph-based questions for Question 6. If unavailable, essay questions will be used.")
            
            if essay_questions < 8:
                recommendations.append(f"Only {essay_questions} essay questions found. Consider adding more essay-type 20-mark questions.")
        
        return {
            'valid': len(issues) == 0,
            'statistics': {
                'section_a_questions': section_a_questions,
                'section_b_graph_questions': graph_questions,
                'section_b_essay_questions': essay_questions,
                'total_section_b': total_section_b
            },
            'issues': issues,
            'recommendations': recommendations
        }


class BiologyPaper2Generator:
    """
    KCSE Biology Paper 2 Generation Algorithm
    
    Paper Structure:
    - Section A: 5 questions (8 marks each) = 40 marks
    - Section B: 3 questions (20 marks each) = 40 marks
      - Question 6: Graph question (compulsory)
      - Question 7 & 8: Essay questions (choose one)
    - Total: 8 questions, 80 marks
    """
    
    # Paper constraints
    TOTAL_MARKS = 80
    SECTION_A_QUESTIONS = 5
    SECTION_A_MARKS_PER_QUESTION = 8
    SECTION_A_TOTAL_MARKS = 40
    
    SECTION_B_QUESTIONS = 3
    SECTION_B_MARKS_PER_QUESTION = 20
    SECTION_B_TOTAL_MARKS = 40
    
    TOTAL_QUESTIONS = SECTION_A_QUESTIONS + SECTION_B_QUESTIONS  # 8 questions
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str]):
        self.paper_id = paper_id
        self.selected_topic_ids = selected_topic_ids
        self.paper = None
        self.topics = []
        self.section_a = None
        self.section_b = None
        
        # Question pools
        self.section_a_pool = []  # 8-mark questions
        self.graph_questions_pool = []  # 20-mark graph questions
        self.essay_questions_pool = []  # 20-mark essay questions
        
        # Selected questions
        self.selected_section_a = []  # 5 questions
        self.selected_graph = None  # 1 question (Question 6)
        self.selected_essays = []  # 2 questions (Questions 7 & 8)
        
        # Tracking
        self.used_question_ids = set()
        self.topic_distribution = defaultdict(int)
        
    def load_data(self):
        """Load paper, sections, topics, and questions"""
        print(f"\n{'='*70}")
        print(f"LOADING DATA FOR BIOLOGY PAPER 2 GENERATION")
        print(f"{'='*70}")
        
        # Load paper
        self.paper = Paper.objects.select_related('subject').get(
            id=self.paper_id,
            is_active=True
        )
        print(f"Paper: {self.paper.name} ({self.paper.subject.name})")
        
        # Load sections
        self.section_a = Section.objects.filter(
            paper=self.paper,
            name__icontains='A',
            is_active=True
        ).first()
        
        self.section_b = Section.objects.filter(
            paper=self.paper,
            name__icontains='B',
            is_active=True
        ).first()
        
        if not self.section_a:
            raise ValueError("Section A not found for this paper")
        if not self.section_b:
            raise ValueError("Section B not found for this paper")
        
        print(f"Section A: {self.section_a.name}")
        print(f"Section B: {self.section_b.name}")
        
        # Load topics
        self.topics = list(Topic.objects.filter(
            id__in=self.selected_topic_ids,
            paper=self.paper,
            is_active=True
        ))
        
        if not self.topics:
            raise ValueError("No valid topics found for the selected IDs")
        
        print(f"\nSelected Topics ({len(self.topics)}):")
        for i, topic in enumerate(self.topics, 1):
            print(f"  {i}. {topic.name}")
        
        # Load Section A questions (8 marks each)
        self.section_a_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_a,
            marks=self.SECTION_A_MARKS_PER_QUESTION,
            is_active=True
        ).select_related('topic', 'section'))
        
        # Load Section B questions (20 marks each)
        # Graph questions (must contain 'graph' in question text)
        self.graph_questions_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_b,
            marks=self.SECTION_B_MARKS_PER_QUESTION,
            is_active=True,
            question_text__icontains='graph'
        ).select_related('topic', 'section'))
        
        # Essay questions (20 marks, not graph questions)
        self.essay_questions_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_b,
            marks=self.SECTION_B_MARKS_PER_QUESTION,
            is_active=True
        ).exclude(
            question_text__icontains='graph'
        ).select_related('topic', 'section'))
        
        # Shuffle for randomness
        random.shuffle(self.section_a_pool)
        random.shuffle(self.graph_questions_pool)
        random.shuffle(self.essay_questions_pool)
        
        print(f"\nQuestion Pools:")
        print(f"  Section A (8 marks): {len(self.section_a_pool)} questions")
        print(f"  Section B Graph (20 marks): {len(self.graph_questions_pool)} questions")
        print(f"  Section B Essay (20 marks): {len(self.essay_questions_pool)} questions")
        
        # Validation
        if len(self.section_a_pool) < self.SECTION_A_QUESTIONS:
            raise ValueError(
                f"Insufficient Section A questions: {len(self.section_a_pool)} "
                f"(need at least {self.SECTION_A_QUESTIONS})"
            )
        
        # Check total Section B questions (graph + essay)
        total_section_b = len(self.graph_questions_pool) + len(self.essay_questions_pool)
        if total_section_b < self.SECTION_B_QUESTIONS:
            raise ValueError(
                f"Insufficient Section B questions: {total_section_b} "
                f"(need at least {self.SECTION_B_QUESTIONS})"
            )
        
        # Warn if no graph questions (will use essay questions for Question 6)
        if len(self.graph_questions_pool) < 1:
            print(f"\nWarning: No graph questions found. Question 6 will be selected from essay questions.")
        
        print(f"\nData loaded successfully")
    
    def select_questions(self):
        """Select questions for the paper"""
        print(f"\n{'='*70}")
        print(f"SELECTING QUESTIONS FOR PAPER")
        print(f"{'='*70}")
        
        # Select 5 questions for Section A (fully random, MUST be 8 marks each)
        print(f"\nSection A: Selecting {self.SECTION_A_QUESTIONS} questions (8 marks each)")
        self.selected_section_a = random.sample(self.section_a_pool, self.SECTION_A_QUESTIONS)
        
        # Validate Section A questions are all 8 marks
        for q in self.selected_section_a:
            if q.marks != self.SECTION_A_MARKS_PER_QUESTION:
                raise ValueError(f"Section A question must be {self.SECTION_A_MARKS_PER_QUESTION} marks, found {q.marks} marks")
        
        for i, question in enumerate(self.selected_section_a, 1):
            self.used_question_ids.add(str(question.id))
            self.topic_distribution[question.topic.name] += 1
            try:
                preview = question.question_text[:60].encode('ascii', 'ignore').decode('ascii')
            except:
                preview = "Question text contains special characters"
            print(f"  Question {i}: {question.topic.name} - {preview}...")
        
        # Select 1 graph question for Question 6 (Section B)
        # Prioritize graph questions, but use essay questions if unavailable
        print(f"\nSection B - Question 6: Selecting question (20 marks)")
        if len(self.graph_questions_pool) > 0:
            # Graph questions available - prioritize these
            self.selected_graph = random.choice(self.graph_questions_pool)
            self.used_question_ids.add(str(self.selected_graph.id))
            self.topic_distribution[self.selected_graph.topic.name] += 1
            try:
                preview = self.selected_graph.question_text[:60].encode('ascii', 'ignore').decode('ascii')
            except:
                preview = "Question text contains special characters"
            print(f"  Question 6 (GRAPH): {self.selected_graph.topic.name} - {preview}...")
        else:
            # No graph questions available, fall back to essay pool
            print(f"  Warning: No graph questions available. Selecting from essay pool...")
            if len(self.essay_questions_pool) < 3:
                raise ValueError("Insufficient questions for Section B. Need at least 3 essay questions when no graph questions are available.")
            self.selected_graph = random.choice(self.essay_questions_pool)
            self.used_question_ids.add(str(self.selected_graph.id))
            self.topic_distribution[self.selected_graph.topic.name] += 1
            try:
                preview = self.selected_graph.question_text[:60].encode('ascii', 'ignore').decode('ascii')
            except:
                preview = "Question text contains special characters"
            print(f"  Question 6 (ESSAY - fallback): {self.selected_graph.topic.name} - {preview}...")
            # Remove selected question from essay pool to avoid duplication
            self.essay_questions_pool = [q for q in self.essay_questions_pool if str(q.id) != str(self.selected_graph.id)]
        
        # Select 2 essay questions for Questions 7 & 8 (Section B)
        print(f"\nSection B - Questions 7 & 8: Selecting {2} essay questions (20 marks each)")
        self.selected_essays = random.sample(self.essay_questions_pool, 2)
        
        # Validate Section B questions are all 20 marks
        if self.selected_graph.marks != self.SECTION_B_MARKS_PER_QUESTION:
            raise ValueError(f"Section B question 6 must be {self.SECTION_B_MARKS_PER_QUESTION} marks, found {self.selected_graph.marks} marks")
        for q in self.selected_essays:
            if q.marks != self.SECTION_B_MARKS_PER_QUESTION:
                raise ValueError(f"Section B questions must be {self.SECTION_B_MARKS_PER_QUESTION} marks, found {q.marks} marks")
        
        for i, question in enumerate(self.selected_essays, 7):
            self.used_question_ids.add(str(question.id))
            self.topic_distribution[question.topic.name] += 1
            try:
                preview = question.question_text[:60].encode('ascii', 'ignore').decode('ascii')
            except:
                preview = "Question text contains special characters"
            print(f"  Question {i}: {question.topic.name} - {preview}...")
        
        print(f"\nSelected {self.TOTAL_QUESTIONS} questions successfully")
        print(f"\nTopic Distribution:")
        for topic, count in sorted(self.topic_distribution.items()):
            print(f"  {topic}: {count} questions")
    
    def save_generated_paper(self) -> GeneratedPaper:
        """Save the generated paper to database"""
        print(f"\n{'='*70}")
        print(f"SAVING GENERATED PAPER")
        print(f"{'='*70}")
        
        with transaction.atomic():
            # Combine all selected questions in order
            all_questions = (
                self.selected_section_a +  # Questions 1-5
                [self.selected_graph] +     # Question 6
                self.selected_essays        # Questions 7-8
            )
            
            # Check if Question 6 is actually a graph question
            question_6_type = 'graph' if 'graph' in self.selected_graph.question_text.lower() else 'essay'
            
            # Calculate mark distribution
            mark_distribution = {
                '8': self.SECTION_A_QUESTIONS,  # 5 questions at 8 marks
                '20': self.SECTION_B_QUESTIONS   # 3 questions at 20 marks
            }
            
            # Calculate topic distribution (marks per topic)
            topic_marks_distribution = {}
            for question in all_questions:
                topic_name = question.topic.name
                if topic_name not in topic_marks_distribution:
                    topic_marks_distribution[topic_name] = 0
                topic_marks_distribution[topic_name] += question.marks
            
            # Calculate question type distribution
            question_type_dist = {
                'structured': self.SECTION_A_QUESTIONS,  # Section A questions
                'graph': 1 if question_6_type == 'graph' else 0,
                'essay': 2 if question_6_type == 'graph' else 3  # Questions 7 & 8, or 6, 7 & 8
            }
            
            # Generate unique code
            import time
            unique_code = f"BP2-{int(time.time() * 1000) % 1000000}"
            
            # Create GeneratedPaper
            generated_paper = GeneratedPaper.objects.create(
                paper=self.paper,
                unique_code=unique_code,
                total_marks=self.TOTAL_MARKS,
                total_questions=self.TOTAL_QUESTIONS,
                question_ids=list(self.used_question_ids),
                selected_topics=[str(t.id) for t in self.topics],
                mark_distribution=mark_distribution,
                topic_distribution=topic_marks_distribution,
                question_type_distribution=question_type_dist,
                metadata={
                    'paper_type': 'Biology Paper 2',
                    'generation_algorithm': 'BiologyPaper2Generator',
                    'section_a_questions': self.SECTION_A_QUESTIONS,
                    'section_a_marks_per_question': self.SECTION_A_MARKS_PER_QUESTION,
                    'section_b_questions': self.SECTION_B_QUESTIONS,
                    'section_b_marks_per_question': self.SECTION_B_MARKS_PER_QUESTION,
                    'question_6_type': question_6_type,
                    'topic_distribution': dict(self.topic_distribution),
                    'selected_topics': [str(t.id) for t in self.topics],
                    'question_order': [
                        {
                            'question_number': idx + 1,
                            'question_id': str(q.id),
                            'section': 'A' if idx < 5 else 'B',
                            'type': question_6_type if idx == 5 else ('essay' if idx > 5 else 'structured'),
                            'marks': q.marks,
                            'topic': q.topic.name
                        }
                        for idx, q in enumerate(all_questions)
                    ]
                }
            )
            
            # Update question usage statistics
            for question in all_questions:
                question.times_used += 1
                question.last_used = timezone.now()
                question.save(update_fields=['times_used', 'last_used'])
            
            print(f"Paper saved successfully")
            print(f"  Generated Paper ID: {generated_paper.id}")
            print(f"  Total Questions: {generated_paper.total_questions}")
            print(f"  Total Marks: {generated_paper.total_marks}")
            
            return generated_paper
    
    def generate(self) -> GeneratedPaper:
        """Main generation method"""
        try:
            print(f"\n{'#'*70}")
            print(f"STARTING BIOLOGY PAPER 2 GENERATION")
            print(f"{'#'*70}")
            
            self.load_data()
            self.select_questions()
            generated_paper = self.save_generated_paper()
            
            print(f"\n{'#'*70}")
            print(f"PAPER GENERATION COMPLETED SUCCESSFULLY")
            print(f"{'#'*70}\n")
            
            return generated_paper
            
        except Exception as e:
            print(f"\n{'!'*70}")
            print(f"ERROR DURING PAPER GENERATION")
            print(f"{'!'*70}")
            print(f"Error: {str(e)}")
            raise


# ==================== API ENDPOINTS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_paper2_pool(request):
    """
    Validate if question pool is sufficient for Biology Paper 2 generation
    
    POST /api/papers/biology-paper2/validate
    Body: {
        "paper_id": "uuid",
        "selected_topics": ["topic_uuid_1", "topic_uuid_2", ...]
    }
    """
    try:
        paper_id = request.data.get('paper_id')
        selected_topics = request.data.get('selected_topics', [])
        
        if not paper_id:
            return Response(
                {'error': 'paper_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not selected_topics:
            return Response(
                {'error': 'selected_topics is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Run validation
        result = BiologyPaper2Validator.validate(paper_id, selected_topics)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_biology_paper2(request):
    """
    Generate a Biology Paper 2
    
    POST /api/papers/biology-paper2/generate
    Body: {
        "paper_id": "uuid",
        "selected_topics": ["topic_uuid_1", "topic_uuid_2", ...]
    }
    """
    try:
        paper_id = request.data.get('paper_id')
        selected_topics = request.data.get('selected_topics', [])
        
        if not paper_id:
            return Response(
                {'error': 'paper_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not selected_topics:
            return Response(
                {'error': 'selected_topics is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate first
        validation = BiologyPaper2Validator.validate(paper_id, selected_topics)
        if not validation['valid']:
            return Response(
                {
                    'error': 'Question pool validation failed',
                    'details': validation
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate paper
        generator = BiologyPaper2Generator(paper_id, selected_topics)
        generated_paper = generator.generate()
        
        # Return response (matching frontend expectations)
        return Response(
            {
                'success': True,
                'message': 'Biology Paper 2 generated successfully',
                'paper_id': str(generated_paper.id),
                'generated_paper_id': str(generated_paper.id),
                'unique_code': generated_paper.unique_code,
                'total_questions': generated_paper.total_questions,
                'total_marks': generated_paper.total_marks,
                'status': generated_paper.status,
                'metadata': generated_paper.metadata
            },
            status=status.HTTP_201_CREATED
        )
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Paper generation failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
