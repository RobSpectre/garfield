from django.test import TestCase

from sims.models import Sim


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
