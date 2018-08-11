from datetime import timedelta

from django.test import TestCase
from django.test import override_settings

from mock import patch

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sims.models import Sim
from sms.models import SmsMessage

from dashboard.tasks import send_daily_statistics


@override_settings(TWILIO_PHONE_NUMBER="+15558675309",
                   GARFIELD_JURISDICTION="childsafe.ai Test")
class TestDailyStatistics(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")
        self.contact = Contact.objects.create(phone_number="+15556667777")
        self.contact.date_created = self.contact.date_created - \
            timedelta(days=1)

        self.adv_phone_number = \
            PhoneNumber.objects.create(sid="PNxxx",
                                       account_sid="ACxxx",
                                       service_sid="SExxx",
                                       url="http://ee.com",
                                       e164="+15558675309",
                                       formatted="(555) "
                                                 "867-"
                                                 "5309",
                                       friendly_name="Sf.",
                                       number_type="ADV",
                                       country_code="1",
                                       related_sim=self.sim)

        self.contact.related_phone_numbers.add(self.adv_phone_number)
        self.contact.save()

        msg = SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            body="Ad response.",
                            related_phone_number=self.adv_phone_number)
        msg.date_created = msg.date_created - timedelta(days=1)
        msg.save()

        msg = SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            body="2nd Ad Response.",
                            related_phone_number=self.adv_phone_number)
        msg.date_created = msg.date_created - timedelta(days=1)
        msg.save()

    @patch('dashboard.tasks.send_sms_message')
    def test_send_daily_statistics(self, mock_send):
        send_daily_statistics("+15556667777")

        mock_send.assert_called_once_with(from_="+15558675309",
                                          to="+15556667777",
                                          body="Today's stats from "
                                               "childsafe.ai Test:\n\n"
                                               "Contacts: 1\n"
                                               "SMS Messages: 2\n"
                                               "Calls: 0\n"
                                               "Deterrents: 0")
