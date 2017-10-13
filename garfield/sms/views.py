from twilio.twiml.messaging_response import MessagingResponse

from .decorators import sms_view


@sms_view
def index(request):
    response = MessagingResponse()

    return response
