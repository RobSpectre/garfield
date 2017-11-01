from celery import shared_task

from contacts.models import Contact
from phone_numbers.models import PhoneNumber

from .models import Call


@shared_task
def save_call(message):
    record = Call(sid=message['CallSid'],
                  from_number=message['From'],
                  to_number=message['To'])
    record.save()

    if PhoneNumber.objects.filter(e164=message['To']):
        phone_number = PhoneNumber.objects.get(e164=message['To'])
        record.related_phone_number = phone_number
        record.save()
    elif PhoneNumber.objects.filter(e164=message['From']):
        phone_number = PhoneNumber.objects.get(e164=message['From'])
        record.related_phone_number = phone_number
        record.save()

    if Contacts.objects.filter(phone_number=message['To']):
        contact = contacts.objects.get(phone_number=message['To'])
        record.related_contact = contact
        record.save()
    elif Contact.objects.filter(phone_number=message['From']):
        contact = Contact.objects.get(phone_number=message['From'])
        record.related_contact = contact
        record.save()


@shared_task
def save_voice_recording(message):
    record = Call.objects.get(sid=message['CallSid'])

    record.recording_url = message['RecordingUrl']
    record.duration = message['RecordingDuration']

    record.save()
