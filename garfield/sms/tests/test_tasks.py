from django.test import TestCase
from django.test import override_settings

from mock import patch

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sims.models import Sim
from voice.models import Call

from sms.models import SmsMessage

import sms.tasks


class TaskSmsMessageTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       number_type="ADV",
                                                       related_sim=self.sim)

        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.sms_message = SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            body="Test.",
                            related_phone_number=self.phone_number)

    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('sms.tasks.check_contact.apply_async')
    def test_save_sms_message_received(self,
                                       mock_check_contact,
                                       mock_check_campaign):
        sms.tasks.save_sms_message({'MessageSid': 'MMxxxx',
                                    'From': '+15556667777',
                                    'To': '+15558675309',
                                    'Body': 'Test.'})

        result = SmsMessage.objects.all().latest('date_created')

        self.assertEquals(result.body,
                          "Test.")
        self.assertEquals(result.related_phone_number,
                          self.phone_number)

        self.assertEquals(result.related_contact,
                          self.contact)
        mock_check_campaign \
            .assert_called_once_with(args=[result.related_contact.id])

        contacts = Contact.objects.all()

        self.assertEquals(len(contacts),
                          1)

    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    def test_save_sms_message_sent(self, mock_check_campaign):
        sms.tasks.save_sms_message({'MessageSid': 'MMxxxx',
                                    'From': 'sim:DExxx',
                                    'To': '+15556667777',
                                    'Body': 'Test.'})

        result = SmsMessage.objects.all().latest('date_created')

        self.assertEquals(result.body,
                          "Test.")
        self.assertEquals(result.related_phone_number,
                          self.phone_number)
        mock_check_campaign \
            .assert_called_once_with(args=[result.related_contact.id])
        contacts = Contact.objects.all()

        self.assertEquals(len(contacts),
                          1)
        self.assertEquals('+15556667777',
                          contacts[0].phone_number)

    @override_settings(TWILIO_ACCOUNT_SID='ACxxxx',
                       TWILIO_AUTH_TOKEN='yyyyyyy')
    @patch('twilio.rest.api.v2010.account.message.MessageList.create')
    def test_send_sms_message(self, mock_messages_create):
        sms.tasks.send_sms_message(from_="+15556667777",
                                   to="+15558675309",
                                   body="Test.")
        self.assertTrue(mock_messages_create.called)


class SendSMSMessageCorrectAttributionTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check):
        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       number_type="ADV",
                                                       related_sim=self.sim)

        self.det_number = PhoneNumber.objects.create(sid="PNxxx",
                                                     account_sid="ACxxx",
                                                     service_sid="SExxx",
                                                     url="http://exmple.com",
                                                     e164="+15558675310",
                                                     formatted="(555) "
                                                     "867-5310",
                                                     friendly_name="Deter.",
                                                     country_code="1",
                                                     number_type="DET",
                                                     related_sim=self.sim)

        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.sms_message = SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            body="Test.",
                            related_phone_number=self.phone_number)

        self.sms_message = SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675310",
                            body="Deterrence Response.",
                            related_phone_number=self.det_number)

    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    def test_save_sms_message_correct_attribution(self,
                                                  mock_check):
        sms.tasks.save_sms_message({'MessageSid': 'MMxxxx',
                                    'From': 'sim:DExxx',
                                    'To': '+15556667777',
                                    'Body': 'Test.'})

        result = SmsMessage.objects.all().latest('date_created')

        self.assertEquals(result.body,
                          "Test.")
        self.assertEquals(result.related_phone_number,
                          self.phone_number)
        self.assertTrue(mock_check.called)


class TaskLookupContactContactDoesNotExistTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    def setUp(self, mock_check_campaign):
        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       related_sim=self.sim)

        self.sms_message = SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            body="Test.",
                            related_phone_number=self.phone_number)

        self.call = Call.objects.create(sid="CAxxxx",
                                        from_number="+15556667777",
                                        to_number="+15558675309",
                                        related_phone_number=self.phone_number)

    @patch('sms.tasks.check_contact.apply_async')
    def test_save_sms_message_received_no_contact(self,
                                                  mock_check_contact):
        sms.tasks.save_sms_message({'MessageSid': 'MMxxxx',
                                    'From': '+15556667777',
                                    'To': '+15558675309',
                                    'Body': 'Test.'})

        result = SmsMessage.objects.all().latest('date_created')

        self.assertEquals(result.body,
                          "Test.")
        self.assertEquals(result.related_phone_number,
                          self.phone_number)

        self.assertTrue(mock_check_contact.called)

    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('sms.tasks.check_for_first_contact_to_ad.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def test_check_contact_contact_does_not_exist(self,
                                                  mock_lookup_contact,
                                                  mock_first_contact,
                                                  mock_check_campaign):
        sms.tasks.check_contact({'MessageSid': 'MMxxxx',
                                 'To': '+15558675309',
                                 'From': '+15556667777',
                                 'Body': 'Test.'})

        result = Contact.objects.all().latest('date_created')

        self.assertEquals(result.phone_number,
                          '+15556667777')
        self.assertTrue(mock_lookup_contact.called)

        message = SmsMessage.objects.get(from_number=result.phone_number)
        self.assertEquals(message.related_contact,
                          result)

    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('sms.tasks.check_for_first_contact_to_ad.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def test_check_contact_contact_does_not_exist_via_call(self,
                                                           mock_contact,
                                                           mock_first_contact,
                                                           mock_campaign):
        sms.tasks.check_contact({'CallSid': 'CAxxxx',
                                 'To': '+15558675309',
                                 'From': '+15556667777'})

        result = Contact.objects.all().latest('date_created')

        self.assertEquals(result.phone_number,
                          '+15556667777')
        self.assertTrue(mock_contact.called)

        call = Call.objects.get(from_number=result.phone_number)
        self.assertEquals(call.related_contact,
                          result)


class TaskLookupContactTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       related_sim=self.sim)
        self.saved_message = \
            SmsMessage.objects.create(from_number="+15556667777",
                                      to_number="+15558675309",
                                      body="Test.",
                                      sid="MMxxx")

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "MessageSid": "MMxxx",
                        "Body": "Test."}

    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('sms.tasks.check_for_first_contact_to_ad.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def test_check_contact(self,
                           mock_lookup_contact,
                           mock_first_contact,
                           mock_check_campaign):
        sms.tasks.check_contact(self.message)

        contact = Contact.objects.all()[0]

        mock_lookup_contact.assert_called_with(args=[self.message['From']])
        mock_check_campaign.assert_called_with(args=[contact.id])


class CheckForFirstContactToAdTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.sim = Sim.objects.create(friendly_name="TestSim",
                                      sid="DExxx",
                                      iccid="asdf",
                                      status="active",
                                      rate_plan="RExxx")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       related_sim=self.sim)

        self.phone_number_2 = PhoneNumber.objects.create(sid="PNyyy",
                                                         account_sid="ACyyy",
                                                         service_sid="SEyyy",
                                                         url="http://ele.com",
                                                         e164="+15558675310",
                                                         formatted="(555) "
                                                                   "867-5310",
                                                         friendly_name="Stf.",
                                                         country_code="1",
                                                         related_sim=self.sim)

        self.contact = Contact.objects.create(phone_number="+15556667777")

    @patch('contacts.tasks.send_whisper.apply_async')
    def test_first_contact_to_ad(self, mock_whisper):
        sms.tasks.check_for_first_contact_to_ad(self.contact.id,
                                                self.phone_number.id)
        kwargs = {'from_': self.contact.phone_number,
                  'to': self.phone_number.e164,
                  'body': "[First contact to {0}]"
                          "".format(self.phone_number.friendly_name)}
        mock_whisper.assert_called_once_with(kwargs=kwargs)
        contact = Contact.objects.get(pk=self.contact.id)
        self.assertEquals(contact.sms_message_count, 0)
        self.assertEquals(contact.contact_count, 0)

    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.send_whisper.apply_async')
    def test_second_contact_to_ad(self, mock_whisper, mock_check_campaign):
        SmsMessage.objects.create(sid="MMxxxx",
                                  from_number="+15556667777",
                                  to_number="+15558675309",
                                  body="Test.",
                                  related_phone_number=self.phone_number,
                                  related_contact=self.contact)

        SmsMessage.objects.create(sid="MMxxxx",
                                  from_number="+15556667777",
                                  to_number="+15558675309",
                                  body="Second test.",
                                  related_phone_number=self.phone_number,
                                  related_contact=self.contact)

        sms.tasks.check_for_first_contact_to_ad(self.contact.id,
                                                self.phone_number.id)
        self.assertFalse(mock_whisper.called)
        contact = Contact.objects.get(pk=self.contact.id)
        self.assertEquals(contact.sms_message_count, 2)
        self.assertEquals(contact.call_count, 0)
        self.assertEquals(contact.contact_count, 2)

    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.send_whisper.apply_async')
    def test_multiple_ads(self, mock_whisper, mock_check_campaign):
        SmsMessage.objects.create(sid="MMxxxx",
                                  from_number="+15556667777",
                                  to_number="+15558675309",
                                  body="Test.",
                                  related_phone_number=self.phone_number,
                                  related_contact=self.contact)

        SmsMessage.objects.create(sid="MMxxxy",
                                  from_number="+15556667777",
                                  to_number="+15558675310",
                                  body="Second test.",
                                  related_phone_number=self.phone_number_2,
                                  related_contact=self.contact)

        sms.tasks.check_for_first_contact_to_ad(self.contact.id,
                                                self.phone_number.id)
        self.assertTrue(mock_whisper.called)

        sms.tasks.check_for_first_contact_to_ad(self.contact.id,
                                                self.phone_number_2.id)

        self.assertEquals(mock_whisper.call_count, 2)

        contact = Contact.objects.get(pk=self.contact.id)
        self.assertEquals(contact.sms_message_count, 2)
        self.assertEquals(contact.call_count, 0)
        self.assertEquals(contact.contact_count, 2)
