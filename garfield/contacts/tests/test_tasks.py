import json

from django.test import TestCase
from django.test import override_settings
from django.core.exceptions import ObjectDoesNotExist

from mock import patch
from mock import Mock
from mock import MagicMock

from phone_numbers.models import PhoneNumber
from sims.models import Sim
from sms.models import SmsMessage

from contacts.models import Contact
import contacts.tasks


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

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}

    def test_lookup_contact_contact_does_not_exist(self):
        with self.assertRaises(ObjectDoesNotExist):
            contacts.tasks.lookup_contact("+15556667777")


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

        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('contacts.tasks.lookup_contact_whitepages.apply_async')
    def test_lookup_contact(self,
                            mock_lookup_contact_whitepages):

        mock_lookup_contact_whitepages.return_value = True

        contacts.tasks.lookup_contact(self.message["From"])

        self.assertTrue(mock_lookup_contact_whitepages.called)
        self.assertTrue((self.contact.id,),
                        mock_lookup_contact_whitepages.call_args[0])


class TaskLookupContactWhitepagesTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}

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

        self.contact.related_phone_numbers.add(self.phone_number)

        self.add_ons_person = '{"whitepages_pro_caller_id":{"code":null,' \
                              '"result":{"belongs_to":[{"link_to_phone_s' \
                              'tart_date":null,"middlename":null,"type":' \
                              '"Person","age_range":null,"name":"John Do' \
                              'e","id":"Person.xxx.Durable","firstname":' \
                              '"John","lastname":"Doe","gender":"Male"}]' \
                              ',"carrier":"AT&T","historical_addresses":' \
                              '[],"is_valid":true,"current_addresses":[{' \
                              '"state_code":"PA","city":"Johnstown","lat' \
                              '_long":{"latitude":40.328487,"accuracy":"' \
                              'RoofTop","longitude":-78.914452},"id":"Lo' \
                              'cation.xxx.Durable","street_line_2":null,' \
                              '"postal_code":"15901","location_type":"Ad' \
                              'dress","is_active":true,"zip4":null,"link' \
                              '_to_person_start_date":null,"delivery_poi' \
                              'nt":"SingleUnit","street_line_1":"123 Joh' \
                              'nny Street","country_code":"US"}],"phone_' \
                              'number":"5556667777","id":"Phone.xxx.Dura' \
                              'ble","alternate_phones":[],"is_prepaid":n' \
                              'ull,"line_type":"Mobile","warnings":[],"c' \
                              'ountry_calling_code":"1","associated_peop' \
                              'le":[],"error":null,"is_commercial":false' \
                              '},"request_sid":"xxx","status":"successfu' \
                              'l","message":null}}'

        self.add_ons_business = '{"whitepages_pro_caller_id":{"code":nul' \
                                'l,"result":{"belongs_to":[{"link_to_pho' \
                                'ne_start_date":null,"middlename":null,"' \
                                'type":"Business","age_range":null,"name' \
                                '":"The John Store","id":"Business.xxxx.' \
                                'Durable","firstname":null,"lastname":nu' \
                                'll,"gender":null}],"carrier":"Verizon",' \
                                '"historical_addresses":[],"is_valid":tr' \
                                'ue,"current_addresses":[{"state_code":"' \
                                'PA","city":"Johnstown","lat_long":{"lat' \
                                'itude":40.328487,"accuracy":"RoofTop","' \
                                'longitude":-78.914452},"id":"Location.x' \
                                'xx.Durable","street_line_2":null,"posta' \
                                'l_code":"15901","location_type":"Addres' \
                                's","is_active":null,"zip4":null,"link_t' \
                                'o_person_start_date":null,"delivery_poi' \
                                'nt":null,"street_line_1":"123 Johnny St' \
                                'reet","country_code":"US"}],"phone_numb' \
                                'er":"5556667778","id":"Phone.xxxxx.Dura' \
                                'ble","alternate_phones":[],"is_prepaid"' \
                                ':false,"line_type":"Landline","warnings' \
                                '":[],"country_calling_code":"1","associ' \
                                'ated_people":[],"error":null,"is_commer' \
                                'cial":true},"request_sid":"xxx","status' \
                                '":"successful","message":null}}'

        self.add_ons_voip = '{"whitepages_pro_caller_id":{"code":null,"r' \
                            'esult":{"belongs_to":[],"carrier":"Bandwidt' \
                            'h","historical_addresses":[],"is_valid":tru' \
                            'e,"current_addresses":[{"state_code":"PA","' \
                            'city":"Johnstown","lat_long":{"latitude":40' \
                            '.328487,"accuracy":"PostalCode","longitude"' \
                            ':-78.914452},"id":"Location.xxxx.Durable","' \
                            'street_line_2":null,"postal_code":"15901","' \
                            'location_type":"PostalCode","is_active":nul' \
                            'l,"zip4":null,"link_to_person_start_date":n' \
                            'ull,"delivery_point":null,"street_line_1":n' \
                            'ull,"country_code":"US"}],"phone_number":"5' \
                            '556667779","id":"Phone.xxx.Durable","altern' \
                            'ate_phones":[],"is_prepaid":null,"line_type' \
                            '":"NonFixedVOIP","warnings":[],"country_cal' \
                            'ling_code":"1","associated_people":[],"erro' \
                            'r":null,"is_commercial":null},"request_sid"' \
                            ':"xxxx","status":"successful","message":null}}'

    @patch('contacts.tasks.send_notification_whitepages.apply_async')
    @patch('contacts.tasks.apply_lookup_whitepages_to_contact')
    @patch('contacts.tasks.lookup_phone_number')
    def test_lookup_contact_whitepages(self,
                                       mock_lookup,
                                       mock_apply,
                                       mock_notification):
        mock_return = Mock()
        mock_return.add_ons = MagicMock()
        mock_return.add_ons.__getitem__.return_value = "successful"
        mock_lookup.return_value = mock_return

        mock_apply.return_value = self.contact

        contacts.tasks.lookup_contact_whitepages(self.contact.id)

        self.assertTrue(mock_lookup.called)
        self.assertTrue(mock_apply.called)
        self.assertTrue(mock_notification.called)

    @patch('contacts.tasks.send_notification_whitepages.apply_async')
    @patch('contacts.tasks.apply_lookup_whitepages_to_contact')
    @patch('contacts.tasks.lookup_phone_number')
    def test_lookup_contact_whitepages_failure(self,
                                               mock_lookup,
                                               mock_apply,
                                               mock_notification):
        mock_return = Mock()
        mock_return.add_ons = MagicMock()
        mock_return.add_ons.__getitem__.return_value = "failed"
        mock_lookup.return_value = mock_return

        mock_apply.return_value = self.contact

        contacts.tasks.lookup_contact_whitepages(self.contact.id)

        self.assertTrue(mock_lookup.called)
        self.assertFalse(mock_apply.called)
        self.assertFalse(mock_notification.called)

    @patch('contacts.tasks.send_whisper.apply_async')
    def test_notification_whitepages(self, mock_whisper):
        self.contact.whitepages_first_name = "Contact"
        self.contact.whitepages_middle_name = "F."
        self.contact.whitepages_last_name = "Doe"
        self.contact.whitepages_address = "123 Paper Street"
        self.contact.whitepages_address_two = "Apt. A"
        self.contact.whitepages_city = "Contactstown"
        self.contact.whitepages_state = "VA"
        self.contact.whitepages_zip_code = "55555"
        self.contact.carrier = "AT&T"
        self.contact.phone_number_type = "mobile"
        self.contact.save()

        body = contacts.tasks.send_notification_whitepages(self.contact.id,
                                                           "+15558675309")

        self.assertTrue(mock_whisper.called)
        self.assertIn("Whitepages Identity Results", body['results'][0])
        self.assertIn("Contact F. Doe", body['results'][0])
        self.assertIn("123 Paper Street", body['results'][1])
        self.assertIn("AT&T", body['results'][0])

    def test_apply_lookup_whitepages_to_contact_person(self):
        payload = json.loads(self.add_ons_person)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        mock_lookup.carrier = MagicMock()
        mock_lookup.carrier.__getitem__.return_value = "Test."
        mock_lookup.national_format.return_value = "(555) 666-7777"

        test = contacts.tasks.apply_lookup_whitepages_to_contact(self.contact,
                                                                 mock_lookup)

        self.assertTrue(test.identified)
        self.assertEqual(test.whitepages_first_name,
                         "John")
        self.assertEqual(test.whitepages_last_name,
                         "Doe")
        self.assertEqual(test.whitepages_address,
                         "123 Johnny Street")
        self.assertEqual(test.whitepages_latitude,
                         40.328487)
        self.assertEqual(test.carrier, "Test.")

    def test_apply_lookup_whitepages_to_contact_person_no_address(self):
        payload = json.loads(self.add_ons_person)

        payload['whitepages_pro_caller_id'
                ]['result']['current_addresses'] = []

        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        mock_lookup.carrier = MagicMock()
        mock_lookup.carrier.__getitem__.return_value = "Test."
        mock_lookup.national_format.return_value = "(555) 666-7777"

        test = contacts.tasks.apply_lookup_whitepages_to_contact(self.contact,
                                                                 mock_lookup)

        self.assertTrue(test.identified)
        self.assertEqual(test.whitepages_first_name,
                         "John")
        self.assertEqual(test.whitepages_last_name,
                         "Doe")
        self.assertEqual(test.whitepages_entity_type,
                         "Person")
        self.assertFalse(test.whitepages_address)
        self.assertFalse(test.whitepages_latitude)
        self.assertEqual(test.carrier, "Test.")

    def test_apply_lookup_whitepages_to_contact_person_no_belongs(self):
        payload = json.loads(self.add_ons_person)

        payload['whitepages_pro_caller_id'
                ]['result']['belongs_to'] = []

        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        mock_lookup.carrier = MagicMock()
        mock_lookup.carrier.__getitem__.return_value = "Test."
        mock_lookup.national_format.return_value = "(555) 666-7777"

        test = contacts.tasks.apply_lookup_whitepages_to_contact(self.contact,
                                                                 mock_lookup)

        self.assertTrue(test.identified)
        self.assertFalse(test.whitepages_first_name)
        self.assertFalse(test.whitepages_last_name)
        self.assertEqual(test.carrier, "Test.")

    def test_apply_lookup_whitepages_to_contact_business(self):
        payload = json.loads(self.add_ons_business)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        mock_lookup.carrier = MagicMock()
        mock_lookup.carrier.__getitem__.return_value = "Test."
        mock_lookup.national_format.return_value = "(555) 666-7777"

        test = contacts.tasks.apply_lookup_whitepages_to_contact(self.contact,
                                                                 mock_lookup)

        self.assertTrue(test.identified)
        self.assertEqual(test.whitepages_entity_type,
                         "Business")
        self.assertEqual(test.whitepages_business_name,
                         "The John Store")
        self.assertEqual(test.whitepages_address,
                         "123 Johnny Street")
        self.assertEqual(test.whitepages_latitude,
                         40.328487)
        self.assertEqual(test.carrier, "Test.")

    def test_apply_lookup_whitepages_to_contact_voip(self):
        payload = json.loads(self.add_ons_voip)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        mock_lookup.carrier = MagicMock()
        mock_lookup.carrier.__getitem__.return_value = "Test."
        mock_lookup.national_format.return_value = "(555) 666-7777"

        test = contacts.tasks.apply_lookup_whitepages_to_contact(self.contact,
                                                                 mock_lookup)

        self.assertTrue(test.identified)
        self.assertFalse(test.whitepages_first_name)
        self.assertFalse(test.whitepages_address)
        self.assertEqual(test.whitepages_latitude,
                         40.328487)
        self.assertEqual(test.carrier, "Test.")
        self.assertEqual(test.whitepages_phone_type, "NonFixedVOIP")
        self.assertEqual(test.phone_number_type, "Test.")


