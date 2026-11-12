# Cómo medir el rendimiento en NodeJS

"Esto va lento" no es un diagnóstico. Antes de optimizar hay que **medir**: saber qué es lento, cuánto y por qué. NodeJS incluye muchas herramientas para ello, y la mayoría no necesitan instalar nada.

En este post veremos, de lo más simple a lo más profundo:

1. Medir el tiempo de un fragmento de código
2. Usar `perf_hooks` para marcas y mediciones
3. Vigilar la salud del event loop
4. Medir el consumo de memoria
5. Perfilar la CPU
6. Hacer benchmarks y pruebas de carga sin engañarte

## 1. Lo básico: medir tiempos correctamente

Lo primero que todos hacemos es esto:

```js
const inicio = Date.now();
hacerAlgo();
console.log(`Tardó ${Date.now() - inicio} ms`);
```

Funciona, pero tiene dos problemas. `Date.now()` solo tiene precisión de milisegundos, y depende del reloj del sistema, que puede ajustarse (NTP, cambios de hora) en mitad de la medición.

Para medir duraciones usa un **reloj monotónico** de alta resolución:

```js
const inicio = performance.now(); // global desde Node 16
hacerAlgo();
console.log(`Tardó ${(performance.now() - inicio).toFixed(3)} ms`);
```

Si necesitas nanosegundos, tienes `process.hrtime.bigint()`:

```js
const inicio = process.hrtime.bigint();
hacerAlgo();
const ns = process.hrtime.bigint() - inicio;
console.log(`Tardó ${Number(ns) / 1e6} ms`);
```

Y para algo rápido durante el desarrollo, `console.time` sigue siendo práctico:

```js
console.time('consulta');
await db.query('SELECT ...');
console.timeEnd('consulta'); // consulta: 12.345ms
```

## 2. `perf_hooks`: marcas, medidas y observadores

El módulo `node:perf_hooks` implementa la API de User Timing del navegador. Su ventaja es que permite poner **marcas con nombre** a lo largo del código y recoger las mediciones en un único sitio, sin llenar todo de `console.log`.

```js
import { performance, PerformanceObserver } from 'node:perf_hooks';

const obs = new PerformanceObserver((lista) => {
  for (const entrada of lista.getEntries()) {
    console.log(`${entrada.name}: ${entrada.duration.toFixed(2)} ms`);
  }
});
obs.observe({ entryTypes: ['measure'] });

performance.mark('inicio-carga');
const datos = await cargarDatos();
performance.mark('fin-carga');

performance.mark('inicio-proceso');
procesar(datos);
performance.mark('fin-proceso');

performance.measure('carga', 'inicio-carga', 'fin-carga');
performance.measure('proceso', 'inicio-proceso', 'fin-proceso');
```

El observador desacopla la medición de lo que haces con ella. Puedes imprimirla, mandarla a tu sistema de métricas o descartarla según el entorno.

### `timerify`: medir funciones sin tocarlas

Si quieres saber cuánto tarda una función cada vez que se llama, `performance.timerify` la envuelve por ti:

```js
import { performance, PerformanceObserver } from 'node:perf_hooks';

function parsearCSV(texto) {
  /* ... */
}

const parsearMedido = performance.timerify(parsearCSV);

new PerformanceObserver((lista) => {
  for (const e of lista.getEntries()) {
    console.log(`${e.name} → ${e.duration.toFixed(2)} ms`);
  }
}).observe({ entryTypes: ['function'] });

parsearMedido(miCSV);
```

> ⚠️ Recuerda llamar a `performance.clearMarks()` y `performance.clearMeasures()` si generas muchas marcas en un proceso de larga duración, o se acumularán en memoria.

## 3. La métrica que más importa: el event loop

NodeJS ejecuta tu JavaScript en un solo hilo. Si una operación síncrona tarda 200 ms, **todas** las demás peticiones esperan 200 ms. Por eso la salud del event loop suele ser la métrica más reveladora de una aplicación Node.

### Retraso del event loop

`monitorEventLoopDelay` mide cuánto se retrasa el loop respecto a lo esperado y guarda los datos en un histograma:

