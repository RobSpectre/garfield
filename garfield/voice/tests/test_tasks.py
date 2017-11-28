from django.http import HttpRequest
from django.test import TestCase

from phone_numbers.models import PhoneNumber
from contacts.models import Contact

from voice.models import Call
import voice.tasks


class SaveCallTestCasePhoneNumberExists(TestCase):
    def setUp(self):
        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1")

        self.contact = Contact.objects.create(phone_number="+15556667777")

        self.request = HttpRequest()

        self.request.POST = {"CallSid": "CAtesting",
                             "AccountSid": "ACxxxxx",
                             "To": "+15558675309",
                             "From": "+15556667777",
                             "Direction": "inbound",
                             "FromCity": "BROOKLYN",
                             "FromState": "NY",
                             "FromCountry": "US",
                             "FromZip": "55555"}

    def test_save_call_to_number(self):
        voice.tasks.save_call(self.request.POST)

        test = Call.objects.all()

        self.assertTrue(test)
        self.assertEquals(test[0].sid, "CAtesting")
        self.assertEquals(test[0].to_number, "+15558675309")
        self.assertEquals(test[0].related_contact,
                          self.contact)

    def test_save_call_from_number(self):
        self.request.POST["From"] = "+15558675309"
        self.request.POST["To"] = "+15556667777"

        voice.tasks.save_call(self.request.POST)

        test = Call.objects.all()

        self.assertTrue(test)
        self.assertEquals(test[0].sid, "CAtesting")
        self.assertEquals(test[0].to_number, "+15556667777")
        self.assertEquals(test[0].related_contact,
                          self.contact)

    def test_save_voice_recording(self):
        voice.tasks.save_call(self.request.POST)

        test_request = HttpRequest()

        test_request.POST = {"CallSid": "CAtesting",
                             "AccountSid": "ACxxxxx",
                             "RecordingUrl": "example.com",
                             "RecordingDuration": 15}

        voice.tasks.save_voice_recording(test_request.POST)

        test_call = Call.objects.all()[0]

        self.assertEquals("example.com", test_call.recording_url)
        self.assertEquals(15, test_call.duration)
