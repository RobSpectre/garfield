from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from mock import patch

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sims.models import Sim
from sms.models import SmsMessage
from voice.models import Call


class CalculateNumberOfContactsTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

        self.contact_1 = Contact.objects.create(phone_number="+15556667777")
        self.contact_2 = Contact.objects.create(phone_number="+15556667778")
        self.contact_3 = Contact.objects.create(phone_number="+15556667779")
        self.contact_4 = Contact.objects.create(phone_number="+15556667780",
                                                sms_message_count=5,
                                                call_count=2,
                                                contact_count=7)

        self.phone_number_1 = PhoneNumber.objects.create(sid="PNxxx",
                                                         account_sid="ACxxx",
                                                         service_sid="SExxx",
                                                         url="http://expl.com",
                                                         e164="+15558675309",
                                                         formatted="(555) "
                                                                   "867-5309",
                                                         friendly_name="Stu.",
                                                         country_code="1",
                                                         related_sim=self.sim)
        self.phone_number_2 = PhoneNumber.objects.create(sid="PNyyy",
                                                         account_sid="ACxxx",
                                                         service_sid="SExxx",
                                                         url="http://expl.com",
                                                         e164="+15558675310",
                                                         formatted="(555) "
                                                                   "867-5309",
                                                         friendly_name="Stu.",
                                                         country_code="1",
                                                         related_sim=self.sim)
        for i in range(3):
            SmsMessage \
                .objects.create(sid="MMxxxx",
                                from_number="+15556667777",
                                to_number="+15558675309",
                                body="Test {0}.".format(i),
                                related_phone_number=self.phone_number_1,
                                related_contact=self.contact_1)

        for i in range(5):
            SmsMessage \
                .objects.create(sid="MMxxxx",
                                from_number="+15556667778",
                                to_number="+15558675310",
                                body="Test {0}.".format(i),
                                related_phone_number=self.phone_number_2,
                                related_contact=self.contact_2)

        for i in range(2):
            SmsMessage \
                .objects.create(sid="MMxxxx",
                                from_number="+15556667779",
                                to_number="+15558675309",
                                body="Test {0}.".format(i),
                                related_phone_number=self.phone_number_1,
                                related_contact=self.contact_3)
            Call \
                .objects.create(sid="CAxxxx",
                                from_number="+15556667779",
                                to_number="+15558675309",
                                related_phone_number=self.phone_number_1,
                                related_contact=self.contact_3)

    def test_calculate_number_of_contacts(self):
        out = StringIO()

        call_command('calculate_number_of_contacts', stdout=out)

        contact_1 = Contact.objects.get(phone_number="+15556667777")
        self.assertEquals(3,
                          contact_1.sms_message_count)
        self.assertEquals(0,
                          contact_1.call_count)
        self.assertEquals(3,
                          contact_1.contact_count)

        contact_2 = Contact.objects.get(phone_number="+15556667778")
        self.assertEquals(5,
                          contact_2.sms_message_count)
        self.assertEquals(0,
                          contact_2.call_count)
        self.assertEquals(5,
                          contact_2.contact_count)

        contact_3 = Contact.objects.get(phone_number="+15556667779")
        self.assertEquals(2,
                          contact_3.sms_message_count)
        self.assertEquals(2,
                          contact_3.call_count)
        self.assertEquals(4,
                          contact_3.contact_count)

        contact_4 = Contact.objects.get(phone_number="+15556667780")
        self.assertEquals(5,
                          contact_4.sms_message_count)
        self.assertEquals(2,
                          contact_4.call_count)
        self.assertEquals(7,
                          contact_4.contact_count)
