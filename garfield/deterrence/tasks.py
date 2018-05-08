from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from celery import shared_task

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sms.models import SmsMessage

from sms.tasks import send_sms_message

from .models import Deterrent
from .models import DeterrenceCampaign


@shared_task
def send_deterrence(absolute_uri, message):
    campaign = \
        DeterrenceCampaign.objects.filter(date_sent=None).latest('date_created')

    for contact in campaign.related_contacts.all():
        if contact.do_not_deter or contact.arrested or contact.recruiter:
            continue

        media_url = "{0}/{1}{2}" \
                    "".format(absolute_uri,
                              settings.MEDIA_ROOT,
                              campaign.related_deterrent.image.url)

        if contact.whitepages_first_name:
            kwargs = {"from_": campaign.related_phone_number.e164,
                      "to": contact.phone_number,
                      "body": "{0}, a message from NY"
                              "PD.".format(contact.whitepages_first_name),
                      "media_url": media_url}
        else:
            kwargs = {"from_": campaign.related_phone_number.e164,
                      "to": contact.phone_number,
                      "body": "A message from NYPD.",
                      "media_url": media_url}

        send_sms_message.apply_async(kwargs=kwargs)

        contact.deterred = True
        contact.deterrents_received += 1
        contact.save(update_fields=['deterred',
                                    'deterrents_received'])


@shared_task
def check_campaign_for_contact(contact_id):
    contact = Contact.objects.get(pk=contact_id)

    try:
        campaign = \
            DeterrenceCampaign.objects \
            .filter(date_sent=None) \
            .latest('date_created')
    except DeterrenceCampaign.DoesNotExist:
        deterrent = Deterrent.objects.latest('date_created')
        phone_number = \
            PhoneNumber.objects \
            .filter(number_type='DET') \
            .latest('date_created')

        campaign = DeterrenceCampaign(related_deterrent=deterrent,
                                      related_phone_number=phone_number)
        campaign.save()

    if contact in campaign.related_contacts.all():
        return True
    else:
        campaign.related_contacts.add(contact)
        campaign.save()
        return False


@receiver(post_save, sender=SmsMessage)
def campaign_check(sender, **kwargs):
    instance = kwargs.get('instance')

    if instance.related_contact:
        check_campaign_for_contact \
            .apply_async(args=[instance.related_contact.id])
