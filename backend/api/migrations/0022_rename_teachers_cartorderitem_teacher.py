# Generated by Django 5.2.3 on 2025-07-24 05:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_rename_teacher_cartorderitem_teachers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartorderitem',
            old_name='teachers',
            new_name='teacher',
        ),
    ]
