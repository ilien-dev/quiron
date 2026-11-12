Entrenar un modelo en tu computadora puede comenzar con unas cuantas líneas de Python. El reto aparece cuando necesitas repetir el entrenamiento, utilizar más recursos o conectar las predicciones con una aplicación.

Amazon SageMaker ofrece herramientas para recorrer ese camino: preparar datos, ejecutar entrenamientos y desplegar modelos sobre infraestructura administrada.

En este artículo construiremos un primer flujo de clasificación con Python y XGBoost. La idea es comprender qué ocurre en cada etapa y cómo se conectan sus componentes.

Una aclaración sobre el nombre: el servicio original pasó a llamarse **Amazon SageMaker AI** en diciembre de 2024. Amazon SageMaker ahora también identifica una plataforma más amplia de datos e inteligencia artificial. Aquí trabajaremos con SageMaker AI, aunque el SDK conserva el nombre `sagemaker`. [Documentación de AWS](https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html).

## ¿Qué vamos a construir?

Usaremos un conjunto de datos incluido en scikit-learn para clasificar tres variedades de vino según sus características químicas.

El recorrido será:

1. Preparar y dividir los datos.
2. Guardarlos en Amazon S3.
3. Entrenar un clasificador XGBoost.
4. Desplegarlo en un endpoint.
5. Evaluar sus predicciones y eliminar los recursos.

Es un ejemplo pequeño, pensado para aprender el funcionamiento del servicio. Para este volumen de datos, entrenar localmente sería suficiente; aquí utilizaremos infraestructura remota con un propósito educativo.

## Antes de comenzar

