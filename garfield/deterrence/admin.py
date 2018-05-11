from django.contrib import admin

from contacts.models import Contact

from .models import Deterrent
from .models import DeterrenceCampaign
from .models import DeterrenceMessage


class DeterrenceMessageInline(admin.TabularInline):
    model = DeterrenceMessage
    readonly_fields = ('date_created',
                       'status',
                       'related_phone_number',
                       'related_contact',
                       'body',
                       'related_deterrent')

    list_display = readonly_fields
    exclude = ['sid', 'deleted']

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        else:
            return 1


@admin.register(Deterrent)
class DeterrentAdmin(admin.ModelAdmin):
    pass


@admin.register(DeterrenceCampaign)
class DeterrenceCampaignAdmin(admin.ModelAdmin):
    inlines = [DeterrenceMessageInline]


@admin.register(DeterrenceMessage)
class DeterrenceMessage(admin.ModelAdmin):
    pass
