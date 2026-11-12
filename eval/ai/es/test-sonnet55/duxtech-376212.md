# ES6: Objetos Literales en JavaScript

Los objetos son el corazón de JavaScript. Casi todo lo que manejas en un programa, desde la configuración de una app hasta la respuesta de una API, termina siendo un objeto. Antes de ES6 (ES2015), escribir objetos literales era funcional pero repetitivo. Con ES6 el lenguaje nos regaló una sintaxis más corta, expresiva y potente. En este post repasamos las mejoras más importantes con ejemplos prácticos.

## 1. Propiedades abreviadas (shorthand)

Cuando el nombre de la variable coincide con el nombre de la propiedad, ya no necesitas repetirlo.

**Antes de ES6:**

```javascript
const nombre = "Ana";
const edad = 28;

const usuario = {
  nombre: nombre,
  edad: edad
};
```

**Con ES6:**

```javascript
const nombre = "Ana";
const edad = 28;

const usuario = { nombre, edad };

console.log(usuario); // { nombre: "Ana", edad: 28 }
```

Es especialmente útil al devolver objetos desde funciones:

```javascript
function crearPunto(x, y) {
  return { x, y };
}
```

## 2. Métodos abreviados

Definir métodos dentro de un objeto también se simplificó. Ya no hace falta la palabra `function`.

**Antes:**

```javascript
const calculadora = {
  sumar: function (a, b) {
    return a + b;
  }
};
```

**Ahora:**

```javascript
const calculadora = {
  sumar(a, b) {
    return a + b;
  },
  restar(a, b) {
    return a - b;
  }
};

console.log(calculadora.sumar(2, 3)); // 5
```

Además de ser más corta, esta sintaxis permite usar `super` dentro de los métodos, algo que no era posible con la forma antigua.

## 3. Nombres de propiedad computados

Quizá la mejora más interesante: puedes usar una expresión como nombre de propiedad envolviéndola entre corchetes `[]`.

Antes tenías que crear el objeto y luego asignar la propiedad dinámica:

```javascript
const clave = "color";
const coche = {};
coche[clave] = "rojo";
```

Con ES6 se hace directamente en el literal:

```javascript
const clave = "color";

const coche = {
  marca: "Toyota",
  [clave]: "rojo",
  ["año" + 2024]: true
};

console.log(coche);
// { marca: "Toyota", color: "rojo", año2024: true }
```

También funciona con métodos:

```javascript
const accion = "saludar";

const persona = {
  [accion]() {
    return "¡Hola!";
  }
};

console.log(persona.saludar()); // "¡Hola!"
```

Esto resulta muy útil para construir objetos a partir de datos dinámicos, como campos de formularios o claves de un diccionario.

## 4. Getters y setters

Aunque ya existían en ES5, se integran de forma natural con la sintaxis moderna y se combinan bien con los nombres computados.

```javascript
const cuenta = {
  _saldo: 100,

  get saldo() {
    return `$${this._saldo}`;
  },

  set saldo(valor) {
    if (valor < 0) {
      throw new Error("El saldo no puede ser negativo");
    }
    this._saldo = valor;
  }
};

console.log(cuenta.saldo); // "$100"
cuenta.saldo = 250;
console.log(cuenta.saldo); // "$250"
```

## 5. Spread en objetos

Estrictamente, el operador spread para objetos (`...`) llegó con ES2018, pero hoy es inseparable de los objetos literales modernos, así que merece mención. Permite copiar y combinar objetos de forma concisa.

```javascript
const base = { tema: "oscuro", idioma: "es" };
const extra = { idioma: "en", notificaciones: true };

const config = { ...base, ...extra };

console.log(config);
// { tema: "oscuro", idioma: "en", notificaciones: true }
```

Fíjate en que las propiedades posteriores sobrescriben a las anteriores. Es una forma excelente de crear copias superficiales sin mutar el original:

```javascript
const original = { a: 1, b: 2 };
const copia = { ...original, b: 99 };

console.log(original); // { a: 1, b: 2 }
console.log(copia);    // { a: 1, b: 99 }
```

Recuerda que la copia es **superficial**: los objetos anidados se siguen compartiendo por referencia.

## 6. Desestructuración: el complemento perfecto

Aunque no es exclusiva de los literales, la desestructuración de ES6 encaja a la perfección con ellos:

```javascript
const producto = { id: 7, nombre: "Teclado", precio: 45 };

const { nombre, precio } = producto;

console.log(nombre, precio); // "Teclado" 45
```

Puedes renombrar, asignar valores por defecto y recoger el resto de propiedades:

```javascript
const { nombre: titulo, stock = 0, ...resto } = producto;

console.log(titulo); // "Teclado"
console.log(stock);  // 0
console.log(resto);  // { id: 7, precio: 45 }
```

## 7. Un ejemplo que lo reúne todo

```javascript
function crearUsuario(nombre, rol, extras = {}) {
  const creadoEn = Date.now();
  const campoRol = `es${rol[0].toUpperCase()}${rol.slice(1)}`;

  return {
    nombre,
    creadoEn,
    [campoRol]: true,
    ...extras,
    describir() {
      return `${this.nombre} (${rol})`;
    }
  };
}

const admin = crearUsuario("Luis", "admin", { pais: "MX" });

console.log(admin.esAdmin);     // true
console.log(admin.describir()); // "Luis (admin)"
```

En pocas líneas usamos propiedades abreviadas, nombres computados, spread y métodos abreviados. El código resultante es corto y fácil de leer.

## Buenas prácticas

- **Usa shorthand siempre que puedas.** Reduce ruido y errores de tipeo.
- **No abuses de los nombres computados.** Si la clave es fija, escríbela directamente.
- **Prefiere spread para no mutar** objetos, especialmente en código con estado (React, Redux).
- **Ten presente la copia superficial.** Para estructuras anidadas considera `structuredClone()`.
- **Evita métodos abreviados cuando necesites `new`**: no son constructores y no pueden invocarse con `new`.

## Conclusión

Las mejoras de ES6 a los objetos literales parecen pequeñas por separado, pero juntas cambian por completo la forma de escribir JavaScript. Propiedades abreviadas, métodos concisos, claves computadas y, más tarde, el spread, hacen que el código sea más limpio y expresivo. Si todavía escribes `nombre: nombre` o asignas propiedades dinámicas en una segunda línea, ahora tienes herramientas mejores.

¿Cuál de estas características usas más en tu día a día? ¡Cuéntamelo en los comentarios!
