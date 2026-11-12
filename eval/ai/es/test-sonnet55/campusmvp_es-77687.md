Casi todos los programadores hemos vivido esta escena: escribimos una comparación que parece obvia, el resultado es `false` y no entendemos por qué. O al revés: modificamos una variable y, sin tocarla, cambia otra.

Detrás de ambos casos está la misma distinción: **valor** frente a **referencia**. Cada lenguaje la resuelve a su manera, y conocerla ahorra muchas horas de depuración. Vamos a recorrer varios lenguajes con ejemplos cortos.

## Dos preguntas distintas

Cuando comparamos dos cosas podemos preguntar:

1. **¿Tienen el mismo contenido?** Es la igualdad de valor (o estructural).
2. **¿Son el mismo objeto en memoria?** Es la igualdad de identidad (o referencial).

Para los tipos primitivos, como enteros o booleanos, ambas preguntas suelen coincidir. Con objetos, listas o estructuras compuestas ya no. Dos listas con `[1, 2, 3]` tienen el mismo contenido, pero pueden ser dos objetos distintos.

Un modelo mental útil: una variable de **valor** es una caja que contiene el dato. Una variable de **referencia** es una caja que contiene una etiqueta con la dirección donde vive el dato. Copiar la primera duplica el dato. Copiar la segunda duplica la etiqueta, y ambas apuntan al mismo sitio.

## Python: `==` frente a `is`

Python separa las dos preguntas con dos operadores:

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)  # True  -> mismo contenido
print(a is b)  # False -> objetos distintos
print(a is c)  # True  -> misma referencia
```

En Python **todo es un objeto** y las variables son nombres que apuntan a objetos. Por eso:

```python
c.append(4)
print(a)  # [1, 2, 3, 4]
```

Modificamos `c` y cambió `a`, porque son el mismo objeto.

Hay una trampa conocida con los enteros pequeños y las cadenas. CPython reutiliza ciertos objetos inmutables (los enteros entre -5 y 256, y muchas cadenas internadas), así que `is` a veces devuelve `True` cuando no lo esperas:

```python
x = 256
y = 256
print(x is y)  # True (optimización de CPython)
```

Es un detalle de implementación, no una garantía del lenguaje. **Usa `==` para comparar valores y `is` solo para identidad**, sobre todo con `None`: `if x is None`.

## JavaScript: primitivos por valor, objetos por referencia

JavaScript tiene una frontera clara. Los primitivos (`number`, `string`, `boolean`, `null`, `undefined`, `symbol`, `bigint`) se comparan por valor. Los objetos, arrays y funciones, por referencia:

```javascript
console.log("hola" === "hola");     // true
console.log(42 === 42);             // true

console.log([1, 2] === [1, 2]);     // false
console.log({a: 1} === {a: 1});     // false

const p = {a: 1};
const q = p;
console.log(p === q);               // true
```

Además, `==` aplica coerciones de tipo y produce resultados sorprendentes (`"0" == false` es `true`). La recomendación habitual es usar siempre `===`.

Para comparar contenido de objetos no hay operador. Hay que recorrer propiedades, usar una librería como Lodash (`_.isEqual`) o, en casos simples, serializar con `JSON.stringify`, que depende del orden de las claves y falla con ciertos tipos.

## Java: el clásico `==` frente a `equals`

Java distingue entre primitivos (`int`, `double`, `boolean`…) y objetos. Con primitivos, `==` compara valores. Con objetos, compara referencias:

```java
String a = new String("java");
String b = new String("java");

System.out.println(a == b);       // false
System.out.println(a.equals(b));  // true
```

Para comparar contenido hay que usar `equals()`, y si defines tus propias clases debes sobrescribirlo (junto con `hashCode()`), o heredarás el comportamiento por defecto de `Object`, que es comparar referencias.

Java tiene su propia trampa con las cadenas literales, que se internan:

```java
String c = "java";
String d = "java";
System.out.println(c == d);  // true, por el pool de cadenas
```

Y otra con los envoltorios (`Integer`) que cachean valores entre -128 y 127:

```java
Integer m = 127, n = 127;
System.out.println(m == n);  // true

Integer x = 1000, y = 1000;
System.out.println(x == y);  // false
```

Moraleja: con objetos en Java, usa `equals()` y olvídate de `==`. Desde Java 16, los `record` generan `equals` por valor automáticamente, lo que simplifica mucho los tipos de datos.

## C#: el lenguaje que te deja elegir

C# separa **tipos por valor** (`struct`, `int`, `enum`) de **tipos por referencia** (`class`, `string`, arrays). Y deja que cada tipo decida qué significa `==`:

```csharp
var a = new int[] { 1, 2, 3 };
var b = new int[] { 1, 2, 3 };
Console.WriteLine(a == b);              // False (referencias)
Console.WriteLine(a.SequenceEqual(b));  // True  (contenido)

string s1 = "hola";
string s2 = new string("hola".ToCharArray());
Console.WriteLine(s1 == s2);            // True: string sobrecarga ==
```

`string` es un tipo por referencia, pero sobrecarga `==` para comparar contenido. Además, los `record` (desde C# 9) comparan por valor por defecto, mientras que las `class` normales comparan por referencia:

```csharp
record Punto(int X, int Y);
Console.WriteLine(new Punto(1, 2) == new Punto(1, 2)); // True
```

Los `struct` se copian al asignarlos. Si pasas un `struct` a un método y lo modificas dentro, el original no cambia. Con una `class`, sí.

## Go: valores por defecto, referencias explícitas

Go es honesto con lo que hace: **todo se pasa por valor**, incluidos los punteros (se copia la dirección). Los structs se comparan por valor si todos sus campos son comparables:

```go
type Punto struct{ X, Y int }

