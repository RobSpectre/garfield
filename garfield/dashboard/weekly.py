import datetime

from django.db.models import Count
from django.db.models.functions import TruncDay

from controlcenter import Dashboard
from controlcenter import widgets

from contacts.models import Contact
from sms.models import SmsMessage
from voice.models import Call

from .util import daterange_by_week


class ContactList(widgets.ItemList):
    title = "This Week's Contacts"
    model = Contact

    width = widgets.FULL

    queryset = \
        Contact.objects.filter(date_created__week=datetime
                               .datetime
                               .today()
                               .isocalendar()[1]) \
                       .order_by('-date_created')
    list_display = ('date_created',
                    'phone_number',
                    'whitepages_first_name',
                    'whitepages_last_name',
                    'nextcaller_first_name',
                    'nextcaller_last_name')

    list_display_links = ('phone_number')
    sortable = True
    limit_to = None

    empty_message = "No contacts so far this week."


class LatestMessagesList(widgets.ItemList):
    title = "Latest Messages"

    model = SmsMessage

    width = widgets.LARGER

    queryset = (SmsMessage.objects
                .filter(date_created__gt=datetime.date.today())
                .filter(related_phone_number__number_type='ADV')
                .order_by('-date_created'))

    limit_to = 20

    list_display = ('date_created',
                    'related_contact',
                    'related_phone_number',
                    'to_number',
                    'from_number',
                    'body')

    list_display_links = ('date_created',
                          'related_contact',
                          'related_phone_number')


class LatestCallsList(widgets.ItemList):
    title = "Latest Calls"

    model = Call

    width = widgets.SMALL

    queryset = (Call.objects
                .filter(date_created__gt=datetime.date.today())
                .filter(related_phone_number__number_type='ADV')
                .order_by('-date_created')[:20])

    list_display = ('date_created',
                    'to_number',
                    'from_number')

    list_display_links = ('date_created',
                          'related_contact',
                          'related_phone_number')


class DailyChart(widgets.SingleBarChart):
    class Chartist:
        options = {"axisX": {"onlyInteger": True}}

    width = widgets.SMALL

    iso_today = datetime.datetime.today().isocalendar()

    def labels(self):
        labels = daterange_by_week(self.iso_today[0],
                                   self.iso_today[1])

        return [label.strftime("%d %b") for label in labels]


class ContactChart(DailyChart):
    title = "Daily Contact Volume"

    def series(self):
        queryset = (Contact.objects
                    .filter(date_created__week=self.iso_today[1])
                    .annotate(day_created=TruncDay('date_created'))
                    .values('day_created')
                    .annotate(count=Count('id')))

        values = {}

        for row in queryset:
            values[row['day_created']] = row['count']

        dates = daterange_by_week(self.iso_today[0],
                                  self.iso_today[1])

        series = []

        for date in dates:
            item = values.get(date, 0)
            series.append(item)

        return series


class SmsMessageChart(DailyChart):
    title = "Daily Message Volume"

    def series(self):
        queryset = (SmsMessage.objects
                    .filter(date_created__week=self.iso_today[1])
                    .filter(related_phone_number__number_type='ADV')
                    .annotate(day_created=TruncDay('date_created'))
                    .values('day_created')
                    .annotate(count=Count('id')))

        values = {}

        for row in queryset:
            values[row['day_created']] = row['count']

        dates = daterange_by_week(self.iso_today[0],
                                  self.iso_today[1])

        series = []

        for date in dates:
            item = values.get(date, 0)
            series.append(item)

        return series


class CallChart(DailyChart):
    title = "Daily Call Volume"

    def series(self):
        queryset = (Call.objects
                    .filter(date_created__week=self.iso_today[1])
                    .filter(related_phone_number__number_type='ADV')
                    .annotate(day_created=TruncDay('date_created'))
                    .values('day_created')
                    .annotate(count=Count('id')))

        values = {}

        for row in queryset:
            values[row['day_created']] = row['count']

        dates = daterange_by_week(self.iso_today[0],
                                  self.iso_today[1])

        series = []

        for date in dates:
            item = values.get(date, 0)
            series.append(item)

        return series


class DeterrenceChart(DailyChart):
    title = "Daily Deterrence Responses"

    def series(self):
        queryset = (SmsMessage.objects
                    .filter(date_created__week=self.iso_today[1])
                    .filter(related_phone_number__number_type='DET')
                    .annotate(day_created=TruncDay('date_created'))
                    .values('day_created')
                    .annotate(count=Count('id')))

        values = {}

        for row in queryset:
            values[row['day_created']] = row['count']

        dates = daterange_by_week(self.iso_today[0],
                                  self.iso_today[1])

        series = []

        for date in dates:
            item = values.get(date, 0)
            series.append(item)

        return series


class WeeklyDashboard(Dashboard):
    widgets = (ContactChart,
               SmsMessageChart,
               CallChart,
               DeterrenceChart,
               LatestMessagesList,
               LatestCallsList,
               ContactList)
