# Crea tu primer componente con Vue.js (para dummies)

Si alguna vez has visto una aplicación web moderna y te has preguntado cómo consigue actualizar botones, textos o listas sin recargar toda la página, probablemente detrás haya un framework como Vue.js.

Vue es una herramienta para construir interfaces de usuario mediante piezas pequeñas y reutilizables llamadas **componentes**. La palabra puede sonar complicada, pero la idea es sencilla: un componente es como una pieza de LEGO. Puede tener su propio contenido, apariencia y comportamiento, y después combinarse con otras piezas para crear una aplicación completa.

En este tutorial construiremos nuestro primer componente con Vue 3. No necesitas experiencia previa con Vue, aunque ayuda conocer un poco de HTML, CSS y JavaScript.

## ¿Qué vamos a crear?

Vamos a construir una tarjeta de perfil que muestre:

- El nombre de una persona.
- Su profesión.
- Un pequeño mensaje.
- Un botón para seguirla.
- El número de seguidores.

Además, el componente será reutilizable. Eso significa que podremos mostrar varias tarjetas cambiando únicamente los datos.

## 1. Crear el proyecto

La forma recomendada de iniciar un proyecto moderno de Vue es con la herramienta oficial `create-vue`.

Abre una terminal y ejecuta:

```bash
npm create vue@latest
```

El asistente te pedirá un nombre para el proyecto y mostrará varias opciones. Para este ejemplo puedes llamarlo `mi-primer-vue` y responder `No` a las características adicionales.

Después, entra en la carpeta e instala las dependencias:

```bash
cd mi-primer-vue
npm install
npm run dev
```

La terminal mostrará una dirección parecida a esta:

```text
http://localhost:5173/
```

Ábrela en tu navegador. Si ves la página inicial de Vue, todo está funcionando.

> Necesitas tener Node.js instalado. Puedes comprobarlo ejecutando `node -v` en la terminal.

## 2. Entender la estructura básica

Dentro del proyecto encontrarás una carpeta llamada `src`. Ahí vivirá la mayor parte de nuestro código.

Los archivos más importantes son:

```text
src/
├── components/
├── App.vue
└── main.js
```

`main.js` inicia la aplicación. `App.vue` es el componente principal y `components` contiene los componentes pequeños que iremos creando.

Los archivos terminados en `.vue` se conocen como **Single-File Components**. Normalmente contienen tres secciones:

```vue
<script setup>
// Lógica de JavaScript
</script>

<template>
  <!-- Estructura HTML -->
</template>

<style scoped>
/* Estilos CSS */
</style>
```

No siempre necesitas las tres, pero esta separación ayuda a mantener organizado cada componente.

## 3. Crear nuestro componente

Dentro de `src/components`, crea un archivo llamado `ProfileCard.vue`.

Añade este código:

```vue
<script setup>
import { ref } from 'vue'

const followers = ref(120)
const isFollowing = ref(false)

function toggleFollow() {
  isFollowing.value = !isFollowing.value

  if (isFollowing.value) {
    followers.value++
  } else {
    followers.value--
  }
}
</script>

<template>
  <article class="profile-card">
    <div class="avatar">AV</div>

    <h2>Ana Vue</h2>
    <p class="job">Desarrolladora frontend</p>
    <p>Me gusta crear interfaces sencillas y aprender cosas nuevas.</p>

    <strong>{{ followers }} seguidores</strong>

    <button @click="toggleFollow">
      {{ isFollowing ? 'Dejar de seguir' : 'Seguir' }}
    </button>
  </article>
</template>

<style scoped>
.profile-card {
  width: 300px;
  padding: 24px;
  border: 1px solid #ddd;
  border-radius: 16px;
  font-family: Arial, sans-serif;
  text-align: center;
  box-shadow: 0 8px 24px rgb(0 0 0 / 10%);
}

.avatar {
  display: grid;
  width: 80px;
  height: 80px;
  margin: 0 auto;
  border-radius: 50%;
  color: white;
  background: #42b883;
  place-items: center;
  font-size: 24px;
  font-weight: bold;
}

.job {
  color: #666;
}

button {
  display: block;
  margin: 20px auto 0;
  padding: 10px 18px;
  border: 0;
  border-radius: 8px;
  color: white;
  background: #35495e;
  cursor: pointer;
}

button:hover {
  background: #42b883;
}
</style>
```

Ya tenemos un componente completo. Ahora veamos qué hace cada parte.

## 4. Añadir datos reactivos

En la sección `<script setup>` importamos `ref`:

```js
import { ref } from 'vue'
```

