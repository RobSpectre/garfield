from django.test import TestCase
from django.http import QueryDict
from django.test import Client
import responses
from .models import Lookup
from contacts.models import Contact
from sms.tests.test_sms import GarfieldTwilioTestCase

# Create your tests here.

class TestTwilioLookupTests(GarfieldTwilioTestCase):
    #create dummy contact

    phoneNumber = "+12222222222"
    to_number = "+1234456789"
    from_number = "+1234456789"
    smsMessageCount = 10
    callCount = 30
    contactCount = 20
    carrier ="Mock Carrier"
    querydict = QueryDict('',mutable=True)
    def testSuccess(self):
        self.Contact = Contact.objects.create(phone_number=self.phoneNumber,
               sms_message_count = self.smsMessageCount,
               call_count = self.callCount,
               contact_count = self.contactCount,
               carrier = self.carrier) 
        self.params = {"From":self.from_number,
              "To":self.to_number,
              "Body":self.phoneNumber}
        self.querydict.update(self.params)
        response = self.client.lookup(from_=self.from_number,to=self.to_number,params=self.querydict)
        self.assertContains(response,"Number of Texts")
        self.assertContains(response,self.callCount)
        self.assertContains(response,self.smsMessageCount)
        self.assertContains(response,self.contactCount)
        self.assertContains(response,self.carrier)
    
