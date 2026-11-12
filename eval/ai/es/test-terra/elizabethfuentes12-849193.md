# Iniciando Machine Learning en Amazon SageMaker

Entrenar un modelo de *machine learning* en una laptop puede ser una excelente manera de aprender. Pero, cuando los datos crecen o queremos compartir resultados y poner el modelo a disposición de una aplicación, aparecen nuevas preguntas: ¿dónde almacenamos los datos?, ¿qué máquina necesitamos?, ¿cómo repetimos el entrenamiento?, ¿cómo servimos las predicciones?

Amazon SageMaker ofrece herramientas para abordar estas etapas en AWS. En este artículo recorreremos los conceptos principales y construiremos un primer modelo de clasificación desde un notebook. La idea es entender el flujo de trabajo antes de añadir infraestructura o complejidad.

## ¿Qué es Amazon SageMaker?

Amazon SageMaker es un conjunto de capacidades de AWS para trabajar con datos, analítica e inteligencia artificial. Dentro de este ecosistema, **Amazon SageMaker AI** reúne herramientas para preparar datos, entrenar, evaluar y desplegar modelos de machine learning.

Una pieza central es **Amazon SageMaker Studio**, una interfaz web desde la que podemos acceder a entornos de desarrollo como JupyterLab, además de herramientas especializadas para ML.

Algunos componentes que encontrarás con frecuencia son:

- **Amazon S3:** almacenamiento de datos y archivos de modelos.
- **Training jobs:** trabajos administrados que ejecutan el entrenamiento en infraestructura de AWS.
- **SageMaker Experiments:** organización y seguimiento de experimentos.
- **SageMaker Pipelines:** automatización de flujos de trabajo de ML.
- **Endpoints de inferencia:** servicios que reciben datos y devuelven predicciones.

No necesitas usar todo desde el primer día. Para empezar, un notebook, un conjunto de datos pequeño y un objetivo claro son suficientes.

## El problema que vamos a resolver

Usaremos el conjunto de datos **Iris**, incluido en scikit-learn. Contiene medidas de flores y su especie. Nuestro objetivo será entrenar un clasificador que prediga la especie a partir de cuatro características:

1. Longitud del sépalo.
2. Ancho del sépalo.
3. Longitud del pétalo.
4. Ancho del pétalo.

Es un ejemplo pequeño y conocido. No representa los desafíos de un proyecto real, pero nos permite concentrarnos en el proceso completo: cargar datos, separarlos, entrenar y evaluar.

## Antes de comenzar

Para seguir el ejemplo necesitarás:

- Una cuenta de AWS con acceso a SageMaker AI.
- Permisos para abrir SageMaker Studio y ejecutar JupyterLab.
- Una región de AWS donde estén disponibles los recursos que utilizarás.
- Conocimientos básicos de Python y notebooks.

