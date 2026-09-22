---
title: "Iniciando Machine Learning en Amazon SageMaker"
published: false
description: "Guía práctica para preparar datos, entrenar un modelo y desplegarlo con Amazon SageMaker."
tags: machinelearning, aws, python, cloud
---

# Iniciando Machine Learning en Amazon SageMaker

Entrenar un modelo de *machine learning* en nuestra computadora suele ser relativamente sencillo: instalamos Python, abrimos un notebook y ejecutamos unas cuantas celdas. El desafío comienza cuando necesitamos trabajar con más datos, utilizar hardware especializado, reproducir experimentos o publicar el modelo para que otras aplicaciones puedan consumirlo.

Amazon SageMaker busca resolver precisamente ese salto entre experimentar y operar modelos en producción.

SageMaker —actualmente denominado **Amazon SageMaker AI** dentro de la oferta ampliada de AWS— es un servicio administrado para preparar datos, entrenar modelos y desplegarlos sin tener que administrar directamente servidores, clústeres o infraestructura de inferencia.

En este tutorial recorreremos un flujo completo:

1. Crear un entorno de trabajo.
2. Preparar y almacenar datos.
3. Ejecutar un trabajo de entrenamiento.
4. Desplegar el modelo como un endpoint.
5. Probarlo y eliminar los recursos.

Utilizaremos Python, Scikit-learn y el clásico conjunto de datos Iris. Aunque el ejemplo es pequeño, el flujo es prácticamente el mismo que usaríamos con un proyecto real.

## El modelo mental de SageMaker

Antes de escribir código conviene entender sus componentes principales.

**SageMaker Studio** es el entorno visual desde el que podemos abrir notebooks, administrar experimentos y acceder a las herramientas de desarrollo.

**Amazon S3** almacena los datos de entrada y los artefactos generados. En SageMaker, los datasets normalmente no viven dentro del notebook: se guardan en S3 para que los trabajos independientes puedan acceder a ellos.

Un **training job** crea infraestructura temporal, descarga los datos, ejecuta nuestro código de entrenamiento, guarda el modelo resultante y apaga la instancia al terminar.

Un **endpoint** mantiene una o más instancias disponibles para recibir predicciones en tiempo real mediante una API administrada.

El flujo general se ve así:

```text
Notebook → Datos en S3 → Training Job → Modelo en S3 → Endpoint
```

Esta separación es importante. El notebook funciona como centro de control, pero el entrenamiento y la inferencia pueden ejecutarse en recursos independientes.

## Requisitos iniciales

Necesitaremos:

- Una cuenta de AWS.
- Una región compatible con SageMaker.
- Un dominio o espacio de SageMaker Studio.
- Un rol de IAM con acceso a SageMaker y al bucket de S3 utilizado.
- Conocimientos básicos de Python y Scikit-learn.

Desde la consola de AWS podemos buscar **Amazon SageMaker AI** y seguir la configuración guiada de Studio. Para aprender, la configuración rápida suele ser suficiente. En un entorno corporativo conviene crear roles y políticas de IAM específicos, aplicando el principio de mínimo privilegio.

Una vez dentro de Studio, abrimos un notebook de Python. Debemos revisar el tipo de instancia seleccionado: incluso un notebook inactivo puede generar costos si su aplicación o espacio continúa ejecutándose.

## Preparar el dataset

Comenzamos importando Iris, separando los datos de entrenamiento y prueba, y creando un archivo CSV.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import pandas as pd

iris = load_iris()

X_train, X_test, y_train, y_test = train_test_split(
    iris.data,
    iris.target,
    test_size=0.2,
    random_state=42,
    stratify=iris.target,
)

train_df = pd.DataFrame(X_train, columns=iris.feature_names)
train_df["target"] = y_train
train_df.to_csv("train.csv", index=False, header=False)
```

Usar una semilla fija mediante `random_state` ayuda a que el experimento sea reproducible. En proyectos reales también deberíamos versionar los datos o, al menos, registrar exactamente qué objeto y versión de S3 se utilizaron.

Ahora subimos el archivo a S3 con el SDK de SageMaker:

```python
import sagemaker

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "tutorial-iris/data"

