import csv
from datetime import datetime

import phonenumbers

from django.core.management.base import BaseCommand

from contacts.models import Contact


class Command(BaseCommand):
    help = "Add contacts manually from a spreadsheet."

    def add_arguments(self, parser):
        parser.add_argument("csv_file_path", type=str)

    def handle(self, *args, **kwargs):
        self.stdout.write("Opening CSV file: {0}..."
                          "".format(kwargs['csv_file_path']))

        with open(kwargs['csv_file_path'], 'r') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                self.stdout.write("Checking contact: {0}"
                                  "".format(row['phone']))

                number = phonenumbers.parse(row['phone'],
                                            'US')
                e164 = phonenumbers.format_number(number,
                                                  phonenumbers
                                                  .PhoneNumberFormat
                                                  .E164)

                check = Contact.objects.filter(phone_number=e164)

                if len(check) > 0:
                    self.stdout.write("Contact exists, skipping.")
                else:
                    self.stdout.write("Adding contact: {0}"
                                      "".format(row['phone']))
                    timestamp = "{0} 2018 18:00:00+0000".format(row['date'])

                    self.stdout.write("Timestamp is: {0}"
                                      "".format(timestamp))

                    timestamp = datetime.strptime(timestamp,
                                                  '%m/%d/%Y %H:%M:%S%z')

                    contact = Contact(phone_number=e164)
                    contact.save()
                    contact.date_created = timestamp

                    if 'Y' in row['arrested'].upper():
                        contact.arrested = True

                    contact.save()
                    self.stdout.write("Contact added.")
