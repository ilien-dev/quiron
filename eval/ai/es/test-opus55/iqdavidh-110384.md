Hay un momento en el que todo el que aprende a programar se atasca: ya sabes qué es una variable, un bucle y una función, pero no sabes **qué construir**. Los tutoriales se acaban y los proyectos "de verdad" parecen inalcanzables.

Esta serie nace para llenar ese hueco. Cada entrega es un ejercicio pequeño, con datos reales y un resultado que puedes enseñar a alguien que no programa. Hoy empezamos con uno que me encanta: **convertir datos de Airbnb en un Excel ordenado y útil**.

## ¿Por qué este ejercicio?

Porque toca casi todo lo que hace un programador en su día a día:

- **Leer datos** de un archivo que no has creado tú.
- **Limpiarlos**, porque los datos reales siempre vienen sucios.
- **Transformarlos** para responder preguntas concretas.
- **Entregar un resultado** en un formato que otra persona entienda.

Y Excel es el formato perfecto: tu jefe, tu tía o tu casero saben abrirlo. Si tu programa genera un Excel, tu programa es útil para el mundo.

## Los datos

No vamos a hacer scraping de Airbnb (va contra sus términos de uso y además es frágil). Usaremos **Inside Airbnb** (insideairbnb.com), un proyecto que publica datos abiertos de alojamientos de muchas ciudades del mundo.

1. Entra en la sección *Get the Data*.
2. Elige una ciudad (Madrid, Barcelona, Ciudad de México, Buenos Aires…).
3. Descarga el archivo `listings.csv` (la versión resumida es suficiente).

Ese CSV tiene columnas como `name`, `neighbourhood`, `room_type`, `price`, `minimum_nights`, `number_of_reviews` o `availability_365`. Miles de filas de datos reales.

## El enunciado

Escribe un programa en Python que lea `listings.csv` y genere un archivo `airbnb.xlsx` con tres hojas:

1. **Alojamientos**: los datos limpios, solo con las columnas útiles.
2. **Por barrio**: número de alojamientos, precio medio y precio mediano de cada barrio, ordenado de más caro a más barato.
3. **Por tipo**: cuántos alojamientos hay de cada tipo (casa entera, habitación privada…) en cada barrio.

Bonus: que el Excel se vea bonito (cabeceras fijas, filtros y columnas con ancho razonable).

> **Antes de seguir leyendo, inténtalo tú.** En serio. Equivocarte es la parte en la que aprendes. Vuelve aquí cuando te atasques o cuando lo tengas.

## Preparación

Necesitas Python 3 y dos librerías:

```bash
pip install pandas openpyxl
```

`pandas` sirve para manipular tablas de datos y `openpyxl` es lo que usa por debajo para escribir archivos `.xlsx`.

## Paso 1: leer y explorar

Lo primero nunca es escribir el programa: es **mirar los datos**.

```python
import pandas as pd

df = pd.read_csv("listings.csv")

print(df.shape)              # (filas, columnas)
print(df.columns.tolist())   # nombres de las columnas
print(df.head())             # primeras filas
print(df["price"].describe())
```

Fíjate en cosas raras: precios vacíos, precios de 0, precios absurdamente altos, nombres de columnas en inglés. Todo eso habrá que decidir cómo tratarlo.

## Paso 2: limpiar

Dependiendo de la versión del archivo, `price` puede venir como número (`85`) o como texto (`"$1,250.00"`). Este código funciona en ambos casos:

```python
df["price"] = pd.to_numeric(
    df["price"].astype(str).str.replace(r"[$,]", "", regex=True),
    errors="coerce",
)

# Quitamos filas sin precio o con precios sin sentido
df = df[(df["price"] > 0) & (df["price"] < 10_000)]

columnas = {
    "name": "Nombre",
    "neighbourhood": "Barrio",
    "room_type": "Tipo",
    "price": "Precio",
    "minimum_nights": "Noches mínimas",
    "number_of_reviews": "Reseñas",
    "availability_365": "Días disponibles",
}
alojamientos = df[list(columnas)].rename(columns=columnas)
```

