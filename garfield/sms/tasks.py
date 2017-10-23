from base64 import b64encode
import json

from celery import shared_task

from django.conf import settings

from twilio.rest import Client

from phone_numbers.models import PhoneNumber
from johns.models import John

from .models import SmsMessage


@shared_task
def save_sms_message(message):
    record = SmsMessage(sid=message['MessageSid'],
                        from_number=message['From'],
                        to_number=message['To'],
                        body=message['Body'])
    record.save()

    if "sim" in message['From']:
        result = \
            SmsMessage.objects.filter(from_number=message['To']) \
            .latest('date_created')
        if result:
            record.related_phone_number = result
            record.save()
    else:
        phone_number = \
            PhoneNumber.objects.filter(e164=message['To']) \
            .latest('date_created')
        if phone_number:
            record.related_phone_number = phone_number
            record.save()

        check_john.apply_async(args=[message])


@shared_task
def send_sms_message(from_=None, to=None, body=None):
    client = Client(settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN)
    client.messages.create(to,
                           from_=from_,
                           body=body)


@shared_task
def send_whisper(from_=None, to=None, body=None):
    whisper = {"To": to,
               "From": from_,
               "Body": body}

    whisper_json = json.dumps(whisper)

    send_sms_message(from_=settings.TWILIO_WHISPER_NUMBER,
                     to=settings.TWILIO_PHONE_NUMBER,
                     body="whisper:{0}".format(whisper_json))


@shared_task
def check_john(message):
    result = \
        John.objects.filter(phone_number=message['From'])

    if not result:
        john = John(phone_number=message['From'])

        john.save()
        lookup_john.apply_async(args=[message['From'],
                                      message['To']])
    elif not result[0].identified:
        lookup_john.apply_async(args=[message['From'],
                                      message['To']])


@shared_task
def lookup_john(john_number, twilio_number):
    john = John.objects.get(phone_number=john_number)

    lookup_john_whitepages.apply_async(args=[john.id, twilio_number])
    # lookup_john_nextcaller.apply_async(args=[john.id, twilio_number])


@shared_task
def lookup_john_whitepages(john_id, twilio_number):
    john = John.objects.get(pk=john_id)
    add_on = "whitepages_pro_caller_id"

    client = Client(settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN)

    lookup = \
        client.lookups.phone_numbers(john.phone_number) \
        .fetch(add_ons=add_on, type="carrier")

    if lookup.add_ons['status'] == 'successful':
        result = lookup.add_ons['results'][add_on]['result']

        if result['belongs_to']:
            john.whitepages_first_name = result['belongs_to'][0]['firstname']
            john.whitepages_middle_name = result['belongs_to'][0]['middlename']
            john.whitepages_last_name = result['belongs_to'][0]['lastname']
            john.whitepages_gender = result['belongs_to'][0]['gender']

        if result['current_addresses']:
            john.whitepages_address = \
                result['current_addresses'][0]['street_line_1']
            john.whitepages_address_two = \
                result['current_addresses'][0]['street_line_2']
            john.whitepages_city = result['current_addresses'][0]['city']
            john.whitepages_state = result['current_addresses'
                                           ''][0]['state_code']
            john.whitepages_country = \
                result['current_addresses'][0]['country_code']
            john.whitepages_zip_code = \
                result['current_addresses'][0]['postal_code']
            john.whitepages_address_type = \
                result['current_addresses'][0]['location_type']

            if result['current_addresses'][0]['lat_long']:
                john.whitepages_latitude = \
                    result['current_addresses'][0]['lat_long']['latitude']
                john.whitepages_longitude = \
                    result['current_addresses'][0]['lat_long']['longitude']
                john.whitepages_accuracy = \
                    result['current_addresses'][0]['lat_long']['accuracy']

        john.whitepages_prepaid = result['is_prepaid']
        john.whitepages_phone_type = result['line_type']
        john.whitepages_commercial = result['is_commercial']

        john.identified = True

    john.carrier = lookup.carrier['name']
    john.phone_number_type = lookup.carrier['type']
    john.phone_number_friendly = lookup.national_format

    john.save()

    if lookup.add_ons['status'] == 'successful':
        send_notification_whitepages.apply_async(args=[john.id,
                                                       twilio_number])


@shared_task
def send_notification_whitepages(john_id, twilio_number):
    number = PhoneNumber.objects.get(e164=twilio_number)
    john = John.objects.get(pk=john_id)

    body = """[WhitePages Info]
    ===
    Name: {0} {1} {2}
    Carrier: {8}
    Phone Type: {9}
    Address:
    {3}
    {4}
    {5}, {6} {7}
    """.format(john.whitepages_first_name,
               john.whitepages_middle_name,
               john.whitepages_last_name,
               john.whitepages_address,
               john.whitepages_address_two,
               john.whitepages_city,
               john.whitepages_state,
               john.whitepages_zip_code,
               john.carrier,
               john.phone_number_type)

    kwargs = {'from_': john.phone_number,
              'to': "sim:{0}".format(number.related_sim.sid),
              'body': body}

    send_whisper.apply_async(kwargs=kwargs)
