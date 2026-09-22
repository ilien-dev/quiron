# Usando Firebase para autenticar en Django REST Framework

Firebase Authentication facilita el registro e inicio de sesión mediante correo electrónico, Google, Apple, GitHub y otros proveedores. Sin embargo, muchas aplicaciones necesitan conservar su API, reglas de negocio y base de datos en Django.

La solución consiste en separar responsabilidades:

1. Firebase autentica al usuario.
2. El cliente obtiene un ID token.
3. El cliente envía ese token a la API.
4. Django REST Framework verifica el token con Firebase Admin SDK.
5. La API identifica al usuario y aplica sus permisos.

Así podemos aprovechar Firebase como proveedor de identidad sin renunciar al ecosistema de Django.

## Cómo funciona el flujo

Después de iniciar sesión, Firebase entrega al cliente un ID token firmado. Este token es un JWT que contiene información como:

- El UID del usuario.
- Su correo electrónico.
- El proveedor utilizado.
- La fecha de emisión y expiración.
- Claims personalizados, si existen.

El cliente debe enviarlo en cada petición protegida:

```http
Authorization: Bearer FIREBASE_ID_TOKEN
```

La API no debe confiar simplemente en el contenido decodificado del JWT. Debe verificar su firma, audiencia, emisor y expiración mediante Firebase Admin SDK.

Es importante no confundir el ID token con un refresh token. El ID token demuestra la identidad del usuario ante nuestra API. El refresh token solamente debe ser utilizado por los SDK de Firebase para renovar la sesión.

## Crear y configurar el proyecto

Comencemos instalando las dependencias:

```bash
pip install django djangorestframework firebase-admin
```

Después añadimos Django REST Framework y nuestra aplicación a `INSTALLED_APPS`:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    "rest_framework",
    "api.apps.ApiConfig",
]
```

También necesitamos conocer el identificador del proyecto de Firebase:

```python
# settings.py

import os

FIREBASE_PROJECT_ID = os.environ["FIREBASE_PROJECT_ID"]
```

Para ejecutar el proyecto localmente podemos descargar una cuenta de servicio desde Firebase Console, en **Configuración del proyecto > Cuentas de servicio**.

La ruta del archivo debe configurarse mediante una variable de entorno:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/ruta/segura/firebase-service-account.json"
export FIREBASE_PROJECT_ID="mi-proyecto-firebase"
```

Nunca debemos subir este JSON al repositorio. Contiene credenciales privadas con acceso administrativo al proyecto.

En Google Cloud Run, App Engine, Compute Engine o Kubernetes con Workload Identity es preferible utilizar Application Default Credentials, sin distribuir archivos de claves.

## Inicializar Firebase Admin

Firebase Admin debe inicializarse una sola vez durante el arranque de Django. Podemos hacerlo desde la configuración de nuestra aplicación:

```python
# api/apps.py

from django.apps import AppConfig
from django.conf import settings

import firebase_admin
from firebase_admin import credentials


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(
                credentials.ApplicationDefault(),
                {
                    "projectId": settings.FIREBASE_PROJECT_ID,
                },
            )
```

La llamada a `get_app()` evita inicializar Firebase dos veces, algo que puede ocurrir durante el desarrollo debido al recargador automático de Django.

## Crear la clase de autenticación

Django REST Framework permite implementar mecanismos personalizados heredando de `BaseAuthentication`.

Nuestra clase realizará cuatro operaciones:

1. Leer el encabezado `Authorization`.
2. Extraer el token.
3. Verificarlo con Firebase.
4. Obtener o crear un usuario local de Django.

