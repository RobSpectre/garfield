import datetime

from django.db.models import Count
from django.db.models.functions import TruncDay

from controlcenter import Dashboard
from controlcenter import widgets

from contacts.models import Contact
from deterrence.models import DeterrenceMessage
from sms.models import SmsMessage
from voice.models import Call

from .util import daterange


class DailyScoreboardTable(widgets.ItemList):
    limit_to = 21
    sortable = True
    list_display = ['Date',
                    'Contacts',
                    'SMS Messages',
                    'Calls',
                    'Deterrents']

    period = datetime.date.today() - datetime.timedelta(days=limit_to)

    contacts = (Contact.objects
                .filter(date_created__gt=period)
                .annotate(date=TruncDay('date_created'))
                .values('date')
                .annotate(count=Count('id')))

    sms_messages = (SmsMessage.objects
                    .filter(date_created__gt=period)
                    .filter(related_phone_number__number_type='ADV')
                    .annotate(date=TruncDay('date_created'))
                    .values('date')
                    .annotate(count=Count('id')))

    calls = (Call.objects
             .filter(date_created__gt=period)
             .filter(related_phone_number__number_type='ADV')
             .annotate(date=TruncDay('date_created'))
             .values('date')
             .annotate(count=Count('id')))

    deterrents = (DeterrenceMessage.objects
                  .filter(date_created__gt=period)
                  .annotate(date=TruncDay('date_created'))
                  .values('date')
                  .annotate(count=Count('id')))

    def dates(self):
        return daterange(self.period,
                         datetime.date.today() + datetime.timedelta(days=1))

    def get_queryset(self):
        values = {}
        dates = []

        for date in self.dates():
            dates.append(date)
            values[date] = {'Contacts': 0,
                            'SMS Messages': 0,
                            'Calls': 0,
                            'Deterrents': 0}

        for i, queryset in enumerate([self.contacts,
                                      self.sms_messages,
                                      self.calls,
                                      self.deterrents]):
            for row in queryset:
                values[row['date'].date()][self.list_display[i + 1]] = \
                    row['count']

        series = []

        for date in dates:
            item = {'Date': date,
                    'Contacts': values[date]['Contacts'],
                    'SMS Messages': values[date]['SMS Messages'],
                    'Calls': values[date]['Calls'],
                    'Deterrents': values[date]['Deterrents']}
            series.append(item)

        return series


class DailyScoreboard(Dashboard):
    widgets = [DailyScoreboardTable]
