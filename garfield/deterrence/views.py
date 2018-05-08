from django.urls import reverse

from twilio.twiml.messaging_response import MessagingResponse

from phone_numbers.models import PhoneNumber
from phone_numbers.tasks import buy_new_phone_number

from sms.decorators import twilio_view
from .tasks import send_deterrence


@twilio_view
def index(request):
    response = MessagingResponse()

    if "!deter" in request.POST['Body']:
        response.redirect(reverse('deterrence:deter'))
    elif "!new_deterrence" in request.POST['Body']:
        response.redirect(reverse('deterrence:new_deterrence'))
    else:
        response.message("I did not understand that command.",
                         from_=request.POST['To'],
                         to=request.POST['From'])

    return response


@twilio_view
def deter(request):
    response = MessagingResponse()

    response.message("Sending deterrence...")

    send_deterrence.apply_async(args=[request.POST])

    return response


@twilio_view
def new_deterrence(request):
    response = MessagingResponse()

    base_uri = "{0}://{1}".format(request.scheme,
                                  request.get_host())

    buy_new_phone_number.apply_async(args=[base_uri,
                                           request.POST,
                                           PhoneNumber.DETERRENCE])

    response.message("Buying new deterrence phone number...",
                     from_=request.POST['To'],
                     to=request.POST['From'])

    return response
