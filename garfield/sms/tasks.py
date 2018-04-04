from celery import shared_task

from django.conf import settings

from twilio.rest import Client

from phone_numbers.models import PhoneNumber
from contacts.models import Contact
from voice.models import Call

from .models import SmsMessage


@shared_task
def save_sms_message(message):
    record = SmsMessage(sid=message['MessageSid'],
                        from_number=message['From'],
                        to_number=message['To'],
                        body=message['Body'])
    record.save()

    if "sim" in message['From']:
        result = \
            SmsMessage.objects.filter(from_number=message['To']) \
            .latest('date_created')
        if result:
            record.related_phone_number = result.related_phone_number
            record.save()
    else:
        phone_number = \
            PhoneNumber.objects.filter(e164=message['To']) \
            .latest('date_created')
        if phone_number:
            record.related_phone_number = phone_number
            record.save()

        check_contact.apply_async(args=[message])

    if Contact.objects.filter(phone_number=message['To']):
        contact = Contact.objects.get(phone_number=message['To'])
        record.related_contact = contact
        record.save()

    if Contact.objects.filter(phone_number=message['From']):
        contact = Contact.objects.get(phone_number=message['From'])
        record.related_contact = contact
        record.save()


@shared_task
def send_sms_message(from_=None, to=None, body=None, media_url=None):
    client = Client(settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN)

    client.messages.create(to,
                           from_=from_,
                           body=body,
                           media_url=media_url)

    return "SMS Message from {0} to {1}: {2}".format(from_,
                                                     to,
                                                     body)


@shared_task
def check_contact(message):
    phone_number = PhoneNumber.objects.get(e164=message['To'])

    result = \
        Contact.objects.filter(phone_number=message['From'])

    if not result:
        contact = Contact(phone_number=message['From'])
        contact.save()
        contact.related_phone_numbers.add(phone_number)

        if message.get("MessageSid", None):
            sms_message = SmsMessage.objects.get(sid=message['MessageSid'])
            sms_message.related_contact = contact
            sms_message.save()

        if message.get("CallSid", None):
            call = Call.objects.get(sid=message['CallSid'])
            call.related_contact = contact
            call.save()


@shared_task
def send_deterrence(absolute_uri, message):
    for contact in Contact.objects.all():
        if contact.do_not_deter or contact.deterred or contact.arrested:
            continue

        if contact.whitepages_first_name:
            kwargs = {"from_": settings.TWILIO_PHONE_NUMBER,
                      "to": contact.phone_number,
                      "body": "{0}, a message from NY"
                              "PD.".format(contact.whitepages_first_name),
                      "media_url": "https://berserk-sleet-3229.twil.io/"
                                   "assets/john_deterrent.jpg"}
        else:
            kwargs = {"from_": settings.TWILIO_PHONE_NUMBER,
                      "to": contact.phone_number,
                      "body": "A message from NYPD.",
                      "media_url": "https://berserk-sleet-3229.twil.io/"
                                   "assets/john_deterrent.jpg"}

        send_sms_message.apply_async(kwargs=kwargs)

        contact.deterred = True
        contact.save(update_fields=['deterred'])
