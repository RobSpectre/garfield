from django.test import TestCase
from django.test import override_settings

from mock import patch
from mock import MagicMock

from twilio.base.exceptions import TwilioRestException

from sims.models import Sim

from phone_numbers.models import PhoneNumber

from phone_numbers.tasks import buy_new_phone_number


@override_settings(TWILIO_ACCOUNT_SID="ACxxxx",
                   TWILIO_AUTH_TOKEN="yyyyyyy",
                   TWILIO_APP_SID="APzzzzzzzz"
                   TWILIO_PHONE_NUMBER="+15556667777")
class TaskPhoneNumbersTestCase(TestCase):
    def setUp(self):
        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

    @patch('sms.tasks.send_sms_message.apply_async')
    @patch('twilio.rest.api.v2010.account.available_phone_number'
           '.LocalList.list')
    @patch('twilio.rest.api.v2010.account.incoming_phone_number'
           '.LocalList.create')
    def test_buy_ad_phone_number(self, mock_buy, mock_search, mock_send):
        mock_return = MagicMock()
        mock_return.phone_number = "+15552223333"

        mock_search.return_value = [mock_return]

        mock_buy_return = MagicMock()
        mock_buy_return.sid = "PNxxxx"
        mock_buy_return.account_sid = "ACxxxx"
        mock_buy_return.uri = "https://example.com/phone"
        mock_buy_return.phone_number = "+15552223333"

        mock_buy.return_value = mock_buy_return

        test = buy_new_phone_number("https://example.com",
                                    {"From": "sim:DExxx"},
                                    "ADV")

        results = PhoneNumber.objects.all()

        self.assertEquals(len(results), 1)
        self.assertEquals(results[0].e164, "+15552223333")
        self.assertEquals(results[0].formatted, "(555) 222-3333")
        mock_send.assert_called_once_with(kwargs={"from_": "+15552223333",
                                                  "to": "+15556667777",
                                                  "body": "This is your new"
                                                          " ADV phone "
                                                          "number."})
        self.assertTrue(mock_search.called)
        self.assertTrue(mock_buy.called)
        self.assertEquals(results[0].related_sim, self.sim)
        self.assertTrue(test)

    @patch('sms.tasks.send_sms_message.apply_async')
    @patch('twilio.rest.api.v2010.account.available_phone_number'
           '.LocalList.list')
    @patch('twilio.rest.api.v2010.account.incoming_phone_number'
           '.LocalList.create')
    def test_buy_ad_phone_number_fail_number_purchase(self,
                                                      mock_buy,
                                                      mock_search,
                                                      mock_send):

        mock_return = MagicMock()
        mock_return.phone_number = "+15552223333"

        mock_search.return_value = [mock_return]

        mock_buy.side_effect = \
            MagicMock(side_effect=TwilioRestException(401,
                                                      "https://error.com",
                                                      "Not Authorized"))

        test = buy_new_phone_number("https://example.com",
                                    {"From": "sim:DExxx"},
                                    "ADV")

        self.assertFalse(test)
        mock_send.assert_called_once_with(kwargs={"from_": "+15556667777",
                                                  "to": "+15556667777",
                                                  "body": "There was an "
                                                          "error purchasing "
                                                          "your phone number"
                                                          ": Not Authorized"})
