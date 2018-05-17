from django.db.models import Count
from django.db.models import Q
from django.db.models.functions import TruncMonth

from controlcenter import Dashboard
from controlcenter import widgets

from contacts.models import Contact
from deterrence.models import DeterrenceMessage
from sms.models import SmsMessage
from voice.models import Call


class MonthlyChart(widgets.SingleBarChart):
    class Chartist:
        options = {'axisX': {'onlyInteger': True}}

    width = widgets.SMALL

    def labels(self):
        labels = []

        for item in self.queryset:
            labels.append(item['month_created'])

        return [label.strftime("%b") for label in labels]


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


class MonthlyDeterrenceMessageChart(widgets.BarChart):
    class Chartist:
        options = {"axisX": {"onlyInteger": True},
                   "stackBars": True}

    title = "Monthly Deterrence Messages"

    width = widgets.SMALL

    failed = Count('id', filter=Q(status='failed'))
    delivered = Count('id', filter=Q(status='delivered'))
    sent = Count('id', filter=Q(status='sent'))
    undelivered = Count('id', filter=Q(status='undelivered'))

    queryset = (DeterrenceMessage.objects
                .annotate(month_created=TruncMonth('date_created'))
                .order_by('month_created')
                .values('month_created')
                .annotate(delivered=delivered)
                .annotate(sent=sent)
                .annotate(undelivered=undelivered)
                .annotate(failed=failed))

    def legend(self):
        return ['failed',
                'sent',
                'delivered',
                'undelivered']

    def labels(self):
        labels = []

        for item in self.queryset:
            labels.append(item['month_created'])

        return [label.strftime("%b") for label in labels]

    def series(self):
        values = {}

        for row in self.queryset:
            values[row['month_created'].strftime("%b")] = \
                {'delivered': row['delivered'],
                 'sent': row['sent'],
                 'undelivered': row['undelivered'],
                 'failed': row['failed']}

        series = []

        for key in self.legend:
            row = []
            for label in self.labels:
                item = values.get(label, {'delivered': 0,
                                          'sent': 0,
                                          'undelivered': 0,
                                          'failed': 0})
                row.append(item[key])
            series.append(row)

        return series


class MonthlyDeterrenceResponseChart(MonthlyChart):
    title = "Monthly Deterrence Responses"

    values_list = ('month_created', 'count')

    queryset = (SmsMessage.objects
                .filter(related_phone_number__number_type='DET')
                .annotate(month_created=TruncMonth('date_created'))
                .order_by('month_created')
                .values('month_created')
                .annotate(count=Count('id')))


class TopContacts(widgets.SingleBarChart):
    class Chartist:
        options = {'horizontalBars': True,
                   'reverseData': True,
                   'axisX': {'onlyInteger': True},
                   'axisY': {'offset': 85}}

    title = "Contacts With Most Messages"

    width = widgets.LARGE

    values_list = ('related_contact__phone_number',
                   'count')

    limit_to = 14

    queryset = (SmsMessage.objects
                .values('related_contact__phone_number')
                .annotate(count=Count('sid'))
                .order_by('-count'))


class TopDeterredContacts(widgets.SingleBarChart):
    class Chartist:
        options = {'horizontalBars': True,
                   'reverseData': True,
                   'axisX': {'onlyInteger': True},
                   'axisY': {'offset': 85}}

    title = "Contacts Receiving Most Deterrents"

    width = widgets.LARGER

    values_list = ('related_contact__phone_number',
                   'count')

    limit_to = 14

    queryset = (DeterrenceMessage.objects
                .values('related_contact__phone_number')
                .annotate(count=Count('sid'))
                .order_by('-count'))


class TopContactsRespondingToDeterrence(widgets.SingleBarChart):
    class Chartist:
        options = {'horizontalBars': True,
                   'reverseData': True,
                   'axisX': {'onlyInteger': True},
                   'axisY': {'offset': 85}}

    title = "Contacts With Most Responses To Deterrence"

    width = widgets.LARGE

    values_list = ('related_contact__phone_number',
                   'count')

    limit_to = 14

    queryset = (SmsMessage.objects
                .filter(related_phone_number__number_type='DET')
                .values('related_contact__phone_number')
                .annotate(count=Count('sid'))
                .order_by('-count'))


class MonthlyDashboard(Dashboard):
    widgets = [MonthlyContactChart,
               MonthlyMessageChart,
               MonthlyCallChart,
               MonthlyDeterrenceMessageChart,
               TopDeterredContacts,
               MonthlyDeterrenceResponseChart,
               TopContacts,
               TopContactsRespondingToDeterrence]
