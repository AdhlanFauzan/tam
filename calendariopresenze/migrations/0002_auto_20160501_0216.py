# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-01 00:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendariopresenze', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendar',
            name='type',
            field=models.IntegerField(choices=[(1, b'Ferie'), (2, b'Riposo')]),
        ),
    ]
