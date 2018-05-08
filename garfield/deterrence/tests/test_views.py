from django.urls import reverse

from mock import patch

from sms.tests.test_sms import GarfieldTwilioTestCase


class DeterrenceViewsTestCase(GarfieldTwilioTestCase):
    def test_index(self):
        response = self.client.sms("!deter",
                                   path=reverse('deterrence:index'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Redirect>{0}</Redirect>"
                            "".format(reverse('deterrence:deter')))

    def test_new_deterrence(self):
        response = self.client.sms("!new_deterrence",
                                   path=reverse('deterrence:index'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "<Redirect>{0}</Redirect>"
                            "".format(reverse('deterrence:new_deterrence')))

    def test_unknown(self):
        response = self.client.sms("HEYYY MOOOOORTY!",
                                   path=reverse('deterrence:index'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "I did not understand")


class DeterrenceDeterTestCase(GarfieldTwilioTestCase):
    @patch('deterrence.tasks.send_deterrence.apply_async')
    def test_deter(self, mock_send):
        response = self.client.sms("!deter",
                                   path=reverse('deterrence:deter'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "Sending deterrence")
        self.assertTrue(mock_send.called)


class DeterrenceNewDeterrenceTestCase(GarfieldTwilioTestCase):
    @patch('phone_numbers.tasks.buy_new_phone_number.apply_async')
    @patch('deterrence.tasks.send_deterrence.apply_async')
    def test_deter(self, mock_send, mock_buy):
        response = self.client.sms("!new_deterrence",
                                   path=reverse('deterrence:new_deterrence'))

        self.assert_twiml(response)
        self.assertContains(response,
                            "Buying new deterrence")
        self.assertFalse(mock_send.called)
        self.assertTrue(mock_buy.called)
