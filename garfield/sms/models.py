from django.db import models

from contacts.models import Contact
from phone_numbers.models import PhoneNumber


class SmsMessage(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    sid = models.CharField(max_length=255)
    from_number = models.CharField(max_length=255)
    to_number = models.CharField(max_length=255)
    body = models.TextField()
    related_contact = models.ForeignKey(Contact,
                                        null=True,
                                        related_name="sms_messages")
    related_phone_number = models.ForeignKey(PhoneNumber,
                                             null=True,
                                             related_name="sms_messages")

    def __str__(self):
        return "{0}: from {1} to {2}".format(self.date_created,
                                             self.from_number,
                                             self.to_number)
