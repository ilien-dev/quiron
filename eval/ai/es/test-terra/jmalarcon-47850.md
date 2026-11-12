# Copiado de texto al portapapeles con JavaScript - API Asíncrona

¿Cuántas veces has encontrado un botón para copiar un enlace, un código de descuento o un fragmento de código? Es una pequeña función que ahorra varios pasos: seleccionar el texto, abrir el menú contextual y elegir «Copiar».

Con JavaScript podemos implementarla mediante la **API asíncrona del portapapeles**, conocida como *Async Clipboard API*. En este artículo veremos cómo copiar texto, informar al usuario del resultado y manejar los casos en los que el navegador no permita completar la operación.

## ¿Qué es la API del portapapeles?

La Clipboard API permite interactuar con el portapapeles del sistema desde una aplicación web. Para copiar texto plano, el punto de entrada es:

```js
navigator.clipboard.writeText(texto);
```

El método `writeText()` recibe una cadena y devuelve una **promesa**. Esta se resuelve cuando el texto se ha escrito en el portapapeles o se rechaza si la operación falla.

Eso significa que no basta con llamar al método y asumir que todo salió bien: debemos esperar el resultado antes de mostrar un mensaje de éxito.

```js
navigator.clipboard.writeText("¡Hola, mundo!")
  .then(() => {
    console.log("Texto copiado");
  })
  .catch((error) => {
    console.error("No se pudo copiar:", error);
  });
```

También podemos utilizar `async` y `await`, una opción cómoda cuando queremos manejar el flujo con `try...catch`.

```js
async function copiarTexto(texto) {
  try {
    await navigator.clipboard.writeText(texto);
    console.log("Texto copiado");
  } catch (error) {
    console.error("No se pudo copiar:", error);
  }
}
```

Antes de construir un ejemplo completo, conviene conocer las condiciones que establece el navegador para acceder al portapapeles.

## Requisitos para usar `writeText()`

### Un contexto seguro

La API está disponible en **contextos seguros**, normalmente páginas servidas mediante HTTPS. Para desarrollo local, los navegadores suelen considerar `localhost` un contexto seguro, incluso cuando se usa HTTP.

Si abres tu aplicación desde una dirección HTTP que no se considere segura, es posible que `navigator.clipboard` no esté disponible. Por ejemplo, una dirección de red local como `http://192.168.1.20` no debe asumirse equivalente a `localhost`.

Puedes consultar si la página se encuentra en un contexto seguro con:

```js
console.log(window.isSecureContext);
```

Si el resultado es `false`, revisa cómo estás sirviendo la página. La documentación de [MDN sobre `writeText()`](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText) explica este requisito.

### Una acción del usuario

Los navegadores aplican restricciones para evitar que una página modifique el portapapeles sin que la persona lo espere. Los detalles de permisos y activación varían entre navegadores, pero una práctica compatible es iniciar la copia directamente como respuesta a una acción del usuario, como pulsar un botón.

Evita depender de que la copia funcione automáticamente al cargar la página o después de una espera prolongada. Además, aunque el usuario haya pulsado un botón, la operación todavía puede fallar; por eso necesitamos manejar el rechazo de la promesa.

