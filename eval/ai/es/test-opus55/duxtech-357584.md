# Las bondades del método .filter() en JavaScript

Si llevas un tiempo escribiendo JavaScript, seguro que alguna vez has recorrido un array con un `for` para quedarte solo con algunos elementos. Funciona, sí, pero hay una forma más clara, más expresiva y menos propensa a errores: el método `.filter()`. En este post repasamos qué hace, por qué conviene usarlo y algunos trucos que te harán la vida más fácil.

## ¿Qué hace exactamente .filter()?

`.filter()` recorre un array y devuelve **un nuevo array** con los elementos que cumplen una condición. Esa condición la defines tú mediante una función (llamada *predicado*) que devuelve `true` o `false`.

```javascript
const numeros = [1, 2, 3, 4, 5, 6];
const pares = numeros.filter(n => n % 2 === 0);

console.log(pares); // [2, 4, 6]
```

Sin contadores, sin `push`, sin índices. Lees la línea y entiendes la intención: "quédate con los pares".

## Bondad #1: No muta el array original

Una de sus grandes virtudes es la **inmutabilidad**. `.filter()` nunca modifica el array sobre el que se llama; siempre crea uno nuevo.

```javascript
const frutas = ['manzana', 'pera', 'kiwi'];
const cortas = frutas.filter(f => f.length <= 4);

console.log(frutas); // ['manzana', 'pera', 'kiwi']
console.log(cortas); // ['pera', 'kiwi']
```

Esto es oro en aplicaciones con estado, como las hechas con React o Redux, donde mutar datos directamente puede provocar bugs difíciles de rastrear.

## Bondad #2: Código declarativo y legible

Compara estas dos versiones:

```javascript
// Imperativo
const activos = [];
for (let i = 0; i < usuarios.length; i++) {
  if (usuarios[i].activo) {
    activos.push(usuarios[i]);
  }
}

// Declarativo
const activos = usuarios.filter(u => u.activo);
```

La segunda dice *qué* quieres, no *cómo* conseguirlo. Menos líneas, menos ruido y menos oportunidades de equivocarte con un índice.

## Bondad #3: Se encadena de maravilla

Como devuelve un array, puedes combinarlo con `.map()`, `.reduce()`, `.sort()` y compañía:

```javascript
const pedidos = [
  { id: 1, total: 120, pagado: true },
  { id: 2, total: 45, pagado: false },
  { id: 3, total: 300, pagado: true },
];

const ingresos = pedidos
  .filter(p => p.pagado)
  .map(p => p.total)
  .reduce((acc, t) => acc + t, 0);

console.log(ingresos); // 420
```

Cada paso hace una sola cosa, y el flujo de datos se lee de arriba abajo como una receta.

## Bondad #4: Acceso al índice y al array completo

El callback recibe tres argumentos: el elemento, su índice y el array original. Esto abre la puerta a usos interesantes, como eliminar duplicados:

```javascript
const repetidos = [1, 2, 2, 3, 3, 3, 4];
const unicos = repetidos.filter((valor, i, arr) => arr.indexOf(valor) === i);

console.log(unicos); // [1, 2, 3, 4]
```

> Nota: para arrays grandes, `[...new Set(repetidos)]` es más eficiente, pero este ejemplo ilustra bien el potencial del tercer argumento.

## Bondad #5: Limpiar valores "falsy" en una línea

Un truco clásico: pasar `Boolean` como predicado para eliminar `null`, `undefined`, `0`, `''`, `NaN` y `false`.

```javascript
const datos = ['hola', '', null, 'mundo', undefined, 0];
const limpios = datos.filter(Boolean);

console.log(limpios); // ['hola', 'mundo']
```

Ojo: si el `0` es un valor válido en tu contexto, este atajo se lo llevará por delante. Úsalo con criterio.

## Bondad #6: Predicados reutilizables

Puedes extraer las condiciones a funciones con nombre y reutilizarlas en todo tu proyecto:

```javascript
const esMayorDeEdad = persona => persona.edad >= 18;
const tieneEmail = persona => Boolean(persona.email);

const contactables = personas
  .filter(esMayorDeEdad)
  .filter(tieneEmail);
```

Tu código empieza a parecerse al lenguaje natural, y probar cada predicado por separado es trivial.

## Algunas precauciones

- **Siempre recorre todo el array.** Si solo necesitas el primer elemento que cumpla la condición, usa `.find()`, que se detiene al encontrarlo.
- **Si solo quieres saber si existe alguno**, `.some()` es más adecuado.
- **Copia superficial:** el nuevo array contiene las *mismas referencias* a los objetos. Si modificas un objeto filtrado, también cambia en el original.

## Conclusión

`.filter()` es una de esas herramientas pequeñas que cambian la forma de escribir código. Aporta inmutabilidad, legibilidad, composición y expresividad, todo en un método que cabe en una línea. La próxima vez que estés a punto de escribir un `for` con un `if` y un `push` dentro, detente un segundo y pregúntate: ¿no sería esto un `.filter()`?

¿Tienes algún truco favorito con `.filter()`? ¡Déjalo en los comentarios! 👇

---

*Ronda las 650 palabras de prosa. Lo dejé con `published: false` en el front matter para que puedas revisarlo antes de publicarlo. Si quieres, lo guardo como archivo `.md`.*
