# Creando Arte CSS Accesible

El "CSS Art" —dibujar ilustraciones usando únicamente HTML y CSS, sin imágenes ni SVG— es una de esas disciplinas que suele verse como puramente lúdica o como un ejercicio de virtuosismo técnico. Sin embargo, cuando se hace bien, puede ser una forma legítima de añadir personalidad visual a un sitio sin sacrificar accesibilidad. En este post vamos a ver cómo crear ilustraciones con CSS teniendo en cuenta, desde el principio, a las personas que usan lectores de pantalla o que navegan sin ver la pantalla en absoluto.

## El problema de base

La mayoría de tutoriales de CSS Art se centran exclusivamente en la técnica visual: cómo usar `border-radius`, `clip-path`, `box-shadow` o pseudo-elementos para dibujar formas complejas. Pero rara vez se menciona qué pasa cuando un lector de pantalla llega a ese `<div>` compuesto por quince elementos anidados sin ningún significado semántico. En el mejor de los casos, el lector de pantalla lo ignora silenciosamente. En el peor, intenta leer atributos, clases o contenido de texto que quedó ahí por accidente, generando ruido innecesario.

## Regla número uno: es decorativo, trátalo como decorativo

Si el dibujo hecho con CSS es puramente decorativo —no transmite información que no esté disponible en otro lugar de la página—, debe ocultarse completamente de la accesibility tree. Esto se logra con `aria-hidden="true"` en el contenedor raíz del dibujo:

```html
<div class="ilustracion-gato" aria-hidden="true">
  <div class="cabeza"></div>
  <div class="oreja oreja-izquierda"></div>
  <div class="oreja oreja-derecha"></div>
  <div class="ojo ojo-izquierdo"></div>
  <div class="ojo ojo-derecho"></div>
</div>
```

Con `aria-hidden="true"`, todo el subárbol de elementos queda excluido de lo que anuncian los lectores de pantalla, sin afectar en absoluto a su renderizado visual. Esto es exactamente lo que queremos: alguien que no puede ver la ilustración no debería tener que escuchar "cabeza, oreja izquierda, oreja derecha, ojo izquierdo, ojo derecho" sin ningún contexto que le explique qué está pasando.

## Regla número dos: si transmite información, dale una alternativa textual

El caso distinto es cuando el CSS Art no es meramente decorativo, sino que comunica algo: un ícono de estado (como una carita feliz o triste indicando el resultado de una acción), un gráfico simplificado, o cualquier elemento donde el contenido visual importa para entender la página. En ese caso, no basta con ocultarlo: hace falta una alternativa textual equivalente.

```html
<div class="icono-exito" role="img" aria-label="Operación completada con éxito">
  <div class="circulo"></div>
  <div class="check"></div>
</div>
```

Aquí usamos `role="img"` para indicarle al lector de pantalla que trate todo el conjunto como una sola imagen conceptual, y `aria-label` para darle el texto equivalente. De esta forma, quien no puede ver la animación de CSS igualmente recibe la información: "Operación completada con éxito".

## Cuidado con el foco y el teclado

Otro error frecuente en CSS Art es hacer que elementos puramente decorativos sean, sin querer, "tabulables". Esto puede pasar si usamos elementos como `<a>` o `<button>` para construir partes del dibujo por conveniencia de estilos, en lugar de `<div>` o `<span>`:

```css
/* Mal: usar un <a> vacío solo para aprovechar :hover */
.parte-decorativa {
  /* ... */
}
```

Si necesitas interactividad real (por ejemplo, que el dibujo cambie al pasar el ratón), usa `:hover` sobre un `<div>` normal, o añade la interacción sobre un elemento contenedor que sí tenga sentido semántico, no sobre fragmentos sueltos del dibujo.

## Animaciones y prefers-reduced-motion

El CSS Art frecuentemente viene acompañado de animaciones: un personaje que parpadea, una nube que se mueve, un sol que gira. Para las personas con trastornos vestibulares o sensibilidad al movimiento, estas animaciones pueden causar mareo o malestar real, no solo una molestia estética. La media query `prefers-reduced-motion` permite respetar la preferencia del sistema operativo del usuario:

```css
.ilustracion-nube {
  animation: flotar 3s ease-in-out infinite;
}

@media (prefers-reduced-motion: reduce) {
  .ilustracion-nube {
    animation: none;
  }
}
```

Esto no significa eliminar toda la animación necesariamente: se puede optar por una versión mucho más sutil o directamente estática, en lugar de un `none` total, dependiendo del caso.

## Contraste de color

Aunque estemos "dibujando" con CSS y no con una herramienta de diseño tradicional, las reglas de contraste de la WCAG siguen aplicando si el dibujo contiene texto o si es parte de un elemento interactivo (como un ícono de botón). La relación de contraste mínima recomendada es de 4.5:1 para texto normal y 3:1 para elementos gráficos que transmiten información de estado, como iconos de éxito o error.

```css
.icono-error {
  background-color: #d32f2f; /* rojo con suficiente contraste sobre blanco */
}
```

Existen múltiples herramientas online para comprobar ratios de contraste antes de decidir la paleta final de un dibujo hecho con CSS.

## Un ejemplo completo

Juntando todo lo anterior, un dibujo decorativo de un sol simple, accesible, quedaría así:

```html
<div class="sol" aria-hidden="true">
  <div class="circulo-sol"></div>
  <div class="rayo" style="--i: 0"></div>
  <div class="rayo" style="--i: 1"></div>
  <!-- más rayos -->
</div>
```

```css
.sol {
  position: relative;
  width: 100px;
  height: 100px;
}

.circulo-sol {
  width: 60px;
  height: 60px;
  background: #ffb703;
  border-radius: 50%;
  position: absolute;
  top: 20px;
  left: 20px;
}

.rayo {
  width: 4px;
  height: 20px;
  background: #ffb703;
  position: absolute;
  top: 0;
  left: 48px;
  transform-origin: 2px 50px;
  transform: rotate(calc(var(--i) * 45deg));
  animation: girar 20s linear infinite;
}

@media (prefers-reduced-motion: reduce) {
  .rayo {
    animation: none;
  }
}

@keyframes girar {
  to {
    transform: rotate(calc(var(--i) * 45deg + 360deg));
  }
}
```

## Conclusión

El CSS Art puede convivir perfectamente con la accesibilidad, pero requiere tomar decisiones conscientes en cada paso: decidir si el dibujo es decorativo o informativo, ocultarlo o darle una alternativa textual según corresponda, respetar las preferencias de movimiento reducido del usuario, y cuidar el contraste cuando aplique. Ninguna de estas prácticas añade complejidad significativa al proceso creativo; simplemente requieren tenerlas presentes desde el diseño inicial, en lugar de tratarlas como un añadido de última hora. Un dibujo bonito que excluye a una parte de tus usuarios no es, en realidad, un buen dibujo.
