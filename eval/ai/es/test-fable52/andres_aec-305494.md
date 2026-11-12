"Mi API va lenta" no es un diagnóstico, es un síntoma. Antes de reescribir ese bucle o de cambiar de framework, necesitas datos: qué es lento, cuánto y por qué. Optimizar sin medir es adivinar, y casi siempre adivinamos mal.

La buena noticia es que NodeJS trae de serie casi todo lo necesario. En este post repasamos las herramientas, de la más simple a la más potente, y cuándo usar cada una.

## 1. Medir tiempos: de `console.time` a `perf_hooks`

Lo más básico es cronometrar un trozo de código. Olvídate de `Date.now()`: tiene resolución de milisegundos y depende del reloj del sistema, que puede ajustarse en mitad de tu medición. Usa `performance.now()`, que es monotónico y tiene resolución de sub-milisegundo:

```js
import { performance } from 'node:perf_hooks';

const inicio = performance.now();
await procesarPedidos();
const duracion = performance.now() - inicio;

console.log(`procesarPedidos: ${duracion.toFixed(2)} ms`);
```

Para una comprobación rápida, `console.time('etiqueta')` y `console.timeEnd('etiqueta')` hacen lo mismo con menos código. Y si necesitas nanosegundos, tienes `process.hrtime.bigint()`.

### Marcas y medidas

Cuando quieres instrumentar varias fases de un proceso, la User Timing API es más cómoda que ir restando variables:

```js
import { performance, PerformanceObserver } from 'node:perf_hooks';

const obs = new PerformanceObserver((lista) => {
  for (const entrada of lista.getEntries()) {
    console.log(`${entrada.name}: ${entrada.duration.toFixed(2)} ms`);
  }
});
obs.observe({ entryTypes: ['measure'] });

performance.mark('db-inicio');
const filas = await consultarBaseDeDatos();
performance.mark('db-fin');

const resultado = transformar(filas);
performance.mark('transformacion-fin');

performance.measure('consulta', 'db-inicio', 'db-fin');
performance.measure('transformacion', 'db-fin', 'transformacion-fin');
```

La ventaja del `PerformanceObserver` es que separa la instrumentación del reporte: tu código solo pone marcas, y en un único sitio decides si las mandas a la consola, a un log o a tu sistema de métricas.

### Cronometrar funciones con `timerify`

Si lo que quieres es saber cuánto tarda una función concreta cada vez que se llama, `performance.timerify` la envuelve por ti:

```js
import { performance, PerformanceObserver } from 'node:perf_hooks';

function calcularRuta(origen, destino) {
  /* ... */
}

const calcularRutaMedida = performance.timerify(calcularRuta);

new PerformanceObserver((lista) => {
  const [entrada] = lista.getEntries();
  console.log(`${entrada.name}: ${entrada.duration.toFixed(3)} ms`);
}).observe({ entryTypes: ['function'] });

calcularRutaMedida('Madrid', 'Sevilla');
```

## 2. La salud del event loop

En NodeJS, el tiempo de una función aislada cuenta solo parte de la historia. Como todo tu JavaScript corre en un único hilo, una operación síncrona de 200 ms no solo tarda 200 ms: bloquea todas las demás peticiones durante ese tiempo. Por eso la métrica más característica de Node es el retraso del event loop.

```js
import { monitorEventLoopDelay } from 'node:perf_hooks';

const histograma = monitorEventLoopDelay({ resolution: 20 });
histograma.enable();

setInterval(() => {
  // Los valores vienen en nanosegundos
  const ms = (ns) => (ns / 1e6).toFixed(2);
  console.log({
    media: ms(histograma.mean),
    p99: ms(histograma.percentile(99)),
    max: ms(histograma.max),
  });
  histograma.reset();
}, 5000);
```

Si el p99 se dispara a decenas o cientos de milisegundos, algo está bloqueando el hilo: un `JSON.parse` gigante, un bucle pesado, criptografía síncrona, una expresión regular con backtracking...

La métrica complementaria es la utilización del event loop (ELU), que indica qué fracción del tiempo el loop está ocupado en lugar de esperando:

```js
import { performance } from 'node:perf_hooks';

let anterior = performance.eventLoopUtilization();

setInterval(() => {
  const actual = performance.eventLoopUtilization();
  const delta = performance.eventLoopUtilization(actual, anterior);
  console.log(`ELU: ${(delta.utilization * 100).toFixed(1)} %`);
  anterior = actual;
}, 5000);
```

Un ELU cercano al 100 % significa que el proceso está saturado, aunque la CPU de la máquina parezca tranquila. Suele ser mejor señal para autoescalar que el porcentaje de CPU.

## 3. Memoria y recolector de basura

Para una foto rápida del consumo de memoria:

```js
const mb = (bytes) => (bytes / 1024 / 1024).toFixed(1);
const { rss, heapUsed, heapTotal, external } = process.memoryUsage();

console.log(`RSS: ${mb(rss)} MB | Heap: ${mb(heapUsed)}/${mb(heapTotal)} MB | Externa: ${mb(external)} MB`);
```

- `rss`: toda la memoria que el proceso ocupa en RAM.
- `heapUsed` / `heapTotal`: el heap de V8, donde viven tus objetos.
- `external`: memoria fuera del heap gestionada por V8 (por ejemplo, los `Buffer`).

Un valor aislado dice poco; lo que importa es la tendencia. Si `heapUsed` crece sin parar tras cada ciclo de GC, tienes una fuga. Para encontrarla, genera *heap snapshots* con `v8.writeHeapSnapshot()` en dos momentos distintos y compáralos en la pestaña *Memory* de Chrome DevTools.

También puedes observar las pausas del recolector, que a veces explican picos de latencia misteriosos:

