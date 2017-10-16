from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse

from sms.decorators import twilio_view


@twilio_view
def receive_sms(request):
    response = MessagingResponse()
    response.message(request.POST['Body'],
                     path="/sims/sms/receive/",
                     to="sim:DE5f66bbec066f92dfda5d881926fd292d",
                     from_=request.POST['From'])

    return response


@twilio_view
def send_sms(request):
    response = MessagingResponse()
    response.message(request.POST['Body'],
                     path="/sims/sms/send/",
                     from_="+16465064701",
                     to=request.POST['To'])

    return response


@twilio_view
def receive_call(request):
    response = VoiceResponse()
    response.dial(request.POST['From'],
                  path="/sims/voice/receive/",
                  to="sim:DE5f66bbec066f92dfda5d881926fd292d")

    return response


@twilio_view
def send_call(request):
    response = VoiceResponse()
    response.dial(request.POST['To'],
                  path="/sims/voice/send/",
                  from_="+16465064701")

    return response
