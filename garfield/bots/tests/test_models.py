from django.test import TestCase

from bots.models import Bot


class BotModelTestCase(TestCase):
    def setUp(self):
        self.bot = Bot.objects.create(alias="Rosa",
                                      neighborhood="Times Square",
                                      location="42nd and Broadway",
                                      rates="100hr 50hh 40 ss",
                                      model="buyer_intent_full")

    def test_string_representation(self):
        self.assertEqual(str(self.bot),
                         "Rosa - buyer_intent_full: Times Square,"
                         " 42nd and Broadway")
