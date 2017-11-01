# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-01 20:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('whitepages_first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_middle_name', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_gender', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_entity_type', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_business_name', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_address', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_address_two', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_city', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_state', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_country', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_zip_code', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_address_type', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_latitude', models.FloatField(null=True)),
                ('whitepages_longitude', models.FloatField(null=True)),
                ('whitepages_accuracy', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_prepaid', models.NullBooleanField(default=False)),
                ('whitepages_phone_type', models.CharField(blank=True, max_length=255, null=True)),
                ('whitepages_commercial', models.NullBooleanField(default=False)),
                ('phone_number', models.CharField(max_length=255)),
                ('carrier', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number_type', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number_friendly', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_middle_name', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_gender', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_age', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_marital_status', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_children_presence', models.NullBooleanField(default=False)),
                ('nextcaller_high_net_worth', models.NullBooleanField(default=False)),
                ('nextcaller_home_owner_status', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_household_income', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_length_of_residence', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_market_value', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_education', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_occupation', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_address', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_address_two', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_city', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_state', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_country', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_zip_code', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_prepaid', models.NullBooleanField(default=False)),
                ('nextcaller_carrier', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_phone_type', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_identity_type', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_business_name', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('nextcaller_twitter', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_facebook', models.CharField(blank=True, max_length=255, null=True)),
                ('nextcaller_linkedin', models.CharField(blank=True, max_length=255, null=True)),
                ('ter_username', models.CharField(blank=True, max_length=255, null=True)),
                ('photo', models.ImageField(blank=True, upload_to='contact_photos/')),
                ('identified', models.BooleanField(default=False)),
                ('registed_offender', models.BooleanField(default=False)),
                ('arrested', models.BooleanField(default=False)),
                ('deterred', models.BooleanField(default=False)),
                ('do_not_deter', models.BooleanField(default=False)),
                ('deterrents_received', models.IntegerField(default=0)),
            ],
        ),
    ]
