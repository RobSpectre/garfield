import os
import operator
from random import choice
import json

from celery import shared_task

from django.conf import settings
from django.template import Context
from django.template import Template

import spacy

from phone_numbers.models import PhoneNumber
from contacts.models import Contact
from sms.models import SmsMessage

from sms.tasks import check_contact
from sms.tasks import send_sms_message

from .models import Bot

phrase_order = {'SALUTATION': 10,
                'ACKNOWLEDGEMENT': 20,
                'FLIRT': 30,
                'AVAILABILITY': 40,
                'HAGGLE': 50,
                'PRICE': 60,
                'IN-OR-OUT': 70,
                'LOCATION': 80,
                'EXTRAS': 90,
                'PICS': 100,
                'ETHNICITY': 110,
                'LE-CHECK': 120,
                'REAL': 130,
                'CONFUSION': 140,
                'PHYSICAL': 150,
                'AGE': 160,
                'SERVICES': 170,
                'SOURCE': 180,
                'VALEDICTION': 190,
                'TIME': 200,
                'RECRUITING': 210}


@shared_task
def process_bot_response(message, bot_id):
    bot = Bot.objects.get(id=bot_id)

    if not bot.debug:
        record_inbound_message(message)

    classify_message_intent.apply_async(args=[message, bot_id])


@shared_task
def classify_message_intent(message, bot_id):
    bot = Bot.objects.get(id=bot_id)

    nlp = spacy.load(os.path.join(settings.ARBUCKLE_DIR,
                                  'models',
                                  bot.model))

    doc = nlp(message['Body'])

    compose_response.apply_async(args=[doc.cats,
                                       message,
                                       bot_id])


@shared_task
def compose_response(cats, message, bot_id):
    bot = Bot.objects.get(id=bot_id)

    intents = process_intents(cats,
                              bot.threshold)

    order = order_intents(intents)

    response = retrieve_answer(order, bot_id)

    send_bot_response.apply_async(args=[response,
                                        intents,
                                        message,
                                        bot_id])


@shared_task
def send_bot_response(response,
                      intents,
                      message,
                      bot_id):

    bot = Bot.objects.get(id=bot_id)

    countdown = choice(range(bot.human_delay_min,
                             bot.human_delay_max))

    if bot.debug:
        countdown = 0

    if intents:
        deliver_bot_response.apply_async(args=[response,
                                               message,
                                               bot_id],
                                         countdown=countdown)

    if bot.debug:
        send_sms_message(to=message['From'],
                         from_=message['To'],
                         body="[Debug]\n{0}".format(intents))


@shared_task
def deliver_bot_response(response, message, bot_id):
    bot = Bot.objects.get(id=bot_id)

    msg = send_sms_message(to=message['From'],
                           from_=message['To'],
                           body=response)

    if not bot.debug:
        record_outbound_message.apply_async(args=[msg])


@shared_task
def record_inbound_message(message):
    try:
        phone_number = PhoneNumber.objects.get(e164=message['To'])
    except PhoneNumber.DoesNotExist:
        return False

    record = SmsMessage(sid=message['MessageSid'],
                        from_number=message['From'],
                        to_number=message['To'],
                        body=message['Body'],
                        related_phone_number=phone_number)
    record.save()

    try:
        contact = Contact.objects.get(phone_number=message['From'])
        record.related_contact = contact
        record.save()
    except Contact.DoesNotExist:
        check_contact.apply_async(args=[message])


@shared_task
def record_outbound_message(message):
    phone_number = PhoneNumber.objects.get(e164=message['From'])
    contact = Contact.objects.get(phone_number=message['To'])

    record = SmsMessage(sid=message['MessageSid'],
                        from_number=message['From'],
                        to_number=message['To'],
                        body=message['Body'],
                        related_phone_number=phone_number,
                        related_contact=contact)
    record.save()

    return record


def process_intents(cats, threshold):
    cats = sorted(cats.items(),
                  key=operator.itemgetter(1))

    intents = {}

    for cat in cats:
        if cat[1] >= threshold:
            intents[cat[0]] = cat[1]

    return intents


def order_intents(intents):
    order = {}

    for key, value in intents.items():
        order[key] = phrase_order[key]

    return sorted(order.items(),
                  key=operator.itemgetter(1))


def retrieve_answer(order, bot_id):
    bot = Bot.objects.get(id=bot_id)

    answers_file = open(os.path.join(settings.ARBUCKLE_DIR,
                                     'answers',
                                     bot.answers),
                        'r')
    answers = json.load(answers_file)
    answers_file.close()

    response = ""

    for key, value in order:
        response = "{0} {1}".format(response,
                                    choice(answers[key])).strip()

    template = Template(response)
    context = Context({'alias': bot.alias,
                       'neighborhood': bot.neighborhood,
                       'location': bot.location,
                       'price': bot.rates})

    return template.render(context)
