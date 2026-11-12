# Iniciando AWS IoT: Conectando NodeMCU con AWS IoT

Si alguna vez has montado un proyecto con un ESP8266 y un sensor, sabes que lo difícil no es leer la temperatura, sino llevar ese dato a algún lugar útil de forma segura. AWS IoT Core resuelve justo eso: es un broker MQTT administrado, con autenticación mutua mediante certificados y reglas para enrutar los mensajes a otros servicios de AWS.

En este artículo vamos a conectar un **NodeMCU** a **AWS IoT Core**, publicar mensajes desde la placa y recibir comandos desde la nube. Al final tendrás una base sólida para cualquier proyecto IoT.

## Qué necesitas

- Una placa NodeMCU (ESP8266, v1.0 o similar)
- Cable micro-USB
- Una cuenta de AWS (el nivel gratuito alcanza de sobra para pruebas)
- Arduino IDE con el soporte para ESP8266 instalado
- Una red Wi-Fi de 2.4 GHz

Librerías de Arduino:

- **PubSubClient** (Nick O'Leary) para MQTT
- **ArduinoJson** para construir los payloads
- `ESP8266WiFi` y `LittleFS`, que vienen con el core de ESP8266

## Cómo funciona la conexión

AWS IoT Core exige que cada dispositivo se autentique con un **certificado X.509**. El flujo es:

1. El dispositivo abre una conexión TLS al *endpoint* de tu cuenta, en el puerto **8883**.
2. El dispositivo verifica la identidad de AWS con la CA raíz (Amazon Root CA 1).
3. AWS verifica la identidad del dispositivo con su certificado y su clave privada.
4. Una **política** de IoT define qué puede hacer ese certificado: conectarse, publicar, suscribirse.

Esto se llama TLS mutuo, y por eso necesitaremos tres archivos en la placa: la CA raíz, el certificado del dispositivo y la clave privada.

## Paso 1: Crear la "Thing" en AWS IoT Core

En la consola de AWS entra a **IoT Core → Manage → All devices → Things** y pulsa **Create things**.

1. Elige *Create single thing* y ponle un nombre, por ejemplo `nodemcu-01`.
2. En *Device certificate* selecciona **Auto-generate a new certificate**.
3. Más adelante te pedirá una política. Si aún no la tienes, créala en el siguiente paso.

Al terminar, la consola te ofrece descargar los archivos. Hazlo **ahora**, porque la clave privada no se puede recuperar después:

- `xxxxxxxx-certificate.pem.crt` (certificado del dispositivo)
- `xxxxxxxx-private.pem.key` (clave privada)
- **Amazon Root CA 1** (`AmazonRootCA1.pem`)

> ⚠️ Trata la clave privada como una contraseña. No la subas a GitHub ni la pegues en capturas de pantalla.

## Paso 2: Crear y adjuntar la política

En **IoT Core → Security → Policies** crea una política, por ejemplo `nodemcu-policy`, y pega este JSON (cambia región y cuenta por los tuyos):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iot:Connect",
      "Resource": "arn:aws:iot:us-east-1:123456789012:client/nodemcu-01"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Publish",
      "Resource": "arn:aws:iot:us-east-1:123456789012:topic/nodemcu/01/telemetry"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Subscribe",
      "Resource": "arn:aws:iot:us-east-1:123456789012:topicfilter/nodemcu/01/commands"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Receive",
      "Resource": "arn:aws:iot:us-east-1:123456789012:topic/nodemcu/01/commands"
    }
  ]
}
```

Fíjate en el principio de **mínimo privilegio**: el dispositivo solo puede conectarse con su propio `clientId` y usar dos tópicos concretos. Es tentador usar `"Resource": "*"` para salir del paso, pero en producción es una mala idea.

Después, ve al certificado que se creó con la Thing y adjunta esta política (*Attach policy*).

## Paso 3: Obtener tu endpoint

En **IoT Core → Settings** copia el **Device data endpoint**. Tiene la forma:

```
xxxxxxxxxxxxxx-ats.iot.us-east-1.amazonaws.com
```

Lo usaremos en el código.

## Paso 4: Cargar los certificados en el NodeMCU

Hay dos formas habituales: incrustarlos en el código o guardarlos en el sistema de archivos. Yo prefiero el sistema de archivos (LittleFS) porque permite cambiar certificados sin tocar el firmware.

1. Crea una carpeta `data/` dentro de tu sketch.
2. Copia ahí los tres archivos con nombres simples: `ca.pem`, `cert.pem` y `private.key`.
3. Sube el contenido con el plugin de carga de LittleFS de tu IDE (en Arduino IDE 2.x hay plugins de la comunidad; en PlatformIO es `pio run -t uploadfs`).

## Paso 5: El código

Primero, un archivo `secrets.h` para tus datos de red:

```cpp
#pragma once

