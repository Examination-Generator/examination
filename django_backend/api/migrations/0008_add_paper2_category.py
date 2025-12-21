# Generated migration for adding paper2_category field to Question model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_generatedpaper_metadata'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='paper2_category',
            field=models.CharField(
                blank=True,
                choices=[
                    ('graph', 'Graph Question'),
                    ('essay', 'Essay Question'),
                    ('structured', 'Structured Question'),
                ],
                help_text='Category for Paper 2 questions (graph/essay/structured). Used for Section B question selection.',
                max_length=20,
                null=True
            ),
        ),
    ]
