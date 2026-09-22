---
title: Copiado de texto al portapapeles con JavaScript - API Asíncrona
published: true
description: Aprende a copiar texto al portapapeles con la API asíncrona de JavaScript, gestionar errores y crear una experiencia accesible.
tags: javascript, webdev, tutorial, frontend
---

# Copiado de texto al portapapeles con JavaScript - API Asíncrona

Copiar texto al portapapeles es una función pequeña, pero muy útil. Aparece en gestores de contraseñas, bloques de código, aplicaciones bancarias, tiendas en línea y cualquier interfaz que permita compartir enlaces, identificadores o datos difíciles de escribir manualmente.

Durante años, implementar esta funcionalidad requería crear un elemento temporal, seleccionar su contenido y ejecutar `document.execCommand("copy")`. Aunque ese método todavía puede encontrarse en proyectos antiguos, actualmente contamos con una alternativa más clara: la **Clipboard API**.

Esta API ofrece métodos asíncronos para leer y escribir en el portapapeles mediante promesas. En este artículo veremos cómo usar `navigator.clipboard.writeText()`, cómo manejar sus errores y qué detalles debemos considerar para construir una solución segura y accesible.

## El método `writeText()`

La forma más sencilla de copiar una cadena es llamar a `navigator.clipboard.writeText()`:

```js
navigator.clipboard.writeText("Texto que será copiado");
```

El método recibe una cadena y devuelve una promesa. Esto es importante porque copiar al portapapeles no es una operación instantánea controlada únicamente por JavaScript: el navegador debe comunicarse con el sistema operativo, verificar permisos y aplicar sus políticas de seguridad.

Por tanto, debemos esperar a que la operación termine:

```js
navigator.clipboard
  .writeText("Hola desde JavaScript")
  .then(() => {
    console.log("Texto copiado");
  })
  .catch((error) => {
    console.error("No fue posible copiar el texto", error);
  });
```

También podemos utilizar `async` y `await`, que suelen producir un código más fácil de leer:

```js
async function copiarTexto(texto) {
  try {
    await navigator.clipboard.writeText(texto);
    console.log("Texto copiado correctamente");
  } catch (error) {
    console.error("Error al copiar:", error);
  }
}
```

La función puede reutilizarse desde diferentes partes de la aplicación:

```js
copiarTexto("ABC-123");
```

## Ejemplo con un botón

Veamos un ejemplo completo. Imaginemos una página que muestra un código de invitación y permite copiarlo pulsando un botón.

```html
<p>
  Código de invitación:
  <strong id="codigo">DEV-2026-JS</strong>
</p>

<button id="copiar" type="button">
  Copiar código
</button>

<p id="mensaje" role="status" aria-live="polite"></p>
```

El comportamiento puede implementarse así:

```js
const boton = document.querySelector("#copiar");
const codigo = document.querySelector("#codigo");
const mensaje = document.querySelector("#mensaje");

boton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(codigo.textContent);

    mensaje.textContent = "Código copiado al portapapeles";
  } catch (error) {
    mensaje.textContent = "No se pudo copiar el código";
    console.error(error);
  }
});
```

Cuando el usuario hace clic, obtenemos el contenido del elemento y esperamos el resultado de `writeText()`. Solo mostramos el mensaje de éxito después de que la promesa se resuelva.

Esto evita un error común: cambiar inmediatamente el texto del botón a “Copiado” sin comprobar si la operación realmente funcionó.

## Requisitos de seguridad

El acceso al portapapeles puede exponer información sensible o permitir que una página reemplace contenido sin que el usuario lo note. Por eso, los navegadores aplican ciertas restricciones.

En general, la Clipboard API necesita ejecutarse en un **contexto seguro**. Esto significa que la página debe utilizar HTTPS. Durante el desarrollo, los navegadores normalmente consideran `localhost` como un contexto seguro, por lo que puedes probar la funcionalidad desde un servidor local.

Una página cargada mediante HTTP desde un dominio público podría no tener acceso a `navigator.clipboard`.

También es recomendable iniciar la copia como resultado directo de una interacción del usuario, por ejemplo:

- Un clic sobre un botón.
- La activación de un control con el teclado.
- Una acción equivalente iniciada por la persona usuaria.

Los navegadores pueden rechazar intentos automáticos realizados al cargar la página o después de procesos que ya no están claramente asociados con la interacción original.

Por ejemplo, esta práctica no es aconsejable:

```js
window.addEventListener("load", () => {
  navigator.clipboard.writeText("Contenido inesperado");
});
```

Aunque el comportamiento exacto depende del navegador y de sus políticas, una interfaz no debería modificar el portapapeles sin una intención clara del usuario.

## Comprobar la disponibilidad de la API