La [documentación de seguridad de la Clipboard API](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API#security_considerations) describe las diferencias entre navegadores.

## Ejemplo completo: copiar el contenido de un campo

Vamos a crear una página sencilla con un campo de texto, un botón y un mensaje que indique si la copia se realizó correctamente.

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Copiar texto al portapapeles</title>
</head>
<body>
  <h1>Copiar texto con JavaScript</h1>

  <label for="texto">Texto para copiar:</label>
  <textarea id="texto" rows="4" cols="40">¡Hola desde la Clipboard API!</textarea>

  <button id="copiar" type="button">Copiar texto</button>

  <p id="mensaje" role="status"></p>

  <script>
    const campo = document.querySelector("#texto");
    const boton = document.querySelector("#copiar");
    const mensaje = document.querySelector("#mensaje");

    boton.addEventListener("click", async () => {
      mensaje.textContent = "";

      if (!navigator.clipboard?.writeText) {
        mensaje.textContent =
          "La copia automática no está disponible. Selecciona el texto y cópialo manualmente.";
        return;
      }

      try {
        await navigator.clipboard.writeText(campo.value);
        mensaje.textContent = "¡Texto copiado al portapapeles!";
      } catch (error) {
        console.error("Error al copiar:", error);
        mensaje.textContent =
          "No se pudo copiar. Selecciona el texto y cópialo manualmente.";
      }
    });
  </script>
</body>
</html>
```

Guarda el archivo y sírvelo desde `localhost` o HTTPS. Después, escribe algo en el campo, pulsa el botón e intenta pegar el resultado en otra aplicación.

### ¿Qué ocurre en el código?

Primero obtenemos las referencias al campo, el botón y el elemento que mostrará el resultado:

```js
const campo = document.querySelector("#texto");
const boton = document.querySelector("#copiar");
const mensaje = document.querySelector("#mensaje");
```

Después escuchamos el evento `click`. La función es `async` porque usaremos `await` para esperar a que finalice la copia:

```js
boton.addEventListener("click", async () => {
  // Aquí intentamos copiar el texto.
});
```

Antes de llamar al método, comprobamos si está disponible:

```js
if (!navigator.clipboard?.writeText) {
  // Mostrar una alternativa.
}
```

El operador `?.` evita intentar acceder a `writeText` si `navigator.clipboard` no existe. Esta comprobación detecta la ausencia de la API, pero **no garantiza que la copia vaya a funcionar**: el navegador podría bloquearla por permisos u otras restricciones.

Por último, `await` espera el resultado de `writeText()`. Solo mostramos el mensaje de éxito después de que la promesa se resuelva. Si se rechaza, `catch` muestra una alternativa.

El atributo `role="status"` ayuda a que los cambios en el mensaje puedan anunciarse mediante tecnologías de asistencia. También mantenemos el texto en un campo visible y seleccionable, de modo que siga siendo posible copiarlo manualmente.

## Copiar texto que no está en un formulario

No siempre queremos copiar lo que hay dentro de un `textarea`. A veces el contenido está en un elemento como un párrafo, un bloque de código o una tarjeta.

En esos casos podemos leer su propiedad `textContent`:

```html
<pre><code id="comando">npm install mi-paquete</code></pre>
<button id="copiar-comando" type="button">Copiar comando</button>
<p id="resultado-comando" role="status"></p>
```

```js
const comando = document.querySelector("#comando");
const botonComando = document.querySelector("#copiar-comando");
const resultado = document.querySelector("#resultado-comando");

botonComando.addEventListener("click", async () => {
  resultado.textContent = "";

  if (!navigator.clipboard?.writeText) {
    resultado.textContent =
      "Selecciona el comando y cópialo manualmente.";
    return;
  }

  try {
    await navigator.clipboard.writeText(comando.textContent);
    resultado.textContent = "Comando copiado.";
  } catch (error) {
    console.error("Error al copiar el comando:", error);
    resultado.textContent =
      "No se pudo copiar. Selecciona el comando y cópialo manualmente.";
  }
});
```

`textContent` devuelve el contenido de texto del elemento, incluidos sus espacios y saltos de línea. Eso resulta útil para bloques de código en los que el formato importa.

Si prefieres eliminar espacios al principio y al final, puedes usar `comando.textContent.trim()`. Hazlo solo cuando esos espacios no formen parte del contenido que se espera copiar.

Una diferencia importante: `textContent` obtiene texto, no conserva etiquetas HTML como formato enriquecido. Para copiar otros tipos de contenido existe `navigator.clipboard.write()`, aunque requiere un tratamiento distinto y su compatibilidad depende del formato.

## Una función reutilizable

Si tienes varios botones de copia, puedes extraer la operación a una función. Una opción es hacer que devuelva `true` cuando la escritura se complete y `false` cuando no esté disponible o falle:

```js
async function copiarAlPortapapeles(texto) {
  if (!navigator.clipboard?.writeText) {
    return false;
  }

  try {
    await navigator.clipboard.writeText(texto);
    return true;
  } catch (error) {
    console.error("No se pudo escribir en el portapapeles:", error);
    return false;
  }
}
```

Ahora cada botón puede decidir qué mensaje mostrar:

```js
boton.addEventListener("click", async () => {
  const copiado = await copiarAlPortapapeles(campo.value);

  mensaje.textContent = copiado
    ? "¡Texto copiado!"
    : "No se pudo copiar. Selecciona el texto y cópialo manualmente.";
});
```

La función devuelve el resultado de la operación y deja que la interfaz se encargue de comunicarlo. Si necesitas distinguir entre distintos errores, puedes adaptar la función para devolver información adicional o dejar que la excepción llegue al código que la llama.

## ¿Qué pasa con los permisos?

Es tentador consultar primero `clipboard-write` mediante la Permissions API y asumir que esa respuesta predice el resultado. Sin embargo, los navegadores no implementan todos los permisos y restricciones del portapapeles de la misma manera.

Para un botón de copia, una estrategia práctica es:

1. Comprobar que `navigator.clipboard.writeText` existe.
2. Invocarlo directamente en respuesta a la acción del usuario.
3. Esperar la promesa y manejar tanto el éxito como el error.

Entre los errores posibles está `NotAllowedError`, que indica que la escritura no fue permitida en ese contexto. La causa concreta puede depender del navegador, sus permisos o las políticas aplicadas a la página.

Si la aplicación se muestra dentro de un `iframe`, también pueden intervenir las políticas de permisos de la página que lo contiene. Si el ejemplo funciona fuera del marco pero falla dentro, revisa esa configuración y la documentación del navegador.

## ¿Y `document.execCommand("copy")`?

Quizá encuentres tutoriales antiguos que crean un campo temporal, seleccionan su contenido y ejecutan:

```js
document.execCommand("copy");
```

Ese método está **obsoleto**. Aunque todavía puede aparecer en proyectos existentes, la Clipboard API es la opción moderna para nuevas implementaciones. Si tu proyecto necesita admitir navegadores antiguos, evalúa cuidadosamente sus requisitos y prueba cualquier alternativa en los entornos que debas soportar. Puedes consultar la [referencia de `execCommand()` en MDN](https://developer.mozilla.org/en-US/docs/Web/API/Document/execCommand).

Para muchos proyectos, mantener el contenido visible y seleccionable ya ofrece una salida sencilla cuando la copia automática no está disponible.

## Consejos para una buena experiencia

Un botón de copiar parece una función pequeña, pero algunos detalles marcan la diferencia:

- **Indica qué se va a copiar.** «Copiar enlace» o «Copiar comando» suele ser más claro que un botón con solo un icono.
- **Confirma el resultado.** Muestra «Copiado» únicamente después de que la promesa se resuelva.
- **Explica cómo continuar si falla.** Deja el contenido seleccionable e invita a copiarlo manualmente.
- **Prueba con teclado y lector de pantalla.** Usa un botón HTML y comunica el estado con texto.
- **Prueba el entorno real.** Revisa la función en HTTPS, en los navegadores que soporta tu aplicación y, si corresponde, dentro del `iframe` donde se publicará.

Copiar texto con JavaScript puede reducirse a una sola llamada a `navigator.clipboard.writeText()`. La parte que convierte esa llamada en una función fiable es esperar su resultado y ofrecer una respuesta clara en ambos casos: cuando el texto llega al portapapeles y cuando el navegador no permite copiarlo.
