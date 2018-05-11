import datetime

from django.contrib import admin

from sms.models import SmsMessage
from voice.models import Call

from .models import PhoneNumber


class SmsMessageInline(admin.TabularInline):
    model = SmsMessage
    readonly_fields = ('related_contact',
                       'from_number',
                       'to_number',
                       'body',
                       'date_created')
    # list_display = readonly_fields
    list_display_links = ('related_contact',
                          'date_created')
    exclude = ['sid', 'deleted']

    def get_queryset(self, request):
        qs = super(SmsMessageInline, self).get_queryset(request)
        threedaysago = datetime.datetime.today() - datetime.timedelta(days=3)

        return qs.filter(date_created__gt=threedaysago) \
            .order_by('-date_created')

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1


class CallInline(admin.TabularInline):
    model = Call
    readonly_fields = ('related_contact',
                       'from_number',
                       'to_number',
                       'recording_url',
                       'date_created',
                       'duration')
    list_display = readonly_fields
    list_display_links = ('related_contact', 'date_created')
    exclude = ['sid']

    def get_queryset(self, request):
        qs = super(CallInline, self).get_queryset(request)
        threedaysago = datetime.datetime.today() - datetime.timedelta(days=3)

        return qs.filter(date_created__gt=threedaysago) \
            .order_by('-date_created')

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    inlines = [SmsMessageInline, CallInline]
