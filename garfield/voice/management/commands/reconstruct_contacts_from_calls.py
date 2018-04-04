from django.core.management.base import BaseCommand

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from voice.models import Call

from sms.tasks import lookup_contact


class Command(BaseCommand):
    help = "Reconstructs Contacts from Calls that were unprocessed."

    def handle(self, *args, **options):
        for call in Call.objects.all():
            self.stdout.write("Checking call: {0}".format(call.sid))

            if not call.related_phone_number:
                for number in (call.from_number, call.to_number):
                    result = PhoneNumber.objects.filter(e164=number)

                    if result:
                        self.stdout.write("Related number found: "
                                          "{0}".format(number))
                        call.related_phone_number = \
                            result.latest('date_created')
                        call.save()

            if not call.related_contact:
                for number in (call.from_number, call.to_number):
                    result = Contact.objects.filter(phone_number=number)

                    if result:
                        self.stdout.write("Related contact found: "
                                          "{0}".format(number))
                        call.related_contact = result.latest('date_created')
                        call.save()

                    if not call.related_contact:
                        result = PhoneNumber.objects.filter(e164=number)

                        if not result:
                            self.stdout.write("Creating related contact for "
                                              "{0}".format(number))
                            try:
                                c = Contact(phone_number=number)
                                c.save()

                                c.date_created = call.date_created
                                c.save()

                                lookup_contact.apply_async(args=[c.id])

                                for related in (call.from_number,
                                                call.to_number):
                                    if number is not related:
                                        num = PhoneNumber \
                                            .objects.get(e164=related)
                                        c.related_phone_numbers.add(num)
                                        c.save()
                            except Exception as e:
                                self.stdout.write("Failure creating contact "
                                                  "for {0}: {1}".format(number,
                                                                        e))
