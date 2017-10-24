# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email', '0031_auto_20170801_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailaccount',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