Aquí hay una lección importante: **limpiar datos es tomar decisiones**. ¿Por qué 10.000 y no 5.000? No hay una respuesta correcta; lo importante es que la decisión sea consciente y esté escrita en el código.

## Paso 3: transformar

Ahora respondemos preguntas. ¿Cuánto cuesta dormir en cada barrio?

```python
por_barrio = (
    alojamientos.groupby("Barrio")
    .agg(
        Alojamientos=("Precio", "count"),
        Precio_medio=("Precio", "mean"),
        Precio_mediano=("Precio", "median"),
    )
    .round(2)
    .sort_values("Precio_medio", ascending=False)
    .reset_index()
)
```

¿Por qué media **y** mediana? Porque un solo ático de lujo puede disparar la media de un barrio entero. La mediana es mucho más resistente a esos casos extremos. Compara ambas columnas cuando abras el Excel: verás barrios donde se parecen mucho y otros donde no tienen nada que ver.

Y ahora la tabla por tipo de alojamiento:

```python
por_tipo = pd.crosstab(
    alojamientos["Barrio"], alojamientos["Tipo"]
).reset_index()
```

`crosstab` cuenta cuántas veces aparece cada combinación de barrio y tipo. Es una tabla dinámica de Excel, pero en una sola línea.

## Paso 4: escribir el Excel

```python
with pd.ExcelWriter("airbnb.xlsx", engine="openpyxl") as writer:
    alojamientos.to_excel(writer, sheet_name="Alojamientos", index=False)
    por_barrio.to_excel(writer, sheet_name="Por barrio", index=False)
    por_tipo.to_excel(writer, sheet_name="Por tipo", index=False)

    for hoja in writer.sheets.values():
        hoja.freeze_panes = "A2"               # cabecera fija
        hoja.auto_filter.ref = hoja.dimensions  # filtros
        for columna in hoja.columns:
            ancho = max(len(str(c.value or "")) for c in columna)
            letra = columna[0].column_letter
            hoja.column_dimensions[letra].width = min(ancho + 2, 50)
```

Ejecuta el programa, abre `airbnb.xlsx` y disfruta. Acabas de convertir miles de filas de datos crudos en un informe que cualquiera puede usar.

## Errores típicos

- **`FileNotFoundError`**: el CSV no está en la misma carpeta desde la que ejecutas el script.
- **`KeyError: 'neighbourhood'`**: tu archivo tiene otros nombres de columna. Revisa el `print(df.columns.tolist())` del paso 1.
- **`PermissionError` al guardar**: tienes el Excel abierto. Ciérralo y vuelve a ejecutar.
- **Caracteres raros en los nombres**: prueba `pd.read_csv("listings.csv", encoding="utf-8")`.

## Retos extra

Si te ha sabido a poco, aquí tienes ideas para ampliarlo:

1. **Ingreso estimado**: calcula `Precio × (365 − Días disponibles)` como aproximación de lo que gana cada alojamiento al año. ¿Qué barrio "factura" más?
2. **Anfitriones profesionales**: usando `host_id`, encuentra los anfitriones con más de 10 alojamientos. ¿Qué porcentaje del total controlan?
3. **Comparar ciudades**: descarga dos ciudades y genera un Excel que las compare lado a lado.
4. **Hazlo reutilizable**: que el nombre del archivo de entrada se pase como argumento (`python airbnb.py madrid.csv`).
5. **Formato condicional**: colorea en rojo los barrios con precio medio por encima de la media de la ciudad.

## Lo que has practicado

Sin darte cuenta, has hecho un pequeño proyecto completo: exploración de datos, limpieza con criterio, agregaciones, tablas cruzadas y generación de un entregable profesional. Es exactamente el tipo de tarea que en muchas empresas se hace a mano, cada semana, durante horas.

Y ahora tú sabes automatizarla.

En el próximo ejercicio de la serie daremos otro paso. Mientras tanto, si lo resuelves, compártelo en los comentarios: me encantará ver qué ciudad elegiste y qué descubriste en sus datos.

¡Feliz programación! 🚀
