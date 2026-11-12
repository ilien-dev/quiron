# Desarrollando un mini-Rock Band con HTML y JavaScript

Los juegos rítmicos parecen magia: las notas caen, tocas la tecla justo a tiempo y todo suena bien. Pero por debajo hay una idea muy simple: **comparar el momento en que el jugador pulsa una tecla con el momento en que debía pulsarla**.

En este post construimos un mini-Rock Band de cuatro carriles usando solo HTML, un `<canvas>` y la Web Audio API. Sin librerías, sin archivos de audio y sin build. Al final tendrás un juego jugable con puntuación, combo y sonido, y una base sólida para extenderlo.

## Qué vamos a construir

- Cuatro carriles controlados con las teclas `D`, `F`, `J` y `K`.
- Notas que caen hacia una línea de impacto.
- Juicio por precisión: *Perfect*, *Good* o *Miss*.
- Puntuación con combo y multiplicador.
- Una base rítmica generada con osciladores, así que no hace falta descargar ningún `.mp3`.

## Paso 1: la estructura HTML

El HTML es mínimo. Un canvas para el juego, un HUD para la puntuación y un botón de inicio:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Mini Rock Band</title>
  <style>
    body { background:#111; color:#eee; font-family:sans-serif; text-align:center; }
    canvas { background:#1b1b2f; border:2px solid #444; }
  </style>
</head>
<body>
  <h1>Mini Rock Band</h1>
  <div id="hud">Puntos: <span id="score">0</span> · Combo: <span id="combo">0</span></div>
  <canvas id="game" width="480" height="640"></canvas><br>
  <button id="start">Empezar</button>
  <script src="game.js"></script>
</body>
</html>
```

## Paso 2: el reloj correcto

Este es el error más común al hacer un juego rítmico: usar `setTimeout`, `setInterval` o incluso `Date.now()` para sincronizar. Esos relojes se desvían del audio, y el jugador lo nota enseguida.

La solución es usar como fuente de verdad **el reloj de audio**: `audioCtx.currentTime`. Es el mismo reloj que reproduce el sonido, así que visuales y música nunca se separan.

```js
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const comboEl = document.getElementById('combo');

let audioCtx;
let startTime = 0;

function songTime() {
  // milisegundos desde que empezó la canción
  return (audioCtx.currentTime - startTime) * 1000;
}
```

Todo lo demás (posición de las notas, aciertos, fallos) se calculará a partir de `songTime()`.

## Paso 3: definir las notas

Un *chart* es simplemente una lista de notas con dos datos: **cuándo** deben tocarse y **en qué carril**. Para mantenerlo sencillo, lo generamos a partir de un BPM y un patrón:

```js
const LANES  = ['d', 'f', 'j', 'k'];
const COLORS = ['#ff4d6d', '#ffd23f', '#3bceac', '#4cc9f0'];

const BPM  = 120;
const BEAT = 60000 / BPM; // ms por negra

const pattern = [0,1,2,3,2,1,0,0, 3,2,1,0,1,2,3,3,
                 0,2,1,3,0,2,1,3, 3,3,2,2,1,1,0,0];

const notes = pattern.map((lane, i) => ({
  time: 2000 + i * (BEAT / 2),  // corcheas, tras 2 s de cuenta atrás
  lane,
  hit: false,
  missed: false
}));
```

Cada número del patrón es el índice de un carril. Con `BEAT / 2` colocamos una nota cada corchea. Si quieres canciones más elaboradas, puedes cargar este array desde un JSON.

## Paso 4: sonido sin archivos

Para la base rítmica generamos un bombo con un oscilador cuya frecuencia cae rápidamente, que es justo lo que hace un bombo sintético:

```js
function kick(when) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.frequency.setValueAtTime(150, when);
  osc.frequency.exponentialRampToValueAtTime(40, when + 0.12);
  gain.gain.setValueAtTime(1, when);
  gain.gain.exponentialRampToValueAtTime(0.001, when + 0.15);
  osc.connect(gain).connect(audioCtx.destination);
  osc.start(when);
  osc.stop(when + 0.2);
}
```

Y un sonido corto para cada nota acertada, con un tono distinto por carril, de modo que el jugador "toque" una melodía:

```js
const NOTE_FREQ = [261.6, 329.6, 392.0, 523.3]; // Do, Mi, Sol, Do agudo

function pluck(lane) {
  const t = audioCtx.currentTime;
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = 'sawtooth';
  osc.frequency.value = NOTE_FREQ[lane];
  gain.gain.setValueAtTime(0.25, t);
  gain.gain.exponentialRampToValueAtTime(0.001, t + 0.3);
  osc.connect(gain).connect(audioCtx.destination);
  osc.start(t);
  osc.stop(t + 0.35);
}
```

Un detalle importante: los navegadores exigen un gesto del usuario antes de iniciar el audio. Por eso creamos el `AudioContext` dentro del clic del botón:

```js
document.getElementById('start').addEventListener('click', () => {
  audioCtx = new AudioContext();
  startTime = audioCtx.currentTime + 0.1;

  // Programamos 40 bombos por adelantado con precisión de audio
  for (let i = 0; i < 40; i++) {
    kick(startTime + (i * BEAT) / 1000);
  }
  requestAnimationFrame(loop);
});
```

Programar los bombos de golpe con `when` es la técnica estándar de Web Audio: el motor de audio los reproduce con precisión de muestra, sin depender del bucle de dibujo.

## Paso 5: el bucle de render

Las notas caen a velocidad constante. Su posición vertical depende solo de cuánto falta para su momento:

```js
const HIT_Y = 540;      // línea de impacto
const SPEED = 0.4;      // píxeles por milisegundo
const LANE_W = canvas.width / 4;

function noteY(note) {
  return HIT_Y - (note.time - songTime()) * SPEED;
}
```

Si `note.time` es igual a `songTime()`, la nota está exactamente en `HIT_Y`. Si falta un segundo, está 400 píxeles más arriba. No hay estado que actualizar: la posición es una función pura del tiempo, lo que elimina toda una clase de bugs de desincronización.

El dibujo:

```js
function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // carriles y línea de impacto
  LANES.forEach((_, i) => {
    ctx.fillStyle = i % 2 ? '#20203a' : '#1b1b2f';
    ctx.fillRect(i * LANE_W, 0, LANE_W, canvas.height);
  });
  ctx.fillStyle = '#fff';
  ctx.fillRect(0, HIT_Y - 2, canvas.width, 4);

  // notas
  for (const n of notes) {
    if (n.hit || n.missed) continue;
    const y = noteY(n);
    if (y < -30 || y > canvas.height + 30) continue;
    ctx.fillStyle = COLORS[n.lane];
    ctx.beginPath();
    ctx.arc(n.lane * LANE_W + LANE_W / 2, y, 22, 0, Math.PI * 2);
    ctx.fill();
  }

  // teclas
  ctx.font = '24px sans-serif';
  ctx.textAlign = 'center';
  LANES.forEach((k, i) => {
    ctx.fillStyle = COLORS[i];
    ctx.fillText(k.toUpperCase(), i * LANE_W + LANE_W / 2, HIT_Y + 50);
  });
}
```

## Paso 6: detectar aciertos y fallos

Aquí está el corazón del juego. Definimos ventanas de tolerancia en milisegundos:

```js
const WINDOW = { perfect: 50, good: 110 };

