import json

from django.test import TestCase
from django.test import override_settings
from django.core.exceptions import ObjectDoesNotExist

from mock import patch
from mock import Mock
from mock import MagicMock

import responses

from johns.models import John
from phone_numbers.models import PhoneNumber
from sims.models import Sim

from sms.models import SmsMessage

import sms.tasks


class TaskSmsMessageTestCase(TestCase):
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

    @patch('sms.tasks.check_john.apply_async')
    def test_save_sms_message_received(self, mock_check_john):
        sms.tasks.save_sms_message({'MessageSid': 'MMxxxx',
                                    'From': '+15556667777',
                                    'To': '+15558675309',
                                    'Body': 'Test.'})

        result = SmsMessage.objects.all().latest('date_created')

        self.assertEquals(result.body,
                          "Test.")
        self.assertEquals(result.related_phone_number,
                          self.phone_number)

        self.assertTrue(mock_check_john.called)

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

    @override_settings(TWILIO_ACCOUNT_SID='ACxxxx',
                       TWILIO_AUTH_TOKEN='yyyyyyy',
                       TWILIO_WHISPER_NUMBER='+15556667777',
                       TWILIO_PHONE_NUMBER='+15558675309')
    @patch('twilio.rest.api.v2010.account.message.MessageList.create')
    def test_send_whisper(self, mock_messages_create):
        test_json = json.dumps({"From": "+15556667778",
                                "To": "+1555867310",
                                "Body": "Test."})

        sms.tasks.send_whisper(from_="+15556667778",
                               to="+15558675310",
                               body="Test.")

        mock_messages_create.called_with(from_="+15556667777",
                                         to="+15558675309",
                                         body="whisper:{0}".format(test_json))


class TaskLookupJohnJohnDoesNotExistTestCase(TestCase):
    @patch('sms.tasks.lookup_john.apply_async')
    def test_check_john_john_does_not_exist(self, mock_lookup_john):
        sms.tasks.check_john({'MessageSid': 'MMxxxx',
                              'To': '+15558675309',
                              'From': '+15556667777',
                              'Body': 'Test.'})

        result = John.objects.all().latest('date_created')

        self.assertEquals(result.phone_number,
                          '+15556667777')
        self.assertTrue(mock_lookup_john.called)

    def test_lookup_john_john_does_not_exist(self):
        with self.assertRaises(ObjectDoesNotExist):
            sms.tasks.lookup_john("+15556667777", "+15558675309")


class TaskLookupJohnTestCase(TestCase):
    def setUp(self):
        self.john = John.objects.create(phone_number="+15556667777")

        self.message = {"From": "+15556667777",
                        "To": "+15558675309",
                        "Body": "Test."}

    @patch('sms.tasks.lookup_john.apply_async')
    def test_check_john(self, mock_lookup_john):
        sms.tasks.check_john(self.message)

        mock_lookup_john.assert_called_with(args=[self.message['From'],
                                                  self.message['To']])

    @patch('sms.tasks.lookup_john.apply_async')
    def test_check_john_already_identified(self, mock_lookup_john):
        self.john.identified = True
        self.john.save()

        self.assertFalse(mock_lookup_john.called)

    @patch('sms.tasks.lookup_john_tellfinder.apply_async')
    @patch('sms.tasks.lookup_john_nextcaller.apply_async')
    @patch('sms.tasks.lookup_john_whitepages.apply_async')
    def test_lookup_john(self,
                         mock_lookup_john_whitepages,
                         mock_lookup_john_nextcaller,
                         mock_lookup_john_tellfinder):
        sms.tasks.lookup_john(self.message["From"],
                              self.message["To"])

        mock_lookup_john_whitepages \
            .assert_called_with(args=[self.john.id,
                                      self.message['To']])
        mock_lookup_john_nextcaller \
            .assert_called_with(args=[self.john.id,
                                      self.message['To']])
        mock_lookup_john_tellfinder \
            .assert_called_with(args=[self.john.id,
                                      self.message['To']])


