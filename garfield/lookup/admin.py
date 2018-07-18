from django.contrib import admin

from .models import Lookup


@admin.register(Lookup)
class LookupAdmin(admin.ModelAdmin):
  list_display = ('officer_phone_number', 'contact_phone_number', 'related_contact')

