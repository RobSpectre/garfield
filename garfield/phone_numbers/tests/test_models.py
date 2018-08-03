from django.test import TestCase

from bots.models import Bot
from phone_numbers.models import PhoneNumber
from sims.models import Sim


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

        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

        self.bot = Bot.objects.create(alias="Rosa",
                                      neighborhood="Times Square",
                                      location="42nd and Broadway",
                                      rates="100hr 50hh 40 ss",
                                      model="buyer_intent_full")

    def test_string_representation(self):
        self.assertEquals(str(self.phone_number),
                          "Stuff.")

    def test_string_representation_with_sim(self):
        self.phone_number.related_sim = self.sim

        self.assertEquals(str(self.phone_number),
                          "Stuff. -> TestSim")

    def test_string_representation_with_bot(self):
        self.phone_number.related_bot = self.bot

        self.assertEquals(str(self.phone_number),
                          "Stuff. -> Rosa - buyer_intent_full: Times Square,"
                          " 42nd and Broadway")
