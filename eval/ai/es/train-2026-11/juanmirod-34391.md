# Ámbito léxico y de bloque en JavaScript

Una variable puede existir en tu programa y, aun así, no estar disponible donde intentas usarla. Para entender por qué, necesitas conocer el ámbito: las reglas que determinan desde qué partes del código puedes acceder a una declaración.

En JavaScript, dos conceptos ayudan a explicar este comportamiento: el ámbito léxico y el ámbito de bloque. Están relacionados, pero describen aspectos diferentes. El primero explica cómo se resuelven los nombres según la ubicación del código. El segundo establece una frontera de visibilidad para ciertas declaraciones.

Vamos a entenderlos con ejemplos y algunas situaciones que aparecen al escribir aplicaciones.

**El ámbito léxico: importa dónde escribes el código**

JavaScript utiliza ámbito léxico. Esto significa que el acceso a una variable depende de dónde está escrita una función, no de dónde se ejecuta.

Considera este ejemplo:

```javascript
const nombre = "Ana";

function saludar() {
  console.log(nombre);
}

function ejecutar() {
  const nombre = "Luis";
  saludar();
}

ejecutar(); // Ana
```

Aunque `saludar()` se invoca dentro de `ejecutar()`, no utiliza su variable `nombre`. La función fue definida en un entorno exterior y busca el identificador siguiendo esa estructura.

Si JavaScript resolviera los nombres según la cadena de llamadas, encontraría `"Luis"`. Pero ese sería otro modelo, llamado ámbito dinámico.

La regla práctica es sencilla: para entender qué variable utiliza una función, observa dónde fue definida.

**La cadena de ámbitos**

Cuando JavaScript encuentra un identificador, comienza buscándolo en el ámbito actual. Si no encuentra una declaración, continúa hacia los ámbitos exteriores hasta llegar al global.

```javascript
const idioma = "es";

function crearMensaje() {
  const saludo = "Hola";

  function mostrar() {
    const nombre = "Marta";
    console.log(`${saludo}, ${nombre} (${idioma})`);
  }

  mostrar();
}
```

Dentro de `mostrar()`, las tres variables son accesibles, aunque pertenecen a entornos diferentes.

La búsqueda funciona hacia afuera. El código exterior no puede acceder automáticamente a las variables de una función interior. Por ejemplo, intentar utilizar `nombre` desde fuera de `mostrar()` produciría un `ReferenceError`, salvo que existiera otra declaración accesible con ese nombre.

Esta estructura permite razonar sobre las dependencias de una función leyendo el código que la rodea.

**El ámbito de bloque: una frontera entre llaves**

Un bloque agrupa instrucciones entre llaves. Lo encuentras en condicionales, bucles o simplemente como un bloque independiente.

Las variables declaradas con `let` y `const` tienen ámbito de bloque:

```javascript
if (true) {
  let intentos = 3;
  const limite = 5;

  console.log(intentos, limite);
}

console.log(intentos); // ReferenceError
```

Ambas declaraciones quedan restringidas al bloque donde aparecen. Esto permite mantener variables temporales cerca del lugar que las necesita y evita que otros fragmentos del programa dependan accidentalmente de ellas.

El ámbito de bloque forma parte de la estructura léxica del programa. Por eso, ambos conceptos se complementan.

**Por qué `var` se comporta diferente**

Una declaración con `var` pertenece al ámbito de la función que la contiene, o al entorno superior correspondiente si aparece fuera de una función. Un bloque ordinario no limita su visibilidad.

```javascript
function comprobar() {
  if (true) {
    var resultado = "correcto";
  }

  console.log(resultado); // correcto
}
```

Si reemplazas `var` por `let`, la última instrucción falla porque `resultado` queda dentro del condicional.

Esta diferencia explica muchos errores en código antiguo: unas llaves pueden parecer una frontera para una variable sin serlo realmente.

Como criterio habitual, utiliza `const` cuando no necesites reasignar y `let` cuando sí. Reserva `var` para situaciones donde necesites comprender o mantener su comportamiento específico.

**Sombreado: mismo nombre, distinta variable**

Dos ámbitos anidados pueden contener declaraciones con el mismo nombre. La más cercana oculta temporalmente a la exterior. Este comportamiento se llama sombreado.

```javascript
const color = "azul";

{
  const color = "verde";
  console.log(color); // verde
}

console.log(color); // azul
```

La declaración interior no modifica la exterior. Son dos variables distintas.

El sombreado puede resultar útil, pero repetir nombres en varios niveles dificulta seguir el código. Si necesitas detenerte constantemente para identificar qué `color` estás utilizando, probablemente convenga elegir nombres más específicos.

**La zona muerta temporal**

Las variables declaradas con `let` y `const` no pueden utilizarse antes de que su declaración se ejecute. El intervalo entre la entrada al ámbito y su inicialización se conoce como zona muerta temporal.

```javascript
const cantidad = 10;

{
  console.log(cantidad); // ReferenceError
  const cantidad = 20;
}
```

Este ejemplo puede sorprender. JavaScript no recurre a la variable exterior: la declaración interior ya determina qué identificador corresponde a ese bloque, pero todavía no está inicializado.

Por eso, explicar este comportamiento diciendo que estas variables «no tienen hoisting» puede resultar engañoso. Lo importante es que su acceso está restringido hasta la inicialización.

**Closures: conservar el acceso al entorno**

Una función puede seguir accediendo a variables de su entorno léxico después de que termine la ejecución de la función exterior. Esa combinación de función y entorno se denomina closure.

```javascript
function crearContador() {
  let valor = 0;

  return function incrementar() {
    valor += 1;
    return valor;
  };
}

const contador = crearContador();

console.log(contador()); // 1
console.log(contador()); // 2
```

La función devuelta conserva acceso a `valor`. Cada llamada a `crearContador()` genera un entorno independiente, por lo que puedes construir varios contadores sin compartir accidentalmente su estado.

Este patrón aparece en callbacks, manejadores de eventos y funciones que encapsulan información.

**Un detalle útil en los bucles**

En un bucle `for`, declarar el contador con `let` permite que cada iteración tenga su propia vinculación:

```javascript
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
// 0, 1, 2
```

Con `var`, los callbacks compartirían una sola variable y mostrarían `3` tres veces.

Cuando una variable te sorprenda, identifica su declaración, localiza el ámbito que la contiene y recorre los entornos exteriores. Esa lectura suele convertir un comportamiento aparentemente extraño en una consecuencia predecible de las reglas del lenguaje.
