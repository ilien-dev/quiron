# JavaScript y el DOM: `keydown` vs `keypress`

Los eventos de teclado permiten detectar cuándo una persona interactúa con una página mediante teclas. Son útiles para crear atajos, validar formularios, controlar juegos o mejorar la accesibilidad. Sin embargo, al comenzar a trabajar con ellos aparece una duda frecuente: ¿cuál es la diferencia entre `keydown` y `keypress`?

Aunque ambos eventos parecen similares, no se comportan igual. Además, uno de ellos ya no debería utilizarse en proyectos nuevos.

## El evento `keydown`

`keydown` se dispara en el momento en que una tecla es presionada. Funciona tanto con teclas que producen caracteres —como `A`, `7` o `?`— como con teclas de control, por ejemplo:

- `Escape`
- `Enter`
- `Shift`
- `Control`
- Flechas de dirección
- Teclas de función

Podemos escucharlo con `addEventListener`:

```javascript
document.addEventListener("keydown", (event) => {
  console.log(`Tecla presionada: ${event.key}`);
});
```

La propiedad `event.key` contiene el valor interpretado de la tecla. Por ejemplo, al presionar la tecla correspondiente a la letra A, puede devolver `"a"` o `"A"`, dependiendo de si `Shift` está activo.

Cuando interesa la posición física de la tecla, existe `event.code`:

```javascript
document.addEventListener("keydown", (event) => {
  console.log(event.key);  // "a"
  console.log(event.code); // "KeyA"
});
```

`event.code` resulta especialmente útil en videojuegos o controles que deben conservar la misma distribución física, sin depender del idioma del teclado.

Si una tecla permanece presionada, `keydown` puede ejecutarse repetidamente. La propiedad `event.repeat` permite detectar esta situación:

```javascript
document.addEventListener("keydown", (event) => {
  if (event.repeat) {
    console.log("La tecla sigue presionada");
  }
});
```

## ¿Qué ocurre con `keypress`?

`keypress` se diseñó para detectar teclas que generan caracteres. A diferencia de `keydown`, normalmente no respondía de forma consistente ante teclas como `Shift`, `Escape` o las flechas.

```javascript
document.addEventListener("keypress", (event) => {
  console.log(event.key);
});
```

El problema es que su comportamiento nunca fue completamente uniforme entre navegadores, teclados e idiomas. La entrada de texto moderna también puede involucrar métodos de composición, teclados virtuales o tecnologías de asistencia, escenarios que `keypress` no representa correctamente.

Por estas razones, `keypress` está obsoleto. Aunque todavía puede funcionar en algunos navegadores por compatibilidad con sitios antiguos, no debe usarse para desarrollar nuevas funcionalidades.

## Cómo sustituir `keypress`

Para detectar acciones del teclado, la alternativa habitual es `keydown`:

```javascript
const input = document.querySelector("#busqueda");

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    console.log("Iniciar búsqueda");
  }
});
```

Si el objetivo es reaccionar al contenido escrito en un campo, suele ser mejor escuchar el evento `input`. Este evento detecta cambios producidos mediante teclado, pegado de texto, dictado y otros mecanismos:

```javascript
input.addEventListener("input", (event) => {
  console.log(event.target.value);
});
```

Esta distinción es importante: `keydown` representa una acción física sobre el teclado, mientras que `input` representa un cambio en el valor del control.

## Cancelar el comportamiento predeterminado

Con `keydown` también podemos impedir una acción predeterminada mediante `preventDefault()`. Por ejemplo, para evitar el envío de un formulario al presionar `Enter`:

```javascript
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
  }
});
```

Esta técnica debe utilizarse con cuidado. Bloquear teclas esperadas puede perjudicar la navegación mediante teclado y afectar la accesibilidad.

## Conclusión

La recomendación actual es sencilla: utiliza `keydown` para detectar teclas y combinaciones, e `input` para observar cambios de texto. Evita `keypress`, ya que está obsoleto y presenta inconsistencias.

Elegir el evento adecuado no solo hace que el código sea más predecible, sino que también mejora su compatibilidad con diferentes navegadores, dispositivos y formas de interacción.