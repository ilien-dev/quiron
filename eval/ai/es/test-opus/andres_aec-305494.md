# Cómo medir el rendimiento en NodeJS

Cuando una aplicación en Node.js empieza a ir lenta, la tentación es ponerse a optimizar a ciegas: cambiar un bucle por aquí, cachear algo por allá y cruzar los dedos. El problema es que sin medir, no sabes si estás mejorando algo o simplemente moviendo el cuello de botella de sitio.

En este artículo vamos a repasar las herramientas que Node.js pone a nuestra disposición para medir el rendimiento, desde lo más básico hasta el perfilado de CPU y memoria. La idea es que al terminar tengas un pequeño kit de herramientas para diagnosticar problemas de rendimiento con datos reales.

## 1. Lo más básico: `console.time`

La forma más rápida de medir cuánto tarda un bloque de código es usar `console.time` y `console.timeEnd`:

```javascript
console.time('procesar');

const resultado = [];
for (let i = 0; i < 1_000_000; i++) {
  resultado.push(i * 2);
}

console.timeEnd('procesar');
// procesar: 12.345ms
```

Es simple y funciona para una comprobación rápida, pero tiene limitaciones: la precisión es de milisegundos, no guarda los datos para análisis posterior y ensucia el código con llamadas que luego hay que borrar.

## 2. Más precisión: `process.hrtime.bigint()`

Si necesitas precisión de nanosegundos, `process.hrtime.bigint()` es tu aliado:

```javascript
const inicio = process.hrtime.bigint();

hacerAlgoCostoso();

const fin = process.hrtime.bigint();
const duracionMs = Number(fin - inicio) / 1e6;
console.log(`Tardó ${duracionMs.toFixed(3)} ms`);
```

A diferencia de `Date.now()`, `hrtime` usa un reloj monotónico, es decir, no se ve afectado por cambios en la hora del sistema. Esto es importante: si mides con `Date.now()` y justo se sincroniza el reloj por NTP, puedes obtener duraciones negativas o absurdas.

## 3. La API `perf_hooks`

Node.js implementa una parte de la API de rendimiento del navegador (User Timing) mediante el módulo `perf_hooks`. Esto permite marcar puntos en el tiempo y medir entre ellos de forma más estructurada:

```javascript
const { performance, PerformanceObserver } = require('node:perf_hooks');

const observer = new PerformanceObserver((items) => {
  for (const entry of items.getEntries()) {
    console.log(`${entry.name}: ${entry.duration.toFixed(2)} ms`);
  }
});
observer.observe({ entryTypes: ['measure'] });

performance.mark('inicio-consulta');
await consultarBaseDeDatos();
performance.mark('fin-consulta');

performance.measure('consulta BD', 'inicio-consulta', 'fin-consulta');
```

La ventaja de este enfoque es que separas la medición de la forma en que consumes los datos. El `PerformanceObserver` podría, por ejemplo, enviar las métricas a un sistema de monitorización en lugar de imprimirlas por consola.

### Medir funciones con `timerify`

`perf_hooks` también incluye `performance.timerify`, que envuelve una función y registra automáticamente cuánto tarda cada llamada:

```javascript
const { performance, PerformanceObserver } = require('node:perf_hooks');

function calcularPrimos(limite) {
  const primos = [];
  for (let n = 2; n < limite; n++) {
    if (primos.every((p) => n % p !== 0)) primos.push(n);
  }
  return primos;
}

const calcularPrimosMedido = performance.timerify(calcularPrimos);

const obs = new PerformanceObserver((list) => {
  console.log(list.getEntries()[0].duration);
  obs.disconnect();
});
obs.observe({ entryTypes: ['function'] });

calcularPrimosMedido(10_000);
```

## 4. Medir el event loop

En Node.js, uno de los problemas de rendimiento más comunes no es que una operación sea lenta en sí, sino que **bloquea el event loop**. Mientras el hilo principal está ocupado con un cálculo síncrono pesado, ninguna otra petición puede atenderse.

`perf_hooks` ofrece `monitorEventLoopDelay`, que mide el retraso del event loop mediante un histograma:

```javascript
const { monitorEventLoopDelay } = require('node:perf_hooks');

const histograma = monitorEventLoopDelay({ resolution: 20 });
histograma.enable();

setInterval(() => {
  console.log({
    min: histograma.min / 1e6,
    max: histograma.max / 1e6,
    media: histograma.mean / 1e6,
    p99: histograma.percentile(99) / 1e6,
  });
  histograma.reset();
}, 5000);
```

Si ves que el percentil 99 se dispara a cientos de milisegundos, tienes código síncrono que está bloqueando el proceso. Es una métrica muy útil para tener en producción.

## 5. Uso de memoria

Para ver cuánta memoria está usando tu proceso, puedes usar `process.memoryUsage()`:

