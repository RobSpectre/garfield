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
         
     message += "Number of Contacts Corresponded With: %d\n"% (parsed_data['suspect_contact_count'])
     if parsed_data['suspect_carrier'] != None:
         message += "Carrier:  " + parsed_data['suspect_carrier']
    response.message(message)
    return response

def lookup_contact(request):
    """
        Given a Phone Number in a twilio response body lookup the information 
        in our db and return meta data
        :param request A query dict from twilio 
    """
    suspect_number = request.GET.get('Body')
    try:
      valid = is_valid_number(suspect_number)
    except 
      error_message = "Error on input %s \nPhone numbers may only contain +[country code] and numeric characters, please check your syntax\n" % (suspect_number)
        raise InputError(suspect_number, error_message)
    except phonenumbers.phonenumberutil.NumberParseException as e:
      return False
    suspect_information = {}
    try:
      contact = Contact.objects.get(phone_number = suspect_number)
      num_texts = contact.sms_message_count 
      num_calls = contact.call_count
      suspect_contact_count = contact.contact_count
      suspect_carrier = contact.carrier
      suspect_information['phone_number'] = suspect_number
      suspect_information['num_texts'] = num_texts
      suspect_information['num_calls'] = num_calls
      suspect_information['suspect_contact_count'] = suspect_contact_count
      suspect_information['suspect_carrier'] = suspect_carrier
    except:
     raise Contact.DoesNotExist
    return (suspect_information)

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



