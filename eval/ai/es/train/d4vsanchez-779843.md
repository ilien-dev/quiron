# Convertir un array de objetos a un objeto usando TypeScript

Trabajar con datos en forma de arrays es habitual en JavaScript y TypeScript. Una API, por ejemplo, puede devolver una lista de usuarios:

```ts
const usuarios = [
  { id: 1, nombre: "Ana", activo: true },
  { id: 2, nombre: "Luis", activo: false },
  { id: 3, nombre: "Marta", activo: true }
];
```

Esta estructura es cómoda para recorrer, filtrar u ordenar elementos. Sin embargo, si necesitamos buscar usuarios repetidamente por su identificador, recorrer todo el array con `find()` en cada consulta no es lo ideal:

```ts
const usuario = usuarios.find((item) => item.id === 2);
```

Una alternativa consiste en convertir el array en un objeto indexado por `id`:

```ts
const usuariosPorId = {
  1: { id: 1, nombre: "Ana", activo: true },
  2: { id: 2, nombre: "Luis", activo: false },
  3: { id: 3, nombre: "Marta", activo: true }
};
```

Ahora podemos acceder directamente al usuario:

```ts
const usuario = usuariosPorId[2];
```

Veamos distintas maneras de realizar esta transformación aprovechando el sistema de tipos de TypeScript.

## Usar `reduce()`

La solución más conocida utiliza `Array.prototype.reduce()`. Este método recorre el array y construye un único valor acumulado:

```ts
type Usuario = {
  id: number;
  nombre: string;
  activo: boolean;
};

const usuarios: Usuario[] = [
  { id: 1, nombre: "Ana", activo: true },
  { id: 2, nombre: "Luis", activo: false },
  { id: 3, nombre: "Marta", activo: true }
];

const usuariosPorId = usuarios.reduce<Record<number, Usuario>>(
  (acumulador, usuario) => {
    acumulador[usuario.id] = usuario;
    return acumulador;
  },
  {}
);
```

El tipo resultante es `Record<number, Usuario>`. `Record` es un tipo de utilidad de TypeScript que describe un objeto cuyas claves pertenecen a un tipo determinado y cuyos valores pertenecen a otro:

```ts
Record<TipoDeClave, TipoDeValor>
```

En nuestro ejemplo, las claves son números y los valores son usuarios.

El objeto vacío pasado como segundo argumento de `reduce()` es el valor inicial del acumulador. Indicar explícitamente el genérico `Record<number, Usuario>` evita que TypeScript infiera el acumulador simplemente como `{}`, lo que produciría errores al intentar asignar propiedades dinámicas.

También podemos escribir la transformación sin mutar el acumulador:

```ts
const usuariosPorId = usuarios.reduce<Record<number, Usuario>>(
  (acumulador, usuario) => ({
    ...acumulador,
    [usuario.id]: usuario
  }),
  {}
);
```

Aunque esta versión resulta expresiva, crea un objeto nuevo en cada iteración. En colecciones grandes puede ser considerablemente menos eficiente que modificar el acumulador existente. Dentro de un `reduce()`, la mutación local y controlada suele ser una opción práctica.

## Usar `Object.fromEntries()`

Otra solución concisa consiste en combinar `map()` con `Object.fromEntries()`:

```ts
const usuariosPorId = Object.fromEntries(
  usuarios.map((usuario) => [usuario.id, usuario])
);
```

Primero transformamos cada usuario en una pareja formada por clave y valor:

```ts
[
  [1, { id: 1, nombre: "Ana", activo: true }],
  [2, { id: 2, nombre: "Luis", activo: false }],
  [3, { id: 3, nombre: "Marta", activo: true }]
]
```

Después, `Object.fromEntries()` convierte esas parejas en propiedades de un objeto.

Podemos mejorar la inferencia de cada entrada mediante `as const`:

```ts
const usuariosPorId = Object.fromEntries(
  usuarios.map((usuario) => [usuario.id, usuario] as const)
);
```

Dependiendo de la versión de TypeScript y del contexto, quizá queramos declarar explícitamente el tipo final:

```ts
const usuariosPorId: Record<number, Usuario> = Object.fromEntries(
  usuarios.map((usuario) => [usuario.id, usuario] as const)
);
```

Esta alternativa es especialmente legible cuando la transformación de cada elemento a una pareja clave-valor es sencilla. `reduce()`, en cambio, ofrece más flexibilidad si necesitamos validaciones, agrupaciones u otras operaciones durante el recorrido.

## Crear una función genérica reutilizable

Si hacemos esta conversión con frecuencia, podemos encapsularla en una función. Una primera versión podría recibir una función que obtenga la clave de cada elemento:

```ts
function indexarPor<T, K extends PropertyKey>(
  elementos: T[],
  obtenerClave: (elemento: T) => K
): Record<K, T> {
  return elementos.reduce(
    (resultado, elemento) => {
      resultado[obtenerClave(elemento)] = elemento;
      return resultado;
    },
    {} as Record<K, T>
  );
}
```

`T` representa el tipo de los elementos y `K` representa el tipo de sus claves. La restricción `K extends PropertyKey` garantiza que la función únicamente acepte valores válidos como claves de objeto: `string`, `number` o `symbol`.

Podemos usarla así:

```ts
const usuariosPorId = indexarPor(usuarios, (usuario) => usuario.id);
const usuariosPorNombre = indexarPor(
  usuarios,
  (usuario) => usuario.nombre
);
```

