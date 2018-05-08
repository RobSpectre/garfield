from django.conf import settings
from django.test import override_settings

from mock import patch

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sms.models import SmsMessage
from voice.models import Call

from sms.tests.test_sms import GarfieldTwilioTestCase
from sms.tests.test_sms import GarfieldTwilioTestClient

from sims.models import Sim
from sims.models import Whisper


@override_settings(TWILIO_PHONE_NUMBER="+15551112222", DEBUG=False)
class GarfieldTestSimSmsCaseNewContact(GarfieldTwilioTestCase):
    @patch('sms.tasks.save_sms_message.apply_async')
    def test_sim_receive_sms(self, mock_save_sms_message):
        response = self.client.sms("Test.",
                                   path="/sims/sms/receive/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_sms_message.called)

    @patch('sms.tasks.save_sms_message.apply_async')
    def test_sim_send_sms(self, mock_save_sms_message):
        PhoneNumber.objects.create(sid="PNxxx",
                                   account_sid="ACxxx",
                                   service_sid="SExxx",
                                   url="http://exmple.com",
                                   e164="+15554445555",
                                   formatted="(555) "
                                             "867-5309",
                                   friendly_name="Stuff.",
                                   country_code="1",
                                   number_type="ADV")
        response = self.client.sms("Test.",
                                   from_="sim:DExxxxx",
                                   path="/sims/sms/send/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_sms_message.called)
        self.assertNotContains(response,
                               settings.TWILIO_PHONE_NUMBER)


@override_settings(TWILIO_PHONE_NUMBER="+15558675309")
class GarfieldTestCaseWithContact(GarfieldTwilioTestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    def setUp(self, mock_check_campaign):
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
                                                       number_type="ADV",
                                                       related_sim=self.sim)

        self.sms_message = SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            body="Test.",
                            related_phone_number=self.phone_number)

        self.call = Call \
            .objects.create(sid="CAxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            related_phone_number=self.phone_number)


@override_settings(TWILIO_PHONE_NUMBER="+15558675309", DEBUG=False)
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
        response = self.client.sms("Test.",
                                   from_="sim:DExxxxx",
                                   to="+15556667777",
                                   path="/sims/sms/send/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_sms_message.called)
        self.assertContains(response,
                            'from="+15558675309"')
        self.assertContains(response,
                            'to="+15556667777"')

    def test_sim_send_admin_number(self):
        response = self.client.sms("!deter", to="+15558675309",
                                   path="/sims/sms/send/")

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Redirect>")


class SimSmsWhisperTestCase(GarfieldTwilioTestCase):
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup):
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
                                                       number_type="ADV",
                                                       related_sim=self.sim)

        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.whisper = Whisper(body="*whisper*",
                               related_phone_number=self.phone_number,
                               related_contact=self.contact)
        self.whisper.save()

        self.client = GarfieldTwilioTestClient()

    @patch('sms.tasks.save_sms_message.apply_async')
    def test_send_whisper(self, mock_send_message):
        response = self.client.sms("Test.",
                                   path="/sims/sms/receive/")

        self.assertContains(response,
                            "*whisper*")
        self.assertTrue(Whisper.objects.all()[0].sent)
        self.assertTrue(mock_send_message.called)

    @patch('contacts.tasks.lookup_contact.apply_async')
    @patch('sms.tasks.save_sms_message.apply_async')
    def test_send_whisper_multiple_contacts(self,
                                            mock_send_message,
                                            mock_lookup):
        new_contact = Contact.objects.create(phone_number="+15551112222")
        new_whisper = Whisper(body="*whisper two*",
                              related_phone_number=self.phone_number,
                              related_contact=new_contact)
        new_whisper.save()

        response = self.client.sms("Test.",
                                   path="/sims/sms/receive/")

        self.assertContains(response,
                            "*whisper*")
        self.assertNotContains(response,
                               "*whisper two*")
        self.assertTrue(Whisper.objects.all()[0].sent)
        self.assertTrue(mock_send_message.called)
        self.assertTrue(mock_lookup.called)


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
        PhoneNumber.objects.create(sid="PNxxx",
                                   account_sid="ACxxx",
                                   service_sid="SExxx",
                                   url="http://exmple.com",
                                   e164="+15551112222",
                                   formatted="(555) "
                                             "867-5309",
                                   friendly_name="Stuff.",
                                   country_code="1",
                                   number_type="ADV")
        response = self.client.call("+15556667777",
                                    path="/sims/voice/send/")

        self.assert_twiml(response)
        self.assertTrue(mock_save_call.called)
        self.assertNotContains(response,
                               settings.TWILIO_PHONE_NUMBER)
        self.assertContains(response,
                            "callerId=\"+15551112222\"")


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


@override_settings(TWILIO_PHONE_NUMBER="+15558675309")
class GarfieldTestCaseNoUseOfDeterrenceNumber(GarfieldTwilioTestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.client = GarfieldTwilioTestClient()

        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")
        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.det_phone_number = \
            PhoneNumber.objects.create(sid="PNxxx",
                                       account_sid="ACxxx",
                                       service_sid="SExxx",
                                       url="http://ee.com",
                                       e164="+15558675309",
                                       formatted="(555) "
                                                 "867-"
                                                 "5309",
                                       friendly_name="Sf.",
                                       number_type="DET",
                                       country_code="1",
                                       related_sim=self.sim)
        self.adv_phone_number = \
            PhoneNumber.objects.create(sid="PNxxx",
                                       account_sid="ACxxx",
                                       service_sid="SExxx",
                                       url="http://ee.com",
                                       e164="+15558675310",
                                       formatted="(555) "
                                                 "867-"
                                                 "5309",
                                       friendly_name="Sf.",
                                       number_type="ADV",
                                       country_code="1",
                                       related_sim=self.sim)

        self.contact.related_phone_numbers.add(self.adv_phone_number)
        self.contact.save()

        SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675310",
                            body="Ad response.",
                            related_phone_number=self.adv_phone_number)

        SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            body="Deterrence Response.",
                            related_phone_number=self.det_phone_number)

    @patch('sms.tasks.save_sms_message.apply_async')
    def test_send_sms_to_deterrence_respondent(self, mock_save):
        response = self.client.sms("Test.",
                                   from_="sim:DExxxxx",
                                   to="+15556667777",
                                   path="/sims/sms/send/")

        self.assertNotContains(response,
                               "+15558675309")
        self.assertTrue(mock_save.called)

    @patch('voice.tasks.save_call.apply_async')
    def test_send_call_to_deterrence_respondent(self, mock_save):
        response = self.client.call(from_="sim:DExxxxx",
                                    to="+15556667777",
                                    path="/sims/voice/send/")

        self.assertNotContains(response,
                               "+15558675309")
        self.assertTrue(mock_save.called)


