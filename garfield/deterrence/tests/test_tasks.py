from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from mock import patch

from contacts.models import Contact
from phone_numbers.models import PhoneNumber

from deterrence.models import Deterrent
from deterrence.models import DeterrenceCampaign
from deterrence.models import DeterrenceMessage

import deterrence.tasks


@override_settings(TWILIO_PHONE_NUMBER="+18881112222",
                   TWILIO_ACCOUNT_SID='ACxxxx',
                   TWILIO_AUTH_TOKEN='yyyyyyy')
class DeterrenceCampaignTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
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

    @patch('deterrence.tasks.send_deterrence.apply_async')
    def test_send_deterrence_campaign(self, mock_send):
        deterrence.tasks.send_deterrence_campaign("http://example.com",
                                                  self.message)

        self.assertEquals(3,
                          mock_send.call_count)

        campaign = DeterrenceCampaign.objects.latest('date_created')
        self.assertFalse(campaign.date_sent is None)

    @patch('deterrence.tasks.send_deterrence.apply_async')
    def test_send_deterrence_do_not_deter(self, mock_send):
        self.contact_a.do_not_deter = True
        self.contact_a.save()

        deterrence.tasks.send_deterrence_campaign("http://example.com",
                                                  self.message)

        self.assertEquals(2, mock_send.call_count)
        self.assertFalse(self.phone_number.contact_set.all()[0].deterred)

        campaign = DeterrenceCampaign.objects.latest('date_created')
        self.assertFalse(campaign.date_sent is None)

    @patch('deterrence.tasks.send_deterrence.apply_async')
    def test_send_deterrence_arrested(self, mock_send):
        self.contact_a.arrested = True
        self.contact_a.save()

        deterrence.tasks.send_deterrence_campaign("http://example.com",
                                                  self.message)

        self.assertEquals(2, mock_send.call_count)
        self.assertFalse(self.phone_number.contact_set.all()[0].deterred)

        campaign = DeterrenceCampaign.objects.latest('date_created')
        self.assertFalse(campaign.date_sent is None)

    @patch('deterrence.tasks.send_deterrence.apply_async')
    def test_send_deterrence_recruiter(self, mock_send):
        self.contact_a.recruiter = True
        self.contact_a.save()

        deterrence.tasks.send_deterrence_campaign("http://example.com",
                                                  self.message)

        self.assertEquals(2, mock_send.call_count)
        self.assertFalse(self.phone_number.contact_set.all()[0].deterred)

        campaign = DeterrenceCampaign.objects.latest('date_created')
        self.assertFalse(campaign.date_sent is None)


class DeterrenceTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.contact_a = Contact.objects.create(phone_number="+15556667777")
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

    @patch('deterrence.tasks.send_sms_message')
    def test_send_deterrence(self, mock_send):
        mock_send.side_effect = [{'Sid': 'MMxxx',
                                  'Body': 'A message from Garfield.',
                                  'Status': 'queued'}]

        deterrence.tasks.send_deterrence("http://example.com",
                                         self.deterrence_campaign.id,
                                         self.contact_a.id)

        mock_send.assert_called_once_with(
            from_="+15558675310",
            to="+15556667777",
            body="A message from Garfield.",
            media_url="http://example.com/"
                      "{0}".format(self.deterrent.image.url),
            status_callback="http://example.com"
                            "{0}".format(reverse('deterrence:deterrence'
                                                 '_message_status_callback')))
        self.assertEquals(1,
                          len(DeterrenceMessage.objects.all()))
        contact = Contact.objects.get(pk=self.contact_a.id)
        self.assertTrue(contact.deterred)
        self.assertEquals(1,
                          contact.deterrents_received)

    @patch('deterrence.tasks.send_sms_message')
    def test_send_deterrence_first_name(self, mock_send):
        mock_send.side_effect = [{'Sid': 'MMxxx',
                                  'Body': 'John, a message from Garfield.',
                                  'Status': 'queued'}]

        self.contact_a.whitepages_first_name = "John"
        self.contact_a.save()

        deterrence.tasks.send_deterrence("http://example.com",
                                         self.deterrence_campaign.id,
                                         self.contact_a.id)

        mock_send.assert_called_once_with(
            from_="+15558675310",
            to="+15556667777",
            body="John, a message from Garfield.",
            media_url="http://example.com/"
                      "{0}".format(self.deterrent.image.url),
            status_callback="http://example.com"
                            "{0}".format(reverse('deterrence:deterrence'
                                                 '_message_status_callback')))
        self.assertEquals(1,
                          len(DeterrenceMessage.objects.all()))
        contact = Contact.objects.get(pk=self.contact_a.id)
        self.assertTrue(contact.deterred)

    @patch('deterrence.tasks.send_sms_message')
    def test_send_deterrence_no_personalize(self, mock_send):
        mock_send.side_effect = [{'Sid': 'MMxxx',
                                  'Body': 'A message from Garfield.',
                                  'Status': 'queued'}]

        self.contact_a.whitepages_first_name = "John"
        self.contact_a.save()

        self.deterrent.personalize = False
        self.deterrent.save()

        deterrence.tasks.send_deterrence("http://example.com",
                                         self.deterrence_campaign.id,
                                         self.contact_a.id)

        mock_send.assert_called_once_with(
            from_="+15558675310",
            to="+15556667777",
            body="A message from Garfield.",
            media_url="http://example.com/"
                      "{0}".format(self.deterrent.image.url),
            status_callback="http://example.com"
                            "{0}".format(reverse('deterrence:deterrence'
                                                 '_message_status_callback')))
        self.assertEquals(1,
                          len(DeterrenceMessage.objects.all()))
        contact = Contact.objects.get(pk=self.contact_a.id)
        self.assertTrue(contact.deterred)


