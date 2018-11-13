from django.test import RequestFactory
from django.test import TestCase

from contacts.admin import SmsMessageInline
from contacts.admin import CallInline


class SmsMessageInlineTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.request = self.factory.get("/stuff")

    def test_sms_message_inline_get_extra(self):
        test = SmsMessageInline.get_extra(None, self.request)

        self.assertEqual(test, 1)

    def test_sms_message_inline_get_extra_obj_exists(self):
        test = SmsMessageInline.get_extra(None, self.request, obj=True)

        self.assertEqual(test, 0)


class CallInlineTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.request = self.factory.get("/stuff")

    def test_call_inline_get_extra(self):
        test = CallInline.get_extra(None, self.request)

        self.assertEqual(test, 1)

    def test_call_inline_get_extra_obj_exists(self):
        test = CallInline.get_extra(None, self.request, obj=True)

        self.assertEqual(test, 0)
