# Comparando valores y referencias en varios lenguajes de programación

Uno de los conceptos que más confusión genera entre quienes están aprendiendo a programar —y que incluso a desarrolladores con experiencia les sigue dando algún que otro dolor de cabeza— es la diferencia entre **paso por valor** y **paso por referencia**. En este artículo vamos a repasar cómo se comportan distintos lenguajes de programación en este aspecto, con ejemplos concretos.

## El concepto básico

Cuando pasamos una variable a una función, o simplemente la asignamos a otra variable, pueden pasar dos cosas:

- **Se copia el valor**: la nueva variable es completamente independiente. Modificarla no afecta a la original.
- **Se copia una referencia**: ambas variables apuntan al mismo dato en memoria. Modificar el contenido a través de una de ellas afecta a la otra.

La complicación viene porque muchos lenguajes mezclan ambos comportamientos según el tipo de dato: los tipos primitivos suelen pasarse por valor, mientras que los objetos suelen pasarse por referencia (o, más precisamente, por "valor de la referencia", como veremos).

## JavaScript

En JavaScript, los tipos primitivos (`number`, `string`, `boolean`, `undefined`, `null`, `symbol`, `bigint`) se pasan siempre por valor:

```js
let a = 5;
let b = a;
b = 10;
console.log(a); // 5
```

Los objetos y arrays, en cambio, se comportan como si se pasaran por referencia:

```js
let obj1 = { valor: 5 };
let obj2 = obj1;
obj2.valor = 10;
console.log(obj1.valor); // 10
```

Sin embargo, hay un matiz importante: si reasignamos `obj2` a un objeto completamente nuevo, `obj1` no se ve afectado:

```js
let obj2 = obj1;
obj2 = { valor: 99 };
console.log(obj1.valor); // 10, no 99
```

Esto es porque, técnicamente, lo que se copia es el **valor de la referencia** (una especie de puntero a la ubicación en memoria), no la referencia en sí como si fuera un alias. Es una distinción sutil pero importante.

## Python

Python funciona de forma muy similar a JavaScript en este aspecto, aunque con su propia terminología: se suele decir que Python pasa "por asignación de objeto" (*pass by object reference* o *pass by assignment*).

```python
def modificar(lista):
    lista.append(4)

mi_lista = [1, 2, 3]
modificar(mi_lista)
print(mi_lista)  # [1, 2, 3, 4]
```

Pero si dentro de la función reasignamos el parámetro a un nuevo objeto, el cambio no se propaga afuera:

```python
def modificar(lista):
    lista = [9, 9, 9]

mi_lista = [1, 2, 3]
modificar(mi_lista)
print(mi_lista)  # [1, 2, 3], sin cambios
```

Además, en Python hay que tener en cuenta la diferencia entre tipos **mutables** (listas, diccionarios, sets, objetos propios) e **inmutables** (int, float, str, tuple, bool). Con los inmutables, cualquier "modificación" en realidad crea un nuevo objeto:

```python
def modificar(numero):
    numero += 1

x = 5
modificar(x)
print(x)  # 5
```

## Java

Java es célebre por generar debates sobre si "todo se pasa por valor" o "los objetos se pasan por referencia". La respuesta técnicamente correcta es: **todo en Java se pasa por valor**, pero en el caso de los objetos, lo que se pasa por valor es la referencia al objeto (como en JavaScript).

```java
public static void modificar(int[] arr) {
    arr[0] = 100;
}

int[] numeros = {1, 2, 3};
modificar(numeros);
System.out.println(numeros[0]); // 100
```

```java
public static void reasignar(int[] arr) {
    arr = new int[]{9, 9, 9};
}

int[] numeros = {1, 2, 3};
reasignar(numeros);
System.out.println(numeros[0]); // 1, sin cambios
```

Este comportamiento es prácticamente idéntico al de JavaScript: podemos mutar el objeto apuntado, pero no podemos hacer que la variable original apunte a otro objeto distinto.

## C

C es de los pocos lenguajes que ofrece control explícito y directo sobre esto mediante **punteros**. Por defecto, todo se pasa por valor:

```c
void modificar(int x) {
    x = 100;
}

int main() {
    int a = 5;
    modificar(a);
    printf("%d", a); // 5
}
```

Pero si queremos un comportamiento equivalente al paso por referencia, debemos pasar explícitamente la dirección de memoria usando el operador `&`, y recibirla como puntero:

```c
void modificar(int *x) {
    *x = 100;
}

int main() {
    int a = 5;
    modificar(&a);
    printf("%d", a); // 100
}
```

Esta explicitud es una de las razones por las que C se considera un lenguaje de "bajo nivel": no hay magia oculta, el programador decide exactamente qué se copia y qué no.

## C++

C++ añade a lo anterior las **referencias** propiamente dichas (`&` en la declaración del parámetro), que son básicamente un alias del original:

```cpp
void modificar(int &x) {
    x = 100;
}

int main() {
    int a = 5;
    modificar(a);
    std::cout << a; // 100
}
```

A diferencia de un puntero, una referencia en C++ no puede ser nula ni reasignada para apuntar a otra variable, lo que la hace más segura de usar en muchos escenarios.

## Kotlin

Kotlin, al correr sobre la JVM, hereda el mismo comportamiento de Java: los tipos primitivos se pasan por valor y los objetos por "valor de la referencia". La particularidad de Kotlin es que distingue entre `val` (inmutable) y `var` (mutable) a nivel de variable, lo cual añade una capa extra de seguridad, aunque no cambia el mecanismo subyacente de paso de parámetros.

```kotlin
fun modificar(lista: MutableList<Int>) {
    lista.add(4)
}

val miLista = mutableListOf(1, 2, 3)
modificar(miLista)
println(miLista) // [1, 2, 3, 4]
```

## Go

Go también pasa todo por valor por defecto, incluyendo slices, maps y structs. Sin embargo, los slices y maps internamente contienen punteros a la estructura de datos subyacente, por lo que modificar su contenido sí se refleja afuera, aunque reasignar la variable dentro de la función no:

```go
func modificar(s []int) {
    s[0] = 100
}

func main() {
    numeros := []int{1, 2, 3}
    modificar(numeros)
    fmt.Println(numeros[0]) // 100
}
```

Para pasar explícitamente por referencia una variable de tipo simple, Go también ofrece punteros con `*` y `&`, de forma similar a C.

## Conclusión

Aunque cada lenguaje tiene su propia terminología y matices, el patrón general se repite una y otra vez: los tipos primitivos casi siempre se copian por valor, y los tipos compuestos (objetos, arrays, listas) se comportan como si se pasaran por referencia, aunque en la mayoría de los casos modernos lo que realmente ocurre es que se copia el valor de un puntero interno a la estructura de datos.

Entender esta diferencia es clave para evitar bugs difíciles de rastrear, especialmente cuando mutamos objetos dentro de funciones esperando (o no esperando) que el cambio se propague hacia afuera. La próxima vez que te encuentres con un comportamiento inesperado al modificar una variable dentro de una función, este es uno de los primeros lugares donde conviene mirar.
