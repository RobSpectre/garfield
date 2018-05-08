from django.test import TestCase
from django.test import override_settings

from mock import patch

from contacts.models import Contact
from phone_numbers.models import PhoneNumber

import deterrence.tasks


@override_settings(TWILIO_PHONE_NUMBER="+18881112222")
class DeterrenceTestCase(TestCase):
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup):
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

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}
        self.deterrence_file_path = "https://berserk-sleet-3229.twil.io/" \
                                    "assets/john_deterrent.jpg"

    @patch('deterrence.tasks.send_sms_message.apply_async')
    def test_send_deterrence(self, mock_sms_message):
        deterrence.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(3, mock_sms_message.call_count)
        for call in mock_sms_message.call_args_list:
            args, kwargs = call
            self.assertEquals(kwargs['kwargs']['media_url'],
                              self.deterrence_file_path)
            self.assertEquals(kwargs['kwargs']['from_'],
                              self.det_number.e164)

        for contact in self.phone_number.contact_set.all():
            self.assertTrue(contact.deterred)

    @patch('deterrence.tasks.send_sms_message.apply_async')
    def test_send_deterrence_do_not_deter(self, mock_sms_message):
        self.contact_a.do_not_deter = True
        self.contact_a.save()

        deterrence.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(2, mock_sms_message.call_count)
        self.assertFalse(self.phone_number.contact_set.all()[0].deterred)

    @patch('deterrence.tasks.send_sms_message.apply_async')
    def test_send_deterrence_deterred(self, mock_sms_message):
        self.contact_a.deterred = True
        self.contact_a.save()

        deterrence.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(2, mock_sms_message.call_count)

    @patch('deterrence.tasks.send_sms_message.apply_async')
    def test_send_deterrence_arrested(self, mock_sms_message):
        self.contact_a.arrested = True
        self.contact_a.save()

        deterrence.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(2, mock_sms_message.call_count)

    @patch('deterrence.tasks.send_sms_message.apply_async')
    def test_send_deterrence_recruiter(self, mock_sms_message):
        self.contact_a.recruiter = True
        self.contact_a.save()

        deterrence.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(2, mock_sms_message.call_count)

    @patch('deterrence.tasks.send_sms_message.apply_async')
    def test_send_deterrence_first_name(self, mock_sms_message):
        self.contact_a.whitepages_first_name = "John"
        self.contact_a.save()

        deterrence.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(3, mock_sms_message.call_count)
        for contact in self.phone_number.contact_set.all():
            self.assertTrue(contact.deterred)


class DeterrenceTestCaseMultipleNumbers(TestCase):
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup):
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
        self.contact_c.related_phone_numbers.add(self.phone_number)

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}
        self.deterrence_file_path = "https://berserk-sleet-3229.twil.io/" \
                                    "assets/john_deterrent.jpg"

    @patch('deterrence.tasks.send_sms_message.apply_async')
    def test_send_deterrence(self, mock_sms_message):
        deterrence.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(3, mock_sms_message.call_count)
        for call in mock_sms_message.call_args_list:
            args, kwargs = call
            self.assertEquals(kwargs['kwargs']['media_url'],
                              self.deterrence_file_path)
            self.assertEquals(kwargs['kwargs']['from_'],
                              self.det_number_2.e164)

        for contact in self.phone_number.contact_set.all():
            self.assertTrue(contact.deterred)
