# No todo es console.log()

Admítelo: la última vez que algo no funcionó, lo primero que escribiste fue `console.log("aquí")`. Y después `console.log("aquí 2")`. Y luego `console.log("AAAAAAA", data)`.

No pasa nada. Todos lo hemos hecho, y yo sigo haciéndolo. `console.log` es rápido, no requiere configuración y funciona en cualquier entorno de JavaScript. Pero cuando es la *única* herramienta que usas, depurar se convierte en una tarea lenta, ruidosa y frustrante.

En este post repasamos lo que hay más allá: desde métodos de `console` que probablemente no conocías hasta el depurador, los logs estructurados y la prevención de errores antes de que ocurran.

## Por qué `console.log` es tan popular

Tiene tres ventajas claras:

1. **Cero fricción.** Escribes una línea y ves el resultado.
2. **Funciona en todas partes.** Navegador, Node, Deno, Bun, React Native.
3. **No exige entender el entorno.** No necesitas configurar nada.

Pero tiene límites importantes:

- **Contamina el código.** Terminas con logs olvidados que llegan a producción.
- **Es estático.** Ves lo que imprimiste, no lo que no pensaste en imprimir.
- **Te obliga a ciclos largos.** Añadir un log, guardar, recargar, reproducir el error, leer, repetir.
- **Escala mal.** Con cientos de líneas de salida, encontrar lo importante es otro problema.

Veamos cómo mejorar cada punto.

## 1. La API de `console` es más grande de lo que crees

Antes de abandonar la consola, usémosla bien.

### `console.table()`

Perfecto para arrays y objetos:

```js
const usuarios = [
  { id: 1, nombre: "Ana", rol: "admin" },
  { id: 2, nombre: "Luis", rol: "editor" },
  { id: 3, nombre: "Marta", rol: "lector" },
];

console.table(usuarios);
```

Obtienes una tabla ordenada en lugar de un árbol de objetos plegados. También acepta un segundo argumento para filtrar columnas: `console.table(usuarios, ["nombre", "rol"])`.

### `console.group()` y `console.groupEnd()`

Organiza la salida en bloques colapsables:

```js
console.group("Petición /api/usuarios");
console.log("Método: GET");
console.log("Status: 200");
console.groupEnd();
```

### `console.time()` y `console.timeEnd()`

Mide cuánto tarda algo sin necesidad de `Date.now()`:

```js
console.time("procesar");
procesarDatos(datos);
console.timeEnd("procesar"); // procesar: 42.3ms
```

### `console.assert()`

Solo imprime si la condición es falsa:

```js
console.assert(usuario.edad >= 18, "El usuario es menor de edad", usuario);
```

Así no llenas la consola de mensajes cuando todo va bien.

### `console.count()`

Cuenta cuántas veces se ejecuta una línea. Ideal para detectar renders de más en React:

```js
function Componente() {
  console.count("render Componente");
  // ...
}
```

### `console.trace()`

Imprime la pila de llamadas en ese punto. Útil cuando una función se invoca desde donde no esperabas.

### `console.dir()`

Muestra un objeto con sus propiedades en formato inspeccionable, especialmente útil con elementos del DOM: `console.dir(document.body)`.

### Niveles: `warn`, `error`, `info`

Usar `console.error` y `console.warn` te permite filtrar por nivel en DevTools. Un detalle pequeño que ahorra mucho tiempo.

## 2. El depurador: tu mejor aliado

Si solo te quedas con una idea de este post, que sea esta: **aprende a usar breakpoints**.

Un breakpoint pausa la ejecución en una línea concreta. En ese momento puedes:

- Ver el valor de **todas** las variables en el ámbito actual.
- Recorrer el código paso a paso.
- Inspeccionar la pila de llamadas.
- Evaluar expresiones en la consola con el contexto real.

Y todo sin modificar una sola línea de código.

### Cómo empezar en el navegador

1. Abre DevTools (`F12`).
2. Ve a la pestaña **Sources** (o *Depurador* en Firefox).
3. Abre tu archivo y haz clic en el número de línea.
4. Recarga o dispara la acción.

Los controles básicos son:

- **Resume** (`F8`): continúa hasta el siguiente breakpoint.
- **Step over** (`F10`): ejecuta la línea sin entrar en funciones.
- **Step into** (`F11`): entra en la función llamada.
- **Step out** (`Shift+F11`): sale de la función actual.

### La palabra clave `debugger`

Si no quieres buscar el archivo, escribe esto en tu código:

```js
function calcularTotal(carrito) {
  debugger;
  return carrito.reduce((acc, item) => acc + item.precio, 0);
}
```

Con DevTools abierto, la ejecución se detendrá ahí. Eso sí, elimínalo antes de hacer commit.

### Breakpoints condicionales

Aquí es donde el depurador supera claramente a los logs. Imagina un bucle de 10.000 iteraciones que falla en la 7.342. Con `console.log` imprimirías 10.000 líneas. Con un breakpoint condicional (clic derecho sobre la línea → *Add conditional breakpoint*), escribes:

