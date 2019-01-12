import datetime
import pytz

from django.db.models import Count
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models.functions import TruncDay
from django.db.models.functions import TruncMonth

from controlcenter import Dashboard
from controlcenter import widgets

from contacts.models import Contact
from deterrence.models import DeterrenceMessage
from sms.models import SmsMessage
from voice.models import Call

from .util import daterange


class DailyScoreboard(widgets.ItemList):
    limit_to = 31
    sortable = True
    width = widgets.LARGE

    list_display = ['Date',
                    'Contacts',
                    'SMS Messages',
                    'Calls',
                    'Deterrents',
                    'Undelivered',
                    'Contacts w/ Name',
                    'Contacts w/ Name & Address']

    period = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=30)

    contacts = (Contact.objects
                .filter(date_created__gte=period)
                .annotate(date=TruncDay('date_created'))
                .values('date')
                .annotate(count=Count('id')))

    sms_messages = (SmsMessage.objects
                    .filter(date_created__gte=period)
                    .filter(related_phone_number__number_type='ADV')
                    .annotate(date=TruncDay('date_created'))
                    .values('date')
                    .annotate(count=Count('id')))

    calls = (Call.objects
             .filter(date_created__gte=period)
             .filter(related_phone_number__number_type='ADV')
             .annotate(date=TruncDay('date_created'))
             .values('date')
             .annotate(count=Count('id')))

    deterrents = (DeterrenceMessage.objects
                  .filter(date_created__gte=period)
                  .annotate(date=TruncDay('date_created'))
                  .values('date')
                  .annotate(count=Count('id')))

    undelivered = (DeterrenceMessage.objects
                   .filter(date_created__gte=period)
                   .filter(status='undelivered')
                   .annotate(date=TruncDay('date_created'))
                   .values('date')
                   .annotate(count=Count('id')))

    contacts_with_name = (Contact.objects
                          .filter(date_created__gte=period)
                          .filter(whitepages_last_name__isnull=False)
                          .annotate(date=TruncDay('date_created'))
                          .values('date')
                          .annotate(count=Count('id')))

    contacts_with_address = (Contact.objects
                             .filter(date_created__gte=period)
                             .filter(whitepages_last_name__isnull=False)
                             .filter(whitepages_address__isnull=False)
                             .annotate(date=TruncDay('date_created'))
                             .values('date')
                             .annotate(count=Count('id')))

    def dates(self):
        return daterange(self.period,
                         datetime.datetime.now(tz=pytz.utc))

    def get_queryset(self):
        values = {}
        dates = []

        for date in self.dates():
            dates.append(date)
            values[date] = {'Contacts': 0,
                            'SMS Messages': 0,
                            'Calls': 0,
                            'Deterrents': 0,
                            'Undelivered': 0,
                            'Contacts w/ Name': 0,
                            'Contacts w/ Name & Address': 0}

        for i, queryset in enumerate([self.contacts,
                                      self.sms_messages,
                                      self.calls,
                                      self.deterrents,
                                      self.undelivered,
                                      self.contacts_with_name,
                                      self.contacts_with_address]):
            for row in queryset:
                values[row['date']][self.list_display[i + 1]] = \
                    row['count']

        series = []

        for date in dates:
            if values[date]['Deterrents'] == 0 or \
               values[date]['Undelivered'] == 0:
                undelivered = 0
            else:
                undelivered = (values[date]['Undelivered'] /
                               values[date]['Deterrents'])

            if values[date]['Contacts'] == 0 or \
               values[date]['Contacts w/ Name'] == 0:
                contacts_with_name = 0
            else:
                contacts_with_name = (values[date]['Contacts w/ Name'] /
                                      values[date]['Contacts'])

            if values[date]['Contacts'] == 0 or \
               values[date]['Contacts w/ Name & Address'] == 0:
                contacts_with_address = 0
            else:
                contacts_with_address = \
                    (values[date]['Contacts w/ Name & Address'] /
                     values[date]['Contacts'])

            item = {'Date': date,
                    'Contacts': values[date]['Contacts'],
                    'SMS Messages': values[date]['SMS Messages'],
                    'Calls': values[date]['Calls'],
                    'Deterrents': values[date]['Deterrents'],
                    'Undelivered': "{0:.0%}"
                                   "".format(undelivered),
                    'Contacts w/ Name': "{0:.0%}"
                                        "".format(contacts_with_name),
                    'Contacts w/ Name '
                    '& Address': "{0:.0%}"
                                 "".format(contacts_with_address)}
            series.append(item)

        return series


