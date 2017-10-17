from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from sms.decorators import twilio_view
from phone_numbers.models import PhoneNumber


@twilio_view
def sms_receive(request):
    response = MessagingResponse()
    result = PhoneNumber.objects.get(e164=request.POST['To'])

    if result and result.related_sim.sid:
        response.message(request.POST['Body'],
                         to="sim:{0}".format(result.related_sim.sid),
                         from_=request.POST['From'])

    return response


@twilio_view
def sms_send(request):
    response = MessagingResponse()
    response.message(request.POST['Body'],
                     from_="+16465064701",
                     to=request.POST['To'])

    return response


@twilio_view
def voice_receive(request):
    response = VoiceResponse()
    result = PhoneNumber.objects.get(e164=request.POST['To'])

    if result and result.related_sim.sid:
        with response.dial(caller_id=request.POST['From']) as dial:
            dial.sim(result.related_sim.sid)

    return response


@twilio_view
def voice_send(request):
    response = VoiceResponse()
    response.dial(request.POST['To'],
                  from_="+16465064701")

    return response
