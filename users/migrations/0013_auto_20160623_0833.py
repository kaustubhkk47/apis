# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-23 08:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20160618_1410'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuyerInterestHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scale', models.PositiveIntegerField(default=5)),
                ('price_filter_applied', models.BooleanField(default=False)),
                ('min_price_per_unit', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=10)),
                ('max_price_per_unit', models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=10)),
                ('fabric_filter_text', models.TextField(blank=True)),
                ('productid_filter_text', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='buyerinterest',
            name='delete_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='buyerinterest',
            name='fabric_filter_text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='buyerinterest',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='buyerinterest',
            name='max_price_per_unit',
            field=models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='buyerinterest',
            name='min_price_per_unit',
            field=models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='buyerinterest',
            name='price_filter_applied',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='buyerinterest',
            name='productid_filter_text',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='buyer',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='buyerinteresthistory',
            name='buyer_interest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.BuyerInterest'),
        ),
    ]