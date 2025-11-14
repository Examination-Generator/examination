"""
KCSE Biology Paper 1 Generation Algorithm - Final Production Version
Based on KCSE Biology Paper 1 patterns (2010-2024)

KEY CONCEPT:
- Nested questions are stored as SINGLE database records with cumulative marks
- Example: A question with parts (a) 2 marks + (b) 2 marks = stored as ONE question with marks=4
- Algorithm counts nested questions as 1 question each (not as multiple parts)
- In the final paper, the parts (a, b, c) are displayed normally from nested_parts JSON

PAPER STRUCTURE:
- 80 marks total
- 28-32 questions (each nested question = 1 question)
- Nested questions: 10-16 questions with 2-8 marks each (cumulative)
- Non-nested: Only 1, 2, or 3 marks
"""

import random
import time
from collections import defaultdict
from typing import List, Dict, Optional
from django.db import transaction
from django.db.models import Q, Count, F
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Paper, Topic, Section, Question, GeneratedPaper


class QuestionPoolValidator:
    """Validates if question pool is sufficient for paper generation"""
    
    @staticmethod
    def validate(paper_id: str, selected_topic_ids: List[str]) -> Dict:
        """
        Validate question availability before generation
        
        Returns:
            Dict with validation results and recommendations
        """
        questions = Question.objects.filter(
            paper_id=paper_id,
            topic_id__in=selected_topic_ids,
            is_active=True
        )
        
        total = questions.count()
        
        # Nested questions (single questions with is_nested=True, marks 2-8)
        nested = questions.filter(is_nested=True, marks__gte=2, marks__lte=8).count()
        
        # Non-nested questions (marks 1, 2, 3 only)
        one_mark = questions.filter(is_nested=False, marks=1).count()
        two_mark = questions.filter(is_nested=False, marks=2).count()
        three_mark = questions.filter(is_nested=False, marks=3).count()
        
        # Per topic distribution
        topic_dist = {}
        for topic_id in selected_topic_ids:
            count = questions.filter(topic_id=topic_id).count()
            topic_dist[str(topic_id)] = count
        
        # Validation
        issues = []
        recommendations = []
        
        if total < 50:
            issues.append(f"Total questions: {total} (need at least 50)")
            recommendations.append("Add more questions across all topics")
        
        if nested < 15:
            issues.append(f"Nested questions: {nested} (need at least 15)")
            recommendations.append("Add more multi-part questions with cumulative marks 2-8")
        
        if one_mark < 15:
            issues.append(f"1-mark questions: {one_mark} (need at least 15)")
            recommendations.append("Add more 1-mark questions (name/identify type)")
        
        if two_mark < 20:
            issues.append(f"2-mark questions: {two_mark} (need at least 20)")
            recommendations.append("Add more 2-mark questions (state/give reasons type)")
        
        if three_mark < 15:
            issues.append(f"3-mark questions: {three_mark} (need at least 15)")
            recommendations.append("Add more 3-mark questions (explain/describe type)")
        
        # Topic balance check
        num_topics = len(selected_topic_ids)
        min_per_topic = 15
        for topic_id, count in topic_dist.items():
            if count < min_per_topic:
                issues.append(f"Topic {topic_id}: {count} questions (need at least {min_per_topic})")
                recommendations.append(f"Add more questions to topic {topic_id}")
        
        return {
            'valid': len(issues) == 0,
            'statistics': {
                'total_questions': total,
                'nested_questions': nested,
                'one_mark_questions': one_mark,
                'two_mark_questions': two_mark,
                'three_mark_questions': three_mark,
                'num_topics': num_topics,
                'topic_distribution': topic_dist
            },
            'issues': issues,
            'recommendations': recommendations
        }


