# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-28 15:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20170628_1551'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='name',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='productsize',
            old_name='name',
            new_name='size',
        ),
    ]