No todos los entornos ofrecen la misma compatibilidad. Un navegador antiguo, una vista web integrada o una página sin HTTPS podrían no exponer `navigator.clipboard`.

Podemos comprobar su disponibilidad antes de usarla:

```js
function permiteCopiar() {
  return Boolean(
    navigator.clipboard &&
    typeof navigator.clipboard.writeText === "function"
  );
}
```

Después utilizamos la comprobación para adaptar la interfaz:

```js
const boton = document.querySelector("#copiar");

if (!permiteCopiar()) {
  boton.disabled = true;
  boton.textContent = "Copia no disponible";
}
```

Ocultar o desactivar el botón puede ser apropiado, pero no siempre es la mejor experiencia. En ocasiones conviene conservar el texto visible y permitir que el usuario lo seleccione manualmente.

Una alternativa es mostrar una instrucción:

```js
if (!permiteCopiar()) {
  mensaje.textContent =
    "Selecciona el código y cópialo manualmente.";
}
```

La mejora progresiva consiste precisamente en esto: ofrecer primero una experiencia básica funcional y añadir capacidades cuando el navegador las soporta.

## Manejo correcto de errores

Aunque la API exista, la copia todavía puede fallar. Algunas causas posibles son:

- El documento no se encuentra en un contexto seguro.
- El navegador bloquea la operación.
- La página está dentro de un `iframe` con permisos limitados.
- La acción no procede de una interacción válida.
- Una política empresarial deshabilita el acceso al portapapeles.
- El documento perdió el foco.
- El usuario o el sistema denegaron el permiso.

Por esa razón, el bloque `catch` no debe considerarse opcional:

```js
async function copiarTexto(texto) {
  if (!navigator.clipboard?.writeText) {
    throw new Error("La Clipboard API no está disponible");
  }

  await navigator.clipboard.writeText(texto);
}
```

La función anterior permite que quien la invoque decida cómo comunicar el problema:

```js
boton.addEventListener("click", async () => {
  try {
    await copiarTexto(codigo.textContent);
    mostrarEstado("Copiado");
  } catch (error) {
    mostrarEstado("No se pudo copiar. Inténtalo manualmente.");
    console.error("Fallo al acceder al portapapeles:", error);
  }
});
```

Separar la operación técnica de la actualización visual facilita reutilizar el código y probar cada parte de forma independiente.

## Mejorar la experiencia del botón

Una confirmación breve ayuda a que el usuario sepa que la acción terminó. Podemos cambiar temporalmente el contenido del botón:

```js
const textoOriginal = boton.textContent;

boton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(codigo.textContent);

    boton.textContent = "¡Copiado!";
    boton.disabled = true;

    setTimeout(() => {
      boton.textContent = textoOriginal;
      boton.disabled = false;
    }, 1500);
  } catch {
    boton.textContent = "Error al copiar";

    setTimeout(() => {
      boton.textContent = textoOriginal;
    }, 1500);
  }
});
```

Desactivar el control durante unos instantes impide clics repetidos, aunque no siempre será necesario. Si el texto puede cambiar en ese intervalo, asegúrate de que la interfaz no dé una impresión equivocada.

También podemos conservar el texto visible y cambiar únicamente un icono o una región de estado. Esto evita que el tamaño del botón varíe y provoque movimientos en el diseño.

## Accesibilidad

Una notificación puramente visual puede pasar desapercibida para personas que utilizan un lector de pantalla. Por eso, en el ejemplo inicial incluimos:

```html
<p id="mensaje" role="status" aria-live="polite"></p>
```

Al actualizar su contenido, las tecnologías de asistencia pueden anunciar el resultado sin interrumpir bruscamente la navegación.

Además, conviene seguir estas recomendaciones:

1. Utiliza un elemento `<button>` real, no un `<div>` con un evento `click`.
2. Proporciona una etiqueta clara, como “Copiar enlace”.
3. No comuniques el éxito únicamente mediante un cambio de color.
4. Mantén visible o recuperable el contenido original.
5. Permite seleccionar manualmente el texto cuando sea posible.
6. No retires el foco del control después de copiar.

Si el botón solo contiene un icono, necesita un nombre accesible:

```html
<button
  type="button"
  id="copiar"
  aria-label="Copiar código de invitación"
>
  📋
</button>
```

Los iconos pueden resultar intuitivos para algunas personas, pero una etiqueta elimina ambigüedades.

## Copiar el valor de un campo

Cuando el contenido está en un `<input>` o `<textarea>`, debemos utilizar su propiedad `value`:

```html
<input
  id="enlace"
  type="text"
  value="https://ejemplo.com/invitacion/abc123"
  readonly
>

<button id="copiar-enlace" type="button">
  Copiar enlace
</button>
```

