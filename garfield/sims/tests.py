from sms.tests.test_sms import GarfieldTwilioTestCase


class GarfieldTestSimSmsCase(GarfieldTwilioTestCase):
    def test_sim_receive_sms(self):
        response = self.client.sms("Test.",
                                   path="/sims/sms/receive/")

        self.assert_twiml(response)

    def test_sim_send_sms(self):
        response = self.client.sms("Test.",
                                   path="/sims/sms/send/")

        self.assert_twiml(response)


class GarfieldTestSimVoiceCase(GarfieldTwilioTestCase):
    def test_sims_receive_call(self):
        response = self.client.call("Test.",
                                    path="/sims/voice/receive/")

        self.assert_twiml(response)

    def test_sims_send_call(self):
        response = self.client.call("Test.",
                                    path="/sims/voice/send/")

        self.assert_twiml(response)
