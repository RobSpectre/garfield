from django.db.models import Count
from django.db.models.functions import TruncMonth

from controlcenter import Dashboard
from controlcenter import widgets

from contacts.models import Contact
from sms.models import SmsMessage
from voice.models import Call


class MonthlyChart(widgets.SingleBarChart):
    class Chartist:
        options = {'axisX': {'onlyInteger': True}}

    width = widgets.SMALL


class MonthlyContactChart(MonthlyChart):
    title = "Monthly Contact Volume"

    values_list = ('month_created', 'count')

    queryset = (Contact.objects
                .annotate(month_created=TruncMonth('date_created'))
                .order_by('month_created')
                .values('month_created')
                .annotate(count=Count('id')))


class MonthlyMessageChart(MonthlyChart):
    title = "Monthly Message Volume"

    values_list = ('month_created', 'count')

    queryset = (SmsMessage.objects
                .filter(related_phone_number__number_type='ADV')
                .annotate(month_created=TruncMonth('date_created'))
                .order_by('month_created')
                .values('month_created')
                .annotate(count=Count('id')))


class MonthlyCallChart(MonthlyChart):
    title = "Monthly Call Volume"

    values_list = ('month_created', 'count')

    queryset = (Call.objects
                .filter(related_phone_number__number_type='ADV')
                .annotate(month_created=TruncMonth('date_created'))
                .order_by('month_created')
                .values('month_created')
                .annotate(count=Count('id')))


class MonthlyDeterrenceChart(MonthlyChart):
    title = "Monthly Deterrence Responses"

    values_list = ('month_created', 'count')

    queryset = (SmsMessage.objects
                .filter(related_phone_number__number_type='DET')
                .annotate(month_created=TruncMonth('date_created'))
                .values('month_created')
                .annotate(count=Count('id')))


class TopContacts(MonthlyChart):
    class Chartist:
        options = {'horizontalBars': True,
                   'reverseData': True,
                   'axisX': {'onlyInteger': True},
                   'axisY': {'offset': 85}}

    title = "Contacts With Most Messages"

    width = widgets.LARGER

    values_list = ('related_contact__phone_number',
                   'count')

    limit_to = 14

    queryset = (SmsMessage.objects
                .values('related_contact__phone_number')
                .annotate(count=Count('sid'))
                .order_by('-count'))


class MonthlyDashboard(Dashboard):
    widgets = [MonthlyContactChart,
               MonthlyMessageChart,
               MonthlyCallChart,
               MonthlyDeterrenceChart,
               TopContacts]