let score = 0, combo = 0;
let feedback = '', feedbackUntil = 0;

function multiplier() {
  return Math.min(4, 1 + Math.floor(combo / 10));
}
```

Cuando el jugador pulsa una tecla, buscamos la nota pendiente más cercana de ese carril y medimos la diferencia de tiempo:

```js
window.addEventListener('keydown', (e) => {
  if (!audioCtx || e.repeat) return;
  const lane = LANES.indexOf(e.key.toLowerCase());
  if (lane === -1) return;

  const now = songTime();
  let best = null, bestDelta = Infinity;

  for (const n of notes) {
    if (n.lane !== lane || n.hit || n.missed) continue;
    const delta = Math.abs(n.time - now);
    if (delta < bestDelta) { best = n; bestDelta = delta; }
  }

  if (best && bestDelta <= WINDOW.good) {
    best.hit = true;
    combo++;
    const perfect = bestDelta <= WINDOW.perfect;
    score += (perfect ? 100 : 50) * multiplier();
    feedback = perfect ? 'PERFECT' : 'GOOD';
    pluck(lane);
  } else {
    combo = 0;
    feedback = 'MISS';
  }
  feedbackUntil = performance.now() + 400;
  updateHud();
});
```

Fíjate en `e.repeat`: sin esa comprobación, mantener la tecla pulsada dispararía eventos repetidos y arruinaría el juicio.

Los fallos pasivos (notas que pasan sin que el jugador toque nada) se detectan en el bucle:

```js
function update() {
  const now = songTime();
  for (const n of notes) {
    if (!n.hit && !n.missed && now - n.time > WINDOW.good) {
      n.missed = true;
      combo = 0;
      feedback = 'MISS';
      feedbackUntil = performance.now() + 400;
      updateHud();
    }
  }
}

