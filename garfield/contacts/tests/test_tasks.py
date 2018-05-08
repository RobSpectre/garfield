import json

from django.test import TestCase
from django.test import override_settings
from django.core.exceptions import ObjectDoesNotExist

from mock import patch
from mock import Mock
from mock import MagicMock

import responses

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
    @patch('contacts.tasks.lookup_contact_tellfinder.apply_async')
    @patch('contacts.tasks.lookup_contact_nextcaller.apply_async')
    @patch('contacts.tasks.lookup_contact_whitepages.apply_async')
    def test_lookup_contact(self,
                            mock_lookup_contact_whitepages,
                            mock_lookup_contact_nextcaller,
                            mock_lookup_contact_tellfinder):

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
        self.assertEquals(test.whitepages_first_name,
                          "John")
        self.assertEquals(test.whitepages_last_name,
                          "Doe")
        self.assertEquals(test.whitepages_address,
                          "123 Johnny Street")
        self.assertEquals(test.whitepages_latitude,
                          40.328487)
        self.assertEquals(test.carrier, "Test.")

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
        self.assertEquals(test.whitepages_first_name,
                          "John")
        self.assertEquals(test.whitepages_last_name,
                          "Doe")
        self.assertEquals(test.whitepages_entity_type,
                          "Person")
        self.assertFalse(test.whitepages_address)
        self.assertFalse(test.whitepages_latitude)
        self.assertEquals(test.carrier, "Test.")

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
        self.assertEquals(test.carrier, "Test.")

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
        self.assertEquals(test.whitepages_entity_type,
                          "Business")
        self.assertEquals(test.whitepages_business_name,
                          "The John Store")
        self.assertEquals(test.whitepages_address,
                          "123 Johnny Street")
        self.assertEquals(test.whitepages_latitude,
                          40.328487)
        self.assertEquals(test.carrier, "Test.")

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
        self.assertEquals(test.whitepages_latitude,
                          40.328487)
        self.assertEquals(test.carrier, "Test.")
        self.assertEquals(test.whitepages_phone_type, "NonFixedVOIP")
        self.assertEquals(test.phone_number_type, "Test.")


