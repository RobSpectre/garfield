from django.test import TestCase
from django.http import QueryDict
from django.test import Client
import responses
from .models import Lookup
from contacts.models import Contact
from sms.tests.test_sms import GarfieldTwilioTestCase
from .lookup_constants import *
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
        self.assertContains(response, lookup_constants.number_of_texts)
        self.assertContains(response,self.callCount)
        self.assertContains(response,self.smsMessageCount)
        self.assertContains(response,self.contactCount)
        self.assertContains(response,self.carrier)

    def testFailureNoCountryCode(self): 
        self.phoneNumber = '2222222222'
        self.params = {"From":self.from_number,
              "To":self.to_number,
              "Body":self.phoneNumber}
        self.querydict.update(self.params)
        response = self.client.lookup(from_=self.from_number,to=self.to_number,params=self.querydict)
        self.assertContains(response,"Error on input")


    def testFailurePhoneNumberInvalidLength(self):
        self.phoneNumber = '+1222222222'
        self.params = {"From":self.from_number,
              "To":self.to_number,
              "Body":self.phoneNumber}
        self.querydict.update(self.params)
        response = self.client.lookup(from_=self.from_number,to=self.to_number,params=self.querydict)
        self.assertContains(response,"Error on input")

    def testStringLookupFailure(self):
        self.Contact = Contact.objects.create(phone_number=self.phoneNumber,
               sms_message_count = self.smsMessageCount,
               call_count = self.callCount,
               contact_count = self.contactCount,
               whitepages_first_name = 'contact name',
               carrier = self.carrier) 
        self.params = {"From":self.from_number,
              "To":self.to_number,
              "Body":'contact name'}
        self.querydict.update(self.params)
        response = self.client.lookup(from_=self.from_number,to=self.to_number,params=self.querydict)
        self.assertContains(response,"Error on input")

    def testPhoneNumberDNE(self):
        self.phoneNumber= '+1222222222'
        self.Contact = Contact.objects.create(phone_number=self.phoneNumber,
               sms_message_count = self.smsMessageCount,
               call_count = self.callCount,
               contact_count = self.contactCount,
               carrier = self.carrier) 
        self.params = {"From":self.from_number,
              "To":self.to_number,
              "Body":'+12222222233'}
        self.querydict.update(self.params)
        response = self.client.lookup(from_=self.from_number,to=self.to_number,params=self.querydict)
        self.assertContains(response, lookup_constants.contact_not_found)
