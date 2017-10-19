from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from sms.decorators import twilio_view
from sms.tasks import save_sms_message
from sms.models import SmsMessage
from phone_numbers.models import PhoneNumber


@twilio_view
def sms_receive(request):
    response = MessagingResponse()
    try:
        result = PhoneNumber.objects.get(e164=request.POST['To'])
    except ObjectDoesNotExist:
        result = None

    if result and result.related_sim.sid:
        response.message(request.POST['Body'],
                         to="sim:{0}".format(result.related_sim.sid),
                         from_=request.POST['From'])

    save_sms_message.apply_async(args=[request.POST])

    return response


@twilio_view
def sms_send(request):
    response = MessagingResponse()
    try:
        result = \
            SmsMessage.objects \
            .filter(from_number=request.POST['To']) \
            .latest('date_created')

        response.message(request.POST['Body'],
                         from_=result.related_phone_number.e164,
                         to=request.POST['To'])
    except ObjectDoesNotExist:
        response.message(request.POST['Body'],
                         from_=settings.TWILIO_PHONE_NUMBER,
                         to=request.POST['To'])

    save_sms_message.apply_async(args=[request.POST])

    return response


@twilio_view
def voice_receive(request):
    response = VoiceResponse()
    try:
        result = PhoneNumber.objects.get(e164=request.POST['To'])
    except ObjectDoesNotExist:
        result = None

    if result and result.related_sim.sid:
        with response.dial(caller_id=request.POST['From'],
                           record=True) as dial:
            dial.sim(result.related_sim.sid)
    else:
        response.record()

    return response


@twilio_view
def voice_send(request):
    response = VoiceResponse()
    try:
        result = \
            SmsMessage.objects \
            .filter(from_number=request.POST['To']) \
            .latest('date_created')

        response.dial(request.POST['To'],
                      caller_id=result.related_phone_number.e164,
                      record=True)
    except ObjectDoesNotExist:
        response.dial(request.POST['To'],
                      caller_id=settings.TWILIO_PHONE_NUMBER,
                      record=True)

    return response
