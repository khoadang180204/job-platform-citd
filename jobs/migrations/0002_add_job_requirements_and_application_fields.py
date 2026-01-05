# Generated migration for new fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        # Add job_requirements ManyToMany to Job
        migrations.AddField(
            model_name='job',
            name='job_requirements',
            field=models.ManyToManyField(blank=True, related_name='jobs', to='jobs.requirement'),
        ),
        # Add new fields to Application
        migrations.AddField(
            model_name='application',
            name='full_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='applications/photos/'),
        ),
        migrations.AddField(
            model_name='application',
            name='cv_file',
            field=models.FileField(blank=True, null=True, upload_to='applications/cv/'),
        ),
        migrations.AddField(
            model_name='application',
            name='introduction',
            field=models.TextField(blank=True, help_text='Giới thiệu bản thân ngắn gọn', null=True),
        ),
    ]