```js
import { monitorEventLoopDelay } from 'node:perf_hooks';

const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();

setInterval(() => {
  // Los valores vienen en nanosegundos
  console.log({
    media: (h.mean / 1e6).toFixed(2) + ' ms',
    p99: (h.percentile(99) / 1e6).toFixed(2) + ' ms',
    max: (h.max / 1e6).toFixed(2) + ' ms',
  });
  h.reset();
}, 5000);
```

Fíjate en el **p99** y el **máximo**, no solo en la media. Una media de 2 ms con picos de 300 ms significa que algunos usuarios sufren esperas notables.

### Utilización del event loop (ELU)

`eventLoopUtilization` indica qué fracción del tiempo el loop estuvo ocupado ejecutando código frente a esperando I/O. Es más útil que el uso de CPU para decidir si un proceso está saturado:

```js
import { performance } from 'node:perf_hooks';

let anterior = performance.eventLoopUtilization();

setInterval(() => {
  const actual = performance.eventLoopUtilization(anterior);
  console.log(`ELU: ${(actual.utilization * 100).toFixed(1)}%`);
  anterior = performance.eventLoopUtilization();
}, 5000);
```

Un ELU que se acerca al 100% de forma sostenida significa que el proceso no da más de sí. Toca optimizar el código caliente, mover trabajo pesado a `worker_threads` o escalar horizontalmente.

## 4. Memoria: cuánto usas y si estás perdiendo

`process.memoryUsage()` te da una foto instantánea:

```js
const mb = (b) => (b / 1024 / 1024).toFixed(1) + ' MB';
const m = process.memoryUsage();

console.log({
  rss: mb(m.rss),             // memoria total del proceso
  heapTotal: mb(m.heapTotal), // heap reservado por V8
  heapUsed: mb(m.heapUsed),   // heap realmente usado
  external: mb(m.external),   // memoria fuera del heap (Buffers, etc.)
});
```

Una sola lectura dice poco. Lo interesante es la **tendencia**. Si `heapUsed` crece sin parar a lo largo de horas, incluso después de que el recolector de basura haga su trabajo, probablemente tienes una fuga de memoria.

Para encontrar al culpable necesitas un *heap snapshot*:

```js
import { writeHeapSnapshot } from 'node:v8';

process.on('SIGUSR2', () => {
  const archivo = writeHeapSnapshot();
  console.log(`Snapshot guardado en ${archivo}`);
});
```

Toma un snapshot al arrancar y otro tras un rato de carga. Ábrelos en Chrome DevTools (pestaña *Memory*) y usa la vista *Comparison* para ver qué objetos se han acumulado entre ambos. Los sospechosos habituales son cachés sin límite, *listeners* que nunca se eliminan y closures que retienen objetos grandes.

> Generar un snapshot bloquea el proceso y puede requerir tanta memoria como el propio heap. Úsalo con cuidado en producción. En Windows, `SIGUSR2` no existe: usa otro disparador, como un endpoint interno protegido.

## 5. Perfilar la CPU: ¿dónde se va el tiempo?

Cuando sabes que algo es lento pero no sabes **qué** exactamente, necesitas un perfilador.

### Con Chrome DevTools

```bash
node --inspect app.js
```

Abre `chrome://inspect` en Chrome, conéctate al proceso y graba un perfil en la pestaña *Performance* o *Profiler* mientras generas carga. Obtendrás un *flame graph* donde las barras más anchas son las funciones que más tiempo consumen.

### Sin interfaz: `--cpu-prof`

Para entornos sin navegador, o para automatizar, Node puede escribir el perfil directamente a disco:

```bash
node --cpu-prof --cpu-prof-dir=./perfiles app.js
```

