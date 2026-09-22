# Primera aplicación con Svelte y Tailwind

Últimamente se habla mucho de Svelte como alternativa a React, Vue o Angular, y con razón: en lugar de hacer la mayor parte del trabajo en tiempo de ejecución (como hacen los frameworks basados en Virtual DOM), Svelte mueve ese trabajo al momento de la compilación, generando código JavaScript optimizado que manipula el DOM directamente. El resultado son aplicaciones más pequeñas y rápidas. En este post vamos a crear una pequeña aplicación combinando Svelte con Tailwind CSS.

## Creando el proyecto

Empezamos creando un proyecto de Svelte con Vite, que es la forma recomendada actualmente:

```bash
npm create vite@latest mi-app-svelte -- --template svelte
cd mi-app-svelte
npm install
```

Esto genera una estructura de proyecto mínima con un componente `App.svelte` como punto de entrada.

## Instalando Tailwind

Instalamos Tailwind CSS junto con PostCSS y Autoprefixer:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Esto genera dos archivos: `tailwind.config.js` y `postcss.config.js`. En `tailwind.config.js`, configuramos las rutas donde Tailwind debe buscar clases usadas, para que el purgado de CSS no eliminado funcione correctamente:

```js
module.exports = {
  content: ['./index.html', './src/**/*.{svelte,js,ts}'],
  theme: {
    extend: {}
  },
  plugins: []
};
```

## Añadiendo las directivas de Tailwind

Creamos un archivo `src/app.css` con las directivas base:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Y lo importamos en `src/main.js`:

```js
import './app.css';
import App from './App.svelte';

const app = new App({
  target: document.getElementById('app')
});

export default app;
```

## Construyendo el componente principal

Ahora vamos a construir una pequeña lista de tareas (*todo list*) para poner en práctica tanto la reactividad de Svelte como las utilidades de Tailwind:

```svelte
<script>
  let tareas = [];
  let nuevaTarea = '';

  function agregarTarea() {
    if (nuevaTarea.trim() === '') return;
    tareas = [...tareas, { texto: nuevaTarea, completada: false }];
    nuevaTarea = '';
  }

  function alternarTarea(index) {
    tareas[index].completada = !tareas[index].completada;
    tareas = tareas;
  }
</script>

<div class="max-w-md mx-auto mt-10 p-6 bg-white rounded-lg shadow-md">
  <h1 class="text-2xl font-bold mb-4 text-gray-800">Mis tareas</h1>

  <div class="flex gap-2 mb-4">
    <input
      class="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      bind:value={nuevaTarea}
      placeholder="Nueva tarea..."
      on:keydown={(e) => e.key === 'Enter' && agregarTarea()}
    />
    <button
      class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
      on:click={agregarTarea}
    >
      Agregar
    </button>
  </div>

  <ul class="space-y-2">
    {#each tareas as tarea, index}
      <li
        class="flex items-center gap-2 p-2 border-b border-gray-100 cursor-pointer"
        on:click={() => alternarTarea(index)}
      >
        <span class:line-through={tarea.completada} class:text-gray-400={tarea.completada}>
          {tarea.texto}
        </span>
      </li>
    {/each}
  </ul>
</div>
```

Hay un par de detalles interesantes en este código que vale la pena resaltar.

## Reactividad de Svelte

A diferencia de React, donde tenemos que usar `useState` y una función `setState` explícita, en Svelte basta con reasignar una variable declarada con `let` para que el componente se vuelva a renderizar. Por eso, en `agregarTarea`, hacemos `tareas = [...tareas, ...]` en lugar de usar `tareas.push(...)`: Svelte detecta reactividad basándose en asignaciones, no en mutaciones, así que si solo hiciéramos `push`, la interfaz no se actualizaría automáticamente.

Por la misma razón, en `alternarTarea` mutamos `tareas[index].completada` directamente, pero luego forzamos la reactividad con la línea `tareas = tareas`, que técnicamente es una reasignación (aunque apunte al mismo array) y por tanto dispara la actualización de la interfaz.

## Bindings de dos vías

El atributo `bind:value` en el `<input>` crea un binding de dos vías entre el valor del input y la variable `nuevaTarea`: cuando el usuario escribe, la variable se actualiza automáticamente, sin necesidad de un manejador `onChange` como haríamos en React.

## Clases condicionales con class:

Svelte ofrece una sintaxis nativa para aplicar clases condicionalmente, sin necesidad de librerías como `clsx` o `classnames`:

```svelte
<span class:line-through={tarea.completada} class:text-gray-400={tarea.completada}>
```

Esto aplica las clases `line-through` y `text-gray-400` de Tailwind únicamente cuando `tarea.completada` es `true`, lo cual combina muy bien con el enfoque utility-first de Tailwind.

## Ejecutando la aplicación

```bash
npm run dev
```

Con esto deberíamos ver nuestra pequeña lista de tareas funcionando, con estilos de Tailwind aplicados y actualizaciones reactivas gracias a Svelte, todo con muy poco código comparado con lo que requeriría una implementación equivalente en otros frameworks.

## Conclusión

La combinación de Svelte y Tailwind resulta muy natural: Svelte se encarga de la lógica y la reactividad con una sintaxis mínima, mientras que Tailwind permite construir la interfaz visual rápidamente sin salir del archivo del componente. Si vienes de React o Vue, probablemente notes enseguida cuánto código de "plumbing" desaparece, y cuánto más cerca se siente el HTML resultante del HTML que escribirías a mano.
