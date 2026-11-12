# Convertir un array de objetos a un objeto usando TypeScript

Trabajar con arrays de objetos es habitual cuando consumimos una API, consultamos una base de datos o procesamos formularios. Sin embargo, algunas operaciones resultan más cómodas si transformamos esa lista en un objeto cuyas claves representan un identificador.

Imagina que recibes una colección de usuarios y necesitas encontrar uno por su `id`. Puedes usar `find()`, pero también puedes construir un índice y acceder directamente mediante `usuariosPorId[id]`.

En este artículo veremos cómo realizar esa transformación con TypeScript, cómo tipar el resultado y qué decisiones conviene tomar cuando existen claves duplicadas o datos incompletos.

Partamos de un ejemplo sencillo:

```typescript
interface Usuario {
  id: string;
  nombre: string;
  activo: boolean;
}

const usuarios: Usuario[] = [
  { id: "u1", nombre: "Ana", activo: true },
  { id: "u2", nombre: "Luis", activo: false },
  { id: "u3", nombre: "María", activo: true },
];
```

Nuestro objetivo es obtener una estructura equivalente a esta:

```typescript
const usuariosPorId = {
  u1: { id: "u1", nombre: "Ana", activo: true },
  u2: { id: "u2", nombre: "Luis", activo: false },
  u3: { id: "u3", nombre: "María", activo: true },
};
```

Cada identificador se convierte en una propiedad, mientras que el objeto original permanece como valor. Este patrón suele llamarse indexación y aparece con frecuencia al organizar el estado de una aplicación.

La primera opción es utilizar `reduce()`. Este método recorre el array y construye un resultado acumulado:

```typescript
type UsuariosPorId = Record<string, Usuario>;

const usuariosPorId = usuarios.reduce<UsuariosPorId>(
  (acumulador, usuario) => {
    acumulador[usuario.id] = usuario;
    return acumulador;
  },
  {}
);
```

El acumulador comienza como un objeto vacío. En cada iteración añadimos una propiedad cuyo nombre corresponde al identificador del usuario. Finalmente, devolvemos el acumulador para continuar el recorrido.

El tipo `Record<string, Usuario>` describe un objeto con claves de texto y valores de tipo `Usuario`. El argumento genérico de `reduce()` permite comprobar tanto las asignaciones como el resultado.

Sin ese tipo explícito, TypeScript puede inferir que el acumulador es simplemente `{}` y rechazar el acceso mediante una clave dinámica.

Hay un detalle importante: `Record<string, Usuario>` puede dar una impresión equivocada sobre las claves existentes. El array contiene tres usuarios, pero eso no significa que cualquier cadena corresponda a uno.

Para reflejar esa posibilidad podemos utilizar:

```typescript
type UsuariosPorId = Partial<Record<string, Usuario>>;

const usuariosPorId = usuarios.reduce<UsuariosPorId>(
  (acumulador, usuario) => {
    acumulador[usuario.id] = usuario;
    return acumulador;
  },
  {}
);

const usuario = usuariosPorId["desconocido"];

console.log(usuario?.nombre);
```

Con `strictNullChecks` habilitado, la lectura devuelve `Usuario | undefined`, así que debemos comprobar el resultado antes de utilizarlo. Otra opción es habilitar `noUncheckedIndexedAccess`, que añade esa precaución a los accesos mediante firmas de índice.

También podemos resolver la transformación con `Object.fromEntries()`. Este método recibe pares de clave y valor y construye un objeto:

```typescript
const entradas = usuarios.map(
  (usuario): [string, Usuario] => [usuario.id, usuario]
);

const usuariosPorId: Partial<Record<string, Usuario>> =
  Object.fromEntries(entradas);
```

Aquí separamos el proceso en dos pasos. Primero generamos las entradas; después construimos el objeto. La anotación `[string, Usuario]` indica que cada entrada es una tupla con exactamente dos elementos.

Esta alternativa suele resultar fácil de leer cuando la transformación consiste únicamente en asociar una clave con un valor. Para que TypeScript reconozca `Object.fromEntries()`, la configuración de `lib` debe incluir `ES2019` o una biblioteca posterior.

Recuerda que disponer de sus tipos no incorpora automáticamente el método al entorno de ejecución. El navegador o la versión de Node.js también deben soportarlo, o necesitarás un polyfill.