AWS ofrece una opción de configuración rápida para crear los recursos iniciales de SageMaker AI. Desde la consola, busca **Amazon SageMaker AI**, completa la configuración y abre **Studio**. Allí podrás iniciar una aplicación de **JupyterLab** y crear un notebook con Python. Los nombres exactos de los botones pueden cambiar con la interfaz. Consulta la [guía oficial de configuración rápida](https://docs.aws.amazon.com/sagemaker/latest/dg/onboard-quick-start.html) si necesitas ayuda.

**Antes de iniciar recursos, revisa los precios y configura un presupuesto o una alerta de facturación.** El acceso a Studio no tiene un cargo independiente, pero el cómputo y el almacenamiento que uses sí pueden generarlo. La elegibilidad y los límites gratuitos dependen de la oferta vigente y de tu cuenta; consulta la [página de precios de SageMaker AI](https://aws.amazon.com/sagemaker/ai/pricing/).

## Paso 1: prepara el notebook

Abre un notebook de Python en JupyterLab y comprueba que tienes instaladas las bibliotecas necesarias:

```python
import sklearn
import pandas as pd

print("scikit-learn:", sklearn.__version__)
print("pandas:", pd.__version__)
```

Si falta alguna, puedes instalarla desde una celda:

```python
%pip install scikit-learn pandas
```

Puede que necesites reiniciar el kernel después de instalar paquetes. En un proyecto compartido conviene fijar las versiones de las dependencias para que otras personas puedan reproducir el entorno.

## Paso 2: carga y explora los datos

Comencemos cargando Iris como un `DataFrame`:

```python
from sklearn.datasets import load_iris

iris = load_iris(as_frame=True)

X = iris.data
y = iris.target

print("Dimensiones:", X.shape)
print("Clases:", list(iris.target_names))
display(X.head())
```

`X` contiene las características que usaremos para predecir; `y` contiene la clase correcta de cada flor.

Antes de entrenar, revisemos también los valores faltantes y la distribución de clases:

```python
print("Valores faltantes:")
print(X.isna().sum())

print("\nEjemplos por clase:")
print(y.value_counts().sort_index())
```

En Iris los datos vienen preparados y el conjunto está equilibrado. En una aplicación real, la exploración suele requerir bastante más trabajo: revisar duplicados, valores imposibles, diferencias entre grupos y la forma en que se obtuvieron los datos.

Una pregunta especialmente útil es: **¿esta información estará disponible cuando hagamos una predicción?** Si usamos durante el entrenamiento datos que solo se conocen después del resultado, podemos obtener métricas engañosamente buenas. A ese problema se le conoce como *fuga de datos*.

## Paso 3: separa entrenamiento y prueba

Necesitamos reservar ejemplos que el modelo no vea durante el entrenamiento. Así tendremos una estimación inicial de su rendimiento con datos nuevos.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

print("Entrenamiento:", X_train.shape)
print("Prueba:", X_test.shape)
```

Con `test_size=0.2` reservamos el 20 % de los ejemplos para prueba. `stratify=y` ayuda a conservar la proporción de clases en ambas particiones, mientras que `random_state` permite repetir la división.

En proyectos reales también es habitual contar con un conjunto de validación para elegir el modelo y sus parámetros, dejando el conjunto de prueba para la evaluación final.

## Paso 4: entrena un primer modelo

Utilizaremos un bosque aleatorio o *random forest*. Es un buen punto de partida para datos tabulares porque requiere poca preparación y permite construir rápidamente una línea base.

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
)

model.fit(X_train, y_train)

print("Entrenamiento completado")
```

La llamada a `fit` ajusta el modelo con los datos de entrenamiento. En este ejemplo, el código se ejecuta directamente en el cómputo asociado a JupyterLab.

Esto es diferente de lanzar un **training job** administrado: en ese caso, SageMaker AI aprovisiona infraestructura para ejecutar el entrenamiento como un trabajo independiente. Ese enfoque resulta útil cuando necesitas máquinas más grandes, ejecuciones repetibles o separar el entrenamiento de tu entorno interactivo. AWS explica las opciones en su [documentación de entrenamiento](https://docs.aws.amazon.com/sagemaker/latest/dg/train-model.html).

## Paso 5: evalúa las predicciones

Ahora probemos el modelo con los ejemplos que reservamos:

```python
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))

print("\nReporte por clase:")
print(classification_report(
    y_test,
    y_pred,
    target_names=iris.target_names,
))

print("Matriz de confusión:")
print(confusion_matrix(y_test, y_pred))
```

La **accuracy** indica la proporción de predicciones correctas. El reporte también muestra precisión, recall y puntuación F1 para cada clase. La matriz de confusión permite ver qué especies se confunden entre sí.

No te quedes únicamente con un número. Una accuracy alta puede ocultar problemas si una clase aparece muy poco o si ciertos errores son más costosos que otros. Por ejemplo, en un sistema de detección de fraude, dejar pasar un caso fraudulento puede tener consecuencias distintas de revisar una transacción legítima.

Además, Iris es pequeño: el conjunto de prueba contiene pocos ejemplos. Su resultado es útil para aprender, pero no demuestra cómo se comportaría el modelo en un entorno de producción.

## Paso 6: prueba una predicción

Podemos tomar una fila del conjunto de prueba y comparar la predicción con su valor real:

```python
sample = X_test.iloc[[0]]

predicted_class = model.predict(sample)[0]
actual_class = y_test.iloc[0]

print("Predicción:", iris.target_names[predicted_class])
print("Clase real:", iris.target_names[actual_class])
```

Observa que usamos un `DataFrame` con los mismos nombres de columnas que durante el entrenamiento. En una aplicación real, mantener el mismo orden, formato y transformación de las características es esencial para obtener predicciones coherentes.

Si quieres guardar el modelo para experimentar más tarde, puedes usar `joblib`:

```python
import joblib

joblib.dump(model, "iris-random-forest.joblib")
```

Este archivo queda en el almacenamiento de tu entorno. Para compartirlo o integrarlo en otro flujo de AWS, podrías guardarlo en un bucket de S3 con los permisos apropiados. Carga archivos de modelos únicamente desde fuentes de confianza.

## ¿Y cómo llegamos a producción?

Entrenar en un notebook es un comienzo, no el final del camino. Una vez que tienes un modelo prometedor, SageMaker AI ofrece varias formas de llevarlo más lejos:

1. **Ejecutar el entrenamiento como un trabajo administrado.** Puedes proporcionar tus datos, tu código y la configuración de cómputo.
2. **Registrar y comparar versiones.** Guarda métricas, parámetros y artefactos para saber qué modelo generó cada resultado.
3. **Automatizar el flujo.** SageMaker Pipelines puede ayudarte a encadenar preparación, entrenamiento y evaluación.
4. **Elegir una forma de inferencia.** Un endpoint puede responder solicitudes en tiempo real; para procesar muchos registros de una vez, *batch transform* escribe las predicciones en S3.
5. **Monitorear el comportamiento.** Revisa tanto la disponibilidad del servicio como la calidad de las predicciones cuando dispongas de resultados reales.

La elección depende de la aplicación. Si necesitas una predicción para cada solicitud de usuario, un endpoint puede tener sentido. Si produces un informe diario, procesar un lote puede ser suficiente. La [guía de despliegue de AWS](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model-get-started.html) describe estas opciones.

## No olvides apagar los recursos

Al terminar, guarda tu trabajo y detén o elimina los recursos que ya no necesites desde la consola o Studio: aplicaciones de JupyterLab, endpoints y otros recursos que hayas creado. Revisa también el almacenamiento y los archivos de S3 si corresponden.

**Cerrar la pestaña del navegador no garantiza que el cómputo se detenga.** Comprueba el estado de los recursos y revisa la facturación después del experimento.

## Próximos pasos

Ya recorriste un primer flujo de ML en SageMaker Studio: exploraste datos, separaste ejemplos de entrenamiento y prueba, entrenaste un clasificador e interpretaste sus resultados.

Para seguir aprendiendo, prueba a cambiar el modelo o sus parámetros y compara las métricas. Después, sustituye Iris por un conjunto de datos propio y pregúntate qué preparación necesita, qué errores son más importantes y cómo sabrías si el modelo sigue funcionando con el tiempo.

Cuando ese flujo te resulte familiar, el siguiente paso natural es convertir el entrenamiento del notebook en un trabajo administrado y explorar las opciones de despliegue. ¡Feliz entrenamiento!
