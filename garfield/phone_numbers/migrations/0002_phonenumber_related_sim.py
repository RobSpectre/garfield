# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-01 20:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('phone_numbers', '0001_initial'),
        ('sims', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonenumber',
            name='related_sim',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='phone_numbers', to='sims.Sim'),
        ),
    ]
