# Generated by Django 2.2.2 on 2019-06-25 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phone_numbers', '0006_auto_20180723_2014'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonenumber',
            name='website',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='website_uri',
            field=models.URLField(blank=True, null=True),
        ),
    ]
