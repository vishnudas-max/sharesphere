# Generated by Django 4.2.13 on 2024-07-02 13:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('story', '0002_story_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='viewed_users',
            field=models.ManyToManyField(related_name='viewed_stories', to=settings.AUTH_USER_MODEL),
        ),
    ]
