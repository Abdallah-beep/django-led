from django.contrib import admin
from .models import DeviceCommand
@admin.register(DeviceCommand)
class DeviceCommandAdmin(admin.ModelAdmin):
    list_display = ("device_id", "led_state", "updated_at")
    list_editable = ("led_state",)
