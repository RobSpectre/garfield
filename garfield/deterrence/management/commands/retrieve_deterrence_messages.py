from django.core.management.base import BaseCommand
from django.conf import settings

from contacts.models import Contact
from deterrence.models import Deterrent
from deterrence.models import DeterrenceCampaign
from deterrence.models import DeterrenceMessage
from phone_numbers.models import PhoneNumber

from twilio.rest import Client


class Command(BaseCommand):
    help = "Retrieve all deterrence messages from Twilio logs."

    def handle(self, *args, **kwargs):
        self.stdout.write("Retrieving previously sent deterrence "
                          "messages from Twilio logs...")

        messages = self.get_deterrence_messages()

        deterrent = Deterrent.objects.latest('date_created')

        for message in messages:
            if message.body.startswith("Deterrence being sent"):
                campaign = \
                    DeterrenceCampaign(related_deterrent=deterrent,
                                       date_created=message.date_sent)
                campaign.save()

                campaign.date_sent = message.date_sent
                campaign.save()
            elif "message from NYPD" in message.body:
                try:
                    deterrence_message = \
                        DeterrenceMessage.objects.get(sid=message.sid)
                    self.stdout.write("Deterrence message {0} is "
                                      "already saved.".format(message.sid))
                    continue
                except DeterrenceMessage.DoesNotExist:
                    pass

                try:
                    contact = \
                        Contact.objects.get(phone_number=message.to)
                except Contact.DoesNotExist:
                    self.stdout.write("Error finding contact: {0}"
                                      "".format(message.to))
                    continue
                except Contact.MultipleObjectsReturned:
                    self.stdout.write("Multiple Contacts found for {0}!"
                                      "".format(message.to))
                    contact = \
                        Contact.objects \
                        .filter(phone_number=message.to) \
                        .latest('date_created')

                phone_number = \
                    PhoneNumber.objects.get(e164=message.from_)

                deterrence_message = \
                    self.create_deterrence_message(message,
                                                   campaign,
                                                   deterrent,
                                                   contact,
                                                   phone_number)

                self.stdout.write("Saving deterrence message: "
                                  "{0}".format(deterrence_message.sid))

                deterrence_message.save()

                campaign.related_contacts.add(contact)
                campaign.save()

        self.stdout.write("Adding undeterred contacts...")

        campaign = DeterrenceCampaign(related_deterrent=deterrent)
        campaign.save()

        queryset = (Contact.objects.filter(deterred=False,
                                           do_not_deter=False,
                                           arrested=False,
                                           recruiter=False))

        for contact in queryset:
            self.stdout.write("Adding contact: {0}".format(contact))
            campaign.related_contacts.add(contact)

        campaign.save()

        self.stdout.write("Added {0} contacts. Done.".format(len(queryset)))

    def get_deterrence_messages(self):
        messages = []

        for phone_number in PhoneNumber.objects.filter(number_type="DET"):
            new_messages = \
                self.get_deterrence_messages_for_phone_number(phone_number)

            self.stdout.write("Retrieved {0} from {1}..."
                              "".format(len(new_messages),
                                        phone_number.friendly_name))
            messages = messages + new_messages

        self.stdout.write("{0} messages retrieved.".format(len(messages)))

        return sorted(messages,
                      key=lambda x: x.date_sent)

    def get_deterrence_messages_for_phone_number(self,
                                                 phone_number):
        client = Client(settings.TWILIO_ACCOUNT_SID,
                        settings.TWILIO_AUTH_TOKEN)
        messages = client.messages.list(from_=phone_number.e164)

        return messages

    def create_deterrence_message(self,
                                  message,
                                  campaign,
                                  deterrent,
                                  contact,
                                  phone_number):
        deterrence_message = \
            DeterrenceMessage(sid=message.sid,
                              body=message.body,
                              status=message.status,
                              related_deterrent=deterrent,
                              related_contact=contact,
                              related_phone_number=phone_number,
                              related_campaign=campaign)
        deterrence_message.save()

        deterrence_message.date_created = message.date_sent
        return deterrence_message
