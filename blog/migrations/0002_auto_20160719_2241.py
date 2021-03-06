# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-19 22:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ['-id'], 'verbose_name': 'Article', 'verbose_name_plural': 'Articles'},
        ),
        migrations.AlterField(
            model_name='article',
            name='blogspot_link',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='article',
            name='linkedin_pulse_link',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='article',
            name='medium_link',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='article',
            name='quora_link',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='article',
            name='tumblr_link',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
