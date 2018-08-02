from django.test import TestCase

from phone_numbers.models import PhoneNumber


class PhoneNumberModelTestCase(TestCase):
    def setUp(self):
        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1")

    def test_string_representation(self):
        self.assertEquals(str(self.phone_number),
                          "Stuff.")
