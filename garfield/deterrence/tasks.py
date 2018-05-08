from celery import shared_task

from phone_numbers.models import PhoneNumber
from contacts.models import Contact

from sms.tasks import send_sms_message


@shared_task
def send_deterrence(absolute_uri, message):
    deterrence_number = \
        PhoneNumber.objects.filter(number_type="DET") \
        .latest("date_created")

    for contact in Contact.objects.all():
        if contact.do_not_deter or contact.deterred or contact.arrested \
                or contact.recruiter:
            continue

        if contact.whitepages_first_name:
            kwargs = {"from_": deterrence_number.e164,
                      "to": contact.phone_number,
                      "body": "{0}, a message from NY"
                              "PD.".format(contact.whitepages_first_name),
                      "media_url": "https://berserk-sleet-3229.twil.io/"
                                   "assets/john_deterrent.jpg"}
        else:
            kwargs = {"from_": deterrence_number.e164,
                      "to": contact.phone_number,
                      "body": "A message from NYPD.",
                      "media_url": "https://berserk-sleet-3229.twil.io/"
                                   "assets/john_deterrent.jpg"}

        send_sms_message.apply_async(kwargs=kwargs)

        contact.deterred = True
        contact.save(update_fields=['deterred'])
