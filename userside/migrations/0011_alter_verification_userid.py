# Generated by Django 4.2.13 on 2024-07-13 11:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userside', '0010_verification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verification',
            name='userID',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='varifiedUsers', to=settings.AUTH_USER_MODEL),
        ),
    ]
