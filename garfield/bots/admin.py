from django.contrib import admin

from bots.models import Bot


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    pass
