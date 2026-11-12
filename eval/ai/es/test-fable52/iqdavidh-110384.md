Aprender a programar viendo tutoriales se parece a aprender a nadar viendo vídeos de natación: en algún momento hay que tirarse al agua. Con esta serie quiero proponerte ejercicios pequeños, con datos reales y con un resultado que puedas enseñarle a alguien que no programa.

Empezamos con un clásico del mundo laboral: **alguien te pide un Excel**.

## El encargo

Imagina que una amiga quiere pasar una semana en Madrid y te dice: «Tú que sabes de ordenadores, ¿me puedes pasar un Excel con los alojamientos de Airbnb por barrio y precio?».

Tu misión es escribir un programa que lea los datos de los anuncios y genere un fichero `.xlsx` ordenado, filtrado y con un pequeño resumen.

## De dónde salen los datos

No vamos a hacer *scraping* de la web de Airbnb: es frágil, va contra sus condiciones de uso y no es lo que queremos practicar hoy. Usaremos [Inside Airbnb](https://insideairbnb.com/get-the-data/), un proyecto que publica datos abiertos de anuncios de muchas ciudades.

Busca tu ciudad y descarga el fichero `listings.csv` (el resumido, no el `.csv.gz`). Cada fila es un anuncio, con columnas como estas:

- `name`: título del anuncio
- `neighbourhood`: barrio
- `room_type`: tipo de alojamiento (piso entero, habitación privada…)
- `price`: precio por noche
- `minimum_nights`: noches mínimas
- `number_of_reviews`: número de reseñas

Antes de escribir una sola línea de código, abre el CSV con un editor de texto y míralo. Este paso lo salta casi todo el mundo, y es donde descubrirás que hay precios vacíos, nombres con comas y otras sorpresas.

## Qué necesitas

- Python 3.10 o superior
- La librería `openpyxl` para escribir el Excel:

```bash
pip install openpyxl
```

Para leer el CSV usaremos el módulo `csv`, que ya viene con Python. Podrías resolverlo en cuatro líneas con `pandas`, pero aquí el objetivo es practicar bucles, condiciones y diccionarios.

## Paso 1: leer el CSV

```python
import csv

with open("listings.csv", encoding="utf-8") as f:
    anuncios = list(csv.DictReader(f))

print(len(anuncios))
print(anuncios[0])
```

`DictReader` convierte cada fila en un diccionario cuyas claves son los nombres de las columnas. Ejecuta el programa y comprueba que el número de anuncios tiene sentido.

**Ojo:** todo lo que sale de un CSV es texto. El precio `"85"` no es el número `85`, y no podrás compararlo ni sumarlo hasta que lo conviertas.

## Paso 2: limpiar y filtrar

Tu amiga solo quiere pisos enteros, de menos de 120 € por noche y que acepten estancias de una semana. Escribe una función que reciba la lista de anuncios y devuelva solo los que cumplen las condiciones:

```python
def filtrar(anuncios, precio_maximo=120, noches=7):
    resultado = []
    for a in anuncios:
        if not a["price"]:
            continue  # anuncios sin precio: fuera
        precio = float(a["price"])
        if (a["room_type"] == "Entire home/apt"
                and precio <= precio_maximo
                and int(a["minimum_nights"]) <= noches):
            a["price"] = precio
            resultado.append(a)
    return resultado
```

Fíjate en el `continue`: algunos anuncios no tienen precio, y `float("")` haría que el programa se detuviera con un error. Tratar los datos que faltan es buena parte del trabajo real de programar.

## Paso 3: escribir el Excel

```python
from openpyxl import Workbook

def guardar_excel(anuncios, ruta="airbnb.xlsx"):
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Anuncios"
    hoja.append(["Nombre", "Barrio", "Precio", "Reseñas"])

    for a in anuncios:
        hoja.append([
            a["name"],
            a["neighbourhood"],
            a["price"],
            int(a["number_of_reviews"]),
        ])

    libro.save(ruta)
```

Cada llamada a `append` añade una fila. Abre el fichero resultante con Excel o LibreOffice y comprueba que la columna de precio contiene números y no texto. Lo notarás porque los números se alinean a la derecha.

## Paso 4: ahora te toca a ti

Hasta aquí te he llevado de la mano. Lo que viene es el ejercicio de verdad:

1. **Ordena** los anuncios de más barato a más caro antes de guardarlos. Pista: `sorted` y su parámetro `key`.
2. **Crea una segunda hoja** llamada «Resumen» con una fila por barrio: número de anuncios, precio medio y precio mínimo. Pista: un diccionario cuya clave sea el barrio y cuyo valor sea una lista de precios.
3. **Dale formato**: cabecera en negrita, columnas con un ancho razonable y la primera fila inmovilizada. Pista: `Font(bold=True)`, `column_dimensions` y `freeze_panes`.
4. **Quita los valores fijos**: que el precio máximo y el nombre del fichero se puedan indicar al ejecutar el programa. Pista: el módulo `argparse`.

## Retos extra

Si te has quedado con ganas de más:

- Añade un gráfico de barras con el precio medio por barrio usando `openpyxl.chart`.
- Marca en verde los anuncios con más de 100 reseñas.
- Haz que el programa funcione con cualquier ciudad sin tocar el código.
- Reescríbelo con `pandas` y compara las dos versiones. ¿Cuál entiendes mejor? ¿Cuál es más corta?

## Qué has practicado

Aunque parezca un ejercicio modesto, aquí dentro hay bastante:

- Leer ficheros y entender su formato
- Convertir tipos de datos
- Bucles, condiciones y funciones
- Diccionarios para agrupar información
- Uso de una librería externa leyendo su documentación
- Tratamiento de datos incompletos

Además, has seguido el patrón **leer, transformar y escribir**, que encontrarás en muchísimos programas profesionales. Cambia el CSV por una base de datos y el Excel por una página web, y la estructura será la misma.

## Un último consejo

No copies y pegues el código: tecléalo. Cuando algo falle (y fallará), lee el mensaje de error completo antes de buscarlo en internet. Casi siempre te dice qué línea ha fallado y por qué.

Si resuelves el ejercicio, deja tu solución en los comentarios o cuéntame dónde te has atascado. En la próxima entrega cambiaremos el Excel por algo más visual.

¡A programar!
