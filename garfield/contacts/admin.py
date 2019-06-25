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
    readonly_fields = ('date_created',
                       'from_number',
                       'to_number',
                       'body',
                       'related_phone_number')
    exclude = ('deleted',
               'sid')
    can_delete = False

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1

    def get_queryset(self, request):
        queryset = super(SmsMessageInline, self).get_queryset(request)
        return queryset.filter(related_phone_number__number_type='ADV')


class CallInline(admin.TabularInline):
    model = Call
    readonly_fields = ('date_created',
                       'from_number',
                       'to_number',
                       'related_phone_number',
                       'duration')
    exclude = ('deleted',
               'sid',
               'recording_url')
    can_delete = False

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1


class DeterrenceSmsResponsesInline(admin.TabularInline):
    model = SmsMessage
    readonly_fields = ('date_created',
                       'from_number',
                       'to_number',
                       'body',
                       'related_phone_number')
    list_display = ('from_number', 'to_number', 'body', 'date_created')
    exclude = ('deleted',
               'sid')
    can_delete = False

    verbose_name = "Deterrence Response via SMS"
    verbose_name_plural = "Deterrence Responses via SMS"

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1

    def get_queryset(self, request):
        queryset = super(DeterrenceSmsResponsesInline,
                         self).get_queryset(request)
        return queryset.filter(related_phone_number__number_type='DET')


class DeterrenceCallResponsesInline(admin.TabularInline):
    model = Call
    readonly_fields = ('date_created',
                       'from_number',
                       'to_number',
                       'related_phone_number',
                       'duration')
    exclude = ('deleted',
               'sid',
               'recording_url')
    can_delete = False

    verbose_name = "Deterrence Response via Phone Call"
    verbose_name_plural = "Deterrence Responses via Phone Call"

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1

    def get_queryset(self, request):
        queryset = super(DeterrenceCallResponsesInline,
                         self).get_queryset(request)
        return queryset.filter(related_phone_number__number_type='DET')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    inlines = [SmsMessageInline,
               CallInline,
               DeterrenceMessageInline,
               DeterrenceSmsResponsesInline,
               DeterrenceCallResponsesInline]
    search_fields = ('phone_number',
                     'phone_number_friendly',
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
