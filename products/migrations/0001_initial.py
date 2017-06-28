# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-06-28 14:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('count', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(help_text='Unique value for product page URL, created from name.', unique=True)),
                ('company', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=400)),
                ('price', models.PositiveIntegerField(default=0)),
                ('added_date', models.DateTimeField(auto_now_add=True)),
                ('available_quantity', models.PositiveIntegerField(default=0)),
                ('image', models.ImageField(upload_to='/home/nobel/DevBox/Senior_Design_Project/websites/bazar/products/static/product_images')),
            ],
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.ProductSize'),
        ),
    ]