```javascript
const formato = (bytes) => `${(bytes / 1024 / 1024).toFixed(2)} MB`;

const uso = process.memoryUsage();
console.log({
  rss: formato(uso.rss),
  heapTotal: formato(uso.heapTotal),
  heapUsed: formato(uso.heapUsed),
  external: formato(uso.external),
});
```

- **rss** (Resident Set Size): memoria total que el sistema operativo ha asignado al proceso.
- **heapTotal** y **heapUsed**: memoria reservada y usada por el heap de V8.
- **external**: memoria usada por objetos C++ vinculados a objetos JavaScript, como los `Buffer`.

Si `heapUsed` crece de forma continua y nunca baja después de las recolecciones de basura, probablemente tienes una fuga de memoria.

## 6. Perfilado de CPU con `--prof` y `--cpu-prof`

Cuando no sabes exactamente dónde está el problema, lo mejor es perfilar la aplicación completa. Node.js incluye dos opciones:

### `--prof`

```bash
node --prof app.js
```

Esto genera un archivo `isolate-0x...-v8.log`. Para convertirlo en algo legible:

```bash
node --prof-process isolate-0x*.log > perfil.txt
```

El resultado muestra qué funciones consumieron más tiempo de CPU, separando el código JavaScript, el código C++ y el recolector de basura.

### `--cpu-prof`

Una opción más moderna es:

```bash
node --cpu-prof app.js
```

Esto genera un archivo `.cpuprofile` que puedes abrir directamente en las Chrome DevTools (pestaña *Performance* o *JavaScript Profiler*) y ver un flame graph interactivo. Personalmente, es la opción que más uso porque la visualización hace mucho más fácil detectar las funciones problemáticas.

## 7. Chrome DevTools con `--inspect`

Si prefieres trabajar de forma interactiva, arranca tu aplicación con:

```bash
node --inspect app.js
```

Luego abre `chrome://inspect` en Chrome y conéctate al proceso. Desde ahí puedes:

- Grabar perfiles de CPU mientras lanzas peticiones a la aplicación.
- Tomar *heap snapshots* y compararlos para encontrar fugas de memoria.
- Poner breakpoints y depurar como en el navegador.

Una técnica muy efectiva para encontrar fugas: toma un snapshot, ejecuta la operación sospechosa varias veces, toma otro snapshot y compara. Los objetos que aparecen en el segundo y no deberían estar ahí son tus candidatos.

## 8. Pruebas de carga: `autocannon`

Medir una función aislada está bien, pero muchas veces lo que quieres saber es cuántas peticiones por segundo aguanta tu servidor. Para eso, `autocannon` es una herramienta excelente escrita en Node:

```bash
npx autocannon -c 100 -d 10 http://localhost:3000
```

Esto lanza 100 conexiones concurrentes durante 10 segundos y te devuelve latencias (media, p99, máxima), peticiones por segundo y throughput. Es ideal para comparar el antes y el después de una optimización.

## 9. Clinic.js

Si quieres ir un paso más allá, **Clinic.js** es un conjunto de herramientas que automatiza gran parte del diagnóstico:

```bash
npm install -g clinic
clinic doctor -- node app.js
```

- `clinic doctor` detecta el tipo de problema (event loop bloqueado, I/O, memoria).
- `clinic flame` genera flame graphs.
- `clinic bubbleprof` analiza las operaciones asíncronas.

Combinado con `autocannon`, te da un diagnóstico bastante completo con muy poco esfuerzo.

## Buenas prácticas al medir

Antes de terminar, algunos consejos que te ahorrarán conclusiones erróneas:

1. **Calienta el código**: V8 optimiza las funciones después de ejecutarlas varias veces. Las primeras ejecuciones siempre serán más lentas, así que descártalas.
2. **Repite las mediciones**: una sola ejecución no significa nada. Toma varias y fíjate en la mediana y los percentiles, no solo en la media.
3. **Mide en condiciones parecidas a producción**: usa `NODE_ENV=production` y datos de un tamaño realista.
4. **Cambia una cosa cada vez**: si aplicas cinco optimizaciones a la vez, no sabrás cuál ha funcionado.
5. **No optimices lo que no importa**: si una función tarda 2 ms en una petición que tarda 800 ms, el problema está en otro sitio.

## Conclusión

Node.js viene con un conjunto de herramientas de medición bastante potente sin necesidad de instalar nada: `console.time` para comprobaciones rápidas, `perf_hooks` para mediciones estructuradas y del event loop, `process.memoryUsage` para la memoria y los flags `--cpu-prof` e `--inspect` para perfilados completos. Si a eso le sumas `autocannon` y Clinic.js, tienes todo lo necesario para dejar de adivinar y empezar a optimizar con datos.

La próxima vez que alguien diga "esto va lento", ya sabes por dónde empezar: mide primero, optimiza después.