class DeterrenceTestCaseMultipleNumbers(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.contact_a = Contact.objects.create(phone_number="+15556667777")
        self.contact_b = Contact.objects.create(phone_number="+15556667778")
        self.contact_c = Contact.objects.create(phone_number="+15556667779")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5308",
                                                       friendly_name="Stuff.",
                                                       number_type="ADV",
                                                       country_code="1")

        self.det_number_1 = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       number_type="DET",
                                                       country_code="1")

        self.det_number_2 = PhoneNumber.objects.create(sid="PNyyy",
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

        image = SimpleUploadedFile(name="example_image.png",
                                   content=open("./deterrence/tests/assets/"
                                                "example_image.png",
                                                "rb").read(),
                                   content_type="image/png")

        self.deterrent = Deterrent.objects.create(image=image,
                                                  body="A message from "
                                                       "Garfield.")
        self.deterrence_campaign = \
            DeterrenceCampaign.objects \
            .create(related_deterrent=self.deterrent,
                    related_phone_number=self.det_number_2)

        self.deterrence_campaign.related_contacts.add(self.contact_a)
        self.deterrence_campaign.related_contacts.add(self.contact_b)
        self.deterrence_campaign.related_contacts.add(self.contact_c)

        self.contact_c.related_phone_numbers.add(self.phone_number)

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}

    @patch('deterrence.tasks.send_deterrence.apply_async')
    def test_send_deterrence_campaign(self, mock_send):
        deterrence.tasks.send_deterrence_campaign("http://example.com",
                                                  self.message)

        self.assertEquals(3, mock_send.call_count)
        for call in mock_send.call_args_list:
            args, kwargs = call
            self.assertEquals(kwargs['args'][1],
                              self.deterrence_campaign.id)


class DeterrenceCheckCampaignTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.contact_a = Contact.objects.create(phone_number="+15556667777")
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
                                                       "Garfield.")
        self.deterrence_campaign = \
            DeterrenceCampaign.objects \
            .create(related_deterrent=self.deterrent,
                    related_phone_number=self.det_number)

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}

    def test_check_campaign_for_contact(self):
        test = deterrence.tasks.check_campaign_for_contact(self.contact_a.id)

        campaign = \
            DeterrenceCampaign.objects.get(pk=self.deterrence_campaign.id)

        self.assertFalse(test)
        self.assertEquals(1,
                          len(DeterrenceCampaign.objects.all()))
        self.assertEquals(campaign.related_contacts.all()[0],
                          self.contact_a)

    def test_check_campaign_for_contact_already_present(self):
        self.deterrence_campaign.related_contacts.add(self.contact_b)
        self.deterrence_campaign.save()

        test = deterrence.tasks.check_campaign_for_contact(self.contact_a.id)

        self.assertFalse(test)

        second_test = \
            deterrence.tasks.check_campaign_for_contact(self.contact_b.id)

        campaign = \
            DeterrenceCampaign.objects.get(pk=self.deterrence_campaign.id)

        self.assertTrue(second_test)
        self.assertEquals(2,
                          len(campaign.related_contacts.all()))

    def test_check_campaign_for_contact_campaign_does_not_exist(self):
        self.deterrence_campaign.delete()

        test = deterrence.tasks.check_campaign_for_contact(self.contact_a.id)

        campaigns = DeterrenceCampaign.objects.all()

        self.assertFalse(test)
        self.assertEquals(1,
                          len(campaigns))
        self.assertEquals(campaigns[0].related_contacts.all()[0],
                          self.contact_a)

    def test_check_campaign_for_contact_multiple_attempts(self):
        self.deterrence_campaign.related_contacts.add(self.contact_a)

        deterrence.tasks.check_campaign_for_contact(self.contact_a.id)
        deterrence.tasks.check_campaign_for_contact(self.contact_a.id)
        deterrence.tasks.check_campaign_for_contact(self.contact_a.id)

        campaigns = DeterrenceCampaign.objects.all()

        self.assertEquals(1,
                          len(campaigns))
        self.assertEquals(1,
                          len(campaigns[0].related_contacts.all()))
        self.assertEquals(campaigns[0].related_contacts.all()[0],
                          self.contact_a)


class DeterrenceMessageStatusCallbackTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.contact_a = Contact.objects.create(phone_number="+15556667777")

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

        image = SimpleUploadedFile(name="example_image.png",
                                   content=open("./deterrence/tests/assets/"
                                                "example_image.png",
                                                "rb").read(),
                                   content_type="image/png")

        self.deterrent = Deterrent.objects.create(image=image,
                                                  body="A message from "
                                                       "Garfield.")
        self.deterrence_campaign = \
            DeterrenceCampaign.objects \
            .create(related_deterrent=self.deterrent,
                    related_phone_number=self.det_number)
        self.deterrence_message = \
            DeterrenceMessage.objects \
            .create(sid="MMxxxx",
                    body="A message to you, Rudy.",
                    status="queued",
                    related_phone_number=self.det_number,
                    related_campaign=self.deterrence_campaign,
                    related_contact=self.contact_a,
                    related_deterrent=self.deterrent)

    def test_handle_deterrence_message_status_callback(self):
        deterrence.tasks \
            .handle_deterrence_message_status_callback("MMxxxx",
                                                       "delivered")
        message = DeterrenceMessage.objects.get(sid="MMxxxx")
        self.assertEquals("delivered",
                          message.status)
