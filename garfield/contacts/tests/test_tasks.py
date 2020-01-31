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

        self.add_ons_person = '{"whitepages_pro_caller_id": {"status": "' \
                              'successful", "request_sid": "asdf", "mess' \
                              'age": null, "code": null, "result": {"pho' \
                              'ne_number": "+15558675309", "warnings": [' \
                              '], "historical_addresses": [], "alternate' \
                              '_phones": [], "error": null, "is_commerci' \
                              'al": false, "associated_people": [{"name"' \
                              ': "Jack Doe", "firstname": "JohJackn", "m' \
                              'iddlename": "Q", "lastname": "Doe", "rela' \
                              'tion": "Household", "id": "Person.asdf"},' \
                              '{"name": "Jane Doe", "firstname": "Jane",' \
                              '"middlename": "", "lastname": "Doe", "rel' \
                              'ation": "Household", "id": "Person.qwer"}' \
                              '], "country_calling_code": "1", "belongs_' \
                              'to": {"age_range": {"to": 67, "from": 60}' \
                              ', "name": "Mr. John Doe", "firstname": "J' \
                              'ohn", "middlename": "Q", "lastname": "Doe' \
                              '", "industry": null, "alternate_names": [' \
                              '], "gender": "Male", "link_to_phone_start' \
                              '_date": "2018-04-06", "type": "Person", "' \
                              'id": "Person.zxcv"}, "is_valid": true, "l' \
                              'ine_type": "Mobile", "carrier": "childsaf' \
                              'e.ai", "current_addresses": [{"city": "Ne' \
                              'w York", "lat_long": {"latitude": 40.328487,' \
                              '"longitude": -73.9855, "accuracy": "RoofT' \
                              'op"}, "is_active": true, "location_type":' \
                              '"Address", "street_line_2": null, "link_t' \
                              'o_person_start_date": "2019-03-01", "stre' \
                              'et_line_1": "123 Johnny Street", "postal_cod' \
                              'e": "10036", "delivery_point": "MultiUnit' \
                              '", "country_code": "US", "state_code": "N' \
                              'Y", "id": "Location.asdf", "zip4": "0000"' \
                              '}], "id": "Phone.lkj", "is_prepaid": null' \
                              '}}}'

        self.add_ons_business = '{"whitepages_pro_caller_id": {"status": "' \
                                'successful", "request_sid": "asdf", "mess' \
                                'age": null, "code": null, "result": {"pho' \
                                'ne_number": "+18888675309", "warnings": [' \
                                '], "historical_addresses": [], "alternate' \
                                '_phones": [], "error": null, "is_commerci' \
                                'al": true, "associated_people": [], "coun' \
                                'try_calling_code": "1", "belongs_to": {"a' \
                                'ge_range": null, "name": "The John Store"' \
                                ', "firstname": null, "middlename": null, ' \
                                '"lastname": null, "industry": null, "alte' \
                                'rnate_names": [], "gender": null, "link_t' \
                                'o_phone_start_date": null, "type": "Busin' \
                                'ess", "id": "Business.asdf"}, "is_valid":' \
                                'true, "line_type": "TollFree", "carrier":' \
                                '"Test.", "current_addresses": [{"city": "' \
                                'New York", "lat_long": {"latitude": 40.32' \
                                '8487, "longitude": -73.9855, "accuracy": ' \
                                '"Rooftop"}, "is_active": null, "location_' \
                                'type": "Address", "street_line_2": null, ' \
                                '"link_to_person_start_date": null, "stree' \
                                't_line_1": "123 Johnny Street", "postal_c' \
                                'ode": null, "delivery_point": null, "coun' \
                                'try_code": "US", "state_code": null, "id"' \
                                ': "Location.asdf", "zip4": null}], "id": ' \
                                '"Phone.asdf", "is_prepaid": null}}}'

        self.add_ons_voip = '{"whitepages_pro_caller_id": {"status": "' \
                            'successful", "request_sid": "asdf", "mess' \
                            'age": null, "code": null, "result": {"pho' \
                            'ne_number": "+15558675309", "warnings": [' \
                            '], "historical_addresses": [], "alternate' \
                            '_phones": [], "error": null, "is_commerci' \
                            'al": false, "associated_people": [], "cou' \
                            'ntry_calling_code": "1", "belongs_to": {"' \
                            'age_range": null, "name": "John Doe", "fi' \
                            'rstname": null, "middlename": null, "la' \
                            'stname": "Doe", "industry": null, "altern' \
                            'ate_names": [], "gender": null, "link_to_' \
                            'phone_start_date": null, "type": "Person"' \
                            ', "id": "Person.asdf"}, "is_valid": true,' \
                            ' "line_type": "NonFixedVOIP", "carrier": ' \
                            '"Test.", "current_addresses": [{"city": "' \
                            'New York", "lat_long": {"latitude": 40.32' \
                            '8487, "longitude": -73.9672, "accuracy": ' \
                            '"PostalCode"}, "is_active": null, "locati' \
                            'on_type": "PostalCode", "street_line_2": ' \
                            'null, "link_to_person_start_date": null, ' \
                            '"street_line_1": null, "postal_code": "10' \
                            '025", "delivery_point": null, "country_co' \
                            'de": "US", "state_code": "NY", "id": "Loc' \
                            'ation.asdf", "zip4": null}], "id": "Phone' \
                            '.asdf", "is_prepaid": null}}}'

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