train_uri = session.upload_data(
    path="train.csv",
    bucket=bucket,
    key_prefix=prefix,
)

print(train_uri)
```

`train_uri` tendrá una dirección similar a esta:

```text
s3://sagemaker-region-cuenta/tutorial-iris/data
```

El bucket predeterminado resulta cómodo para comenzar. Para producción suele ser mejor utilizar buckets definidos explícitamente, con cifrado, control de acceso, versionado y reglas de ciclo de vida.

## Escribir el programa de entrenamiento

SageMaker puede ejecutar algoritmos integrados, contenedores propios o contenedores administrados para frameworks populares. Utilizaremos el contenedor de Scikit-learn y proporcionaremos un script llamado `train.py`.

```python
import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def model_fn(model_dir):
    return joblib.load(os.path.join(model_dir, "model.joblib"))


if __name__ == "__main__":
    training_dir = os.environ["SM_CHANNEL_TRAIN"]
    model_dir = os.environ["SM_MODEL_DIR"]

    data = pd.read_csv(
        os.path.join(training_dir, "train.csv"),
        header=None,
    )

    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
    )
    model.fit(X, y)

    predictions = model.predict(X)
    accuracy = accuracy_score(y, predictions)
    print(f"training_accuracy={accuracy:.4f}")

    joblib.dump(
        model,
        os.path.join(model_dir, "model.joblib"),
    )
```

Las variables `SM_CHANNEL_TRAIN` y `SM_MODEL_DIR` son proporcionadas automáticamente por SageMaker.

El servicio descarga el canal llamado `train` en `SM_CHANNEL_TRAIN`. Todo lo que guardemos dentro de `SM_MODEL_DIR` se comprime al finalizar y se copia a S3 como artefacto del modelo.

La función `model_fn` indica cómo reconstruir el modelo durante la inferencia. Para transformaciones más complejas también podemos implementar funciones como `input_fn`, `predict_fn` y `output_fn`.

## Ejecutar el trabajo de entrenamiento

Desde el notebook creamos un estimador de Scikit-learn:

```python
from sagemaker import get_execution_role
from sagemaker.sklearn.estimator import SKLearn

role = get_execution_role()

estimator = SKLearn(
    entry_point="train.py",
    role=role,
    instance_count=1,
    instance_type="ml.m5.large",
    framework_version="1.2-1",
    py_version="py3",
    base_job_name="iris-random-forest",
)
```

La versión del framework disponible puede variar por región y evolucionar con el tiempo. Conviene consultar la lista de [versiones compatibles de Scikit-learn](https://docs.aws.amazon.com/sagemaker/latest/dg/sklearn.html) antes de elegirla.

Iniciamos el entrenamiento pasando la ubicación de los datos:

```python
estimator.fit({
    "train": train_uri
})
```

Al ejecutar `fit`, SageMaker realiza varias tareas:

- Crea una instancia de entrenamiento.
- Descarga el contenedor de Scikit-learn.
- Obtiene los datos desde S3.
- Ejecuta `train.py`.
- Captura los logs y métricas en CloudWatch.
- Guarda el modelo en S3.
- Elimina la instancia de entrenamiento.

El notebook espera de forma predeterminada hasta que termine el trabajo. También podemos iniciarlo de manera asíncrona utilizando `wait=False`.

La dirección del artefacto generado está disponible mediante:

```python
print(estimator.model_data)
```

## Desplegar el modelo

Ahora convertimos el resultado del entrenamiento en un endpoint HTTPS administrado:

```python
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    endpoint_name="iris-demo-endpoint",
)
```

Este paso puede tardar varios minutos. SageMaker prepara el contenedor, descarga `model.tar.gz` desde S3 y crea la infraestructura de inferencia.

Cuando el endpoint esté activo, podemos enviar algunas observaciones:

```python
predictions = predictor.predict(X_test[:5])

