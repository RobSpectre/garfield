from django.test import RequestFactory
from django.test import TestCase

from contacts.admin import SmsMessageInline

from sms.models import SmsMessage

'''
class SmsMessageInlineTestCase(TestCase):
    def setUp(self):
        self.inline = SmsMessageInline(parent_model=SmsMessage)

        self.factory = RequestFactory()

        self.request = self.factor.get("/stuff")

    def test_get_extra(self):
        test = self.inline.get_extra(self.request)

        self.assertEquals(test, 0)

    def test_get_extra_obj_exists(self):
        test = self.inline.get_extra(self.request, obj=True)

        self.assertEquals(test, 0)
'''
