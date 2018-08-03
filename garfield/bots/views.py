from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.urls import reverse

from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from phone_numbers.models import PhoneNumber

from sms.decorators import twilio_view
from sms.tasks import save_sms_message
from voice.tasks import save_call

from .tasks import process_bot_response


VOICEMAIL_MESSAGES = [static('/recordings/agnostic_male.mp3'),
                      static('/recordings/agnostic_female.mp3'),
                      static('/recordings/verizon_female.mp3'),
                      static('/recordings/agnostic_female_2.mp3')]


@twilio_view
def sms(request):
    response = MessagingResponse()

    result = get_phone_number(request.POST['To'])

    if result and result.number_type == PhoneNumber.DETERRENCE:
        save_sms_message.apply_async(args=[request.POST])
    elif result and result.related_sim:
        response.redirect(reverse('sims:sms_receive'))
    elif result and result.related_bot:
        process_bot_response.apply_async(args=[request.POST,
                                               result.related_bot.id])

    return response


@twilio_view
def voice(request):
    response = VoiceResponse()

    result = get_phone_number(request.POST['To'])

    if result and result.number_type == PhoneNumber.DETERRENCE:
        response.say("You are contacting an unused phone number "
                     "for the {0}. Voicemail is not configured for "
                     "this line - please call your local precinct "
                     "if you need assistance. Goodbye."
                     "".format(settings.GARFIELD_JURISDICTION),
                     voice="alice")
        save_call.apply_async(args=[request.POST])
    elif result and result.related_sim:
        response.redirect(reverse('sims:voice_receive'))
    elif result and result.related_bot:
        voicemail = get_voicemail(request.POST['To'])
        response.play(voicemail)
        save_call.apply_async(args=[request.POST])

    return response


def get_phone_number(number):
    try:
        result = PhoneNumber.objects.get(e164=number)
    except PhoneNumber.DoesNotExist:
        result = None

    return result


def get_voicemail(number):
    last_digit = int(number[-1:])

    selection = last_digit % len(VOICEMAIL_MESSAGES)

    return VOICEMAIL_MESSAGES[selection]
