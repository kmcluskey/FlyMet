# Generated by Django 3.1.2 on 2020-10-29 12:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('met_explore', '0008_factor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sample',
            name='group',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='life_stage',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='mutant',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='tissue',
        ),
    ]