p1 := Punto{1, 2}
p2 := Punto{1, 2}
fmt.Println(p1 == p2) // true

q1 := &Punto{1, 2}
q2 := &Punto{1, 2}
fmt.Println(q1 == q2) // false: comparas direcciones
```

Los slices, mapas y funciones no se pueden comparar con `==` (salvo contra `nil`). Para slices necesitas `slices.Equal` o `reflect.DeepEqual`. Además, un slice es internamente un pequeño struct con un puntero a un array, así que copiarlo comparte los datos subyacentes:

```go
a := []int{1, 2, 3}
b := a
b[0] = 99
fmt.Println(a[0]) // 99
```

## Rust: la propiedad cambia las reglas

Rust no tiene recolector de basura y su modelo de **propiedad** (*ownership*) hace explícito quién posee cada dato. `==` compara por valor mediante el trait `PartialEq`, incluso a través de referencias:

```rust
let a = vec![1, 2, 3];
let b = vec![1, 2, 3];
println!("{}", a == b); // true

let r1 = &a;
let r2 = &a;
println!("{}", std::ptr::eq(r1, r2)); // true: misma dirección
```

Si quieres identidad, la pides con `std::ptr::eq`. Y las asignaciones **mueven** el valor por defecto:

```rust
let s1 = String::from("hola");
let s2 = s1;       // s1 deja de ser válido
// println!("{}", s1); // error de compilación
```

Para duplicar hay que ser explícito con `.clone()`. El compilador te impide el bug de "cambié una variable y cambió otra", y eso es una de las grandes ventajas del lenguaje.

## Paso de parámetros: la confusión más común

Muchas discusiones sobre "paso por valor o por referencia" se aclaran con esta idea: en lenguajes como Python, JavaScript y Java, **se pasa una copia de la referencia** (a veces llamado "paso por compartición"):

```python
def reasignar(lista):
    lista = [9, 9, 9]   # solo cambia la copia local de la referencia

def mutar(lista):
    lista.append(4)     # modifica el objeto compartido

datos = [1, 2, 3]
reasignar(datos)
print(datos)  # [1, 2, 3]
mutar(datos)
print(datos)  # [1, 2, 3, 4]
```

Reasignar no afecta al exterior. Mutar sí. Si entiendes esa diferencia, entiendes el 90 % del problema.

Lenguajes como C++ o C# (con `ref`/`out`) sí permiten pasar una referencia real a la variable, de modo que la reasignación también se ve fuera.

## Copias superficiales y profundas

Cuando quieres independencia real, necesitas copiar. Pero hay dos niveles:

```python
import copy

original = [[1, 2], [3, 4]]
superficial = original.copy()
profunda = copy.deepcopy(original)

original[0].append(99)
print(superficial)  # [[1, 2, 99], [3, 4]] -> comparte las sublistas
print(profunda)     # [[1, 2], [3, 4]]     -> totalmente independiente
```

En JavaScript, el equivalente moderno es `structuredClone(obj)`, y el operador *spread* (`{...obj}`) solo hace copia superficial. En Java no hay una solución universal: usa constructores de copia o librerías de serialización.

## Resumen rápido

| Lenguaje | Comparar contenido | Comparar identidad | Notas |
|---|---|---|---|
| Python | `==` | `is` | Cuidado con la internación de enteros |
| JavaScript | manual / librería | `===` en objetos | Evita `==` |
| Java | `equals()` | `==` | Cachés de `Integer` y pool de `String` |
| C# | `==` / `Equals` | `ReferenceEquals` | `record` compara por valor |
| Go | `==` en structs | `==` en punteros | Slices y mapas no son comparables |
| Rust | `==` | `ptr::eq` | Movimientos y `clone` explícito |

## Consejos prácticos

- **Pregúntate siempre qué estás comparando**: contenido o identidad. Si no sabes cuál necesitas, probablemente es contenido.
- **Prefiere la inmutabilidad** cuando puedas. Si un objeto no cambia, compartir referencias es seguro.
- **Define igualdad en tus tipos** de forma consciente. En Java, `equals` y `hashCode` juntos. En C#, usa `record` si el tipo es puro dato.
- **Copia de forma explícita** al devolver o guardar colecciones mutables que no quieres exponer.
- **Escribe tests** para estos casos: un test que mute una copia y verifique el original evita muchas sorpresas.

## Cierre

La diferencia entre valor y referencia no es un detalle académico: determina cómo se comportan tus asignaciones, tus comparaciones y tus funciones. Cada lenguaje toma decisiones distintas, y por eso un mismo patrón puede ser inofensivo en uno y peligroso en otro.

Lo que se mantiene constante es la pregunta de fondo: *¿estoy comparando lo que contiene o lo que es?* Si te la haces cada vez, tendrás medio camino ganado.

¿Qué trampa de igualdad o de referencias te ha costado más tiempo encontrar? Cuéntamelo en los comentarios.
