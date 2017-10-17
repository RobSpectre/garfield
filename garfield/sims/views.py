from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from sms.decorators import twilio_view


@twilio_view
def sms_receive(request):
    response = MessagingResponse()
    response.message(request.POST['Body'],
                     to="sim:DE184e039058c056aab5dd9c3555667942",
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
    response.dial("sim:DE184e039058c056aab5dd9c3555667942",
                  from_=request.POST['From'])

    return response


@twilio_view
def voice_send(request):
    response = VoiceResponse()
    response.dial(request.POST['To'],
                  from_="+16465064701")

    return response
