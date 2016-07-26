# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-13 17:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_auto_20160530_0754'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['priority', '-id']},
        ),
        migrations.AddField(
            model_name='category',
            name='priority',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
