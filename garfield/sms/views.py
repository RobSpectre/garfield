from django.urls import reverse

from twilio.twiml.messaging_response import MessagingResponse

from phone_numbers.tasks import buy_new_phone_number
from phone_numbers.models import PhoneNumber

from .decorators import twilio_view


@twilio_view
def index(request):
    response = MessagingResponse()

    base_uri = "{0}://{1}".format(request.scheme,
                                  request.get_host())

    if "deter" in request.POST['Body']:
        response.redirect(reverse("deterrence:index"))
    elif "!new_ad" in request.POST['Body']:
        buy_new_phone_number.apply_async(args=[base_uri,
                                               request.POST,
                                               PhoneNumber.AD])

        response.message("Buying new advertisement phone number...",
                         from_=request.POST['To'],
                         to=request.POST['From'])
    else:
        response.message("I did not understand that command.",
                         from_=request.POST['To'],
                         to=request.POST['From'])

    return response