Al terminar el proceso se genera un archivo `.cpuprofile` que puedes arrastrar a DevTools o a herramientas como [speedscope](https://www.speedscope.app/). Existe también `--heap-prof` para perfilar asignaciones de memoria con el mismo flujo.

### Cómo leer un flame graph

- **El ancho es lo que importa**, no la altura. Una barra ancha es una función que pasa mucho tiempo en la CPU.
- Busca "mesetas": funciones anchas en la parte superior. Son las que consumen tiempo por sí mismas y no a través de sus llamadas.
- Los nombres `(anonymous)` dificultan el análisis. Nombrar tus funciones flecha ayuda más de lo que parece.
- Las barras de `(garbage collector)` muy anchas indican que estás creando demasiados objetos temporales.

## 6. Benchmarks y pruebas de carga sin engañarte

### Microbenchmarks

Comparar dos implementaciones con un bucle y `performance.now()` es tentador, pero engañoso. V8 optimiza el código en caliente (JIT), elimina código cuyo resultado no se usa y el recolector de basura introduce ruido. Una librería como [tinybench](https://github.com/tinylibs/tinybench) gestiona el calentamiento, las repeticiones y las estadísticas por ti:

```js
import { Bench } from 'tinybench';

const bench = new Bench({ time: 500 });
const arr = Array.from({ length: 10_000 }, (_, i) => i);

bench
  .add('for clásico', () => {
    let s = 0;
    for (let i = 0; i < arr.length; i++) s += arr[i];
    return s;
  })
  .add('reduce', () => arr.reduce((a, b) => a + b, 0));

await bench.run();
console.table(bench.table());
```

Aun así, desconfía de los microbenchmarks. Que algo sea un 30% más rápido aislado no importa si representa el 0,1% del tiempo total de tu petición. **Perfila primero y haz benchmarks después**, solo de lo que el perfil señala.

### Pruebas de carga HTTP

Para APIs, lo que de verdad importa es el comportamiento bajo carga. [autocannon](https://github.com/mcollina/autocannon) está escrito en Node y es muy fácil de usar:

```bash
npx autocannon -c 100 -d 30 http://localhost:3000/api/productos
```

Esto abre 100 conexiones concurrentes durante 30 segundos y te muestra peticiones por segundo, latencias (incluidos p97,5 y p99) y errores.

Un buen flujo de trabajo combina todo lo anterior:

1. Lanza la prueba de carga con autocannon.
2. Mientras tanto, vigila el retraso del event loop y el ELU.
3. Si el loop se satura, perfila la CPU con `--cpu-prof` durante la carga.
4. Optimiza la función que aparece en el flame graph.
5. Repite la prueba y **compara números**, no sensaciones.

## Buenas prácticas para medir bien

- **Mide en condiciones parecidas a producción**: misma versión de Node, `NODE_ENV=production` y datos de un tamaño realista.
- **Calienta antes de medir**. Las primeras ejecuciones no están optimizadas por el JIT.
- **Repite las mediciones** y fíjate en la dispersión. Un solo número no significa nada.
- **Usa percentiles, no medias.** Tus usuarios más afectados viven en el p99.
- **Cambia una cosa cada vez.** Si cambias tres y mejora, no sabrás cuál fue.
- **Lleva las métricas a producción.** El retraso del event loop, el ELU y la memoria son baratos de recoger y puedes exportarlos a Prometheus, OpenTelemetry o el sistema que uses.

## Conclusión

NodeJS trae de serie casi todo lo necesario para entender su rendimiento: `performance.now()` para tiempos precisos, `perf_hooks` para instrumentar, `monitorEventLoopDelay` y `eventLoopUtilization` para la salud del loop, `process.memoryUsage()` y los heap snapshots para la memoria, y `--cpu-prof` o el inspector para saber dónde se va la CPU.

La regla de oro es sencilla: **no optimices lo que no has medido**. La mayoría de las veces el cuello de botella está en un sitio que no esperabas, y los datos te llevan hasta él mucho más rápido que la intuición.

¿Qué herramientas usas tú para medir el rendimiento de tus apps Node? ¡Te leo en los comentarios! 👇

---

El post tiene unas 1.400 palabras sin contar el código. Lo he dejado con `published: false` en el front matter para que lo revises antes de publicarlo. Si quieres, lo guardo en un archivo `.md` o ajusto el tono y la extensión.
