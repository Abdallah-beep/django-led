import os

# config/settings.py
os.makedirs("config", exist_ok=True)
os.makedirs("led_control", exist_ok=True)
os.makedirs("led_control/templates/led_control", exist_ok=True)

with open("config/settings.py", "w", encoding="utf-8") as f:
    f.write("""from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-changez-moi"
DEBUG = True
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "led_control",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates","DIRS": [],"APP_DIRS": True,"OPTIONS": {"context_processors": ["django.template.context_processors.debug","django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3","NAME": BASE_DIR / "db.sqlite3"}}
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
""")

with open("config/__init__.py", "w") as f:
    f.write("")

with open("config/urls.py", "w", encoding="utf-8") as f:
    f.write("""from django.contrib import admin
from django.urls import path, include
urlpatterns = [path("admin/", admin.site.urls), path("", include("led_control.urls"))]
""")

with open("config/wsgi.py", "w", encoding="utf-8") as f:
    f.write("""import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
""")

with open("manage.py", "w", encoding="utf-8") as f:
    f.write("""import os, sys
def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
if __name__ == "__main__":
    main()
""")

with open("led_control/__init__.py", "w") as f:
    f.write("")

with open("led_control/apps.py", "w", encoding="utf-8") as f:
    f.write("""from django.apps import AppConfig
class LedControlConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "led_control"
""")

with open("led_control/admin.py", "w", encoding="utf-8") as f:
    f.write("""from django.contrib import admin
from .models import DeviceCommand
@admin.register(DeviceCommand)
class DeviceCommandAdmin(admin.ModelAdmin):
    list_display = ("device_id", "led_state", "updated_at")
    list_editable = ("led_state",)
""")

with open("led_control/urls.py", "w", encoding="utf-8") as f:
    f.write("""from django.urls import path
from . import views
urlpatterns = [
    path("", views.dashboard),
    path("api/led/<str:device_id>/", views.get_led_command),
    path("api/led/<str:device_id>/<str:state>/", views.set_led_command),
    path("api/devices/", views.list_devices),
]
""")

print("Tous les fichiers ont ete crees avec succes !")