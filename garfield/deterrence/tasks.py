from random import uniform

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from celery import shared_task

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sms.models import SmsMessage
from voice.models import Call

from sms.tasks import send_sms_message

from .models import Deterrent
from .models import DeterrenceCampaign
from .models import DeterrenceMessage

from .util import lowercase_sentence


@shared_task
def send_deterrence_campaign(absolute_uri):
    campaign = \
        DeterrenceCampaign.objects \
        .filter(date_sent=None).latest('date_created')

    for contact in campaign.related_contacts.all():
        if contact.do_not_deter or contact.arrested or contact.recruiter:
            continue

        countdown = 0
        for i in range(0, settings.GARFIELD_NUMBER_OF_DETERRENTS):

            send_deterrence.apply_async(args=[absolute_uri,
                                              campaign.id,
                                              contact.id],
                                        countdown=countdown)
            countdown += \
                (settings.GARFIELD_DETERRENT_INTERVAL +
                 settings.GARFIELD_DETERRENT_INTERVAL * uniform(0, 0.3))

    campaign.date_sent = timezone.now()
    campaign.save()


@shared_task
def send_deterrence(absolute_uri,
                    campaign_id,
                    contact_id):
    campaign = DeterrenceCampaign.objects.get(pk=campaign_id)
    contact = Contact.objects.get(pk=contact_id)

    media_url = "{0}/{1}{2}" \
                "".format(absolute_uri,
                          settings.MEDIA_ROOT,
                          campaign.related_deterrent.image.url)

    if campaign.related_deterrent.personalize:
        if contact.whitepages_first_name:
            body = lowercase_sentence(campaign.related_deterrent.body)
            body = \
                "{0}, {1}" \
                "".format(contact.whitepages_first_name,
                          body)
        else:
            body = campaign.related_deterrent.body

    else:
        body = campaign.related_deterrent.body

    status_callback = "{0}{1}".format(absolute_uri,
                                      reverse('deterrence:deterrence'
                                              '_message_status_callback'))

    number = get_unused_deterrence_phone_number(contact)

    message = \
        send_sms_message(from_=number.e164,
                         to=contact.phone_number,
                         body=body,
                         media_url=media_url,
                         status_callback=status_callback)

    contact.deterred = True
    contact.deterrents_received += 1
    contact.save(update_fields=['deterred',
                                'deterrents_received'])

    deterrence_message = \
        DeterrenceMessage(sid=message['MessageSid'],
                          body=message['Body'],
                          status=message['Status'],
                          related_deterrent=campaign.related_deterrent,
                          related_contact=contact,
                          related_phone_number=number,
                          related_campaign=campaign)

    deterrence_message.save()


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

        campaign = DeterrenceCampaign(related_deterrent=deterrent)
        campaign.save()

    if contact in campaign.related_contacts.all():
        return True
    else:
        campaign.related_contacts.add(contact)
        campaign.save()
    return False


def get_unused_deterrence_phone_number(contact):
    messages = DeterrenceMessage.objects.filter(related_contact=contact)

    used_numbers = [msg.related_phone_number.e164 for msg in messages]

    try:
        number = PhoneNumber.objects \
            .filter(number_type="DET") \
            .filter(burned=False) \
            .exclude(e164__in=used_numbers) \
            .latest('date_created')
    except PhoneNumber.DoesNotExist:
        number = PhoneNumber.objects \
            .filter(number_type="DET") \
            .filter(burned=False) \
            .latest('date_created')

    return number


@shared_task
def handle_deterrence_message_status_callback(sid, status):
    message = DeterrenceMessage.objects.get(sid=sid)
    message.status = status
    message.save(update_fields=['status'])

    return True


@receiver(post_save, sender=SmsMessage)
def check_campaign_for_sms_message_contact(sender, **kwargs):
    instance = kwargs.get('instance')

    if instance.related_contact and instance.related_phone_number:
        if instance.related_phone_number.number_type == "ADV":
            check_campaign_for_contact \
                .apply_async(args=[instance.related_contact.id])


@receiver(post_save, sender=Call)
def check_campaign_for_call_contact(sender, **kwargs):
    instance = kwargs.get('instance')

    if instance.related_contact and instance.related_phone_number:
        if instance.related_phone_number.number_type == "ADV":
            check_campaign_for_contact \
                .apply_async(args=[instance.related_contact.id])


@receiver(post_save, sender=Contact)
def check_campaign_for_new_contact(sender, **kwargs):
    instance = kwargs.get('instance')

    if kwargs.get('created', False):
        check_campaign_for_contact \
            .apply_async(args=[instance.id])