class MonthlyScoreboard(widgets.ItemList):
    limit_to = 13
    sortable = True
    width = widgets.LARGE

    list_display = ['Date',
                    'Contacts',
                    'SMS Messages',
                    'Calls',
                    'Deterrents',
                    'Undelivered',
                    'Contacts w/ Name',
                    'Contacts w/ Name & Address',
                    'Responded to Deterrent']

    period = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=365)

    contacts = (Contact.objects
                .filter(date_created__gte=period)
                .annotate(date=TruncMonth('date_created'))
                .values('date')
                .annotate(count=Count('id')))

    sms_messages = (SmsMessage.objects
                    .filter(date_created__gte=period)
                    .filter(related_phone_number__number_type='ADV')
                    .annotate(date=TruncMonth('date_created'))
                    .values('date')
                    .annotate(count=Count('id')))

    calls = (Call.objects
             .filter(date_created__gte=period)
             .filter(related_phone_number__number_type='ADV')
             .annotate(date=TruncMonth('date_created'))
             .values('date')
             .annotate(count=Count('id')))

    deterrents = (DeterrenceMessage.objects
                  .filter(date_created__gte=period)
                  .annotate(date=TruncMonth('date_created'))
                  .values('date')
                  .annotate(count=Count('id')))

    undelivered = (DeterrenceMessage.objects
                   .filter(date_created__gte=period)
                   .filter(status='undelivered')
                   .annotate(date=TruncMonth('date_created'))
                   .values('date')
                   .annotate(count=Count('id')))

    contacts_with_name = (Contact.objects
                          .filter(date_created__gte=period)
                          .filter(whitepages_last_name__isnull=False)
                          .annotate(date=TruncMonth('date_created'))
                          .values('date')
                          .annotate(count=Count('id')))

    contacts_with_address = (Contact.objects
                             .filter(date_created__gte=period)
                             .filter(whitepages_last_name__isnull=False)
                             .filter(whitepages_address__isnull=False)
                             .annotate(date=TruncMonth('date_created'))
                             .values('date')
                             .annotate(count=Count('id')))

    respondents = \
        (SmsMessage.objects
         .filter(date_created__gte=period)
         .filter(related_phone_number__number_type='DET')
         .annotate(date=TruncMonth('date_created'))
         .filter(related_contact__id__in=Subquery(
             Contact
             .objects
             .filter(date_created__gte=OuterRef('date'))
             .values('id')))
         .values('date')
         .annotate(count=Count('related_contact__id',
                               distinct=True)))

    def dates(self):
        return [row['date'] for row in self.contacts.order_by('date')]

    def get_queryset(self):
        values = {}
        dates = []

        for date in self.dates():
            dates.append(date)
            values[date] = {'Contacts': 0,
                            'SMS Messages': 0,
                            'Calls': 0,
                            'Deterrents': 0,
                            'Undelivered': 0,
                            'Contacts w/ Name': 0,
                            'Contacts w/ Name & Address': 0,
                            'Responded to Deterrent': 0}

        for i, queryset in enumerate([self.contacts,
                                      self.sms_messages,
                                      self.calls,
                                      self.deterrents,
                                      self.undelivered,
                                      self.contacts_with_name,
                                      self.contacts_with_address,
                                      self.respondents]):
            for row in queryset:
                values[row['date']][self.list_display[i + 1]] = \
                    row['count']

        series = []

        for date in dates:
            if values[date]['Deterrents'] == 0 or \
               values[date]['Undelivered'] == 0:
                undelivered = 0
            else:
                undelivered = (values[date]['Undelivered'] /
                               values[date]['Deterrents'])

            if values[date]['Contacts'] == 0 or \
               values[date]['Contacts w/ Name'] == 0:
                contacts_with_name = 0
            else:
                contacts_with_name = (values[date]['Contacts w/ Name'] /
                                      values[date]['Contacts'])

            if values[date]['Contacts'] == 0 or \
               values[date]['Contacts w/ Name & Address'] == 0:
                contacts_with_address = 0
            else:
                contacts_with_address = \
                    (values[date]['Contacts w/ Name & Address'] /
                     values[date]['Contacts'])

            if values[date]['Contacts'] == 0 or \
               values[date]['Responded to Deterrent'] == 0:
                responded_to_deterrent = 0
            else:
                responded_to_deterrent = \
                    (values[date]['Responded to Deterrent'] /
                     values[date]['Contacts'])

            item = {'Date': date,
                    'Contacts': values[date]['Contacts'],
                    'SMS Messages': values[date]['SMS Messages'],
                    'Calls': values[date]['Calls'],
                    'Deterrents': values[date]['Deterrents'],
                    'Undelivered': "{0:.0%}"
                                   "".format(undelivered),
                    'Contacts w/ Name': "{0:.0%}"
                                        "".format(contacts_with_name),
                    'Contacts w/ Name '
                    '& Address': "{0:.0%}"
                                 "".format(contacts_with_address),
                    'Responded to '
                    'Deterrent': "{0:.0%}"
                                 "".format(responded_to_deterrent)}
            series.append(item)

        return series


class Scoreboard(Dashboard):
    widgets = [DailyScoreboard,
               MonthlyScoreboard]
