# JavaScript y el DOM: keyDown vs keyPress

Estás programando un buscador y quieres ejecutar una acción cuando alguien presione Enter. Encuentras ejemplos con `keydown`, otros con `keypress` y una duda bastante razonable: ¿hacen lo mismo?

Aunque ambos están relacionados con el teclado, representan comportamientos diferentes. Además, `keypress` está obsoleto: para código nuevo, conviene elegir el evento según la acción que necesitas detectar. [MDN explica su estado y las alternativas](https://developer.mozilla.org/en-US/docs/Web/API/Element/keypress_event).

Primero, un detalle: aunque el título utiliza “keyDown” y “keyPress”, los nombres que pasamos a `addEventListener` se escriben completamente en minúsculas.

**¿Qué detecta `keydown`?**

El evento `keydown` se dispara cuando presionas una tecla, produzca o no un carácter. Permite responder a letras, números, flechas, Escape, Shift o Tab. Por eso resulta útil para atajos y controles de interfaz. [Documentación de `keydown`](https://developer.mozilla.org/en-US/docs/Web/API/Element/keydown_event).

Puedes probarlo directamente en la consola del navegador:

```javascript
document.addEventListener("keydown", (event) => {
  console.log("Tecla:", event.key);
});
```

El listener está registrado en `document`, así que puede recibir eventos que se propagan desde el elemento enfocado. Si tu comportamiento pertenece únicamente a un campo, registra el listener en ese campo para limitar su alcance.

**¿Qué hacía `keypress`?**

Históricamente, `keypress` se utilizaba principalmente para teclas que producían caracteres y también para Enter. No ofrecía el mismo comportamiento para teclas de control, como las flechas o los modificadores.

Eso explica por qué algunos ejemplos antiguos funcionan al escribir una letra, pero fallan cuando intentas detectar otra tecla. Su nombre puede sugerir que captura cualquier pulsación; esa interpretación suele causar errores.

Si encuentras este patrón:

```javascript
campo.addEventListener("keypress", manejarTecla);
```

Revisa qué intenta conseguir antes de sustituirlo. Un atajo puede requerir `keydown`; observar el contenido escrito suele requerir `input`. Migrar implica revisar la intención del código, además del nombre del evento.

**Un ejemplo práctico con Escape**

Supongamos que quieres vaciar un buscador al presionar Escape. Coloca este ejemplo en un documento HTML y abre la página:

```html
<label for="buscador">Buscar artículos</label>
<input id="buscador" type="search">

<script>
  const buscador = document.querySelector("#buscador");

  buscador.addEventListener("keydown", (event) => {
    if (event.isComposing) return;

    if (event.key === "Escape") {
      event.preventDefault();
      buscador.value = "";
    }
  });
</script>
```

Aquí comprobamos una tecla concreta y cancelamos su comportamiento predeterminado porque definimos una acción propia. Evita cancelar indiscriminadamente todas las pulsaciones: podrías impedir la escritura o la navegación con teclado.

La comprobación de `isComposing` evita ejecutar esta acción mientras hay una sesión de composición activa, utilizada por ciertos métodos de entrada. Conviene considerar estos métodos cuando una interfaz responde al teclado. [Referencia de `KeyboardEvent`](https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent).

**`key`, `code` y las pulsaciones repetidas**

`event.key` expresa el valor de la tecla teniendo en cuenta modificadores y distribución del teclado. Una letra puede llegar como `"a"` o `"A"`.

`event.code` identifica la posición física mediante valores como `"KeyA"`. Puede servir para controles basados en posiciones, pero no debes asumir que coincide con el carácter impreso en cualquier teclado.

Si mantienes una tecla presionada, puedes recibir varios eventos `keydown`. La propiedad `event.repeat` permite reconocer la repetición automática. Para una acción que deba ejecutarse una sola vez por pulsación, puedes ignorar los eventos donde sea verdadera. [Propiedades de los eventos de teclado](https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent).

**Para leer texto, escucha `input`**

Detectar teclas y detectar cambios de contenido son necesidades distintas. Un usuario también puede pegar texto, dictarlo o introducirlo mediante otras herramientas.

Para actualizar resultados mientras cambia un campo:

```javascript
buscador.addEventListener("input", (event) => {
  console.log("Contenido actual:", event.target.value);
});
```

`input` permite observar el cambio producido por el usuario. `beforeinput` puede servir cuando necesitas intervenir antes de determinadas ediciones, aunque debes revisar su comportamiento para tu caso. [MDN recomienda distinguir la entrada de texto de los eventos de teclado](https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent).

La próxima vez que implementes una interacción, empieza por describirla: “responder a Escape”, “observar el texto” o “detectar una posición física”. Esa pequeña decisión te ayudará a elegir el evento y la propiedad adecuados.
