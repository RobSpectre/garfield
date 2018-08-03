from django.test import override_settings
from django.urls import reverse

from mock import patch

from bots.models import Bot
from phone_numbers.models import PhoneNumber
from sims.models import Sim

from sms.tests.test_sms import GarfieldTwilioTestCase
from sms.tests.test_sms import GarfieldTwilioTestClient


class BotsViewsTestCaseNoBotNoSim(GarfieldTwilioTestCase):
    def test_sms(self):
        response = self.client.sms("Hello.",
                                   path=reverse('bots:sms'))
        self.assert_twiml(response)

    def test_voice(self):
        response = self.client.call("+15558675309",
                                    path=reverse('bots:voice'))
        self.assert_twiml(response)
        self.assertContains(response,
                            "<Response />")


class BotsViewsTestCaseNoBotSim(GarfieldTwilioTestCase):
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
                                                       number_type="ADV",
                                                       related_sim=self.sim)

    def test_sms(self):
        response = self.client.sms("Hello.",
                                   path=reverse('bots:sms'))
        self.assert_twiml(response)
        self.assertContains(response,
                            "Redirect")
        self.assertContains(response,
                            "{0}".format(reverse('sims:sms_receive')))

    @patch('voice.tasks.save_call.apply_async')
    def test_voice(self, mock_save):
        response = self.client.call("+15558675309",
                                    path=reverse('bots:voice'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Redirect>")
        self.assertContains(response,
                            reverse('sims:voice_receive'))
        self.assertFalse(mock_save.called)


class BotsViewsTestCaseNoSimBot(GarfieldTwilioTestCase):
    def setUp(self):
        self.client = GarfieldTwilioTestClient()

        self.bot = Bot.objects.create(alias="Botty McBotface",
                                      neighborhood="Brooklyn",
                                      location="Prospect Park",
                                      rates="$1,000,000",
                                      model='test_model')

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
                                                       related_bot=self.bot)

    @patch('bots.tasks.process_bot_response.apply_async')
    def test_sms(self, mock_bot):
        response = self.client.sms("Hello.",
                                   path=reverse('bots:sms'))

        self.assert_twiml(response)
        self.assertTrue(mock_bot.called)

    @patch('voice.tasks.save_call.apply_async')
    def test_voice(self, mock_save):
        response = self.client.call("+15558675309",
                                    path=reverse('bots:voice'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Play>")
        self.assertContains(response,
                            ".mp3")
        self.assertTrue(mock_save.called)


class BotsViewsTestCaseDeterrenceResponse(GarfieldTwilioTestCase):
    def setUp(self):
        self.client = GarfieldTwilioTestClient()

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       number_type="DET")

    @patch('sms.tasks.save_sms_message.apply_async')
    def test_sms(self, mock_save):
        response = self.client.sms('Test.',
                                   path=reverse('bots:sms'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Response />")
        self.assertTrue(mock_save.called)

    @override_settings(GARFIELD_JURISDICTION="ChildSafe")
    @patch('voice.tasks.save_call.apply_async')
    def test_voice(self, mock_save):
        response = self.client.call("+15558675309",
                                    path=reverse('bots:voice'))
        self.assertContains(response,
                            "<Say voice")
        self.assertContains(response,
                            "ChildSafe")
