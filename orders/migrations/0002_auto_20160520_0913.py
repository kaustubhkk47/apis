# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-20 09:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderitem',
            options={'ordering': ['-id']},
        ),
    ]
