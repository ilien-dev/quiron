# Crea tu primer componente con Vue.js (para dummies)

Aprender un framework puede sentirse como llegar a una fiesta donde todos hablan en siglas. Escuchas “props”, “estado”, “reactividad” y “componentes”, mientras tú solo quieres poner un botón en pantalla y conseguir que haga algo.

Vamos a empezar precisamente por ahí.

En este tutorial crearás una tarjeta con un contador de aplausos. Tendrá un título, un mensaje y un botón que actualizará un número. Parece poca cosa, pero contiene varias ideas fundamentales de Vue.js.

No necesitas dominar JavaScript. Conocer un poco de HTML, CSS y variables será suficiente. Usaremos Vue 3 y la sintaxis `<script setup>`.

## ¿Qué es un componente?

Un componente es una pieza de interfaz que reúne su propia estructura, comportamiento y apariencia.

Piensa en una página de compras: tiene un buscador, tarjetas de productos, un carrito y botones. Cada una de esas partes puede construirse como un componente.

La ventaja aparece cuando necesitas repetir algo. En lugar de copiar el mismo HTML veinte veces, creas una pieza reutilizable y cambias los datos que recibe.

Para nuestro ejemplo, construiremos `TarjetaAplausos.vue`. Los archivos terminados en `.vue` pueden agrupar tres bloques:

- `<script setup>`: la lógica y los datos.
- `<template>`: el contenido que aparece en pantalla.
- `<style scoped>`: los estilos del componente.

No necesitas memorizarlo todavía. Vamos a verlo funcionando.

## Prepara un lugar para practicar

