# Generated by Django 2.0.4 on 2018-04-23 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20180413_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='call_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='contact',
            name='contact_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='contact',
            name='sms_message_count',
            field=models.IntegerField(default=0),
        ),
    ]
