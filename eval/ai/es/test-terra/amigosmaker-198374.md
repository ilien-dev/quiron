# Python Flask vs Bottle (Spanish)

Elegir un framework web para Python no siempre requiere comparar docenas de opciones. Si buscas crear una API pequeña, un prototipo o una aplicación web sencilla, Flask y Bottle son dos alternativas ligeras que merecen atención. Ambas permiten empezar con poco código, pero toman caminos distintos cuando el proyecto crece.

## ¿Qué tienen en común?

Flask y Bottle son *microframeworks*: ofrecen las piezas esenciales para recibir solicitudes HTTP, definir rutas y devolver respuestas, sin imponer una arquitectura completa. Esa flexibilidad permite elegir las herramientas que necesita cada proyecto.

Una aplicación mínima en Flask puede verse así:

```python
from flask import Flask

app = Flask(__name__)

@app.get("/")
def inicio():
    return "¡Hola desde Flask!"

if __name__ == "__main__":
    app.run(debug=True)
```

Con Bottle, el ejemplo es igual de directo:

```python
from bottle import get, run

@get("/")
def inicio():
    return "¡Hola desde Bottle!"

run(host="localhost", port=8080, debug=True)
```

En ambos casos, una ruta asocia la dirección `/` con una función que devuelve una respuesta. La diferencia aparece cuando necesitas añadir funcionalidades y organizar la aplicación.

## Flask: flexibilidad con un ecosistema amplio

Flask es una buena opción si quieres empezar con algo pequeño y conservar espacio para crecer. Su núcleo es reducido, pero cuenta con un ecosistema amplio de extensiones para integrar bases de datos, autenticación, formularios y otras necesidades habituales.

También ofrece herramientas para organizar aplicaciones en módulos mediante *blueprints*. Esto resulta útil cuando las rutas, los modelos y la lógica de negocio dejan de caber cómodamente en unos pocos archivos.

Por ejemplo, puedes construir una API sencilla con Flask y, más adelante, añadir persistencia y autenticación sin cambiar de framework. Esa libertad también implica tomar decisiones: tendrás que elegir las bibliotecas que mejor encajen con tu proyecto y mantenerlas compatibles.

Flask suele ser una apuesta práctica para aplicaciones que evolucionarán con el tiempo, equipos que necesitan encontrar recursos de aprendizaje o proyectos que se beneficiarán de integraciones existentes.

## Bottle: simplicidad en un solo archivo

Bottle destaca por su tamaño reducido y su enfoque minimalista. El framework se distribuye como un único archivo y proporciona funciones para rutas, plantillas y acceso a datos de solicitudes.

Esta simplicidad puede ser atractiva para herramientas internas, demostraciones, pequeños servicios o proyectos educativos. Si necesitas exponer unas pocas rutas HTTP, Bottle te permite hacerlo sin introducir una estructura demasiado elaborada.

La contrapartida es que, conforme aumentan las necesidades de la aplicación, tendrás que dedicar más atención a elegir y conectar componentes. Bottle puede servir para proyectos más grandes, pero su principal atractivo está en mantener las cosas sencillas.

## ¿Cuál deberías elegir?

La decisión depende más del futuro del proyecto que del ejemplo «Hola, mundo»:

| Necesidad | Opción a considerar |
| --- | --- |
| Un prototipo o servicio muy pequeño | Bottle |
| Una aplicación que probablemente crecerá | Flask |
| Acceso a una comunidad y un ecosistema amplios | Flask |
| Una solución minimalista y fácil de transportar | Bottle |
| Aprender conceptos básicos de rutas HTTP | Cualquiera de los dos |

Ninguna de estas opciones garantiza por sí sola un mejor rendimiento o una aplicación más segura. El servidor utilizado, la configuración, las dependencias y el diseño de la aplicación también importan. En particular, los servidores de desarrollo de los ejemplos son útiles para pruebas locales; para producción necesitarás una configuración adecuada.

Si aún dudas, prueba ambos con la misma tarea: crea una API con dos o tres rutas, añade una plantilla y conecta una fuente de datos. La experiencia te mostrará rápidamente cuál encaja mejor con tu manera de trabajar.

Flask ofrece más caminos para crecer; Bottle mantiene el punto de partida lo más ligero posible. Para muchos proyectos, la mejor elección será la que permita al equipo construir, entender y mantener la aplicación con menos fricción.
