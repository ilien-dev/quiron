# Ámbito léxico y de bloque en JavaScript

Entender el ámbito —o *scope*— es esencial para escribir JavaScript predecible. El ámbito determina en qué partes del programa puede utilizarse una variable, una función o una clase. También explica por qué algunos identificadores están disponibles dentro de una función, por qué otros desaparecen al terminar un bloque y cómo una función puede recordar valores del lugar donde fue creada.

En JavaScript conviven varios tipos de ámbito, pero dos conceptos resultan especialmente importantes: el **ámbito léxico** y el **ámbito de bloque**.

## ¿Qué significa “ámbito”?

Cuando JavaScript encuentra un identificador, necesita averiguar a qué declaración corresponde:

```js
const nombre = "Ada";

function saludar() {
  console.log(nombre);
}

saludar(); // Ada
```

La función `saludar` no declara una variable llamada `nombre`. Por eso, el motor busca ese identificador en un ámbito exterior y encuentra la constante global.

Los ámbitos forman una cadena. Si un identificador no existe en el ámbito actual, JavaScript continúa buscándolo hacia fuera. Si llega al final de la cadena sin encontrarlo, normalmente lanza un `ReferenceError`.

```js
function mostrarMensaje() {
  console.log(mensaje);
}

mostrarMensaje(); // ReferenceError: mensaje is not defined
```

Esta búsqueda solo avanza desde los ámbitos interiores hacia los exteriores. El código externo no puede acceder directamente a las variables privadas de una función:

```js
function crearMensaje() {
  const mensaje = "Hola";
}

console.log(mensaje); // ReferenceError
```

## Ámbito léxico

JavaScript utiliza ámbito léxico, también llamado ámbito estático. Esto significa que la accesibilidad de los identificadores se determina según la posición de las declaraciones en el código fuente.

Una función puede acceder a las variables que estaban visibles en el lugar donde fue definida:

```js
const idioma = "es";

function presentar() {
  const nombre = "Lin";

  function mostrar() {
    console.log(`${nombre} (${idioma})`);
  }

  mostrar();
}

presentar(); // Lin (es)
```

`mostrar` puede utilizar tanto `nombre`, declarado en `presentar`, como `idioma`, declarado en el ámbito global. La estructura del código establece esa relación.

Lo importante es que el lugar desde donde se invoca una función no cambia su ámbito léxico:

```js
const valor = "exterior";

function imprimir() {
  console.log(valor);
}

function ejecutar() {
  const valor = "interior";
  imprimir();
}

ejecutar(); // exterior
```

Aunque `imprimir` se ejecuta dentro de `ejecutar`, fue definida en el ámbito global. Por tanto, su referencia a `valor` se resuelve allí y no en el contexto de la llamada.

Esta regla hace que el comportamiento del programa pueda entenderse leyendo su estructura, sin tener que reconstruir dinámicamente quién llamó a cada función.

## Sombreado de variables

Un ámbito interior puede declarar un identificador con el mismo nombre que otro de un ámbito exterior. La declaración interior “sombrea” a la exterior:

```js
const estado = "global";

function comprobar() {
  const estado = "local";
  console.log(estado);
}

comprobar();        // local
console.log(estado); // global
```

Las dos constantes son distintas. Dentro de `comprobar`, la búsqueda encuentra primero la declaración local y deja de avanzar por la cadena de ámbitos.

El sombreado puede ser útil, pero abusar de él dificulta distinguir qué variable se está utilizando. En funciones complejas conviene elegir nombres más descriptivos.

## Ámbito de bloque

Un bloque es una sección delimitada por llaves, como las utilizadas en `if`, `for`, `while` o simplemente en un bloque independiente:

```js
{
  const mensaje = "Solo dentro del bloque";
  console.log(mensaje);
}

console.log(mensaje); // ReferenceError
```

Las declaraciones realizadas con `let` y `const` tienen ámbito de bloque. Solo están disponibles dentro del bloque en el que se declaran y en sus bloques descendientes.

