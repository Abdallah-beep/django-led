/**
 * TTGO T-Call ESP32 SIM800L — Pilotage LED via Django
 * =====================================================
 * La carte interroge un serveur Django toutes les 10 secondes
 * et allume/éteint la LED selon la réponse JSON.
 *
 * Bibliothèques requises (Arduino Library Manager) :
 *   - TinyGSM         (vshymanskyy/TinyGSM)
 *   - ArduinoHttpClient
 *   - ArduinoJson
 *
 * Matériel :
 *   - TTGO T-Call ESP32 SIM800L
 *   - Carte SIM avec forfait data (GPRS/2G)
 */

#define TINY_GSM_MODEM_SIM800
#include <TinyGsmClient.h>
#include <ArduinoHttpClient.h>
#include <ArduinoJson.h>

// ============================================================
// ⚙️  CONFIGURATION — À ADAPTER SELON VOTRE SITUATION
// ============================================================

// --- Paramètres SIM / APN ---
const char APN[]       = "internet";   // APN de votre opérateur
const char APN_USER[]  = "";           // Laisser vide si non requis
const char APN_PASS[]  = "";           // Laisser vide si non requis

// --- Serveur Django ---
const char SERVER[]    = "votre-domaine.com";  // ⚠️ Sans https://
const int  PORT        = 80;                    // 80 pour HTTP, 443 pour HTTPS
const char DEVICE_ID[] = "ttgo01";             // ID unique de cette carte

// --- Intervalle de polling (ms) ---
const unsigned long POLL_INTERVAL = 10000;  // 10 secondes

// ============================================================
// 🔌  BROCHES TTGO T-CALL (version standard)
// ============================================================
#define MODEM_TX       27
#define MODEM_RX       26
#define MODEM_PWRKEY    4
#define MODEM_POWER_ON 23
#define MODEM_RST       5
#define MODEM_DTR      25

// LED intégrée — essayez GPIO 13, sinon GPIO 2
#define LED_PIN        13

// ============================================================
// 🔧  VARIABLES GLOBALES
// ============================================================
HardwareSerial SerialAT(1);
TinyGsm        modem(SerialAT);
TinyGsmClient  gsmClient(modem);

// Construit l'URL de l'API
String buildResource() {
    return "/api/led/" + String(DEVICE_ID) + "/";
}

// ============================================================
// 🔋  DÉMARRAGE DU MODEM
// ============================================================
void modemPowerOn() {
    Serial.println("[MODEM] Mise sous tension...");

    pinMode(MODEM_POWER_ON, OUTPUT);
    digitalWrite(MODEM_POWER_ON, HIGH);

    pinMode(MODEM_RST, OUTPUT);
    digitalWrite(MODEM_RST, HIGH);

    pinMode(MODEM_PWRKEY, OUTPUT);
    digitalWrite(MODEM_PWRKEY, LOW);
    delay(1000);
    digitalWrite(MODEM_PWRKEY, HIGH);
    delay(2000);
    digitalWrite(MODEM_PWRKEY, LOW);
    delay(1000);

    Serial.println("[MODEM] Séquence d'allumage terminée.");
}

// ============================================================
// 📡  CONNEXION GPRS
// ============================================================
bool connectGPRS() {
    Serial.println("[GPRS] Connexion en cours...");

    if (!modem.waitForNetwork(60000L)) {
        Serial.println("[GPRS] Réseau introuvable.");
        return false;
    }
    Serial.println("[GPRS] Réseau trouvé.");

    if (!modem.gprsConnect(APN, APN_USER, APN_PASS)) {
        Serial.println("[GPRS] Échec de connexion GPRS.");
        return false;
    }

    Serial.print("[GPRS] Connecté. IP : ");
    Serial.println(modem.localIP());
    return true;
}

// ============================================================
// 💡  MISE À JOUR DE LA LED
// ============================================================
void setLED(bool state) {
    digitalWrite(LED_PIN, state ? HIGH : LOW);
    Serial.println(state ? "[LED] ✅ ON" : "[LED] ⭕ OFF");
}

// ============================================================
// 🌐  APPEL API DJANGO
// ============================================================
void pollServer() {
    // Vérification / reconnexion GPRS
    if (!modem.isGprsConnected()) {
        Serial.println("[GPRS] Déconnecté. Tentative de reconnexion...");
        if (!connectGPRS()) {
            Serial.println("[GPRS] Reconnexion échouée. Prochaine tentative dans 10s.");
            return;
        }
    }

    String resource = buildResource();
    Serial.print("[HTTP] GET http://");
    Serial.print(SERVER);
    Serial.println(resource);

    HttpClient http(gsmClient, SERVER, PORT);
    http.connectionKeepAlive();

    int err = http.get(resource);
    if (err != 0) {
        Serial.print("[HTTP] Erreur requête : ");
        Serial.println(err);
        http.stop();
        return;
    }

    int statusCode = http.responseStatusCode();
    Serial.print("[HTTP] Code : ");
    Serial.println(statusCode);

    if (statusCode != 200) {
        Serial.println("[HTTP] Réponse inattendue.");
        http.stop();
        return;
    }

    String body = http.responseBody();
    Serial.print("[HTTP] Corps : ");
    Serial.println(body);

    // Désérialisation JSON
    StaticJsonDocument<256> doc;
    DeserializationError jsonErr = deserializeJson(doc, body);

    if (jsonErr) {
        Serial.print("[JSON] Erreur : ");
        Serial.println(jsonErr.c_str());
        http.stop();
        return;
    }

    bool ledState = doc["led"].as<bool>();
    setLED(ledState);

    http.stop();
}

// ============================================================
// 🚀  SETUP
// ============================================================
void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n===== TTGO LED Controller =====");

    // LED
    pinMode(LED_PIN, OUTPUT);
    setLED(false);

    // Modem
    modemPowerOn();
    SerialAT.begin(115200, SERIAL_8N1, MODEM_RX, MODEM_TX);
    delay(3000);

    Serial.println("[MODEM] Redémarrage...");
    modem.restart();
    delay(2000);

    String modemInfo = modem.getModemInfo();
    Serial.print("[MODEM] Info : ");
    Serial.println(modemInfo);

    // GPRS
    if (!connectGPRS()) {
        Serial.println("[ERREUR] GPRS non disponible au démarrage. La carte réessaiera dans la boucle.");
    }
}

// ============================================================
// 🔁  LOOP
// ============================================================
unsigned long lastPoll = 0;

void loop() {
    unsigned long now = millis();

    if (now - lastPoll >= POLL_INTERVAL) {
        lastPoll = now;
        pollServer();
    }

    // Petite pause pour éviter de monopoliser le CPU
    delay(100);
}
