# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-20 20:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('display_name', models.CharField(max_length=50)),
                ('slug', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit', models.CharField(max_length=15)),
                ('tax', models.DecimalField(decimal_places=2, max_digits=5)),
                ('max_discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('lot_size', models.PositiveIntegerField(default=1)),
                ('price_per_lot', models.DecimalField(decimal_places=2, max_digits=10)),
                ('images', models.CommaSeparatedIntegerField(blank=True, max_length=255)),
                ('verification', models.BooleanField(default=False)),
                ('show_online', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slug', models.CharField(blank=True, max_length=100)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Category')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Seller')),
            ],
        ),
        migrations.CreateModel(
            name='ProductDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seller_catalog_number', models.CharField(blank=True, max_length=200)),
                ('brand', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField()),
                ('gender', models.CharField(blank=True, max_length=20)),
                ('pattern', models.CharField(blank=True, max_length=40)),
                ('style', models.CharField(blank=True, max_length=40)),
                ('gsm', models.CharField(blank=True, max_length=40)),
                ('sleeve', models.CharField(blank=True, max_length=40)),
                ('neck_collar_type', models.CharField(blank=True, max_length=40)),
                ('length', models.CharField(blank=True, max_length=40)),
                ('work_decoration_type', models.CharField(blank=True, max_length=40)),
                ('colours', models.CharField(blank=True, max_length=100)),
                ('sizes', models.CharField(blank=True, max_length=100)),
                ('special_feature', models.TextField(blank=True)),
                ('manufactured_country', models.CharField(blank=True, default=b'India', max_length=50)),
                ('warranty', models.CharField(blank=True, max_length=100)),
                ('remarks', models.TextField()),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='catalog.Product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductLot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lot_size_from', models.IntegerField()),
                ('lot_size_to', models.IntegerField()),
                ('lot_discount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Product')),
            ],
        ),
    ]
