from django.contrib import admin

from .models import Sim


@admin.register(Sim)
class SimAdmin(admin.ModelAdmin):
    pass
