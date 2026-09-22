# Iniciando AWS IoT: Conectando NodeMCU con AWS IoT

En este tutorial vamos a ver cómo conectar una placa NodeMCU (basada en el chip ESP8266) al servicio AWS IoT Core, de forma que podamos publicar y recibir mensajes MQTT desde la nube de Amazon. Este es uno de los primeros pasos típicos al adentrarse en el mundo del IoT usando servicios en la nube, así que vamos a cubrir desde la configuración en AWS hasta el código que corre en la placa.

## ¿Qué es AWS IoT Core?

AWS IoT Core es un servicio administrado que permite que dispositivos conectados (sensores, actuadores, microcontroladores) se comuniquen de forma segura con aplicaciones en la nube y entre ellos mismos, usando principalmente el protocolo MQTT, aunque también soporta HTTP y otros. Cada dispositivo se identifica mediante un certificado X.509 único, lo cual garantiza que la comunicación esté cifrada y autenticada extremo a extremo.

## Requisitos previos

- Una cuenta de AWS (la capa gratuita es suficiente para este tutorial).
- Una placa NodeMCU (ESP8266).
- Arduino IDE configurado con soporte para placas ESP8266.
- Las librerías `PubSubClient` y `WiFiClientSecure` instaladas en el IDE.

## Paso 1: Crear una "Thing" en AWS IoT

Desde la consola de AWS, entramos a **AWS IoT Core** y en el menú lateral seleccionamos **Manage > Things > Create things**. Elegimos "Create single thing" y le damos un nombre, por ejemplo `nodemcu-sensor-01`.

## Paso 2: Generar los certificados

Durante el proceso de creación, AWS IoT nos ofrece generar automáticamente un certificado. Es fundamental descargar los siguientes archivos, ya que no se pueden volver a descargar después:

- El certificado del dispositivo (`xxxxx-certificate.pem.crt`)
- La clave privada (`xxxxx-private.pem.key`)
- El certificado raíz de Amazon (`AmazonRootCA1.pem`)

Estos tres archivos son los que usará el NodeMCU para autenticarse ante AWS IoT.

## Paso 3: Crear y adjuntar una política

Las "Things" en AWS IoT necesitan una política (policy) que defina qué acciones tienen permitido realizar: conectarse, publicar en ciertos topics, suscribirse, etc. Un ejemplo básico de política (para pruebas; en producción conviene restringirla mucho más) sería:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect",
        "iot:Publish",
        "iot:Subscribe",
        "iot:Receive"
      ],
      "Resource": "*"
    }
  ]
}
```

Creamos esta política desde **Security > Policies > Create policy**, y luego la adjuntamos al certificado generado para nuestro dispositivo.

## Paso 4: Obtener el endpoint de AWS IoT

Cada cuenta de AWS tiene un endpoint único para IoT Core, que podemos encontrar en **Settings**, dentro de la consola de AWS IoT. Tiene un formato similar a:

```
xxxxxxxxxxxxxx-ats.iot.us-east-1.amazonaws.com
```

Este endpoint es el que usaremos en el código del NodeMCU para conectarnos.

## Paso 5: Preparar el código en Arduino IDE

Con los certificados descargados, hay que convertirlos a arrays de bytes en C para poder incluirlos directamente en el sketch de Arduino. Existen herramientas online y scripts en Python para hacer esta conversión automáticamente. El resultado se ve algo así:

```cpp
const char* AWS_CERT_CA = R"EOF(
-----BEGIN CERTIFICATE-----
... contenido del AmazonRootCA1.pem ...
-----END CERTIFICATE-----
)EOF";

const char* AWS_CERT_CRT = R"EOF(
-----BEGIN CERTIFICATE-----
... contenido del certificado del dispositivo ...
-----END CERTIFICATE-----
)EOF";

