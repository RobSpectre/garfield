from django.db import models

from contacts.models import Contact
from phone_numbers.models import PhoneNumber


class Call(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    sid = models.CharField(max_length=255, db_index=True)
    from_number = models.CharField(max_length=255, db_index=True)
    to_number = models.CharField(max_length=255, db_index=True)
    recording_url = models.URLField(null=True,
                                    blank=True)
    duration = models.IntegerField(null=True, blank=True)
    related_contact = models.ForeignKey(Contact,
                                        null=True,
                                        related_name="calls")
    related_phone_number = models.ForeignKey(PhoneNumber,
                                             null=True,
                                             related_name="calls")

    def __str__(self):
        return "{0}: from {1} to {2}".format(self.date_created,
                                             self.from_number,
                                             self.to_number)