```python
# api/authentication.py

import logging

from django.contrib.auth import get_user_model
from firebase_admin import auth as firebase_auth
from rest_framework.authentication import (
    BaseAuthentication,
    get_authorization_header,
)
from rest_framework.exceptions import AuthenticationFailed


logger = logging.getLogger(__name__)
User = get_user_model()


class FirebaseAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        authorization = get_authorization_header(request).split()

        if not authorization:
            return None

        if authorization[0].lower() != self.keyword.lower().encode():
            return None

        if len(authorization) != 2:
            raise AuthenticationFailed(
                "El encabezado Authorization no tiene un formato válido."
            )

        try:
            token = authorization[1].decode("utf-8")
        except UnicodeError:
            raise AuthenticationFailed("El token contiene caracteres inválidos.")

        try:
            decoded_token = firebase_auth.verify_id_token(token)
        except firebase_auth.ExpiredIdTokenError:
            raise AuthenticationFailed("El token ha expirado.")
        except firebase_auth.RevokedIdTokenError:
            raise AuthenticationFailed("El token ha sido revocado.")
        except firebase_auth.InvalidIdTokenError:
            raise AuthenticationFailed("El token no es válido.")
        except Exception:
            logger.exception("No fue posible verificar el token de Firebase.")
            raise AuthenticationFailed("No fue posible validar la sesión.")

        uid = decoded_token.get("uid")

        if not uid:
            raise AuthenticationFailed("El token no contiene un UID.")

        user, created = User.objects.get_or_create(
            username=uid,
            defaults={
                "email": decoded_token.get("email", ""),
            },
        )

        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])

        return user, decoded_token

    def authenticate_header(self, request):
        return self.keyword
```

El UID de Firebase se utiliza como `username` porque es estable y único dentro del proyecto. No es recomendable buscar usuarios por correo electrónico: el correo puede cambiar y, dependiendo de la configuración de proveedores, incluso podría no estar presente.

Si tenemos un modelo de usuario personalizado, podemos guardar el UID en un campo exclusivo:

```python
firebase_uid = models.CharField(
    max_length=128,
    unique=True,
    db_index=True,
)
```

En ese caso, la consulta sería:

```python
user, created = User.objects.get_or_create(
    firebase_uid=uid,
    defaults={"email": decoded_token.get("email", "")},
)
```

Esta opción suele ser más clara en proyectos nuevos.

## Activar la autenticación en DRF

Podemos convertir Firebase en el mecanismo predeterminado de la API:

```python
# settings.py

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "api.authentication.FirebaseAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

A partir de ahora, todos los endpoints exigirán autenticación, salvo que indiquemos lo contrario.

Un endpoint protegido puede acceder tanto al usuario local como al token verificado:

```python
# api/views.py

from rest_framework.response import Response
from rest_framework.views import APIView


class ProfileView(APIView):
    def get(self, request):
        return Response(
            {
                "id": request.user.pk,
                "firebase_uid": request.auth["uid"],
                "email": request.auth.get("email"),
                "provider": request.auth.get("firebase", {}).get(
                    "sign_in_provider"
                ),
            }
        )
```

Para permitir acceso público en una vista concreta:

```python
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok"})
```

La autenticación responde a la pregunta “¿quién es el usuario?”. Los permisos responden a “¿puede realizar esta acción?”. Conviene mantener ambas responsabilidades separadas.

## Enviar el token desde el cliente

Con el SDK web modular de Firebase, el cliente puede obtener un token después de iniciar sesión:

```javascript
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "./firebase";

async function loadProfile(email, password) {
  const credential = await signInWithEmailAndPassword(
    auth,
    email,
    password
  );

  const idToken = await credential.user.getIdToken();

  const response = await fetch("https://api.example.com/profile/", {
    headers: {
      Authorization: `Bearer ${idToken}`,
    },
  });

  if (!response.ok) {
    throw new Error("No fue posible cargar el perfil");
  }

  return response.json();
}
```

Los ID tokens suelen tener una vida corta. El SDK de Firebase se encarga de renovarlos, por lo que el cliente debe solicitar un token actualizado antes de llamar a la API, en lugar de almacenar uno indefinidamente.

No es recomendable guardar tokens en `localStorage` cuando la arquitectura permite evitarlo, porque cualquier vulnerabilidad XSS podría exponerlos. En aplicaciones web debemos evaluar cuidadosamente el modelo de amenazas y aplicar una política CSP estricta.

## Claims personalizados y autorización

Firebase permite agregar claims personalizados desde un entorno administrativo:

```python
from firebase_admin import auth