for expected, predicted in zip(y_test[:5], predictions):
    print({
        "esperado": int(expected),
        "prediccion": int(predicted),
    })
```

En una aplicación real no llamaríamos normalmente al endpoint desde el mismo notebook. Un backend podría invocarlo mediante el SDK de AWS y exponer el resultado a una aplicación web, un proceso empresarial o una API pública.

No debemos hacer público el endpoint directamente. El acceso se controla mediante IAM, y la aplicación consumidora debería contar únicamente con los permisos necesarios para invocarlo.

## Evaluar antes de desplegar

Nuestro ejemplo calcula precisión sobre los mismos datos utilizados para entrenar. Esto sirve para demostrar el registro de métricas, pero no es una evaluación adecuada.

Un flujo más serio debe incluir un conjunto de validación o prueba que el modelo no haya visto. También debemos observar métricas apropiadas para el problema:

- Precisión, *recall* y F1 para clasificación.
- MAE o RMSE para regresión.
- AUC cuando importa el balance entre verdaderos y falsos positivos.
- Métricas separadas por grupos relevantes para detectar sesgos.
- Latencia, errores y costo durante la inferencia.

SageMaker ofrece herramientas adicionales para procesamiento, ajuste de hiperparámetros, seguimiento de experimentos, pipelines, monitoreo y registro de modelos. No es necesario adoptarlas todas desde el primer día. Es mejor comenzar con un flujo comprensible y añadir automatización conforme aparezcan necesidades reales.

## Costos y limpieza

Un error frecuente al aprender AWS es finalizar el código pero dejar el endpoint ejecutándose. Los endpoints en tiempo real generan cargos mientras mantienen instancias aprovisionadas, aunque no reciban solicitudes.

Cuando terminemos la práctica debemos eliminarlo:

```python
predictor.delete_endpoint()
```

También conviene revisar:

- Aplicaciones y espacios activos en SageMaker Studio.
- Modelos y configuraciones de endpoints que ya no se utilizan.
- Objetos almacenados en S3.
- Logs de CloudWatch.
- Notebooks, trabajos de procesamiento y otros recursos asociados.

Para cargas intermitentes podemos evaluar alternativas como inferencia sin servidor o transformaciones por lotes. Un endpoint en tiempo real tiene sentido cuando necesitamos baja latencia y tráfico relativamente constante.

Configurar presupuestos y alertas de facturación desde el inicio es una excelente práctica, incluso en cuentas destinadas al aprendizaje.

## Del tutorial a producción

Entrenar y desplegar un modelo es solo una parte del sistema. Un proyecto mantenible también necesita:

- Versionar código, datos y parámetros.
- Separar ambientes de desarrollo y producción.
- Automatizar validaciones antes del despliegue.
- Registrar la procedencia de cada modelo.
- Cifrar información sensible.
- Limitar permisos mediante IAM.
- Monitorear calidad, latencia y desviación de datos.
- Definir cómo regresar a una versión anterior.
- Eliminar automáticamente recursos temporales.

SageMaker facilita muchas de estas tareas, pero no reemplaza las decisiones de arquitectura ni las buenas prácticas de ingeniería.

## Conclusión

Amazon SageMaker permite pasar de un experimento local a un flujo administrado sin construir toda la infraestructura desde cero. En este recorrido preparamos datos, los subimos a S3, ejecutamos entrenamiento en una instancia temporal, generamos un artefacto y publicamos el modelo mediante un endpoint.

El punto más importante no es el algoritmo utilizado, sino la separación de responsabilidades: almacenamiento, entrenamiento e inferencia se convierten en componentes independientes y reproducibles.

Como siguiente paso, podemos reemplazar Iris por un dataset propio, agregar un conjunto de validación, registrar métricas con SageMaker Experiments y automatizar el proceso mediante SageMaker Pipelines. Con esa base estaremos mucho más cerca de un sistema de *machine learning* listo para evolucionar de manera segura.