@override_settings(TWILIO_PHONE_NUMBER="+15558675309")
class GarfieldTestCaseNoUseOfDeterrenceNumberNoMsgs(GarfieldTwilioTestCase):
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup):
        self.client = GarfieldTwilioTestClient()

        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")
        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.det_phone_number = \
            PhoneNumber.objects.create(sid="PNxxx",
                                       account_sid="ACxxx",
                                       service_sid="SExxx",
                                       url="http://ee.com",
                                       e164="+15558675309",
                                       formatted="(555) "
                                                 "867-"
                                                 "5309",
                                       friendly_name="Sf.",
                                       number_type="DET",
                                       country_code="1",
                                       related_sim=self.sim)
        self.adv_phone_number = \
            PhoneNumber.objects.create(sid="PNxxx",
                                       account_sid="ACxxx",
                                       service_sid="SExxx",
                                       url="http://ee.com",
                                       e164="+15558675310",
                                       formatted="(555) "
                                                 "867-"
                                                 "5309",
                                       friendly_name="Sf.",
                                       number_type="ADV",
                                       country_code="1",
                                       related_sim=self.sim)

    @patch('sms.tasks.save_sms_message.apply_async')
    def test_send_sms_to_deterrence_respondent(self, mock_save):
        response = self.client.sms("Test.",
                                   from_="sim:DExxxxx",
                                   to="+15556667777",
                                   path="/sims/sms/send/")

        self.assertNotContains(response,
                               "+15558675309")
        self.assertTrue(mock_save.called)

    @patch('voice.tasks.save_call.apply_async')
    def test_send_call_to_deterrence_respondent(self, mock_save):
        response = self.client.call(from_="sim:DExxxxx",
                                    to="+15556667777",
                                    path="/sims/voice/send/")

        self.assertNotContains(response,
                               "+15558675309")
        self.assertTrue(mock_save.called)
