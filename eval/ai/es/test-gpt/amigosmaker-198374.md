# Python Flask vs Bottle (Spanish)

Cuando queremos crear una aplicación web con Python, dos de las opciones más ligeras son **Flask** y **Bottle**. Ambos son microframeworks: ofrecen una base sencilla para recibir peticiones HTTP, definir rutas y generar respuestas sin imponer la estructura de un framework completo como Django.

Aunque parecen similares, Flask y Bottle están pensados para necesidades ligeramente distintas. Veamos sus principales diferencias.

## ¿Qué es Flask?

Flask es uno de los microframeworks más populares del ecosistema Python. Su núcleo es pequeño, pero puede ampliarse mediante extensiones para añadir autenticación, acceso a bases de datos, validación de formularios, migraciones y muchas otras funciones.

Una aplicación mínima se ve así:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def inicio():
    return "¡Hola desde Flask!"

if __name__ == "__main__":
    app.run(debug=True)
```

Flask incluye un servidor de desarrollo, integración con el motor de plantillas Jinja y herramientas para gestionar peticiones, respuestas, cookies y sesiones.

Su mayor ventaja es el equilibrio entre simplicidad y capacidad de crecimiento. Podemos comenzar con un único archivo y, cuando el proyecto aumente de tamaño, dividirlo en módulos, usar *blueprints* y añadir extensiones.

## ¿Qué es Bottle?

Bottle es un microframework todavía más pequeño. Se distribuye como un solo archivo de Python y no necesita dependencias externas para sus funciones básicas. Esto lo convierte en una alternativa atractiva para prototipos, scripts, servicios internos y entornos con recursos limitados.

Una aplicación básica con Bottle sería:

```python
from bottle import route, run

@route("/")
def inicio():
    return "¡Hola desde Bottle!"

run(host="localhost", port=8080, debug=True)
```

La filosofía de Bottle es ofrecer lo necesario para construir una aplicación web sencilla sin complicaciones. Incluye enrutamiento, plantillas, acceso a formularios y soporte para distintos servidores WSGI.

## Flask vs Bottle

La primera diferencia importante es el **ecosistema**. Flask cuenta con una comunidad más grande, abundante documentación, numerosos tutoriales y una amplia colección de extensiones. Si necesitamos integrar SQLAlchemy, autenticación, APIs REST o validación avanzada, probablemente encontraremos una solución conocida.

Bottle posee un ecosistema más reducido. Esto no significa que sea incapaz, pero ciertas integraciones pueden requerir más trabajo manual. Para proyectos pequeños, esa limitación quizá ni siquiera importe.

Otra diferencia es la **distribución**. Bottle puede ejecutarse desde un único archivo, algo especialmente cómodo en herramientas portátiles, demostraciones o dispositivos limitados. Flask requiere instalar el paquete y sus dependencias, aunque este proceso sigue siendo muy sencillo mediante `pip`.

En cuanto a las **plantillas**, Flask utiliza Jinja, una opción potente, popular y ampliamente documentada. Bottle incorpora su propio sistema, SimpleTemplate, adecuado para casos básicos, pero menos extendido.

Respecto al **rendimiento**, los dos pueden ofrecer buenos resultados para aplicaciones pequeñas. Sin embargo, la velocidad del framework rara vez es el factor decisivo: la base de datos, las consultas externas, la arquitectura y el servidor de producción suelen tener un impacto mucho mayor.

## ¿Cuál deberías elegir?

Elige **Flask** si:

- Quieres construir una aplicación que podría crecer.
- Necesitas extensiones e integraciones conocidas.
- Valoras una comunidad amplia y abundante documentación.
- Trabajarás con varias personas o módulos.

Elige **Bottle** si:

- Necesitas una aplicación extremadamente pequeña.
- Quieres distribuir todo en un solo archivo.
- Estás creando un prototipo, una herramienta interna o una API sencilla.
- Prefieres reducir al mínimo las dependencias.

## Conclusión

Flask es generalmente la opción más versátil y segura para proyectos profesionales, especialmente cuando no conocemos todavía su alcance final. Bottle destaca por su sencillez radical y por permitir desarrollar servicios pequeños con muy poco código.

No existe un ganador absoluto. Flask ofrece un camino de crecimiento más claro, mientras que Bottle resulta excelente cuando la portabilidad y el tamaño mínimo son prioritarios. La mejor elección dependerá menos de cuál sea “más rápido” y más de cuánto esperamos que evolucione nuestra aplicación.