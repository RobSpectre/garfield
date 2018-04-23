from django.core.management.base import BaseCommand

from contacts.models import Contact
from sms.models import SmsMessage
from voice.models import Call


class Command(BaseCommand):
    help = "Adds all the SMS Messages and Calls received by a Contact"

    def handle(self, *args, **kwargs):
        for contact in Contact.objects.filter(contact_count__lt=1):
            self.stdout.write("Calculating contact: {0}".format(contact))
            sms_messages = (SmsMessage.objects
                            .filter(related_contact=contact))

            calls = (Call.objects
                     .filter(related_contact=contact))

            contact.sms_message_count = len(sms_messages)
            contact.call_count = len(calls)
            contact.contact_count = len(sms_messages) + len(calls)
            contact.save(update_fields=['sms_message_count',
                                        'call_count',
                                        'contact_count'])
            self.stdout.write("Updated contact {0} with {1}."
                              "".format(contact,
                                        contact.contact_count))
