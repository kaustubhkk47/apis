# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-30 07:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_auto_20160516_2252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productdetails',
            name='remarks',
            field=models.TextField(blank=True),
        ),
    ]
