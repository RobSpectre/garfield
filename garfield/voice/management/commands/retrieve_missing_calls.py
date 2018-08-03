from datetime import date

from django.core.management.base import BaseCommand
from django.conf import settings

from twilio.rest import Client

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from voice.models import Call


class Command(BaseCommand):
    help = "Retrieve calls that are missing from Garfield's database."

    def handle(self, *args, **kwargs):
        missing = []
        missed_contacts = []

        self.stdout.write("Retrieving all calls set to account.")

        client = Client(settings.TWILIO_ACCOUNT_SID,
                        settings.TWILIO_AUTH_TOKEN)

        for phone_number in PhoneNumber.objects.all():
            if "dev" in phone_number.friendly_name.lower():
                continue

            self.stdout.write("Retrieving calls for {0}"
                              "".format(phone_number.e164))
            calls = client.calls.list(to=phone_number.e164)
            self.stdout.write("{0} calls retrieved."
                              "".format(len(calls)))

            for call in calls:
                if call.date_created.date() < date(2018, 5, 1):
                    continue
                try:
                    Call.objects.get(sid=call.sid)
                except Call.DoesNotExist:
                    self.stdout.write("{0} does not exist. Saving..."
                                      "".format(call.sid))
                    missing.append(call)

                    try:
                        contact = Contact \
                            .objects \
                            .filter(phone_number=call.from_) \
                            .latest('date_created')
                    except Contact.DoesNotExist:
                        self.stdout.write("Contact does not exist for {0}"
                                          "...".format(call.from_))
                        contact = Contact(phone_number=call.from_)
                        try:
                            contact.save()
                            contact.date_created = call.date_created
                            contact.save()
                            missed_contacts.append(contact)
                        except Exception:
                            contact = None

                    record = self.save_call(call)

                    record.related_contact = contact
                    record.related_phone_number = phone_number
                    record.save()

                    self.stdout.write("{0} saved."
                                      "".format(call.sid))
        self.stdout.write("Missing calls: {0}".format(len(missing)))
        self.stdout.write("Missing contacts: {0}".format(len(missed_contacts)))

    def save_call(self, call):
        record = Call(sid=call.sid,
                      from_number=call.from_,
                      to_number=call.to)

        record.save()

        record.date_created = call.date_created
        record.save()

        return record
