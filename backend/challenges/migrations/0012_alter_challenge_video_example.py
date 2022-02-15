# Generated by Django 4.0 on 2022-02-15 16:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0011_rename_challegewinner_challengewinner_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='video_example',
            field=models.FileField(blank=True, null=True, upload_to='video_examples/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4'])], verbose_name='example of perform'),
        ),
    ]