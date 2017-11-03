from mock import patch

from sms.tests.test_sms import GarfieldTwilioTestCase


class SmsViewsTestCase(GarfieldTwilioTestCase):
    def test_index_no_keyword(self):
        response = self.client.sms("Test.",
                                   path="/sms/")

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Response />")

    @patch('sms.tasks.send_deterrence.apply_async')
    def test_index_send_deterrence(self, mock_deterrence):
        response = self.client.sms("!deter",
                                   path="/sms/")

        self.assert_twiml(response)
        self.assertContains(response,
                            "Deterrence being sent.")
        self.assertTrue(mock_deterrence.called)
