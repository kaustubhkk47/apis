# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-10 00:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20160706_2302'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyerproducts',
            name='shared_on_whatsapp',
            field=models.BooleanField(default=False),
        ),
    ]
