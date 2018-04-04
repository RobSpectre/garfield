from celery import shared_task

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sms.tasks import check_contact

from .models import Call


@shared_task
def save_call(message):
    record = Call(sid=message['CallSid'],
                  from_number=message['From'],
                  to_number=message['To'])
    record.save()

    if "sim" in message['From']:
        result = \
            Call.objects.filter(from_number=message['To']) \
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
def save_voice_recording(message):
    record = Call.objects.get(sid=message['CallSid'])

    record.recording_url = message['RecordingUrl']
    record.duration = message['RecordingDuration']

    record.save()
