from django.http import QueryDict
from django.urls import reverse

from mock import patch

from phone_numbers.models import PhoneNumber
from sms.tests.test_sms import GarfieldTwilioTestCase


class SmsViewsTestCase(GarfieldTwilioTestCase):
    params = {"MessageSid": "SMtesting",
              "AccountSid": "ACxxxxx",
              "From": "+15556667777",
              "To": "+15558675309",
              "Body": "!deter",
              "Direction": "inbound",
              "FromCity": "BROOKLYN",
              "FromState": "NY",
              "FromCountry": "US",
              "FromZip": "55555"}
    querydict = QueryDict('', mutable=True)
    querydict.update(params)

    def test_index_no_keyword(self):
        response = self.client.sms("Test.",
                                   path="/sms/")

        self.assert_twiml(response)
        self.assertContains(response,
                            "I did not understand")

    def test_index_send_deterrence(self):
        response = self.client.sms("!deter",
                                   path="/sms/")

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Redirect>{0}</Redirect>"
                            "".format(reverse('deterrence:index')))


class SmsViewsPhoneNumberTestCase(GarfieldTwilioTestCase):
    @patch('phone_numbers.tasks.buy_new_phone_number.apply_async')
    def test_buy_new_ad_phone_number(self, mock_buy):
        params = {"MessageSid": "SMtesting",
                  "AccountSid": "ACxxxxx",
                  "From": "+15556667777",
                  "To": "+15558675309",
                  "Body": "!new_ad",
                  "Direction": "inbound",
                  "FromCity": "BROOKLYN",
                  "FromState": "NY",
                  "FromCountry": "US",
                  "FromZip": "55555"}
        querydict = QueryDict('', mutable=True)
        querydict.update(params)

        response = self.client.sms("!new_ad",
                                   path="/sms/")

        self.assert_twiml(response)
        self.assertContains(response,
                            "Buying new advertisement phone number")

        self.assertTrue(mock_buy.called)
        mock_buy.assert_called_once_with(args=["http://example.com",
                                               querydict,
                                               PhoneNumber.AD])

    def test_buy_new_deterrence_phone_number(self):
        response = self.client.sms("!new_deterrence",
                                   path="/sms/")

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Redirect>{0}</Redirect"
                            "".format(reverse('deterrence:index')))
