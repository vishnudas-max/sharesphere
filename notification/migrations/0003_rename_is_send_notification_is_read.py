# Generated by Django 4.2.13 on 2024-07-07 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_notification_postid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='is_send',
            new_name='is_read',
        ),
    ]
