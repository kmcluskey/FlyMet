# Generated by Django 3.0.5 on 2020-09-03 11:46

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('met_explore', '0004_auto_20200903_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uniquetoken',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(2020, 9, 3, 11, 46, 15, 889166, tzinfo=utc)),
        ),
    ]