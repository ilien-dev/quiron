En la [primera parte](#) vimos qué es Docker, la diferencia entre una **imagen** y un **contenedor**, y ejecutamos nuestros primeros comandos como `docker run`, `docker ps` y `docker pull`. Hoy damos un paso más: vamos a **construir nuestra propia imagen**, exponer una aplicación al exterior, guardar datos que sobrevivan a los contenedores y, por último, orquestar varios servicios con **Docker Compose**.

## Repaso rápido

Antes de empezar, recordemos dos ideas clave:

- Una **imagen** es una plantilla de solo lectura: contiene el sistema de archivos, las dependencias y la configuración necesarias para ejecutar algo.
- Un **contenedor** es una instancia en ejecución de esa imagen. Puedes tener muchos contenedores a partir de la misma imagen, y cada uno está aislado de los demás.

Hasta ahora hemos usado imágenes que otras personas publicaron en Docker Hub. Ahora vamos a crear la nuestra.

## Nuestra aplicación de ejemplo

Usaremos una API mínima en Node.js. Crea una carpeta llamada `mi-api` con estos dos archivos:

**package.json**

```json
{
  "name": "mi-api",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.19.2"
  }
}
```

**index.js**

```javascript
const express = require("express");
const app = express();
const PORT = process.env.PORT || 3000;

app.get("/", (req, res) => {
  res.json({ mensaje: "¡Hola desde Docker!" });
});

app.listen(PORT, () => console.log(`Escuchando en el puerto ${PORT}`));
```

## El Dockerfile

Un **Dockerfile** es un archivo de texto con las instrucciones para construir una imagen. Crea un archivo llamado `Dockerfile` (sin extensión) en la misma carpeta:

```dockerfile
FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

Vamos línea por línea:

- `FROM`: la imagen base. Partimos de Node 22 sobre Alpine, una distribución Linux muy ligera.
- `WORKDIR`: el directorio de trabajo dentro del contenedor. Si no existe, se crea.
- `COPY package*.json ./`: copiamos primero solo los archivos de dependencias.
- `RUN`: ejecuta un comando durante la construcción. Aquí instalamos las dependencias.
- `COPY . .`: copiamos el resto del código.
- `EXPOSE`: documenta que la aplicación escucha en el puerto 3000. Ojo: **no** publica el puerto por sí solo.
- `CMD`: el comando que se ejecuta al arrancar el contenedor.

### ¿Por qué copiar `package.json` por separado?

Docker construye las imágenes **por capas**, y cada instrucción genera una capa que se guarda en caché. Si copiamos primero `package.json` e instalamos dependencias, esa capa solo se reconstruye cuando cambian las dependencias. Si modificas `index.js`, Docker reutiliza la caché y la construcción es mucho más rápida.

### El archivo .dockerignore

Igual que `.gitignore`, evita que se copien archivos innecesarios a la imagen:

```
node_modules
npm-debug.log
.git
.env
```

Esto reduce el tamaño de la imagen y evita filtrar archivos sensibles como `.env`.

## Construir y ejecutar la imagen

Desde la carpeta del proyecto:

```bash
docker build -t mi-api:1.0 .
```

La opción `-t` asigna un nombre y una etiqueta (`tag`) a la imagen. El punto final indica el **contexto de construcción**: la carpeta actual.

Comprueba que existe:

```bash
docker images
```

Y ahora ejecútala:

```bash
docker run -d -p 8080:3000 --name api mi-api:1.0
```

- `-d` ejecuta el contenedor en segundo plano.
- `-p 8080:3000` publica el puerto: el 8080 de tu máquina se conecta al 3000 del contenedor.
- `--name` le da un nombre legible.

Abre `http://localhost:8080` en tu navegador y verás el mensaje en JSON. 🎉

Para ver los logs:

```bash
docker logs -f api
```

## Volúmenes: datos que sobreviven

Los contenedores son **efímeros**: si eliminas uno, todo lo que se escribió dentro desaparece. Para datos persistentes, como una base de datos, usamos **volúmenes**.

```bash
docker volume create datos-postgres

docker run -d \
  --name db \
  -e POSTGRES_PASSWORD=secreto \
  -v datos-postgres:/var/lib/postgresql/data \
  postgres:16
```

Ahora, aunque borres el contenedor `db` y crees otro con el mismo volumen, los datos seguirán ahí.

También existen los **bind mounts**, que montan una carpeta de tu máquina dentro del contenedor. Son muy útiles en desarrollo para ver los cambios del código al instante:

```bash
docker run -v ${PWD}:/app mi-api:1.0
```

## Docker Compose: varios servicios a la vez

Cuando tu aplicación necesita una API, una base de datos y quizás una caché, escribir todos esos `docker run` se vuelve tedioso. **Docker Compose** permite describirlo todo en un archivo `compose.yaml`:

```yaml
services:
  api:
    build: .
    ports:
      - "8080:3000"
    environment:
      - DATABASE_URL=postgres://postgres:secreto@db:5432/postgres
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      - POSTGRES_PASSWORD=secreto
    volumes:
      - datos-postgres:/var/lib/postgresql/data

volumes:
  datos-postgres:
```

Fíjate en un detalle importante: la API se conecta a la base de datos usando el host `db`, que es el nombre del servicio. Compose crea una red interna donde los servicios se encuentran por su nombre.

Para levantarlo todo:

```bash
docker compose up -d
```

Y para pararlo:

```bash
docker compose down
```

Si además quieres borrar los volúmenes, añade `-v`. ¡Cuidado, perderás los datos!

## Comandos útiles de limpieza

Con el tiempo se acumulan imágenes y contenedores que ya no usas:

```bash
docker container prune   # elimina contenedores detenidos
docker image prune       # elimina imágenes sin etiqueta
docker system df         # muestra cuánto espacio ocupa Docker
```

## Conclusión

En esta segunda parte hemos aprendido a:

1. Escribir un **Dockerfile** y aprovechar la caché de capas.
2. Construir imágenes con `docker build` y publicar puertos con `-p`.
3. Persistir información con **volúmenes** y **bind mounts**.
4. Orquestar varios servicios con **Docker Compose**.

En la próxima entrega veremos **builds multi-etapa** para crear imágenes más pequeñas, buenas prácticas de seguridad y cómo publicar tus imágenes en un registro.

¿Tienes dudas o algún truco que quieras compartir? ¡Déjalo en los comentarios! 🐳
