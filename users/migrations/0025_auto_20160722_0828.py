# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-22 08:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_auto_20160721_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyerpanelinstructionstracking',
            name='page_closed',
            field=models.TextField(blank=True),
        ),
    ]