class TaskLookupJohnWhitepagesTestCase(TestCase):
    def setUp(self):
        self.john = John.objects.create(phone_number="+15556667777")

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

    @patch('sms.tasks.send_notification_whitepages.apply_async')
    @patch('sms.tasks.apply_lookup_whitepages_to_john')
    @patch('sms.tasks.lookup_phone_number')
    def test_lookup_john_whitepages(self,
                                    mock_lookup,
                                    mock_apply,
                                    mock_notification):
        mock_return = Mock()
        mock_return.add_ons = MagicMock()
        mock_return.add_ons.__getitem__.return_value = "successful"
        mock_lookup.return_value = mock_return

        mock_apply.return_value = self.john

        sms.tasks.lookup_john_whitepages(self.john.id, "+15558675309")

        self.assertTrue(mock_lookup.called)
        self.assertTrue(mock_apply.called)
        self.assertTrue(mock_notification.called)

    @patch('sms.tasks.send_notification_whitepages.apply_async')
    @patch('sms.tasks.apply_lookup_whitepages_to_john')
    @patch('sms.tasks.lookup_phone_number')
    def test_lookup_john_whitepages_failure(self,
                                            mock_lookup,
                                            mock_apply,
                                            mock_notification):
        mock_return = Mock()
        mock_return.add_ons = MagicMock()
        mock_return.add_ons.__getitem__.return_value = "failed"
        mock_lookup.return_value = mock_return

        mock_apply.return_value = self.john

        sms.tasks.lookup_john_whitepages(self.john.id, "+15558675309")

        self.assertTrue(mock_lookup.called)
        self.assertFalse(mock_apply.called)
        self.assertFalse(mock_notification.called)

    @patch('sms.tasks.send_whisper.apply_async')
    def test_notification_whitepages(self, mock_whisper):
        self.john.whitepages_first_name = "John"
        self.john.whitepages_middle_name = "F."
        self.john.whitepages_last_name = "Doe"
        self.john.whitepages_address = "123 Paper Street"
        self.john.whitepages_address_two = "Apt. A"
        self.john.whitepages_city = "Johnstown"
        self.john.whitepages_state = "VA"
        self.john.whitepages_zip_code = "55555"
        self.john.carrier = "AT&T"
        self.john.phone_number_type = "mobile"
        self.john.save()

        body = sms.tasks.send_notification_whitepages(self.john.id,
                                                      "+15558675309")

        self.assertTrue(mock_whisper.called)
        self.assertIn("Whitepages Results", body)
        self.assertIn("John F. Doe", body)
        self.assertIn("123 Paper Street", body)
        self.assertIn("AT&T", body)

    def test_apply_lookup_whitepages_to_john_person(self):
        payload = json.loads(self.add_ons_person)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        mock_lookup.carrier = MagicMock()
        mock_lookup.carrier.__getitem__.return_value = "Test."
        mock_lookup.national_format.return_value = "(555) 666-7777"

        test = sms.tasks.apply_lookup_whitepages_to_john(self.john,
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

    def test_apply_lookup_whitepages_to_john_person_no_address(self):
        payload = json.loads(self.add_ons_person)

        payload['whitepages_pro_caller_id'
                ]['result']['current_addresses'] = []

        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        mock_lookup.carrier = MagicMock()
        mock_lookup.carrier.__getitem__.return_value = "Test."
        mock_lookup.national_format.return_value = "(555) 666-7777"

        test = sms.tasks.apply_lookup_whitepages_to_john(self.john,
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

    def test_apply_lookup_whitepages_to_john_person_no_belongs(self):
        payload = json.loads(self.add_ons_person)

        payload['whitepages_pro_caller_id'
                ]['result']['belongs_to'] = []

        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        mock_lookup.carrier = MagicMock()
        mock_lookup.carrier.__getitem__.return_value = "Test."
        mock_lookup.national_format.return_value = "(555) 666-7777"

        test = sms.tasks.apply_lookup_whitepages_to_john(self.john,
                                                         mock_lookup)

        self.assertTrue(test.identified)
        self.assertFalse(test.whitepages_first_name)
        self.assertFalse(test.whitepages_last_name)
        self.assertEquals(test.carrier, "Test.")

    def test_apply_lookup_whitepages_to_john_business(self):
        payload = json.loads(self.add_ons_business)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        mock_lookup.carrier = MagicMock()
        mock_lookup.carrier.__getitem__.return_value = "Test."
        mock_lookup.national_format.return_value = "(555) 666-7777"

        test = sms.tasks.apply_lookup_whitepages_to_john(self.john,
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

    def test_apply_lookup_whitepages_to_john_voip(self):
        payload = json.loads(self.add_ons_voip)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        mock_lookup.carrier = MagicMock()
        mock_lookup.carrier.__getitem__.return_value = "Test."
        mock_lookup.national_format.return_value = "(555) 666-7777"

        test = sms.tasks.apply_lookup_whitepages_to_john(self.john,
                                                         mock_lookup)

        self.assertTrue(test.identified)
        self.assertFalse(test.whitepages_first_name)
        self.assertFalse(test.whitepages_address)
        self.assertEquals(test.whitepages_latitude,
                          40.328487)
        self.assertEquals(test.carrier, "Test.")
        self.assertEquals(test.whitepages_phone_type, "NonFixedVOIP")
        self.assertEquals(test.phone_number_type, "Test.")


class TaskLookupJohnNextCallerTestCase(TestCase):
    def setUp(self):
        self.john = John.objects.create(phone_number="+15556667777")

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
                               'address":[{"line1":"123 Johnny Street' \
                               '","country":"USA","city":"Johnstown",' \
                               '"home_data":null,"line2":"","extended' \
                               '_zip":"","state":"PA","zip_code":"159' \
                               '01"}],"household_income":"","id":"x",' \
                               '"telco_zip_4":"","market_value":"","l' \
                               'inked_emails":[],"name":"The John Sto' \
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

    @patch('sms.tasks.send_notification_nextcaller.apply_async')
    @patch('sms.tasks.apply_lookup_nextcaller_to_john')
    @patch('sms.tasks.lookup_phone_number')
    def test_lookup_john_nextcaller(self,
                                    mock_lookup,
                                    mock_apply,
                                    mock_notification):
        mock_return = Mock()
        mock_return.add_ons = MagicMock()
        mock_return.add_ons.__getitem__.return_value = "successful"
        mock_lookup.return_value = mock_return

        mock_apply.return_value = self.john

        sms.tasks.lookup_john_nextcaller(self.john.id, "+15558675309")

        self.assertTrue(mock_lookup.called)
        self.assertTrue(mock_apply.called)
        self.assertTrue(mock_notification.called)

    @patch('sms.tasks.send_notification_nextcaller.apply_async')
    @patch('sms.tasks.apply_lookup_nextcaller_to_john')
    @patch('sms.tasks.lookup_phone_number')
    def test_lookup_john_nextcaller_unsuccessful(self,
                                                 mock_lookup,
                                                 mock_apply,
                                                 mock_notification):
        mock_return = Mock()
        mock_return.add_ons = MagicMock()
        mock_return.add_ons.__getitem__.return_value = "failure"
        mock_lookup.return_value = mock_return

        mock_apply.return_value = self.john

        sms.tasks.lookup_john_nextcaller(self.john.id, "+15558675309")

        self.assertTrue(mock_lookup.called)
        self.assertFalse(mock_apply.called)
        self.assertFalse(mock_notification.called)

    def test_apply_lookup_nextcaller_to_john_person(self):
        payload = json.loads(self.add_on_person)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        test = sms.tasks.apply_lookup_nextcaller_to_john(self.john,
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

    def test_apply_lookup_nextcaller_to_john_person_no_records(self):
        payload = json.loads(self.add_on_person)

        payload['nextcaller_advanced_caller_id'
                ]['result']['records'] = []

        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        test = sms.tasks.apply_lookup_nextcaller_to_john(self.john,
                                                         mock_lookup)

        self.assertFalse(test.identified)

    def test_apply_lookup_nextcaller_to_john_business(self):
        payload = json.loads(self.add_on_business)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        test = sms.tasks.apply_lookup_nextcaller_to_john(self.john,
                                                         mock_lookup)

        self.assertTrue(test.identified)
        self.assertEquals(test.nextcaller_business_name,
                          "The John Store")

    def test_apply_lookup_nextcaller_to_john_voip(self):
        payload = json.loads(self.add_on_voip)
        mock_lookup = Mock()
        mock_lookup.add_ons = MagicMock()
        mock_lookup.add_ons.__getitem__.return_value = payload

        test = sms.tasks.apply_lookup_nextcaller_to_john(self.john,
                                                         mock_lookup)

        self.assertTrue(test.identified)
        self.assertEquals(test.nextcaller_carrier,
                          "Level 3 Communications Llc ")

    @patch('sms.tasks.send_whisper.apply_async')
    def test_notification_nextcaller(self, mock_whisper):
        self.john.nextcaller_first_name = "John"
        self.john.nextcaller_middle_name = "F."
        self.john.nextcaller_last_name = "Doe"
        self.john.nextcaller_address = "123 Paper Street"
        self.john.nextcaller_address_two = "Apt. A"
        self.john.nextcaller_city = "Johnstown"
        self.john.nextcaller_state = "VA"
        self.john.nextcaller_zip_code = "55555"
        self.john.save()

        body = sms.tasks.send_notification_nextcaller(self.john.id,
                                                      "+15558675309")

        self.assertTrue(mock_whisper.called)
        self.assertIn("NextCaller Results", body)
        self.assertIn("John F. Doe", body)
        self.assertIn("123 Paper Street", body)


@override_settings(TELLFINDER_API_KEY="xxx")
class TaskLookupJohnTellfinderTestCase(TestCase):
    def setUp(self):
        self.john = John.objects.create(phone_number="+15556667777")

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
    @patch('sms.tasks.send_whisper.apply_async')
    @patch('sms.tasks.send_notification_tellfinder.apply_async')
    def test_lookup_john_tellfinder(self, mock_notification, mock_whisper):
        responses.add(responses.GET,
                      "https://api.tellfinder.com/facets"
                      "?q=phone:+15556667777&keys[]=posttime",
                      json=json.loads(self.tellfinder_positive_result),
                      status=200)

        test = sms.tasks.lookup_john_tellfinder(self.john.id,
                                                "+15558675309")

        self.assertEquals(len(responses.calls), 1)
        self.assertTrue(mock_notification.called)
        self.assertFalse(mock_whisper.called)
        self.assertEquals(test['total'], 31)

    @responses.activate
    @patch('sms.tasks.send_whisper.apply_async')
    @patch('sms.tasks.send_notification_tellfinder.apply_async')
    def test_lookup_john_tellfinder_negative_results(self,
                                                     mock_notification,
                                                     mock_whisper):
        responses.add(responses.GET,
                      "https://api.tellfinder.com/facets"
                      "?q=phone:+15556667777&keys[]=posttime",
                      json=self.tellfinder_negative_result,
                      status=200)

        sms.tasks.lookup_john_tellfinder(self.john.id,
                                         "+15558675309")

        self.assertEquals(len(responses.calls), 1)
        self.assertFalse(mock_notification.called)
        self.assertFalse(mock_whisper.called)

    @responses.activate
    @patch('sms.tasks.send_whisper.apply_async')
    @patch('sms.tasks.send_notification_tellfinder.apply_async')
    def test_lookup_john_tellfinder_wrong_key(self,
                                              mock_notification,
                                              mock_whisper):
        responses.add(responses.GET,
                      "https://api.tellfinder.com/facets"
                      "?q=phone:+15556667777&keys[]=posttime",
                      json={"error": "not authorized"},
                      status=403)

        sms.tasks.lookup_john_tellfinder(self.john.id,
                                         "+15558675309")

        self.assertEquals(len(responses.calls), 1)
        self.assertFalse(mock_notification.called)
        self.assertTrue(mock_whisper.called)

    @responses.activate
    @patch('sms.tasks.send_whisper.apply_async')
    @patch('sms.tasks.send_notification_tellfinder.apply_async')
    def test_lookup_john_tellfinder_server_error(self,
                                                 mock_notification,
                                                 mock_whisper):
        responses.add(responses.GET,
                      "https://api.tellfinder.com/facets"
                      "?q=phone:+15556667777&keys[]=posttime",
                      json={"error": "not authorized"},
                      status=502)

        sms.tasks.lookup_john_tellfinder(self.john.id,
                                         "+15558675309")

        self.assertEquals(len(responses.calls), 1)
        self.assertFalse(mock_notification.called)
        self.assertTrue(mock_whisper.called)

    @patch('sms.tasks.send_whisper.apply_async')
    def test_send_notification_tellfinder(self, mock_whisper):
        test_dict = {"Total": 31,
                     "Earliest Ad": "1955-11-15",
                     "Latest Ad": "2017-02-05"}

        sms.tasks.send_notification_tellfinder(test_dict,
                                               self.john.id,
                                               "+15558675309")

        self.assertTrue(mock_whisper.called)


@override_settings(TWILIO_ACCOUNT_SID='ACxxxx',
                   TWILIO_AUTH_TOKEN='yyyyyyy')
class TaskUtilitiesTestCase(TestCase):
    @patch('twilio.rest.lookups.v1.phone_number.PhoneNumberContext')
    def test_lookup_phone_number(self, mock_context):
        sms.tasks.lookup_phone_number("+15556667777")

        self.assertTrue(mock_context.called)