class TaskContactsWhisperTestCase(TestCase):
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

        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.sms_message = SmsMessage \
            .objects.create(sid="MMxxxx",
                            from_number="+15556667777",
                            to_number="+15558675309",
                            body="Test.",
                            related_phone_number=self.phone_number)

    @override_settings(TWILIO_ACCOUNT_SID='ACxxxx',
                       TWILIO_AUTH_TOKEN='yyyyyyy',
                       TWILIO_PHONE_NUMBER='+15558675309')
    @patch('twilio.rest.api.v2010.account.message.MessageList.create')
    def test_send_whisper(self, mock_messages_create):
        test_json = json.dumps({"From": "+15556667777",
                                "To": "+1555867309",
                                "Body": "Test."})

        contacts.tasks.send_whisper(from_="+15556667777",
                                    to="+15558675309",
                                    body="Test.")

        mock_messages_create.called_with(from_="+15556667777",
                                         to="+15558675309",
                                         body="whisper:{0}".format(test_json))


@override_settings(TWILIO_ACCOUNT_SID='ACxxxx',
                   TWILIO_AUTH_TOKEN='yyyyyyy')
class TaskUtilitiesTestCase(TestCase):
    @patch('twilio.rest.lookups.v1.phone_number.PhoneNumberContext')
    def test_lookup_phone_number(self, mock_context):
        contacts.tasks.lookup_phone_number("+15556667777")

        self.assertTrue(mock_context.called)
