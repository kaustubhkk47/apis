# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-20 08:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0033_auto_20160819_0721'),
        ('orders', '0023_auto_20160819_1058'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(default=0)),
                ('payment_method', models.IntegerField(default=-1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('address_given_time', models.DateTimeField(blank=True, null=True)),
                ('summary_confirmed_time', models.DateTimeField(blank=True, null=True)),
                ('payment_done_time', models.DateTimeField(blank=True, null=True)),
                ('buyer_address_history', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.BuyerAddressHistory')),
                ('cart', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.Cart')),
            ],
            options={
                'verbose_name': 'Checkout',
                'verbose_name_plural': 'Checkout',
            },
        ),
    ]
