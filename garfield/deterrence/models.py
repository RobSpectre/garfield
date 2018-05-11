from django.db import models

from contacts.models import Contact
from phone_numbers.models import PhoneNumber


class Deterrent(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    image = models.ImageField(upload_to="static/deterrents/")
    body = models.CharField(max_length=255, null=True, blank=True)
    friendly_name = models.CharField(max_length=255, null=True,
                                     blank=True)
    personalize = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def __str__(self):
        return "Deterrent ({2}): {0} - {1}".format(self.date_created,
                                                   self.body,
                                                   self.friendly_name)


class DeterrenceCampaign(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    date_sent = models.DateTimeField(null=True, blank=True)

    related_deterrent = models.ForeignKey(Deterrent,
                                          null=True,
                                          related_name="campaigns",
                                          on_delete=models.SET_NULL)

    related_contacts = models.ManyToManyField(Contact,
                                              blank=True)

    def __str__(self):
        if self.date_sent:
            return "Deterrence Campaign: Sent {0} to {1} contacts" \
                "".format(self.date_sent,
                          self.related_contacts.all().count())
        else:
            return "Pending Deterrence Campaign with {0} contacts" \
                   "".format(self.related_contacts.all().count())


class DeterrenceMessage(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    sid = models.CharField(max_length=255)
    body = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

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
        return "Deterrence message {0} {1} to {2}" \
            "".format(self.status,
                      self.date_created,
                      self.related_contact)
