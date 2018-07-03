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
@twilio_view
def index(request):
    """
        Endpoint to lookup contact information via Twilio
    """
    response = MessagingResponse()
    parsed_data = lookup_contact(request)
    if(parsed_data == {}):
         response.message("Contact is not in the System")
    else:
         response.message("Number of Texts: "+ parsed_data['num_texts'])
         response.message("Number of Calls: "+parsed_data['num_calls'])
         response.message("Contact Count:  "+  parsed_data['suspect_contact_count'])
         response.message("Carrier:  " + parsed_data['suspect_carrier'])
    return response

def lookup_contact(request):
    """
        Given a Phone Number in a twilio response body lookup the information 
        in our db and return meta data
        :param request A query dict from twilio 
    """
    suspect_number = request.GET.get('From')
    #init an empty dict for suspect info
    suspect_information = {}
    contact = Contact.objects.get(phone_number = suspect_number)

    if contact != None:
        
        num_texts = contact.sms_message_count 
        num_calls = contact.call_count
        suspect_contact_count = contact.contact_count
        #carrier information
        suspect_carrier = contact.carrier
        suspect_information['phone_number'] = suspect_number
        suspect_information['num_texts'] = num_texts
        suspect_information['num_calls'] = num_calls
        suspect_information['suspect_contact_count'] = suspect_contact_count
        suspect_information['suspect_carrier'] = suspect_carrier
        return (suspect_information)
    else:
        return ({})


