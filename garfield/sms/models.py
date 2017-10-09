from django.db import models

from johns.models import John
from phone_numbers.models import PhoneNumber


class GarfieldSmsModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)


class SmsMessage(GarfieldSmsModel):
    from_number = models.CharField(max_length=255)
    to_number = models.CharField(max_length=255)
    body = models.TextField()
    related_john = models.ForeignKey(John,
                                     null=True,
                                     related_name="sms_messages")
    related_phone_number = models.ForeignKey(PhoneNumber,
                                             null=True,
                                             related_name="phone_number")
