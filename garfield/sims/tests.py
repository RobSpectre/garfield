from mock import patch

from sms.tests.test_sms import GarfieldTwilioTestCase
from sms.tests.test_sms import GarfieldTwilioTestClient


class GarfieldTestSimSmsCaseNewJohn(GarfieldTwilioTestCase):
    @patch('sms.tasks.save_sms_message.apply_async')
    def test_sim_receive_sms(self, mock_save_sms_message):
        response = self.client.sms("Test.",
                                   path="/sims/sms/receive/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_sms_message.called)

    @patch('sms.tasks.save_sms_message.apply_async')
    def test_sim_send_sms(self, mock_save_sms_message):
        response = self.client.sms("Test.",
                                   path="/sims/sms/send/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_sms_message.called)


class GarfieldTestSimVoiceCase(GarfieldTwilioTestCase):
    def test_sims_receive_call(self):
        response = self.client.call("Test.",
                                    path="/sims/voice/receive/")

        self.assert_twiml(response)

    def test_sims_send_call(self):
        response = self.client.call("Test.",
                                    path="/sims/voice/send/")

        self.assert_twiml(response)
