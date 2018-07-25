from django.test import TestCase
from django.test import override_settings

from mock import Mock
from mock import patch

from phone_numbers.models import PhoneNumber

from bots.models import Bot
from bots import tasks


class BotsTasksNoContactTestCase(TestCase):
    def setUp(self):
        self.bot = Bot.objects.create(alias="Botty McBotface",
                                      neighborhood="Brooklyn",
                                      location="Prospect Park",
                                      rates="$1,000,000",
                                      model='test_model',
                                      answers='answers.json')

        self.phone_number = PhoneNumber.objects.create(sid="PNxxx",
                                                       account_sid="ACxxx",
                                                       service_sid="SExxx",
                                                       url="http://exmple.com",
                                                       e164="+15558675309",
                                                       formatted="(555) "
                                                                 "867-5309",
                                                       friendly_name="Stuff.",
                                                       country_code="1",
                                                       number_type="ADV",
                                                       related_bot=self.bot)

        self.msg = {'From': "+15556667777",
                    'To': "+15558675309",
                    'Body': "Test",
                    'MessageSid': "MMxxxx"}

    @patch('bots.tasks.save_sms_message')
    @patch('bots.tasks.classify_message_intent.apply_async')
    def test_process_bot_response(self,
                                  mock_classify,
                                  mock_record):
        tasks.process_bot_response(self.msg, self.bot.id)

        mock_classify.assert_called_once_with(args=[self.msg,
                                                    self.bot.id])
        mock_record.assert_called_once_with(self.msg)

    @patch('bots.tasks.save_sms_message')
    @patch('bots.tasks.classify_message_intent.apply_async')
    def test_process_bot_response_debug(self,
                                        mock_classify,
                                        mock_record):
        self.bot.debug = True
        self.bot.save()

        tasks.process_bot_response(self.msg, self.bot.id)

        mock_classify.assert_called_once_with(args=[self.msg,
                                                    self.bot.id])
        self.assertFalse(mock_record.called)

    @override_settings(ARBUCKLE_DIR="/tmp")
    @patch('spacy.load')
    @patch('bots.tasks.compose_response.apply_async')
    def test_classify_message_intent(self,
                                     mock_compose,
                                     mock_load):
        mock_doc = Mock(cats={'STUFF': 0.9, 'THINGS': 0.2})

        mock_load.return_value = mock_doc

        tasks.classify_message_intent(self.msg, self.bot.id)

        mock_load.assert_called_once_with("/tmp/models/test_model")
        self.assertTrue(mock_compose.called)

    @patch('bots.tasks.process_intents')
    @patch('bots.tasks.order_intents')
    @patch('bots.tasks.retrieve_answer')
    @patch('bots.tasks.send_bot_response.apply_async')
    def test_compose_response(self, mock_send, mock_retrieve, mock_order,
                              mock_process):
        tasks.compose_response({'STUFF': 0.9, 'THINGS': 0.2},
                               self.msg,
                               self.bot.id)

        self.assertTrue(mock_send.called)
        self.assertTrue(mock_retrieve.called)
        self.assertTrue(mock_order.called)
        self.assertTrue(mock_process.called)

    @patch('bots.tasks.deliver_bot_response.apply_async')
    @patch('sms.tasks.send_sms_message')
    def test_send_bot_response(self, mock_send, mock_deliver):
        tasks.send_bot_response('Stuff.',
                                {'STUFF': 0.9, 'THINGS': 0.2},
                                self.msg,
                                self.bot.id)
        self.assertTrue(mock_deliver.called)
        self.assertFalse(mock_send.called)

    @patch('bots.tasks.deliver_bot_response.apply_async')
    @patch('bots.tasks.send_sms_message')
    def test_send_bot_response_debug(self, mock_send, mock_deliver):
        self.bot.debug = True
        self.bot.save()

        tasks.send_bot_response('Stuff.',
                                {'STUFF': 0.9, 'THINGS': 0.2},
                                self.msg,
                                self.bot.id)
        self.assertTrue(mock_deliver.called)
        self.assertTrue(mock_send.called)

    @patch('bots.tasks.save_sms_message.apply_async')
    @patch('bots.tasks.send_sms_message')
    def test_deliver_bot_response(self, mock_send, mock_record):
        tasks.deliver_bot_response("Stuff.",
                                   self.msg,
                                   self.bot.id)

        self.assertTrue(mock_send.called)
        self.assertTrue(mock_record.called)

    @patch('bots.tasks.save_sms_message.apply_async')
    @patch('bots.tasks.send_sms_message')
    def test_deliver_bot_response_debug(self, mock_send, mock_record):
        self.bot.debug = True
        self.bot.save()

        tasks.deliver_bot_response("Stuff.",
                                   self.msg,
                                   self.bot.id)

        self.assertTrue(mock_send.called)
        self.assertFalse(mock_record.called)

    @override_settings(ARBUCKLE_DIR='./bots/tests/assets')
    def test_retrieve_answer(self):
        answers = tasks.retrieve_answer([('SALUTATION', 10),
                                         ('LOCATION', 20)],
                                        self.bot.id)
        self.assertEquals(answers,
                          "Hi Prospect Park")

        answers = tasks.retrieve_answer([('SALUTATION', 10)],
                                        self.bot.id)
        self.assertEquals(answers,
                          "Hi")

        answers = tasks.retrieve_answer([],
                                        self.bot.id)
        self.assertFalse(answers)


class BotsUtilTestCase(TestCase):
    def test_process_intents(self):
        intents = tasks.process_intents({"STUFF": 0.9,
                                         "THINGS": 0.5,
                                         "WOO": 0.95},
                                        0.7)

        self.assertEquals(intents,
                          {"WOO": 0.95, "STUFF": 0.9})

        intents = tasks.process_intents({"STUFF": 0.9,
                                         "THINGS": 0.7},
                                        0.7)
        self.assertEquals(intents,
                          {"STUFF": 0.9, "THINGS": 0.7})

    def test_order_intents(self):
        order = tasks.order_intents({"AVAILABILITY": 0.9,
                                     "SALUTATION": 0.8})
        self.assertEquals([i[0] for i in order],
                          ['SALUTATION', 'AVAILABILITY'])
