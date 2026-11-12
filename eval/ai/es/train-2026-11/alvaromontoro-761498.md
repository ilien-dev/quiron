# Creando Arte CSS Accesible

El arte CSS tiene algo hipnótico: con un puñado de `div`, gradientes y `border-radius` puedes dibujar un gato, un paisaje o el logo de tu framework favorito. Es un gran ejercicio para entender el modelo de caja, el posicionamiento y las capas.

Pero hay un problema que casi nunca se menciona en los tutoriales: **la mayoría de las piezas de arte CSS son invisibles o ruidosas para quien usa un lector de pantalla**, y muchas incluyen animaciones que pueden provocar mareos o molestias a otras personas.

En este post vamos a construir una pequeña ilustración (un paisaje con sol y montañas) y a hacerla accesible paso a paso. Las ideas se aplican a cualquier pieza que hagas.

## El problema: un dibujo hecho de "nada"

Imagina este HTML típico de arte CSS:

```html
<div class="escena">
  <div class="sol"></div>
  <div class="montana montana-1"></div>
  <div class="montana montana-2"></div>
</div>
```

Para un lector de pantalla, esto es básicamente vacío. Los `div` sin texto no se anuncian, así que la persona se pierde la ilustración por completo. Y si alguien añade contenido de relleno o `title` por todas partes, el resultado puede ser peor: una cascada de ruido.

La pregunta clave es: **¿esta imagen es informativa o decorativa?**

- Si es **decorativa** (un adorno sin significado), debe ocultarse a la tecnología de asistencia.
- Si es **informativa** (aporta contenido, como una ilustración de portfolio), debe exponerse como una única imagen con una descripción.

## Paso 1: tratar toda la escena como una sola imagen

En lugar de dejar que cada `div` sea un elemento suelto, agrupamos todo con `role="img"` y le damos un nombre accesible:

```html
<div
  class="escena"
  role="img"
  aria-label="Paisaje al atardecer: un sol naranja asoma tras dos montañas azules."
>
  <div class="sol"></div>
  <div class="montana montana-1"></div>
  <div class="montana montana-2"></div>
</div>
```

Con `role="img"`, el lector de pantalla anuncia el contenedor como una imagen y lee el `aria-label`. Además, los hijos de un elemento con rol `img` se consideran "presentacionales": no se recorren individualmente. Justo lo que queremos.

Unas pautas para escribir buenas descripciones:

- **Sé concreto y breve.** Una o dos frases suelen bastar.
- **Describe lo que importa**, no cada detalle de implementación. Nadie necesita saber que hay tres `div` y un gradiente.
- **No empieces con "Imagen de…"**: el rol ya lo dice.

Si la descripción es larga, puedes usar `aria-labelledby` o `aria-describedby` apuntando a un texto visible o a un párrafo oculto visualmente.

## Paso 2: si es decorativa, escóndela

Si el dibujo es solo un adorno, por ejemplo un fondo en la cabecera, lo correcto es sacarlo del árbol de accesibilidad:

```html
<div class="escena" aria-hidden="true">
  ...
</div>
```

Un detalle importante: `aria-hidden="true"` **no** debe usarse en elementos que puedan recibir foco. Si tu arte tiene un enlace o un botón dentro, tendrías un elemento enfocable pero invisible para el lector, que es peor que no hacer nada.

Lo mismo se aplica a los pseudoelementos. El contenido generado con `::before` y `::after` puede ser leído por algunos lectores si usas la propiedad `content` con texto. Para formas puramente visuales, deja el contenido vacío:

```css
.sol::after {
  content: "";
  /* formas, no texto */
}
```

Y si necesitas un carácter decorativo, puedes añadir una alternativa vacía con la sintaxis moderna:

```css
.adorno::before {
  content: "★" / "";
}
```

Esa barra indica que el texto alternativo del contenido generado es una cadena vacía, así que se ignora en la tecnología de asistencia (con soporte creciente en los navegadores actuales).

## Paso 3: colores con contraste suficiente

Aquí hay un matiz interesante. Las WCAG exigen contraste para **texto** (4.5:1 para texto normal) y para **componentes de interfaz y gráficos necesarios para entender el contenido** (3:1). Si tu arte transmite información, por ejemplo un gráfico o un icono con significado, aplica ese 3:1.

Si es puramente estético, no hay obligación estricta, pero conviene pensarlo igual. Una ilustración donde el sol se confunde con el cielo pierde su gracia para quien tiene baja visión o ve la pantalla bajo mucha luz.

Definir los colores con variables te ayuda a revisarlos y a ajustarlos en un solo sitio:

```css
:root {
  --cielo: #1b2a49;
  --sol: #ffb347;
  --montana-1: #3d5a80;
  --montana-2: #98c1d9;
}

.escena {
  background: var(--cielo);
}
```

Puedes comprobar los ratios con las herramientas de contraste de las DevTools del navegador o con cualquier comprobador online.

## Paso 4: respeta `prefers-reduced-motion`

Lo más vistoso del arte CSS suele ser la animación: el sol que sube, las nubes que se desplazan, estrellas que parpadean. Pero para personas con trastornos vestibulares, migrañas o epilepsia fotosensible, el movimiento puede ser un problema real.

