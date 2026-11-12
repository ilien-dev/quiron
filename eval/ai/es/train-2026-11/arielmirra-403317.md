# ¿Qué es una API y para qué sirve? Cómo funcionan y por qué son tan valiosas

Si alguna vez has pagado con una pasarela online, consultado el clima en tu móvil o iniciado sesión con tu cuenta de Google en otra aplicación, has usado una API sin darte cuenta. Son tan comunes que casi son invisibles, pero hoy sostienen buena parte del software que usamos a diario. Vamos a ver qué son, cómo funcionan y por qué valen tanto.

## ¿Qué es una API?

API significa **Application Programming Interface** (Interfaz de Programación de Aplicaciones). Es un conjunto de reglas y definiciones que permite que dos programas se comuniquen entre sí sin necesidad de conocer cómo está construido el otro por dentro.

La analogía clásica es la de un restaurante. Tú (el cliente) no entras a la cocina a preparar tu plato. Le haces el pedido a un camarero, que lo lleva a la cocina y te trae el resultado. La API es ese camarero: recibe tu petición, la entrega al sistema adecuado y te devuelve la respuesta. Tú no necesitas saber qué ingredientes hay ni cómo se cocina; solo conocer el menú.

## ¿Para qué sirve?

Una API sirve, en esencia, para **exponer funcionalidades o datos de forma controlada**. Algunos usos habituales:

- **Integrar servicios:** pagar con Stripe o PayPal, enviar correos con un proveedor externo o mostrar mapas de terceros.
- **Conectar frontend y backend:** tu aplicación web pide datos a un servidor mediante una API y los muestra al usuario.
- **Automatizar tareas:** sincronizar un CRM con una hoja de cálculo o publicar contenido en redes sociales desde un script.
- **Reutilizar lógica:** en lugar de reescribir algo complejo (autenticación, geolocalización, traducción), lo consumes ya hecho.
- **Abrir una plataforma a terceros:** permitir que otros desarrolladores construyan sobre tu producto.

## Cómo funciona una API

El modelo más extendido es **cliente-servidor**. El cliente envía una *petición* (request) y el servidor devuelve una *respuesta* (response). En las APIs web, esto ocurre normalmente sobre HTTP.

Una petición suele incluir:

1. **Un endpoint (URL):** la dirección del recurso, por ejemplo `https://api.ejemplo.com/usuarios/42`.
2. **Un método HTTP:** indica la acción que quieres realizar.
3. **Cabeceras (headers):** metadatos como el formato esperado o las credenciales.
4. **Un cuerpo (body):** los datos que envías, si procede.

Los métodos más comunes son:

| Método | Acción |
|--------|--------|
| `GET` | Obtener un recurso |
| `POST` | Crear un recurso |
| `PUT` / `PATCH` | Actualizar un recurso |
| `DELETE` | Eliminar un recurso |

La respuesta incluye un **código de estado** (como `200 OK`, `404 Not Found` o `500 Internal Server Error`) y, normalmente, datos en formato **JSON**.

### Un ejemplo sencillo

Pedimos la información de un usuario:

```bash
curl https://api.ejemplo.com/usuarios/42 \
  -H "Authorization: Bearer TU_TOKEN"
```

Y el servidor responde:

```json
{
  "id": 42,
  "nombre": "Ana García",
  "email": "ana@ejemplo.com",
  "activo": true
}
```

Desde JavaScript, lo mismo se vería así:

```javascript
const respuesta = await fetch("https://api.ejemplo.com/usuarios/42", {
  headers: { Authorization: "Bearer TU_TOKEN" },
});

if (!respuesta.ok) {
  throw new Error(`Error ${respuesta.status}`);
}

const usuario = await respuesta.json();
console.log(usuario.nombre);
```

## Tipos de API más habituales

- **REST:** la más popular. Usa HTTP, recursos identificados por URL y suele devolver JSON. Es simple y fácil de adoptar.
- **GraphQL:** el cliente define exactamente qué datos necesita en una sola consulta, evitando pedir de más o de menos.
- **gRPC:** pensada para comunicación eficiente entre servicios, usa Protocol Buffers y es muy rápida.
- **WebSockets:** comunicación bidireccional en tiempo real, ideal para chats o notificaciones en vivo.

Además, según su acceso, pueden ser **públicas** (abiertas a cualquiera), **privadas** (de uso interno) o de **partners** (compartidas con socios concretos).

## Autenticación y seguridad

Una API expone datos y acciones, así que protegerla es fundamental. Las prácticas más habituales son:

- **API keys:** una clave que identifica a quien consume el servicio.
- **OAuth 2.0:** permite dar acceso limitado a un tercero sin compartir tu contraseña.
- **Tokens JWT:** credenciales firmadas que viajan en cada petición.
- **Rate limiting:** limitar el número de peticiones para evitar abusos.
- **HTTPS siempre:** cifrar la comunicación es innegociable.

## Por qué son tan valiosas

### 1. Ahorran tiempo y dinero
No tienes que construir todo desde cero. Integrar un servicio de pagos o de mapas con una API lleva horas; desarrollarlo internamente llevaría meses.

### 2. Fomentan la modularidad
Separar un sistema en servicios que se comunican mediante APIs facilita el mantenimiento, las pruebas y el escalado de cada parte por separado.

### 3. Crean ecosistemas
Plataformas como Shopify, Slack o GitHub han crecido en gran parte porque otros desarrolladores construyen herramientas sobre sus APIs, lo que multiplica el valor del producto.

### 4. Son un modelo de negocio
Muchas empresas monetizan directamente su API: cobran por petición, por volumen o por funcionalidades. Se habla incluso de la *economía de las APIs*.

### 5. Permiten innovar más rápido
Combinar APIs existentes permite prototipar ideas en días. Hoy, por ejemplo, integrar un modelo de lenguaje en una aplicación es cuestión de unas pocas líneas de código.

## Buenas prácticas si vas a crear una

- Diseña **URLs claras y consistentes** (`/usuarios`, `/pedidos`).
- Usa **los códigos de estado HTTP correctamente**.
- **Versiona** tu API (`/v1/`, `/v2/`) para no romper a quienes ya la usan.
- Escribe **documentación** buena, con ejemplos. Herramientas como OpenAPI/Swagger ayudan mucho.
- Devuelve **errores descriptivos** que ayuden a depurar.
- Piensa en la **paginación** desde el principio.

## Conclusión

Una API es, ante todo, un **contrato**: define qué puedes pedir, cómo hacerlo y qué recibirás a cambio. Gracias a ese contrato, sistemas construidos por equipos distintos, en lenguajes distintos y en lugares distintos pueden trabajar juntos como si fueran uno solo.

Entender las APIs ya no es opcional para quien desarrolla software: son el pegamento de internet moderno. Si estás empezando, mi consejo es sencillo: elige una API pública (la del clima, la de GitHub o la de PokéAPI), haz tus primeras peticiones con `curl` o `fetch` y observa qué pasa. Es la forma más rápida de que todo esto cobre sentido.

¿Y tú? ¿Cuál fue la primera API que usaste? Cuéntamelo en los comentarios. 👇
