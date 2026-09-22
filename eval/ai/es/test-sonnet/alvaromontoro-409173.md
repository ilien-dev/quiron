# Desarrollando un mini-Rock Band con HTML y JavaScript

¿Quién no ha soñado alguna vez con tener su propia consola de Guitar Hero o Rock Band en el navegador? En este post vamos a construir, paso a paso, una versión muy simplificada de ese tipo de juego usando solo HTML, CSS y JavaScript puro, sin frameworks ni librerías externas. El objetivo no es crear un juego comercial, sino entender los conceptos básicos detrás de este tipo de mecánicas: notas que caen, sincronización con el tiempo, detección de pulsaciones de teclado y retroalimentación visual.

## La idea general

Un juego de ritmo como Rock Band se basa en unos pocos elementos:

1. Una serie de "carriles" (lanes) por los que caen notas.
2. Una zona de impacto donde el jugador debe pulsar la tecla correspondiente en el momento exacto.
3. Un sistema de puntuación que evalúa qué tan cerca estuvo la pulsación del momento ideal.
4. Una canción o pista de audio que marca el ritmo.

Vamos a simplificar todo esto a cuatro carriles, cada uno asociado a una tecla (por ejemplo, D, F, J, K), y notas que se generan a intervalos regulares o según un patrón predefinido.

## Estructura HTML

Empezamos con un esqueleto sencillo:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Mini Rock Band</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div id="game">
    <div class="lane" data-key="KeyD"></div>
    <div class="lane" data-key="KeyF"></div>
    <div class="lane" data-key="KeyJ"></div>
    <div class="lane" data-key="KeyK"></div>
  </div>
  <div id="score">0</div>
  <script src="game.js"></script>
</body>
</html>
```

Cada `div.lane` representa un carril. Vamos a posicionarlos uno al lado del otro con flexbox, y dentro de cada uno se irán insertando las notas dinámicamente.

## Estilos básicos

```css
#game {
  display: flex;
  width: 400px;
  height: 600px;
  margin: 0 auto;
  position: relative;
  background: #111;
  overflow: hidden;
}

.lane {
  flex: 1;
  position: relative;
  border-right: 1px solid #333;
}

.lane::after {
  content: "";
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  height: 10px;
  background: #555;
}

.note {
  position: absolute;
  top: -20px;
  left: 10%;
  width: 80%;
  height: 20px;
  background: tomato;
  border-radius: 4px;
}
```

La zona de impacto la marcamos con el pseudo-elemento `::after` en la parte inferior de cada carril. Las notas comienzan arriba (`top: -20px`) y su animación las llevará hacia abajo.

## Generando notas

En JavaScript, necesitamos una función que cree una nota nueva en un carril aleatorio (o siguiendo un patrón) cada cierto intervalo de tiempo:

```js
const lanes = document.querySelectorAll('.lane');
const game = document.getElementById('game');

function spawnNote() {
  const laneIndex = Math.floor(Math.random() * lanes.length);
  const lane = lanes[laneIndex];

  const note = document.createElement('div');
  note.classList.add('note');
  note.dataset.key = lane.dataset.key;
  note.dataset.spawnTime = performance.now();

  lane.appendChild(note);
}

setInterval(spawnNote, 800);
```

Aquí guardamos el momento exacto en que se generó la nota (`spawnTime`). Esto nos va a servir más adelante para calcular la posición correcta sin depender de animaciones CSS que sean difíciles de sincronizar con la lógica del juego.

## Moviendo las notas con requestAnimationFrame

En lugar de usar animaciones CSS, es más flexible mover las notas manualmente con `requestAnimationFrame`, porque así podemos calcular en todo momento la posición exacta de cada nota y compararla con la zona de impacto.

```js
const noteSpeed = 0.3; // píxeles por milisegundo
const gameHeight = 600;
const hitZone = gameHeight - 30;

function update(time) {
  document.querySelectorAll('.note').forEach(note => {
    const elapsed = time - note.dataset.spawnTime;
    const y = elapsed * noteSpeed;
    note.style.top = y + 'px';

    if (y > gameHeight) {
      note.remove(); // se perdió la nota
    }
  });

  requestAnimationFrame(update);
}

