from twilio.twiml.messaging_response import MessagingResponse

from .decorators import twilio_view
from .tasks import send_deterrence


@twilio_view
def index(request):
    response = MessagingResponse()

    if "!deter" in request.POST['Body']:
        send_deterrence.apply_async(args=["{0}://{1}"
                                          "".format(request.scheme,
                                                    request.get_host()),
                                          request.POST])
        response.message("Deterrence being sent.",
                         from_=request.POST['To'],
                         to=request.POST['From'])

    return response
