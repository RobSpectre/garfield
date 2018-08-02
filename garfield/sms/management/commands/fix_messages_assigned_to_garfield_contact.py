from django.core.management.base import BaseCommand

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sms.models import SmsMessage
from voice.models import Call


class Command(BaseCommand):
    help = "Adds all the SMS Messages and Calls received by a Contact"

    def handle(self, *args, **kwargs):
        self.stdout.write("Gathering Garfield numbers...")

        phone_numbers = [p.e164 for p in PhoneNumber.objects.all()]

        self.stdout.write("Checking contacts for {0} phone numbers..."
                          "".format(len(phone_numbers)))

        error_contacts = Contact \
            .objects.filter(phone_number__in=phone_numbers)

        self.stdout.write("Found {0} contacts that are Garfield "
                          "numbers...".format(len(error_contacts)))

        messages = SmsMessage \
            .objects.filter(related_contact__in=error_contacts)

        self.stdout.write("Found {0} messages erroneously "
                          "related to Garfield contacts..."
                          "".format(len(messages)))

        for message in messages:
            self.stdout.write("Fixing {0}...".format(message.sid))

            for number in [message.to_number,
                           message.from_number]:
                if number in phone_numbers or number.startswith('sim:'):
                    continue
                else:
                    try:
                        result = Contact.objects.get(phone_number=number)
                        self.stdout.write("Contact exists...")
                    except Contact.DoesNotExist:
                        self.stdout.write("Contact does not exist...")
                        result = Contact(phone_number=number)
                        result.save()

                        result.date_created = message.date_created
                        result.save()
                    except Contact.MultipleObjectsReturned:
                        result = Contact \
                            .objects \
                            .filter(phone_number=number) \
                            .latest('date_created')

                    self.stdout.write("Relating {0} to {1}..."
                                      "".format(result,
                                                message.sid))
                    message.related_contact = result
                    message.save()

        calls = Call \
            .objects.filter(related_contact__in=error_contacts)

        self.stdout.write("Found {0} calls erroneously "
                          "related to Garfield contacts..."
                          "".format(len(messages)))

        for call in calls:
            self.stdout.write("Fixing {0}...".format(message.sid))

            for number in [call.to_number,
                           call.from_number]:
                if number in phone_numbers or number.startswith('sim:'):
                    continue
                else:
                    try:
                        result = Contact.objects.get(phone_number=number)
                        self.stdout.write("Contact exists...")
                    except Contact.DoesNotExist:
                        self.stdout.write("Contact does not exist...")
                        result = Contact(phone_number=number)
                        result.save()
                    except Contact.MultipleObjectsReturned:
                        result = Contact \
                            .objects \
                            .filter(phone_number=number) \
                            .latest('date_created')

                    self.stdout.write("Relating {0} to {1}..."
                                      "".format(result,
                                                call.sid))
                    call.related_contact = result
                    call.save()
