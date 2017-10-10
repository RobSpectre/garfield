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

    def test_correct_twilio_signature(self):
        response = self.client.sms("Test.")
        self.assertEquals(response.status_code, 200)
