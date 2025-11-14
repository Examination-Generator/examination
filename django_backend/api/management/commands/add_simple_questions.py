"""
Management command to add questions with simplified nested structure.
Nested questions only need is_nested=True and total marks (no parts breakdown).
"""
from django.core.management.base import BaseCommand
from api.models import Question, Topic, Paper
import random


class Command(BaseCommand):
    help = 'Add questions with simplified nested structure (no parts needed)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding questions to the database...'))
        
        # Get Paper 1
        paper = Paper.objects.filter(name='Paper 1').first()
        if not paper:
            self.stdout.write(self.style.ERROR('Paper 1 not found!'))
            return
        
        # Get all topics
        topics = list(Topic.objects.all())
        if not topics:
            self.stdout.write(self.style.ERROR('No topics found!'))
            return
        
        self.stdout.write(f'Found {len(topics)} topics')
        
        # Delete existing questions to start fresh
        deleted_count = Question.objects.all().delete()[0]
        self.stdout.write(f'Deleted {deleted_count} existing questions')
        
        # Add nested questions (target: 100)
        self.add_nested_questions(paper, topics, 100)
        
        # Add standalone questions (target: 150)
        self.add_standalone_questions(paper, topics, 150)
        
        # Show final counts
        total_nested = Question.objects.filter(is_nested=True).count()
        total_standalone = Question.objects.filter(is_nested=False).count()
        
        self.stdout.write(self.style.SUCCESS(f'\n=== FINAL COUNTS ==='))
        self.stdout.write(self.style.SUCCESS(f'Nested questions: {total_nested}'))
        self.stdout.write(self.style.SUCCESS(f'Standalone questions: {total_standalone}'))
        self.stdout.write(self.style.SUCCESS(f'Total: {total_nested + total_standalone}'))
        
    def add_nested_questions(self, paper, topics, target_count):
        """Add nested questions (only is_nested and total marks needed)"""
        self.stdout.write('\n=== Adding Nested Questions ===')
        self.stdout.write(f'Target: {target_count} nested questions')
        
        # Simplified nested question templates (no parts breakdown)
        nested_templates = {
            'Cell Biology': [
                {'text': 'The diagram below shows a plant cell.', 'marks': 4},
                {'text': 'Study the structure of a mitochondrion.', 'marks': 5},
                {'text': 'The following diagram shows osmosis in cells.', 'marks': 6},
                {'text': 'The diagram shows cell division process.', 'marks': 4},
                {'text': 'Study the diagram of an animal cell below.', 'marks': 5},
                {'text': 'The diagram shows DNA structure.', 'marks': 4},
                {'text': 'Study the process of active transport.', 'marks': 5},
                {'text': 'The diagram shows different types of cells.', 'marks': 6},
                {'text': 'Study cell membrane structure.', 'marks': 7},
                {'text': 'The diagram shows protein synthesis.', 'marks': 6},
            ],
            'Ecology': [
                {'text': 'The diagram shows a food web.', 'marks': 5},
                {'text': 'Study the carbon cycle diagram below.', 'marks': 6},
                {'text': 'The following shows an ecosystem.', 'marks': 5},
                {'text': 'Study the nitrogen cycle.', 'marks': 6},
                {'text': 'The diagram shows energy pyramid.', 'marks': 5},
                {'text': 'Study the biotic and abiotic factors.', 'marks': 4},
                {'text': 'The diagram shows ecological succession.', 'marks': 6},
                {'text': 'Study the population growth curve.', 'marks': 5},
                {'text': 'The diagram shows nutrient cycling.', 'marks': 7},
                {'text': 'Study the water cycle.', 'marks': 5},
            ],
            'Nutrition': [
                {'text': 'The diagram shows the human digestive system.', 'marks': 6},
                {'text': 'Study the process of photosynthesis below.', 'marks': 5},
                {'text': 'The following shows enzyme action.', 'marks': 5},
                {'text': 'Study the light reaction of photosynthesis.', 'marks': 4},
                {'text': 'The diagram shows structure of small intestine.', 'marks': 5},
                {'text': 'Study the graph of enzyme activity vs temperature.', 'marks': 6},
                {'text': 'The diagram shows autotrophic vs heterotrophic nutrition.', 'marks': 7},
                {'text': 'Study the absorption of nutrients.', 'marks': 5},
                {'text': 'The diagram shows dental formula.', 'marks': 4},
                {'text': 'Study mineral deficiency symptoms.', 'marks': 6},
            ],
            'Reproduction': [
                {'text': 'The diagram shows the human reproductive system.', 'marks': 6},
                {'text': 'Study the menstrual cycle below.', 'marks': 6},
                {'text': 'The following shows seed germination.', 'marks': 4},
                {'text': 'Study the flower structure.', 'marks': 5},
                {'text': 'The diagram shows types of pollination.', 'marks': 5},
                {'text': 'Study sexual vs asexual reproduction.', 'marks': 6},
                {'text': 'The diagram shows embryo development.', 'marks': 7},
                {'text': 'Study the fertilization process.', 'marks': 5},
                {'text': 'The diagram shows placenta structure.', 'marks': 6},
                {'text': 'Study fruit formation and dispersal.', 'marks': 5},
            ],
            'Respiration': [
                {'text': 'The diagram shows aerobic respiration.', 'marks': 6},
                {'text': 'Study the structure of ATP below.', 'marks': 4},
                {'text': 'The following shows the Krebs cycle.', 'marks': 5},
                {'text': 'Study aerobic vs anaerobic respiration in yeast.', 'marks': 6},
                {'text': 'The diagram shows glycolysis pathway.', 'marks': 7},
                {'text': 'Study the electron transport chain.', 'marks': 6},
                {'text': 'The diagram shows cellular respiration overview.', 'marks': 5},
                {'text': 'Study energy yield from glucose breakdown.', 'marks': 5},
                {'text': 'The diagram shows anaerobic respiration in muscles.', 'marks': 4},
                {'text': 'Study the respiratory quotient.', 'marks': 6},
            ],
            'Transport': [
                {'text': 'The diagram shows the human circulatory system.', 'marks': 6},
                {'text': 'Study the structure of the heart below.', 'marks': 6},
                {'text': 'The following shows blood composition.', 'marks': 5},
                {'text': 'Study the cardiac cycle.', 'marks': 4},
                {'text': 'The diagram shows xylem and phloem tissues.', 'marks': 5},
                {'text': 'Study the graph of blood pressure changes.', 'marks': 6},
                {'text': 'The diagram shows double circulation system.', 'marks': 7},
                {'text': 'Study transpiration in plants.', 'marks': 5},
                {'text': 'The diagram shows root pressure mechanism.', 'marks': 4},
                {'text': 'Study the lymphatic system.', 'marks': 6},
            ]
        }
        
        added = 0
        for _ in range(target_count):
            topic = random.choice(topics)
            
            if topic.name in nested_templates:
                template = random.choice(nested_templates[topic.name])
                
                # Add variation to question text
                variations = [
                    'Study the diagram below.',
                    'The following shows an important biological process.',
                    'Examine the structure shown.',
                    'The illustration below demonstrates a key concept.',
                    'Observe the following biological system.'
                ]
                
                question_text = f"{random.choice(variations)} {template['text']}"
                
                question = Question.objects.create(
                    subject=paper.subject,
                    paper=paper,
                    topic=topic,
                    question_text=question_text,
                    marks=template['marks'],
                    is_nested=True,
                    nested_parts=None,  # Not needed - only is_nested and marks matter
                    answer_text=f"Complete answer for {template['marks']}-mark nested question.",
                    kcse_question_type='structured',
                    is_active=True
                )
                added += 1
        
        self.stdout.write(self.style.SUCCESS(f'Added {added} nested questions'))
    
    def add_standalone_questions(self, paper, topics, target_count):
        """Add standalone questions (1-4 marks each)"""
        self.stdout.write('\n=== Adding Standalone Questions ===')
        self.stdout.write(f'Target: {target_count} standalone questions')
        
        # Question starters for different types
        question_starters = {
            'name_identify': [
                'Name the process shown in',
                'Identify the structure labeled',
                'Name the organism that',
                'Identify the part responsible for'
            ],
            'state_give_reasons': [
                'State the function of',
                'Give reasons why',
                'State two adaptations of',
                'Give the importance of'
            ],
            'distinguish': [
                'Distinguish between',
                'Differentiate between',
                'State the difference between',
                'Compare and contrast'
            ],
            'explain_account': [
                'Explain why',
                'Account for the fact that',
                'Explain the role of',
                'Account for the observation that'
            ],
            'describe': [
                'Describe the process of',
                'Describe how',
                'Describe the structure of',
                'Describe the mechanism of'
            ]
        }
        
        question_types = list(question_starters.keys())
        
        added = 0
        for _ in range(target_count):
            topic = random.choice(topics)
            question_type = random.choice(question_types)
            starter = random.choice(question_starters[question_type])
            
            # Marks distribution for standalone: prefer 2-3 marks
            marks_pool = [1] * 25 + [2] * 35 + [3] * 25 + [4] * 15  # Weighted distribution
            marks = random.choice(marks_pool)
            
            question = Question.objects.create(
                subject=paper.subject,
                paper=paper,
                topic=topic,
                question_text=f"{starter} {topic.name.lower()}.",
                marks=marks,
                is_nested=False,
                nested_parts=None,
                answer_text=f"Answer for {marks}-mark question on {topic.name}.",
                kcse_question_type=question_type,
                is_active=True
            )
            added += 1
        
        self.stdout.write(self.style.SUCCESS(f'Added {added} standalone questions'))