class TaskLookupContactNextCallerTestCase(TestCase):
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

        self.add_on_person = '{"nextcaller_advanced_caller_id":{"code' \
                             '":null,"result":{"records":[{"age":"","' \
                             'relatives":[],"education":"Completed Hi' \
                             'gh School","high_net_worth":"Yes","presenc' \
                             'e_of_children":"Yes","middle_name":"","' \
                             'marital_status":"Single","first_name":"' \
                             'John","home_owner_status":"Own","gender' \
                             '":"Male","occupation":"Professional","l' \
                             'ength_of_residence":"11-15 years","last' \
                             '_name":"Doe","email":"johndoe@john.com"' \
                             ',"telco_zip":"","address":[{"line1":"12' \
                             '3 Johnny Street","country":"USA","city"' \
                             ':"Johnstown","home_data":null,"line2":"' \
                             '","extended_zip":"","state":"PA","zip_c' \
                             'ode":"15901"}],"household_income":"125k' \
                             '-150k","id":"x","telco_zip_4":"","marke' \
                             't_value":"500k-1mm","linked_emails":[],' \
                             '"name":"John Doe","first_pronounced":"J' \
                             'AWN","phone":[{"line_type":"Mobile","ca' \
                             'rrier":"At&t Wireless","number":"555666' \
                             '7777"}],"social_links":[{"followers":0,' \
                             '"type":"facebook","url":"https://www.fa' \
                             'cebook.com/johndoe"},{"followers":0, "t' \
                             'ype":"twitter","url":"https://www.twitt' \
                             'er.com/johndoe"},{"followers":0, "type"' \
                             ':"linkedin","url":"https://www.linked.c' \
                             'om/johndoe"}]}]},"request_sid":' \
                             '"x","status":"successful","message":null}}'

        self.add_on_business = '{"nextcaller_advanced_caller_id":{"co' \
                               'de":null,"result":{"records":[{"age":' \
                               '"","relatives":[],"education":"","hig' \
                               'h_net_worth":"","presence_of_children' \
                               '":"","middle_name":"","marital_status' \
                               '":"","first_name":"","home_owner_stat' \
                               'us":"","gender":"Male","occupation":"' \
                               '","length_of_residence":"","last_name' \
                               '":"","email":"","telco_zip":"95101","' \
                               'address":[{"line1":"123 Contactny Street' \
                               '","country":"USA","city":"Contactstown",' \
                               '"home_data":null,"line2":"","extended' \
                               '_zip":"","state":"PA","zip_code":"159' \
                               '01"}],"household_income":"","id":"x",' \
                               '"telco_zip_4":"","market_value":"","l' \
                               'inked_emails":[],"name":"The Contact Sto' \
                               're","first_pronounced":"JAWN","phone"' \
                               ':[{"line_type":"Landline","carrier":"' \
                               'Verizon","number":"5556667778"}],"soc' \
                               'ial_links":[]}]},"request_sid":"x","s' \
                               'tatus":"successful","message":null}}'

        self.add_on_voip = '{"nextcaller_advanced_caller_id":{"code":' \
                           'null,"result":{"records":[{"age":"","rela' \
                           'tives":[],"education":"","high_net_worth"' \
                           ':"","presence_of_children":"","middle_nam' \
                           'e":"","marital_status":"","first_name":""' \
                           ',"home_owner_status":"","gender":"","occu' \
                           'pation":"","length_of_residence":"","last' \
                           '_name":"","email":"","telco_zip":"15901",' \
                           '"address":[],"household_income":"","id":"' \
                           'x","telco_zip_4":"","market_value":"","li' \
                           'nked_emails":[],"name":"","first_pronounc' \
                           'ed":"","phone":[{"line_type":"Landline","' \
                           'carrier":"Level 3 Communications Llc ","n' \
                           'umber":"5556667779"}],"social_links":[]}]' \
                           '},"request_sid":"x","status":"successful"' \
                           ',"message":null}}'

    @patch('contacts.tasks.send_notification_nextcaller.apply_async')
    @patch('contacts.tasks.apply_lookup_nextcaller_to_contact')
    @patch('contacts.tasks.lookup_phone_number')
    def test_lookup_contact_nextcaller(self,
                                       mock_lookup,
                                       mock_apply,
                                       mock_notification):
        mock_return = Mock()
        mock_return.add_ons = MagicMock()
        mock_return.add_ons.__getitem__.return_value = "successful"
        mock_lookup.return_value = mock_return

        mock_apply.return_value = self.contact

        contacts.tasks.lookup_contact_nextcaller(self.contact.id)

        self.assertTrue(mock_lookup.called)
        self.assertTrue(mock_apply.called)
        self.assertTrue(mock_notification.called)

    @patch('contacts.tasks.send_notification_nextcaller.apply_async')
    @patch('contacts.tasks.apply_lookup_nextcaller_to_contact')
    @patch('contacts.tasks.lookup_phone_number')
    def test_lookup_contact_nextcaller_unsuccessful(self,
                                                    mock_lookup,
                                                    mock_apply,
                                                    mock_notification):
        mock_return = Mock()
        mock_return.add_ons = MagicMock()
        mock_return.add_ons.__getitem__.return_value = "failure"
        mock_lookup.return_value = mock_return

        mock_apply.return_value = self.contact

        contacts.tasks.lookup_contact_nextcaller(self.contact.id)

        self.assertTrue(mock_lookup.called)
        self.assertFalse(mock_apply.called)
        self.assertFalse(mock_notification.called)

    def test_apply_lookup_nextcaller_to_contact_person(self):
        payload = json.loads(self.add_on_person)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        test = contacts.tasks.apply_lookup_nextcaller_to_contact(self.contact,
                                                                 mock_lookup)

        test.save()

        self.assertTrue(test.identified)
        self.assertEquals(test.nextcaller_first_name,
                          "John")
        self.assertEquals(test.nextcaller_last_name,
                          "Doe")
        self.assertEquals(test.nextcaller_address,
                          "123 Johnny Street")
        self.assertEquals(test.nextcaller_email,
                          "johndoe@john.com")

    def test_apply_lookup_nextcaller_to_contact_person_no_records(self):
        payload = json.loads(self.add_on_person)

        payload['nextcaller_advanced_caller_id'
                ]['result']['records'] = []

        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        test = contacts.tasks.apply_lookup_nextcaller_to_contact(self.contact,
                                                                 mock_lookup)

        self.assertFalse(test.identified)

    def test_apply_lookup_nextcaller_to_contact_business(self):
        payload = json.loads(self.add_on_business)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        test = contacts.tasks.apply_lookup_nextcaller_to_contact(self.contact,
                                                                 mock_lookup)

        self.assertTrue(test.identified)
        self.assertEquals(test.nextcaller_business_name,
                          "The Contact Store")

    def test_apply_lookup_nextcaller_to_contact_voip(self):
        payload = json.loads(self.add_on_voip)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        test = contacts.tasks.apply_lookup_nextcaller_to_contact(self.contact,
                                                                 mock_lookup)

        self.assertTrue(test.identified)
        self.assertEquals(test.nextcaller_carrier,
                          "Level 3 Communications Llc ")

    @patch('contacts.tasks.send_whisper.apply_async')
    def test_notification_nextcaller(self, mock_whisper):
        self.contact.nextcaller_first_name = "John"
        self.contact.nextcaller_middle_name = "F."
        self.contact.nextcaller_last_name = "Doe"
        self.contact.nextcaller_address = "123 Paper Street"
        self.contact.nextcaller_address_two = "Apt. A"
        self.contact.nextcaller_city = "Johnstown"
        self.contact.nextcaller_state = "PA"
        self.contact.nextcaller_zip_code = "55555"
        self.contact.save()

        body = contacts.tasks.send_notification_nextcaller(self.contact.id,
                                                           "+15558675309")

        self.assertTrue(mock_whisper.called)
        self.assertIn("NextCaller Identity Results", body['results'][0])
        self.assertIn("John F. Doe", body['results'][0])
        self.assertIn("123 Paper Street", body['results'][1])


