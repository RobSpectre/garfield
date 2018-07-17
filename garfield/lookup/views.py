#from celery import chain
#from celery import shared_task

#from django.conf import settings
#from django.db.models.signals import post_save
#from django.dispatch import receiver
#from django.forms.models import model_to_dict
#from django.template.loader import render_to_string

import requests
#import sys

#from django.shortcuts import render
from django.http import HttpResponse

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from contacts.models import Contact
from lookup.models import Lookup
from .decorators import twilio_view
from garfield import local as local
import phonenumbers
# Create your views here.
@twilio_view
def index(request):
    """
        Endpoint to lookup contact information via Twilio
    """
    response = MessagingResponse()
    message = ""
    try:
      parsed_data = lookup_contact(request)
    except InputError as e:
      message = str(e.message)
      response.message(message)
      return response
    except Contact.DoesNotExist as contacexp:
        response.message("Contact was not found")
        return response
    message += "Number of Texts: %d\n" % (parsed_data['num_texts'])

    message += "Number of Calls: %d\n"% (parsed_data['num_calls'])
         
    message += "Number of Contacts Corresponded With: %d\n"% (parsed_data['contact_contact_count'])
    if parsed_data['contact_carrier'] != None:
      message += "Carrier:  " + parsed_data['contact_carrier']
    response.message(message)
    return response

def lookup_contact(request):
    """
        Given a Phone Number in a twilio response body lookup the information 
        in our db and return meta data
        :param request A query dict from twilio 
    """
    contact_number = request.GET.get('Body')
    try:
      valid = is_valid_number(contact_number)
    except: 
      error_message = "Error on input %s \nPhone numbers may only contain +[country code] and numeric characters, please check your syntax\n" % (contact_number)
      raise InputError(contact_number, error_message)
    contact_information = {}
    try:
      contact = Contact.objects.get(phone_number = contact_number)
      num_texts = contact.sms_message_count 
      num_calls = contact.call_count
      contact_contact_count = contact.contact_count
      contact_carrier = contact.carrier
      contact_information['phone_number'] = contact_number
      contact_information['num_texts'] = num_texts
      contact_information['num_calls'] = num_calls
      contact_information['contact_contact_count'] = contact_contact_count
      contact_information['contact_carrier'] = contact_carrier
    except:
     raise Contact.DoesNotExist
    return (contact_information)

class Error(Exception):
  pass

class InputError(Error):
  def __init__(self, expression, message):
    self.expression = expression
    self.message = message

def is_valid_number(number:str):
    phnumber = phonenumbers.parse(number)
    try:
      return phonenumbers.is_possible_number(phnumber)
    except Exception as e:  
      raise e



