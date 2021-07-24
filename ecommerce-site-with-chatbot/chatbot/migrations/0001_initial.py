# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-30 20:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BanglaRequests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request', models.CharField(max_length=500, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='BanglaResponses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(max_length=2000, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClassTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tagName', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Complaints',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request', models.CharField(max_length=500)),
                ('response', models.CharField(max_length=2000)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContextTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tagName', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='EnglishRequests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request', models.CharField(max_length=500, unique=True)),
                ('tag', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.ClassTag')),
            ],
        ),
        migrations.CreateModel(
            name='EnglishResponses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(max_length=2000, unique=True)),
                ('tag', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.ClassTag')),
            ],
        ),
        migrations.CreateModel(
            name='Feedbacks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('comment', models.CharField(max_length=3000)),
            ],
        ),
        migrations.AddField(
            model_name='banglaresponses',
            name='tag',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.ClassTag'),
        ),
        migrations.AddField(
            model_name='banglarequests',
            name='tag',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chatbot.ClassTag'),
        ),
    ]