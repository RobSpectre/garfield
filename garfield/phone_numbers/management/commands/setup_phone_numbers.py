from django.core.management.base import BaseCommand
from django.conf import settings

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

import phonenumbers

from phone_numbers.models import PhoneNumber


class Command(BaseCommand):
    help = "Setup phone numbers for a new instance."

    client = Client(settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN)

    def add_arguments(self, parser):
        parser.add_argument("total_numbers", type=int)
        parser.add_argument("locality", type=str)

    def handle(self, *args, **options):
        self.stdout.write("Provisioning {0} numbers..."
                          "".format(options['total_numbers'] * 2))

        for i in range(options['total_numbers']):
            number = self.buy_phone_number(options['locality'],
                                           PhoneNumber.DETERRENCE)
            self.stdout.write("{0} acquired!".format(number.friendly_name))

        for i in range(options['total_numbers']):
            number = self.buy_phone_number(options['locality'],
                                           PhoneNumber.AD)
            self.stdout.write("{0} acquired!".format(number.friendly_name))

    def buy_phone_number(self, locality, number_type):
        try:
            available = self.client.available_phone_numbers("US") \
                .local.list(in_locality=locality)

            parsed = phonenumbers.parse(available[0].phone_number, None)
            formatted = \
                phonenumbers.format_number(parsed,
                                           phonenumbers.PhoneNumberFormat
                                           .NATIONAL)

            new_number = self.client.incoming_phone_numbers \
                .local.create(phone_number=available[0].phone_number,
                              friendly_name="Garfield {0} Number - {1}"
                                            "".format(number_type,
                                                      formatted),
                              voice_application_sid=settings.TWILIO_APP_SID,
                              sms_application_sid=settings.TWILIO_APP_SID)
        except TwilioRestException as e:
            self.stdout.write("There was an error purchasing "
                              "your phone number: {0}".format(e.msg))

        phone_number = PhoneNumber(sid=new_number.sid,
                                   account_sid=settings.TWILIO_ACCOUNT_SID,
                                   service_sid="None",
                                   url=new_number.uri,
                                   e164=new_number.phone_number,
                                   friendly_name="{0} - {1}"
                                                 "".format(number_type,
                                                           formatted),
                                   formatted=formatted,
                                   country_code="1",
                                   number_type=PhoneNumber.AD)
        phone_number.save()

        return phone_number
