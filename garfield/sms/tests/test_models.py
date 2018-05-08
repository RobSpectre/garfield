from django.test import TestCase

from mock import patch

from sms.models import SmsMessage


class SmsMessageModelTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    def setUp(self, mock_check_campaign):
        self.sms_message = SmsMessage.objects.create(sid="MMxxxx",
                                                     from_number="from",
                                                     to_number="to",
                                                     body="Test.")

    def test_string_representation(self):
        date = self.sms_message.date_created
        self.assertEquals(str(self.sms_message),
                          "{0}: from from to to".format(date))
