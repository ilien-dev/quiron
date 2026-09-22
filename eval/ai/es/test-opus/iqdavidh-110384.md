# Ejercicio para aprender a programar 01 - Excel desde Airbnb

Una de las mejores formas de aprender a programar es resolver problemas reales. Los ejercicios de "calcula el factorial" o "invierte una cadena" están bien para practicar la sintaxis, pero no se parecen mucho a lo que harás en un trabajo. Por eso inauguro esta serie de ejercicios con uno muy práctico: **obtener datos de anuncios de Airbnb y guardarlos en un archivo Excel**.

El objetivo no es construir un scraper profesional, sino practicar varias habilidades a la vez: leer datos estructurados, recorrerlos, transformarlos y generar un archivo que cualquier persona pueda abrir.

## El enunciado

Imagina que un amigo quiere invertir en un piso para alquiler vacacional en tu ciudad y te pide ayuda. Quiere una hoja de cálculo con información de los alojamientos disponibles en un barrio concreto:

- Nombre del anuncio
- Tipo de alojamiento (piso entero, habitación privada...)
- Precio por noche
- Valoración media
- Número de reseñas
- Número de huéspedes

Tu tarea es escribir un programa que genere ese Excel automáticamente.

## Antes de empezar: una advertencia

Hacer scraping directo de la web de Airbnb no es buena idea. Sus términos de servicio lo prohíben, la página se carga dinámicamente con JavaScript y cambia con frecuencia, así que tu código dejaría de funcionar en cualquier momento.

Afortunadamente, existe una alternativa perfecta para aprender: **Inside Airbnb** (insideairbnb.com), un proyecto que publica datos abiertos de anuncios de Airbnb de decenas de ciudades del mundo, incluidas Madrid, Barcelona, Ciudad de México o Buenos Aires. Los datos vienen en archivos CSV que podemos descargar libremente.

Descarga el archivo `listings.csv` de la ciudad que prefieras.

## Herramientas

Usaremos **Python** porque es sencillo de leer y tiene librerías excelentes para este tipo de tareas:

- `pandas`: para leer y manipular datos en forma de tabla.
- `openpyxl`: para escribir archivos `.xlsx`.

Instálalas con:

```bash
pip install pandas openpyxl
```

## Paso 1: leer los datos

```python
import pandas as pd

df = pd.read_csv("listings.csv")

print(df.shape)       # número de filas y columnas
print(df.columns)     # nombres de las columnas
print(df.head())      # primeras 5 filas
```

Antes de escribir más código, **explora los datos**. Mira qué columnas hay, qué tipo de valores contienen y si hay celdas vacías. Este hábito te ahorrará muchos errores.

## Paso 2: quedarnos con lo que nos interesa

El archivo tiene muchas columnas. Seleccionamos solo las que necesitamos y las renombramos al español:

```python
columnas = {
    "name": "Nombre",
    "neighbourhood_cleansed": "Barrio",
    "room_type": "Tipo",
    "price": "Precio",
    "review_scores_rating": "Valoración",
    "number_of_reviews": "Reseñas",
    "accommodates": "Huéspedes",
}

df = df[list(columnas.keys())].rename(columns=columnas)
```

## Paso 3: filtrar por barrio

```python
barrio = "Palermo"
df = df[df["Barrio"] == barrio]
print(f"Encontrados {len(df)} alojamientos en {barrio}")
```

Cambia `"Palermo"` por un barrio de la ciudad que hayas elegido. Puedes ver los disponibles con `df["Barrio"].unique()`.

## Paso 4: limpiar los datos

Aquí aparece el primer problema real. La columna de precio viene como texto, por ejemplo `"$1,250.00"`. Para poder ordenarla o hacer cálculos, hay que convertirla a número:

```python
df["Precio"] = (
    df["Precio"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float)
)
```

También eliminamos los anuncios sin precio y rellenamos las valoraciones vacías:

```python
df = df.dropna(subset=["Precio"])
df["Valoración"] = df["Valoración"].fillna(0)
```

## Paso 5: ordenar y exportar

```python
df = df.sort_values("Precio")
df.to_excel("airbnb_palermo.xlsx", index=False, sheet_name="Alojamientos")
print("¡Excel generado!")
```

Abre el archivo y ahí tienes la tabla.

## Paso 6 (extra): un resumen

Tu amigo seguramente querrá algo más que una lista. Añadamos una segunda hoja con estadísticas por tipo de alojamiento:

```python
resumen = df.groupby("Tipo").agg(
    Cantidad=("Nombre", "count"),
    Precio_medio=("Precio", "mean"),
    Valoración_media=("Valoración", "mean"),
).round(2)

with pd.ExcelWriter("airbnb_palermo.xlsx") as writer:
    df.to_excel(writer, sheet_name="Alojamientos", index=False)
    resumen.to_excel(writer, sheet_name="Resumen")
```

## Retos para seguir practicando

Si terminaste, intenta estas mejoras por tu cuenta:

1. Pide el barrio al usuario con `input()` en lugar de escribirlo en el código.
2. Añade una columna con el **precio por huésped**.
3. Filtra solo los alojamientos con más de 10 reseñas y valoración superior a 4.5.
4. Da formato al Excel con `openpyxl`: encabezados en negrita y ancho de columnas ajustado.
5. Genera un Excel por cada barrio de la ciudad, con un bucle.

## Qué has aprendido

Con este ejercicio has practicado:

- Instalar y usar librerías externas.
- Leer archivos CSV.
- Seleccionar, filtrar y ordenar datos.
- Limpiar datos con formatos incorrectos.
- Agrupar y calcular estadísticas.
- Exportar resultados a Excel.

Son tareas que aparecen en muchísimos trabajos, no solo en programación: análisis de datos, marketing, finanzas o administración. En el próximo ejercicio daremos un paso más y convertiremos estos datos en gráficos. ¡Comparte tu solución en los comentarios!
