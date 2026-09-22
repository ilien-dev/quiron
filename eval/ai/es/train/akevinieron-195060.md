# Docker - Introducción parte 2

En la primera parte de esta serie vimos qué es Docker, en qué se diferencia un contenedor de una máquina virtual y cómo ejecutar nuestros primeros contenedores a partir de imágenes de Docker Hub. Ahora toca dar el siguiente paso: **crear nuestras propias imágenes**.

En este post vamos a escribir un Dockerfile, construir una imagen para una pequeña aplicación en Node.js, ejecutarla exponiendo un puerto y aprender a trabajar con volúmenes.

## La aplicación

Vamos a usar un servidor muy simple con Express. Crea una carpeta llamada `mi-app` y dentro un archivo `package.json`:

```json
{
  "name": "mi-app",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.19.0"
  }
}
```

Y un archivo `index.js`:

```javascript
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('¡Hola desde un contenedor Docker!');
});

app.listen(PORT, () => {
  console.log(`Servidor escuchando en el puerto ${PORT}`);
});
```

Fíjate en que no hace falta tener Node.js instalado en tu máquina. Todo se ejecutará dentro del contenedor.

## El Dockerfile

Un Dockerfile es un archivo de texto con las instrucciones para construir una imagen. Crea un archivo llamado exactamente `Dockerfile` (sin extensión) en la carpeta del proyecto:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

Vamos línea por línea:

- **`FROM node:20-alpine`**: indica la imagen base. Partimos de una imagen oficial que ya tiene Node.js 20 instalado sobre Alpine Linux, una distribución muy ligera.
- **`WORKDIR /app`**: establece el directorio de trabajo dentro del contenedor. Los comandos siguientes se ejecutarán desde ahí.
- **`COPY package*.json ./`**: copia `package.json` (y `package-lock.json` si existe) al contenedor.
- **`RUN npm install`**: instala las dependencias. `RUN` se ejecuta durante la construcción de la imagen.
- **`COPY . .`**: copia el resto del código.
- **`EXPOSE 3000`**: documenta que la aplicación escucha en el puerto 3000. Ojo: no publica el puerto por sí mismo, solo es informativo.
- **`CMD ["npm", "start"]`**: el comando que se ejecutará al arrancar el contenedor.

### ¿Por qué copiar package.json por separado?

Docker construye las imágenes por **capas**, y cada instrucción genera una. Si una capa no ha cambiado, Docker la reutiliza de la caché. Al copiar primero solo el `package.json` e instalar las dependencias, conseguimos que `npm install` solo se vuelva a ejecutar cuando cambien las dependencias, no cada vez que modifiquemos una línea de código. Esto acelera muchísimo las construcciones.

## El archivo .dockerignore

Igual que `.gitignore`, el archivo `.dockerignore` indica qué no debe copiarse al contenedor:

```
node_modules
npm-debug.log
.git
```

Sobre todo es importante excluir `node_modules`, porque las dependencias se instalan dentro del contenedor.

## Construir la imagen

Desde la carpeta del proyecto:

```bash
docker build -t mi-app:1.0 .
```

- `-t mi-app:1.0` le da un nombre (`mi-app`) y una etiqueta (`1.0`) a la imagen.
- El `.` final indica el contexto de construcción, es decir, la carpeta actual.

Comprueba que se ha creado:

```bash
docker images
```

## Ejecutar el contenedor

```bash
docker run -d -p 8080:3000 --name servidor mi-app:1.0
```

- `-d` ejecuta el contenedor en segundo plano (*detached*).
- `-p 8080:3000` mapea el puerto 8080 de tu máquina al 3000 del contenedor.
- `--name servidor` le asigna un nombre para no tener que usar el ID.

Abre `http://localhost:8080` en el navegador y verás el mensaje de bienvenida.

Para ver los logs:

```bash
docker logs -f servidor
```

Y para detenerlo y eliminarlo:

```bash
docker stop servidor
docker rm servidor
```

## Variables de entorno

Puedes pasar variables de entorno al contenedor con `-e`:

```bash
docker run -d -p 8080:4000 -e PORT=4000 mi-app:1.0
```

Así la misma imagen puede configurarse de forma distinta en desarrollo y producción.

## Volúmenes: persistir datos

Los contenedores son efímeros: cuando eliminas uno, todo lo que había dentro desaparece. Para conservar datos (por ejemplo, los de una base de datos) usamos **volúmenes**:

```bash
docker volume create datos-postgres

docker run -d \
  --name db \
  -e POSTGRES_PASSWORD=secreto \
  -v datos-postgres:/var/lib/postgresql/data \
  postgres:16
```

Aunque borres el contenedor `db`, los datos seguirán en el volumen `datos-postgres` y podrás montarlos en un contenedor nuevo.

También puedes montar una carpeta de tu máquina (*bind mount*), muy útil en desarrollo para ver los cambios sin reconstruir la imagen:

```bash
docker run -d -p 8080:3000 -v $(pwd):/app mi-app:1.0
```

## Conclusión

Ya sabes crear tus propias imágenes con un Dockerfile, construirlas, ejecutarlas con puertos y variables de entorno, y persistir datos con volúmenes. Con esto puedes dockerizar prácticamente cualquier aplicación sencilla.

En la tercera parte veremos **Docker Compose**, que nos permitirá levantar varios contenedores a la vez (por ejemplo, nuestra aplicación y una base de datos) con un único comando. ¡Hasta la próxima!