```js
import { PerformanceObserver } from 'node:perf_hooks';

new PerformanceObserver((lista) => {
  for (const entrada of lista.getEntries()) {
    if (entrada.duration > 50) {
      console.warn(`Pausa de GC larga: ${entrada.duration.toFixed(1)} ms`);
    }
  }
}).observe({ entryTypes: ['gc'] });
```

## 4. Perfilado de CPU: encontrar el culpable

Las métricas anteriores te dicen *que* hay un problema. El profiler te dice *dónde*. La forma más sencilla no requiere instalar nada:

```bash
node --cpu-prof --cpu-prof-dir=./perfiles app.js
```

Al terminar el proceso, Node escribe un fichero `.cpuprofile` que puedes abrir en Chrome DevTools (pestaña *Performance*) o directamente en VS Code. Verás un *flame graph*: cada barra es una función y su anchura es el tiempo que ha pasado en la CPU. Busca las barras anchas, ahí está tu cuello de botella.

Si prefieres perfilar en vivo, arranca con `node --inspect app.js`, abre `chrome://inspect` en Chrome y tendrás las DevTools completas conectadas a tu proceso: profiler de CPU, heap snapshots y debugger.

Como alternativas de terceros, [0x](https://github.com/davidmarkclements/0x) genera un flame graph interactivo con un solo comando (`npx 0x app.js`), y la suite Clinic.js ofrece diagnósticos guiados, aunque lleva tiempo sin mucho mantenimiento.

Un consejo importante: perfila bajo carga realista. Un servidor sin tráfico no tiene nada interesante que enseñarte.

## 5. Pruebas de carga con autocannon

Para generar esa carga en un servidor HTTP, [autocannon](https://github.com/mcollina/autocannon) es la opción habitual en el ecosistema:

```bash
npx autocannon -c 100 -d 30 http://localhost:3000/api/pedidos
```

Esto lanza 100 conexiones concurrentes durante 30 segundos y te devuelve peticiones por segundo, throughput y latencias por percentil.

Fíjate en los percentiles, no en la media. Una media de 20 ms puede esconder un p99 de 900 ms, y ese 1 % de peticiones lentas son usuarios reales teniendo una mala experiencia. Además, en una página que hace muchas llamadas a tu API, la probabilidad de toparse con al menos una de esas peticiones lentas es mucho mayor que el 1 %.

Un flujo de trabajo muy efectivo es combinar las dos cosas: arrancar el servidor con `--cpu-prof`, lanzarle autocannon y analizar el perfil resultante.

## 6. Microbenchmarks sin autoengañarse

A veces quieres comparar dos implementaciones de una función. Un bucle con `performance.now()` alrededor suele dar resultados engañosos, porque V8 es un compilador JIT:

- El código arranca interpretado y se optimiza al "calentarse". Las primeras iteraciones no son representativas.
- Si no usas el resultado, V8 puede eliminar el cálculo entero y estarás midiendo un bucle vacío.
- Una sola ejecución no tiene validez estadística: el GC o cualquier otro proceso pueden contaminarla.

Usa una librería que gestione el calentamiento y la estadística, como [tinybench](https://github.com/tinylibs/tinybench) o [mitata](https://github.com/evanwashere/mitata):

```js
import { Bench } from 'tinybench';

const datos = Array.from({ length: 10_000 }, (_, i) => i);
const bench = new Bench({ time: 1000 });

bench
  .add('for clásico', () => {
    let suma = 0;
    for (let i = 0; i < datos.length; i++) suma += datos[i];
    return suma;
  })
  .add('reduce', () => datos.reduce((acc, n) => acc + n, 0));

await bench.run();
console.table(bench.table());
```

Y aun así, tómate los microbenchmarks con escepticismo: que una función sea un 30 % más rápida en aislamiento no importa si representa el 0,1 % del tiempo total de tu petición. Deja que el profiler te diga qué merece la pena optimizar.

## Buenas prácticas para medir bien

1. **Establece una línea base.** Mide antes de tocar nada; sin el "antes" no puedes demostrar el "después".
2. **Cambia una sola cosa cada vez.** Si aplicas tres optimizaciones juntas, no sabrás cuál funcionó ni cuál empeoró las cosas.
3. **Mide en condiciones parecidas a producción.** Usa `NODE_ENV=production`, datos de tamaño realista y la misma versión de Node. Tu portátil con veinte pestañas abiertas no es un entorno fiable.
4. **Repite las mediciones.** Una ejecución es una anécdota; varias son un dato.
5. **Monitoriza en producción.** Exporta el retraso del event loop, el ELU, la memoria y las latencias a tu sistema de métricas, con OpenTelemetry o `prom-client`, por ejemplo. Los problemas más interesantes solo aparecen con tráfico real.

## Resumen

| Pregunta | Herramienta |
|---|---|
| ¿Cuánto tarda este código? | `performance.now()`, `mark`/`measure`, `timerify` |
| ¿Se está bloqueando el hilo? | `monitorEventLoopDelay`, `eventLoopUtilization` |
| ¿Hay una fuga de memoria? | `process.memoryUsage()`, heap snapshots |
| ¿Qué función consume la CPU? | `--cpu-prof`, `--inspect`, 0x |
| ¿Cuánto tráfico aguanta el servidor? | autocannon |
| ¿Cuál de las dos implementaciones es más rápida? | tinybench, mitata |

El orden importa: primero mide el sistema completo bajo carga, después usa el profiler para localizar el cuello de botella y solo entonces baja al detalle. Casi siempre el problema está en un sitio distinto al que sospechabas.

¿Qué herramientas usas tú para medir el rendimiento de tus aplicaciones Node? Te leo en los comentarios 👇
