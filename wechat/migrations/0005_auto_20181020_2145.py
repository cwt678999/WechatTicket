# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-10-20 13:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wechat', '0004_activity_used_tickets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='used_tickets',
            field=models.IntegerField(default=0),
        ),
    ]
