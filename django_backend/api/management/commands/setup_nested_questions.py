"""
Management command to set up nested question structure for Biology Paper 1
"""
from django.core.management.base import BaseCommand
from api.models import Question, Paper, Topic


class Command(BaseCommand):
    help = 'Set up nested questions for Biology Paper 1'

    def handle(self, *args, **options):
        # Step 1: Mark all existing questions as standalone (is_nested=False)
        all_questions = Question.objects.all()
        updated_count = all_questions.update(is_nested=False, nested_parts=[])
        self.stdout.write(self.style.SUCCESS(f'Marked {updated_count} existing questions as standalone'))

        # Step 2: Create sample nested questions
        try:
            paper1 = Paper.objects.get(name='Paper 1')
            topics = Topic.objects.filter(paper=paper1)

            nested_questions_data = [
                {
                    'topic': 'Cell Biology',
                    'question_text': 'The diagram below shows a cell structure observed under an electron microscope.',
                    'marks': 5,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the structure labeled X.'},
                        {'part': 'b', 'marks': 2, 'text': 'State two functions of structure X.'},
                        {'part': 'c', 'marks': 2, 'text': 'Explain why this structure is more visible under an electron microscope than a light microscope.'},
                    ],
                    'answer_text': 'a) Mitochondrion\nb) - Site of cellular respiration; Produces ATP/energy\nc) Electron microscope has higher magnification and resolution; Can reveal internal structures of organelles'
                },
                {
                    'topic': 'Nutrition',
                    'question_text': 'An experiment was conducted to investigate the effect of temperature on enzyme activity.',
                    'marks': 6,
                    'nested_parts': [
                        {'part': 'a', 'marks': 2, 'text': 'State two precautions that should be taken during this experiment.'},
                        {'part': 'b', 'marks': 2, 'text': 'Explain the effect of temperature on enzyme activity.'},
                        {'part': 'c', 'marks': 2, 'text': 'Account for the shape of the graph obtained between 40°C and 60°C.'},
                    ],
                    'answer_text': 'a) - Maintain constant pH; Keep enzyme concentration constant; Use same substrate concentration\nb) Low temperature reduces kinetic energy, slowing enzyme-substrate collisions; Optimal temperature provides maximum enzyme activity; High temperature denatures enzyme\nc) Enzyme denatures at high temperatures; Active site changes shape; Enzyme-substrate complex cannot form'
                },
                {
                    'topic': 'Respiration',
                    'question_text': 'Study the diagram showing stages of cellular respiration.',
                    'marks': 7,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the process shown in stage A.'},
                        {'part': 'b', 'marks': 2, 'text': 'State the location where stage A occurs in the cell.'},
                        {'part': 'c', 'marks': 2, 'text': 'Distinguish between aerobic and anaerobic respiration.'},
                        {'part': 'd', 'marks': 2, 'text': 'Calculate the net ATP produced during glycolysis.'},
                    ],
                    'answer_text': 'a) Glycolysis\nb) Cytoplasm/cell cytosol\nc) Aerobic requires oxygen while anaerobic does not; Aerobic produces more ATP (38) while anaerobic produces less (2); Aerobic end product is CO2 and H2O while anaerobic produces lactic acid or ethanol\nd) 2 ATP (4 produced - 2 used)'
                },
            ]

            created_count = 0
            for data in nested_questions_data:
                topic = topics.filter(name=data['topic']).first()
                if topic:
                    question = Question.objects.create(
                        subject=paper1.subject,
                        paper=paper1,
                        topic=topic,
                        question_text=data['question_text'],
                        answer_text=data['answer_text'],
                        marks=data['marks'],
                        is_nested=True,
                        nested_parts=data['nested_parts'],
                        question_type='structured',
                        kcse_question_type='explain_account',
                        difficulty='medium',
                        is_active=True
                    )
                    created_count += 1
                    self.stdout.write(f'  Created nested question: {data["topic"]} ({data["marks"]} marks)')

            self.stdout.write(self.style.SUCCESS(f'\nCreated {created_count} nested questions'))
            self.stdout.write(self.style.SUCCESS('\nNested question setup complete!'))
            self.stdout.write(self.style.WARNING('\nNote: You need to create more nested questions (10-18 per topic) for full generation'))

        except Paper.DoesNotExist:
            self.stdout.write(self.style.ERROR('Paper 1 not found. Please run initial migrations first.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