#define WIFI_SSID     "tu_red_wifi"
#define WIFI_PASSWORD "tu_password"
#define AWS_ENDPOINT  "xxxxxxxxxxxxxx-ats.iot.us-east-1.amazonaws.com"
#define THING_NAME    "nodemcu-01"
```

Ahora el sketch principal:

```cpp
#include <ESP8266WiFi.h>
#include <LittleFS.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include "secrets.h"

const char* TOPIC_PUB = "nodemcu/01/telemetry";
const char* TOPIC_SUB = "nodemcu/01/commands";

BearSSL::WiFiClientSecure net;
PubSubClient mqtt(net);

BearSSL::X509List caCert;
BearSSL::X509List clientCert;
BearSSL::PrivateKey clientKey;

String readFile(const char* path) {
  File f = LittleFS.open(path, "r");
  if (!f) { Serial.printf("No se pudo abrir %s\n", path); return ""; }
  String s = f.readString();
  f.close();
  return s;
}

void syncTime() {
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  Serial.print("Sincronizando hora");
  time_t now = time(nullptr);
  while (now < 1700000000) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }
  Serial.println(" OK");
}

void onMessage(char* topic, byte* payload, unsigned int length) {
  Serial.printf("Mensaje en [%s]: ", topic);
  for (unsigned int i = 0; i < length; i++) Serial.print((char)payload[i]);
  Serial.println();

  StaticJsonDocument<128> doc;
  if (deserializeJson(doc, payload, length) == DeserializationError::Ok) {
    const char* cmd = doc["led"];
    if (cmd) digitalWrite(LED_BUILTIN, strcmp(cmd, "on") == 0 ? LOW : HIGH);
  }
}

