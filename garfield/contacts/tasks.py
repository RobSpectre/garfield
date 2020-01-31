from celery import chain
from celery import shared_task

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.template.loader import render_to_string

from twilio.rest import Client

from contacts.models import Contact
from phone_numbers.models import PhoneNumber
from sims.models import Whisper


@shared_task
def lookup_phone_number(phone_number, type=None, addons=None):
    client = Client(settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN)

    return client.lookups.phone_numbers(phone_number).fetch(add_ons=addons,
                                                            type=type)


@shared_task
def lookup_contact(contact_number):
    contact = Contact.objects.get(phone_number=contact_number)

    return chain(lookup_contact_whitepages.si(contact.id)).apply_async()


@shared_task
def lookup_contact_whitepages(contact_id):
    contact = Contact.objects.get(pk=contact_id)

    lookup = lookup_phone_number(contact.phone_number,
                                 type="carrier",
                                 addons="whitepages_pro_caller_id")

    if lookup.add_ons['status'] == 'successful':
        contact = apply_lookup_whitepages_to_contact(contact, lookup)

        fields = [field.name for field in Contact._meta.get_fields()
                  if field.name.startswith('whitepages')]

        contact.save(update_fields=fields)

        contact.identified = True
        contact.save(update_fields=['identified'])

    if lookup.add_ons['status'] == 'successful':
        twilio_number = contact.related_phone_numbers.last()
        if twilio_number:
            send_notification_whitepages.apply_async(args=[contact.id,
                                                           twilio_number.e164])


def apply_lookup_whitepages_to_contact(contact, lookup):
    result = lookup.add_ons['results']["whitepages_pro_caller_id"]['result']

    if result['belongs_to']:
        contact.whitepages_entity_type = result['belongs_to']['type']

        if contact.whitepages_entity_type == "Person":
            contact.whitepages_first_name = result['belongs_to'
                                                   ]['firstname']
            contact.whitepages_middle_name = result['belongs_to'
                                                    ]['middlename']
            contact.whitepages_last_name = result['belongs_to']['lastname']
            contact.whitepages_gender = result['belongs_to']['gender']
        else:
            contact.whitepages_business_name = result['belongs_to']['name']

    if result['current_addresses']:
        contact.whitepages_address = \
            result['current_addresses'][0]['street_line_1']
        contact.whitepages_address_two = \
            result['current_addresses'][0]['street_line_2']
        contact.whitepages_city = result['current_addresses'][0]['city']
        contact.whitepages_state = result['current_addresses'
                                          ][0]['state_code']
        contact.whitepages_country = \
            result['current_addresses'][0]['country_code']
        contact.whitepages_zip_code = \
            result['current_addresses'][0]['postal_code']
        contact.whitepages_address_type = \
            result['current_addresses'][0]['location_type']

        if result['current_addresses'][0]['lat_long']:
            contact.whitepages_latitude = \
                result['current_addresses'][0]['lat_long']['latitude']
            contact.whitepages_longitude = \
                result['current_addresses'][0]['lat_long']['longitude']
            contact.whitepages_accuracy = \
                result['current_addresses'][0]['lat_long']['accuracy']

    contact.whitepages_prepaid = result['is_prepaid']
    contact.whitepages_phone_type = result['line_type']
    contact.whitepages_commercial = result['is_commercial']

    contact.identified = True

    contact.carrier = lookup.carrier['name']
    contact.phone_number_type = lookup.carrier['type']
    contact.phone_number_friendly = lookup.national_format

    return contact


@shared_task
def send_notification_whitepages(contact_id, twilio_number):
    number = PhoneNumber.objects.get(e164=twilio_number)
    contact = Contact.objects.get(pk=contact_id)

    kwargs = {'from_': contact.phone_number,
              'to': number.e164}

    identity = render_to_string("sms_notification_whitepages_identity.html",
                                model_to_dict(contact))

    kwargs['body'] = identity
    send_whisper.apply_async(kwargs=kwargs)

    location = render_to_string("sms_notification_whitepages_location.html",
                                model_to_dict(contact))

    kwargs['body'] = location
    send_whisper.apply_async(kwargs=kwargs)

    return {'results': [identity, location]}


@shared_task
def send_whisper(from_=None, to=None, body=None):
    phone_number = PhoneNumber.objects.get(e164=to)
    contact = Contact.objects.get(phone_number=from_)

    whisper = Whisper(related_phone_number=phone_number,
                      related_contact=contact,
                      body=body)

    whisper.save()


@receiver(post_save, sender=Contact)
def identify_contact(sender, **kwargs):
    if kwargs.get('created', False):
        instance = kwargs.get('instance')

        lookup_contact \
            .apply_async(args=[instance.phone_number])
