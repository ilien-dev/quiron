Si llevas un tiempo programando, seguro que has oído (o dicho) la frase: *"en mi máquina funciona"*. Docker nació precisamente para acabar con ella. En este post vemos qué es, qué conceptos necesitas conocer y cómo arrancar tu primer contenedor.

## ¿Qué es Docker?

Docker es una plataforma que permite empaquetar una aplicación junto con todo lo que necesita para ejecutarse (runtime, librerías, dependencias del sistema y configuración) en una unidad llamada **contenedor**. Ese contenedor se ejecuta igual en tu portátil, en el de tu compañera y en el servidor de producción.

## Contenedores vs. máquinas virtuales

La comparación es inevitable. Una máquina virtual incluye un sistema operativo completo sobre un hipervisor, por lo que pesa gigas y tarda en arrancar. Un contenedor, en cambio, comparte el kernel del sistema anfitrión y solo aísla los procesos, el sistema de ficheros y la red.

| | Máquina virtual | Contenedor |
|---|---|---|
| Arranque | Decenas de segundos o minutos | Segundos o menos |
| Tamaño | Gigas | Megas |
| Aislamiento | Completo (SO propio) | A nivel de proceso |
| Consumo | Alto | Bajo |

No son tecnologías enemigas; de hecho, es habitual ejecutar contenedores dentro de máquinas virtuales.

## Conceptos básicos

- **Imagen**: plantilla de solo lectura con la aplicación y sus dependencias. Se construye por capas.
- **Contenedor**: instancia en ejecución de una imagen. Puedes crear muchos a partir de la misma.
- **Dockerfile**: fichero de texto con las instrucciones para construir una imagen.
- **Registro**: almacén de imágenes. El más conocido es Docker Hub.
- **Volumen**: mecanismo para persistir datos más allá de la vida del contenedor.

Una analogía útil: la imagen es la clase y el contenedor es el objeto.

## Tu primer contenedor

Con Docker instalado (Docker Desktop en Windows y macOS, Docker Engine en Linux), prueba esto:

```bash
docker run hello-world
```

Docker busca la imagen en local, no la encuentra, la descarga del registro y crea un contenedor que imprime un mensaje y termina. Algo más interesante:

```bash
docker run -d -p 8080:80 --name mi-web nginx
```

Abre `http://localhost:8080` y verás Nginx funcionando sin haber instalado nada en tu sistema. La opción `-d` lo ejecuta en segundo plano y `-p` mapea el puerto 8080 de tu máquina al 80 del contenedor.

## Tu primer Dockerfile

Supongamos una aplicación Node.js sencilla:

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "index.js"]
```

Copiar primero el `package.json` e instalar dependencias antes de copiar el resto del código permite aprovechar la caché de capas: si solo cambias el código, Docker no reinstala las dependencias.

Para construir y ejecutar:

```bash
docker build -t mi-app .
docker run -p 3000:3000 mi-app
```

## Comandos imprescindibles

```bash
docker ps              # contenedores en ejecución
docker ps -a           # todos, incluidos los parados
docker images          # imágenes locales
docker logs mi-web     # logs de un contenedor
docker exec -it mi-web sh   # abrir una shell dentro
docker stop mi-web     # parar
docker rm mi-web       # eliminar
```

## ¿Por qué merece la pena?

- **Entornos reproducibles**: el mismo comportamiento en desarrollo, pruebas y producción.
- **Onboarding rápido**: quien llega al equipo ejecuta un comando y tiene el proyecto funcionando.
- **Aislamiento**: puedes tener varias versiones de una base de datos o de un lenguaje sin conflictos.
- **Despliegue sencillo**: lo que construyes es exactamente lo que despliegas.

## Siguientes pasos

Cuando te sientas cómodo con lo anterior, el camino natural es **Docker Compose**, para definir aplicaciones con varios contenedores (por ejemplo, API más base de datos) en un único fichero YAML. Después vienen los volúmenes, las redes y las compilaciones multietapa para reducir el tamaño de las imágenes.

Docker tiene fama de complejo, pero con los conceptos de imagen, contenedor y Dockerfile ya puedes hacer mucho. La mejor forma de aprenderlo es dockerizar un proyecto propio.

¿Ya usas Docker en tu día a día? Cuéntamelo en los comentarios. 🐳
