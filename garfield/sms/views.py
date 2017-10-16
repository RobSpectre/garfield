from twilio.twiml.messaging_response import MessagingResponse

from .decorators import twilio_view


@twilio_view
def index(request):
    response = MessagingResponse()

    return response
