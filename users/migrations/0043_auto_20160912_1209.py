# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-12 12:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0042_buyerproductresponse_store_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyerproductresponse',
            name='store_discount',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=10, null=True),
        ),
    ]
