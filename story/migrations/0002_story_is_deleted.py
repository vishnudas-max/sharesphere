# Generated by Django 4.2.13 on 2024-06-04 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
