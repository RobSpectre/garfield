from celery import shared_task

from django.conf import settings

from twilio.rest import Client

from phone_numbers.models import PhoneNumber
from contacts.models import Contact
from contacts.tasks import send_whisper
from voice.models import Call

from .models import SmsMessage


@shared_task
def save_sms_message(message):
    record = SmsMessage(sid=message['MessageSid'],
                        from_number=message['From'],
                        to_number=message['To'],
                        body=message['Body'])
    record.save()

    for number in [message['To'], message['From']]:
        if "sim" in number:
            result = \
                SmsMessage.objects.filter(from_number=message['To']) \
                .filter(related_phone_number__number_type="ADV") \
                .latest('date_created')
            if result:
                record.related_phone_number = result.related_phone_number
                record.save()
            continue

        result = PhoneNumber.objects.filter(e164=number)

        if result:
            record.related_phone_number = result.latest('date_created')
            record.save()
            continue

    for number in [message['To'], message['From']]:
        result = Contact.objects.filter(phone_number=number)

        if result:
            contact = result.latest('date_created')
            record.related_contact = contact
            record.save()

    if not record.related_contact:
        check_contact.apply_async(args=[message])


@shared_task
def send_sms_message(from_=None,
                     to=None,
                     body=None,
                     media_url=None,
                     status_callback=None):
    client = Client(settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(to,
                                     from_=from_,
                                     body=body,
                                     media_url=media_url,
                                     status_callback=status_callback)

    return {'MessageSid': message.sid,
            'To': message.to,
            'From': message.from_,
            'Body': message.body,
            'DateSent': message.date_sent,
            'Status': message.status,
            'ApiVersion': message.api_version,
            'Price': message.price,
            'PriceUnit': message.price_unit,
            'Uri': message.uri,
            'ErrorCode': message.error_code,
            'ErrorMessage': message.error_message,
            'Direction': message.direction}


@shared_task
def check_contact(message):
    phone_number = PhoneNumber.objects.get(e164=message['To'])

    try:
        contact = \
            Contact.objects.get(phone_number=message['From'])
    except Contact.DoesNotExist:
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

    check_for_first_contact_to_ad.apply_async(args=[contact.id,
                                                    phone_number.id])


@shared_task
def check_for_first_contact_to_ad(contact_id, phone_number_id):
    contact = Contact.objects.get(pk=contact_id)
    phone_number = PhoneNumber.objects.get(pk=phone_number_id)

    sms_messages = (SmsMessage.objects
                    .filter(related_contact=contact))

    calls = (Call.objects
             .filter(related_contact=contact))

    contact_to_number = (len(sms_messages
                             .filter(related_phone_number=phone_number_id)) +
                         len(calls
                             .filter(related_phone_number=phone_number_id)))

    if contact_to_number < 2:
        kwargs = {'from_': contact.phone_number,
                  'to': phone_number.e164,
                  'body': "[First contact to {0}]"
                          "".format(phone_number.friendly_name)}

        send_whisper.apply_async(kwargs=kwargs)

    contact.sms_message_count = len(sms_messages)
    contact.call_count = len(calls)
    contact.contact_count = len(sms_messages) + len(calls)
    contact.save(update_fields=['sms_message_count',
                                'call_count',
                                'contact_count'])
