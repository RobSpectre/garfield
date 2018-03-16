from celery import shared_task

from django.conf import settings

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

import phonenumbers

from phone_numbers.models import PhoneNumber

from sims.models import Sim
from sms.tasks import send_sms_message


@shared_task
def buy_new_phone_number(base_uri, message, number_type):
    client = Client(settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN)

    try:
        available = client.available_phone_numbers("US") \
            .local.list(in_locality="New York")

        parsed = phonenumbers.parse(available[0].phone_number, None)
        formatted = \
            phonenumbers.format_number(parsed,
                                       phonenumbers.PhoneNumberFormat.NATIONAL)

        new_number = client.incoming_phone_numbers \
            .local.create(phone_number=available[0].phone_number,
                          friendly_name="Garfield {0} Number - {1}"
                                        "".format(number_type,
                                                  formatted),
                          voice_application_sid=settings.TWILIO_APP_SID,
                          sms_application_sid=settings.TWILIO_APP_SID)
    except TwilioRestException as e:
        kwargs = {"from_": settings.TWILIO_PHONE_NUMBER,
                  "to": settings.TWILIO_PHONE_NUMBER,
                  "body": "There was an error purchasing "
                          "your phone number: {0}".format(e.msg)}
        send_sms_message.apply_async(kwargs=kwargs)

        return False

    sim = Sim.objects.get(sid=message['From'].replace("sim:", ""))

    phone_number = PhoneNumber(sid=new_number.sid,
                               account_sid=settings.TWILIO_ACCOUNT_SID,
                               service_sid="None",
                               url=new_number.uri,
                               e164=new_number.phone_number,
                               formatted=formatted,
                               country_code="1",
                               number_type=number_type,
                               related_sim=sim)
    phone_number.save()

    send_sms_message.apply_async(kwargs={"from_": phone_number.e164,
                                         "to": settings.TWILIO_PHONE_NUMBER,
                                         "body": "This is your new {0}"
                                                 " phone number."
                                                 "".format(number_type)})

    return True
