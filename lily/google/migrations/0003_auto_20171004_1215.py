# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-04 12:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('google', '0002_auto_20161025_1426'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flowmodel',
            name='id',
        ),
        migrations.DeleteModel(
            name='FlowModel',
        ),
    ]