```js
i === 7342
```

y la ejecución se detiene justo ahí.

### Logpoints

Los logpoints son lo mejor de ambos mundos: imprimen un mensaje sin que modifiques el código. Clic derecho → *Add logpoint* y escribes la expresión, por ejemplo `"usuario:", usuario.id`. No hay nada que limpiar después, porque el logpoint vive en DevTools y no en tu archivo.

### Watch expressions y breakpoints de excepción

- **Watch**: añade expresiones que se reevalúan en cada pausa.
- **Pause on exceptions**: el depurador se detiene automáticamente cuando se lanza un error, mostrándote el estado exacto en que ocurrió.

## 3. Depurar en Node.js y en el editor

No necesitas un navegador para usar un depurador.

Con Node puedes lanzar:

```bash
node --inspect-brk app.js
```

Y conectarte desde `chrome://inspect`. Aun más cómodo es usar el depurador integrado de **VS Code**: crea un `launch.json` o simplemente usa el botón *JavaScript Debug Terminal* y ejecuta tu comando habitual. Los breakpoints funcionan directamente en el editor, con la misma experiencia que en el navegador.

Si trabajas con TypeScript, los *source maps* hacen que puedas depurar tu código `.ts` original, no el JavaScript compilado.

## 4. Otras pestañas de DevTools que merecen cariño

Muchos problemas no son de lógica, sino de red, rendimiento o memoria:

- **Network**: ¿la petición realmente se envió? ¿Qué cabeceras llevaba? ¿Qué respondió el servidor? Puedes incluso simular una conexión lenta o sin conexión.
- **Performance**: graba una sesión y descubre qué función bloquea el hilo principal.
- **Memory**: toma *heap snapshots* para localizar fugas de memoria.
- **Application**: inspecciona `localStorage`, cookies, IndexedDB y service workers.

Antes de llenar tu código de logs para averiguar por qué algo va lento, graba un perfil de rendimiento. Te dirá mucho más.

## 5. Logging estructurado para producción

En producción, `console.log("llegó aquí")` no sirve de nada. Necesitas logs que puedas **buscar, filtrar y correlacionar**.

Librerías como [pino](https://github.com/pinojs/pino) o [winston](https://github.com/winstonjs/winston) generan logs en JSON con niveles y metadatos:

```js
import pino from "pino";
const logger = pino();

logger.info({ userId: 42, accion: "login" }, "Usuario autenticado");
logger.error({ err, pedidoId: 981 }, "Fallo al procesar el pago");
```

Ventajas:

- **Niveles** configurables por entorno (`debug` en desarrollo, `info` en producción).
- **Formato consistente** que herramientas como Datadog, Grafana Loki o ELK pueden indexar.
- **Contexto** como ID de petición o de usuario, para seguir una operación completa.

## 6. Previene en lugar de depurar

El mejor bug es el que nunca llega a ejecutarse. Algunas herramientas que reducen la necesidad de depurar:

- **TypeScript**: detecta errores de tipos antes de ejecutar nada.
- **ESLint**: avisa de variables sin usar, comparaciones peligrosas y, si quieres, de `console.log` olvidados (regla `no-console`).
- **Tests automatizados**: un test que falla te dice qué se rompió y dónde, y se queda como red de seguridad. Con Vitest o Jest puedes incluso depurar un test concreto con breakpoints.
- **Validación en los límites**: librerías como Zod validan datos externos (APIs, formularios) en tiempo de ejecución, y los errores llegan con mensajes claros.

## ¿Cuándo usar cada herramienta?

| Situación | Herramienta recomendada |
|---|---|
| Comprobar rápidamente un valor | `console.log` / `console.table` |
| Entender el flujo de ejecución | Breakpoints y *step over/into* |
| Bug que ocurre en una iteración concreta | Breakpoint condicional |
| Quieres un log sin tocar el código | Logpoint |
| Algo va lento | Pestaña Performance |
| Petición que falla | Pestaña Network |
| Seguimiento en producción | Logging estructurado |
| Evitar regresiones | Tests y tipos |

## Conclusión

`console.log` no es el enemigo. Es una herramienta útil, y para comprobaciones rápidas seguirá siendo mi primera opción. El problema aparece cuando es la *única* que conoces: terminas perdiendo tiempo en tareas que otras herramientas resuelven en segundos.

Si quieres dar un paso concreto esta semana, te propongo este mini reto:

1. La próxima vez que vayas a escribir un `console.log`, pregúntate si un breakpoint serviría mejor.
2. Prueba un **logpoint** y un **breakpoint condicional**.
3. Sustituye un `console.log(array)` por `console.table(array)`.

Con esos tres hábitos ya notarás la diferencia.

¿Y tú? ¿Cuál es tu truco favorito de depuración que no sea `console.log`? Cuéntamelo en los comentarios. 👇