auth.set_custom_user_claims(
    firebase_uid,
    {
        "role": "editor",
        "tenant_id": "empresa-123",
    },
)
```

Después de renovar el ID token, esos valores estarán disponibles en Django:

```python
role = request.auth.get("role")
tenant_id = request.auth.get("tenant_id")
```

Podemos convertirlos en un permiso de DRF:

```python
# api/permissions.py

from rest_framework.permissions import BasePermission


class IsEditor(BasePermission):
    message = "Se requiere el rol de editor."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.auth.get("role") == "editor"
        )
```

Y aplicarlo a una vista:

```python
from rest_framework.views import APIView

from api.permissions import IsEditor


class ArticleAdminView(APIView):
    permission_classes = [IsEditor]

    def post(self, request):
        # Crear o publicar un artículo
        return Response({"created": True}, status=201)
```

Los claims son apropiados para datos pequeños y relativamente estables, como roles globales. Los permisos complejos, relaciones entre organizaciones o reglas que cambian con frecuencia deberían almacenarse en la base de datos de la aplicación.

## Revocación de sesiones

`verify_id_token()` comprueba la firma y la expiración, pero no consulta por defecto si la sesión fue revocada. Para incluir esa comprobación podemos usar:

```python
decoded_token = firebase_auth.verify_id_token(
    token,
    check_revoked=True,
)
```

Esto permite rechazar tokens pertenecientes a sesiones revocadas o usuarios deshabilitados. La contrapartida es que puede introducir una consulta adicional a Firebase y aumentar la latencia.

Una estrategia razonable es activar la comprobación estricta en operaciones sensibles, o utilizarla globalmente si el volumen y los requisitos de seguridad lo justifican.

## Probar la autenticación

Las pruebas no deberían depender de Firebase ni de una conexión externa. Podemos simular la verificación del token:

```python
from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class ProfileTests(APITestCase):
    @patch("api.authentication.firebase_auth.verify_id_token")
    def test_authenticated_user_can_read_profile(self, verify):
        verify.return_value = {
            "uid": "firebase-user-123",
            "email": "ana@example.com",
            "firebase": {
                "sign_in_provider": "google.com",
            },
        }

        response = self.client.get(
            "/profile/",
            HTTP_AUTHORIZATION="Bearer token-de-prueba",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["firebase_uid"],
            "firebase-user-123",
        )

        user = get_user_model().objects.get(
            username="firebase-user-123"
        )
        self.assertEqual(user.email, "ana@example.com")
```

También conviene probar encabezados mal formados, tokens expirados, tokens inválidos, usuarios deshabilitados y endpoints públicos.

## Consideraciones de seguridad

Una integración lista para producción debería cumplir al menos estas reglas:

- Usar HTTPS en todas las comunicaciones.
- No registrar tokens completos.
- No enviar cuentas de servicio al cliente.
- Validar permisos en el servidor, aunque la interfaz oculte acciones.
- Tratar el UID, no el correo, como identificador de identidad.
- Limitar los privilegios de las credenciales administrativas.
- Configurar CORS únicamente para los orígenes necesarios.
- Mantener `firebase-admin`, Django y DRF actualizados.
- No asumir que las reglas de seguridad de Firestore protegen endpoints de Django.

Las reglas de Firebase se aplican cuando el cliente accede directamente a productos como Firestore o Storage. Nuestra API de Django tiene sus propias rutas y debe implementar explícitamente sus permisos.

## Conclusión

Firebase Authentication y Django REST Framework encajan bien cuando Firebase se utiliza como proveedor de identidad y Django conserva el control de la aplicación.

El cliente inicia sesión y obtiene un ID token; DRF lo verifica, relaciona el UID con un usuario local y aplica permisos sobre cada operación. Esta separación permite incorporar proveedores sociales y gestión de sesiones sin trasladar la lógica de negocio ni la autorización al frontend.

El punto fundamental es recordar que recibir un JWT no equivale a confiar en él: siempre debe verificarse en el servidor antes de utilizar cualquiera de sus datos.