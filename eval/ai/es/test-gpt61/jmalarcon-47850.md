# Copiado de texto al portapapeles con JavaScript - API Asíncrona

Copiar un enlace, un comando o un código de descuento debería tomar un solo clic. Es una interacción pequeña, pero muy útil: evita seleccionar texto a mano y reduce los errores al llevar información de una aplicación a otra.

Con JavaScript podemos implementar esta funcionalidad mediante la **API asíncrona del portapapeles**, también conocida como *Async Clipboard API*. Para copiar texto, su pieza central es `navigator.clipboard.writeText()`.

En este artículo construiremos un botón de copiado, entenderemos cómo manejar su resultado y revisaremos los detalles que suelen causar problemas al pasar del ejemplo a una aplicación real.

## El punto de partida: `writeText()`

La instrucción básica es esta:

```javascript
await navigator.clipboard.writeText("¡Hola desde JavaScript!");
```

`writeText()` recibe una cadena y devuelve una promesa. Esta se resuelve cuando el portapapeles se ha actualizado; si la operación no está permitida, puede rechazarse con un error. Su valor de resolución no contiene el texto copiado. Puedes consultar su definición en la [especificación de Clipboard API](https://www.w3.org/TR/clipboard-apis/#dom-clipboard-writetext).

Esto nos permite expresar el flujo con claridad:

1. Solicitar que se copie el texto.
2. Esperar el resultado.
3. Informar si la operación terminó correctamente.

El tercer paso debe ocurrir después del segundo. Mostrar “¡Copiado!” inmediatamente después de llamar al método, sin esperar su promesa, puede comunicar un éxito que nunca ocurrió.

## ¿Por qué una API asíncrona?

Una operación asíncrona permite continuar con otras tareas mientras esperamos su resultado. En nuestro código, `await` suspende la ejecución de la función `async` que lo contiene hasta que la promesa se resuelva o rechace.

No congela toda la página.

Este modelo también facilita organizar el tratamiento de errores mediante `try...catch`:

```javascript
async function copiarTexto(texto) {
  try {
    await navigator.clipboard.writeText(texto);
    console.log("Texto copiado");
  } catch (error) {
    console.error("No se pudo copiar:", error);
  }
}
```

La función resulta útil para comprender la operación, pero todavía necesitamos conectarla con una acción de la persona que utiliza la página.

## Antes de empezar: contexto seguro

El acceso al portapapeles está restringido a contextos seguros. Para una página publicada, utiliza HTTPS. Durante el desarrollo, direcciones locales como `http://localhost` también se consideran potencialmente confiables. Puedes comprobar el contexto mediante `window.isSecureContext`. La documentación de [contextos seguros](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Secure_Contexts) explica estas condiciones.

Además, conviene comprobar que el método existe:

```javascript
const puedeCopiar =
  window.isSecureContext &&
  typeof navigator.clipboard?.writeText === "function";
```

Esta comprobación detecta disponibilidad, pero **no garantiza que el navegador autorice la operación**. Por eso seguiremos necesitando manejar el rechazo de la promesa.

Piensa en ella como una primera pregunta: “¿Puedo intentar utilizar esta funcionalidad?”. La respuesta definitiva llegará al ejecutar el método.

## Construyamos un ejemplo completo

Vamos a permitir que el usuario escriba un texto y lo copie mediante un botón. También mostraremos el resultado en la propia página.

Puedes colocar este contenido dentro del `<body>` de un documento HTML. El script debe aparecer después de los elementos que consulta:

```html
<label for="texto">Texto para copiar</label>

<textarea id="texto" rows="4">¡Hola, comunidad de DEV!</textarea>

<button id="copiar" type="button">
  Copiar texto
</button>

<p id="estado" role="status"></p>

<script>
  const campo = document.querySelector("#texto");
  const boton = document.querySelector("#copiar");
  const estado = document.querySelector("#estado");

  boton.addEventListener("click", async () => {
    const texto = campo.value;

    if (texto.length === 0) {
      estado.textContent = "Escribe algo antes de copiar.";
      return;
    }

    if (
      !window.isSecureContext ||
      typeof navigator.clipboard?.writeText !== "function"
    ) {
      estado.textContent =
        "El copiado automático no está disponible. " +
        "Selecciona el texto y cópialo manualmente.";
      return;
    }

    boton.disabled = true;
    estado.textContent = "Copiando…";

    try {
      await navigator.clipboard.writeText(texto);
      estado.textContent = "¡Texto copiado al portapapeles!";
    } catch (error) {
      console.error("Error al copiar:", error);

      estado.textContent =
        "No se pudo copiar. Selecciona el texto " +
        "y utiliza la opción Copiar de tu dispositivo.";
    } finally {
      boton.disabled = false;
    }
  });
</script>
```

Aquí hay varias decisiones pequeñas que mejoran el comportamiento.

Usamos `.value` porque el origen es un campo de formulario. El atributo `type="button"` evita que el botón envíe accidentalmente un formulario si después lo colocamos dentro de uno.

Mientras la operación está pendiente, deshabilitamos el botón para evitar solicitudes repetidas. El bloque `finally` lo habilita tanto si la copia funciona como si falla.

Por último, `role="status"` permite que las tecnologías de asistencia anuncien los cambios del mensaje sin que tengamos que desplazar el foco.

## Copiar exactamente lo que corresponde

Nuestro ejemplo comprueba si el campo está vacío, pero conserva el contenido original. No aplica `trim()` antes de copiar.

Esto es intencional: los espacios y saltos de línea pueden formar parte de un fragmento de código, una plantilla o un bloque de configuración. Eliminarlos automáticamente podría modificar el resultado esperado.

El origen del texto también determina cómo debemos obtenerlo:

```javascript
// Campo de formulario
const nombre = document.querySelector("#nombre").value;

// Contenido textual de un elemento
const comando = document.querySelector("#comando").textContent;

// Dato generado por la aplicación
const referencia = `Pedido: ${numeroPedido}`;
```

Para copiar un bloque de código, `textContent` suele ser una buena elección:

```html
<pre><code id="comando">npm install mi-paquete</code></pre>
```

```javascript
const texto = document.querySelector("#comando").textContent;
```

Revisa la indentación de tu HTML: los espacios y saltos presentes dentro del elemento también pueden aparecer en el texto obtenido.

Si utilizas `innerHTML`, obtendrás una cadena con etiquetas. Pasar esa cadena a `writeText()` copiará los caracteres de esas etiquetas; no creará contenido enriquecido.

## El clic y los permisos del navegador

La forma más portable de iniciar la copia es hacerlo directamente desde una interacción explícita, como pulsar el botón.

Los navegadores tienen diferencias en sus requisitos. Firefox y Safari requieren activación transitoria del usuario para escribir; Chromium admite escritura mediante activación o mediante el permiso correspondiente. Consultar `clipboard-write` con la API de permisos tampoco funciona de manera uniforme entre navegadores. Estos matices aparecen en la [documentación de seguridad de Clipboard API](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API#security_considerations).

Por ello, para este caso práctico podemos llamar a `writeText()` dentro del evento `click` y capturar cualquier error.

También conviene evitar una petición de red antes de intentar copiar:

```javascript
boton.addEventListener("click", async () => {
  const respuesta = await fetch("/api/enlace");
  const { enlace } = await respuesta.json();

  await navigator.clipboard.writeText(enlace);
});
```

Durante esa espera puede perderse la activación necesaria. Una alternativa es obtener el enlace previamente y habilitar el botón cuando el dato esté listo.

## Cómo tratar los errores

Uno de los errores documentados de `writeText()` es `NotAllowedError`, que indica que la escritura no está permitida. La referencia de [MDN sobre `writeText()`](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText) detalla este comportamiento.

No conviene traducir cualquier rechazo como “Has denegado el permiso”. El problema también puede estar relacionado con las restricciones del contexto o la forma de iniciar la operación.

Para la interfaz, un mensaje útil sería:

> No se pudo copiar automáticamente. Puedes seleccionar el texto y copiarlo manualmente.

Para depurar, conserva el error en la consola. Así ayudas al desarrollador sin mostrar detalles técnicos innecesarios al usuario.

## Una función reutilizable

Si necesitas copiar desde varios componentes, puedes separar la operación de los mensajes visuales:

```javascript
async function copiarAlPortapapeles(texto) {
  if (typeof texto !== "string") {
    throw new TypeError("El contenido debe ser una cadena.");
  }

  if (
    !window.isSecureContext ||
    typeof navigator.clipboard?.writeText !== "function"
  ) {
    throw new Error("El copiado automático no está disponible.");
  }

  await navigator.clipboard.writeText(texto);
}
```

Cada componente decide después cómo presentar el resultado:

```javascript
boton.addEventListener("click", async () => {
  try {
    await copiarAlPortapapeles(campo.value);
    estado.textContent = "¡Copiado!";
  } catch (error) {
    estado.textContent = "No se pudo copiar automáticamente.";
    console.error(error);
  }
});
```

La función deja que los errores lleguen al código que la utiliza. Así evitamos ocultar un fallo y continuar como si todo hubiera funcionado.

## ¿Qué ocurre con `execCommand("copy")`?

Quizá hayas visto ejemplos que crean un `<textarea>` temporal, lo seleccionan y ejecutan `document.execCommand("copy")`.

Ese método está obsoleto para este propósito; la documentación recomienda utilizar Clipboard API. Encontrarás esa recomendación en la [introducción de MDN a la API](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API).

Para una implementación nueva, empieza con `writeText()` y ofrece una alternativa manual cuando no esté disponible. Si tu proyecto necesita compatibilidad heredada, evalúa ese requisito por separado.

## Comprueba la experiencia completa

Prueba el botón en los navegadores que utiliza tu audiencia. Copia texto con acentos, emojis, espacios y varias líneas; después pégalo en otra aplicación y comprueba el resultado.

Revisa también el caso vacío, la navegación con teclado y el mensaje que aparece cuando la copia falla. Si pruebas dentro de un editor con vista previa embebida, verifica además las restricciones del contenedor.

Con `navigator.clipboard.writeText()` podemos resolver la escritura de texto con muy poco código. Una implementación cuidada añade lo que hace útil esa operación: una acción clara, confirmación después del éxito y una salida comprensible cuando algo falla.
