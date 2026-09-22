# Las bondades del método .filter() en JavaScript

Si trabajas con arrays en JavaScript (y seguramente lo haces a diario), hay un método que tarde o temprano se convierte en uno de tus mejores amigos: `.filter()`. En este post vamos a ver cómo funciona, por qué es mejor que un bucle tradicional en muchos casos y algunos trucos para sacarle el máximo partido.

## ¿Qué hace .filter()?

El método `.filter()` crea un **nuevo array** con todos los elementos del array original que cumplan una condición. Esa condición la defines tú mediante una función que devuelve `true` (el elemento se queda) o `false` (el elemento se descarta).

Su sintaxis es:

```javascript
const nuevoArray = array.filter((elemento, indice, arrayOriginal) => {
  // devuelve true o false
});
```

En la práctica, casi siempre usarás solo el primer parámetro.

## Un ejemplo sencillo

Supongamos que tenemos una lista de números y queremos quedarnos solo con los pares:

```javascript
const numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

const pares = numeros.filter((n) => n % 2 === 0);

console.log(pares); // [2, 4, 6, 8, 10]
```

Compáralo con la versión usando un bucle `for`:

```javascript
const pares = [];
for (let i = 0; i < numeros.length; i++) {
  if (numeros[i] % 2 === 0) {
    pares.push(numeros[i]);
  }
}
```

Hacen lo mismo, pero la versión con `.filter()` es más corta, más legible y expresa directamente la intención: "filtra los números pares".

## Bondad 1: no modifica el array original

`.filter()` es un método **inmutable**. El array original queda intacto:

```javascript
const frutas = ['manzana', 'pera', 'plátano', 'kiwi'];
const cortas = frutas.filter((f) => f.length <= 4);

console.log(cortas); // ['pera', 'kiwi']
console.log(frutas); // ['manzana', 'pera', 'plátano', 'kiwi']
```

Esto es muy importante en frameworks como React, donde modificar el estado directamente puede provocar errores difíciles de rastrear.

## Bondad 2: funciona genial con objetos

El caso de uso más habitual en el mundo real es filtrar arrays de objetos:

```javascript
const usuarios = [
  { nombre: 'Ana', edad: 28, activo: true },
  { nombre: 'Luis', edad: 17, activo: true },
  { nombre: 'Marta', edad: 35, activo: false },
  { nombre: 'Pedro', edad: 42, activo: true },
];

const adultosActivos = usuarios.filter((u) => u.edad >= 18 && u.activo);

console.log(adultosActivos);
// [{ nombre: 'Ana', ... }, { nombre: 'Pedro', ... }]
```

## Bondad 3: se encadena con otros métodos

Como `.filter()` devuelve un array, puedes encadenarlo con `.map()`, `.reduce()`, `.sort()` y compañía:

```javascript
const nombres = usuarios
  .filter((u) => u.activo)
  .map((u) => u.nombre.toUpperCase());

console.log(nombres); // ['ANA', 'LUIS', 'PEDRO']
```

Este estilo declarativo hace que el código se lea casi como una frase.

## Trucos útiles

### Eliminar valores "falsy"

```javascript
const datos = [0, 'hola', '', null, 42, undefined, false, 'mundo'];
const limpios = datos.filter(Boolean);

console.log(limpios); // ['hola', 42, 'mundo']
```

### Eliminar duplicados

```javascript
const repetidos = [1, 2, 2, 3, 4, 4, 5];
const unicos = repetidos.filter((valor, i, arr) => arr.indexOf(valor) === i);

console.log(unicos); // [1, 2, 3, 4, 5]
```

(Aunque para arrays grandes, `[...new Set(repetidos)]` es más eficiente).

### Buscador simple

```javascript
const buscar = (lista, texto) =>
  lista.filter((item) => item.toLowerCase().includes(texto.toLowerCase()));

buscar(['JavaScript', 'Java', 'Python', 'TypeScript'], 'script');
// ['JavaScript', 'TypeScript']
```

## Cuándo no usar .filter()

Si solo necesitas **un** elemento, usa `.find()`, que se detiene en la primera coincidencia. Y si solo quieres saber si **existe** alguno, usa `.some()`. Usar `.filter()` en esos casos recorre el array completo innecesariamente.

## Conclusión

`.filter()` es uno de esos métodos que, una vez que lo incorporas, cambia tu forma de escribir código. Es inmutable, legible, se combina con otros métodos y cubre una gran cantidad de casos de uso con una sola línea. Si todavía filtras con bucles `for`, ¡dale una oportunidad!
