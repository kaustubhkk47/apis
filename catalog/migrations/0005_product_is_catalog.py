# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-08 11:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_auto_20160429_0331'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_catalog',
            field=models.BooleanField(default=False),
        ),
    ]
