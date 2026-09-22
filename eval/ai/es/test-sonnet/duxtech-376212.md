# ES6: Objetos Literales en JavaScript

ECMAScript 6 (ES2015) trajo consigo una serie de mejoras a la sintaxis de los objetos literales en JavaScript que, aunque pequeñas individualmente, en conjunto hacen que el código sea mucho más limpio y expresivo. En este post repasamos las principales.

## Shorthand de propiedades

Antes de ES6, si queríamos crear un objeto cuyas propiedades tuvieran el mismo nombre que las variables usadas para asignarlas, teníamos que repetir el nombre dos veces:

```js
const nombre = 'Ana';
const edad = 28;

const usuario = {
  nombre: nombre,
  edad: edad
};
```

Con ES6, si el nombre de la propiedad coincide con el de la variable, podemos omitir la repetición:

```js
const nombre = 'Ana';
const edad = 28;

const usuario = { nombre, edad };
```

Esto no solo reduce la cantidad de código, sino que también reduce la probabilidad de errores al renombrar variables, ya que hay menos texto duplicado que mantener sincronizado.

## Shorthand de métodos

De forma similar, antes teníamos que escribir explícitamente la palabra clave `function` para definir métodos dentro de un objeto:

```js
const calculadora = {
  sumar: function(a, b) {
    return a + b;
  }
};
```

Con ES6, podemos omitirla:

```js
const calculadora = {
  sumar(a, b) {
    return a + b;
  }
};
```

Esto se aplica también a generadores, usando el asterisco:

```js
const iterable = {
  *generar() {
    yield 1;
    yield 2;
    yield 3;
  }
};
```

## Nombres de propiedades computados

Antes de ES6, si el nombre de una propiedad debía calcularse dinámicamente, había que crear primero el objeto y luego asignar la propiedad usando notación de corchetes:

```js
const clave = 'color';
const obj = {};
obj[clave] = 'rojo';
```

Con ES6, se puede hacer directamente dentro del literal usando corchetes:

```js
const clave = 'color';
const obj = {
  [clave]: 'rojo'
};
```

Esto es especialmente útil combinado con template literals, por ejemplo para generar claves dinámicas basadas en un prefijo:

```js
const id = 42;
const obj = {
  [`usuario_${id}`]: { nombre: 'Ana' }
};
// { usuario_42: { nombre: 'Ana' } }
```

## Spread operator en objetos

Aunque técnicamente el spread operator (`...`) en objetos literales llegó formalmente con ES2018 y no con ES6/ES2015, se suele mencionar junto al resto de mejoras de objetos literales porque sigue el mismo espíritu. Permite copiar las propiedades de un objeto en otro de forma muy concisa:

```js
const base = { a: 1, b: 2 };
const extendido = { ...base, c: 3 };
// { a: 1, b: 2, c: 3 }
```

También es muy útil para crear copias inmutables al actualizar el estado, un patrón muy común en librerías como React:

```js
const estadoActualizado = {
  ...estadoAnterior,
  cargando: false
};
```

## Desestructuración de objetos

Aunque no es estrictamente parte de la sintaxis de "objetos literales", la desestructuración es el complemento natural de estas mejoras, y también llegó con ES6:

```js
const usuario = { nombre: 'Ana', edad: 28, ciudad: 'Madrid' };
const { nombre, edad } = usuario;

console.log(nombre); // Ana
console.log(edad); // 28
```

Se puede renombrar la variable resultante y asignar valores por defecto:

```js
const { nombre: nombreUsuario, pais = 'España' } = usuario;
```

Y combinarla con el resto de propiedades usando spread:

```js
const { nombre, ...resto } = usuario;
// resto = { edad: 28, ciudad: 'Madrid' }
```

## Un ejemplo combinando todo

Para ver el poder de estas mejoras juntas, veamos una función que construye un objeto de configuración combinando varias técnicas:

```js
function crearConfiguracion(entorno, opciones = {}) {
  const timestamp = Date.now();

  return {
    entorno,
    timestamp,
    [`config_${entorno}`]: true,
    ...opciones,
    validar() {
      return this.entorno !== undefined;
    }
  };
}

const config = crearConfiguracion('produccion', { debug: false });
console.log(config);
```

En pocas líneas estamos usando shorthand de propiedades (`entorno`, `timestamp`), un nombre de propiedad computado (`[\`config_${entorno}\`]`), spread para mezclar opciones adicionales, y shorthand de método (`validar()`). Antes de ES6, este mismo código habría requerido bastantes más líneas y repeticiones innecesarias.

## Conclusión

Ninguna de estas características cambia radicalmente lo que se puede hacer con objetos en JavaScript —todo esto era posible antes de ES6, solo que con más código—, pero sí cambian radicalmente la legibilidad y la ergonomía del lenguaje. Si todavía escribes objetos literales a la manera antigua, vale la pena revisar tu código y aprovechar estas mejoras: además de escribir menos, el código resultante suele ser más fácil de leer y de mantener.
