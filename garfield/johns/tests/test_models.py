from django.test import TestCase

from johns.models import John


class JohnModelTestCase(TestCase):
    def setUp(self):
        self.john = John.objects.create(phone_number="+15558675309")

    def test_string_representation(self):
        self.assertEquals(str(self.john),
                          "+15558675309: None None")
