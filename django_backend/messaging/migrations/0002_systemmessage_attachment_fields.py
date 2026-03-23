from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemmessage',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='system_messages/'),
        ),
        migrations.AddField(
            model_name='systemmessage',
            name='attachment_content_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='systemmessage',
            name='attachment_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
