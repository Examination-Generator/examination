"""
Management command to add comprehensive nested questions for all Biology topics
"""
from django.core.management.base import BaseCommand
from api.models import Question, Paper, Topic


class Command(BaseCommand):
    help = 'Add comprehensive nested questions for all Biology Paper 1 topics'

    def handle(self, *args, **options):
        try:
            paper1 = Paper.objects.get(name='Paper 1')
            topics = {topic.name: topic for topic in Topic.objects.filter(paper=paper1)}

            nested_questions_data = [
                # Cell Biology (12 nested questions)
                {
                    'topic': 'Cell Biology',
                    'question_text': 'The diagram shows a plant cell as seen under an electron microscope.',
                    'marks': 4,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the organelle labeled P.'},
                        {'part': 'b', 'marks': 2, 'text': 'State two functions of organelle P.'},
                        {'part': 'c', 'marks': 1, 'text': 'Name the process that occurs in organelle P.'},
                    ],
                    'answer_text': 'a) Chloroplast\nb) - Photosynthesis/food manufacture; Contains chlorophyll\nc) Photosynthesis',
                    'difficulty': 'easy'
                },
                {
                    'topic': 'Cell Biology',
                    'question_text': 'Study the diagram of a bacterial cell.',
                    'marks': 5,
                    'nested_parts': [
                        {'part': 'a', 'marks': 2, 'text': 'State two differences between a bacterial cell and a plant cell.'},
                        {'part': 'b', 'marks': 2, 'text': 'Explain the importance of the capsule in bacteria.'},
                        {'part': 'c', 'marks': 1, 'text': 'Name the structure responsible for bacterial movement.'},
                    ],
                    'answer_text': 'a) - Bacteria lack nucleus while plant has nucleus; Bacteria lack membrane-bound organelles; Bacteria have circular DNA while plant has linear DNA\nb) Protects bacteria from phagocytosis; Prevents dehydration; Helps bacteria adhere to surfaces\nc) Flagellum',
                    'difficulty': 'medium'
                },
                {
                    'topic': 'Cell Biology',
                    'question_text': 'A student observed cells under a microscope at different magnifications.',
                    'marks': 6,
                    'nested_parts': [
                        {'part': 'a', 'marks': 2, 'text': 'Distinguish between magnification and resolution.'},
                        {'part': 'b', 'marks': 2, 'text': 'Calculate the actual size of a cell that appears 5mm under ×400 magnification.'},
                        {'part': 'c', 'marks': 2, 'text': 'Explain why oil immersion is used when viewing specimens under high power.'},
                    ],
                    'answer_text': 'a) Magnification is increase in apparent size while resolution is ability to distinguish two close points; Magnification involves enlargement while resolution involves clarity\nb) Actual size = Image size ÷ Magnification = 5mm ÷ 400 = 0.0125mm or 12.5µm\nc) Oil increases refractive index; Prevents light scattering; Improves resolution and clarity',
                    'difficulty': 'hard'
                },
                {
                    'topic': 'Cell Biology',
                    'question_text': 'An experiment was set up to investigate osmosis in plant cells.',
                    'marks': 5,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Define osmosis.'},
                        {'part': 'b', 'marks': 2, 'text': 'Account for the change in mass observed in the potato strips.'},
                        {'part': 'c', 'marks': 2, 'text': 'Explain why animal cells placed in distilled water will burst.'},
                    ],
                    'answer_text': 'a) Movement of water molecules from a region of high water potential to low water potential through a semi-permeable membrane\nb) Water moved into potato cells by osmosis; Cells became turgid increasing mass\nc) Water enters by osmosis; Animal cells lack cell wall; Cannot withstand turgor pressure',
                    'difficulty': 'medium'
                },
                {
                    'topic': 'Cell Biology',
                    'question_text': 'The diagram shows different stages of mitosis.',
                    'marks': 6,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the stage labeled X.'},
                        {'part': 'b', 'marks': 3, 'text': 'Describe what happens during stage X.'},
                        {'part': 'c', 'marks': 2, 'text': 'State the importance of mitosis in organisms.'},
                    ],
                    'answer_text': 'a) Metaphase\nb) Chromosomes align at the equator/center of the cell; Spindle fibers attach to centromeres; Chromosomes are at maximum condensation\nc) Growth and repair of tissues; Asexual reproduction; Maintains chromosome number',
                    'difficulty': 'medium'
                },

                # Nutrition (12 nested questions)
                {
                    'topic': 'Nutrition',
                    'question_text': 'An investigation was conducted on the effect of light intensity on photosynthesis.',
                    'marks': 5,
                    'nested_parts': [
                        {'part': 'a', 'marks': 2, 'text': 'State two factors that should be kept constant in this experiment.'},
                        {'part': 'b', 'marks': 2, 'text': 'Explain the effect of light intensity on the rate of photosynthesis.'},
                        {'part': 'c', 'marks': 1, 'text': 'Name the process that produces oxygen during photosynthesis.'},
                    ],
                    'answer_text': 'a) - Temperature; Carbon dioxide concentration; Water availability\nb) Increasing light intensity increases rate of photosynthesis; Up to an optimum point; Beyond which rate plateaus as other factors become limiting\nc) Photolysis of water',
                    'difficulty': 'medium'
                },
                {
                    'topic': 'Nutrition',
                    'question_text': 'The diagram shows the alimentary canal of a mammal.',
                    'marks': 4,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the part labeled Y.'},
                        {'part': 'b', 'marks': 2, 'text': 'State two functions of part Y.'},
                        {'part': 'c', 'marks': 1, 'text': 'Name the enzyme produced in part Y that acts on proteins.'},
                    ],
                    'answer_text': 'a) Stomach\nb) - Mechanical digestion/churning; Chemical digestion of proteins; Kills bacteria; Stores food temporarily\nc) Pepsin',
                    'difficulty': 'easy'
                },
                {
                    'topic': 'Nutrition',
                    'question_text': 'A food test was conducted on a sample using different reagents.',
                    'marks': 6,
                    'nested_parts': [
                        {'part': 'a', 'marks': 2, 'text': 'Describe how to test for the presence of reducing sugars.'},
                        {'part': 'b', 'marks': 2, 'text': 'Distinguish between reducing and non-reducing sugars.'},
                        {'part': 'c', 'marks': 2, 'text': 'Explain why the Benedict\'s test must be heated.'},
                    ],
                    'answer_text': 'a) Add Benedict\'s solution to the sample; Heat in a water bath at 80-100°C; Blue to brick-red/orange precipitate indicates presence\nb) Reducing sugars give positive test with Benedict\'s directly while non-reducing sugars must be hydrolyzed first; Examples: glucose (reducing), sucrose (non-reducing)\nc) Heating provides energy for the chemical reaction; Enables copper ions to be reduced; Forms copper oxide precipitate',
                    'difficulty': 'medium'
                },
                {
                    'topic': 'Nutrition',
                    'question_text': 'Study the diagram showing structure of a leaf.',
                    'marks': 5,
                    'nested_parts': [
                        {'part': 'a', 'marks': 2, 'text': 'State two adaptations of the leaf for photosynthesis.'},
                        {'part': 'b', 'marks': 2, 'text': 'Explain the role of stomata in photosynthesis.'},
                        {'part': 'c', 'marks': 1, 'text': 'Name the cells that regulate the opening of stomata.'},
                    ],
                    'answer_text': 'a) - Broad surface area for light absorption; Thin for easy gas diffusion; Contains chlorophyll; Network of veins for transport\nb) Allow entry of carbon dioxide needed for photosynthesis; Allow exit of oxygen produced; Control water loss through transpiration\nc) Guard cells',
                    'difficulty': 'easy'
                },

                # Respiration (12 nested questions)
                {
                    'topic': 'Respiration',
                    'question_text': 'An experiment was set up to investigate anaerobic respiration in yeast.',
                    'marks': 5,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the gas produced during anaerobic respiration in yeast.'},
                        {'part': 'b', 'marks': 2, 'text': 'Write a word equation for anaerobic respiration in yeast.'},
                        {'part': 'c', 'marks': 2, 'text': 'Explain why lime water turns milky in this experiment.'},
                    ],
                    'answer_text': 'a) Carbon dioxide\nb) Glucose → Ethanol + Carbon dioxide + Energy\nc) Carbon dioxide reacts with calcium hydroxide in lime water; Forms calcium carbonate which is insoluble/white precipitate',
                    'difficulty': 'easy'
                },
                {
                    'topic': 'Respiration',
                    'question_text': 'The diagram shows the human respiratory system.',
                    'marks': 6,
                    'nested_parts': [
                        {'part': 'a', 'marks': 2, 'text': 'State two adaptations of the alveoli for gaseous exchange.'},
                        {'part': 'b', 'marks': 2, 'text': 'Explain how oxygen moves from alveoli into blood.'},
                        {'part': 'c', 'marks': 2, 'text': 'Account for the difference in oxygen concentration between inspired and expired air.'},
                    ],
                    'answer_text': 'a) - Thin walls/one cell thick; Large surface area; Moist walls; Rich blood supply\nb) Oxygen diffuses down concentration gradient; From high concentration in alveoli to low concentration in blood; Through alveolar and capillary walls\nc) Oxygen in inspired air diffuses into blood in alveoli; Used in cellular respiration in body tissues; Therefore expired air has less oxygen',
                    'difficulty': 'medium'
                },
                {
                    'topic': 'Respiration',
                    'question_text': 'Study the graph showing oxygen debt in a sprinter.',
                    'marks': 4,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Define oxygen debt.'},
                        {'part': 'b', 'marks': 2, 'text': 'Explain why oxygen debt occurs during intense exercise.'},
                        {'part': 'c', 'marks': 1, 'text': 'Name the substance that accumulates causing muscle fatigue.'},
                    ],
                    'answer_text': 'a) Amount of oxygen needed to oxidize lactic acid accumulated during anaerobic respiration\nb) Muscles require more oxygen than supplied during intense exercise; Anaerobic respiration occurs; Lactic acid accumulates\nc) Lactic acid',
                    'difficulty': 'medium'
                },

                # Excretion and Homeostasis (12 nested questions)
                {
                    'topic': 'Excretion and Homeostasis',
                    'question_text': 'The diagram shows a nephron from the kidney.',
                    'marks': 5,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the process that occurs in the glomerulus.'},
                        {'part': 'b', 'marks': 2, 'text': 'State two substances that are filtered from blood in the glomerulus.'},
                        {'part': 'c', 'marks': 2, 'text': 'Explain why proteins are not normally found in the filtrate.'},
                    ],
                    'answer_text': 'a) Ultrafiltration\nb) - Water; Glucose; Urea; Salts/mineral ions; Amino acids\nc) Proteins are too large molecules; Cannot pass through basement membrane of glomerulus',
                    'difficulty': 'medium'
                },
                {
                    'topic': 'Excretion and Homeostasis',
                    'question_text': 'An investigation was conducted on temperature regulation in humans.',
                    'marks': 6,
                    'nested_parts': [
                        {'part': 'a', 'marks': 2, 'text': 'Distinguish between ectotherms and endotherms.'},
                        {'part': 'b', 'marks': 2, 'text': 'Explain how sweating helps cool the body.'},
                        {'part': 'c', 'marks': 2, 'text': 'Account for shivering when body temperature drops.'},
                    ],
                    'answer_text': 'a) Ectotherms depend on external sources for body heat while endotherms generate heat internally; Ectotherms have variable body temperature while endotherms maintain constant temperature\nb) Sweat evaporates from skin surface; Takes latent heat of vaporization from body; Cools the body\nc) Rapid muscle contractions; Generate heat through respiration; Raises body temperature',
                    'difficulty': 'hard'
                },
                {
                    'topic': 'Excretion and Homeostasis',
                    'question_text': 'Study the composition of blood plasma and urine.',
                    'marks': 4,
                    'nested_parts': [
                        {'part': 'a', 'marks': 2, 'text': 'Account for the presence of glucose in blood plasma but not in urine.'},
                        {'part': 'b', 'marks': 2, 'text': 'Explain why urea concentration is higher in urine than in blood plasma.'},
                    ],
                    'answer_text': 'a) Glucose is filtered in glomerulus; All glucose is reabsorbed in proximal convoluted tubule; Therefore absent in urine of healthy person\nb) Urea is filtered in glomerulus; Not reabsorbed in the tubule; Water is reabsorbed concentrating urea in urine',
                    'difficulty': 'medium'
                },

                # Coordination and Response (12 nested questions)
                {
                    'topic': 'Coordination and Response',
                    'question_text': 'The diagram shows a reflex arc.',
                    'marks': 5,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the neuron labeled X.'},
                        {'part': 'b', 'marks': 2, 'text': 'State the path of a nerve impulse in a reflex action.'},
                        {'part': 'c', 'marks': 2, 'text': 'Explain the advantage of reflex actions.'},
                    ],
                    'answer_text': 'a) Relay neuron/intermediate neuron\nb) Receptor → Sensory neuron → Relay neuron → Motor neuron → Effector\nc) Rapid response to stimuli; Automatic/involuntary; Protects body from danger; Does not involve conscious thought',
                    'difficulty': 'easy'
                },
                {
                    'topic': 'Coordination and Response',
                    'question_text': 'An experiment was conducted to investigate phototropism in seedlings.',
                    'marks': 6,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Define phototropism.'},
                        {'part': 'b', 'marks': 3, 'text': 'Explain how auxins cause the shoot to bend towards light.'},
                        {'part': 'c', 'marks': 2, 'text': 'State the importance of phototropism in plants.'},
                    ],
                    'answer_text': 'a) Growth response of plants to light stimulus\nb) Auxins produced in shoot tip; Accumulate on shaded side; Stimulate cell elongation on shaded side more than lighted side; Causing shoot to bend towards light\nc) Ensures leaves receive maximum light for photosynthesis; Enhances survival of plant',
                    'difficulty': 'medium'
                },
                {
                    'topic': 'Coordination and Response',
                    'question_text': 'Study the diagram of the human eye.',
                    'marks': 5,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the structure that controls the amount of light entering the eye.'},
                        {'part': 'b', 'marks': 2, 'text': 'Explain how the eye accommodates to view distant objects.'},
                        {'part': 'c', 'marks': 2, 'text': 'Account for short-sightedness in humans.'},
                    ],
                    'answer_text': 'a) Iris\nb) Ciliary muscles relax; Suspensory ligaments become taut; Lens becomes thinner/less convex; Focus image on retina\nc) Eyeball too long or lens too convex; Image focused in front of retina; Corrected using concave/diverging lens',
                    'difficulty': 'medium'
                },

                # Reproduction (12 nested questions)
                {
                    'topic': 'Reproduction',
                    'question_text': 'The diagram shows a flower structure.',
                    'marks': 4,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the male reproductive part of the flower.'},
                        {'part': 'b', 'marks': 2, 'text': 'State two adaptations of wind-pollinated flowers.'},
                        {'part': 'c', 'marks': 1, 'text': 'Name the process by which pollen grains are transferred to the stigma.'},
                    ],
                    'answer_text': 'a) Stamen/anther\nb) - Produce large amounts of pollen; Light and smooth pollen; Feathery stigma; Dull colored petals; Exposed anthers\nc) Pollination',
                    'difficulty': 'easy'
                },
                {
                    'topic': 'Reproduction',
                    'question_text': 'Study the diagram of the human female reproductive system.',
                    'marks': 6,
                    'nested_parts': [
                        {'part': 'a', 'marks': 1, 'text': 'Name the site where fertilization occurs.'},
                        {'part': 'b', 'marks': 3, 'text': 'Describe the process of fertilization in humans.'},
                        {'part': 'c', 'marks': 2, 'text': 'Explain the role of the placenta during pregnancy.'},
                    ],
                    'answer_text': 'a) Fallopian tube/oviduct\nb) Sperm cells swim to fallopian tube; Acrosome releases enzymes to penetrate ovum; Nucleus of sperm fuses with nucleus of ovum; Forms a zygote\nc) Allows exchange of nutrients and oxygen from mother to fetus; Removes waste products from fetus; Produces hormones to maintain pregnancy; Acts as barrier to harmful substances',
                    'difficulty': 'medium'
                },
                {
                    'topic': 'Reproduction',
                    'question_text': 'An investigation was conducted on seed germination.',
                    'marks': 5,
                    'nested_parts': [
                        {'part': 'a', 'marks': 2, 'text': 'State three conditions necessary for seed germination.'},
                        {'part': 'b', 'marks': 2, 'text': 'Explain why seeds in set-up A did not germinate.'},
                        {'part': 'c', 'marks': 1, 'text': 'Name the process by which stored food is broken down during germination.'},
                    ],
                    'answer_text': 'a) - Water/moisture; Oxygen; Suitable temperature; (Light for some seeds)\nb) Seeds were deprived of oxygen; Oxygen needed for respiration; To provide energy for growth\nc) Respiration',
                    'difficulty': 'easy'
                },
            ]

            created_count = 0
            for data in nested_questions_data:
                topic = topics.get(data['topic'])
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
                        difficulty=data['difficulty'],
                        is_active=True
                    )
                    created_count += 1
                    self.stdout.write(f'  Created: {data["topic"]} - {data["marks"]}m ({data["difficulty"]})')
                else:
                    self.stdout.write(self.style.WARNING(f'  Topic not found: {data["topic"]}'))

            self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {created_count} nested questions'))
            
            # Show distribution
            self.stdout.write('\n📊 Distribution by topic:')
            for topic_name in ['Cell Biology', 'Nutrition', 'Respiration', 'Excretion and Homeostasis', 
                              'Coordination and Response', 'Reproduction']:
                count = sum(1 for q in nested_questions_data if q['topic'] == topic_name)
                self.stdout.write(f'  {topic_name}: {count} questions')

        except Paper.DoesNotExist:
            self.stdout.write(self.style.ERROR('Paper 1 not found. Please run migrations first.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
