Si llevas un tiempo escribiendo JavaScript, seguro que has recorrido un array con un `for`, has comprobado una condición y has ido metiendo elementos en otro array. Funciona, pero hay una forma más limpia y expresiva de hacerlo: `.filter()`.

## ¿Qué hace exactamente?

`.filter()` crea un **nuevo array** con los elementos que superan la prueba que tú definas. Recibe una función (el *callback*) que se ejecuta una vez por elemento: si devuelve un valor *truthy*, el elemento se queda; si no, se descarta.

```javascript
const numeros = [3, 8, 12, 5, 20];
const mayoresDeSiete = numeros.filter(n => n > 7);

console.log(mayoresDeSiete); // [8, 12, 20]
console.log(numeros);        // [3, 8, 12, 5, 20]
```

El array original queda intacto, y esa es la primera gran bondad.

## 1. No muta el array original

Muchos bugs difíciles de rastrear nacen de modificar datos compartidos. `.filter()` siempre devuelve un array nuevo, lo que encaja muy bien con React, Redux o cualquier enfoque donde la inmutabilidad importa. Por ejemplo, para eliminar un elemento del estado:

```javascript
const eliminarTarea = (tareas, id) => tareas.filter(t => t.id !== id);
```

Una línea, sin `splice`, sin índices y sin efectos secundarios.

Ojo: la copia es superficial. Los objetos del nuevo array son los mismos que los del original, así que si modificas uno, cambia en ambos.

## 2. Código declarativo

Compara estas dos versiones:

```javascript
// Imperativa
const activos = [];
for (let i = 0; i < usuarios.length; i++) {
  if (usuarios[i].activo) {
    activos.push(usuarios[i]);
  }
}

// Declarativa
const activos = usuarios.filter(u => u.activo);
```

La primera describe *cómo* hacerlo; la segunda dice *qué* quieres. Al leer `.filter()` ya sabes que el resultado es un subconjunto del original, sin tener que interpretar el cuerpo de un bucle.

## 3. Se encadena de maravilla

Como devuelve un array, puedes enlazarlo con `.map()`, `.sort()` o `.reduce()`:

```javascript
const total = productos
  .filter(p => p.enStock)
  .map(p => p.precio)
  .reduce((suma, precio) => suma + precio, 0);
```

Cada paso hace una sola cosa y el flujo se lee de arriba abajo.

## 4. Trucos útiles

**Eliminar valores falsy:**

```javascript
const limpio = [0, 'hola', null, 42, '', undefined].filter(Boolean);
// ['hola', 42]
```

Ten cuidado: también elimina el `0` y las cadenas vacías, que a veces son datos válidos.

**Quitar duplicados:**

```javascript
const unicos = lista.filter((item, i, arr) => arr.indexOf(item) === i);
```

El callback recibe tres argumentos: el elemento, su índice y el array completo. Para listas grandes, `[...new Set(lista)]` es más eficiente, pero el ejemplo ilustra bien el uso de esos parámetros.

**Búsquedas sencillas:**

```javascript
const resultados = articulos.filter(a =>
  a.titulo.toLowerCase().includes(busqueda.toLowerCase())
);
```

## 5. Predicados reutilizables

Si extraes las condiciones a funciones con nombre, el código gana en legibilidad y resulta más fácil de testear:

```javascript
const esMayorDeEdad = persona => persona.edad >= 18;
const tieneEmail = persona => Boolean(persona.email);

const contactables = personas.filter(esMayorDeEdad).filter(tieneEmail);
```

## Cuándo no usarlo

- **Si solo necesitas un elemento**, usa `.find()`, que se detiene en la primera coincidencia. `.filter()` recorre siempre todo el array.
- **Si solo quieres saber si existe alguno**, `.some()` es más adecuado que comprobar `.filter(...).length > 0`.
- **Si no vas a usar el array devuelto**, estás buscando `.forEach()`.
- **Con callbacks asíncronos no funciona como esperas**: una función `async` devuelve una promesa, que siempre es *truthy*, así que no se filtra nada. Resuelve primero con `Promise.all()` y filtra después.
- **En arrays enormes**, encadenar varios métodos implica varias pasadas y varios arrays intermedios. Casi nunca es un problema real, pero si lo mides y lo es, un único `reduce` o un bucle clásico siguen siendo opciones válidas.

## Conclusión

`.filter()` es uno de esos métodos que, una vez interiorizados, cambian tu forma de escribir código. Aporta inmutabilidad, legibilidad y composición a cambio de muy poco. No sustituye a todos los bucles, pero para seleccionar elementos según una condición suele ser la herramienta más clara.

¿Tienes algún truco favorito con `.filter()`? Cuéntamelo en los comentarios. 👇
