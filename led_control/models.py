from django.db import models


class DeviceCommand(models.Model):
    device_id = models.CharField(max_length=50, unique=True)
    led_state = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device_id} - LED {'ON' if self.led_state else 'OFF'}"

    class Meta:
        verbose_name = "Commande appareil"
        verbose_name_plural = "Commandes appareils"
