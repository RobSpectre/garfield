from datetime import date

from django.conf import settings

from celery import shared_task

from contacts.models import Contact
from sms.models import SmsMessage
from voice.models import Call
from deterrence.models import DeterrenceMessage

from sms.tasks import send_sms_message


@shared_task
def send_daily_statistics(recipient):
    stats = gather_daily_statistics()

    body = "Today's stats from {0}:\n".format(settings.GARFIELD_JURISDICTION)

    for key, value in stats.items():
        body += "\n{0}: {1}".format(key, value)

    return send_sms_message(from_=settings.TWILIO_PHONE_NUMBER,
                            to=recipient,
                            body=body)


def gather_daily_statistics():
    contacts = Contact.objects.filter(date_created__date=date.today())
    messages = \
        SmsMessage.objects.filter(date_created__date=date.today()) \
        .filter(related_phone_number__number_type='ADV')
    calls = Call.objects.filter(date_created__date=date.today()) \
        .filter(related_phone_number__number_type='ADV')
    deterrents = \
        DeterrenceMessage.objects \
        .filter(date_created__date=date.today())

    return {'Contacts': len(contacts),
            'SMS Messages': len(messages),
            'Calls': len(calls),
            'Deterrents': len(deterrents)}
