# Docker - Introducción

Si llevas un tiempo en el mundo del desarrollo, seguramente has escuchado la frase "en mi máquina funciona". Es uno de los problemas más clásicos del software: una aplicación que corre perfectamente en el portátil del desarrollador falla en el servidor de pruebas o en producción porque la versión de una librería es distinta, falta una dependencia del sistema o la configuración no coincide. Docker nació precisamente para resolver este problema.

En este post vamos a ver qué es Docker, cuáles son sus conceptos básicos y cómo dar los primeros pasos con él.

## ¿Qué es Docker?

Docker es una plataforma de código abierto que permite empaquetar una aplicación junto con todas sus dependencias en una unidad estandarizada llamada **contenedor**. Ese contenedor puede ejecutarse de la misma forma en cualquier máquina que tenga Docker instalado, ya sea tu portátil, un servidor en la nube o el equipo de un compañero.

La idea es sencilla: en lugar de instalar la aplicación y sus dependencias directamente en el sistema operativo, las metes en una "caja" aislada que contiene todo lo necesario para funcionar.

## Contenedores vs. máquinas virtuales

Es común confundir los contenedores con las máquinas virtuales, pero hay una diferencia importante.

Una **máquina virtual** emula un equipo completo, incluyendo su propio sistema operativo. Esto implica que cada máquina virtual necesita varios gigabytes de espacio, bastante memoria y tarda en arrancar.

Un **contenedor**, en cambio, comparte el kernel del sistema operativo anfitrión y solo aísla los procesos, el sistema de archivos y la red de la aplicación. El resultado es que los contenedores:

- Arrancan en segundos (o menos).
- Ocupan mucho menos espacio.
- Consumen menos recursos.
- Permiten ejecutar muchas más instancias en el mismo hardware.

## Conceptos clave

Antes de empezar a escribir comandos, conviene tener claros algunos términos:

**Imagen**: es una plantilla de solo lectura que contiene el sistema de archivos y la configuración necesarios para ejecutar una aplicación. Puedes pensar en ella como una "receta" o como una clase en programación orientada a objetos.

**Contenedor**: es una instancia en ejecución de una imagen. Siguiendo la analogía anterior, sería el objeto creado a partir de la clase. Puedes tener muchos contenedores a partir de la misma imagen.

**Dockerfile**: es un archivo de texto con las instrucciones para construir una imagen.

**Docker Hub**: es un registro público donde se almacenan y comparten imágenes. Allí encontrarás imágenes oficiales de Ubuntu, Node.js, PostgreSQL, Nginx y muchísimas más.

## Instalación

Docker está disponible para Linux, macOS y Windows. En macOS y Windows lo más sencillo es instalar **Docker Desktop** desde la web oficial. En Linux puedes instalarlo desde el gestor de paquetes de tu distribución. Por ejemplo, en Ubuntu:

```bash
sudo apt update
sudo apt install docker.io
```

Para comprobar que todo funciona:

```bash
docker --version
```

## Tu primer contenedor

El clásico "hola mundo" de Docker es este:

```bash
docker run hello-world
```

Al ejecutarlo, Docker busca la imagen `hello-world` en tu máquina. Como no la encuentra, la descarga de Docker Hub, crea un contenedor a partir de ella y lo ejecuta. Verás un mensaje explicando precisamente estos pasos.

Probemos algo un poco más interesante:

```bash
docker run -it ubuntu bash
```

Este comando descarga la imagen de Ubuntu y te abre una terminal dentro del contenedor. Puedes ejecutar comandos como si estuvieras en una máquina Ubuntu. Cuando escribas `exit`, el contenedor se detendrá.

## Comandos básicos

Estos son algunos de los comandos que usarás con más frecuencia:

```bash
docker ps            # Lista los contenedores en ejecución
docker ps -a         # Lista todos los contenedores, incluidos los detenidos
docker images        # Lista las imágenes descargadas
docker stop <id>     # Detiene un contenedor
docker rm <id>       # Elimina un contenedor
docker rmi <imagen>  # Elimina una imagen
```

## Conclusión

Docker ha cambiado la forma en que desarrollamos, probamos y desplegamos aplicaciones. Gracias a los contenedores, podemos garantizar que el entorno sea el mismo en todas partes y olvidarnos del famoso "en mi máquina funciona".

En la próxima parte veremos cómo crear nuestras propias imágenes con un Dockerfile y cómo exponer puertos para ejecutar una aplicación web dentro de un contenedor. ¡Nos vemos!
