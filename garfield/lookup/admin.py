from django.contrib import admin

from .models import Lookup


@admin.register(Lookup)
class LookupAdmin(admin.ModelAdmin):
  pass

