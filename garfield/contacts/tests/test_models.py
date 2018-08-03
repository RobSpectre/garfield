from django.core.exceptions import ValidationError
from django.test import TestCase

from mock import patch

from contacts.models import Contact


class ContactModelTestCase(TestCase):
    @patch('deterrence.tasks.check_campaign_for_contact.apply_async')
    @patch('contacts.tasks.lookup_contact.apply_async')
    def setUp(self, mock_lookup, mock_check_campaign):
        self.contact = Contact.objects.create(phone_number="+15558675309")

    def test_string_representation(self):
        self.assertEquals(str(self.contact),
                          "(555) 867-5309: Unidentified")

    @patch('contacts.tasks.lookup_contact.apply_async')
    def test_phone_number_validation(self, mock_lookup):
        contact = Contact(phone_number="1111")
        self.assertRaises(ValidationError,
                          contact.full_clean)

    def test_string_representation_no_friendly(self):
        self.contact.phone_number_friendly = None

        self.assertEquals(str(self.contact),
                          "+15558675309: Unidentified")

    def test_string_representation_no_identity_found(self):
        self.contact.identified = True

        self.assertEquals(str(self.contact),
                          "(555) 867-5309: Identity Not Found")

    def test_string_representation_identity_found(self):
        self.contact.identified = True
        self.contact.whitepages_first_name = "John"
        self.contact.whitepages_last_name = "Arbuckle"

        self.assertEquals(str(self.contact),
                          "(555) 867-5309: John Arbuckle")
