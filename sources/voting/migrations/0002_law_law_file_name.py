# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-06 11:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='law',
            name='law_file_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