```js
const enlace = document.querySelector("#enlace");
const botonEnlace = document.querySelector("#copiar-enlace");

botonEnlace.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(enlace.value);
    console.log("Enlace copiado");
  } catch (error) {
    console.error("No se pudo copiar el enlace", error);
  }
});
```

`textContent` sirve para obtener el texto de un elemento del documento, mientras que `value` representa el contenido actual de un control de formulario. Confundirlos puede producir una cadena vacía o copiar un valor desactualizado.

## Crear un componente reutilizable

Si una página tiene varios botones para copiar, podemos evitar registrar cada evento manualmente mediante atributos `data-*`:

```html
<pre id="comando-instalacion">npm install mi-paquete</pre>
<button type="button" data-copy="#comando-instalacion">
  Copiar comando
</button>

<p id="token-publico">pk_demo_123456</p>
<button type="button" data-copy="#token-publico">
  Copiar token
</button>
```

Un único listener puede atender todos los controles:

```js
document.addEventListener("click", async (event) => {
  const boton = event.target.closest("[data-copy]");

  if (!boton) {
    return;
  }

  const selector = boton.dataset.copy;
  const origen = document.querySelector(selector);

  if (!origen) {
    console.error(`No existe un elemento para: ${selector}`);
    return;
  }

  const texto =
    "value" in origen
      ? origen.value
      : origen.textContent;

  try {
    await navigator.clipboard.writeText(texto.trim());
    boton.dataset.estado = "copiado";
  } catch (error) {
    boton.dataset.estado = "error";
    console.error(error);
  }
});
```

Este enfoque utiliza delegación de eventos y permite añadir nuevos botones desde HTML sin repetir la lógica de JavaScript.

El uso de `trim()` es opcional. Resulta útil para eliminar saltos de línea producidos por el formato del documento, pero no debe aplicarse cuando los espacios iniciales o finales forman parte significativa del contenido.

## Alternativa para navegadores antiguos

En código heredado es frecuente encontrar `document.execCommand("copy")`. Una implementación típica crea un `<textarea>` temporal, selecciona su contenido y ejecuta el comando:

```js
function copiarConMetodoAntiguo(texto) {
  const area = document.createElement("textarea");

  area.value = texto;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";

  document.body.appendChild(area);
  area.select();

  const resultado = document.execCommand("copy");

  area.remove();

  return resultado;
}
```

Sin embargo, `execCommand()` está obsoleto. No debería ser la primera opción en proyectos nuevos y su comportamiento puede variar entre navegadores.

Si necesitas mantener compatibilidad con un entorno específico, puedes utilizarlo como último recurso:

```js
async function copiar(texto) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(texto);
    return true;
  }

  return copiarConMetodoAntiguo(texto);
}
```

Antes de añadir esta complejidad, revisa qué navegadores debe soportar realmente el proyecto. A veces una selección manual acompañada de instrucciones claras es una alternativa más mantenible.

## `writeText()` frente a `write()`

`writeText()` está diseñado para texto plano. Es suficiente para enlaces, comandos, identificadores y fragmentos de código.

La Clipboard API también incluye `navigator.clipboard.write()`, que permite trabajar con objetos `ClipboardItem` y otros formatos, como imágenes o contenido HTML:

```js
const contenido = new Blob(
  ["<strong>Hola</strong>"],
  { type: "text/html" }
);

const elemento = new ClipboardItem({
  "text/html": contenido
});

await navigator.clipboard.write([elemento]);
```

Esta capacidad tiene más consideraciones de compatibilidad y seguridad. Si solo necesitas copiar una cadena, `writeText()` es la solución más directa y predecible.

## Conclusión

La API asíncrona del portapapeles convierte una operación históricamente incómoda en unas pocas líneas:

```js
await navigator.clipboard.writeText(texto);
```

Pero una implementación completa requiere algo más que llamar al método. Debemos ejecutarlo desde una interacción del usuario, servir la página mediante HTTPS, comprobar la disponibilidad de la API y manejar cualquier rechazo de la promesa.

También es importante comunicar el resultado de manera accesible y ofrecer una alternativa cuando la copia automática no esté disponible.

Una función sencilla y reutilizable puede cubrir la mayoría de los casos:

```js
async function copiarAlPortapapeles(texto) {
  if (!navigator.clipboard?.writeText) {
    throw new Error("El portapapeles no está disponible");
  }

  await navigator.clipboard.writeText(String(texto));
}
```

A partir de ahí, cada aplicación puede decidir cómo presentar el éxito, el error y la opción de copia manual. La operación técnica es pequeña; la diferencia entre una función que simplemente existe y una que se siente bien está en esos detalles.