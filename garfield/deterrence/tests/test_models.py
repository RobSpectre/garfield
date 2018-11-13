from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from mock import patch

from contacts.models import Contact
from phone_numbers.models import PhoneNumber

from deterrence.models import Deterrent
from deterrence.models import DeterrenceCampaign
from deterrence.models import DeterrenceMessage


class DeterrentTestCase(TestCase):
    def setUp(self):
        image = SimpleUploadedFile(name="example_image.png",
                                   content=open("./deterrence/tests/assets/"
                                                "example_image.png",
                                                "rb").read(),
                                   content_type="image/png")

        self.deterrent = Deterrent.objects.create(image=image,
                                                  body="A message from "
                                                       "Garfield.")

    def test_string_representation(self):
        self.assertTrue("Deterrent" in str(self.deterrent))
        self.assertTrue("A message from" in str(self.deterrent))


class DeterrenceCampaignTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15554445555",
                                                       formatted="(555) "
                                                       "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       number_type="ADV")

        image = SimpleUploadedFile(name="example_image.png",
                                   content=open("./deterrence/tests/assets/"
                                                "example_image.png",
                                                "rb").read(),
                                   content_type="image/png")

        self.deterrent = Deterrent.objects.create(image=image,
                                                  body="A message from "
                                                       "Garfield.")

        self.contact_1 = \
            Contact.objects.create(phone_number="+15556667777")
        self.contact_2 = \
            Contact.objects.create(phone_number="+15556667778")

        self.deterrence_campaign = \
            DeterrenceCampaign.objects \
            .create(related_deterrent=self.deterrent)

        self.deterrence_campaign.related_contacts.add(self.contact_1)
        self.deterrence_campaign.related_contacts.add(self.contact_2)

    def test_string_representation(self):
        self.assertTrue("Deterrence "
                        "Campaign" in str(self.deterrence_campaign))
        self.assertTrue("sent to 2 contacts",
                        "Campaign" in str(self.deterrence_campaign))

    def test_date_sent_string_representation(self):
        self.deterrence_campaign.date_sent = timezone.now()
        self.assertEqual("Deterrence Campaign: Sent {0} to 2 contacts"
                         "".format(self.deterrence_campaign.date_sent),
                         str(self.deterrence_campaign))


class DeterrenceMessageTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15554445555",
                                                       formatted="(555) "
                                                       "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       number_type="ADV")

        image = SimpleUploadedFile(name="example_image.png",
                                   content=open("./deterrence/tests/assets/"
                                                "example_image.png",
                                                "rb").read(),
                                   content_type="image/png")

        self.deterrent = Deterrent.objects.create(image=image,
                                                  body="A message from "
                                                       "Garfield.")

        self.contact_1 = \
            Contact.objects.create(phone_number="+15556667777")
        self.contact_2 = \
            Contact.objects.create(phone_number="+15556667778")

        self.deterrence_campaign = \
            DeterrenceCampaign.objects \
            .create(related_deterrent=self.deterrent)

        self.deterrence_campaign.related_contacts.add(self.contact_1)
        self.deterrence_campaign.related_contacts.add(self.contact_2)

        self.deterrence_message = \
            DeterrenceMessage.objects \
            .create(status="queued",
                    related_deterrent=self.deterrent,
                    related_phone_number=self.phone_number,
                    related_campaign=self.deterrence_campaign,
                    related_contact=self.contact_1)

    def test_string_representation(self):
        self.assertEqual(str(self.deterrence_message),
                         "Deterrence message queued {0} to (555) 666-7777: "
                         "Unidentified"
                         "".format(self.deterrence_message.date_created))
