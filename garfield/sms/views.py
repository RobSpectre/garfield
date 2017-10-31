from twilio.twiml.messaging_response import MessagingResponse

from .decorators import twilio_view
from .tasks import send_deterrence


@twilio_view
def index(request):
    response = MessagingResponse()

    if "!deter" in request.POST['Body']:
        send_deterrence.apply_async(args=[request.POST])
        response.message("Deterrence being sent.",
                         from_=request['To'],
                         to=request['From'])

    return response
