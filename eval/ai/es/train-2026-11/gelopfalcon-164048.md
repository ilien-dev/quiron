# Buenas prácticas en Docker

Docker es parte del día a día de casi cualquier equipo de desarrollo, pero es fácil escribir un `Dockerfile` que funcione y sea a la vez lento, pesado e inseguro. Estas son las prácticas que más impacto tienen.

## 1. Elige una imagen base pequeña y fija su versión

Evita `latest`. Hace que tus builds no sean reproducibles y puede romperte la aplicación sin avisar.

```dockerfile
# Mal
FROM node:latest

# Mejor
FROM node:22-alpine
```

Las variantes `alpine` o `slim` reducen el tamaño y la superficie de ataque. Si necesitas máxima reproducibilidad, puedes fijar incluso el digest de la imagen.

## 2. Usa builds multi-stage

Compila en una etapa y copia solo el resultado a la imagen final. Así las herramientas de build no acaban en producción.

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/package*.json ./
RUN npm ci --omit=dev
CMD ["node", "dist/index.js"]
```

El resultado suele ser una imagen mucho más ligera.

## 3. Aprovecha la caché de capas

Docker cachea cada instrucción. Ordénalas de lo que menos cambia a lo que más cambia. Copiar primero los archivos de dependencias y después el código evita reinstalar paquetes en cada cambio.

```dockerfile
COPY package*.json ./
RUN npm ci
COPY . .
```

## 4. No ejecutes como root

Por defecto, el proceso corre como `root` dentro del contenedor. Si alguien explota una vulnerabilidad, tendrá más privilegios de los necesarios.

```dockerfile
RUN addgroup -S app && adduser -S app -G app
USER app
```

## 5. Usa `.dockerignore`

Igual que `.gitignore`, evita enviar al contexto de build archivos innecesarios o sensibles:

```
node_modules
.git
.env
*.log
Dockerfile
```

Esto acelera el build y evita filtrar secretos por accidente.

## 6. Nunca metas secretos en la imagen

Las variables definidas con `ENV` o archivos copiados quedan guardados en las capas, aunque los borres después. Para secretos usa:

- Variables de entorno en tiempo de ejecución.
- Docker secrets o el gestor de secretos de tu orquestador.
- `RUN --mount=type=secret` con BuildKit si los necesitas durante el build.

## 7. Reduce el número de capas y limpia en el mismo paso

Combina comandos relacionados y elimina cachés en la misma instrucción `RUN`, o el espacio seguirá ocupado en una capa anterior.

```dockerfile
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*
```

## 8. Un proceso por contenedor

Cada contenedor debería hacer una sola cosa. Separar aplicación, base de datos y cola de mensajes facilita escalar, depurar y actualizar cada pieza. Con Docker Compose, orquestarlo en local es trivial.

## 9. Añade un `HEALTHCHECK`

Permite que Docker o tu orquestador sepan si la aplicación realmente responde, no solo si el proceso sigue vivo.

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -qO- http://localhost:3000/health || exit 1
```

## 10. Escanea tus imágenes

Herramientas como `docker scout`, Trivy o Grype detectan vulnerabilidades conocidas en dependencias y en la imagen base. Intégralas en tu CI para que cada build se revise automáticamente.

## 11. Usa `COPY` en lugar de `ADD`

`ADD` tiene comportamientos implícitos, como descomprimir archivos o descargar URLs, que pueden sorprenderte. `COPY` es explícito y predecible.

## 12. Define límites de recursos

En producción, limita CPU y memoria para que un contenedor descontrolado no afecte al resto del host:

```bash
docker run --memory=512m --cpus=1 mi-app
```

## Conclusión

Mejorar tu uso de Docker no requiere grandes cambios. Con imágenes base ligeras y fijadas, multi-stage builds, una buena gestión de la caché, usuarios sin privilegios y escaneo continuo, tendrás contenedores más rápidos, pequeños y seguros.

Si te quedas con una sola idea: **trata tu `Dockerfile` como código de producción**, con revisiones, mantenimiento y mejora continua.

¿Qué otras buenas prácticas añadirías? ¡Te leo en los comentarios!
