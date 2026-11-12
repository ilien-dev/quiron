# Primera aplicación con Svelte y Tailwind

Llevaba tiempo oyendo que Svelte es "el framework que desaparece" y que Tailwind te hace olvidarte de los archivos CSS. Este fin de semana los probé juntos construyendo algo pequeño: una lista de tareas. Te cuento cómo fue, por si es tu primera vez con ellos.

## Por qué esta combinación

**Svelte** compila tus componentes a JavaScript muy ligero en lugar de enviar un runtime pesado al navegador. Su sintaxis se parece a HTML, CSS y JS normales, así que la curva de aprendizaje es suave.

**Tailwind** te da clases utilitarias (`p-4`, `text-xl`, `rounded`) que aplicas directamente en el marcado. Al principio choca, pero enseguida notas que dejas de inventar nombres de clases.

## Crear el proyecto

Necesitas Node instalado. Después:

```bash
npx sv create mi-app
cd mi-app
npx sv add tailwindcss
npm install
npm run dev
```

El asistente `sv` te pregunta por opciones (TypeScript, linter, etc.). El comando `sv add tailwindcss` instala Tailwind y configura el plugin de Vite. Comprueba que tu `src/app.css` contiene:

```css
@import "tailwindcss";
```

y que ese CSS se importa en tu layout principal (`src/routes/+layout.svelte`). Con eso, ya puedes usar clases de Tailwind en cualquier componente.

## La lógica: estado reactivo

En Svelte 5 el estado se declara con la *rune* `$state`. Abre `src/routes/+page.svelte` y escribe:

```svelte
<script>
  let tareas = $state([]);
  let nueva = $state('');

  function agregar() {
    const texto = nueva.trim();
    if (!texto) return;
    tareas.push({ texto, hecha: false });
    nueva = '';
  }
</script>
```

Fíjate en que `tareas.push(...)` basta para actualizar la interfaz. No hay `setState` ni copias del array: Svelte hace reactivos los objetos y arrays de forma profunda.

## La interfaz con Tailwind

Debajo del `<script>` añade el marcado:

```svelte
<main class="mx-auto max-w-md p-6">
  <h1 class="mb-4 text-3xl font-bold text-orange-600">Mis tareas</h1>

  <form
    onsubmit={(e) => { e.preventDefault(); agregar(); }}
    class="flex gap-2"
  >
    <input
      bind:value={nueva}
      placeholder="¿Qué toca hoy?"
      class="flex-1 rounded border border-slate-300 px-3 py-2
             focus:outline-none focus:ring-2 focus:ring-orange-400"
    />
    <button
      class="rounded bg-orange-600 px-4 py-2 font-semibold text-white
             hover:bg-orange-700"
    >
      Añadir
    </button>
  </form>

  <ul class="mt-4 space-y-2">
    {#each tareas as tarea}
      <li class="flex items-center gap-2 rounded bg-slate-100 px-3 py-2">
        <input type="checkbox" bind:checked={tarea.hecha} />
        <span
          class:line-through={tarea.hecha}
          class:text-slate-400={tarea.hecha}
        >
          {tarea.texto}
        </span>
      </li>
    {/each}
  </ul>
</main>
```

Hay tres cosas de Svelte que merece la pena destacar:

- `bind:value` y `bind:checked` enlazan los campos con las variables en ambos sentidos, sin manejadores manuales.
- `{#each}` recorre la lista y se actualiza solo cuando cambia.
- `class:nombre={condición}` activa una clase según el estado. Aquí tacha la tarea cuando está hecha.

Con Tailwind, el diseño responsivo, los estados `hover:` y `focus:` y el espaciado salen directamente de las clases, sin tocar una hoja de estilos.

## Lo que me gustó (y lo que no)

**Lo bueno:**

- Muy poco código para lograr interactividad. El componente entero cabe en una pantalla.
- Tailwind y los componentes de Svelte se complementan bien: el estilo vive junto al marcado y no hay que saltar entre archivos.
- El servidor de desarrollo es rapidísimo.

**Lo mejorable:**

- Las líneas de clases se alargan. Si algo se repite mucho, conviene extraerlo a un componente (por ejemplo, un `<Boton>`), no a CSS aparte.
- Si vienes de Svelte 4, las runes (`$state`, `$derived`) requieren un pequeño cambio de chip, y parte de los tutoriales antiguos ya no aplican.

## Siguientes pasos

Si quieres seguir practicando con esta app, prueba a:

1. Guardar las tareas en `localStorage`.
2. Añadir un botón para borrar tareas.
3. Calcular cuántas quedan pendientes con `$derived`.
4. Implementar un modo oscuro con la variante `dark:` de Tailwind.

Mi impresión es que Svelte y Tailwind forman una pareja muy cómoda para empezar: poco ceremonial, resultados rápidos y un código que se lee bien. ¿Y tú, qué tal tu primera experiencia con ellos? Cuéntamelo en los comentarios.
