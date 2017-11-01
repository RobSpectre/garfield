from django.test import TestCase

from contacts.models import Contact


class ContactModelTestCase(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(phone_number="+15558675309")

    def test_string_representation(self):
        self.assertEquals(str(self.contact),
                          "+15558675309: None None")
