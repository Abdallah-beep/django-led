from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from .models import DeviceCommand


def dashboard(request):
    """Page HTML pour piloter la LED depuis un navigateur."""
    devices = DeviceCommand.objects.all()
    return render(request, "led_control/dashboard.html", {"devices": devices})


@require_http_methods(["GET"])
def get_led_command(request, device_id):
    """
    API lue par l'ESP32 pour connaître l'état voulu de la LED.
    GET /api/led/<device_id>/
    Réponse : {"device_id": "ttgo01", "led": true}
    """
    obj, created = DeviceCommand.objects.get_or_create(device_id=device_id)
    return JsonResponse({
        "device_id": obj.device_id,
        "led": obj.led_state,
        "updated_at": obj.updated_at.isoformat(),
    })


@csrf_exempt
@require_http_methods(["GET", "POST"])
def set_led_command(request, device_id, state):
    """
    API pour changer l'état de la LED.
    GET ou POST /api/led/<device_id>/on/
    GET ou POST /api/led/<device_id>/off/
    """
    if state.lower() not in ("on", "off"):
        return JsonResponse({"error": "État invalide. Utilisez 'on' ou 'off'."}, status=400)

    obj, created = DeviceCommand.objects.get_or_create(device_id=device_id)
    obj.led_state = (state.lower() == "on")
    obj.save()

    return JsonResponse({
        "device_id": obj.device_id,
        "led": obj.led_state,
        "message": f"LED mise à {'ON' if obj.led_state else 'OFF'}",
        "updated_at": obj.updated_at.isoformat(),
    })


@require_http_methods(["GET"])
def list_devices(request):
    """Liste tous les appareils enregistrés."""
    devices = DeviceCommand.objects.all().values("device_id", "led_state", "updated_at")
    return JsonResponse({"devices": list(devices)})
