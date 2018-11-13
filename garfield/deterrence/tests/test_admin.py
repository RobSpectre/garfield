from django.test import RequestFactory
from django.test import TestCase

from deterrence.admin import DeterrenceMessageInline


class DeterrenceInlineTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.request = self.factory.get("/stuff")

    def test_deterrence_message_inline_get_extra(self):
        test = DeterrenceMessageInline.get_extra(None, self.request)

        self.assertEqual(test, 1)

    def test_deterrence_message_inline_get_extra_obj_exists(self):
        test = DeterrenceMessageInline.get_extra(None,
                                                 self.request,
                                                 obj=True)

        self.assertEqual(test, 0)
