# 🔆 Pilotage LED ESP32 via Django

Contrôlez la LED d'une carte **TTGO T-Call ESP32 SIM800L** depuis un serveur **Django** via HTTP/GPRS.

---

## 📁 Structure du projet

```
django_led/                     ← Projet Django
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── led_control/
│   ├── models.py               ← Modèle DeviceCommand
│   ├── views.py                ← API GET/SET + Dashboard
│   ├── urls.py                 ← Routes API
│   ├── admin.py                ← Interface admin Django
│   └── templates/led_control/
│       └── dashboard.html      ← Interface web de contrôle
├── manage.py
└── requirements.txt

arduino_led/
└── ttgo_led_controller.ino     ← Code Arduino TTGO
```

---

## 🚀 Installation Django

### 1. Prérequis
```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Migrations
```bash
python manage.py makemigrations led_control
python manage.py migrate
```

### 3. Créer un compte admin (optionnel)
```bash
python manage.py createsuperuser
```

### 4. Lancer en développement
```bash
python manage.py runserver 0.0.0.0:8000
```

### 5. Déploiement en production
```bash
# Exemple avec Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# ⚠️ En production, configurez aussi :
# - DEBUG = False dans settings.py
# - ALLOWED_HOSTS = ["votre-domaine.com"]
# - Une vraie SECRET_KEY
# - Un reverse proxy Nginx
```

---

## 🌐 Endpoints API

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/` | Dashboard web |
| GET | `/api/led/<device_id>/` | Lire l'état de la LED |
| GET | `/api/led/<device_id>/on/` | Allumer la LED |
| GET | `/api/led/<device_id>/off/` | Éteindre la LED |
| GET | `/api/devices/` | Lister tous les appareils |

### Exemple de réponse
```json
{
  "device_id": "ttgo01",
  "led": true,
  "updated_at": "2024-01-15T14:30:00+01:00"
}
```

---

## 🔧 Configuration Arduino (TTGO T-Call)

### Bibliothèques requises
Installez via Arduino Library Manager :
- **TinyGSM** (par Volodymyr Shymanskyy)
- **ArduinoHttpClient**
- **ArduinoJson** (par Benoit Blanchon)

### Paramètres à modifier dans `ttgo_led_controller.ino`

```cpp
const char APN[]    = "internet";          // ← APN de votre opérateur
const char SERVER[] = "votre-domaine.com"; // ← Votre domaine (sans https://)
const int  PORT     = 80;                  // ← 80 pour HTTP
const char DEVICE_ID[] = "ttgo01";        // ← ID unique de la carte
```

### APN courants (Maroc / France)
| Opérateur | APN |
|-----------|-----|
| Maroc Telecom | internet.iam.ma |
| Orange France | orange |
| Free Mobile | free |
| SFR | sl2sfr |
| Bouygues | mmsbouygtel.com |

### Broche LED
La LED intégrée varie selon la version de la carte :
- Essayez d'abord `GPIO 13`
- Si ça ne fonctionne pas, essayez `GPIO 2`

```cpp
#define LED_PIN 13   // ← Changer si besoin
```

---

## ⚡ Fonctionnement

```
[Navigateur]  →  Django  ←→  [TTGO ESP32]
    |              |               |
    |   /led/on/   |               |
    |─────────────>|               |
    |              |  GET /api/led/ toutes les 10s
    |              |<──────────────|
    |              |  {"led": true}|
    |              |──────────────>|
    |              |               |  digitalWrite(LED, HIGH)
```

1. Vous cliquez "Allumer" sur le dashboard Django
2. Django stocke `led_state = True` en base
3. L'ESP32 interroge l'API toutes les 10 secondes
4. Il reçoit `{"led": true}` et allume la LED

---

## ⚠️ Points d'attention

- **Alimentation** : le SIM800L est gourmand (~2A en pic). Utilisez une bonne alimentation 5V.
- **Réseau 2G** : vérifiez que votre opérateur supporte encore le GPRS/2G dans votre zone.
- **HTTP vs HTTPS** : le SIM800L a des difficultés avec HTTPS. Commencez en HTTP (port 80).
- **Pare-feu** : votre serveur Django doit être accessible depuis Internet sur le port choisi.
