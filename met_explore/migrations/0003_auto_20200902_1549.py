# Generated by Django 3.0.5 on 2020-09-02 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('met_explore', '0002_uniquetoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uniquetoken',
            name='name',
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
