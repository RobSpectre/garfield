from django.db import models

from johns.models import John
from phone_numbers.models import PhoneNumber


class Call(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    sid = models.CharField(max_length=255)
    from_number = models.CharField(max_length=255)
    to_number = models.CharField(max_length=255)
    recording_url = models.URLField(null=True,
                                    blank=True)
    related_john = models.ForeignKey(John,
                                     null=True,
                                     related_name="calls")
    related_phone_number = models.ForeignKey(PhoneNumber,
                                             null=True,
                                             related_name="calls")

    def __str__(self):
        return "{0}: from {1} to {2}".format(self.date_created,
                                             self.from_number,
                                             self.to_number)