Los sistemas operativos permiten indicar "reducir movimiento", y CSS lo expone con una media query:

```css
.sol {
  animation: amanecer 8s ease-in-out infinite alternate;
}

@keyframes amanecer {
  from { transform: translateY(40px); }
  to   { transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
  .sol {
    animation: none;
  }
}
```

Otra estrategia, a veces más limpia, es plantearlo al revés: **la animación solo se activa si el usuario no ha pedido reducirla**.

```css
@media (prefers-reduced-motion: no-preference) {
  .sol {
    animation: amanecer 8s ease-in-out infinite alternate;
  }
}
```

Así, el estado por defecto es estático y seguro, y el movimiento es una mejora progresiva.

Además, evita destellos: nada que parpadee más de tres veces por segundo. Y si tu animación dura más de cinco segundos y se reproduce sola, ofrece un control para pausarla.

## Paso 5: modo de alto contraste y colores forzados

En Windows, el modo de alto contraste (`forced-colors`) reemplaza tus colores por una paleta del sistema. Los `background-color` de tus formas pueden desaparecer, y tu paisaje se convertiría en un rectángulo vacío.

Puedes detectarlo y ajustar:

```css
@media (forced-colors: active) {
  .escena {
    border: 2px solid CanvasText;
  }
  .sol {
    border: 2px solid CanvasText;
    background: Canvas;
  }
}
```

No hace falta recrear la obra artística: basta con que las formas principales sigan siendo reconocibles gracias a sus bordes.

## Paso 6: considera SVG cuando CSS ya no es la herramienta

Hay una verdad incómoda: a veces el arte CSS no es la mejor opción para contenido informativo. Un SVG permite un `<title>` y un `<desc>` nativos, escala sin perder calidad y es más fácil de mantener.

```html
<svg role="img" aria-labelledby="t d" viewBox="0 0 200 120">
  <title id="t">Paisaje al atardecer</title>
  <desc id="d">Un sol naranja asoma tras dos montañas azules.</desc>
  <circle cx="100" cy="70" r="24" fill="#ffb347" />
  <polygon points="0,120 60,50 120,120" fill="#3d5a80" />
  <polygon points="80,120 150,40 200,120" fill="#98c1d9" />
</svg>
```

El arte CSS sigue siendo un fantástico ejercicio creativo y de aprendizaje. Pero si tu ilustración va a formar parte del contenido real de un producto, valora si SVG te da mejores garantías.

## Paso 7: prueba de verdad

La accesibilidad no se asume, se verifica. Una lista corta de comprobaciones:

1. **Lector de pantalla.** Prueba con NVDA o Narrator en Windows, VoiceOver en macOS o TalkBack en Android. ¿Se anuncia una sola imagen con una descripción útil?
2. **Teclado.** Si hay elementos interactivos, ¿se puede navegar con `Tab` y se ve el foco?
3. **Movimiento reducido.** Activa la preferencia en tu sistema y recarga. ¿Se detienen las animaciones?
4. **Zoom al 200 %–400 %.** ¿Se rompe la composición o aparece scroll horizontal?
5. **Contraste.** Revisa los colores clave con las DevTools.
6. **Auditoría automática.** Lighthouse o axe DevTools detectan errores comunes, aunque no sustituyen las pruebas manuales.

## Resultado final: el esqueleto accesible

Juntando todo, el patrón base queda así:

```html
<figure>
  <div
    class="escena"
    role="img"
    aria-label="Paisaje al atardecer: un sol naranja asoma tras dos montañas azules."
  >
    <div class="sol"></div>
    <div class="montana montana-1"></div>
    <div class="montana montana-2"></div>
  </div>
  <figcaption>Ilustración hecha solo con CSS.</figcaption>
</figure>
```

```css
.escena {
  position: relative;
  width: min(100%, 400px);
  aspect-ratio: 5 / 3;
  background: var(--cielo);
  overflow: hidden;
}

@media (prefers-reduced-motion: no-preference) {
  .sol { animation: amanecer 8s ease-in-out infinite alternate; }
}

@media (forced-colors: active) {
  .escena, .sol { border: 2px solid CanvasText; }
}
```

## Conclusión

Hacer arte CSS accesible no quita creatividad; añade una capa de oficio. Se reduce a unas pocas decisiones:

- **Decide si el dibujo es informativo o decorativo.**
- **Usa `role="img"` y `aria-label`** para las piezas con significado, y `aria-hidden="true"` para las decorativas.
- **Cuida el contraste** cuando la imagen transmita información.
- **Respeta `prefers-reduced-motion`** y evita destellos.
- **Contempla `forced-colors`** para que la pieza siga siendo legible.
- **Considera SVG** cuando el contenido sea realmente importante.
- **Prueba con herramientas reales** y, si puedes, con personas usuarias reales.

La próxima vez que dibujes con `div`, pregúntate quién podría quedarse fuera de tu obra. Con unos pocos atributos y media queries, la respuesta puede ser: nadie.

¿Tienes alguna pieza de arte CSS que quieras adaptar? Cuéntamelo en los comentarios y la revisamos juntos.
