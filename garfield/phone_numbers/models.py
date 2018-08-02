from django.db import models

from sims.models import Sim
from bots.models import Bot


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
    burned = models.BooleanField(default=False)

    AD = 'ADV'
    DETERRENCE = 'DET'
    DEVELOPMENT = 'DEV'
    STAGE = 'STG'
    TEST = 'TST'
    DEMO = 'DEM'
    OPERATOR = 'OPR'

    NUMBER_TYPE_CHOICES = ((AD, 'Advertisement'),
                           (DETERRENCE, 'Deterrence'),
                           (DEMO, 'Demo'),
                           (DEVELOPMENT, 'Development'),
                           (STAGE, 'Stage'),
                           (TEST, 'Test'),
                           (OPERATOR, 'Operator'))
    number_type = models.CharField(choices=NUMBER_TYPE_CHOICES,
                                   max_length=3)

    related_sim = models.ForeignKey(Sim,
                                    null=True,
                                    blank=True,
                                    related_name="phone_numbers",
                                    on_delete=models.CASCADE)

    related_bot = models.ForeignKey(Bot,
                                    null=True,
                                    blank=True,
                                    related_name="phone_numbers",
                                    on_delete=models.CASCADE)

    def __str__(self):
        if self.related_sim:
            return "{0} -> {1}".format(self.friendly_name,
                                       self.related_sim)
        elif self.related_bot:
            return "{0} -> {1}".format(self.friendly_name,
                                       self.related_bot)
        else:
            return "{0}".format(self.friendly_name)
