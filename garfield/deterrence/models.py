from django.db import models
from django.conf import settings

from contacts.models import Contact
from phone_numbers.models import PhoneNumber


class Deterrent(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    image = models.ImageField(upload_to="{0}deterrents"
                                        "".format(settings.STATIC_ROOT))
    body = models.CharField(max_length=255, null=True, blank=True)
    friendly_name = models.CharField(max_length=255, null=True,
                                     blank=True)
    personalize = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def __str__(self):
        return "Deterrent: {0} - {1}".format(self.date_created,
                                             self.body)


class DeterrenceCampaign(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    date_sent = models.DateTimeField(null=True, blank=True)

    related_deterrent = models.ForeignKey(Deterrent,
                                          null=True,
                                          related_name="campaigns",
                                          on_delete=models.SET_NULL)

    related_phone_number = models.ForeignKey(PhoneNumber,
                                             null=True,
                                             related_name="campaigns",
                                             on_delete=models.SET_NULL)

    related_contacts = models.ManyToManyField(Contact,
                                              blank=True)

    def __str__(self):
        return "Deterrence Campaign: {0} sent to {1} contacts" \
            "".format(self.date_sent,
                      self.related_contacts.all().count())


class DeterrenceMessage(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    body = models.CharField(max_length=255)

    related_deterrent = models.ForeignKey(Deterrent,
                                          null=True,
                                          related_name="deterrence_messages",
                                          on_delete=models.SET_NULL)

    related_phone_number = models.ForeignKey(PhoneNumber,
                                             null=True,
                                             related_name="deterrence_"
                                                          "messages",
                                             on_delete=models.SET_NULL)

    related_campaign = models.ForeignKey(DeterrenceCampaign,
                                         null=True,
                                         related_name="deterrence_messages",
                                         on_delete=models.SET_NULL)

    related_contact = models.ForeignKey(Contact,
                                        null=True,
                                        related_name="deterrence_messages",
                                        on_delete=models.SET_NULL)

    def __str__(self):
        return "Deterrence message sent {1} to {0}" \
            "".format(self.related_contact.phone_number_friendly,
                      self.date_created)
