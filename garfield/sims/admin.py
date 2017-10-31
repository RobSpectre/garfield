from django.contrib import admin

from .models import Sim
from .models import Whisper


@admin.register(Sim)
class SimAdmin(admin.ModelAdmin):
    pass


@admin.register(Whisper)
class WhisperAdmin(admin.ModelAdmin):
    pass
