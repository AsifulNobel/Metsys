# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-31 09:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0008_auto_20171031_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classtag',
            name='tagName',
            field=models.CharField(max_length=255),
        ),
    ]
