# Usando Firebase para autenticar en Django REST Framework

Implementar autenticación suele empezar con un formulario de acceso y terminar con recuperación de contraseñas, verificación de correo y conexiones con proveedores externos. Si además tienes una aplicación web y otra móvil, mantener toda esa infraestructura puede ocupar más tiempo del esperado.

Firebase Authentication puede encargarse del inicio de sesión mientras Django REST Framework administra los datos y las reglas de tu aplicación. La integración gira alrededor de un flujo sencillo: el cliente obtiene un token de Firebase y tu API lo verifica antes de responder.

En este tutorial construiremos esa conexión utilizando el SDK oficial de Firebase Admin y una clase de autenticación personalizada.

## Cómo funcionará nuestra autenticación

El recorrido de una petición será el siguiente:

1. El usuario inicia sesión con Firebase desde el frontend.
2. El cliente obtiene un **ID token**.
3. Envía ese token a Django mediante `Authorization: Bearer <token>`.
4. El backend verifica el token y encuentra al usuario local.
5. DRF evalúa los permisos y ejecuta la vista.

La verificación debe realizarse en el servidor. Decodificar un JWT para leer su contenido no demuestra que sea auténtico: hay que comprobar su firma y sus atributos, como expiración, emisor y proyecto de destino. Firebase Admin realiza estas comprobaciones. Además, espera un ID token del cliente, no un custom token generado por el servidor. [Documentación de verificación](https://firebase.google.com/docs/auth/admin/verify-id-tokens).

Para este ejemplo utilizaremos el modelo de usuario predeterminado de Django. Si tu proyecto tiene un modelo personalizado, adapta la creación del usuario a sus campos obligatorios.

## 1. Preparar el proyecto

Instala las dependencias dentro de tu entorno virtual:

```bash
pip install django djangorestframework firebase-admin
```

Si comienzas desde cero:

```bash
django-admin startproject config .
python manage.py startapp accounts
```

Agrega las aplicaciones a `config/settings.py`:

```python
INSTALLED_APPS = [
    # Aplicaciones predeterminadas de Django...
    "rest_framework",
    "accounts",
]
```

En Firebase, crea un proyecto y habilita el proveedor **Correo electrónico/contraseña** dentro de Authentication. Registra también una aplicación web para obtener su configuración de cliente.

Firebase documenta el inicio de sesión con `signInWithEmailAndPassword`; utilizaremos esa función al conectar el frontend. [Guía de autenticación con contraseña](https://firebase.google.com/docs/auth/web/password-auth).

## 2. Configurar Firebase Admin

El frontend y el backend utilizan configuraciones diferentes. Django necesita credenciales de servidor para inicializar Firebase Admin.

En desarrollo local puedes usar un archivo JSON de una cuenta de servicio, guardado fuera del repositorio. Define estas variables de entorno; en PowerShell:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\secrets\firebase-admin.json"
$env:FIREBASE_PROJECT_ID="mi-proyecto-firebase"
```

Crea `accounts/firebase.py`:

```python
import os
from functools import lru_cache

import firebase_admin


@lru_cache(maxsize=1)
def get_firebase_app():
    return firebase_admin.initialize_app(
        options={
            "projectId": os.environ["FIREBASE_PROJECT_ID"],
        }
    )
```

`initialize_app()` puede descubrir las credenciales mediante Application Default Credentials. En entornos compatibles de Google Cloud, esto permite utilizar la identidad asignada al servicio, evitando distribuir archivos de claves. [Configuración del SDK Admin](https://firebase.google.com/docs/admin/setup).

La función conserva la instancia para reutilizarla dentro del proceso. Reserva esta inicialización para este módulo y evita repetirla en otras partes del proyecto.

Nunca incluyas el JSON de la cuenta de servicio en el frontend, una imagen pública de contenedor o un commit.

## 3. Relacionar Firebase con los usuarios de Django

Aunque Firebase gestione el acceso, tener usuarios locales facilita relacionar pedidos, artículos o comentarios con una cuenta.

Podríamos utilizar el correo como identificador, pero puede cambiar. Usaremos el `uid` de Firebase mediante una tabla explícita de correspondencia.

En `accounts/models.py`:

```python
from django.conf import settings
from django.db import models


class FirebaseIdentity(models.Model):
    uid = models.CharField(max_length=128, unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="firebase_identity",
    )
```

Genera y aplica las migraciones:

```bash
python manage.py makemigrations accounts
python manage.py migrate
```

La restricción única evita vincular una identidad de Firebase con varias cuentas locales. Este diseño supone que la API acepta identidades de un único proyecto Firebase.

También evita vincular automáticamente cuentas por coincidencia de correo. Si necesitas conectar usuarios existentes, diseña un proceso que compruebe que la persona controla ambas cuentas.

## 4. Crear la autenticación personalizada

DRF permite extender `BaseAuthentication`. El método `authenticate()` devuelve `(usuario, autenticación)` cuando identifica al solicitante, `None` cuando el esquema no aplica y una excepción cuando las credenciales presentadas son inválidas. [Autenticación personalizada en DRF](https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication).

Crea `accounts/authentication.py`:

```python
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import transaction
from firebase_admin import auth
from rest_framework.authentication import (
    BaseAuthentication,
    get_authorization_header,
)
from rest_framework.exceptions import AuthenticationFailed

from .firebase import get_firebase_app
from .models import FirebaseIdentity


def create_local_user():
    User = get_user_model()
    return User.objects.create_user(
        username=f"firebase_{uuid4().hex}",
        password=None,
    )


class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        parts = get_authorization_header(request).split()

        if not parts or parts[0].lower() != b"bearer":
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                "Encabezado Authorization inválido."
            )

        try:
            token = parts[1].decode("ascii")
        except UnicodeDecodeError:
            raise AuthenticationFailed("Token inválido.")

        try:
            claims = auth.verify_id_token(
                token,
                app=get_firebase_app(),
                check_revoked=True,
            )
        except (
            auth.InvalidIdTokenError,
            auth.RevokedIdTokenError,
            auth.UserDisabledError,
        ):
            raise AuthenticationFailed(
                "Token inválido, vencido o revocado."
            )

        with transaction.atomic():
            identity, _ = FirebaseIdentity.objects.get_or_create(
                uid=claims["uid"],
                defaults={"user": create_local_user},
            )
            user = identity.user

        if not user.is_active:
            raise AuthenticationFailed("Usuario desactivado.")

        return user, claims

    def authenticate_header(self, request):
        return "Bearer"
```

El valor de `defaults` es una función: Django la ejecuta cuando necesita crear la identidad. La transacción engloba también la creación del usuario local.

`create_user(password=None)` establece una contraseña inutilizable. El acceso de estas cuentas se realizará mediante Firebase.

La comprobación `check_revoked=True` permite detectar revocaciones y usuarios deshabilitados, pero añade una consulta al servicio de autenticación. Evalúa ese coste según las necesidades de tu API. [Referencia de Firebase Admin para Python](https://firebase.google.com/docs/reference/admin/python/firebase_admin.auth).

Observa que no capturamos cualquier excepción indiscriminadamente: una credencial de servidor mal configurada o una caída de infraestructura necesita diagnóstico, no convertirse silenciosamente en “contraseña incorrecta”.

## 5. Proteger los endpoints

Configura DRF en `config/settings.py`:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.FirebaseAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

Así, las vistas de DRF exigirán autenticación por defecto. Para registro público, información de estado u otros endpoints abiertos, podrás declarar `AllowAny` expresamente.

Autenticar y autorizar son responsabilidades diferentes: `IsAuthenticated` comprueba que existe un usuario autenticado, pero los permisos sobre recursos requieren reglas adicionales. Por ejemplo, un usuario no debería poder consultar pedidos ajenos únicamente porque inició sesión. [Permisos en DRF](https://www.django-rest-framework.org/api-guide/permissions/).

Agrega una vista en `accounts/views.py`:

```python
from rest_framework.response import Response
from rest_framework.views import APIView


class MeView(APIView):
    def get(self, request):
        return Response({
            "id": request.user.pk,
            "firebase_uid": request.auth["uid"],
        })
```

Y registra la ruta en `config/urls.py`:

```python
from django.urls import path

from accounts.views import MeView

urlpatterns = [
    path("api/me/", MeView.as_view()),
]
```

No devolvemos todos los atributos del token: exponemos únicamente los campos que necesita el cliente.

## 6. Enviar el token desde el frontend

Con Firebase inicializado y una instancia llamada `firebaseAuth`, el cliente puede iniciar sesión y consultar el endpoint:

```javascript
import {
  signInWithEmailAndPassword,
} from "firebase/auth";

async function cargarPerfil(email, password) {
  const credential = await signInWithEmailAndPassword(
    firebaseAuth,
    email,
    password
  );

  const token = await credential.user.getIdToken();

  const response = await fetch(
    "http://localhost:8000/api/me/",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Error HTTP ${response.status}`);
  }

  return response.json();
}
```

En producción, utiliza HTTPS. Si frontend y API viven en orígenes diferentes, configura CORS para permitir tu origen y el encabezado `Authorization`.

Pide el token al SDK cuando prepares las peticiones. Evita copiarlo una vez y reutilizar esa cadena indefinidamente.

## 7. Comprobar el comportamiento

Antes de desplegar, prueba el recorrido completo con una cuenta de desarrollo:

- Sin encabezado de autenticación, `/api/me/` debe responder `401`.
- Con un token válido, debe devolver el usuario local.
- Una segunda petición debe reutilizar la misma cuenta.
- Un token alterado o perteneciente a otro proyecto debe rechazarse.
- Un usuario local con `is_active=False` debe perder el acceso.

En pruebas automatizadas puedes sustituir la verificación de Firebase por respuestas controladas para comprobar la integración con Django. Complementa esas pruebas con una validación real: un mock no comprueba las credenciales del despliegue.

Con esta integración, Firebase se ocupa del inicio de sesión y Django conserva los usuarios, las relaciones y las decisiones de acceso. A partir de aquí puedes añadir permisos por propietario, organizaciones o roles sin reescribir el mecanismo de autenticación.
