from celery import chain
from celery import shared_task

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.template.loader import render_to_string

import requests

from django.shortcuts import render
from django.http import HttpResponse

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from contacts.models import Contact
from .decorators import twilio_view

# Create your views here.
#@twilio_view
def index(request):
  x = lookup_contact("+17327591778")
  return "Hello World"
  #return lookup_contact('+17327591778')
    #response = MessagingResponse()
    #response.message("Hello World!")
    #return response

def lookup_contact(contact_number):
    contact = Contact.objects.all()#(phone_number = contact_number)
    return 'Hello World'


