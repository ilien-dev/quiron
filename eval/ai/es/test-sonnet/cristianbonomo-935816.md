# No todo es console.log()

Si le preguntas a cualquier desarrollador JavaScript cómo depura su código, es muy probable que la primera respuesta sea "con `console.log()`". Y no hay nada de malo en eso: es rápido, no requiere configuración y funciona en cualquier entorno. Pero el objeto `console` del navegador (y de Node.js) ofrece muchas más herramientas que la mayoría de desarrolladores nunca llega a usar. En este post vamos a repasar algunas de ellas.

## console.table()

Cuando trabajamos con arrays de objetos, imprimir cada uno con `console.log` puede volverse ilegible rápidamente. `console.table()` los muestra en formato de tabla, con columnas para cada propiedad:

```js
const usuarios = [
  { id: 1, nombre: 'Ana', edad: 28 },
  { id: 2, nombre: 'Luis', edad: 34 },
  { id: 3, nombre: 'Marta', edad: 25 }
];

console.table(usuarios);
```

Esto genera una tabla perfectamente legible en las DevTools, con una columna por cada propiedad y una fila por cada elemento del array. Incluso se puede pasar un segundo argumento con un array de nombres de columnas para filtrar cuáles mostrar.

## console.group() y console.groupEnd()

Cuando tenemos múltiples `console.log` relacionados entre sí, agruparlos visualmente ayuda mucho a la legibilidad:

```js
console.group('Validación de formulario');
console.log('Nombre: válido');
console.log('Email: inválido');
console.log('Contraseña: válida');
console.groupEnd();
```

En consola, esto se muestra como un bloque colapsable con el título "Validación de formulario", dentro del cual aparecen los tres logs indentados. También existe `console.groupCollapsed()`, que hace lo mismo pero empieza colapsado por defecto, ideal para logs muy extensos que no queremos ver a menos que sea necesario.

## console.time() y console.timeEnd()

Para medir cuánto tarda en ejecutarse un bloque de código, no hace falta instalar ninguna librería de profiling ni calcular manualmente diferencias de timestamps:

```js
console.time('procesamiento');

for (let i = 0; i < 1000000; i++) {
  Math.sqrt(i);
}

console.timeEnd('procesamiento');
// procesamiento: 12.34ms
```

Se pueden tener múltiples temporizadores activos a la vez, cada uno identificado por su propia etiqueta (el string que se pasa como argumento).

## console.count()

Útil para saber cuántas veces se ejecuta una determinada línea de código, sin necesidad de declarar una variable contador manualmente:

```js
function manejarClick() {
  console.count('click en botón');
}
```

Cada vez que se llame a `manejarClick`, se imprimirá algo como `click en botón: 1`, `click en botón: 2`, etc.

## console.trace()

Cuando queremos saber desde dónde se llamó a una función —especialmente útil en código con muchas capas de abstracción o callbacks anidados—, `console.trace()` imprime la pila de llamadas completa:

```js
function a() { b(); }
function b() { c(); }
function c() { console.trace('llegué hasta aquí'); }

a();
```

Esto es mucho más informativo que intentar reconstruir manualmente la cadena de llamadas con logs dispersos por el código.

## console.assert()

Permite imprimir un mensaje de error únicamente si una condición es falsa, lo cual es útil para validaciones rápidas durante el desarrollo:

```js
const edad = -5;
console.assert(edad >= 0, 'La edad no puede ser negativa', { edad });
```

Si la condición es verdadera, no se imprime nada. Esto evita tener que envolver el log en un `if` manualmente.

## Estilos con %c

Se puede dar formato con CSS a los mensajes de consola usando el especificador `%c`:

```js
console.log('%cAtención', 'color: red; font-size: 20px; font-weight: bold;');
```

Aunque parezca un truco cosmético sin mucha utilidad, en proyectos grandes con muchos logs, poder resaltar visualmente ciertos mensajes (errores críticos, warnings de negocio, etc.) ayuda mucho a encontrarlos rápidamente entre el ruido.

## El objeto debugger

Más allá del objeto `console`, la palabra clave `debugger` es una herramienta que muchos desarrolladores subestiman:

```js
function calcularTotal(items) {
  debugger;
  return items.reduce((acc, item) => acc + item.precio, 0);
}
```

Cuando el navegador (con las DevTools abiertas) encuentra esta línea, pausa la ejecución exactamente ahí, permitiendo inspeccionar el estado de todas las variables, avanzar línea por línea, entrar y salir de funciones, y evaluar expresiones en el contexto actual. Es mucho más potente que ir añadiendo y quitando `console.log` a mano, porque no hay que modificar el código para cada nueva hipótesis que queramos probar: basta con ir explorando el estado en vivo.

## Breakpoints condicionales

Directamente desde las DevTools (sin tocar el código fuente), se pueden añadir breakpoints condicionales haciendo click derecho sobre el número de línea en la pestaña "Sources". Esto permite pausar la ejecución solo cuando se cumple una condición específica, por ejemplo `item.id === 42`, lo cual es extremadamente útil cuando un bug solo ocurre para un caso particular dentro de un bucle con miles de iteraciones.

## console.error() y console.warn()

Aunque parezcan simples variantes de `console.log`, tienen un propósito semántico importante: `console.error` imprime en rojo y suele incluir el stack trace automáticamente, mientras que `console.warn` lo hace en amarillo. Usarlos correctamente (en vez de todo con `console.log`) facilita filtrar por nivel de severidad directamente desde las DevTools, algo que la mayoría de navegadores permite hacer con un simple checkbox.

## Conclusión

`console.log()` seguirá siendo, con toda seguridad, la herramienta de depuración más usada por la comunidad JavaScript, y no pasa nada por eso: para depuraciones rápidas y puntuales sigue siendo la opción más práctica. Pero conocer el resto de herramientas disponibles —tablas, agrupaciones, temporizadores, trazas, breakpoints condicionales— puede ahorrar muchísimo tiempo en sesiones de debugging más complejas, donde simplemente ir imprimiendo variables ya no es suficiente. La próxima vez que te encuentres depurando un bug difícil de rastrear, antes de llenar el código de `console.log`, prueba alguna de estas alternativas: puede que te sorprenda cuánto simplifican el proceso.
