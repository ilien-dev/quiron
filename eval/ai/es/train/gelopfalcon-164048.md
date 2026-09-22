# Buenas prácticas en Docker

Docker se ha convertido en una herramienta imprescindible en el desarrollo y despliegue de aplicaciones modernas, pero es fácil caer en malos hábitos que resultan en imágenes pesadas, builds lentos o contenedores poco seguros. En este post repasamos algunas buenas prácticas que conviene aplicar desde el principio.

## Usa imágenes base ligeras

Es tentador partir de una imagen base completa como `ubuntu` o `debian`, pero en la mayoría de los casos existen alternativas mucho más ligeras. Para aplicaciones Node.js, Python o similares, las variantes `alpine` o `slim` reducen drásticamente el tamaño final de la imagen:

```dockerfile
# En lugar de esto
FROM node:18

# Considera esto
FROM node:18-alpine
```

Menos tamaño significa builds más rápidos, menos superficie de ataque y despliegues más ágiles.

## Aprovecha el cache de capas

Docker construye las imágenes por capas, y cada instrucción del `Dockerfile` genera una capa que se cachea si no cambió respecto al build anterior. El orden de las instrucciones importa mucho: hay que colocar primero lo que cambia con menos frecuencia.

```dockerfile
# Mal: cualquier cambio en el código invalida el cache de las dependencias
COPY . .
RUN npm install

# Bien: solo se reinstalan dependencias si package.json cambió
COPY package*.json ./
RUN npm install
COPY . .
```

Este simple reordenamiento puede reducir builds de minutos a segundos cuando solo cambiamos código de la aplicación sin tocar las dependencias.

## Usa builds multi-etapa

Los **multi-stage builds** permiten usar una imagen con todas las herramientas necesarias para compilar (compiladores, dependencias de desarrollo) y luego copiar únicamente el resultado final a una imagen mucho más liviana:

```dockerfile
# Etapa de build
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Etapa final
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

El resultado es una imagen final que solo contiene los archivos estáticos y Nginx, sin ninguna de las dependencias de desarrollo ni el código fuente original.

## No corras como root

Por defecto, muchos contenedores corren como usuario `root`, lo cual representa un riesgo de seguridad innecesario si un atacante logra comprometer la aplicación dentro del contenedor. Es buena práctica crear un usuario específico:

```dockerfile
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```

Muchas imágenes base oficiales ya incluyen un usuario no privilegiado predefinido (por ejemplo, `node` en las imágenes de Node.js), que se puede usar directamente sin crear uno nuevo.

## Usa .dockerignore

Igual que con `.gitignore`, un archivo `.dockerignore` evita copiar archivos innecesarios (como `node_modules`, archivos de configuración local, o carpetas `.git`) al contexto de build, lo cual acelera el proceso y reduce el riesgo de filtrar información sensible dentro de la imagen:

```
node_modules
.git
.env
*.log
```

## No hardcodees secretos en el Dockerfile

Nunca se deben incluir contraseñas, tokens o claves API directamente en el `Dockerfile` ni en variables `ENV` fijas, ya que quedan grabadas en el historial de capas de la imagen y son recuperables incluso si se "eliminan" en una instrucción posterior. Para esto existen mecanismos específicos, como `--secret` en BuildKit, o simplemente inyectar variables de entorno en tiempo de ejecución del contenedor en lugar de en tiempo de build.

## Fija versiones específicas

Usar `latest` como tag puede parecer conveniente, pero introduce comportamiento impredecible: el mismo `Dockerfile` puede producir resultados distintos en días distintos, dependiendo de qué versión sea "latest" en ese momento.

```dockerfile
# Evita esto
FROM node:latest

# Prefiere esto
FROM node:18.19.0-alpine
```

Fijar versiones específicas hace que los builds sean reproducibles, algo fundamental para depurar problemas y garantizar consistencia entre entornos de desarrollo, staging y producción.

## Combina instrucciones RUN cuando tenga sentido

Cada instrucción `RUN` genera una capa nueva. Combinar comandos relacionados en una sola instrucción, especialmente cuando incluyen limpieza de archivos temporales, reduce el tamaño final:

```dockerfile
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

Si se hiciera en instrucciones `RUN` separadas, los archivos temporales de `apt-get update` quedarían "atrapados" en una capa anterior, ocupando espacio aunque después se borren en una capa posterior.

## Define un HEALTHCHECK

Añadir una instrucción `HEALTHCHECK` permite que Docker (y orquestadores como Kubernetes o Docker Swarm) sepan si el contenedor está realmente funcionando correctamente, más allá de simplemente estar "corriendo":

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:3000/health || exit 1
```

## Conclusión

Ninguna de estas prácticas es complicada de implementar individualmente, pero en conjunto marcan una diferencia enorme en el tamaño, la velocidad de build, la seguridad y la mantenibilidad de las imágenes Docker. Vale la pena revisar los `Dockerfile` existentes en tus proyectos y aplicar, poco a poco, las que todavía no estés siguiendo.
