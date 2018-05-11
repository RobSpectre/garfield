from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from mock import patch

from sms.tests.test_sms import GarfieldTwilioTestCase
from sms.tests.test_sms import GarfieldTwilioTestClient

from contacts.models import Contact
from phone_numbers.models import PhoneNumber

from deterrence.models import Deterrent
from deterrence.models import DeterrenceCampaign


class DeterrenceViewsTestCase(GarfieldTwilioTestCase):
    def test_index(self):
        response = self.client.sms("!deter",
                                   path=reverse('deterrence:index'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Redirect>{0}</Redirect>"
                            "".format(reverse('deterrence:deter')))

    def test_new_deterrence(self):
        response = self.client.sms("!new_deterrence",
                                   path=reverse('deterrence:index'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Redirect>{0}</Redirect>"
                            "".format(reverse('deterrence:new_deterrence')))

    def test_unknown(self):
        response = self.client.sms("HEYYY MOOOOORTY!",
                                   path=reverse('deterrence:index'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "I did not understand")


class DeterrenceDeterTestCase(GarfieldTwilioTestCase):
    @patch('deterrence.tasks.send_deterrence_campaign.apply_async')
    def test_deter(self, mock_send):
        response = self.client.sms("!deter",
                                   path=reverse('deterrence:deter'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "No contacts are currently queued for "
                            "deterrence.")
        self.assertFalse(mock_send.called)


@override_settings(TWILIO_AUTH_TOKEN="yyyyyyyy",
                   ALLOWED_HOSTS=['example.com'])
class DeterrenceDeterCampaignTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.client = GarfieldTwilioTestClient()
        self.contact_a = \
            Contact.objects.create(phone_number="+15556667777",
                                   whitepages_first_name="John")
        self.contact_b = Contact.objects.create(phone_number="+15556667778")
        self.contact_c = Contact.objects.create(phone_number="+15556667779")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       number_type="ADV",
                                                       country_code="1")

        self.det_number = PhoneNumber.objects.create(sid="PNyyy",
                                                     account_sid="ACxxx",
                                                     service_sid="SExxx",
                                                     url="http://exmple.com",
                                                     e164="+15558675310",
                                                     formatted="(555) "
                                                               "867-5310",
                                                     friendly_name="Stuff.",
                                                     number_type="DET",
                                                     country_code="1")

        self.contact_a.related_phone_numbers.add(self.phone_number)
        self.contact_b.related_phone_numbers.add(self.phone_number)
        self.contact_c.related_phone_numbers.add(self.phone_number)

        image = SimpleUploadedFile(name="example_image.png",
                                   content=open("./deterrence/tests/assets/"
                                                "example_image.png",
                                                "rb").read(),
                                   content_type="image/png")

        self.deterrent = Deterrent.objects.create(image=image,
                                                  body="A message from "
                                                       "Garfield.",
                                                  personalize=True)
        self.deterrence_campaign = \
            DeterrenceCampaign.objects \
            .create(related_deterrent=self.deterrent,
                    related_phone_number=self.det_number)

        self.deterrence_campaign.related_contacts.add(self.contact_a)
        self.deterrence_campaign.related_contacts.add(self.contact_b)
        self.deterrence_campaign.related_contacts.add(self.contact_c)

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}

    @patch('deterrence.tasks.send_deterrence_campaign.apply_async')
    def test_deter_no_campaign(self, mock_send):
        self.deterrence_campaign.delete()

        response = self.client.sms("!deter",
                                   path=reverse('deterrence:deter'))

        GarfieldTwilioTestCase().assert_twiml(response)
        self.assertContains(response,
                            "No contacts are currently queued for "
                            "deterrence.")
        self.assertFalse(mock_send.called)

    @patch('deterrence.tasks.send_deterrence_campaign.apply_async')
    def test_deter_full_campaign(self, mock_send):
        response = self.client.sms("!deter",
                                   path=reverse('deterrence:deter'))

        GarfieldTwilioTestCase().assert_twiml(response)
        self.assertContains(response,
                            "Sending deterrence to 3 contacts.")
        self.assertTrue(mock_send.called)


class DeterrenceNewDeterrenceTestCase(GarfieldTwilioTestCase):
    @patch('phone_numbers.tasks.buy_new_phone_number.apply_async')
    @patch('deterrence.tasks.send_deterrence.apply_async')
    def test_deter(self, mock_send, mock_buy):
        response = self.client.sms("!new_deterrence",
                                   path=reverse('deterrence:new_deterrence'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "Buying new deterrence")
        self.assertFalse(mock_send.called)
        self.assertTrue(mock_buy.called)


class DeterrenceMessageStatusCallbackTestCase(GarfieldTwilioTestCase):
    @patch('deterrence.tasks.'
           'handle_deterrence_message_status_callback.apply_async')
    def test_deterrence_message_status_callback(self, mock_status_callback):
        response = self.client.sms("A message from Garfield.",
                                   path=reverse("deterrence:deterrence_"
                                                "message_status_callback"),
                                   extra_params={"MessageStatus": "delivered",
                                                 "MessageSid": "MMxxxx"})

        self.assert_twiml(response)
        mock_status_callback.assert_called_once_with(args=['MMxxxx',
                                                           'delivered'])