requestAnimationFrame(update);
```

Con esto, cada nota calcula su propia posición en función del tiempo transcurrido desde que apareció, lo cual es mucho más preciso que depender de transiciones CSS.

## Detectando las pulsaciones

Ahora necesitamos escuchar el teclado y comprobar si hay alguna nota cerca de la zona de impacto en el carril correspondiente:

```js
let score = 0;
const scoreEl = document.getElementById('score');

window.addEventListener('keydown', (e) => {
  const lane = document.querySelector(`.lane[data-key="${e.code}"]`);
  if (!lane) return;

  const notes = lane.querySelectorAll('.note');
  let bestNote = null;
  let bestDiff = Infinity;

  notes.forEach(note => {
    const top = parseFloat(note.style.top || 0);
    const diff = Math.abs(top - hitZone);
    if (diff < bestDiff) {
      bestDiff = diff;
      bestNote = note;
    }
  });

  if (bestNote && bestDiff < 40) {
    score += bestDiff < 10 ? 100 : 50;
    bestNote.remove();
    scoreEl.textContent = score;
  }
});
```

La lógica es sencilla: cuando el jugador pulsa una tecla, buscamos entre todas las notas de ese carril cuál está más cerca de la zona de impacto. Si la distancia es menor a un umbral (en este caso 40 píxeles), consideramos que fue un acierto, y le damos más puntos cuanto más cerca haya estado.

## Añadiendo sonido

Un juego de ritmo sin música no tiene mucho sentido. Podemos usar el elemento `<audio>` de HTML5 y sincronizar la generación de notas con la reproducción:

```html
<audio id="track" src="cancion.mp3"></audio>
```

```js
const track = document.getElementById('track');
track.play();
```

Para una sincronización más precisa, en lugar de usar `setInterval` para generar notas, podríamos leer un archivo de "chart" (un JSON con los tiempos exactos en que debe aparecer cada nota) y compararlo contra `track.currentTime`. Esto es exactamente lo que hacen juegos como osu! o StepMania: separan la canción de la partitura de notas, y esta última se puede diseñar manualmente o incluso generar de forma semiautomática analizando los picos de energía del audio.

## Feedback visual

Para que el juego se sienta más satisfactorio, conviene añadir algún tipo de retroalimentación cuando el jugador acierta o falla una nota. Un truco simple es cambiar brevemente el color de fondo del carril:

```js
function flashLane(lane, color) {
  lane.style.background = color;
  setTimeout(() => {
    lane.style.background = '';
  }, 100);
}
```

Llamando a `flashLane(lane, 'green')` en un acierto y `flashLane(lane, 'red')` en un fallo, el jugador recibe una confirmación inmediata sin necesidad de mirar el marcador.

## Posibles mejoras

Este mini proyecto es solo el punto de partida. Algunas ideas para seguir ampliándolo:

- Cargar patrones de notas desde un archivo JSON en lugar de generarlas aleatoriamente.
- Añadir un sistema de combos que multiplique la puntuación tras varios aciertos seguidos.
- Mostrar una barra de "salud" que baje cuando se fallan notas.
- Soportar múltiples canciones y dificultades.
- Usar Canvas en lugar de elementos DOM para mejorar el rendimiento con muchas notas en pantalla.

## Conclusión

Con relativamente poco código —un puñado de elementos HTML, algo de CSS y unas cien líneas de JavaScript— es posible construir la base de un juego de ritmo funcional. Lo más interesante de este tipo de ejercicios es que obliga a pensar en sincronización temporal, algo que no siempre trabajamos en el desarrollo web tradicional. Si te animas a probarlo, te recomiendo empezar por lo más simple (un solo carril, una sola tecla) e ir añadiendo complejidad poco a poco.

¿Te gustaría que en un próximo post exploremos cómo cargar un "chart" de notas desde un archivo externo para sincronizarlo con una canción real? Cuéntamelo en los comentarios.
