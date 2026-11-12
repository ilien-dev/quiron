# JavaScript y el DOM: keyDown vs keyPress

Cuando construimos una interfaz interactiva, escuchar el teclado puede ser tan útil como escuchar clics. Tal vez quieras cerrar una ventana con Escape, detectar las flechas en un juego o reaccionar a lo que alguien escribe en un formulario.

Al buscar ejemplos, es común encontrar dos eventos: `keydown` y `keypress`. Aunque sus nombres se parecen, tienen diferencias importantes. Además, uno de ellos ya no se recomienda para proyectos nuevos.

> **Un detalle de sintaxis:** los nombres de los eventos del DOM se escriben en minúsculas: `keydown` y `keypress`.

## ¿Qué hace `keydown`?

El evento `keydown` se dispara cuando se presiona una tecla. Funciona tanto para teclas que producen caracteres, como `a` o `5`, como para otras que no lo hacen, como Escape, Shift o las flechas.

Por ejemplo, podemos detectar cuándo alguien pulsa Escape:

```js
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    console.log("Pulsaste Escape");
  }
});
```

La propiedad `event.key` describe el valor de la tecla teniendo en cuenta factores como la distribución del teclado y las teclas modificadoras. Por ejemplo, puede devolver `"a"`, `"A"`, `"Enter"` o `"ArrowLeft"`.

`keydown` es una buena opción para atajos y controles de interfaz. Si necesitas detectar cuándo se *suelta* una tecla, existe el evento `keyup`.

## ¿Y qué pasa con `keypress`?

Históricamente, `keypress` se utilizaba para detectar teclas que producen caracteres. Por ejemplo, suele dispararse al escribir una letra o un número, pero no al pulsar Shift por sí sola. También puede dispararse con Enter.

La diferencia más importante hoy es que **`keypress` está obsoleto**. Todavía puedes encontrarlo en aplicaciones existentes, pero [MDN recomienda usar `keydown` o `beforeinput` en su lugar](https://developer.mozilla.org/en-US/docs/Web/API/Element/keypress_event).

Esto no significa que debas reemplazar automáticamente cada `keypress` por `keydown`. Primero conviene entender qué intenta hacer el código: ¿responder a una tecla o detectar un cambio en el texto? La respuesta determina qué evento usar.

## Si te interesa el texto, usa `input`

Un campo puede cambiar sin que el usuario escriba una tecla: también puede pegar texto, usar el dictado o seleccionar una sugerencia del teclado. Para reaccionar al valor después de que cambia, escucha `input`:

```html
<label for="nombre">Nombre</label>
<input id="nombre" type="text">
<p id="saludo"></p>
```

```js
const nombre = document.querySelector("#nombre");
const saludo = document.querySelector("#saludo");

nombre.addEventListener("input", () => {
  saludo.textContent = `Hola, ${nombre.value}`;
});
```

Así, el saludo se actualiza cuando cambia el contenido, incluso si el texto llega mediante una acción de pegado.

Si necesitas intervenir *antes* de una modificación editable, investiga `beforeinput`. Sus detalles de cancelación y compatibilidad dependen del tipo de edición, así que conviene probar el caso concreto.

## `key` o `code`: ¿cuál elijo?

Además de `event.key`, existe `event.code`:

- **`event.key`** representa el valor de la tecla, como `"a"` o `"Escape"`.
- **`event.code`** representa una posición física del teclado, como `"KeyA"`.

Para un atajo que dependa de una letra, normalmente querrás `key`. Para controles de un juego basados en posiciones físicas, `code` puede resultar más adecuado, aunque debes considerar las distintas distribuciones y ofrecer controles configurables.

También puedes consultar `event.repeat` para saber si un `keydown` se está repitiendo porque la tecla sigue presionada:

```js
document.addEventListener("keydown", (event) => {
  if (event.key === " " && !event.repeat) {
    console.log("Se pulsó la barra espaciadora");
  }
});
```

## Un cuidado con la escritura internacional

Algunos usuarios escriben mediante editores de métodos de entrada, o IME, que permiten componer caracteres en varios pasos. Si un atajo puede interferir con esa escritura, revisa `event.isComposing` antes de ejecutarlo. Para manejar también casos límite al inicio o al final de la composición, consulta la [guía de `keydown` de MDN](https://developer.mozilla.org/en-US/docs/Web/API/Element/keydown_event#keydown_events_with_ime).

La elección práctica queda así: usa `keydown` para responder a teclas, `input` para observar cambios en el texto y deja `keypress` para entender o mantener código antiguo. Elegir el evento según la intención hará que tus interfaces sean más claras y funcionen mejor para más usuarios.