TypeScript infiere los resultados:

```ts
// Record<number, Usuario>
usuariosPorId;

// Record<string, Usuario>
usuariosPorNombre;
```

Otra variante permite indicar directamente el nombre de una propiedad:

```ts
function indexarPorPropiedad<
  T,
  K extends keyof T
>(
  elementos: T[],
  propiedad: K
): Record<PropertyKey, T> {
  return elementos.reduce<Record<PropertyKey, T>>(
    (resultado, elemento) => {
      const clave = elemento[propiedad];

      if (
        typeof clave !== "string" &&
        typeof clave !== "number" &&
        typeof clave !== "symbol"
      ) {
        throw new Error("La propiedad no contiene una clave válida");
      }

      resultado[clave] = elemento;
      return resultado;
    },
    {}
  );
}

const usuariosPorId = indexarPorPropiedad(usuarios, "id");
```

La versión basada en una función selectora suele ser más flexible y mantiene tipos más precisos. También permite generar una clave que no exista directamente como propiedad:

```ts
const usuariosPorClave = indexarPor(
  usuarios,
  (usuario) => `usuario-${usuario.id}`
);
```

## ¿Qué ocurre con las claves duplicadas?

Al convertir un array en un objeto, cada clave solo puede almacenar un valor. Si dos elementos generan la misma clave, el último sobrescribirá al anterior:

```ts
const productos = [
  { codigo: "A1", precio: 10 },
  { codigo: "A1", precio: 15 }
];

const productosPorCodigo = indexarPor(
  productos,
  (producto) => producto.codigo
);

console.log(productosPorCodigo.A1.precio); // 15
```

Este comportamiento puede ser correcto si deseamos conservar la versión más reciente. Si los duplicados representan un error, conviene detectarlos:

```ts
function indexarSinDuplicados<T, K extends PropertyKey>(
  elementos: T[],
  obtenerClave: (elemento: T) => K
): Record<K, T> {
  return elementos.reduce(
    (resultado, elemento) => {
      const clave = obtenerClave(elemento);

      if (Object.hasOwn(resultado, clave)) {
        throw new Error(`Clave duplicada: ${String(clave)}`);
      }

      resultado[clave] = elemento;
      return resultado;
    },
    {} as Record<K, T>
  );
}
```

Si queremos conservar todos los elementos con la misma clave, entonces no estamos indexando, sino agrupando. En ese caso, los valores deben ser arrays:

```ts
function agruparPor<T, K extends PropertyKey>(
  elementos: T[],
  obtenerClave: (elemento: T) => K
): Partial<Record<K, T[]>> {
  return elementos.reduce<Partial<Record<K, T[]>>>(
    (grupos, elemento) => {
      const clave = obtenerClave(elemento);
      (grupos[clave] ??= []).push(elemento);
      return grupos;
    },
    {}
  );
}

const usuariosPorEstado = agruparPor(
  usuarios,
  (usuario) => String(usuario.activo)
);
```

Usamos `Partial` porque no podemos garantizar que el resultado contenga todas las claves posibles.

## Una precisión importante sobre `Record`

El tipo `Record<number, Usuario>` puede resultar engañoso. En JavaScript, las claves numéricas de objetos se convierten internamente en cadenas:

```ts
const objeto = {
  1: "uno"
};

console.log(Object.keys(objeto)); // ["1"]
```

Además, `Record<K, T>` afirma que cualquier clave de tipo `K` contiene un valor. Sin embargo, acceder a un identificador inexistente devuelve `undefined`:

```ts
const usuario = usuariosPorId[999];
```

El tipo más realista para datos construidos dinámicamente puede ser:

```ts
const usuariosPorId: Partial<Record<number, Usuario>> = {};
```

Así, cada acceso produce `Usuario | undefined`, obligándonos a comprobar el resultado:

```ts
const usuario = usuariosPorId[999];

if (usuario) {
  console.log(usuario.nombre);
}
```

También podemos activar la opción `noUncheckedIndexedAccess` de TypeScript para obtener comprobaciones más estrictas al acceder mediante índices.

## ¿Cuándo conviene utilizar `Map`?

Un objeto no siempre es la mejor estructura. `Map` conserva el tipo real de las claves, proporciona una API explícita y representa correctamente la posibilidad de que una clave no exista:

```ts
const usuariosPorId = new Map(
  usuarios.map((usuario) => [usuario.id, usuario] as const)
);

const usuario = usuariosPorId.get(2);
// Usuario | undefined
```

`Map` es una buena elección cuando añadimos y eliminamos entradas con frecuencia, necesitamos claves que no sean cadenas o símbolos, o queremos evitar las particularidades del prototipo de los objetos. Un objeto suele resultar más conveniente para serializar datos como JSON, interoperar con APIs o producir diccionarios simples.

## Conclusión

Para convertir un array de objetos en un objeto indexado, `reduce()` ofrece control y buen rendimiento, mientras que `Object.fromEntries()` proporciona una sintaxis breve y declarativa. Una función genérica como `indexarPor()` permite reutilizar la operación sin perder seguridad de tipos.

La elección final depende del objetivo: indexar elementos únicos, detectar duplicados, agrupar valores o mantener una colección dinámica. Lo importante es reflejar esas reglas en los tipos. TypeScript no solo documentará mejor la transformación, sino que también nos ayudará a detectar accesos inválidos y supuestos incorrectos antes de ejecutar el código.