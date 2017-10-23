from django.test import TestCase

from sms.models import SmsMessage


class SmsMessageModelTestCase(TestCase):
    def setUp(self):
        self.sms_message = SmsMessage.objects.create(sid="MMxxxx",
                                                     from_number="+15556667777",
                                                     to_number="+15558675309",
                                                     body="Test.")

    def test_string_representation(self):
        date = self.sms_message.date_created
        self.assertEquals(str(self.sms_message),
                          "{0}: from +15556667777 to +15558675309".format(date))
