from django.contrib import admin
from .models import John


@admin.register(John)
class JohnAdmin(admin.ModelAdmin):
    pass
