# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-20 14:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tam', '0004_auto_20160831_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='viaggio',
            name='additional_stop',
            field=models.IntegerField(default=0, verbose_name='Sosta addizionale (minuti)'),
        ),
    ]