const char* AWS_CERT_PRIVATE = R"EOF(
-----BEGIN RSA PRIVATE KEY-----
... contenido de la clave privada ...
-----END RSA PRIVATE KEY-----
)EOF";
```

## Paso 6: El sketch completo

```cpp
#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include "certificados.h"

const char* WIFI_SSID = "tu_red_wifi";
const char* WIFI_PASSWORD = "tu_password";
const char* AWS_ENDPOINT = "xxxxxxxxxxxxxx-ats.iot.us-east-1.amazonaws.com";
const int AWS_PORT = 8883;
const char* TOPIC_PUB = "nodemcu/sensor01/data";
const char* TOPIC_SUB = "nodemcu/sensor01/comandos";

WiFiClientSecure net;
PubSubClient client(net);

void conectarWifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" ¡Conectado!");
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensaje recibido en ");
  Serial.println(topic);
  for (unsigned int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void conectarAWS() {
  net.setTrustAnchors(new BearSSL::X509List(AWS_CERT_CA));
  net.setClientRSACert(new BearSSL::X509List(AWS_CERT_CRT), new BearSSL::PrivateKey(AWS_CERT_PRIVATE));

  client.setServer(AWS_ENDPOINT, AWS_PORT);
  client.setCallback(callback);

  Serial.println("Conectando a AWS IoT...");
  while (!client.connect("NodeMCU-Sensor01")) {
    Serial.print(".");
    delay(1000);
  }

  if (!client.connected()) {
    Serial.println("Error al conectar con AWS IoT");
    return;
  }

  client.subscribe(TOPIC_SUB);
  Serial.println("¡Conectado a AWS IoT!");
}

void setup() {
  Serial.begin(115200);
  conectarWifi();
  conectarAWS();
}

void loop() {
  if (!client.connected()) {
    conectarAWS();
  }
  client.loop();

  static unsigned long ultimoEnvio = 0;
  if (millis() - ultimoEnvio > 5000) {
    ultimoEnvio = millis();
    String payload = "{\"temperatura\": 23.5, \"humedad\": 60}";
    client.publish(TOPIC_PUB, payload.c_str());
    Serial.println("Mensaje publicado: " + payload);
  }
}
```

## Explicando el código

El sketch hace básicamente tres cosas: se conecta al WiFi local, establece una conexión TLS segura con AWS IoT usando los certificados generados anteriormente, y publica un mensaje JSON simulado cada cinco segundos en el topic `nodemcu/sensor01/data`. También se suscribe al topic `nodemcu/sensor01/comandos`, de forma que puede recibir comandos enviados desde la nube (por ejemplo, para encender o apagar un actuador conectado a la placa).

## Verificando la conexión desde AWS

Desde la consola de AWS IoT, en **MQTT test client**, podemos suscribirnos manualmente al topic `nodemcu/sensor01/data` y ver en tiempo real los mensajes que la placa está publicando. Esto es extremadamente útil para depurar sin necesidad de montar ninguna aplicación adicional.

También podemos publicar mensajes manualmente desde la consola hacia el topic `nodemcu/sensor01/comandos`, y verlos aparecer en el monitor serie de Arduino IDE gracias a la función `callback` que definimos.

## Siguientes pasos

Una vez que la comunicación básica funciona, el siguiente paso natural suele ser conectar sensores reales (temperatura, humedad, movimiento) en lugar de datos simulados, y usar AWS IoT Rules para enrutar automáticamente los mensajes hacia otros servicios de AWS, como DynamoDB para almacenar históricos, Lambda para procesar los datos, o SNS para enviar alertas.

## Conclusión

Conectar un NodeMCU a AWS IoT Core requiere bastante configuración inicial —certificados, políticas, endpoints—, pero una vez resuelta esa parte, el flujo de trabajo se vuelve muy fluido gracias al protocolo MQTT y a las librerías disponibles para ESP8266. Este montaje básico es la base sobre la que se pueden construir proyectos mucho más elaborados de IoT, aprovechando el resto del ecosistema de servicios que ofrece AWS.
