# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-15 15:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_auto_20160613_1736'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['priority', 'id']},
        ),
    ]
