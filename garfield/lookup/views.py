from django.shortcuts import render
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse

from .decorators import twilio_view
# Create your views here.
@twilio_view
def index(request):
    response = MessagingResponse()
    response.message("Hello World!")
    return response

