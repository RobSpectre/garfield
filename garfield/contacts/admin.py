from django.contrib import admin

from sms.models import SmsMessage
from voice.models import Call
from deterrence.admin import DeterrenceMessageInline

from .models import Contact


admin.site.site_header = "Demand Deterrence Platform"
admin.site.site_title = admin.site.site_header
admin.site.index_title = "Dashboard"


class SmsMessageInline(admin.TabularInline):
    model = SmsMessage
    readonly_fields = ('from_number', 'to_number', 'body', 'date_created')
    list_display = ('from_number', 'to_number', 'body', 'date_created')

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1


class CallInline(admin.TabularInline):
    model = Call
    readonly_fields = ('from_number',
                       'to_number',
                       'recording_url',
                       'date_created')
    list_display = ('from_number',
                    'to_number',
                    'recording_url',
                    'date_created')

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    inlines = [SmsMessageInline, CallInline, DeterrenceMessageInline]
    search_fields = ('phone_number',
                     'whitepages_first_name',
                     'whitepages_last_name',
                     'nextcaller_first_name',
                     'nextcaller_last_name')
    list_display = ('phone_number',
                    'phone_number_friendly',
                    'date_created',
                    'whitepages_first_name',
                    'whitepages_last_name',
                    'sms_message_count',
                    'call_count',
                    'deterrents_received')
