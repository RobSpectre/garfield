from twilio.twiml.messaging_response import MessagingResponse

from .decorators import sms_view


@sms_view
def index(request):
    response = MessagingResponse()

    return response


@sms_view
def sim_inbound(request):
    response = MessagingResponse()
    response.message(request.POST['Body'],
                     to="sim:DE5f66bbec066f92dfda5d881926fd292d",
                     from_=request.POST['From'])

    return response


@sms_view
def sim_outbound(request):
    response = MessagingResponse()
    response.message(request.POST['Body'],
                     from_="+16465064701",
                     to=request.POST['To'])

    return response
