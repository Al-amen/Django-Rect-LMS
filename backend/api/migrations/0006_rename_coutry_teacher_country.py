# Generated by Django 5.2.3 on 2025-07-14 03:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_cartorder_options_alter_category_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teacher',
            old_name='coutry',
            new_name='country',
        ),
    ]