function updateHud() {
  scoreEl.textContent = score;
  comboEl.textContent = combo;
}

function loop() {
  update();
  draw();
  if (performance.now() < feedbackUntil) {
    ctx.fillStyle = '#fff';
    ctx.font = '32px sans-serif';
    ctx.fillText(feedback, canvas.width / 2, 300);
  }
  requestAnimationFrame(loop);
}
```

Con esto el juego ya funciona. Abre el archivo en el navegador, pulsa *Empezar* y toca al ritmo.

## Lecciones aprendidas

**1. El reloj lo manda el audio.** Todo lo que depende del tiempo (posición, aciertos, fallos) se deriva de `audioCtx.currentTime`. Es el cambio que más mejora la sensación del juego.

**2. Estado mínimo.** Las notas solo guardan `time`, `lane` y dos banderas. La posición se calcula, no se almacena. Menos estado, menos bugs.

**3. La latencia existe.** Cada dispositivo tiene un retraso entre pulsar y oír. En un juego serio se añade una pantalla de calibración que guarde un `offset` en `localStorage` y lo reste al `songTime()` en el `keydown`. Con una línea basta:

```js
const now = songTime() - calibrationOffset;
```

**4. Las ventanas de tolerancia son diseño, no matemáticas.** 50 ms y 110 ms son valores razonables, pero ajustarlos cambia por completo la dificultad. Prueba con valores distintos y juega.

## Ideas para seguir

- **Notas largas (sustain):** añade un campo `duration` y exige mantener la tecla.
- **Soporte táctil y gamepad:** cada carril puede ser una zona táctil, y la Gamepad API permite usar mandos reales.
- **Editor de charts:** una pantalla donde grabes tus pulsaciones mientras suena la música y exportes el JSON.
- **Música real:** carga un `.mp3` con `fetch` y `decodeAudioData`, y usa `source.start(startTime)` para que todo siga alineado al mismo reloj.
- **Efectos visuales:** partículas al acertar, flash en el carril y una barra de vida al estilo Rock Band.

## Cierre

Un juego rítmico es un excelente proyecto para aprender sobre tiempo, eventos y renderizado en el navegador. Con menos de 150 líneas tenemos un bucle de juego, una API de audio de baja latencia, detección de entrada y un sistema de puntuación.

Lo mejor es que la arquitectura escala: cambia el array de notas por un JSON, sustituye los osciladores por una pista real y tendrás la base de algo mucho más grande.

Si te animas a extenderlo, me encantaría ver tu versión en los comentarios. ¿Qué canción pondrías primero? 🎸
