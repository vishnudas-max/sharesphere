# Generated by Django 4.2.13 on 2024-06-24 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0003_comments_commentime'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comments',
            name='comment_time',
        ),
    ]
