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
            record.related_phone_number = result.related_phone_number
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

    return client.messages.create(to,
                                  from_=from_,
                                  body=body)


@shared_task
def lookup_phone_number(phone_number, type=None, addons=None):
    client = Client(settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN)

    return client.lookups.phone_numbers(phone_number).fetch(add_ons=addons,
                                                            type=type)


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
    lookup_john_nextcaller.apply_async(args=[john.id, twilio_number])


@shared_task
def lookup_john_whitepages(john_id, twilio_number):
    john = John.objects.get(pk=john_id)

    lookup = lookup_phone_number(john.phone_number,
                                 type="carrier",
                                 addons="whitepages_pro_caller_id")

    if lookup.add_ons['status'] == 'successful':
        john = apply_lookup_whitepages_to_john(john, lookup)

        john.save()

    if lookup.add_ons['status'] == 'successful':
        send_notification_whitepages.apply_async(args=[john.id,
                                                       twilio_number])


def apply_lookup_whitepages_to_john(john, lookup):
    result = lookup.add_ons['results']["whitepages_pro_caller_id"]['result']

    if result['belongs_to']:
        john.whitepages_entity_type = result['belongs_to'][0]['type']

        if john.whitepages_entity_type == "Person":
            john.whitepages_first_name = result['belongs_to'][0]['firstname']
            john.whitepages_middle_name = result['belongs_to'][0]['middlename']
            john.whitepages_last_name = result['belongs_to'][0]['lastname']
            john.whitepages_gender = result['belongs_to'][0]['gender']
        else:
            john.whitepages_business_name = result['belongs_to'][0]['name']

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

    return john


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

    return body


@shared_task
def lookup_john_nextcaller(john_id, twilio_number):
    john = John.objects.get(pk=john_id)

    lookup = lookup_phone_number(john.phone_number,
                                 addons="nextcaller_advanced_caller_id")

    if lookup.add_ons['status'] == 'successful':
        john = apply_lookup_nextcaller_to_john(john, lookup)

        john.save()

    if lookup.add_ons['status'] == 'successful':
        send_notification_nextcaller.apply_async(args=[john.id,
                                                       twilio_number])


def apply_lookup_nextcaller_to_john(john, lookup):
    result = lookup.add_ons['results'
                            ]['nextcaller_advanced_caller_id']['result']

    if result['records']:
        result = result['records'][0]

        john.nextcaller_email = result['email']

        john.nextcaller_first_name = result['first_name']
        john.nextcaller_middle_name = result['middle_name']
        john.nextcaller_last_name = result['last_name']
        john.nextcaller_gender = result['gender']
        john.nextcaller_age = result['age']

        if not result['first_name'] and not result['last_name']:
            john.nextcaller_business_name = result['name']

        john.nextcaller_marital_status = result['marital_status']
        john.nextcaller_home_owner_status = result['home_owner_status']
        john.nextcaller_education = result['education']
        john.nextcaller_household_income = result['household_income']
        john.nextcaller_length_of_residence = result['length_of_residence']
        john.nextcaller_market_value = result['market_value']
        john.nextcaller_occupation = result['occupation']

        if result['presence_of_children'] == 'Yes':
            john.nextcaller_children_presence = True
        else:
            john.nextcaller_children_presence = False

        if result['high_net_worth'] == 'Yes':
            john.nextcaller_high_net_worth = True
        else:
            john.nextcaller_high_net_worth = False

        if result['address']:
            john.nextcaller_address = result['address'][0]['line1']
            john.nextcaller_address_two = result['address'][0]['line2']
            john.nextcaller_city = result['address'][0]['city']
            john.nextcaller_state = result['address'][0]['state']
            john.nextcaller_country = result['address'][0]['country']
            john.nextcaller_zip_code = result['address'][0]['zip_code']

        if result['phone']:
            john.nextcaller_phone_type = result['phone'][0]['line_type']
            john.nextcaller_carrier = result['phone'][0]['carrier']

        for link in result['social_links']:
            if link['type'] == 'facebook':
                john.nextcaller_facebook = link['url']
            elif link['type'] == 'twitter':
                john.nextcaller_twitter = link['url']
            elif link['type'] == 'linkedin':
                john.nextcaller_linkedin = link['url']

        john.identified = True

    return john


@shared_task
def send_notification_nextcaller(john_id, twilio_number):
    number = PhoneNumber.objects.get(e164=twilio_number)
    john = John.objects.get(pk=john_id)

    body = """[NextCaller Info]
    ===
    Name: {0} {1} {2}
    Carrier: {8}
    Phone Type: {9}
    Address:
    {3}
    {4}
    {5}, {6} {7}
    """.format(john.nextcaller_first_name,
               john.nextcaller_middle_name,
               john.nextcaller_last_name,
               john.nextcaller_address,
               john.nextcaller_address_two,
               john.nextcaller_city,
               john.nextcaller_state,
               john.nextcaller_zip_code,
               john.nextcaller_carrier,
               john.nextcaller_phone_type)

    kwargs = {'from_': john.phone_number,
              'to': "sim:{0}".format(number.related_sim.sid),
              'body': body}

    send_whisper.apply_async(kwargs=kwargs)

    return body
