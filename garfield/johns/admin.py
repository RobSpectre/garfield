from django.contrib import admin

from sms.models import SmsMessage
from voice.models import Call

from .models import John


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


@admin.register(John)
class JohnAdmin(admin.ModelAdmin):
    inlines = [SmsMessageInline, CallInline]
