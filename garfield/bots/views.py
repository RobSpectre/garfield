from django.urls import reverse

from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from phone_numbers.models import PhoneNumber

from sms.decorators import twilio_view
from sms.tasks import save_sms_message

from .tasks import process_bot_response


@twilio_view
def sms(request):
    response = MessagingResponse()

    try:
        result = PhoneNumber.objects.get(e164=request.POST['To'])
    except PhoneNumber.DoesNotExist:
        result = None
        response.message(request.POST['To'])

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
    response.hangup()

    return response
