# Cómo limitar las peticiones a una API

Si publicas una API, tarde o temprano alguien la usará más de lo previsto. Puede ser un script con un bucle mal escrito, un cliente que reintenta sin pausa o un bot que prueba contraseñas. Sin límites, una sola fuente puede degradar el servicio para todos. La solución es el **rate limiting**: restringir cuántas peticiones puede hacer un cliente en un periodo de tiempo.

## ¿Por qué limitar?

- **Estabilidad:** evitas que un cliente acapare CPU, memoria o conexiones a la base de datos.
- **Seguridad:** frenas ataques de fuerza bruta contra endpoints como `/login`.
- **Costes:** si tu backend llama a servicios de pago, cada petición cuesta dinero.
- **Equidad:** todos los usuarios reciben una calidad de servicio razonable.

## Los algoritmos más comunes

### 1. Ventana fija (fixed window)

Cuentas las peticiones por intervalo, por ejemplo 100 por minuto, y el contador se reinicia al empezar cada minuto. Es fácil de implementar, pero tiene un problema: un cliente puede hacer 100 peticiones a las 12:00:59 y otras 100 a las 12:01:00, o sea 200 en dos segundos.

### 2. Ventana deslizante (sliding window)

En lugar de reiniciar el contador en momentos fijos, miras siempre los últimos 60 segundos. Elimina los picos en los bordes de la ventana a cambio de algo más de cálculo o memoria.

### 3. Token bucket

Cada cliente tiene un "cubo" con capacidad para N tokens, que se rellena a un ritmo constante. Cada petición consume un token, y si el cubo está vacío la petición se rechaza. Permite ráfagas cortas sin perder el control del promedio, y por eso es el algoritmo que usan muchos proveedores de APIs públicas.

### 4. Leaky bucket

Las peticiones entran en una cola que se vacía a ritmo constante. Suaviza el tráfico de salida, pero añade latencia.

## Ejemplo rápido con Express

Para la mayoría de los proyectos basta con una librería probada:

```bash
npm install express-rate-limit
```

```javascript
import express from 'express';
import rateLimit from 'express-rate-limit';

const app = express();

const limiter = rateLimit({
  windowMs: 60 * 1000,    // 1 minuto
  limit: 100,             // 100 peticiones por IP y ventana
  standardHeaders: 'draft-7',
  legacyHeaders: false,
});

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 5,
  message: { error: 'Demasiados intentos, prueba más tarde.' },
});

app.use('/api', limiter);
app.post('/login', loginLimiter, (req, res) => { /* ... */ });

app.listen(3000);
```

## Implementando un token bucket a mano

Si quieres entender qué pasa por dentro:

```javascript
const buckets = new Map();
const CAPACITY = 10;
const REFILL_PER_SEC = 1;

function allow(clientId) {
  const now = Date.now() / 1000;
  const b = buckets.get(clientId) ?? { tokens: CAPACITY, last: now };

  b.tokens = Math.min(CAPACITY, b.tokens + (now - b.last) * REFILL_PER_SEC);
  b.last = now;

  if (b.tokens < 1) {
    buckets.set(clientId, b);
    return false;
  }
  b.tokens -= 1;
  buckets.set(clientId, b);
  return true;
}
```

## ¿Y si tengo varios servidores?

Un `Map` en memoria solo funciona con una instancia. Si tienes varias detrás de un balanceador, cada una llevará su propia cuenta. Lo habitual es guardar los contadores en **Redis**, que ofrece operaciones atómicas como `INCR` y `EXPIRE`, o scripts Lua para algoritmos más complejos. `express-rate-limit` tiene adaptadores como `rate-limit-redis` para esto.

También puedes delegar el límite en la capa de infraestructura, por ejemplo en Nginx (`limit_req`), en un API Gateway o en tu CDN.

## Buenas prácticas

1. **Responde con `429 Too Many Requests`.** No uses un 500 ni un 403.
2. **Incluye la cabecera `Retry-After`** para que el cliente sepa cuánto esperar.
3. **Expón los límites** con cabeceras como `RateLimit-Limit` y `RateLimit-Remaining`.
4. **Elige bien la clave.** Limitar por IP es sencillo, pero penaliza a usuarios detrás de la misma NAT. Si hay autenticación, limita por usuario o API key.
5. **Aplica límites distintos por endpoint.** Un `GET` barato no necesita el mismo límite que un endpoint que genera informes.
6. **Documenta tus límites** para que los desarrolladores puedan diseñar sus integraciones con ellos en mente.
7. **Ojo con los proxies.** Si estás detrás de uno, configura `app.set('trust proxy', 1)` para leer la IP real, pero solo si confías en ese proxy.

## Conclusión

Limitar las peticiones es una de las medidas más baratas y efectivas para proteger una API. Empieza con una librería y una ventana deslizante o un token bucket. Cuando escales a varias instancias, mueve los contadores a Redis. Tu servidor y tus usuarios te lo agradecerán.

---

He puesto tilde en "Cómo" en el título, que es la forma correcta en una pregunta indirecta. El front matter lleva `published: false` para que puedas revisarlo antes de publicarlo.
