from django.test import override_settings

from sms.decorators import sms_view

from .test_sms import GarfieldSmsTestCase


class GarfieldSmsDecoratorsTestCase(GarfieldSmsTestCase):
    def test_not_get_or_post(self):
        response = self.client.delete("/sms/",
                                      HTTP_HOST="example.com")

        self.assertEquals(response.status_code, 405)

    def test_wrong_twilio_signature_post(self):
        response = self.client.post("/sms/", params={"Body": "foo"},
                                    HTTP_X_TWILIO_SIGNATURE="Xxx",
                                    HTTP_HOST="example.com")
        self.assertEquals(response.status_code, 403)

    def test_wrong_twilio_signature_get(self):
        response = self.client.get("/sms/?Body=foo",
                                   HTTP_X_TWILIO_SIGNATURE="Xxx",
                                   HTTP_HOST="example.com")
        self.assertEquals(response.status_code, 403)

    def test_missing_twilio_signature(self):
        response = self.client.post("/sms/", params={"Body": "foo"},
                                    HTTP_HOST="example.com")
        self.assertEquals(response.status_code, 403)

    def test_correct_twilio_signature(self):
        response = self.client.sms("Test.")
        self.assertEquals(response.status_code, 200)
        self.assert_twiml(response)

    @override_settings(DEBUG=True)
    def test_non_twiml_response(self):
        @sms_view
        def return_empty_list(request):
            return request

        self.assertEquals([], return_empty_list([]))