@override_settings(TELLFINDER_API_KEY="xxx")
class TaskLookupContactTellfinderTestCase(TestCase):
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

        self.tellfinder_positive_result = '{"took":52,"facets":[{"cardinal' \
                                          'ity":null,"friendlyName":"Post ' \
                                          'Time","values":[{"standardDev":' \
                                          'null,"selected":null,"mean":nul' \
                                          'l,"selectedTimeseries":null,"pr' \
                                          'evRank":0,"filter":false,"curRa' \
                                          'nk":0,"key":"posttime","expansi' \
                                          'on":false,"value":"2012-01-01T0' \
                                          '0:00:00Z","timeseries":[],"coun' \
                                          't":1},{"standardDev":null,"sele' \
                                          'cted":null,"mean":null,"selecte' \
                                          'dTimeseries":null,"prevRank":0,' \
                                          '"filter":false,"curRank":0,"key' \
                                          '":"posttime","expansion":false,' \
                                          '"value":"2013-01-01T00:00:00Z",' \
                                          '"timeseries":[],"count":0},{"st' \
                                          'andardDev":null,"selected":null' \
                                          ',"mean":null,"selectedTimeserie' \
                                          's":null,"prevRank":0,"filter":f' \
                                          'alse,"curRank":0,"key":"posttim' \
                                          'e","expansion":false,"value":"2' \
                                          '014-01-01T00:00:00Z","timeserie' \
                                          's":[],"count":30}],"otherDocCou' \
                                          'nt":0,"key":"posttime","tags":[' \
                                          '"STRING","DATE","ARRAY","FACET"' \
                                          ',"PRIMARY_DATE","SORTABLE"],"me' \
                                          'trics":{"max":"2014-11-01","sel' \
                                          'ectedMin":null,"min":"2012-08-1' \
                                          '1","selectedMax":null,"avg":nul' \
                                          'l,"selectedAvg":null}}],"expans' \
                                          'ionResults":[{"standardDev":nul' \
                                          'l,"selected":null,"mean":null,"' \
                                          'selectedTimeseries":null,"prevR' \
                                          'ank":0,"filter":false,"curRank"' \
                                          ':0,"key":null,"expansion":false' \
                                          ',"value":"phone:xxx","timeserie' \
                                          's":null,"count":31}],"total":31}'

        self.tellfinder_negative_result = {'total': 0}

    @responses.activate
    @patch('contacts.tasks.send_whisper.apply_async')
    @patch('contacts.tasks.send_notification_tellfinder.apply_async')
    def test_lookup_contact_tellfinder(self, mock_notification, mock_whisper):
        responses.add(responses.GET,
                      "https://api.tellfinder.com/facets"
                      "?q=phone:+15556667777&keys[]=posttime",
                      json=json.loads(self.tellfinder_positive_result),
                      status=200)

        test = contacts.tasks.lookup_contact_tellfinder(self.contact.id)

        self.assertEquals(len(responses.calls), 1)
        self.assertTrue(mock_notification.called)
        self.assertFalse(mock_whisper.called)
        self.assertEquals(test['total'], 31)

    @responses.activate
    @patch('contacts.tasks.send_whisper.apply_async')
    @patch('contacts.tasks.send_notification_tellfinder.apply_async')
    def test_lookup_contact_tellfinder_negative_results(self,
                                                        mock_notification,
                                                        mock_whisper):
        responses.add(responses.GET,
                      "https://api.tellfinder.com/facets"
                      "?q=phone:+15556667777&keys[]=posttime",
                      json=self.tellfinder_negative_result,
                      status=200)

        contacts.tasks.lookup_contact_tellfinder(self.contact.id)

        self.assertEquals(len(responses.calls), 1)
        self.assertFalse(mock_notification.called)
        self.assertFalse(mock_whisper.called)

    @patch('contacts.tasks.send_whisper.apply_async')
    def test_send_notification_tellfinder(self, mock_whisper):
        test_dict = {"Total": 31,
                     "Earliest Ad": "1955-11-15",
                     "Latest Ad": "2017-02-05"}

        contacts.tasks.send_notification_tellfinder(test_dict,
                                                    self.contact.id,
                                                    "+15558675309")

        self.assertTrue(mock_whisper.called)


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
