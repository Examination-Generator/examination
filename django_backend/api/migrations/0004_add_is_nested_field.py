# Generated migration for nested question structure

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_paper_time_allocation_paper_total_marks_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='is_nested',
            field=models.BooleanField(
                default=False,
                help_text='True if question has multiple parts (a, b, c, d). Marks represent total for all parts.'
            ),
        ),
        migrations.AddField(
            model_name='question',
            name='nested_parts',
            field=models.JSONField(
                default=list,
                blank=True,
                help_text='Array of parts: [{"part": "a", "marks": 2, "text": "..."}, ...]'
            ),
        ),
    ]