void connectAWS() {
  while (!mqtt.connected()) {
    Serial.print("Conectando a AWS IoT... ");
    if (mqtt.connect(THING_NAME)) {
      Serial.println("conectado");
      mqtt.subscribe(TOPIC_SUB);
    } else {
      char err[128];
      net.getLastSSLError(err, sizeof(err));
      Serial.printf("falló (mqtt=%d, ssl=%s)\n", mqtt.state(), err);
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);

  LittleFS.begin();

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWi-Fi conectado");

  syncTime();

  caCert.append(readFile("/ca.pem").c_str());
  clientCert.append(readFile("/cert.pem").c_str());
  clientKey.parse(readFile("/private.key").c_str());

  net.setTrustAnchors(&caCert);
  net.setClientRSACert(&clientCert, &clientKey);
  net.setBufferSizes(512, 512);

  mqtt.setServer(AWS_ENDPOINT, 8883);
  mqtt.setCallback(onMessage);
}

unsigned long lastPublish = 0;

void loop() {
  if (!mqtt.connected()) connectAWS();
  mqtt.loop();

  if (millis() - lastPublish > 10000) {
    lastPublish = millis();

    StaticJsonDocument<128> doc;
    doc["device"] = THING_NAME;
    doc["uptime"] = millis() / 1000;
    doc["rssi"]   = WiFi.RSSI();

    char buffer[128];
    serializeJson(doc, buffer);
    mqtt.publish(TOPIC_PUB, buffer);
    Serial.printf("Publicado: %s\n", buffer);
  }
}
```

### Detalles que importan

- **La hora es obligatoria.** TLS valida la fecha de vigencia de los certificados. Sin NTP, el ESP8266 cree que estamos en 1970 y el handshake falla. Es el error número uno de quien empieza.
- **`setBufferSizes(512, 512)`** reduce el consumo de RAM. BearSSL con buffers por defecto consume mucha memoria en un ESP8266.
- **El `clientId`** (`THING_NAME`) debe coincidir con el que permite tu política en `iot:Connect`.
- Usamos `getLastSSLError` para obtener un diagnóstico útil cuando algo falla.

## Paso 6: Probar con el cliente MQTT de la consola

Abre el Monitor Serie a 115200 baudios. Deberías ver algo así:

```
Wi-Fi conectado
Sincronizando hora... OK
Conectando a AWS IoT... conectado
Publicado: {"device":"nodemcu-01","uptime":10,"rssi":-58}
```

Ahora en la consola ve a **IoT Core → MQTT test client**:

1. En *Subscribe to a topic* escribe `nodemcu/01/telemetry` y pulsa **Subscribe**. Verás llegar los mensajes cada 10 segundos.
2. En *Publish to a topic* usa el tópico `nodemcu/01/commands` con este mensaje:

```json
{ "led": "on" }
```

El LED integrado del NodeMCU debería encenderse (en esta placa el LED es activo en bajo, por eso el código usa `LOW` para encender). Con `{ "led": "off" }` se apaga.

Ya tienes comunicación bidireccional completa.

## Problemas comunes

| Síntoma | Causa probable |
|---|---|
| `mqtt=-2` (conexión fallida) | Endpoint incorrecto o sin salida al puerto 8883 |
| Error SSL de certificado expirado/no válido | La hora no se sincronizó con NTP |
| Conecta y se desconecta de inmediato | La política no permite `iot:Connect` con ese `clientId`, o no está adjunta al certificado |
| `Subscribe` sin efecto | Falta `iot:Subscribe` sobre `topicfilter/...` o `iot:Receive` sobre `topic/...` |
| Reinicios por falta de memoria | Buffers SSL grandes o demasiadas cadenas `String` |

Una herramienta muy útil para depurar políticas es el **registro de CloudWatch** de AWS IoT: actívalo en *Settings → Logs* con nivel `DEBUG` mientras haces pruebas, y verás el motivo exacto de cada rechazo.

## Siguientes pasos

Con la conexión funcionando, hay muchas direcciones interesantes:

- **Reglas de AWS IoT**: guarda cada mensaje en DynamoDB, envíalo a S3 o dispara una función Lambda con una sentencia SQL como `SELECT * FROM 'nodemcu/+/telemetry' WHERE rssi < -80`.
- **Device Shadow**: mantiene el estado deseado y reportado del dispositivo, incluso si está desconectado.
- **Sensores reales**: sustituye `uptime` y `rssi` por un DHT22 o un BME280.
- **Aprovisionamiento masivo**: cuando pases de uno a cientos de dispositivos, investiga *fleet provisioning* para no crear certificados a mano.
- **Seguridad**: rota certificados periódicamente y considera ESP32, que soporta almacenamiento seguro de claves con mejor rendimiento criptográfico.

## Conclusión

Conectar un NodeMCU a AWS IoT Core no es complicado, pero tiene varias piezas que deben encajar: una Thing, un certificado, una política con los permisos justos, el endpoint correcto y, sobre todo, la hora sincronizada. Una vez que entiendes ese esquema, cambiar de sensor o de placa es lo de menos.

Si te quedaste atascado en algún paso o quieres que cubra Device Shadow o reglas hacia DynamoDB en un siguiente post, cuéntamelo en los comentarios. ¡Feliz hacking! 🚀
