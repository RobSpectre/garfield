from django.core.management.base import BaseCommand

from contacts.models import Contact


class Command(BaseCommand):
    help = "Fix quick copy for contacts."

    def handle(self, *args, **kwargs):
        self.stdout.write("Collecting contacts...")

        for contact in Contact.objects.all():
            self.stdout.write("Fixing quick copy: {0}"
                              "".format(contact.phone_number))

            contact.phone_number_quick_copy = \
                contact.phone_number[2:]

            self.stdout.write("Quick copy: {0}"
                              "".format(contact.phone_number_quick_copy))

            contact.save(update_fields=['phone_number_quick_copy'])

        self.stdout.write("Finished!")
