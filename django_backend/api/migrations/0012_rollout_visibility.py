from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_paper_duration_hours_paper_duration_minutes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='is_rollout_enabled',
            field=models.BooleanField(
                default=True,
                help_text='Whether this subject is visible to paper-generation users',
            ),
        ),
        migrations.AddField(
            model_name='paper',
            name='is_rollout_enabled',
            field=models.BooleanField(
                default=True,
                help_text='Whether this paper is visible to paper-generation users',
            ),
        ),
        migrations.AddField(
            model_name='topic',
            name='is_rollout_enabled',
            field=models.BooleanField(
                default=True,
                help_text='Whether this topic is visible to paper-generation users',
            ),
        ),
    ]
