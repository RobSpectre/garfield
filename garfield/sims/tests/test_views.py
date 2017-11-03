from django.test import override_settings

from mock import patch

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sms.models import SmsMessage

from sms.tests.test_sms import GarfieldTwilioTestCase
from sms.tests.test_sms import GarfieldTwilioTestClient

from sims.models import Sim
from sims.models import Whisper


@override_settings(TWILIO_PHONE_NUMBER="+15558675309")
class GarfieldTestSimSmsCaseNewContact(GarfieldTwilioTestCase):
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


@override_settings(TWILIO_PHONE_NUMBER="+15558675309")
class GarfieldTestCaseWithContact(GarfieldTwilioTestCase):
    def setUp(self):
        self.client = GarfieldTwilioTestClient()

        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       related_sim=self.sim)

        self.sms_message = SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            body="Test.",
                            related_phone_number=self.phone_number)


@override_settings(TWILIO_PHONE_NUMBER="+15558675309")
class GarfieldTestSimSmsCaseExistingContact(GarfieldTestCaseWithContact):
    @patch('sms.tasks.save_sms_message.apply_async')
    def test_sim_receive_sms(self, mock_save_sms_message):
        response = self.client.sms("Test.",
                                   path="/sims/sms/receive/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_sms_message.called)
        self.assertContains(response,
                            'from="+15556667777"')
        self.assertContains(response,
                            'to="sim:DExxx"')

    @patch('sms.tasks.save_sms_message.apply_async')
    def test_sim_send_sms(self, mock_save_sms_message):
        response = self.client.sms("Test.", to="+15556667777",
                                   path="/sims/sms/send/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_sms_message.called)
        self.assertContains(response,
                            'from="+15558675309"')
        self.assertContains(response,
                            'to="+15556667777"')


class SimSmsWhisperTestCase(GarfieldTwilioTestCase):
    def setUp(self):
        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       related_sim=self.sim)

        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.whisper = Whisper(body="*whisper*",
                               related_phone_number=self.phone_number,
                               related_contact=self.contact)
        self.whisper.save()

        self.client = GarfieldTwilioTestClient()

    def test_send_whisper(self):
        response = self.client.sms("Test.",
                                   path="/sims/sms/receive/")

        self.assertContains(response,
                            "*whisper*")
        self.assertTrue(Whisper.objects.all()[0].sent)


@override_settings(TWILIO_PHONE_NUMBER="+15558675309")
class GarfieldSimVoiceTestCase(GarfieldTwilioTestCase):
    @patch('voice.tasks.save_call.apply_async')
    def test_sims_receive_call(self, mock_save_call):
        response = self.client.call("Test.",
                                    path="/sims/voice/receive/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_call.called)

    @patch('voice.tasks.save_call.apply_async')
    def test_sims_send_call(self, mock_save_call):
        response = self.client.call("Test.",
                                    path="/sims/voice/send/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_call.called)


@override_settings(TWILIO_PHONE_NUMBER="+15558675309")
class GarfieldSimVoiceTestCaseExistingContact(GarfieldTestCaseWithContact):
    @patch('voice.tasks.save_call.apply_async')
    def test_sims_receive_call(self, mock_save_call):
        response = self.client.call("+15558675309",
                                    path="/sims/voice/receive/")

        self.assert_twiml(response)
        self.assertContains(response,
                            'callerId="+15556667777"')
        self.assertContains(response,
                            "<Sim>DExxx</Sim>")
        self.assertTrue(mock_save_call.called)

    @patch('voice.tasks.save_call.apply_async')
    def test_sims_send_call(self, mock_save_call):
        response = self.client.call("+15556667777",
                                    path="/sims/voice/send/")

        self.assert_twiml(response)
        self.assertContains(response,
                            'callerId="+15558675309"')
        self.assertContains(response,
                            "+15556667777</Dial>")
        self.assertTrue(mock_save_call.called)

    @patch('voice.tasks.save_voice_recording.apply_async')
    def test_sims_voice_recording(self, mock_save_voice_recording):
        response = self.client.call("Test.",
                                    path="/sims/voice/recording/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_voice_recording.called)
