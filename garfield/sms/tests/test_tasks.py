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
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup):
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

        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.sms_message = SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            body="Test.",
                            related_phone_number=self.phone_number)

    @patch('sms.tasks.check_contact.apply_async')
    def test_save_sms_message_received(self, mock_check_contact):
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

    def test_save_sms_message_sent(self):
        sms.tasks.save_sms_message({'MessageSid': 'MMxxxx',
                                    'From': 'sim:DExxx',
                                    'To': '+15556667777',
                                    'Body': 'Test.'})

        result = SmsMessage.objects.all().latest('date_created')

        self.assertEquals(result.body,
                          "Test.")
        self.assertEquals(result.related_phone_number,
                          self.phone_number)

    @override_settings(TWILIO_ACCOUNT_SID='ACxxxx',
                       TWILIO_AUTH_TOKEN='yyyyyyy')
    @patch('twilio.rest.api.v2010.account.message.MessageList.create')
    def test_send_sms_message(self, mock_messages_create):
        sms.tasks.send_sms_message(from_="+15556667777",
                                   to="+15558675309",
                                   body="Test.")
        self.assertTrue(mock_messages_create.called)


class TaskLookupContactContactDoesNotExistTestCase(TestCase):
    def setUp(self):
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

    @patch('sms.tasks.check_for_first_contact_to_ad.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def test_check_contact_contact_does_not_exist(self,
                                                  mock_lookup_contact,
                                                  mock_first_contact):
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

    @patch('sms.tasks.check_for_first_contact_to_ad.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def test_check_contact_contact_does_not_exist_via_call(self,
                                                           mock_contact,
                                                           mock_first_contact):
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
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup):
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

    @patch('sms.tasks.check_for_first_contact_to_ad.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def test_check_contact(self, mock_lookup_contact, mock_first_contact):
        sms.tasks.check_contact(self.message)

        mock_lookup_contact.assert_called_with(args=[self.message['From']])


class CheckForFirstContactToAdTestCase(TestCase):
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup):
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
                                                         url="http://exmle.com",
                                                         e164="+15558675310",
                                                         formatted="(555) "
                                                                   "867-5310",
                                                         friendly_name="Stuff.",
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

    @patch('contacts.tasks.send_whisper.apply_async')
    def test_second_contact_to_ad(self, mock_whisper):
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

    @patch('contacts.tasks.send_whisper.apply_async')
    def test_multiple_ads(self, mock_whisper):
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


@override_settings(TWILIO_PHONE_NUMBER="+18881112222")
class DeterrenceTestCase(TestCase):
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup):
        self.contact_a = Contact.objects.create(phone_number="+15556667777")
        self.contact_b = Contact.objects.create(phone_number="+15556667778")
        self.contact_c = Contact.objects.create(phone_number="+15556667779")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       number_type="ADV",
                                                       country_code="1")

        self.det_number = PhoneNumber.objects.create(sid="PNyyy",
                                                     account_sid="ACxxx",
                                                     service_sid="SExxx",
                                                     url="http://exmple.com",
                                                     e164="+15558675310",
                                                     formatted="(555) "
                                                               "867-5310",
                                                     friendly_name="Stuff.",
                                                     number_type="DET",
                                                     country_code="1")

        self.contact_a.related_phone_numbers.add(self.phone_number)
        self.contact_b.related_phone_numbers.add(self.phone_number)
        self.contact_c.related_phone_numbers.add(self.phone_number)

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}
        self.deterrence_file_path = "https://berserk-sleet-3229.twil.io/" \
                                    "assets/john_deterrent.jpg"

    @patch('sms.tasks.send_sms_message.apply_async')
    def test_send_deterrence(self, mock_sms_message):
        sms.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(3, mock_sms_message.call_count)
        for call in mock_sms_message.call_args_list:
            args, kwargs = call
            self.assertEquals(kwargs['kwargs']['media_url'],
                              self.deterrence_file_path)
            self.assertEquals(kwargs['kwargs']['from_'],
                              self.det_number.e164)

        for contact in self.phone_number.contact_set.all():
            self.assertTrue(contact.deterred)

    @patch('sms.tasks.send_sms_message.apply_async')
    def test_send_deterrence_do_not_deter(self, mock_sms_message):
        self.contact_a.do_not_deter = True
        self.contact_a.save()

        sms.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(2, mock_sms_message.call_count)
        self.assertFalse(self.phone_number.contact_set.all()[0].deterred)

    @patch('sms.tasks.send_sms_message.apply_async')
    def test_send_deterrence_deterred(self, mock_sms_message):
        self.contact_a.deterred = True
        self.contact_a.save()

        sms.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(2, mock_sms_message.call_count)

    @patch('sms.tasks.send_sms_message.apply_async')
    def test_send_deterrence_arrested(self, mock_sms_message):
        self.contact_a.arrested = True
        self.contact_a.save()

        sms.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(2, mock_sms_message.call_count)

    @patch('sms.tasks.send_sms_message.apply_async')
    def test_send_deterrence_recruiter(self, mock_sms_message):
        self.contact_a.recruiter = True
        self.contact_a.save()

        sms.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(2, mock_sms_message.call_count)

    @patch('sms.tasks.send_sms_message.apply_async')
    def test_send_deterrence_first_name(self, mock_sms_message):
        self.contact_a.whitepages_first_name = "John"
        self.contact_a.save()

        sms.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(3, mock_sms_message.call_count)
        for contact in self.phone_number.contact_set.all():
            self.assertTrue(contact.deterred)


class DeterrenceTestCaseMultipleNumbers(TestCase):
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup):
        self.contact_a = Contact.objects.create(phone_number="+15556667777")
        self.contact_b = Contact.objects.create(phone_number="+15556667778")
        self.contact_c = Contact.objects.create(phone_number="+15556667779")

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5308",
                                                       friendly_name="Stuff.",
                                                       number_type="ADV",
                                                       country_code="1")

        self.det_number_1 = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       number_type="DET",
                                                       country_code="1")

        self.det_number_2 = PhoneNumber.objects.create(sid="PNyyy",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675310",
                                                       formatted="(555) "
                                                                 "867-5310",
                                                       friendly_name="Stuff.",
                                                       number_type="DET",
                                                       country_code="1")

        self.contact_a.related_phone_numbers.add(self.phone_number)
        self.contact_b.related_phone_numbers.add(self.phone_number)
        self.contact_c.related_phone_numbers.add(self.phone_number)

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}
        self.deterrence_file_path = "https://berserk-sleet-3229.twil.io/" \
                                    "assets/john_deterrent.jpg"

    @patch('sms.tasks.send_sms_message.apply_async')
    def test_send_deterrence(self, mock_sms_message):
        sms.tasks.send_deterrence("http://example.com", self.message)

        self.assertEquals(3, mock_sms_message.call_count)
        for call in mock_sms_message.call_args_list:
            args, kwargs = call
            self.assertEquals(kwargs['kwargs']['media_url'],
                              self.deterrence_file_path)
            self.assertEquals(kwargs['kwargs']['from_'],
                              self.det_number_2.e164)

        for contact in self.phone_number.contact_set.all():
            self.assertTrue(contact.deterred)