class BiologyPaperGenerator:
    """
    KCSE Biology Paper 1 Generation Algorithm
    
    IMPORTANT: Each nested question is counted as ONE question regardless of parts
    - Nested question with marks=5 (parts a+b+c) = 1 question
    - Non-nested question with marks=2 = 1 question
    
    Target Structure:
    - 80 marks total
    - 28-32 questions (target: 30)
    - Nested: 10-16 questions (each stored as single DB record with cumulative marks 2-8)
    - Non-nested: Remaining questions (only 1, 2, 3 marks)
    """
    
    # Core constraints
    TOTAL_MARKS = 80
    TARGET_QUESTIONS = 40  # Real KCSE has ~40 questions
    MIN_QUESTIONS = 38
    MAX_QUESTIONS = 42
    
    # Nested question constraints (each nested = 1 question)
    MIN_NESTED_QUESTIONS = 8   # Real KCSE: 8-12 multi-part questions
    MAX_NESTED_QUESTIONS = 12
    TARGET_NESTED_QUESTIONS = 10
    MIN_NESTED_TOTAL_MARKS = 20  # Real KCSE: 20-35 marks total from nested
    MAX_NESTED_TOTAL_MARKS = 35
    MIN_NESTED_QUESTION_MARKS = 2  # Cumulative marks per nested question
    MAX_NESTED_QUESTION_MARKS = 8
    
    # Mark distribution for non-nested (as ratio of remaining marks)
    # Real KCSE: 1-mark questions dominate (~35-40% of paper)
    TARGET_1_MARK_RATIO = 0.60  # 60% of remaining marks go to 1-mark questions
    TARGET_2_MARK_RATIO = 0.30  # 30% to 2-mark questions
    TARGET_3_MARK_RATIO = 0.10  # 10% to 3-mark questions
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str]):
        self.paper_id = paper_id
        self.selected_topic_ids = selected_topic_ids
        self.paper = None
        self.topics = []
        
        # Question pools
        self.nested_questions = []  # List of nested questions (each with cumulative marks)
        self.non_nested_by_marks = {1: [], 2: [], 3: []}
        
        # Selected questions tracking
        self.selected_questions = []  # List of Question objects
        self.used_question_ids = set()
        
        # Statistics
        self.current_total_marks = 0
        self.current_nested_marks = 0
        self.current_nested_count = 0
        self.topic_marks = defaultdict(int)
        self.topic_question_count = defaultdict(int)
        self.section_distribution = defaultdict(int)
        
        # Generation metadata
        self.generation_attempts = 0
        self.start_time = None
    
    def load_data(self):
        """Load paper, topics, and questions with optimization"""
        print(f"\n{'='*70}")
        print(f"LOADING DATA FOR PAPER GENERATION")
        print(f"{'='*70}")
        
        # Load paper
        self.paper = Paper.objects.select_related('subject').get(
            id=self.paper_id,
            is_active=True
        )
        print(f"Paper: {self.paper.name} ({self.paper.subject.name})")
        
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
        
        # Load all questions
        questions = list(Question.objects.filter(
            topic__in=self.topics,
            paper=self.paper,
            is_active=True
        ).select_related('topic', 'section', 'subject'))
        
        if not questions:
            raise ValueError("No questions found for selected topics")
        
        print(f"\nTotal Questions Loaded: {len(questions)}")
        
        # Separate nested and non-nested questions
        # CRITICAL: Each nested question is ONE question with cumulative marks
        for question in questions:
            if question.is_nested:
                # Nested question: cumulative marks should be 2-8
                if self.MIN_NESTED_QUESTION_MARKS <= question.marks <= self.MAX_NESTED_QUESTION_MARKS:
                    self.nested_questions.append(question)
            else:
                # Non-nested: only 1, 2, 3 marks
                if question.marks in [1, 2, 3]:
                    self.non_nested_by_marks[question.marks].append(question)
        
        # Shuffle for randomness
        random.shuffle(self.nested_questions)
        for mark_value in self.non_nested_by_marks:
            random.shuffle(self.non_nested_by_marks[mark_value])
        
        print(f"\nQuestion Distribution:")
        print(f"  Nested questions (2-8 marks cumulative): {len(self.nested_questions)}")
        
        # Show nested mark distribution
        nested_mark_dist = defaultdict(int)
        for q in self.nested_questions:
            nested_mark_dist[q.marks] += 1
        print(f"    Distribution by marks: {dict(nested_mark_dist)}")
        
        print(f"  Non-nested questions:")
        print(f"    1-mark: {len(self.non_nested_by_marks[1])}")
        print(f"    2-mark: {len(self.non_nested_by_marks[2])}")
        print(f"    3-mark: {len(self.non_nested_by_marks[3])}")
        
        # Validation
        if len(self.nested_questions) < self.MIN_NESTED_QUESTIONS:
            raise ValueError(
                f"Insufficient nested questions: {len(self.nested_questions)} "
                f"(need at least {self.MIN_NESTED_QUESTIONS})"
            )
        
        for mark in [1, 2, 3]:
            if len(self.non_nested_by_marks[mark]) < 10:
                raise ValueError(
                    f"Insufficient {mark}-mark questions: "
                    f"{len(self.non_nested_by_marks[mark])} (need at least 10)"
                )
        
        print(f"\n[OK] Data loaded successfully")
        print(f"{'='*70}\n")
    
    def select_nested_questions(self) -> bool:
        """
        Select nested questions first
        Each nested question = 1 question (with cumulative marks 2-8)
        
        Target:
        - 10-16 questions
        - 35-50 total marks from all nested questions
        """
        print(f"\n{'-'*70}")
        print(f"PHASE 1: SELECTING NESTED QUESTIONS")
        print(f"{'-'*70}")
        print(f"Target: {self.MIN_NESTED_QUESTIONS}-{self.MAX_NESTED_QUESTIONS} questions")
        print(f"Target marks: {self.MIN_NESTED_TOTAL_MARKS}-{self.MAX_NESTED_TOTAL_MARKS} total marks\n")
        
        available = [q for q in self.nested_questions if q.id not in self.used_question_ids]
        
        if len(available) < self.MIN_NESTED_QUESTIONS:
            print(f"[X] Not enough nested questions: {len(available)} available\n")
            return False
        
        selected = []
        total_marks = 0
        
        # Sort by marks for variety (mix of different mark values)
        available_sorted = sorted(available, key=lambda q: (q.marks, random.random()))
        
        # Greedy selection with topic balancing
        for question in available_sorted:
            # Stop if we've reached max questions
            if len(selected) >= self.MAX_NESTED_QUESTIONS:
                break
            
            # Stop if we've reached max marks
            if total_marks >= self.MAX_NESTED_TOTAL_MARKS:
                break
            
            new_marks = total_marks + question.marks
            new_count = len(selected) + 1
            
            # Check if we should add this question
            if new_count >= self.MIN_NESTED_QUESTIONS and total_marks >= self.MIN_NESTED_TOTAL_MARKS:
                # We have minimum requirements, decide if we should add more
                if new_marks <= self.MAX_NESTED_TOTAL_MARKS:
                    # Check topic balance before adding
                    if self._should_add_question(question, selected):
                        selected.append(question)
                        total_marks += question.marks
                        print(f"  Added: Q{len(selected)} - {question.marks} marks - {question.topic.name[:30]}")
                else:
                    # Would exceed max marks, stop
                    break
            else:
                # Still building minimum, add the question
                selected.append(question)
                total_marks += question.marks
                print(f"  Added: Q{len(selected)} - {question.marks} marks - {question.topic.name[:30]}")
        
        # Validate selection
        count_valid = self.MIN_NESTED_QUESTIONS <= len(selected) <= self.MAX_NESTED_QUESTIONS
        marks_valid = self.MIN_NESTED_TOTAL_MARKS <= total_marks <= self.MAX_NESTED_TOTAL_MARKS
        
        if not (count_valid and marks_valid):
            print(f"\n[X] Selection failed:")
            print(f"  Questions: {len(selected)} (need {self.MIN_NESTED_QUESTIONS}-{self.MAX_NESTED_QUESTIONS})")
            print(f"  Marks: {total_marks} (need {self.MIN_NESTED_TOTAL_MARKS}-{self.MAX_NESTED_TOTAL_MARKS})\n")
            return False
        
        # Commit selection
        self.selected_questions.extend(selected)
        self.used_question_ids.update(q.id for q in selected)
        self.current_total_marks = total_marks
        self.current_nested_marks = total_marks
        self.current_nested_count = len(selected)
        
        # Update tracking
        for question in selected:
            topic_id = str(question.topic.id)
            self.topic_marks[topic_id] += question.marks
            self.topic_question_count[topic_id] += 1
            if question.section:
                self.section_distribution[str(question.section.id)] += 1
        
        print(f"\n[OK] Nested Selection Success:")
        print(f"  Questions: {len(selected)}")
        print(f"  Total marks: {total_marks}")
        print(f"  Topic distribution: {dict(self.topic_question_count)}")
        print(f"{'-'*70}\n")
        
        return True
    
    def _should_add_question(self, question: Question, current_selected: List[Question]) -> bool:
        """
        Determine if question should be added based on topic balance
        Ensures even distribution across selected topics
        """
        if not current_selected:
            return True
        
        topic_id = str(question.topic.id)
        current_topic_count = self.topic_question_count[topic_id]
        
        # Calculate average questions per topic
        avg_per_topic = len(current_selected) / len(self.topics) if len(self.topics) > 0 else 0
        
        # Prefer topics with fewer questions (allow up to 50% above average)
        if current_topic_count <= avg_per_topic * 1.5:
            return True
        
        # Random chance for variety even if topic is over-represented
        return random.random() < 0.3
    
    def select_non_nested_questions(self) -> bool:
        """
        Fill remaining marks with non-nested questions (1, 2, 3 marks only)
        Each non-nested question also counts as 1 question
        
        Strategy: Target distribution
        - 15% of remaining marks from 1-mark questions
        - 40% from 2-mark questions
        - 45% from 3-mark questions
        """
        remaining_marks = self.TOTAL_MARKS - self.current_total_marks
        max_additional_questions = self.MAX_QUESTIONS - len(self.selected_questions)
        
        print(f"{'-'*70}")
        print(f"PHASE 2: SELECTING NON-NESTED QUESTIONS")
        print(f"{'-'*70}")
        print(f"Remaining marks to fill: {remaining_marks}")
        print(f"Max additional questions: {max_additional_questions}")
        print(f"Current question count: {len(self.selected_questions)}\n")
        
        if remaining_marks <= 0:
            print("[OK] No more marks needed\n")
            return True
        
        if max_additional_questions <= 0:
            print("[X] Already at maximum question count\n")
            return False
        
        # Calculate target marks for each type
        target_1_marks = int(remaining_marks * self.TARGET_1_MARK_RATIO)
        target_2_marks = int(remaining_marks * self.TARGET_2_MARK_RATIO)
        target_3_marks = remaining_marks - target_1_marks - target_2_marks
        
        print(f"Target distribution:")
        print(f"  1-mark questions: ~{target_1_marks} marks")
        print(f"  2-mark questions: ~{target_2_marks} marks")
        print(f"  3-mark questions: ~{target_3_marks} marks\n")
        
        selected = []
        current_1_marks = 0
        current_2_marks = 0
        current_3_marks = 0
        
        # Fill with strategy
        max_iterations = remaining_marks * 4
        iterations = 0
        
        while remaining_marks > 0 and len(selected) < max_additional_questions and iterations < max_iterations:
            iterations += 1
            
            # Determine priority order based on how far we are from targets
            priorities = []
            
            # Prioritize marks that are furthest from target
            if current_2_marks < target_2_marks and remaining_marks >= 2:
                priorities.append(2)
            if current_3_marks < target_3_marks and remaining_marks >= 3:
                priorities.append(3)
            if current_1_marks < target_1_marks and remaining_marks >= 1:
                priorities.append(1)
            
            # If all targets met, fill with whatever fits
            if not priorities:
                if remaining_marks >= 3:
                    priorities = [3, 2, 1]
                elif remaining_marks >= 2:
                    priorities = [2, 1]
                else:
                    priorities = [1]
            
            question_added = False
            
            for mark_value in priorities:
                if mark_value > remaining_marks:
                    continue
                
                available = [
                    q for q in self.non_nested_by_marks[mark_value]
                    if q.id not in self.used_question_ids
                ]
                
                if available:
                    question = self._select_best_non_nested(available)
                    
                    if question:
                        selected.append(question)
                        self.used_question_ids.add(question.id)
                        remaining_marks -= question.marks
                        
                        # Track marks
                        if question.marks == 1:
                            current_1_marks += 1
                        elif question.marks == 2:
                            current_2_marks += 2
                        elif question.marks == 3:
                            current_3_marks += 3
                        
                        # Update tracking
                        topic_id = str(question.topic.id)
                        self.topic_marks[topic_id] += question.marks
                        self.topic_question_count[topic_id] += 1
                        if question.section:
                            self.section_distribution[str(question.section.id)] += 1
                        
                        if len(selected) % 5 == 0:  # Print every 5 questions
                            print(f"  Progress: {len(selected)} questions, {remaining_marks} marks remaining")
                        
                        question_added = True
                        break
            
            if not question_added:
                print(f"\n[X] Cannot fill remaining {remaining_marks} marks with available questions\n")
                return False
        
        # Check if we successfully filled to exactly 80 marks
        if remaining_marks == 0:
            self.selected_questions.extend(selected)
            self.current_total_marks = self.TOTAL_MARKS
            
            total_questions = len(self.selected_questions)
            
            if self.MIN_QUESTIONS <= total_questions <= self.MAX_QUESTIONS:
                print(f"\n[OK] Non-Nested Selection Success:")
                print(f"  Questions added: {len(selected)}")
                print(f"  Total paper questions: {total_questions}")
                print(f"  Distribution: {current_1_marks//1}×1mk, {current_2_marks//2}×2mk, {current_3_marks//3}×3mk")
                print(f"{'-'*70}\n")
                return True
            else:
                print(f"\n[X] Total question count out of range: {total_questions}")
                print(f"  (Need {self.MIN_QUESTIONS}-{self.MAX_QUESTIONS})\n")
                return False
        
        print(f"\n[X] Failed to fill exactly. Remaining marks: {remaining_marks}\n")
        return False
    
    def _select_best_non_nested(self, available: List[Question]) -> Optional[Question]:
        """
        Select best non-nested question considering topic distribution
        Prefers topics with fewer questions
        """
        if not available:
            return None
        
        # Score based on topic balance
        scored = []
        total_selected = len(self.selected_questions)
        avg_per_topic = total_selected / len(self.topics) if len(self.topics) > 0 else 0
        
        for question in available:
            topic_id = str(question.topic.id)
            current_count = self.topic_question_count[topic_id]
            
            # Lower score = better (prefer topics with fewer questions)
            score = current_count - avg_per_topic
            
            # Add small random factor for variety
            score += random.random() * 0.2
            
            scored.append((score, question))
        
        # Sort by score (ascending)
        scored.sort(key=lambda x: x[0])
        
        # Pick from top 3 candidates for variety
        if len(scored) > 3:
            return random.choice([q for _, q in scored[:3]])
        else:
            return scored[0][1]
    
    def generate(self) -> Dict:
        """
        Main generation algorithm
        
        Returns:
            Dict containing complete paper data
        """
        self.start_time = time.time()
        self.generation_attempts = 0
        
        max_attempts = 25
        
        print(f"\n{'='*70}")
        print(f"STARTING KCSE BIOLOGY PAPER 1 GENERATION")
        print(f"{'='*70}\n")
        
        while self.generation_attempts < max_attempts:
            self.generation_attempts += 1
            
            print(f"\n{'#'*70}")
            print(f"GENERATION ATTEMPT #{self.generation_attempts}")
            print(f"{'#'*70}\n")
            
            # Reset state
            self._reset_state()
            
            # Step 1: Select nested questions (each nested = 1 question)
            if not self.select_nested_questions():
                print(f"[ATTEMPT {self.generation_attempts}] Failed at nested selection phase\n")
                continue
            
            # Step 2: Fill with non-nested questions
            if not self.select_non_nested_questions():
                print(f"[ATTEMPT {self.generation_attempts}] Failed at non-nested selection phase\n")
                continue
            
            # Success!
            generation_time = time.time() - self.start_time
            
            print(f"\n{'='*70}")
            print(f"[OK][OK][OK] PAPER GENERATED SUCCESSFULLY! [OK][OK][OK]")
            print(f"{'='*70}")
            print(f"Generation Time: {generation_time:.2f} seconds")
            print(f"Attempts: {self.generation_attempts}")
            print(f"Total Questions: {len(self.selected_questions)}")
            print(f"Total Marks: {self.current_total_marks}")
            print(f"Nested Questions: {self.current_nested_count} ({self.current_nested_marks} marks)")
            print(f"Non-Nested Questions: {len(self.selected_questions) - self.current_nested_count} ({self.current_total_marks - self.current_nested_marks} marks)")
            print(f"{'='*70}\n")
            
            return self._build_result(generation_time)
        
        # Failed after all attempts
        raise Exception(
            f"Failed to generate paper after {max_attempts} attempts.\n\n"
            f"Question Pool Analysis:\n"
            f"  Nested questions (2-8 marks): {len(self.nested_questions)}\n"
            f"  1-mark questions: {len(self.non_nested_by_marks[1])}\n"
            f"  2-mark questions: {len(self.non_nested_by_marks[2])}\n"
            f"  3-mark questions: {len(self.non_nested_by_marks[3])}\n\n"
            f"Recommendations:\n"
            f"  1. Ensure at least 15 nested questions per topic\n"
            f"  2. Ensure at least 20 questions of each mark value (1, 2, 3)\n"
            f"  3. Balance questions across selected topics\n"
            f"  4. Check that nested questions have cumulative marks 2-8"
        )
    
    def _reset_state(self):
        """Reset all state for new generation attempt"""
        self.selected_questions = []
        self.used_question_ids = set()
        self.current_total_marks = 0
        self.current_nested_marks = 0
        self.current_nested_count = 0
        self.topic_marks = defaultdict(int)
        self.topic_question_count = defaultdict(int)
        self.section_distribution = defaultdict(int)
    
    def _build_result(self, generation_time: float) -> Dict:
        """Build complete result dictionary with all paper data"""
        
        # Calculate distributions
        mark_distribution = defaultdict(int)
        question_type_distribution = defaultdict(int)
        difficulty_distribution = defaultdict(int)
        
        for question in self.selected_questions:
            mark_distribution[question.marks] += 1
            if question.kcse_question_type:
                question_type_distribution[question.kcse_question_type] += 1
            if question.difficulty:
                difficulty_distribution[question.difficulty] += 1
        
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
                'question_inline_images': question.question_inline_images,
                'answer_inline_images': question.answer_inline_images,
                'question_image_positions': question.question_image_positions,
                'answer_image_positions': question.answer_image_positions,
                'question_answer_lines': question.question_answer_lines,
                'answer_answer_lines': question.answer_answer_lines,
            })
        
        return {
            'paper': {
                'id': str(self.paper.id),
                'name': self.paper.name,
                'subject': {
                    'id': str(self.paper.subject.id),
                    'name': self.paper.subject.name
                },
                'total_marks': self.TOTAL_MARKS,
                'time_allocation': self.paper.time_allocation
            },
            'questions': questions_data,
            'statistics': {
                'total_marks': self.current_total_marks,
                'total_questions': len(self.selected_questions),
                'nested_questions_count': self.current_nested_count,
                'nested_questions_marks': self.current_nested_marks,
                'non_nested_questions_count': len(self.selected_questions) - self.current_nested_count,
                'non_nested_questions_marks': self.current_total_marks - self.current_nested_marks,
                'mark_distribution': dict(mark_distribution),
                'question_type_distribution': dict(question_type_distribution),
                'difficulty_distribution': dict(difficulty_distribution),
                'topic_distribution': dict(self.topic_marks),
                'topic_question_count': dict(self.topic_question_count),
                'section_distribution': dict(self.section_distribution),
                'generation_attempts': self.generation_attempts,
                'generation_time_seconds': round(generation_time, 2)
            }
        }