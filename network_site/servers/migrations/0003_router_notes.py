# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-03 17:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0002_router'),
    ]

    operations = [
        migrations.AddField(
            model_name='router',
            name='notes',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
