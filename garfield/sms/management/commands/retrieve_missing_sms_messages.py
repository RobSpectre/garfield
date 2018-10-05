from datetime import date

from django.core.management.base import BaseCommand
from django.conf import settings

from twilio.rest import Client

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sms.models import SmsMessage 


class Command(BaseCommand):
    help = "Retrieve sms_messages that are missing from Garfield's database."

    def handle(self, *args, **kwargs):
        missing = []
        missed_contacts = []

        self.stdout.write("Retrieving all sms_messages set to account.")

        client = Client(settings.TWILIO_ACCOUNT_SID,
                        settings.TWILIO_AUTH_TOKEN)

        for phone_number in PhoneNumber.objects.all():
            if "dev" in phone_number.friendly_name.lower():
                continue

            self.stdout.write("Retrieving sms_messages for {0}"
                              "".format(phone_number.e164))
            sms_messages = client.messages.list(to=phone_number.e164)
            self.stdout.write("{0} sms_messages retrieved."
                              "".format(len(sms_messages)))

            for sms_message in sms_messages:
                if sms_message.date_created.date() < date(2018, 5, 1):
                    continue
                try:
                    SmsMessage.objects.get(sid=sms_message.sid)
                except SmsMessage.DoesNotExist:
                    self.stdout.write("{0} does not exist. Saving..."
                                      "".format(sms_message.sid))
                    missing.append(sms_message)

                    try:
                        contact = Contact \
                            .objects \
                            .filter(phone_number=sms_message.from_) \
                            .latest('date_created')
                    except Contact.DoesNotExist:
                        self.stdout.write("Contact does not exist for {0}"
                                          "...".format(sms_message.from_))
                        contact = Contact(phone_number=sms_message.from_)
                        try:
                            contact.save()
                            contact.date_created = sms_message.date_created
                            contact.save()
                            missed_contacts.append(contact)
                        except Exception:
                            contact = None

                    record = self.save_sms_message(sms_message)

                    record.related_contact = contact
                    record.related_phone_number = phone_number
                    record.save()

                    self.stdout.write("{0} saved."
                                      "".format(sms_message.sid))
        self.stdout.write("Missing sms_messages: {0}".format(len(missing)))
        self.stdout.write("Missing contacts: {0}".format(len(missed_contacts)))

    def save_sms_message(self, sms_message):
        record = SmsMessage(sid=sms_message.sid,
                            from_number=sms_message.from_,
                            to_number=sms_message.to,
                            body=sms_message.body)

        record.save()

        record.date_created = sms_message.date_created
        record.save()

        return record
