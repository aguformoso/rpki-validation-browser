# Generated by Django 2.2 on 2019-07-01 11:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
