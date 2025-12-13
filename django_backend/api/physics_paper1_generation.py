# -*- coding: utf-8 -*-
"""
KCSE Physics Paper 1 Generation Algorithm
Physics Paper 1 has a distinct structure with sections A and B

PAPER STRUCTURE:
- 80 marks total
- Section A: 13 questions = 25 marks
  - 4 questions × 1 mark = 4 marks
  - 6 questions × 2 marks = 12 marks
  - 3 questions × 3 marks = 9 marks
- Section B: 5-6 questions = 55 marks (questions 14-18 or 14-19)
  - Questions are selected to total exactly 55 marks
  - Common marks: 8, 10, 11, 12 marks per question
"""

import random
from collections import defaultdict
from typing import List, Dict, Optional
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Paper, Topic, Section, Question, GeneratedPaper


class PhysicsPaper1Validator:
    """Validates if question pool is sufficient for Physics Paper 1 generation"""
    
    @staticmethod
    def validate(paper_id: str, selected_topic_ids: List[str]) -> Dict:
        """
        Validate question availability before generation
        
        Returns:
            Dict with validation results and recommendations
        """
        # Get sections
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
        
        # Section A questions
        one_mark_questions = 0
        two_mark_questions = 0
        three_mark_questions = 0
        
        if section_a:
            one_mark_questions = Question.objects.filter(
                paper_id=paper_id,
                topic_id__in=selected_topic_ids,
                section=section_a,
                marks=1,
                is_active=True
            ).count()
            
            two_mark_questions = Question.objects.filter(
                paper_id=paper_id,
                topic_id__in=selected_topic_ids,
                section=section_a,
                marks=2,
                is_active=True
            ).count()
            
            three_mark_questions = Question.objects.filter(
                paper_id=paper_id,
                topic_id__in=selected_topic_ids,
                section=section_a,
                marks=3,
                is_active=True
            ).count()
        
        # Section B questions (8-12 marks typically)
        section_b_questions = 0
        if section_b:
            section_b_questions = Question.objects.filter(
                paper_id=paper_id,
                topic_id__in=selected_topic_ids,
                section=section_b,
                marks__gte=8,
                marks__lte=12,
                is_active=True
            ).count()
        
        # Validation
        issues = []
        recommendations = []
        
        if not section_a:
            issues.append("Section A not found in paper")
            recommendations.append("Create Section A for the paper")
        else:
            if one_mark_questions < 4:
                issues.append(f"Section A: {one_mark_questions} one-mark questions (need at least 4)")
                recommendations.append("Add more 1-mark questions to Section A")
            
            if two_mark_questions < 6:
                issues.append(f"Section A: {two_mark_questions} two-mark questions (need at least 6)")
                recommendations.append("Add more 2-mark questions to Section A")
            
            if three_mark_questions < 3:
                issues.append(f"Section A: {three_mark_questions} three-mark questions (need at least 3)")
                recommendations.append("Add more 3-mark questions to Section A")
        
        if not section_b:
            issues.append("Section B not found in paper")
            recommendations.append("Create Section B for the paper")
        elif section_b_questions < 10:
            issues.append(f"Section B: {section_b_questions} questions (need at least 10 questions of 8-12 marks)")
            recommendations.append("Add more 8-12 mark questions to Section B")
        
        return {
            'valid': len(issues) == 0,
            'statistics': {
                'section_a_1mark': one_mark_questions,
                'section_a_2mark': two_mark_questions,
                'section_a_3mark': three_mark_questions,
                'section_b_questions': section_b_questions
            },
            'issues': issues,
            'recommendations': recommendations
        }


