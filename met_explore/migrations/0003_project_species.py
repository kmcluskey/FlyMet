# Generated by Django 3.1.8 on 2021-06-16 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('met_explore', '0002_project_metadata'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='species',
            field=models.CharField(default='Drosophila melanogaster', max_length=500),
            preserve_default=False,
        ),
    ]