`ref` permite crear valores **reactivos**. Cuando un valor reactivo cambia, Vue actualiza automáticamente la parte correspondiente de la pantalla.

Creamos dos valores:

```js
const followers = ref(120)
const isFollowing = ref(false)
```

El primero guarda el número de seguidores. El segundo indica si estamos siguiendo a la persona.

La función `toggleFollow` cambia ambos valores cuando pulsamos el botón:

```js
function toggleFollow() {
  isFollowing.value = !isFollowing.value

  if (isFollowing.value) {
    followers.value++
  } else {
    followers.value--
  }
}
```

Dentro de JavaScript usamos `.value` para acceder al contenido de una referencia. En el HTML no hace falta escribirlo porque Vue se encarga de desempaquetar el valor.

## 5. Mostrar valores en el HTML

En el `<template>` encontramos esta línea:

```vue
<strong>{{ followers }} seguidores</strong>
```

Las dobles llaves se llaman **interpolación**. Sirven para insertar valores de JavaScript dentro del HTML.

También utilizamos una expresión condicional:

```vue
{{ isFollowing ? 'Dejar de seguir' : 'Seguir' }}
```

Si `isFollowing` es verdadero, el botón muestra “Dejar de seguir”. Si es falso, muestra “Seguir”.

Para escuchar el clic usamos `@click`:

```vue
<button @click="toggleFollow">
```

`@click` es la forma abreviada de `v-on:click`. Cuando el usuario pulsa el botón, Vue ejecuta nuestra función.

## 6. Usar el componente

Crear el componente no basta: tenemos que incluirlo en la aplicación.

Abre `src/App.vue`, elimina su contenido y escribe:

```vue
<script setup>
import ProfileCard from './components/ProfileCard.vue'
</script>

<template>
  <main>
    <h1>Personas interesantes</h1>
    <ProfileCard />
  </main>
</template>

<style scoped>
main {
  display: grid;
  min-height: 100vh;
  margin: 0;
  place-content: center;
  justify-items: center;
  gap: 24px;
}

h1 {
  font-family: Arial, sans-serif;
}
</style>
```

Primero importamos el archivo:

```js
import ProfileCard from './components/ProfileCard.vue'
```

Después lo usamos como si fuera una etiqueta HTML:

```vue
<ProfileCard />
```

Este es uno de los grandes beneficios de Vue: podemos inventar nuestras propias etiquetas y darles comportamiento.

## 7. Hacerlo reutilizable con props

Nuestro componente funciona, pero siempre muestra a Ana. Para cambiar sus datos desde fuera podemos utilizar **props**.

Modifica el `<script setup>` de `ProfileCard.vue`:

```vue
<script setup>
import { ref } from 'vue'

defineProps({
  name: {
    type: String,
    required: true
  },
  job: {
    type: String,
    default: 'Sin profesión'
  },
  bio: {
    type: String,
    default: 'Esta persona todavía no tiene biografía.'
  }
})

const followers = ref(120)
const isFollowing = ref(false)

function toggleFollow() {
  isFollowing.value = !isFollowing.value
  followers.value += isFollowing.value ? 1 : -1
}
</script>
```

Ahora sustituye los textos fijos del template:

```vue
<h2>{{ name }}</h2>
<p class="job">{{ job }}</p>
<p>{{ bio }}</p>
```

Finalmente, pasa los datos desde `App.vue`:

```vue
<ProfileCard
  name="Ana Vue"
  job="Desarrolladora frontend"
  bio="Me gusta crear interfaces sencillas y aprender cosas nuevas."
/>

<ProfileCard
  name="Carlos JavaScript"
  job="Profesor"
  bio="Explico programación sin palabras imposibles."
/>
```

Las props funcionan como los argumentos de una función: permiten utilizar la misma estructura con información diferente.

## ¿Qué hemos aprendido?

Con unas pocas líneas hemos creado un componente que tiene:

- Estructura propia mediante `<template>`.
- Lógica interactiva mediante `<script setup>`.
- Estilos aislados mediante `<style scoped>`.
- Estado reactivo con `ref`.
- Eventos con `@click`.
- Datos configurables mediante props.

Eso es, en esencia, trabajar con Vue. Una aplicación grande no es más que un conjunto de componentes que intercambian datos y reaccionan a las acciones del usuario.

A partir de aquí puedes experimentar: añade una imagen, permite cambiar la biografía, recibe el número inicial de seguidores como prop o cambia el color del botón cuando la persona ya está siendo seguida.

No necesitas memorizarlo todo. Empieza con componentes pequeños, rompe cosas y observa qué sucede. En Vue, como en casi toda la programación, la mejor forma de aprender es construir algo.