class PhysicsPaper1Generator:
    """
    KCSE Physics Paper 1 Generation Algorithm
    
    Paper Structure:
    - Section A: 13 questions = 25 marks (1-13)
      - 4 × 1 mark = 4 marks
      - 6 × 2 marks = 12 marks
      - 3 × 3 marks = 9 marks
    - Section B: 5-6 questions = 55 marks (14-18 or 14-19)
      - Dynamic selection to total exactly 55 marks
    """
    
    # Paper constraints
    TOTAL_MARKS = 80
    SECTION_A_QUESTIONS = 13
    SECTION_A_TOTAL_MARKS = 25
    SECTION_B_TOTAL_MARKS = 55
    SECTION_B_MIN_QUESTIONS = 5
    SECTION_B_MAX_QUESTIONS = 6
    
    # Section A breakdown
    SECTION_A_1MARK_COUNT = 4
    SECTION_A_2MARK_COUNT = 6
    SECTION_A_3MARK_COUNT = 3
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str]):
        self.paper_id = paper_id
        self.selected_topic_ids = selected_topic_ids
        self.paper = None
        self.topics = []
        self.section_a = None
        self.section_b = None
        
        # Question pools
        self.one_mark_pool = []
        self.two_mark_pool = []
        self.three_mark_pool = []
        self.section_b_pool = []
        
        # Selected questions
        self.selected_section_a = []  # 13 questions
        self.selected_section_b = []  # 5-6 questions
        
        # Tracking
        self.used_question_ids = set()
        self.topic_distribution = defaultdict(int)
        
    def load_data(self):
        """Load paper, sections, topics, and questions"""
        print(f"\n{'='*70}")
        print(f"LOADING DATA FOR PHYSICS PAPER 1 GENERATION")
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
        
        # Load Section A questions
        self.one_mark_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_a,
            marks=1,
            is_active=True
        ).select_related('topic', 'section'))
        
        self.two_mark_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_a,
            marks=2,
            is_active=True
        ).select_related('topic', 'section'))
        
        self.three_mark_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_a,
            marks=3,
            is_active=True
        ).select_related('topic', 'section'))
        
        # Load Section B questions (8-12 marks)
        self.section_b_pool = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            section=self.section_b,
            marks__gte=8,
            marks__lte=12,
            is_active=True
        ).select_related('topic', 'section').order_by('marks'))
        
        # Shuffle for randomness
        random.shuffle(self.one_mark_pool)
        random.shuffle(self.two_mark_pool)
        random.shuffle(self.three_mark_pool)
        random.shuffle(self.section_b_pool)
        
        print(f"\nQuestion Pools:")
        print(f"  Section A (1 mark): {len(self.one_mark_pool)} questions")
        print(f"  Section A (2 marks): {len(self.two_mark_pool)} questions")
        print(f"  Section A (3 marks): {len(self.three_mark_pool)} questions")
        print(f"  Section B (8-12 marks): {len(self.section_b_pool)} questions")
        
        # Validation
        if len(self.one_mark_pool) < self.SECTION_A_1MARK_COUNT:
            raise ValueError(
                f"Insufficient 1-mark questions: {len(self.one_mark_pool)} "
                f"(need at least {self.SECTION_A_1MARK_COUNT})"
            )
        
        if len(self.two_mark_pool) < self.SECTION_A_2MARK_COUNT:
            raise ValueError(
                f"Insufficient 2-mark questions: {len(self.two_mark_pool)} "
                f"(need at least {self.SECTION_A_2MARK_COUNT})"
            )
        
        if len(self.three_mark_pool) < self.SECTION_A_3MARK_COUNT:
            raise ValueError(
                f"Insufficient 3-mark questions: {len(self.three_mark_pool)} "
                f"(need at least {self.SECTION_A_3MARK_COUNT})"
            )
        
        if len(self.section_b_pool) < 10:
            raise ValueError(
                f"Insufficient Section B questions: {len(self.section_b_pool)} "
                f"(need at least 10)"
            )
        
        print(f"\nData loaded successfully")
    
    def select_questions(self):
        """Select questions for the paper"""
        print(f"\n{'='*70}")
        print(f"SELECTING QUESTIONS FOR PAPER")
        print(f"{'='*70}")
        
        # Select Section A questions
        print(f"\nSection A: Selecting {self.SECTION_A_QUESTIONS} questions (25 marks total)")
        
        # Select 4 one-mark questions
        print(f"  Selecting {self.SECTION_A_1MARK_COUNT} × 1 mark = {self.SECTION_A_1MARK_COUNT} marks")
        selected_1mark = random.sample(self.one_mark_pool, self.SECTION_A_1MARK_COUNT)
        self.selected_section_a.extend(selected_1mark)
        
        # Select 6 two-mark questions
        print(f"  Selecting {self.SECTION_A_2MARK_COUNT} × 2 marks = {self.SECTION_A_2MARK_COUNT * 2} marks")
        selected_2mark = random.sample(self.two_mark_pool, self.SECTION_A_2MARK_COUNT)
        self.selected_section_a.extend(selected_2mark)
        
        # Select 3 three-mark questions
        print(f"  Selecting {self.SECTION_A_3MARK_COUNT} × 3 marks = {self.SECTION_A_3MARK_COUNT * 3} marks")
        selected_3mark = random.sample(self.three_mark_pool, self.SECTION_A_3MARK_COUNT)
        self.selected_section_a.extend(selected_3mark)
        
        # Shuffle Section A questions to mix marks
        random.shuffle(self.selected_section_a)
        
        # Track used questions
        for q in self.selected_section_a:
            self.used_question_ids.add(str(q.id))
            self.topic_distribution[q.topic.name] += 1
        
        # Display Section A selection
        section_a_marks = sum(q.marks for q in self.selected_section_a)
        print(f"\n  Selected {len(self.selected_section_a)} questions for Section A (Total: {section_a_marks} marks)")
        for i, question in enumerate(self.selected_section_a, 1):
            try:
                preview = question.question_text[:60].encode('ascii', 'ignore').decode('ascii')
            except:
                preview = "Question text contains special characters"
            print(f"    Q{i} ({question.marks}m): {question.topic.name} - {preview}...")
        
        # Select Section B questions (must total exactly 55 marks)
        print(f"\nSection B: Selecting questions to total {self.SECTION_B_TOTAL_MARKS} marks")
        self.selected_section_b = self._select_section_b_questions()
        
        # Display Section B selection
        section_b_marks = sum(q.marks for q in self.selected_section_b)
        print(f"\n  Selected {len(self.selected_section_b)} questions for Section B (Total: {section_b_marks} marks)")
        for i, question in enumerate(self.selected_section_b, 14):
            self.used_question_ids.add(str(question.id))
            self.topic_distribution[question.topic.name] += 1
            try:
                preview = question.question_text[:60].encode('ascii', 'ignore').decode('ascii')
            except:
                preview = "Question text contains special characters"
            print(f"    Q{i} ({question.marks}m): {question.topic.name} - {preview}...")
        
        total_questions = len(self.selected_section_a) + len(self.selected_section_b)
        total_marks = section_a_marks + section_b_marks
        print(f"\nTotal: {total_questions} questions, {total_marks} marks")
        print(f"\nTopic Distribution:")
        for topic, count in sorted(self.topic_distribution.items()):
            print(f"  {topic}: {count} questions")
    
    def _select_section_b_questions(self) -> List[Question]:
        """
        Select Section B questions to total exactly 55 marks
        Uses dynamic programming approach
        """
        target_marks = self.SECTION_B_TOTAL_MARKS
        max_questions = self.SECTION_B_MAX_QUESTIONS
        
        # Try to find combination that totals exactly 55 marks
        # Start with 5 questions, then try 6 if needed
        for num_questions in range(self.SECTION_B_MIN_QUESTIONS, max_questions + 1):
            result = self._find_combination(self.section_b_pool, target_marks, num_questions)
            if result:
                print(f"  Found combination: {num_questions} questions totaling {target_marks} marks")
                return result
        
        # If exact match not found, get as close as possible with 5-6 questions
        print(f"  Warning: Could not find exact 55 marks. Finding closest match...")
        return self._find_closest_combination(self.section_b_pool, target_marks, max_questions)
    
    def _find_combination(self, questions: List[Question], target: int, num_q: int) -> Optional[List[Question]]:
        """
        Find combination of exactly num_q questions that total target marks
        """
        from itertools import combinations
        
        for combo in combinations(questions, num_q):
            if sum(q.marks for q in combo) == target:
                return list(combo)
        
        return None
    
    def _find_closest_combination(self, questions: List[Question], target: int, max_q: int) -> List[Question]:
        """
        Find combination of questions (5-6) that gets closest to target marks
        """
        from itertools import combinations
        
        best_combo = None
        best_diff = float('inf')
        
        for num_q in range(self.SECTION_B_MIN_QUESTIONS, max_q + 1):
            for combo in combinations(questions, num_q):
                total = sum(q.marks for q in combo)
                diff = abs(total - target)
                
                if diff < best_diff:
                    best_diff = diff
                    best_combo = combo
                
                if diff == 0:
                    return list(combo)
        
        return list(best_combo) if best_combo else questions[:self.SECTION_B_MIN_QUESTIONS]
    
    def save_generated_paper(self) -> GeneratedPaper:
        """Save the generated paper to database"""
        print(f"\n{'='*70}")
        print(f"SAVING GENERATED PAPER")
        print(f"{'='*70}")
        
        with transaction.atomic():
            # Combine all selected questions in order
            all_questions = self.selected_section_a + self.selected_section_b
            
            # Calculate total marks
            total_marks = sum(q.marks for q in all_questions)
            section_a_marks = sum(q.marks for q in self.selected_section_a)
            section_b_marks = sum(q.marks for q in self.selected_section_b)
            
            # Calculate mark distribution
            mark_counts = defaultdict(int)
            for q in all_questions:
                mark_counts[str(q.marks)] += 1
            
            # Calculate topic distribution (marks per topic)
            topic_marks_distribution = {}
            for question in all_questions:
                topic_name = question.topic.name
                if topic_name not in topic_marks_distribution:
                    topic_marks_distribution[topic_name] = 0
                topic_marks_distribution[topic_name] += question.marks
            
            # Generate unique code
            import time
            unique_code = f"PP1-{int(time.time() * 1000) % 1000000}"
            
            # Create GeneratedPaper
            generated_paper = GeneratedPaper.objects.create(
                paper=self.paper,
                unique_code=unique_code,
                total_questions=len(all_questions),
                total_marks=total_marks,
                question_ids=[str(q.id) for q in all_questions],
                selected_topics=[str(t.id) for t in self.topics],
                mark_distribution=dict(mark_counts),
                topic_distribution=topic_marks_distribution,
                question_type_distribution={
                    'section_a': len(self.selected_section_a),
                    'section_b': len(self.selected_section_b)
                },
                status='validated',
                validation_passed=True,
                metadata={
                    'paper_type': 'Paper 1',
                    'section_a_marks': section_a_marks,
                    'section_b_marks': section_b_marks,
                    'section_a_questions': len(self.selected_section_a),
                    'section_b_questions': len(self.selected_section_b)
                }
            )
            
            print(f"✓ Generated Paper saved: {unique_code}")
            print(f"  - ID: {generated_paper.id}")
            print(f"  - Total Questions: {len(all_questions)}")
            print(f"  - Total Marks: {total_marks}")
            print(f"  - Section A: {len(self.selected_section_a)} questions ({section_a_marks} marks)")
            print(f"  - Section B: {len(self.selected_section_b)} questions ({section_b_marks} marks)")
            
            return generated_paper
    
    def generate(self) -> GeneratedPaper:
        """Main generation workflow"""
        self.load_data()
        self.select_questions()
        generated_paper = self.save_generated_paper()
        return generated_paper


