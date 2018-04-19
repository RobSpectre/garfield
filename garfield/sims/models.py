from django.db import models


class Sim(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    friendly_name = models.CharField(max_length=255)
    sid = models.CharField(max_length=255)
    iccid = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    rate_plan = models.CharField(max_length=255)

    receives_whispers = models.BooleanField(default=False)

    def __str__(self):
        return "{0}: {1}".format(self.sid,
                                 self.friendly_name)


class Whisper(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    body = models.TextField()
    sent = models.BooleanField(default=False)
    related_phone_number = models.ForeignKey('phone_numbers.PhoneNumber',
                                             null=True,
                                             related_name="whispers",
                                             on_delete=models.CASCADE)
    related_contact = models.ForeignKey('contacts.Contact',
                                        null=True,
                                        related_name="whispers",
                                        on_delete=models.CASCADE)

    def __str__(self):
        return "Whisper for {0}: " \
               "{1}".format(self.related_phone_number.e164,
                            self.date_created)
