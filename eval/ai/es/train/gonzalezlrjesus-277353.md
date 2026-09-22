# Cómo limitar las peticiones a una API

Cuando publicas una API, tarde o temprano alguien la va a usar más de lo que debería. A veces es un script mal escrito que entra en un bucle infinito, a veces es un bot que intenta adivinar contraseñas y a veces es simplemente un cliente con demasiado entusiasmo. En cualquiera de los casos, el resultado puede ser el mismo: tu servidor saturado y el resto de usuarios sin servicio.

La solución es el **rate limiting**, o limitación de peticiones. En este post vemos qué es, qué algoritmos existen y cómo implementarlo en una API con Node.js y Express.

## ¿Qué es el rate limiting?

Consiste en establecer un número máximo de peticiones que un cliente puede hacer en un periodo de tiempo. Por ejemplo, 100 peticiones por minuto por dirección IP. Si el cliente supera ese límite, la API responde con el código **429 Too Many Requests** en lugar de procesar la petición.

Sirve para:

- Proteger el servidor frente a sobrecargas y ataques de denegación de servicio.
- Evitar ataques de fuerza bruta en endpoints como el login.
- Repartir los recursos de forma justa entre los usuarios.
- Controlar costes, sobre todo si tu API depende de servicios de pago.
- Definir planes de uso (por ejemplo, gratis con 1.000 peticiones al día y premium con 100.000).

## Algoritmos más comunes

### Ventana fija (*fixed window*)

Se cuenta el número de peticiones en intervalos fijos, por ejemplo de 0:00 a 0:59. Es muy sencillo, pero tiene un problema: un cliente puede hacer 100 peticiones en el segundo 59 y otras 100 en el segundo 0 del minuto siguiente, es decir, 200 en dos segundos.

### Ventana deslizante (*sliding window*)

Tiene en cuenta las peticiones de los últimos N segundos contados desde el momento actual. Es más preciso y evita los picos en los bordes de la ventana, aunque requiere algo más de memoria.

### Token bucket

Cada cliente tiene un "cubo" con un número máximo de fichas que se recarga a un ritmo constante. Cada petición consume una ficha y, si el cubo está vacío, la petición se rechaza. Permite ráfagas cortas de tráfico sin superar la media a largo plazo, y es el que usan muchas APIs públicas.

### Leaky bucket

Las peticiones entran en una cola que se vacía a un ritmo fijo. Suaviza el tráfico, pero puede añadir latencia.

## Implementación con Express

La forma más rápida en Node.js es usar el paquete `express-rate-limit`:

```bash
npm install express-rate-limit
```

```javascript
const express = require('express');
const rateLimit = require('express-rate-limit');

const app = express();

const limitadorGeneral = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  limit: 100,               // 100 peticiones por IP en esa ventana
  standardHeaders: 'draft-7',
  legacyHeaders: false,
  message: { error: 'Demasiadas peticiones, inténtalo más tarde.' },
});

app.use('/api', limitadorGeneral);
```

Y para el login, un límite mucho más estricto:

```javascript
const limitadorLogin = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 5,
  message: { error: 'Demasiados intentos de inicio de sesión.' },
});

app.post('/api/login', limitadorLogin, (req, res) => {
  // lógica de autenticación
});
```

## Cabeceras informativas

Es buena práctica indicar al cliente cuántas peticiones le quedan mediante cabeceras como:

```
RateLimit-Limit: 100
RateLimit-Remaining: 42
RateLimit-Reset: 360
Retry-After: 360
```

Así los clientes bien escritos pueden ajustar su ritmo antes de ser bloqueados.

## Si tienes varios servidores

Por defecto, `express-rate-limit` guarda los contadores en memoria. Si tu API corre en varias instancias detrás de un balanceador, cada una tendrá su propio contador y el límite real se multiplicará. La solución es usar un almacenamiento compartido como **Redis**, por ejemplo con el paquete `rate-limit-redis`.

Otra opción es delegar el rate limiting en la capa de infraestructura: Nginx, un API Gateway (AWS API Gateway, Kong) o un servicio como Cloudflare.

## Detrás de un proxy

Si tu aplicación está detrás de un proxy o balanceador, todas las peticiones parecerán venir de la misma IP. Activa esta opción en Express para leer la IP real del cliente:

```javascript
app.set('trust proxy', 1);
```

## Conclusión

Limitar las peticiones es una de esas medidas sencillas que marcan la diferencia entre una API robusta y una que se cae al primer abuso. Empieza con un límite general, añade límites más estrictos en los endpoints sensibles y, cuando escales, lleva los contadores a Redis. Tu servidor (y tus usuarios) te lo agradecerán.
