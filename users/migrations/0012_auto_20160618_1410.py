# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-18 14:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
        ('catalog', '0010_auto_20160615_1556'),
        ('users', '0011_auto_20160616_1059'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_type', models.CharField(max_length=30)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='BuyerBuysFrom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.BusinessType')),
            ],
        ),
        migrations.CreateModel(
            name='BuyerInterest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scale', models.PositiveIntegerField(default=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='BuyerPurchasingState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='buyerdetails',
            name='buys_from',
        ),
        migrations.AddField(
            model_name='buyer',
            name='blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='buyeraddress',
            name='pincode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='address.Pincode'),
        ),
        migrations.AddField(
            model_name='selleraddress',
            name='pincode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='address.Pincode'),
        ),
        migrations.AlterField(
            model_name='buyerdetails',
            name='buying_capacity',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='buyerdetails',
            name='customer_type',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='buyerpurchasingstate',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Buyer'),
        ),
        migrations.AddField(
            model_name='buyerpurchasingstate',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='address.State'),
        ),
        migrations.AddField(
            model_name='buyerinterest',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Buyer'),
        ),
        migrations.AddField(
            model_name='buyerinterest',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.Category'),
        ),
        migrations.AddField(
            model_name='buyerbuysfrom',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Buyer'),
        ),
        migrations.AddField(
            model_name='buyerdetails',
            name='buyer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.BusinessType'),
        ),
        migrations.AddField(
            model_name='sellerdetails',
            name='seller_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.BusinessType'),
        ),
    ]