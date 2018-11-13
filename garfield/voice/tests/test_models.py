from django.test import TestCase

from voice.models import Call


class CallModelTestCase(TestCase):
    def setUp(self):
        self.call = Call(sid="CAxxx",
                         from_number="+15558675309",
                         to_number="+15556667777")
        self.call.save()

    def test_string_representation(self):
        self.assertEqual(str(self.call),
                         "{0}: from +15558675309 to "
                         "+15556667777".format(self.call.date_created))
