from django.db import models

from sims.models import Sim


class PhoneNumber(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    sid = models.CharField(max_length=255)
    account_sid = models.CharField(max_length=255)
    service_sid = models.CharField(max_length=255)
    url = models.URLField()
    e164 = models.CharField(max_length=255)
    formatted = models.CharField(max_length=255)
    friendly_name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=255)

    related_sim = models.ForeignKey(Sim,
                                    null=True,
                                    related_name="phone_numbers")
