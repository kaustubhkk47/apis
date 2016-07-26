# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-16 10:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20160615_1556'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyerdetails',
            name='purchasing_states',
        ),
        migrations.AlterField(
            model_name='buyerdetails',
            name='purchase_duration',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