Para evitar instalaciones durante este primer ejercicio, puedes trabajar en el playground de Vue: [play.vuejs.org](https://play.vuejs.org/).

Encontrarás un editor y una vista previa. Puedes modificar el código y observar el resultado en el navegador.

Si ya tienes un proyecto con Vue 3, también puedes seguir el tutorial allí. Crea el archivo `TarjetaAplausos.vue` dentro de `src/components`.

En el playground, crea un archivo con ese mismo nombre. Después lo importaremos desde `App.vue`, que será el componente encargado de mostrar nuestra tarjeta.

Nuestro objetivo es sencillo: pulsar un botón y ver cómo aumenta el contador.

## Escribe tu primer componente

Pega este código en `TarjetaAplausos.vue`:

```vue
<script setup>
import { ref } from 'vue'

const aplausos = ref(0)

function aplaudir() {
  aplausos.value++
}
</script>

<template>
  <article class="tarjeta">
    <h2>¡Mi primer componente!</h2>

    <p>Estoy aprendiendo Vue paso a paso.</p>

    <button type="button" @click="aplaudir">
      👏 Aplaudir
    </button>

    <p aria-live="polite">
      Aplausos: {{ aplausos }}
    </p>
  </article>
</template>

<style scoped>
.tarjeta {
  max-width: 360px;
  padding: 24px;
  border: 1px solid #ddd;
  border-radius: 16px;
  font-family: sans-serif;
}

button {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  background: #42b883;
  color: #102a20;
  cursor: pointer;
}
</style>
```

Ya tienes la pieza completa. Ahora vamos a entenderla sin convertir esto en una clase de tres horas.

## La magia tiene nombre: reactividad

La primera línea importa `ref`, una función de Vue:

```js
import { ref } from 'vue'
```

Después creamos un valor reactivo:

```js
const aplausos = ref(0)
```

“Reactivo” significa que Vue puede detectar sus cambios y actualizar las partes de la interfaz que lo utilizan.

Comenzamos en cero. Cuando alguien pulsa el botón, ejecutamos:

```js
aplausos.value++
```

Ese `++` aumenta el número en uno.

Aquí hay un detalle importante: dentro de JavaScript usamos `.value` para acceder al contenido de este `ref`. Dentro del template, Vue lo desenvuelve automáticamente, así que escribimos directamente `aplausos`.

Puede parecer una pequeña rareza al principio. Con un poco de práctica, se vuelve natural.

## Conecta los datos con el HTML

En el template encontramos esta expresión:

```vue
<p>Aplausos: {{ aplausos }}</p>
```

Las dobles llaves permiten mostrar un valor como texto. Cuando cambia `aplausos`, Vue actualiza ese contenido.

No tienes que buscar el párrafo con `document.querySelector` ni cambiar su texto manualmente. Tú modificas el dato y Vue se encarga de reflejarlo.

El botón utiliza otra herramienta:

```vue
<button type="button" @click="aplaudir">
  👏 Aplaudir
</button>
```

`@click` escucha los clics y ejecuta la función `aplaudir`.

Piensa en esta secuencia: haces clic, cambia el contador y la pantalla muestra el nuevo número. Ese recorrido es el corazón de nuestro componente.

Además, `aria-live="polite"` ayuda a que los lectores de pantalla anuncien los cambios del contador sin interrumpir inmediatamente lo que estaban leyendo.

## Muéstralo desde App.vue

Crear un componente no hace que aparezca automáticamente. Necesitamos utilizarlo desde otro componente.

Abre `App.vue` y reemplaza su contenido por esto:

```vue
<script setup>
import TarjetaAplausos from './TarjetaAplausos.vue'
</script>

<template>
  <main>
    <h1>Mi primera página con Vue</h1>
    <TarjetaAplausos />
  </main>
</template>
```

Si estás trabajando en un proyecto y guardaste la tarjeta dentro de `src/components`, ajusta la importación:

```js
import TarjetaAplausos from './components/TarjetaAplausos.vue'
```

Dentro de `<script setup>`, importar el componente permite utilizarlo directamente en el template.

Ahora deberías ver la tarjeta. Pulsa el botón varias veces. Si el número aumenta, ya construiste tu primer componente interactivo.

## Dale personalidad con props

Nuestra tarjeta funciona, pero siempre muestra el mismo título. Para reutilizarla con diferentes textos, podemos recibir información mediante props.

Una prop es un dato que un componente recibe de su padre. En este caso, `App.vue` enviará el título a `TarjetaAplausos.vue`.

Agrega esto dentro del `<script setup>` de la tarjeta:

```js
defineProps({
  titulo: {
    type: String,
    default: '¡Mi primer componente!'
  }
})
```

`defineProps` está disponible dentro de `<script setup>` sin importarlo.

Después, reemplaza el encabezado fijo:

```vue
<h2>{{ titulo }}</h2>
```

Ahora puedes utilizar la tarjeta así desde `App.vue`:

```vue
<TarjetaAplausos titulo="Aprendiendo componentes" />
<TarjetaAplausos titulo="Mi siguiente proyecto" />
```

Cada tarjeta mostrará su título y mantendrá su propio contador. Aplaudir en una no cambiará el número de la otra.

Esto ocurre porque cada instancia del componente crea su propio `ref`. Comparten la misma definición, pero tienen datos independientes.

## Tres tropiezos completamente normales

Si algo falla, revisa primero estas posibilidades:

- **El contador no cambia:** comprueba que utilizaste `ref(0)` y que la función modifica `aplausos.value`.
- **La tarjeta no aparece:** revisa la ruta de importación y el nombre del archivo.
- **El título sale como texto literal:** para mostrar su valor necesitas `{{ titulo }}`, incluyendo las llaves.

También recuerda que `scoped` limita los estilos mediante selectores que Vue transforma. Es útil para evitar que el estilo de este botón termine afectando accidentalmente otros botones de la aplicación.

## Tu siguiente pequeño reto

Agrega un segundo botón que permita reiniciar el contador. Necesitarás una función que asigne cero a `aplausos.value` y un `@click` que la ejecute.

Después prueba a mostrar un mensaje cuando llegues a diez aplausos.

Ya tienes las herramientas para experimentar: datos reactivos, eventos, texto dinámico y props. Empieza cambiando una cosa cada vez, observa el resultado y sigue construyendo.