Necesitas una cuenta de AWS y acceso a SageMaker AI. Desde su consola, configura un dominio, abre Amazon SageMaker Studio y crea un espacio de JupyterLab con un notebook de Python. AWS documenta el proceso de incorporación en su [guía de dominios](https://docs.aws.amazon.com/sagemaker/latest/dg/gs-studio-onboard.html).

El entorno debe tener un rol de ejecución autorizado para utilizar los recursos del ejemplo: trabajos de entrenamiento, modelos, endpoints y el bucket de S3 correspondiente. Si trabajas en una organización, utiliza el rol y la configuración que te proporcione su administrador.

También revisa las cuotas disponibles para las instancias de entrenamiento y alojamiento. Una cuenta puede tener acceso al servicio y, aun así, carecer de cuota para cierto tipo de instancia.

**Este ejercicio crea recursos facturables.** Al terminar, eliminaremos el endpoint y revisaremos los recursos restantes.

## 1. Configurar el notebook

El código utiliza la interfaz del SDK de SageMaker para Python **2.x**. Para mantener esa compatibilidad, instala las dependencias así:

```python
%pip install "sagemaker>=2.232,<3" scikit-learn pandas
```

Si el notebook solicita reiniciar el kernel, hazlo antes de continuar.

Después, configura la sesión:

```python
import sagemaker
from sagemaker import get_execution_role

session = sagemaker.Session()
role = get_execution_role()
region = session.boto_region_name
bucket = session.default_bucket()
prefix = "primer-modelo-vinos"
```

La sesión conecta el notebook con los servicios de AWS. El rol proporciona permisos al trabajo remoto y el bucket almacenará los datos y artefactos.

`get_execution_role()` está pensado aquí para ejecutarse dentro del entorno administrado de SageMaker. Desde una computadora local necesitarías configurar las credenciales y proporcionar el ARN del rol.

## 2. Preparar los datos

En aprendizaje supervisado tenemos variables de entrada y una etiqueta conocida. Nuestro modelo aprenderá a relacionar las características químicas con la variedad de vino.

Separamos los datos antes de entrenar:

```python
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split

X, y = load_wine(return_X_y=True)

X_train, X_temp, y_train, y_temp = train_test_split(
    X, y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)
```

Reservamos aproximadamente 70 % para entrenamiento, 15 % para validación y 15 % para prueba.

El entrenamiento permite ajustar el modelo. La validación ayuda a comparar configuraciones. La prueba queda apartada para la evaluación final.

`stratify` mantiene una distribución similar de las clases entre particiones. La semilla permite repetir la división.

Si después incorporas transformaciones que aprenden de los datos, como imputación o normalización, ajústalas utilizando únicamente el conjunto de entrenamiento. Así evitas filtrar información de evaluación.

## 3. Subir los archivos a S3

Usaremos XGBoost como algoritmo integrado. Para entrenarlo con CSV, SageMaker espera la etiqueta en la primera columna y archivos sin encabezados. En inferencia, se envían solamente las características. [Formato documentado por AWS](https://docs.aws.amazon.com/sagemaker/latest/dg/xgboost-how-to-use.html).

```python
import pandas as pd

def guardar_csv(X_part, y_part, filename):
    df = pd.DataFrame(X_part)
    df.insert(0, "label", y_part)
    df.to_csv(filename, index=False, header=False)

guardar_csv(X_train, y_train, "train.csv")
guardar_csv(X_val, y_val, "validation.csv")

train_uri = session.upload_data(
    "train.csv",
    bucket=bucket,
    key_prefix=f"{prefix}/train"
)

val_uri = session.upload_data(
    "validation.csv",
    bucket=bucket,
    key_prefix=f"{prefix}/validation"
)
```

El trabajo de entrenamiento leerá estos archivos desde S3. No depende de que los datos permanezcan en la memoria del notebook.

El conjunto de prueba se queda fuera del entrenamiento.

## 4. Entrenar XGBoost

XGBoost combina árboles de decisión para resolver problemas de clasificación y regresión. Es una opción útil para experimentar con datos tabulares.

Configuramos su contenedor y el trabajo remoto:

```python
from sagemaker import image_uris
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput

image_uri = image_uris.retrieve(
    framework="xgboost",
    region=region,
    version="1.7-1"
)

estimator = Estimator(
    image_uri=image_uri,
    role=role,
    instance_count=1,
    instance_type="ml.m5.large",
    output_path=f"s3://{bucket}/{prefix}/output",
    sagemaker_session=session
)

estimator.set_hyperparameters(
    objective="multi:softprob",
    num_class=3,
    num_round=50,
    max_depth=3,
    eta=0.1,
    eval_metric="mlogloss"
)

estimator.fit({
    "train": TrainingInput(
        train_uri, content_type="text/csv"
    ),
    "validation": TrainingInput(
        val_uri, content_type="text/csv"
    )
})
```

La versión del contenedor queda explícita para facilitar la reproducción. Su disponibilidad, al igual que la del tipo de instancia, depende de la región seleccionada.

`multi:softprob` indica que queremos probabilidades para tres clases. `num_round` define las rondas de boosting; `max_depth` controla la profundidad de los árboles y `eta` regula la contribución de cada ronda.

Estos valores son un punto de partida, no una configuración óptima demostrada.

Al ejecutar `fit()`, SageMaker inicia el trabajo, prepara el entorno y guarda el modelo resultante en S3. El entrenamiento ocurre en una instancia distinta del notebook.

## 5. Publicar el modelo y evaluarlo

Ahora creamos un endpoint para recibir solicitudes:

```python
from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer

predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    serializer=CSVSerializer(),
    deserializer=JSONDeserializer()
)
```

El despliegue puede tardar varios minutos. Cuando termine, enviamos las muestras reservadas:

```python
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix

response = predictor.predict(X_test)

probabilities = np.array([
    item["score"]
    for item in response["predictions"]
])

predictions = probabilities.argmax(axis=1)

print("Accuracy:", accuracy_score(y_test, predictions))
print(confusion_matrix(y_test, predictions))
```

Cada muestra devuelve probabilidades por clase. Con `argmax` elegimos la más alta.

La exactitud expresa qué proporción de predicciones fue correcta. La matriz de confusión muestra qué variedades se confundieron entre sí.

Como el conjunto es pequeño, unos cuantos errores pueden cambiar bastante la métrica. Evita interpretar un resultado alto como garantía de rendimiento con datos reales.

## 6. Revisar errores frecuentes

Si aparece `AccessDenied`, identifica primero la operación rechazada y el recurso involucrado. Ajusta los permisos necesarios del rol.

Si recibes `ResourceLimitExceeded`, revisa las cuotas de SageMaker para ese tipo de instancia y operación.

Los errores de formato suelen venir de encabezados en el CSV, etiquetas mal ubicadas o características enviadas en un orden diferente durante la inferencia.

También comprueba que S3, el entrenamiento y el endpoint estén en la región prevista. Mantener una configuración consistente simplifica este primer ejercicio.

## 7. Eliminar los recursos

Después de evaluar, elimina el endpoint y su configuración, y después el recurso del modelo:

```python
predictor.delete_endpoint(
    delete_endpoint_config=True
)
predictor.delete_model()
```

Haz esta limpieza incluso si decides abandonar el experimento antes de terminar la evaluación.

Después, elimina de S3 los archivos y artefactos del ejercicio que ya no necesites, y detén el espacio de JupyterLab desde Studio.

Cerrar la pestaña del navegador no apaga los recursos. AWS mantiene una [guía de apagado por componente](https://docs.aws.amazon.com/sagemaker/latest/dg/sm-shut-down-resources-per-feature.html) para revisar qué sigue activo.

## El siguiente experimento

Ya recorriste un flujo completo: datos, entrenamiento remoto, despliegue, predicción y evaluación.

Ahora cambia una sola variable, como `max_depth`, compara la pérdida de validación y registra la configuración utilizada. Reserva la prueba para evaluar el modelo elegido.

Cuando puedas repetir ese proceso y explicar por qué una versión funciona mejor, tendrás una base concreta para avanzar hacia automatización, monitoreo y proyectos con datos propios.