# ==================== API ENDPOINTS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_physics_paper1(request):
    """
    Validate Physics Paper 1 generation prerequisites
    POST /api/papers/physics-paper1/validate
    """
    try:
        paper_id = request.data.get('paper_id')
        selected_topic_ids = request.data.get('topic_ids', [])
        
        if not paper_id:
            return Response(
                {'error': 'paper_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not selected_topic_ids:
            return Response(
                {'error': 'topic_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate
        validation_result = PhysicsPaper1Validator.validate(paper_id, selected_topic_ids)
        
        return Response(validation_result)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_physics_paper1(request):
    """
    Generate Physics Paper 1
    POST /api/papers/physics-paper1/generate
    
    """
    import traceback
    
    print("=" * 70)
    print("PHYSICS PAPER 1 GENERATION ENDPOINT HIT")
    print("=" * 70)
    print(f"Request method: {request.method}")
    print(f"Request data: {request.data}")
    print(f"Request user: {request.user}")
    
    
    try:
        paper_id = request.data.get('paper_id')
        selected_topic_ids = request.data.get('topic_ids', [])
        
        print(f"Extracted paper_id: {paper_id}")
        print(f"Extracted topic_ids: {selected_topic_ids}")
        
        if not paper_id:
            return Response(
                {'error': 'paper_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not selected_topic_ids:
            return Response(
                {'error': 'topic_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate paper
        generator = PhysicsPaper1Generator(paper_id, selected_topic_ids)
        generated_paper = generator.generate()
        
        return Response({
            'success': True,
            'message': 'Physics Paper 1 generated successfully',
            'paper_id': str(generated_paper.id),
            'generated_paper_id': str(generated_paper.id),
            'unique_code': generated_paper.unique_code,
            'total_questions': generated_paper.total_questions,
            'total_marks': generated_paper.total_marks,
            'section_a_questions': len(generator.selected_section_a),
            'section_b_questions': len(generator.selected_section_b),
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