```js
if (true) {
  let contador = 1;
  const limite = 10;

  console.log(contador, limite);
}

console.log(contador); // ReferenceError
console.log(limite);   // ReferenceError
```

Esto permite limitar la vida conceptual de una variable a la parte del programa que realmente la necesita.

Un caso habitual aparece en los bucles:

```js
for (let i = 0; i < 3; i++) {
  console.log(i);
}

console.log(i); // ReferenceError
```

Como `i` pertenece al ámbito del `for`, no contamina el ámbito exterior.

## La diferencia de `var`

`var` no tiene ámbito de bloque. Sus declaraciones quedan asociadas al ámbito de la función que las contiene o al ámbito global si están fuera de una función:

```js
if (true) {
  var disponible = "todavía visible";
}

console.log(disponible); // todavía visible
```

En una función, la variable sigue estando aislada del exterior, pero no del bloque:

```js
function ejemplo() {
  if (true) {
    var resultado = 42;
  }

  console.log(resultado); // 42
}

ejemplo();
```

Esta diferencia histórica puede producir errores, especialmente al crear funciones dentro de bucles:

```js
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}

// 3
// 3
// 3
```

Todas las funciones comparten la misma variable `i`. Cuando se ejecutan, el bucle ya terminó y su valor es `3`.

Con `let`, cada iteración recibe una vinculación diferente:

```js
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}

// 0
// 1
// 2
```

Por este y otros motivos, el JavaScript moderno suele preferir `const` y `let` sobre `var`.

## La zona muerta temporal

Las variables declaradas con `let` y `const` existen desde el comienzo de su bloque, pero no pueden utilizarse antes de que se ejecute su declaración. Ese intervalo se conoce como **zona muerta temporal**:

```js
{
  console.log(usuario); // ReferenceError
  const usuario = "Grace";
}
```

Esto es diferente de afirmar que la variable no existe. JavaScript ya reconoce que `usuario` pertenece al ámbito actual, pero todavía no permite acceder a ella.

La zona muerta temporal también influye cuando hay sombreado:

```js
const total = 100;

{
  console.log(total); // ReferenceError
  const total = 20;
}
```

La constante interior ya sombrea a la exterior desde el inicio del bloque, aunque aún no haya sido inicializada.

## Closures: cuando el ámbito sobrevive

El ámbito léxico permite crear *closures* o clausuras. Una función conserva acceso a las variables del entorno donde fue definida, incluso después de que la función exterior haya terminado:

```js
function crearContador() {
  let valor = 0;

  return function incrementar() {
    valor++;
    return valor;
  };
}

const contador = crearContador();

console.log(contador()); // 1
console.log(contador()); // 2
console.log(contador()); // 3
```

La función `incrementar` mantiene acceso a `valor`. Esa variable no es global ni puede modificarse directamente desde fuera, pero continúa existiendo mientras la función retornada pueda utilizarse.

Las clausuras son la base de muchos patrones de encapsulación, fábricas de funciones, manejadores de eventos y operaciones asíncronas.

## Buenas prácticas

Para aprovechar el ámbito de forma clara y segura:

- Usa `const` por defecto cuando la variable no deba reasignarse.
- Usa `let` cuando la reasignación sea necesaria.
- Evita `var` en código moderno, salvo que exista una razón concreta.
- Declara las variables en el ámbito más pequeño posible.
- Evita el sombreado cuando pueda generar confusión.
- Recuerda que una función resuelve identificadores según dónde fue definida, no dónde fue llamada.

El ámbito léxico describe cómo se conectan los entornos según la estructura del código. El ámbito de bloque, por su parte, permite controlar con precisión dónde viven las declaraciones realizadas con `let` y `const`. Juntos proporcionan las reglas necesarias para organizar datos, evitar colisiones y construir abstracciones mediante clausuras. Dominar estas reglas convierte muchos comportamientos aparentemente extraños de JavaScript en consecuencias previsibles de un modelo coherente.