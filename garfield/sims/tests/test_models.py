from django.test import TestCase

from phone_numbers.models import PhoneNumber
from sims.models import Sim
from sims.models import Whisper


class SimTestCase(TestCase):
    def setUp(self):
        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

    def test_string_respresentation(self):
        self.assertEquals(str(self.sim),
                          "DExxx: TestSim")


class WhisperTestCase(TestCase):
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

        self.whisper = Whisper.objects \
            .create(body="Test.",
                    related_phone_number=self.phone_number)

    def test_string_representation(self):
        self.assertEquals(str(self.whisper),
                          "Whisper for +15558675309: "
                          "{0}".format(self.whisper.date_created))
