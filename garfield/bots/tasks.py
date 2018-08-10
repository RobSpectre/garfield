import os
import operator
from random import choice
import json

from django.conf import settings
from django.template import Context
from django.template import Template

from celery import shared_task

import spacy

from sms.tasks import send_sms_message
from sms.tasks import save_sms_message

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
        save_sms_message(message)

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
        save_sms_message.apply_async(args=[msg])


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
