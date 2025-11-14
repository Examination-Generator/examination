"""
KCSE Biology Paper 1 Generation Algorithm
Database-driven paper generation with comprehensive validation
"""

import random
import logging
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from django.db.models import Q, Count
from django.utils import timezone

from .models import (
    Paper, Topic, Question, PaperConfiguration, 
    GeneratedPaper, Subject
)

logger = logging.getLogger(__name__)


class PaperGenerationException(Exception):
    """Custom exception for paper generation errors"""
    pass


class BiologyPaper1Generator:
    """
    KCSE Biology Paper 1 Generator
    
    Implements the complete algorithm as described in the specification.
    All configuration data is retrieved from the database.
    """
    
    def __init__(self, paper_id: str, selected_topic_ids: List[str], user):
        """
        Initialize the paper generator
        
        Args:
            paper_id: UUID of the paper (Biology Paper 1)
            selected_topic_ids: List of topic UUIDs selected by user
            user: User who is generating the paper
        """
        self.paper_id = paper_id
        self.selected_topic_ids = selected_topic_ids
        self.user = user
        
        # Will be populated during initialization
        self.paper = None
        self.config = None
        self.selected_topics = []
        self.topic_constraints = {}
        
        # Tracking variables for generation
        self.total_marks = 0
        self.selected_questions = []
        self.selected_question_ids = set()
        
        # Counters - Extended to support nested questions up to 8 marks
        self.mark_value_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
        self.topic_mark_counts = {}
        self.question_type_counts = {
            'name_identify': 0,
            'state_give_reasons': 0,
            'distinguish': 0,
            'explain_account': 0,
            'describe': 0,
            'calculate': 0,
        }
        
        # Statistics
        self.generation_start_time = None
        self.backtracking_count = 0
        self.generation_attempts = 0
        # Target question count for this generation (will be set during init)
        self.target_question_count = None
        # Target distribution - exact counts for each mark value
        self.target_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        # Nested question targets
        self.target_nested_questions = 0
        self.target_nested_marks = 0
        self.actual_nested_marks = 0  # Actual marks achieved in nested phase
        self.selected_nested_questions = []
        self.selected_standalone_questions = []    
    def generate(self) -> GeneratedPaper:
        """
        Main entry point for paper generation
        
        Returns:
            GeneratedPaper: The successfully generated and validated paper
        """
        self.generation_start_time = time.time()
        
        try:
            # Step 1: Initialize and retrieve database configuration
            logger.info(f"[STEP 1] Initializing paper generation for paper {self.paper_id}")
            self._initialize_from_database()
            
            # Step 2: Apply proportional adjustment if needed
            logger.info(f"[STEP 2] Applying proportional adjustments for {len(self.selected_topics)} topics")
            self._apply_proportional_adjustment()
            
            # Step 3-6: Generate paper with retries
            max_attempts = self.config.max_generation_attempts
            
            for attempt in range(1, max_attempts + 1):
                self.generation_attempts = attempt
                logger.info(f"[ATTEMPT {attempt}/{max_attempts}] Starting paper generation")
                
                try:
                    # Step 3: Iterative question selection
                    self._reset_tracking_variables()
                    self._select_questions()
                    
                    # Step 5: Arrange questions
                    logger.info(f"[STEP 5] Arranging {len(self.selected_questions)} questions")
                    self._arrange_questions()
                    
                    # Step 7: Comprehensive validation
                    logger.info(f"[STEP 7] Validating generated paper")
                    validation_report = self._validate_paper()
                    
                    if validation_report['all_passed']:
                        # Step 8: Generate output and save
                        logger.info(f"[STEP 8] Validation passed! Creating GeneratedPaper record")
                        generated_paper = self._create_generated_paper(validation_report)
                        
                        generation_time = time.time() - self.generation_start_time
                        logger.info(f"[SUCCESS] Paper generated in {generation_time:.2f}s after {attempt} attempt(s)")
                        
                        return generated_paper
                    else:
                        logger.warning(f"[ATTEMPT {attempt}] Validation failed: {validation_report['failed_checks']}")
                        
                except PaperGenerationException as e:
                    logger.warning(f"[ATTEMPT {attempt}] Generation failed: {str(e)}")
                    continue
            
            # All attempts exhausted
            raise PaperGenerationException(
                f"Failed to generate valid paper after {max_attempts} attempts"
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Paper generation failed: {str(e)}", exc_info=True)
            raise
    
    def _initialize_from_database(self):
        """
        Step 1: Retrieve all configuration data from database
        """
        # Retrieve paper
        try:
            self.paper = Paper.objects.select_related('subject').get(
                id=self.paper_id,
                is_active=True
            )
        except Paper.DoesNotExist:
            raise PaperGenerationException(f"Paper {self.paper_id} not found or inactive")
        
        # Retrieve or create paper configuration
        self.config, created = PaperConfiguration.objects.get_or_create(
            paper=self.paper,
            defaults={
                # Default values are already set in model
            }
        )
        
        if created:
            logger.info(f"[INIT] Created default configuration for {self.paper}")
        
        # Retrieve selected topics
        self.selected_topics = list(
            Topic.objects.filter(
                id__in=self.selected_topic_ids,
                paper=self.paper,
                is_active=True
            ).order_by('name')
        )
        
        if not self.selected_topics:
            raise PaperGenerationException("No valid topics selected")
        
        logger.info(f"[INIT] Loaded {len(self.selected_topics)} topics: {[t.name for t in self.selected_topics]}")
        
        # Initialize topic tracking
        for topic in self.selected_topics:
            self.topic_mark_counts[str(topic.id)] = 0
            self.topic_constraints[str(topic.id)] = {
                'name': topic.name,
                'min_marks': topic.min_marks,
                'max_marks': topic.max_marks,
                'original_min': topic.min_marks,
                'original_max': topic.max_marks,
            }
        
        logger.info(f"[INIT] Paper: {self.paper.name}, Total Marks: {self.paper.total_marks}, "
                   f"Time: {self.paper.time_allocation} mins")
        
        # Calculate exact question distribution based on percentage of MARKS
        # This will also set self.target_question_count
        self._calculate_target_distribution()
    
    def _calculate_target_distribution(self):
        """
        Calculate distribution for NESTED and STANDALONE questions.
        
        KCSE Biology Paper 1 Structure:
        - Total: 22-30 questions, 80 marks
        - Nested questions: 10-18 questions (50-65 marks)
          * Each nested question has parts (a, b, c, d) with varying marks
          * Total marks = sum of all parts
        - Standalone questions: Top-up to complete 80 marks
          * Prefer 2-mark and 3-mark questions
          * Use 1-mark only if 1 mark remaining (79→80)
          * Use 4-mark, 5-mark, or 6-mark if that exact amount remaining
        
        Algorithm:
        1. Randomly select number of nested questions (10-18)
        2. Randomly select total marks from nested (50-65 marks)
        3. Calculate remaining marks (80 - nested_marks)
        4. Fill remaining marks with standalone questions
        5. Verify total questions in 22-30 range
        """
        total_marks_target = self.paper.total_marks  # 80
        min_total_questions = 22
        max_total_questions = 30
        
        # Nested question constraints
        min_nested_questions = 10
        max_nested_questions = 18
        min_nested_marks = 50
        max_nested_marks = 65
        
        max_attempts = 100
        
        for attempt in range(max_attempts):
            # Step 1: Randomly decide nested question count and marks
            num_nested_questions = random.randint(min_nested_questions, max_nested_questions)
            total_nested_marks = random.randint(min_nested_marks, max_nested_marks)
            
            # Step 2: Calculate remaining marks for standalone questions
            remaining_marks = total_marks_target - total_nested_marks
            
            # Step 3: Determine standalone question distribution
            # Prefer 2-mark and 3-mark, use 1-mark/4-mark only for exact completion
            standalone_counts = self._distribute_standalone_marks(remaining_marks)
            
            if standalone_counts is None:
                continue  # This distribution didn't work, try again
            
            # Step 4: Calculate total question count
            total_standalone_questions = sum(standalone_counts.values())
            total_questions = num_nested_questions + total_standalone_questions
            
            # Step 5: Verify constraints
            if min_total_questions <= total_questions <= max_total_questions:
                # SUCCESS! Valid distribution
                logger.info(f"[DISTRIBUTION] Valid distribution found on attempt {attempt + 1}")
                logger.info(f"[DISTRIBUTION] Nested questions: {num_nested_questions} questions = {total_nested_marks} marks")
                logger.info(f"[DISTRIBUTION] Standalone questions:")
                
                standalone_total_marks = 0
                for mark_value, count in standalone_counts.items():
                    if count > 0:
                        marks = count * mark_value
                        standalone_total_marks += marks
                        logger.info(f"  {mark_value}-mark: {count} questions = {marks} marks")
                
                logger.info(f"[DISTRIBUTION] Total standalone: {total_standalone_questions} questions = {standalone_total_marks} marks")
                logger.info(f"[DISTRIBUTION] FINAL: {total_questions} questions, {total_nested_marks + standalone_total_marks} marks")
                
                # Store distribution
                self.target_question_count = total_questions
                self.target_nested_questions = num_nested_questions
                self.target_nested_marks = total_nested_marks
                self.target_distribution = standalone_counts  # Only standalone counts
                
                return  # Success!
            
            # Log progress every 20 attempts
            if attempt % 20 == 19:
                logger.debug(f"[DISTRIBUTION] Attempt {attempt + 1}: {total_questions} questions "
                           f"(nested: {num_nested_questions}, standalone: {total_standalone_questions})")
        
        # Fallback if no valid distribution found
        logger.warning(f"[DISTRIBUTION] No valid distribution after {max_attempts} attempts. Using fallback.")
        self._create_fallback_nested_distribution()
    
    def _distribute_standalone_marks(self, remaining_marks: int) -> dict:
        """
        Distribute remaining marks across standalone questions.
        
        Strategy:
        - Prefer 2-mark and 3-mark questions (most common)
        - Use 1-mark only if exactly 1 mark remaining
        - Use 4-mark only if needed for final completion
        - STANDALONE QUESTIONS ARE LIMITED TO 1-4 MARKS ONLY
        
        Args:
            remaining_marks: Marks to distribute (e.g., 15-30 marks)
        
        Returns:
            Dict {mark_value: count} or None if distribution impossible
        """
        if remaining_marks < 0 or remaining_marks > 30:
            return None
        
        # Try different combinations of 2-mark and 3-mark questions
        max_attempts = 50
        
        for _ in range(max_attempts):
            counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            marks_left = remaining_marks
            
            # Strategy 1: Mix of 2-mark and 3-mark questions
            while marks_left > 0:
                if marks_left == 1:
                    # Exactly 1 mark left - use 1-mark question
                    counts[1] += 1
                    marks_left -= 1
                elif marks_left == 4:
                    # Exactly 4 marks left - use 4-mark question
                    counts[4] += 1
                    marks_left -= 4
                elif marks_left >= 3 and random.random() < 0.5:
                    # 50% chance to use 3-mark
                    counts[3] += 1
                    marks_left -= 3
                elif marks_left >= 2:
                    # Use 2-mark
                    counts[2] += 1
                    marks_left -= 2
                else:
                    # Can't distribute - try again
                    break
            
            if marks_left == 0:
                # Success! Check if question count is reasonable (4-15 standalone)
                total_standalone = sum(counts.values())
                if 4 <= total_standalone <= 15:
                    return counts
        
        # Fallback: Simple distribution prioritizing 2 and 3-mark
        counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        marks_left = remaining_marks
        
        # Fill with 3-mark questions first
        while marks_left >= 3:
            if marks_left == 4:
                counts[4] += 1
                marks_left -= 4
            else:
                counts[3] += 1
                marks_left -= 3
        
        # Fill remaining with 2-mark or 1-mark
        if marks_left == 2:
            counts[2] += 1
        elif marks_left == 1:
            counts[1] += 1
        
        return counts
    
    def _create_fallback_nested_distribution(self):
        """
        Create a guaranteed valid nested distribution.
        
        Fallback: 
        - 14 nested questions = 56 marks
        - Standalone: 8×3-mark = 24 marks
        - Total: 22 questions, 80 marks
        """
        self.target_nested_questions = 14
        self.target_nested_marks = 56
        self.target_distribution = {1: 0, 2: 0, 3: 8, 4: 0, 5: 0, 6: 0}
        self.target_question_count = 22
        
        logger.info(f"[FALLBACK] Nested: 14 questions = 56 marks")
        logger.info(f"[FALLBACK] Standalone: 8×3-mark = 24 marks")
        logger.info(f"[FALLBACK] FINAL: 22 questions, 80 marks")
    
    def _create_fallback_distribution(self):
        """
        Create a guaranteed valid distribution that always works.
        
        Strategy: Work backwards from desired question count (26-27 questions)
        - Target: 27 questions, 80 marks
        - Average: 80÷27 ≈ 2.96 marks/question
        - Use a balanced mix that guarantees 80 marks
        
        Example distribution:
        - 1-mark: 8 questions = 8 marks (10%)
        - 2-mark: 12 questions = 24 marks (30%)
        - 3-mark: 6 questions = 18 marks (22.5%)
        - 4-mark: 1 question = 4 marks (5%)
        Total: 27 questions, 54 marks... need 26 more marks
        
        Better approach: Start with high-mark questions and fill down
        """
        total_marks_target = self.paper.total_marks  # 80
        target_questions = 27  # Middle of 24-29 range
        
        # Start with a proven distribution that works
        # This is based on: 25% 1-mark, 40% 2-mark, 30% 3-mark, 5% 4-mark OF MARKS
        marks_from_1mark = 20  # 25% of 80
        marks_from_2mark = 32  # 40% of 80
        marks_from_3mark = 24  # 30% of 80
        marks_from_4mark = 4   # 5% of 80
        
        # Convert to questions
        count_1mark = marks_from_1mark  # 20 questions
        count_2mark = marks_from_2mark // 2  # 16 questions
        count_3mark = marks_from_3mark // 3  # 8 questions
        count_4mark = marks_from_4mark // 4  # 1 question
        
        # Total: 20+16+8+1 = 45 questions (too many!)
        # We need 24-29, so reduce 1-mark questions
        
        # Recalculate with fewer 1-mark questions
        # Try: 10% 1-mark, 45% 2-mark, 40% 3-mark, 5% 4-mark
        marks_from_1mark = 8   # 10% of 80
        marks_from_2mark = 36  # 45% of 80
        marks_from_3mark = 32  # 40% of 80 (will be 30 after rounding)
        marks_from_4mark = 4   # 5% of 80
        
        # Adjust to exactly 80
        total = marks_from_1mark + marks_from_2mark + marks_from_3mark + marks_from_4mark
        if total != total_marks_target:
            diff = total_marks_target - total
            marks_from_2mark += diff
        
        # Convert to questions
        count_1mark = marks_from_1mark  # 8 questions
        count_2mark = marks_from_2mark // 2  # 18 questions
        count_3mark = marks_from_3mark // 3  # 10 questions (30÷3)
        count_4mark = marks_from_4mark // 4  # 1 question
        
        # Handle remainders
        remainder_2 = marks_from_2mark % 2
        remainder_3 = marks_from_3mark % 3
        
        # Calculate current marks
        current_marks = (count_1mark * 1) + (count_2mark * 2) + (count_3mark * 3) + (count_4mark * 4)
        remaining = total_marks_target - current_marks
        
        # Add questions for remaining marks
        if remaining >= 3 and remainder_3 > 0:
            count_3mark += 1
            remaining -= 3
        if remaining >= 2 and remainder_2 > 0:
            count_2mark += 1
            remaining -= 2
        while remaining > 0:
            if remaining >= 3:
                count_3mark += 1
                remaining -= 3
            elif remaining >= 2:
                count_2mark += 1
                remaining -= 2
            else:
                count_1mark += 1
        logger.info(f"[FALLBACK] Nested: 14 questions = 56 marks")
        logger.info(f"[FALLBACK] Standalone: 8×3-mark = 24 marks")
        logger.info(f"[FALLBACK] FINAL: 22 questions, 80 marks")
    
    def _adjust_distribution_for_exact_marks(self, marks_diff: int):
        """
        Fine-tune the target distribution to reach exactly 80 marks.
        
        Strategy:
        - If marks_diff > 0: Need MORE marks - replace lower-mark with higher-mark questions
        - If marks_diff < 0: Need FEWER marks - replace higher-mark with lower-mark questions
        
        Args:
            marks_diff: How many marks we need to add (positive) or remove (negative)
        """
        iterations = 0
        max_iterations = 100
        
        while marks_diff != 0 and iterations < max_iterations:
            iterations += 1
            
            if marks_diff > 0:
                # Need to add marks - replace lower with higher
                replaced = False
                
                # Try replacing 1-mark with higher marks (priority: 4, 3, 2)
                if marks_diff >= 3 and self.target_distribution[1] > 0:
                    self.target_distribution[1] -= 1
                    self.target_distribution[4] += 1
                    marks_diff -= 3
                    replaced = True
                elif marks_diff >= 2 and self.target_distribution[1] > 0:
                    self.target_distribution[1] -= 1
                    self.target_distribution[3] += 1
                    marks_diff -= 2
                    replaced = True
                elif marks_diff >= 1 and self.target_distribution[1] > 0:
                    self.target_distribution[1] -= 1
                    self.target_distribution[2] += 1
                    marks_diff -= 1
                    replaced = True
                # Try replacing 2-mark with higher marks
                elif marks_diff >= 2 and self.target_distribution[2] > 0:
                    self.target_distribution[2] -= 1
                    self.target_distribution[4] += 1
                    marks_diff -= 2
                    replaced = True
                elif marks_diff >= 1 and self.target_distribution[2] > 0:
                    self.target_distribution[2] -= 1
                    self.target_distribution[3] += 1
                    marks_diff -= 1
                    replaced = True
                # Try replacing 3-mark with 4-mark
                elif marks_diff >= 1 and self.target_distribution[3] > 0:
                    self.target_distribution[3] -= 1
                    self.target_distribution[4] += 1
                    marks_diff -= 1
                    replaced = True
                
                if not replaced:
                    logger.warning(f"[ADJUST] Cannot add {marks_diff} more marks")
                    break
            
            else:  # marks_diff < 0
                # Need to remove marks - replace higher with lower
                marks_to_remove = abs(marks_diff)
                replaced = False
                
                # Try replacing 4-mark with lower marks (priority: 1, 2, 3)
                if marks_to_remove >= 3 and self.target_distribution[4] > 0:
                    self.target_distribution[4] -= 1
                    self.target_distribution[1] += 1
                    marks_diff += 3
                    replaced = True
                elif marks_to_remove >= 2 and self.target_distribution[4] > 0:
                    self.target_distribution[4] -= 1
                    self.target_distribution[2] += 1
                    marks_diff += 2
                    replaced = True
                elif marks_to_remove >= 1 and self.target_distribution[4] > 0:
                    self.target_distribution[4] -= 1
                    self.target_distribution[3] += 1
                    marks_diff += 1
                    replaced = True
                # Try replacing 3-mark with lower marks
                elif marks_to_remove >= 2 and self.target_distribution[3] > 0:
                    self.target_distribution[3] -= 1
                    self.target_distribution[1] += 1
                    marks_diff += 2
                    replaced = True
                elif marks_to_remove >= 1 and self.target_distribution[3] > 0:
                    self.target_distribution[3] -= 1
                    self.target_distribution[2] += 1
                    marks_diff += 1
                    replaced = True
                # Try replacing 2-mark with 1-mark
                elif marks_to_remove >= 1 and self.target_distribution[2] > 0:
                    self.target_distribution[2] -= 1
                    self.target_distribution[1] += 1
                    marks_diff += 1
                    replaced = True
                
                if not replaced:
                    logger.warning(f"[ADJUST] Cannot remove {marks_to_remove} marks")
                    break
        
        # Final verification
        total_marks = sum(
            count * mark_value 
            for mark_value, count in self.target_distribution.items()
        )
        logger.info(f"[ADJUST] After {iterations} adjustments: {total_marks} marks (target: 80, remaining diff: {marks_diff})")
    
    def _apply_proportional_adjustment(self):
        """
        Step 2: Apply proportional adjustment if not all topics selected
        """
        all_topics = Topic.objects.filter(paper=self.paper, is_active=True)
        total_topics = all_topics.count()
        selected_count = len(self.selected_topics)
        
        if selected_count == total_topics:
            logger.info(f"[ADJUSTMENT] All topics selected, no adjustment needed")
            return
        
        # Calculate total maximum marks from selected topics
        total_max_marks = sum(topic.max_marks for topic in self.selected_topics)
        
        if total_max_marks == 0:
            raise PaperGenerationException("Total maximum marks for selected topics is zero")
        
        # Calculate scaling factor
        scaling_factor = self.paper.total_marks / total_max_marks
        
        logger.info(f"[ADJUSTMENT] Scaling factor: {scaling_factor:.2f} "
                   f"(target: {self.paper.total_marks}, available: {total_max_marks})")
        
        # Apply scaling to each topic
        for topic in self.selected_topics:
            topic_id = str(topic.id)
            original_min = topic.min_marks
            original_max = topic.max_marks
            
            # Apply scaling
            adjusted_min = original_min * scaling_factor
            adjusted_max = original_max * scaling_factor
            
            # Round intelligently
            adjusted_min = max(1, round(adjusted_min))
            adjusted_max = max(adjusted_min + 1, round(adjusted_max))
            
            self.topic_constraints[topic_id]['min_marks'] = adjusted_min
            self.topic_constraints[topic_id]['max_marks'] = adjusted_max
            
            logger.info(f"[ADJUSTMENT] {topic.name}: {original_min}-{original_max} -> "
                       f"{adjusted_min}-{adjusted_max} marks")
        
        # Verify that generation is possible
        total_min = sum(c['min_marks'] for c in self.topic_constraints.values())
        total_max = sum(c['max_marks'] for c in self.topic_constraints.values())
        
        if total_min > self.paper.total_marks:
            raise PaperGenerationException(
                f"Cannot generate paper: minimum marks ({total_min}) exceeds target ({self.paper.total_marks})"
            )
        
        if total_max < self.paper.total_marks:
            raise PaperGenerationException(
                f"Cannot generate paper: maximum marks ({total_max}) below target ({self.paper.total_marks})"
            )
        
        logger.info(f"[ADJUSTMENT] Adjusted ranges allow {total_min}-{total_max} marks (target: {self.paper.total_marks})")
    
    def _reset_tracking_variables(self):
        """Reset all tracking variables for a fresh generation attempt"""
        self.total_marks = 0
        self.selected_questions = []
        self.selected_question_ids = set()
        self.selected_nested_questions = []  # Clear nested tracking
        self.selected_standalone_questions = []  # Clear standalone tracking
        self.actual_nested_marks = 0  # Reset actual nested marks achieved
        self.mark_value_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
        self.question_type_counts = {
            'name_identify': 0,
            'state_give_reasons': 0,
            'distinguish': 0,
            'explain_account': 0,
            'describe': 0,
            'calculate': 0,
        }
        
        for topic_id in self.topic_mark_counts:
            self.topic_mark_counts[topic_id] = 0
        
        self.backtracking_count = 0
    
    def _select_questions(self):
        """
        Step 3: Select questions - NESTED first, then STANDALONE
        
        Process:
        1. Select nested questions (target 50-65 marks, flexible question count)
        2. Recalculate standalone distribution based on actual nested marks achieved
        3. Select standalone questions to complete exactly 80 marks
        """
        max_iterations = 2000
        
        # Step 1: Select nested questions
        logger.info(f"[SELECTION] Phase 1: Selecting nested questions (target {self.target_nested_marks} marks)")
        self._select_nested_questions()
        
        logger.info(f"[SELECTION] Phase 1 complete: {len(self.selected_nested_questions)} nested questions, "
                   f"{self.actual_nested_marks} marks")
        
        # Step 2: Recalculate standalone distribution based on ACTUAL nested marks
        remaining_marks = self.paper.total_marks - self.actual_nested_marks
        logger.info(f"[SELECTION] Phase 2: Need {remaining_marks} marks from standalone questions")
        
        # Recalculate standalone distribution for exact remaining marks
        standalone_distribution = self._distribute_standalone_marks(remaining_marks)
        if standalone_distribution:
            self.target_distribution = standalone_distribution
            logger.info(f"[SELECTION] Standalone distribution: {standalone_distribution}")
        else:
            logger.warning(f"[SELECTION] Could not calculate distribution for {remaining_marks} marks")
        
        # Step 3: Select standalone questions
        self._select_standalone_questions()
        
        logger.info(f"[SELECTION] Complete: {len(self.selected_questions)} questions "
                   f"({len(self.selected_nested_questions)} nested + {len(self.selected_standalone_questions)} standalone), "
                   f"{self.total_marks} marks")
        
        # Verify totals
        if self.total_marks != self.paper.total_marks:
            logger.warning(f"[SELECTION] Total marks {self.total_marks} != target {self.paper.total_marks}")
            # Try fine-tuning
            self._fine_tune_to_exact_marks()
    
    def _select_nested_questions(self):
        """
        Select nested questions with flexible completion strategy.
        
        Strategy:
        - Try to reach target nested marks using nested questions
        - If only 1-2 marks remain to reach target, use standalone to complete
        - Early success is fine - if we hit target marks early, stop
        
        Target: self.target_nested_marks marks (question count is flexible)
        """
        iteration = 0
        max_iterations = 500
        consecutive_failures = 0
        max_consecutive_failures = 50
        
        # Calculate average marks per nested question
        if self.target_nested_questions > 0:
            avg_marks_per_nested = self.target_nested_marks / self.target_nested_questions
        else:
            avg_marks_per_nested = 5
        
        logger.info(f"[NESTED] Target: {self.target_nested_marks} marks "
                   f"(estimated {self.target_nested_questions} questions)")
        
        nested_marks_so_far = 0
        
        while nested_marks_so_far < self.target_nested_marks and iteration < max_iterations:
            iteration += 1
            
            # Calculate how many marks we still need
            marks_remaining = self.target_nested_marks - nested_marks_so_far
            
            # If only 1 or 2 marks remaining, complete with standalone question
            if marks_remaining <= 2:
                logger.info(f"[NESTED] Only {marks_remaining} mark(s) remaining - completing with standalone")
                standalone_q = self._query_standalone_questions_by_marks(marks_remaining)
                
                if standalone_q:
                    selected = random.choice(standalone_q)
                    if self._can_add_question(selected):
                        self._add_question(selected)
                        nested_marks_so_far += selected.marks
                        logger.info(f"[NESTED] Added {marks_remaining}-mark standalone to complete nested phase")
                        break
                else:
                    logger.warning(f"[NESTED] No {marks_remaining}-mark standalone found, trying nested")
            
            # STRATEGIC SELECTION: If we're close to target (3-7 marks remaining),
            # try to find a nested question with EXACT marks needed
            eligible_questions = []
            
            if 3 <= marks_remaining <= 7:
                # Try to find exact match
                logger.debug(f"[NESTED] Strategic: Looking for exact {marks_remaining}-mark nested question")
                exact_match_questions = self._query_nested_questions_by_marks(marks_remaining)
                
                if exact_match_questions:
                    eligible_questions = exact_match_questions
                    logger.info(f"[NESTED] Strategic: Found {len(exact_match_questions)} nested questions "
                              f"with exactly {marks_remaining} marks!")
            
            # If no exact match or not in strategic range, use normal range query
            if not eligible_questions:
                # Query for nested questions close to remaining marks
                # Prefer questions with 4-6 marks
                min_marks = max(3, marks_remaining - 3)
                max_marks = min(7, marks_remaining + 1)
                
                eligible_questions = self._query_nested_questions(min_marks, max_marks)
                
                if not eligible_questions:
                    # Expand range to any nested (3-8 marks)
                    eligible_questions = self._query_nested_questions(3, 8)
            
            if not eligible_questions:
                logger.warning(f"[NESTED] No nested questions available!")
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    logger.error(f"[NESTED] Cannot find nested questions!")
                    break
                continue
            
            # Select random nested question
            selected_question = random.choice(eligible_questions)
            
            # Check if adding it would exceed target by too much (more than 3 marks)
            if nested_marks_so_far + selected_question.marks > self.target_nested_marks + 3:
                # This would overshoot too much, try to find smaller one
                logger.debug(f"[NESTED] {selected_question.marks}-mark would overshoot, looking for smaller")
                consecutive_failures += 1
                continue
            
            # Check if we can add it
            if self._can_add_question(selected_question):
                self._add_question(selected_question)
                self.selected_nested_questions.append(selected_question)
                nested_marks_so_far += selected_question.marks
                consecutive_failures = 0
                
                logger.debug(f"[NESTED] Added nested question: {selected_question.marks} marks "
                           f"({nested_marks_so_far}/{self.target_nested_marks} marks)")
            else:
                consecutive_failures += 1
        
        # Mark nested phase as success if we're within acceptable range (50-65 marks)
        if 50 <= nested_marks_so_far <= 65:
            logger.info(f"[NESTED] ✅ Success! Selected {len(self.selected_nested_questions)} nested questions, "
                       f"{nested_marks_so_far} marks (target: {self.target_nested_marks})")
        else:
            logger.warning(f"[NESTED] ⚠️ Nested marks {nested_marks_so_far} outside ideal range (50-65)")
        
        # Update target nested marks to actual achieved (for standalone calculation)
        self.actual_nested_marks = nested_marks_so_far
    
    def _select_standalone_questions(self):
        """
        Select standalone questions based on target_distribution.
        
        Prefer 2-mark and 3-mark questions.
        """
        iteration = 0
        max_iterations = 1000
        consecutive_failures = 0
        max_consecutive_failures = 50
        
        # Create remaining distribution tracker
        remaining_distribution = dict(self.target_distribution)
        
        logger.info(f"[STANDALONE] Target distribution: {remaining_distribution}")
        
        while sum(remaining_distribution.values()) > 0 and iteration < max_iterations:
            iteration += 1
            
            # Progress logging
            if iteration % 100 == 0:
                logger.info(f"[STANDALONE] Iteration {iteration}: Remaining {remaining_distribution}")
            
            # Determine which mark value to select next
            target_mark_value = self._determine_next_mark_value_from_distribution(remaining_distribution)
            
            if target_mark_value is None:
                break
            
            # Query for standalone questions (is_nested=False)
            eligible_questions = self._query_standalone_questions(mark_value=target_mark_value)
            
            if not eligible_questions:
                logger.warning(f"[STANDALONE] No {target_mark_value}-mark standalone questions available!")
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    logger.error(f"[STANDALONE] Cannot find standalone questions!")
                    break
                continue
            
            # Select random question
            selected_question = random.choice(eligible_questions)
            
            # Validate before adding
            if self._can_add_question(selected_question):
                self._add_question(selected_question)
                self.selected_standalone_questions.append(selected_question)
                remaining_distribution[target_mark_value] -= 1
                consecutive_failures = 0
                
                logger.debug(f"[STANDALONE] Added {target_mark_value}-mark question. Remaining: {remaining_distribution}")
            else:
                consecutive_failures += 1
        
        logger.info(f"[STANDALONE] Selected {len(self.selected_standalone_questions)} standalone questions")
    
    def _determine_next_mark_value_from_distribution(self, remaining_distribution: Dict[int, int]) -> Optional[int]:
        """
        Determine which mark value to select next based on remaining distribution targets.
        
        Prioritizes mark values that still need to be selected according to the plan.
        
        Args:
            remaining_distribution: Dict mapping mark_value -> count still needed
            
        Returns:
            Mark value (1, 2, 3, or 4) to select next, or None if all targets met
        """
        # Filter out mark values we've already satisfied
        available_mark_values = [
            mark_value for mark_value, count in remaining_distribution.items() 
            if count > 0
        ]
        
        if not available_mark_values:
            return None
        
        # Prioritize based on strategy:
        # 1. If we need higher-mark questions, prioritize them (helps reach 80 marks)
        # 2. Mix in lower-mark questions to maintain distribution
        
        # Calculate weights - prefer higher marks slightly to ensure we reach 80
        weights = []
        for mark_value in available_mark_values:
            # Base weight is the count remaining (need more = higher weight)
            weight = remaining_distribution[mark_value]
            # Bonus for higher mark values (helps reach target marks)
            weight *= (mark_value / 2.5)  # 4-mark gets 1.6x, 3-mark gets 1.2x, etc.
            weights.append(weight)
        
        # Weighted random selection
        selected = random.choices(available_mark_values, weights=weights, k=1)[0]
        return selected
    
    def _query_nested_questions_by_marks(self, exact_marks: int) -> List[Question]:
        """
        Query for nested questions with a specific mark value.
        
        Used for strategic selection when approaching nested mark target.
        
        Args:
            exact_marks: The exact mark value needed (e.g., 3, 4, 5)
            
        Returns:
            List of available nested questions with that exact mark value
        """
        # Get already selected question IDs to exclude
        selected_ids = [q.id for q in self.selected_nested_questions + self.selected_standalone_questions]
        
        # Query nested questions with exact marks that haven't been selected
        queryset = Question.objects.filter(
            topic_id__in=self.selected_topic_ids,
            is_nested=True,
            marks=exact_marks
        ).exclude(
            id__in=selected_ids
        )
        
        available_questions = list(queryset)
        logger.debug(f"[QUERY] Found {len(available_questions)} nested questions with exactly {exact_marks} marks")
        
        return available_questions
    
    def _query_standalone_questions_by_marks(self, mark_value: int, limit: int = 50) -> List[Question]:
        """
        Query for standalone questions with a specific mark value.
        
        Args:
            mark_value: The mark value (1, 2, 3, or 4)
            limit: Maximum number of questions to retrieve
            
        Returns:
            List of available standalone questions with that mark value
        """
        # Get already selected question IDs to exclude
        selected_ids = [q.id for q in self.selected_nested_questions + self.selected_standalone_questions]
        
        # Query standalone questions with specific marks that haven't been selected
        queryset = Question.objects.filter(
            topic_id__in=self.selected_topic_ids,
            is_nested=False,
            marks=mark_value
        ).exclude(
            id__in=selected_ids
        )[:limit]
        
        available_questions = list(queryset)
        logger.debug(f"[QUERY] Found {len(available_questions)} standalone questions with {mark_value} marks")
        
        return available_questions
    
    def _fine_tune_to_exact_marks(self):
        """
        Fine-tune the selected questions to reach exactly 80 marks.
        
        Uses backtracking and replacement to adjust the final mark count.
        """
        max_adjustments = 50
        adjustments = 0
        
        while self.total_marks != self.paper.total_marks and adjustments < max_adjustments:
            adjustments += 1
            marks_diff = self.paper.total_marks - self.total_marks
            
            if marks_diff > 0:
                # Need to add marks - try replacing a lower-mark question with higher-mark
                logger.info(f"[FINE-TUNE] Need {marks_diff} more marks")
                
                # Try to replace 1-mark with 2, 3, or 4-mark
                for i, q in enumerate(self.selected_questions):
                    if q.marks == 1 and marks_diff >= 1:
                        # Try to find a replacement with more marks
                        target_marks = min(4, q.marks + marks_diff)
                        replacement = self._find_replacement_question(q, target_marks)
                        if replacement:
                            self._replace_question(i, replacement)
                            logger.info(f"[FINE-TUNE] Replaced {q.marks}-mark with {replacement.marks}-mark")
                            break
                else:
                    # Try replacing 2-mark with 3 or 4-mark
                    for i, q in enumerate(self.selected_questions):
                        if q.marks == 2 and marks_diff >= 1:
                            target_marks = min(4, q.marks + marks_diff)
                            replacement = self._find_replacement_question(q, target_marks)
                            if replacement:
                                self._replace_question(i, replacement)
                                logger.info(f"[FINE-TUNE] Replaced {q.marks}-mark with {replacement.marks}-mark")
                                break
                    else:
                        break  # Can't fine-tune further
            
            else:  # marks_diff < 0
                # Need to remove marks - try replacing a higher-mark question with lower-mark
                marks_to_remove = abs(marks_diff)
                logger.info(f"[FINE-TUNE] Need to remove {marks_to_remove} marks")
                
                # Try to replace 4-mark with 3, 2, or 1-mark
                for i, q in enumerate(self.selected_questions):
                    if q.marks == 4 and marks_to_remove >= 1:
                        target_marks = max(1, q.marks - marks_to_remove)
                        replacement = self._find_replacement_question(q, target_marks)
                        if replacement:
                            self._replace_question(i, replacement)
                            logger.info(f"[FINE-TUNE] Replaced {q.marks}-mark with {replacement.marks}-mark")
                            break
                else:
                    # Try replacing 3-mark with 2 or 1-mark
                    for i, q in enumerate(self.selected_questions):
                        if q.marks == 3 and marks_to_remove >= 1:
                            target_marks = max(1, q.marks - marks_to_remove)
                            replacement = self._find_replacement_question(q, target_marks)
                            if replacement:
                                self._replace_question(i, replacement)
                                logger.info(f"[FINE-TUNE] Replaced {q.marks}-mark with {replacement.marks}-mark")
                                break
                    else:
                        break  # Can't fine-tune further
        
        logger.info(f"[FINE-TUNE] Complete after {adjustments} adjustments: {self.total_marks} marks")
    
    def _find_replacement_question(self, current_question, target_marks: int):
        """Find a replacement question with target marks from the same topic."""
        eligible = self._query_eligible_questions(
            topic_id=str(current_question.topic_id),
            mark_value=target_marks
        )
        return random.choice(eligible) if eligible else None
    
    def _replace_question(self, index: int, new_question):
        """Replace a question at the given index with a new question."""
        old_question = self.selected_questions[index]
        
        # Remove old question's contribution
        self.selected_question_ids.remove(str(old_question.id))
        self.total_marks -= old_question.marks
        self.mark_value_counts[old_question.marks] -= 1
        
        # Use .get() with default 0 to handle missing topic_ids gracefully
        old_topic_id = str(old_question.topic_id)
        if old_topic_id in self.topic_mark_counts:
            self.topic_mark_counts[old_topic_id] -= old_question.marks
        
        # Handle question_type safely
        if old_question.question_type and old_question.question_type in self.question_type_counts:
            self.question_type_counts[old_question.question_type] -= 1
        
        # Add new question
        self.selected_questions[index] = new_question
        self.selected_question_ids.add(str(new_question.id))
        self.total_marks += new_question.marks
        self.mark_value_counts[new_question.marks] += 1
        
        # Use .get() with default for new question too
        new_topic_id = str(new_question.topic_id)
        if new_topic_id in self.topic_mark_counts:
            self.topic_mark_counts[new_topic_id] += new_question.marks
        else:
            self.topic_mark_counts[new_topic_id] = new_question.marks
        
        # Handle question_type safely for new question too
        if new_question.question_type:
            if new_question.question_type in self.question_type_counts:
                self.question_type_counts[new_question.question_type] += 1
            else:
                self.question_type_counts[new_question.question_type] = 1
    
    def _try_exact_completion(self, remaining_marks: int) -> bool:
        """
        Try to complete the paper exactly when close to target marks
        
        Smart combinations (include 4-mark questions with lower priority):
        - 1 mark: add one 1-mark question
        - 2 marks: add one 2-mark OR two 1-mark
        - 3 marks: add one 3-mark OR one 2-mark + one 1-mark OR three 1-mark
        - 4 marks: prefer non-4-mark combinations, but allow 4-mark as valid option
        
        Args:
            remaining_marks: Marks needed to reach 80
            
        Returns:
            True if exact completion successful, False otherwise
        """
        # Define all possible combinations to reach target
        # For 4 marks: try other combinations first, but include [4] as valid option
        combinations = []
        
        if remaining_marks == 1:
            combinations = [[1]]
        elif remaining_marks == 2:
            combinations = [[2], [1, 1]]
        elif remaining_marks == 3:
            combinations = [[3], [2, 1], [1, 1, 1]]
        elif remaining_marks == 4:
            # Try multiple combinations including a single 4-mark question
            # Order: prefer combinations without 4-mark, but include it
            combinations = [[2, 2], [3, 1], [4], [2, 1, 1], [1, 1, 1, 1]]
        
        # Try each combination
        for combo in combinations:
            if self._try_add_combination(combo):
                return True
        
        return False
    
    def _try_add_combination(self, mark_values: list) -> bool:
        """
        Try to add a specific combination of mark values
        
        Args:
            mark_values: List of mark values to add (e.g., [3, 1] for 3-mark + 1-mark)
            
        Returns:
            True if combination successfully added, False otherwise
        """
        questions_to_add = []
        
        logger.info(f"[SMART COMPLETION] Trying combination: {mark_values}")
        
        # Try to find questions for each mark value in the combination
        for mark_value in mark_values:
            # Find a topic that can accept this question
            suitable_topic = None
            
            for topic_id, constraints in self.topic_constraints.items():
                current_marks = self.topic_mark_counts[topic_id]
                max_marks = constraints['max_marks']
                
                # Allow some tolerance (±2 marks)
                if current_marks < (max_marks + 2):
                    suitable_topic = topic_id
                    break
            
            if suitable_topic is None:
                logger.info(f"[SMART COMPLETION] No suitable topic for {mark_value}-mark question")
                return False
            
            # Query for question
            eligible_questions = self._query_eligible_questions(
                topic_id=suitable_topic,
                mark_value=mark_value
            )
            
            if not eligible_questions:
                logger.info(f"[SMART COMPLETION] No eligible {mark_value}-mark questions found")
                return False
            
            # Select random question from eligible
            question = random.choice(eligible_questions)
            questions_to_add.append(question)
        
        # Check if adding all questions would violate constraints
        # For exact completion, we're more lenient
        test_total = self.total_marks + sum(q.marks for q in questions_to_add)
        if test_total != self.paper.total_marks:
            logger.info(f"[SMART COMPLETION] Total would be {test_total}, need {self.paper.total_marks}")
            return False
        
        # Add all questions
        for question in questions_to_add:
            self._add_question(question)
        
        logger.info(f"[SMART COMPLETION] Successfully added combination: {mark_values} marks")
        return True
    
    def _determine_next_mark_value(self) -> Optional[int]:
        """
        Determine which mark value should be selected next based on current distribution
        
        Returns:
            Mark value (1, 2, 3, or 4) or None if backtracking needed
        """
        if not self.selected_questions:
            # First question - start with 2 or 3 marks to avoid hitting question limit
            return random.choice([2, 3])
        
        total_questions = len(self.selected_questions)
        remaining_marks = self.paper.total_marks - self.total_marks
        
        if remaining_marks <= 0:
            return None
        
        # CRITICAL: Check if we're approaching question limit
        # If we have many questions but low marks, prioritize higher-mark questions
        marks_per_question_needed = remaining_marks / max(1, self.config.max_questions - total_questions)
        
        # Calculate current percentages
        priorities = {}
        
        for mark_value in [1, 2, 3, 4]:
            count = self.mark_value_counts[mark_value]
            current_percent = (count / total_questions * 100) if total_questions > 0 else 0
            
            # Get target range from config
            if mark_value == 1:
                min_p, max_p = self.config.one_mark_min_percent, self.config.one_mark_max_percent
            elif mark_value == 2:
                min_p, max_p = self.config.two_mark_min_percent, self.config.two_mark_max_percent
            elif mark_value == 3:
                min_p, max_p = self.config.three_mark_min_percent, self.config.three_mark_max_percent
            else:  # 4
                min_p, max_p = self.config.four_mark_min_percent, self.config.four_mark_max_percent
            
            # Check if this mark value can fit in remaining marks
            if mark_value > remaining_marks:
                priorities[mark_value] = 0
                continue
            
            # Use relaxed tolerance during selection (±5%)
            selection_tolerance = 5.0
            
            # CRITICAL: If approaching question limit, strongly prioritize higher marks
            if total_questions >= self.config.max_questions - 5:
                # Less than 5 questions left - strongly prefer higher marks
                if mark_value >= marks_per_question_needed:
                    priorities[mark_value] = 5  # Very high priority
                else:
                    priorities[mark_value] = 0  # Don't select low marks
                continue
            elif total_questions >= self.config.max_questions - 10:
                # Less than 10 questions left - prefer higher marks
                if mark_value >= 2:
                    priorities[mark_value] = 3
                else:
                    priorities[mark_value] = 1
                continue
            
            # Special handling for 4-mark questions (0-5% range)
            if mark_value == 4:
                # Give 4-mark questions a chance even at 0%
                # If we're at 0%, still give it low-medium priority
                if current_percent == 0:
                    # Small chance to include 4-mark questions (10% probability)
                    priorities[mark_value] = 1 if random.random() < 0.10 else 0
                elif current_percent < (max_p + selection_tolerance):
                    # Within acceptable range - low priority
                    priorities[mark_value] = 1
                else:
                    # Exceeded limit
                    priorities[mark_value] = 0
            else:
                # Normal priority logic for 1, 2, 3 mark questions
                if current_percent < min_p:
                    # Below minimum - high priority
                    priorities[mark_value] = 3
                elif current_percent < (max_p + selection_tolerance):
                    # Within range or slightly above - medium priority
                    priorities[mark_value] = 2
                else:
                    # Well above maximum - low priority (but not zero)
                    priorities[mark_value] = 1
        
        # Weighted random selection
        if sum(priorities.values()) == 0:
            return None
        
        # Create weighted list
        weighted_options = []
        for mark_value, priority in priorities.items():
            weighted_options.extend([mark_value] * priority)
        
        return random.choice(weighted_options) if weighted_options else None
    
    def _determine_next_topic(self) -> Optional[str]:
        """
        Determine which topic should be selected from next
        
        Returns:
            Topic ID or None if no suitable topic
        """
        priorities = {}
        
        # Use relaxed tolerance for topic selection (±2 marks)
        topic_tolerance = 2
        
        for topic_id, constraints in self.topic_constraints.items():
            current_marks = self.topic_mark_counts[topic_id]
            min_marks = constraints['min_marks']
            max_marks = constraints['max_marks']
            
            # Check if topic can receive more marks (with tolerance)
            if current_marks >= (max_marks + topic_tolerance):
                priorities[topic_id] = 0
                continue
            
            # Assign priority
            if current_marks < min_marks:
                # Below minimum - high priority
                priorities[topic_id] = 3
            elif current_marks < max_marks:
                # Above minimum but below maximum - medium priority
                priorities[topic_id] = 2
            else:
                # At or slightly above maximum - low priority (but allow)
                priorities[topic_id] = 1
        
        # Weighted random selection
        if sum(priorities.values()) == 0:
            return None
        
        weighted_options = []
        for topic_id, priority in priorities.items():
            weighted_options.extend([topic_id] * priority)
        
        return random.choice(weighted_options) if weighted_options else None
    
    def _query_eligible_questions(self, topic_id: str, mark_value: int) -> List[Question]:
        """
        Query database for eligible questions
        
        Args:
            topic_id: UUID of topic
            mark_value: Mark value (1, 2, 3, or 4)
        
        Returns:
            List of eligible Question objects
        """
        questions = Question.objects.filter(
            paper=self.paper,
            topic_id=topic_id,
            marks=mark_value,
            is_active=True
        ).exclude(
            id__in=self.selected_question_ids
        ).order_by('?')[:50]  # Random sample of up to 50
        
        return list(questions)
    
    def _query_nested_questions(self, min_marks: int, max_marks: int) -> List[Question]:
        """
        Query database for nested questions (is_nested=True) within mark range.
        
        Args:
            min_marks: Minimum marks
            max_marks: Maximum marks
        
        Returns:
            List of eligible nested Question objects
        """
        topic_ids = [str(topic.id) for topic in self.selected_topics]
        
        questions = Question.objects.filter(
            paper=self.paper,
            topic_id__in=topic_ids,
            is_nested=True,
            marks__gte=min_marks,
            marks__lte=max_marks,
            is_active=True
        ).exclude(
            id__in=self.selected_question_ids
        ).order_by('?')[:50]
        
        return list(questions)
    
    def _query_standalone_questions(self, mark_value: int) -> List[Question]:
        """
        Query database for standalone questions (is_nested=False) of specific mark value.
        
        Args:
            mark_value: Mark value (1, 2, 3, 4, 5, or 6)
        
        Returns:
            List of eligible standalone Question objects
        """
        topic_ids = [str(topic.id) for topic in self.selected_topics]
        
        questions = Question.objects.filter(
            paper=self.paper,
            topic_id__in=topic_ids,
            is_nested=False,
            marks=mark_value,
            is_active=True
        ).exclude(
            id__in=self.selected_question_ids
        ).order_by('?')[:100]
        
        return list(questions)
    
    def _query_all_eligible_questions(self, mark_value: int) -> List[Question]:
        """
        Query database for ALL eligible questions of a given mark value,
        regardless of topic. Used for flexible selection.
        
        Args:
            mark_value: Mark value (1, 2, 3, or 4)
        
        Returns:
            List of eligible Question objects from all selected topics
        """
        # Get topic IDs from selected topics
        topic_ids = [str(topic.id) for topic in self.selected_topics]
        
        questions = Question.objects.filter(
            paper=self.paper,
            topic_id__in=topic_ids,
            marks=mark_value,
            is_active=True
        ).exclude(
            id__in=self.selected_question_ids
        ).order_by('?')[:100]  # Random sample of up to 100
        
        return list(questions)
    
    def _can_add_question(self, question: Question) -> bool:
        """
        Check if a question can be added without violating hard constraints.
        More lenient than _validate_question_addition - focuses on critical constraints only.
        
        Args:
            question: Question to check
        
        Returns:
            True if question can be added, False otherwise
        """
        # Already selected?
        if str(question.id) in self.selected_question_ids:
            return False
        
        # Would exceed total marks?
        if self.total_marks + question.marks > self.paper.total_marks:
            return False
        
        # Check topic marks with tolerance (+3 marks tolerance)
        topic_id = str(question.topic_id)
        if topic_id in self.topic_constraints:
            current = self.topic_mark_counts[topic_id]
            max_marks = self.topic_constraints[topic_id]['max_marks']
            # Allow up to 3 marks over the max (will be balanced by other topics)
            if current + question.marks > (max_marks + 3):
                return False
        
        return True
    
    def _validate_question_addition(self, question: Question) -> bool:
        """
        Validate if adding this question would violate any constraints
        
        Args:
            question: Question to validate
        
        Returns:
            True if question can be added, False otherwise
        """
        # Check total marks
        if self.total_marks + question.marks > self.paper.total_marks:
            return False
        
        # Check topic marks
        topic_id = str(question.topic_id)
        if topic_id in self.topic_constraints:
            current = self.topic_mark_counts[topic_id]
            max_marks = self.topic_constraints[topic_id]['max_marks']
            if current + question.marks > max_marks:
                return False
        
        # Check question type distribution (soft check)
        if question.kcse_question_type:
            # This is a soft check - we allow some flexibility
            pass
        
        return True
    
    def _add_question(self, question: Question):
        """Add question to selected list and update all tracking variables"""
        self.selected_questions.append(question)
        self.selected_question_ids.add(str(question.id))  # Store as string for consistency
        self.total_marks += question.marks
        self.mark_value_counts[question.marks] += 1
        
        topic_id = str(question.topic_id)
        if topic_id in self.topic_mark_counts:
            self.topic_mark_counts[topic_id] += question.marks
        
        if question.kcse_question_type:
            if question.kcse_question_type in self.question_type_counts:
                self.question_type_counts[question.kcse_question_type] += 1
    
    def _attempt_backtracking(self) -> bool:
        """
        Step 4: Attempt backtracking by replacing questions
        
        Returns:
            True if backtracking successful, False otherwise
        """
        if self.backtracking_count >= self.config.max_backtracking_attempts:
            logger.warning(f"[BACKTRACK] Maximum backtracking attempts ({self.config.max_backtracking_attempts}) reached")
            return False
        
        self.backtracking_count += 1
        
        # Strategy: Try to replace a lower-mark question with a higher-mark one
        remaining_marks = self.paper.total_marks - self.total_marks
        
        if remaining_marks > 0:
            # Need more marks - try to upgrade questions
            for i, question in enumerate(self.selected_questions):
                if question.marks < 4:  # Can upgrade
                    # Try to find higher-mark replacement from same topic
                    higher_mark = question.marks + 1
                    
                    replacements = Question.objects.filter(
                        paper=self.paper,
                        topic=question.topic,
                        marks=higher_mark,
                        is_active=True
                    ).exclude(
                        id__in=self.selected_question_ids
                    )[:10]
                    
                    for replacement in replacements:
                        # Check if replacement would be valid
                        test_total = self.total_marks - question.marks + replacement.marks
                        if test_total <= self.paper.total_marks:
                            # Check if this would violate percentage constraints
                            total_questions = len(self.selected_questions)
                            test_count = self.mark_value_counts[higher_mark] + 1
                            test_percent = (test_count / total_questions * 100) if total_questions > 0 else 0
                            
                            # Get max percentage for this mark value
                            if higher_mark == 1:
                                max_p = self.config.one_mark_max_percent
                            elif higher_mark == 2:
                                max_p = self.config.two_mark_max_percent
                            elif higher_mark == 3:
                                max_p = self.config.three_mark_max_percent
                            else:  # 4
                                max_p = self.config.four_mark_max_percent
                            
                            # Only proceed if we won't exceed max percentage
                            if test_percent <= max_p + 5:  # Allow 5% tolerance during backtracking
                                # Check topic constraints
                                topic_id = str(question.topic_id)
                                test_topic_marks = self.topic_mark_counts.get(topic_id, 0) + (replacement.marks - question.marks)
                                max_topic_marks = self.topic_constraints.get(topic_id, {}).get('max_marks', 999)
                                
                                if test_topic_marks <= max_topic_marks + 2:  # Allow 2 marks tolerance
                                    # Perform replacement
                                    self.selected_questions[i] = replacement
                                    self.selected_question_ids.remove(question.id)
                                    self.selected_question_ids.add(replacement.id)
                                    self.total_marks = test_total
                                    self.mark_value_counts[question.marks] -= 1
                                    self.mark_value_counts[replacement.marks] += 1
                                    
                                    if topic_id in self.topic_mark_counts:
                                        self.topic_mark_counts[topic_id] += (replacement.marks - question.marks)
                                    
                                    logger.info(f"[BACKTRACK] Replaced {question.marks}-mark with {replacement.marks}-mark question")
                                    return True
        
        return False
    
    def _final_adjustment(self) -> bool:
        """
        Final adjustment to reach exact target marks
        
        Returns:
            True if adjustment successful, False otherwise
        """
        attempts = 0
        max_attempts = 20
        
        while self.total_marks != self.paper.total_marks and attempts < max_attempts:
            attempts += 1
            difference = self.paper.total_marks - self.total_marks
            
            if difference > 0:
                # Need more marks
                if not self._attempt_backtracking():
                    break
            else:
                # Have too many marks (shouldn't happen, but handle it)
                if not self._reduce_marks():
                    break
        
        return self.total_marks == self.paper.total_marks
    
    def _reduce_marks(self) -> bool:
        """
        Reduce total marks by replacing higher-mark questions with lower-mark ones
        
        Returns:
            True if reduction successful, False otherwise
        """
        for i, question in enumerate(self.selected_questions):
            if question.marks > 1:
                lower_mark = question.marks - 1
                
                replacements = Question.objects.filter(
                    paper=self.paper,
                    topic=question.topic,
                    marks=lower_mark,
                    is_active=True
                ).exclude(
                    id__in=self.selected_question_ids
                )[:10]
                
                for replacement in replacements:
                    # Perform replacement
                    self.selected_questions[i] = replacement
                    self.selected_question_ids.remove(question.id)
                    self.selected_question_ids.add(replacement.id)
                    self.total_marks += (replacement.marks - question.marks)
                    self.mark_value_counts[question.marks] -= 1
                    self.mark_value_counts[replacement.marks] += 1
                    
                    topic_id = str(question.topic_id)
                    if topic_id in self.topic_mark_counts:
                        self.topic_mark_counts[topic_id] += (replacement.marks - question.marks)
                    
                    return True
        
        return False
    
    def _arrange_questions(self):
        """
        Step 5: Arrange questions in pedagogical order
        
        Questions are arranged in three sections:
        - Early section (40%): Mostly 1-mark questions
        - Middle section (40%): Mix of 1, 2, and 3-mark questions
        - Final section (20%): Complex questions (3, 4, 5, 6, 7, 8-mark including nested)
        """
        # Separate questions by mark value - Extended to support nested questions up to 8 marks
        questions_by_mark = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
        
        for question in self.selected_questions:
            questions_by_mark[question.marks].append(question)
        
        # Shuffle each group for topic distribution
        for mark_value in questions_by_mark:
            random.shuffle(questions_by_mark[mark_value])
        
        total_questions = len(self.selected_questions)
        early_count = int(total_questions * 0.4)
        middle_count = int(total_questions * 0.4)
        
        arranged_questions = []
        
        # Early section - mostly 1-mark, some 2-mark
        early_questions = questions_by_mark[1][:early_count]
        remaining_early = early_count - len(early_questions)
        if remaining_early > 0:
            early_questions.extend(questions_by_mark[2][:remaining_early])
            questions_by_mark[2] = questions_by_mark[2][remaining_early:]
        questions_by_mark[1] = questions_by_mark[1][early_count:]
        
        random.shuffle(early_questions)
        arranged_questions.extend(early_questions)
        
        # Middle section - mix of remaining 1, 2, and some 3-mark
        middle_questions = []
        middle_questions.extend(questions_by_mark[1])
        middle_target = middle_count - len(middle_questions)
        
        if middle_target > 0:
            two_mark_for_middle = min(len(questions_by_mark[2]), middle_target)
            middle_questions.extend(questions_by_mark[2][:two_mark_for_middle])
            questions_by_mark[2] = questions_by_mark[2][two_mark_for_middle:]
            middle_target -= two_mark_for_middle
        
        if middle_target > 0:
            three_mark_for_middle = min(len(questions_by_mark[3]), middle_target)
            middle_questions.extend(questions_by_mark[3][:three_mark_for_middle])
            questions_by_mark[3] = questions_by_mark[3][three_mark_for_middle:]
        
        random.shuffle(middle_questions)
        arranged_questions.extend(middle_questions)
        
        # Final section - remaining 2, 3, 4, 5, 6, 7, 8-mark questions (including nested)
        final_questions = []
        final_questions.extend(questions_by_mark[2])
        final_questions.extend(questions_by_mark[3])
        final_questions.extend(questions_by_mark[4])
        final_questions.extend(questions_by_mark[5])
        final_questions.extend(questions_by_mark[6])
        final_questions.extend(questions_by_mark[7])
        final_questions.extend(questions_by_mark[8])
        
        random.shuffle(final_questions)
        arranged_questions.extend(final_questions)
        
        self.selected_questions = arranged_questions
        
        logger.info(f"[ARRANGE] Arranged into sections: "
                   f"Early={early_count}, Middle={len(middle_questions)}, Final={len(final_questions)}")
    
    def _validate_paper(self) -> Dict:
        """
        Step 7: Comprehensive validation
        
        Returns:
            Dictionary containing validation results
        """
        validation_report = {
            'all_passed': True,
            'passed_checks': [],
            'failed_checks': [],
            'warnings': []
        }
        
        # 1. Total marks validation
        if self.total_marks == self.paper.total_marks:
            validation_report['passed_checks'].append('Total marks exactly matches target')
        else:
            validation_report['failed_checks'].append(
                f'Total marks mismatch: got {self.total_marks}, expected {self.paper.total_marks}'
            )
            validation_report['all_passed'] = False
        
        # 2. Mark distribution validation
        total_q = len(self.selected_questions)
        
        # Use slightly relaxed tolerance for validation (±3%)
        tolerance = 3.0
        
        for mark_value in [1, 2, 3, 4]:
            count = self.mark_value_counts[mark_value]
            percent = (count / total_q * 100) if total_q > 0 else 0
            
            if mark_value == 1:
                min_p, max_p = self.config.one_mark_min_percent, self.config.one_mark_max_percent
            elif mark_value == 2:
                min_p, max_p = self.config.two_mark_min_percent, self.config.two_mark_max_percent
            elif mark_value == 3:
                min_p, max_p = self.config.three_mark_min_percent, self.config.three_mark_max_percent
            else:
                min_p, max_p = self.config.four_mark_min_percent, self.config.four_mark_max_percent
            
            # Apply tolerance
            if (min_p - tolerance) <= percent <= (max_p + tolerance):
                validation_report['passed_checks'].append(
                    f'{mark_value}-mark questions: {percent:.1f}% (target: {min_p}-{max_p}%)'
                )
            else:
                validation_report['failed_checks'].append(
                    f'{mark_value}-mark questions: {percent:.1f}% out of range (target: {min_p}-{max_p}%)'
                )
                validation_report['all_passed'] = False
        
        # 3. Topic coverage validation
        # Use slightly relaxed tolerance for topic marks (±1 mark)
        topic_tolerance = 1
        
        for topic_id, constraints in self.topic_constraints.items():
            current = self.topic_mark_counts[topic_id]
            min_m, max_m = constraints['min_marks'], constraints['max_marks']
            
            if (min_m - topic_tolerance) <= current <= (max_m + topic_tolerance):
                validation_report['passed_checks'].append(
                    f"{constraints['name']}: {current} marks (target: {min_m}-{max_m})"
                )
            else:
                validation_report['failed_checks'].append(
                    f"{constraints['name']}: {current} marks out of range (target: {min_m}-{max_m})"
                )
                validation_report['all_passed'] = False
        
        # 4. Question count validation
        # Prefer exact match with the generation target_question_count when set
        if getattr(self, 'target_question_count', None) is not None:
            if total_q == self.target_question_count:
                validation_report['passed_checks'].append(
                    f'Question count: {total_q} (target: {self.target_question_count})'
                )
            else:
                validation_report['failed_checks'].append(
                    f'Question count: {total_q} out of range (target: {self.target_question_count})'
                )
                validation_report['all_passed'] = False
        else:
            if self.config.min_questions <= total_q <= self.config.max_questions:
                validation_report['passed_checks'].append(
                    f'Question count: {total_q} (target: {self.config.min_questions}-{self.config.max_questions})'
                )
            else:
                validation_report['failed_checks'].append(
                    f'Question count: {total_q} out of range (target: {self.config.min_questions}-{self.config.max_questions})'
                )
                validation_report['all_passed'] = False
        
        # 5. Duplicate detection
        unique_ids = len(set(q.id for q in self.selected_questions))
        if unique_ids == total_q:
            validation_report['passed_checks'].append('No duplicate questions')
        else:
            validation_report['failed_checks'].append(f'Duplicate questions detected: {total_q - unique_ids} duplicates')
            validation_report['all_passed'] = False
        
        # 6. Answer completeness
        questions_without_answers = sum(1 for q in self.selected_questions if not q.answer_text)
        if questions_without_answers == 0:
            validation_report['passed_checks'].append('All questions have answers')
        else:
            validation_report['failed_checks'].append(
                f'{questions_without_answers} questions lack complete answers'
            )
            validation_report['all_passed'] = False
        
        logger.info(f"[VALIDATION] Passed: {len(validation_report['passed_checks'])}, "
                   f"Failed: {len(validation_report['failed_checks'])}")
        
        return validation_report
    
    def _create_generated_paper(self, validation_report: Dict) -> GeneratedPaper:
        """
        Step 8: Create and save GeneratedPaper record
        
        Args:
            validation_report: Validation results
        
        Returns:
            GeneratedPaper instance
        """
        # Generate unique code
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_code = f"KCSE-BIO-P1-{timestamp}"
        
        # Prepare distributions
        mark_distribution = {
            'one_mark': self.mark_value_counts[1],
            'two_mark': self.mark_value_counts[2],
            'three_mark': self.mark_value_counts[3],
            'four_mark': self.mark_value_counts[4],
        }
        
        topic_distribution = {
            constraints['name']: self.topic_mark_counts[topic_id]
            for topic_id, constraints in self.topic_constraints.items()
        }
        
        question_type_distribution = dict(self.question_type_counts)
        
        # Topic adjustments
        topic_adjustments = {
            constraints['name']: {
                'original_min': constraints['original_min'],
                'original_max': constraints['original_max'],
                'adjusted_min': constraints['min_marks'],
                'adjusted_max': constraints['max_marks'],
            }
            for topic_id, constraints in self.topic_constraints.items()
        }
        
        # Create record
        generated_paper = GeneratedPaper.objects.create(
            paper=self.paper,
            unique_code=unique_code,
            status='validated',
            question_ids=[str(q.id) for q in self.selected_questions],
            selected_topics=self.selected_topic_ids,
            topic_adjustments=topic_adjustments,
            total_marks=self.total_marks,
            total_questions=len(self.selected_questions),
            mark_distribution=mark_distribution,
            topic_distribution=topic_distribution,
            question_type_distribution=question_type_distribution,
            validation_passed=validation_report['all_passed'],
            validation_report=validation_report,
            generation_attempts=self.generation_attempts,
            backtracking_count=self.backtracking_count,
            generation_time_seconds=time.time() - self.generation_start_time,
            generated_by=self.user,
        )
        
        # Update question usage statistics
        for question in self.selected_questions:
            question.times_used += 1
            question.last_used = timezone.now()
        
        Question.objects.bulk_update(
            self.selected_questions,
            ['times_used', 'last_used']
        )
        
        logger.info(f"[SAVED] Generated paper: {unique_code}")
        
        return generated_paper
