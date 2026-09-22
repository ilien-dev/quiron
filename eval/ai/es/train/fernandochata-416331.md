# Formatos de fechas y horas en JavaScript

Trabajar con fechas en JavaScript tiene fama de ser complicado, y no sin razón. Pero cuando se trata de **mostrarlas** en un formato legible, el lenguaje incluye herramientas muy potentes que mucha gente no conoce. En este post vamos a ver las formas más útiles de formatear fechas y horas sin instalar ninguna librería.

## El objeto Date

Todo empieza con el objeto `Date`:

```javascript
const ahora = new Date();
const fecha = new Date(2024, 2, 15, 14, 30); // 15 de marzo de 2024, 14:30
```

Ojo con un detalle clásico: **los meses empiezan en 0**. Enero es 0 y diciembre es 11.

## Los métodos básicos

`Date` tiene varios métodos que devuelven la fecha en distintos formatos:

```javascript
fecha.toString();      // "Fri Mar 15 2024 14:30:00 GMT+0100 (hora estándar de Europa central)"
fecha.toDateString();  // "Fri Mar 15 2024"
fecha.toTimeString();  // "14:30:00 GMT+0100 ..."
fecha.toISOString();   // "2024-03-15T13:30:00.000Z"
```

`toISOString()` es especialmente útil para enviar fechas a una API o guardarlas en una base de datos, ya que usa el estándar ISO 8601 y siempre está en UTC.

## toLocaleDateString y toLocaleTimeString

Para mostrar fechas al usuario, lo ideal es usar los métodos `toLocale...`, que respetan el idioma y la región:

```javascript
fecha.toLocaleDateString('es-ES');  // "15/3/2024"
fecha.toLocaleDateString('en-US');  // "3/15/2024"
fecha.toLocaleTimeString('es-ES');  // "14:30:00"
fecha.toLocaleString('es-MX');      // "15/3/2024, 14:30:00"
```

Y lo mejor es que aceptan un objeto de opciones para personalizar el resultado:

```javascript
fecha.toLocaleDateString('es-ES', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});
// "viernes, 15 de marzo de 2024"

fecha.toLocaleTimeString('es-ES', {
  hour: '2-digit',
  minute: '2-digit',
});
// "14:30"

fecha.toLocaleTimeString('en-US', {
  hour: 'numeric',
  minute: '2-digit',
  hour12: true,
});
// "2:30 PM"
```

Las opciones más comunes son:

| Opción | Valores |
|---|---|
| `weekday` | `'long'`, `'short'`, `'narrow'` |
| `year` | `'numeric'`, `'2-digit'` |
| `month` | `'numeric'`, `'2-digit'`, `'long'`, `'short'` |
| `day` | `'numeric'`, `'2-digit'` |
| `hour`, `minute`, `second` | `'numeric'`, `'2-digit'` |
| `timeZone` | `'America/Bogota'`, `'Europe/Madrid'`, `'UTC'`... |

## Intl.DateTimeFormat

Si vas a formatear muchas fechas con el mismo formato, es más eficiente crear un formateador una sola vez con `Intl.DateTimeFormat`:

```javascript
const formateador = new Intl.DateTimeFormat('es-AR', {
  dateStyle: 'full',
  timeStyle: 'short',
  timeZone: 'America/Argentina/Buenos_Aires',
});

formateador.format(fecha);
// "viernes, 15 de marzo de 2024, 10:30"
```

`dateStyle` y `timeStyle` aceptan `'full'`, `'long'`, `'medium'` y `'short'`, y son un atajo muy cómodo.

## Formato personalizado a mano

A veces necesitas un formato exacto, como `AAAA-MM-DD`. Puedes construirlo con `padStart`:

```javascript
const pad = (n) => String(n).padStart(2, '0');

const formatear = (d) =>
  `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

formatear(fecha); // "2024-03-15"
```

## Fechas relativas

Para textos como "hace 3 días", existe `Intl.RelativeTimeFormat`:

```javascript
const rtf = new Intl.RelativeTimeFormat('es', { numeric: 'auto' });

rtf.format(-1, 'day');   // "ayer"
rtf.format(-3, 'day');   // "hace 3 días"
rtf.format(2, 'week');   // "dentro de 2 semanas"
```

## Conclusión

Antes de instalar una librería para formatear fechas, prueba con `toLocaleDateString`, `Intl.DateTimeFormat` e `Intl.RelativeTimeFormat`. Cubren la gran mayoría de casos, respetan el idioma del usuario y no añaden ni un byte a tu bundle.
