from django.core.management.base import BaseCommand

from contacts.models import Contact

from contacts.tasks import lookup_contact_whitepages


class Command(BaseCommand):
    help = "Identify contacts that are not yet identified."

    def handle(self, *args, **kwargs):
        self.stdout.write("Collecting contacts...")

        for contact in Contact.objects.all():
            if not contact.identified:
                self.stdout.write("Identifying contact: {0}"
                                  "".format(contact.phone_number))

                lookup_contact_whitepages.apply_async(args=[contact.id])

        self.stdout.write("Finished!")
