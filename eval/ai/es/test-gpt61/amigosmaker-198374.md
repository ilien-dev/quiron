# Python Flask vs Bottle (Spanish)

Elegir un framework web en Python puede convertirse en una investigación interminable. Si buscas algo ligero, Flask y Bottle aparecen pronto entre las opciones. Ambos permiten crear aplicaciones con pocas líneas de código, pero sus prioridades son diferentes.

La pregunta útil es: **¿cuál encaja mejor con el tamaño, las dependencias y la evolución de tu proyecto?**

**Dos formas de entender el minimalismo**

Flask es un microframework que proporciona una base para desarrollar aplicaciones web sin imponer toda su arquitectura. Utiliza Werkzeug para funciones relacionadas con HTTP y WSGI, Jinja para plantillas y Click para su interfaz de comandos. Puedes consultar sus componentes en la [documentación oficial](https://flask.palletsprojects.com/en/stable/).

Bottle lleva la sencillez de distribución un paso más allá: su núcleo se distribuye como un único archivo y no requiere dependencias externas a la biblioteca estándar de Python. También incluye rutas, acceso a solicitudes y respuestas, y un motor de plantillas. Así lo describe su [documentación oficial](https://bottlepy.org/docs/stable/).

Esto hace que Bottle resulte atractivo cuando quieres incorporar una interfaz web pequeña a una herramienta existente.

**El primer endpoint**

En Flask, una aplicación mínima puede verse así:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/saludo/<nombre>")
def saludo(nombre):
    return {"mensaje": f"Hola, {nombre}"}

if __name__ == "__main__":
    app.run()
```

En Bottle, el equivalente es muy parecido:

```python
from bottle import Bottle

app = Bottle()

@app.route("/saludo/<nombre>")
def saludo(nombre):
    return {"mensaje": f"Hola, {nombre}"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
```

En ambos ejemplos, visitar `/saludo/Ana` devuelve una respuesta JSON con un saludo. La diferencia inicial de esfuerzo es pequeña: ambos permiten conectar una URL con una función de Python de manera directa.

Estos ejemplos utilizan servidores de desarrollo. Para publicar una aplicación, conviene revisar las opciones de despliegue de [Flask](https://flask.palletsprojects.com/en/stable/deploying/) y [Bottle](https://bottlepy.org/docs/stable/deployment.html).

**Cuando la aplicación crece**

La decisión empieza a importar más cuando aparecen usuarios, permisos, formularios, persistencia y pruebas.

Flask ofrece mecanismos como los *blueprints* para dividir una aplicación en componentes. Su documentación también presenta el patrón de fábricas de aplicaciones, útil para crear instancias con distintas configuraciones. Estas herramientas ayudan a organizar proyectos que acumulan funcionalidades. Puedes profundizar en sus [patrones de aplicaciones](https://flask.palletsprojects.com/en/stable/patterns/).

Bottle permite organizar código en módulos, utilizar plugins y combinar aplicaciones. Que su núcleo viva en un archivo no significa que tu proyecto deba hacerlo. Sin embargo, tendrás que decidir cómo estructurar las distintas piezas según tus necesidades. Su [tutorial](https://bottlepy.org/docs/stable/tutorial.html) explica estas posibilidades.

Mi criterio sería elegir Flask si espero incorporar varias áreas funcionales y mantener el proyecto entre varias personas. Consideraría Bottle si el servicio tiene un alcance pequeño y bien definido.

**Dependencias y rendimiento**

Tener menos dependencias puede simplificar la distribución, especialmente en herramientas internas o entornos controlados. Esa ventaja pierde peso si la aplicación necesita después numerosas bibliotecas adicionales.

Tampoco elegiría por la promesa de que uno será automáticamente más rápido. El rendimiento depende de las consultas a la base de datos, las llamadas externas, la serialización y la configuración del servidor.

Antes de optimizar el framework, mediría una operación representativa de la aplicación.

**¿Cuál elegiría?**

Para un panel interno pequeño, un prototipo acotado o una interfaz HTTP para un script, empezaría evaluando Bottle.

Para una aplicación con varias funcionalidades, integraciones y crecimiento previsto, empezaría evaluando Flask.

Si estás aprendiendo, ambos sirven para practicar rutas, solicitudes y respuestas. Puedes implementar el mismo pequeño servicio en los dos: esa comparación enseña más que discutir cuál gana en abstracto.

**La mejor elección es la que reduce trabajo durante la vida real de tu proyecto.**
