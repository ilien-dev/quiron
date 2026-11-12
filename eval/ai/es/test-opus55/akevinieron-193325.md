Si llevas un tiempo en el mundo del desarrollo, seguro que has escuchado (o dicho) la famosa frase: **"En mi máquina funciona"**. Docker nació, en gran parte, para que esa frase deje de existir. En este post veremos qué es Docker, qué problemas resuelve y cómo empezar a usarlo en pocos minutos.

## ¿Qué es Docker?

Docker es una plataforma que permite **empaquetar una aplicación junto con todas sus dependencias** (librerías, runtime, configuración, herramientas del sistema) en una unidad llamada **contenedor**. Ese contenedor se ejecuta igual en tu portátil, en el servidor de tu empresa o en la nube.

Piensa en un contenedor como en una caja estandarizada: no importa qué haya dentro, cualquier "barco" (máquina con Docker) sabe cómo transportarla y ejecutarla.

## Contenedores vs. máquinas virtuales

Es habitual confundir contenedores con máquinas virtuales, pero no son lo mismo:

- **Máquina virtual:** incluye un sistema operativo completo, con su propio kernel. Es pesada, tarda en arrancar y consume bastantes recursos.
- **Contenedor:** comparte el kernel del sistema anfitrión y solo aísla los procesos, el sistema de archivos y la red. Es ligero, arranca en segundos (o menos) y puedes ejecutar decenas en una sola máquina.

Esto no significa que las VMs sean malas; simplemente resuelven problemas distintos. Para empaquetar y desplegar aplicaciones, los contenedores suelen ser la opción más práctica.

## Conceptos clave

Antes de escribir comandos, conviene tener claro el vocabulario básico:

- **Imagen:** una plantilla de solo lectura con todo lo necesario para ejecutar una aplicación. Por ejemplo, una imagen de `node:20` o de `postgres:16`.
- **Contenedor:** una instancia en ejecución de una imagen. Puedes crear muchos contenedores a partir de la misma imagen.
- **Dockerfile:** un archivo de texto con las instrucciones para construir una imagen.
- **Registro (Registry):** un lugar donde se almacenan y comparten imágenes. El más conocido es **Docker Hub**.

## Tus primeros comandos

Una vez instalado Docker (Docker Desktop en Windows/macOS o Docker Engine en Linux), prueba lo siguiente:

    docker run hello-world

Este comando descarga una imagen de prueba y la ejecuta. Si ves un mensaje de bienvenida, todo funciona.

Ahora algo más útil: levantar un servidor web Nginx.

    docker run -d -p 8080:80 --name mi-nginx nginx

- `-d` lo ejecuta en segundo plano.
- `-p 8080:80` mapea el puerto 8080 de tu máquina al 80 del contenedor.
- `--name` le asigna un nombre fácil de recordar.

Abre `http://localhost:8080` en tu navegador y verás la página de bienvenida de Nginx.

Algunos comandos que usarás a diario:

    docker ps            # Lista los contenedores en ejecución
    docker ps -a         # Lista todos los contenedores
    docker images        # Lista las imágenes descargadas
    docker stop mi-nginx # Detiene el contenedor
    docker rm mi-nginx   # Elimina el contenedor

## Tu primer Dockerfile

Supongamos que tienes una pequeña app en Node.js. Un Dockerfile básico sería:

    FROM node:20-alpine
    WORKDIR /app
    COPY package*.json ./
    RUN npm install
    COPY . .
    EXPOSE 3000
    CMD ["node", "index.js"]

Para construir y ejecutar la imagen:

    docker build -t mi-app .
    docker run -p 3000:3000 mi-app

Y listo: tu aplicación corre en un entorno aislado y reproducible. Cualquier persona de tu equipo puede ejecutar exactamente lo mismo con esos dos comandos.

## ¿Por qué deberías aprender Docker?

- **Consistencia:** el mismo entorno en desarrollo, pruebas y producción.
- **Onboarding rápido:** un nuevo miembro del equipo no necesita instalar diez herramientas a mano.
- **Aislamiento:** puedes tener varias versiones de una base de datos o lenguaje sin conflictos.
- **Base para el futuro:** herramientas como Docker Compose, Kubernetes o muchos pipelines de CI/CD se apoyan en contenedores.

## Próximos pasos

Esto es solo la punta del iceberg. Cuando te sientas cómodo con lo básico, te recomiendo explorar:

1. **Volúmenes**, para persistir datos fuera del contenedor.
2. **Redes**, para que varios contenedores se comuniquen entre sí.
3. **Docker Compose**, para definir aplicaciones con múltiples servicios en un solo archivo.

Docker puede parecer intimidante al principio, pero con unos pocos comandos ya puedes sacarle mucho partido. ¡Anímate a "dockerizar" tu próximo proyecto!

¿Usas Docker en tu día a día? Cuéntame en los comentarios qué fue lo que más te costó entender al empezar. 🐳
