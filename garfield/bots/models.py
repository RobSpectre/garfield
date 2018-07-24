from django.db import models


class Bot(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    alias = models.CharField(max_length=255, null=True, blank=True)
    neighborhood = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    rates = models.CharField(max_length=255, null=True, blank=True)

    model = models.CharField(max_length=255, null=True, blank=True)
    answers = models.CharField(max_length=255, null=True, blank=True)
    threshold = models.FloatField(default=0.7)

    human_delay_min = models.IntegerField(default=30)
    human_delay_max = models.IntegerField(default=120)

    debug = models.BooleanField(default=False)

    def __str__(self):
        return "{0} - {1}: {2}, {3}".format(self.alias,
                                            self.model,
                                            self.neighborhood,
                                            self.location)
