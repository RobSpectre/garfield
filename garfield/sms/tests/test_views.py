from mock import patch

from django.http import QueryDict

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
                            "<Response />")

    @patch('sms.tasks.send_deterrence.apply_async')
    def test_index_send_deterrence(self, mock_deterrence):
        response = self.client.sms("!deter",
                                   path="/sms/")

        self.assert_twiml(response)
        self.assertContains(response,
                            "Deterrence being sent.")
        self.assertTrue(mock_deterrence.called)
        mock_deterrence.assert_called_once_with(args=["http://example.com",
                                                      self.querydict])
