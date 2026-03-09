from django.urls import path
from . import views
urlpatterns = [
    path("", views.dashboard),
    path("api/led/<str:device_id>/", views.get_led_command),
    path("api/led/<str:device_id>/<str:state>/", views.set_led_command),
    path("api/devices/", views.list_devices),
]