Aunque `reduce()` es popular, un bucle `for...of` ofrece una solución igualmente válida y muy directa:

```typescript
const usuariosPorId: Partial<Record<string, Usuario>> = {};

for (const usuario of usuarios) {
  usuariosPorId[usuario.id] = usuario;
}
```

Este enfoque facilita añadir condiciones, registrar errores o detener el procesamiento. También evita crear el array intermedio de entradas que utiliza la combinación de `map()` y `Object.fromEntries()`.

Las tres alternativas recorren la colección una vez. Para este caso sencillo, su complejidad temporal esperada es O(n), y el índice necesita espacio proporcional al número de claves diferentes.

Conviene evitar una variante frecuente de `reduce()`:

```typescript
const usuariosPorId = usuarios.reduce<
  Partial<Record<string, Usuario>>
>(
  (acumulador, usuario) => ({
    ...acumulador,
    [usuario.id]: usuario,
  }),
  {}
);
```

Aunque funciona, copia las propiedades acumuladas en cada iteración. Cuando crece la cantidad de claves distintas, el trabajo total puede volverse cuadrático.

Modificar un acumulador recién creado es razonable: no estamos alterando el array original ni un objeto recibido desde fuera. Estamos construyendo una estructura local.

Ahora bien, ¿qué ocurre si dos elementos tienen el mismo identificador?

```typescript
const usuariosRepetidos: Usuario[] = [
  { id: "u1", nombre: "Ana", activo: true },
  { id: "u1", nombre: "Andrea", activo: false },
];
```

Con las implementaciones anteriores, el último elemento reemplaza al primero. El resultado contendrá a Andrea bajo la clave `"u1"`.

Ese comportamiento puede ser correcto, pero debe ser una decisión consciente. Si necesitas conservar el primero, comprueba la existencia de la propiedad antes de asignarla:

```typescript
const usuariosPorId: Partial<Record<string, Usuario>> = {};

for (const usuario of usuariosRepetidos) {
  if (!Object.prototype.hasOwnProperty.call(
    usuariosPorId,
    usuario.id
  )) {
    usuariosPorId[usuario.id] = usuario;
  }
}
```

También puedes lanzar un error cuando detectes un duplicado. Si necesitas conservar todos los elementos asociados a una misma clave, entonces estás buscando una agrupación y el valor debería ser un array.

Cuando esta operación aparece varias veces, una función genérica evita repetir código:

```typescript
function indexarPor<T>(
  elementos: readonly T[],
  obtenerClave: (elemento: T) => string
): Partial<Record<string, T>> {
  const resultado: Partial<Record<string, T>> =
    Object.create(null);

  for (const elemento of elementos) {
    resultado[obtenerClave(elemento)] = elemento;
  }

  return resultado;
}

const usuariosPorId = indexarPor(
  usuarios,
  (usuario) => usuario.id
);
```

El parámetro `readonly T[]` permite recibir arrays normales y arrays de solo lectura. La función selectora decide cómo obtener la clave, mientras TypeScript infiere el tipo de los valores.

Usamos `Object.create(null)` para construir un diccionario sin prototipo. Así, claves como `"__proto__"` se almacenan como propiedades ordinarias. A cambio, el resultado no tiene métodos heredados como `toString()` o `hasOwnProperty()`.

Otro aspecto importante es que estas soluciones conservan las referencias originales:

```typescript
const indice = indexarPor(usuarios, (usuario) => usuario.id);

console.log(indice["u1"] === usuarios[0]); // true
```

Por lo tanto, modificar un usuario mediante el índice también modifica el objeto visible desde el array. Si necesitas objetos independientes, debes copiarlos durante la transformación. El operador spread realiza una copia superficial; las propiedades anidadas seguirán compartiendo referencias.

Finalmente, recuerda que las claves numéricas de un objeto se convierten en cadenas durante la ejecución. Si necesitas distinguir entre `1` y `"1"`, o utilizar objetos como claves, considera un `Map`.

Convertir un array en un objeto es una operación pequeña, pero sus detalles afectan al resultado: elige una clave adecuada, representa las ausencias en el tipo y define cómo resolver duplicados. Con esas decisiones claras, tanto `reduce()` como `Object.fromEntries()` o `for...of` ofrecen una implementación sencilla y fácil de mantener.
