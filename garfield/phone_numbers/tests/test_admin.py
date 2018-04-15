import datetime

from django.test import RequestFactory
from django.test import TestCase

from sms.models import SmsMessage

from phone_numbers.admin import SmsMessageInline
from phone_numbers.admin import CallInline


class SmsMessageInlineTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.request = self.factory.get("/stuff")

        for i in range(5):
            SmsMessage.objects.create(sid="MMxxx{0}".format(str(i)),
                                      from_number="+15556667777",
                                      to_number="+15558675309",
                                      body="Woo times {0}".format(str(i)))

        for i in range(5):
            msg = SmsMessage.objects.get(sid="MMxxx{0}".format(str(i)))
            msg.date_created = msg.date_created - datetime.timedelta(days=i)
            msg.save()

    def test_sms_message_inline_get_extra(self):
        test = SmsMessageInline.get_extra(None, self.request)

        self.assertEquals(test, 1)

    def test_sms_message_inline_get_extra_obj_exists(self):
        test = SmsMessageInline.get_extra(None, self.request, obj=True)

        self.assertEquals(test, 0)


class CallInlineTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.request = self.factory.get("/stuff")

    def test_call_inline_get_extra(self):
        test = CallInline.get_extra(None, self.request)

        self.assertEquals(test, 1)

    def test_call_inline_get_extra_obj_exists(self):
        test = CallInline.get_extra(None, self.request, obj=True)

        self.assertEquals(test, 0)
