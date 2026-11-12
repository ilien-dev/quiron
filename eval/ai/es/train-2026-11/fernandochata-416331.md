Trabajar con fechas en JavaScript tiene fama de ser complicado, y con razón. Pero gran parte del dolor desaparece cuando conoces las herramientas que ya trae el lenguaje. En este post repasamos las formas más útiles de **formatear** fechas y horas sin instalar ninguna librería.

## El punto de partida: `Date`

Todo empieza con un objeto `Date`:

```js
const ahora = new Date();
console.log(ahora);
// 2026-11-12T10:30:00.000Z (según el entorno)
```

Internamente, un `Date` es solo un número: los milisegundos transcurridos desde el 1 de enero de 1970 en UTC. Lo que ves al imprimirlo es una *representación*, y ahí es donde entra el formateo.

## Los métodos básicos

`Date` incluye varios métodos que devuelven cadenas listas para usar:

```js
const fecha = new Date('2026-11-12T10:30:00Z');

fecha.toISOString();   // "2026-11-12T10:30:00.000Z"
fecha.toString();      // "Thu Nov 12 2026 11:30:00 GMT+0100 (hora estándar de Europa central)"
fecha.toDateString();  // "Thu Nov 12 2026"
fecha.toUTCString();   // "Thu, 12 Nov 2026 10:30:00 GMT"
```

De todos ellos, **`toISOString()`** es el que más vas a usar en la práctica: sigue el estándar ISO 8601, siempre está en UTC y es perfecto para guardar en bases de datos o enviar a una API. El resto dependen del entorno o no son muy amigables para el usuario.

## Formato local con `toLocaleDateString()` y `toLocaleTimeString()`

Para mostrar fechas a personas, lo ideal es respetar su idioma y sus convenciones:

```js
fecha.toLocaleDateString('es-ES'); // "12/11/2026"
fecha.toLocaleDateString('en-US'); // "11/12/2026"
fecha.toLocaleTimeString('es-ES'); // "11:30:00"
```

Fíjate en que el mismo día se escribe distinto en España y en Estados Unidos. Por eso nunca deberías construir fechas "a mano" concatenando `getDate()`, `getMonth()` y `getFullYear()` si van a verlas usuarios de distintos países.

Estos métodos aceptan un segundo argumento con opciones:

```js
fecha.toLocaleDateString('es-ES', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});
// "jueves, 12 de noviembre de 2026"
```

## `Intl.DateTimeFormat`: la herramienta potente

Si vas a formatear muchas fechas con la misma configuración, crea un formateador reutilizable. Es más eficiente que llamar a `toLocaleDateString()` una y otra vez:

```js
const formateador = new Intl.DateTimeFormat('es-MX', {
  dateStyle: 'full',
  timeStyle: 'short',
  timeZone: 'America/Mexico_City',
});

formateador.format(fecha);
// "jueves, 12 de noviembre de 2026, 4:30"
```

Las opciones `dateStyle` y `timeStyle` (`full`, `long`, `medium`, `short`) son un atajo muy cómodo. Y `timeZone` te permite mostrar la hora en cualquier zona horaria sin cálculos manuales.

¿Necesitas piezas sueltas para construir tu propio diseño? Usa `formatToParts()`:

```js
formateador.formatToParts(fecha);
// [{ type: 'weekday', value: 'jueves' }, { type: 'literal', value: ', ' }, ...]
```

## Tiempos relativos con `Intl.RelativeTimeFormat`

Para textos como "hace 3 días" o "dentro de 2 horas":

```js
const rtf = new Intl.RelativeTimeFormat('es', { numeric: 'auto' });

rtf.format(-1, 'day');  // "ayer"
rtf.format(-3, 'day');  // "hace 3 días"
rtf.format(2, 'hour');  // "dentro de 2 horas"
```

La opción `numeric: 'auto'` es la que convierte "hace 1 día" en "ayer". Un detalle pequeño que mejora mucho la experiencia.

## Errores comunes

- **Los meses empiezan en 0.** `new Date(2026, 0, 1)` es el 1 de enero, no de febrero.
- **Parsear cadenas ambiguas.** `new Date('12/11/2026')` puede interpretarse de forma distinta según el entorno. Usa siempre ISO 8601 (`'2026-11-12'`).
- **Olvidar la zona horaria.** `'2026-11-12'` se interpreta en UTC, pero `'2026-11-12T10:00'` en hora local. Esta inconsistencia causa más de un bug.

## Un vistazo al futuro: Temporal

La propuesta **Temporal** llega para sustituir a `Date` con una API inmutable, tipos separados para fechas, horas y zonas horarias, y mucho menos margen de error. Ya está disponible en varios navegadores modernos, así que revisa el soporte en tu entorno objetivo antes de usarla en producción (o tira de un polyfill).

```js
Temporal.Now.plainDateISO().toLocaleString('es-ES');
```

## Conclusión

- Para **guardar o transmitir** fechas: `toISOString()`.
- Para **mostrarlas** a usuarios: `Intl.DateTimeFormat` o `toLocaleDateString()`.
- Para **tiempos relativos**: `Intl.RelativeTimeFormat`.

Con estas tres ideas cubres la gran mayoría de casos sin añadir dependencias. ¿Qué otros problemas con fechas te has encontrado? ¡Cuéntamelo en los comentarios! 👇

---

Lo dejé con `published: false` en el front matter para que puedas revisarlo antes de publicarlo. Ten en cuenta que los ejemplos de salida de `toString()` y `toLocaleTimeString()` dependen de la zona horaria del entorno. ¿Quieres que lo guarde como archivo `.md`?
