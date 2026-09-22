# Servir sitios y aplicaciones web en Azure usando un archivo ZIP (Run From Package)

Una de las funcionalidades menos conocidas, pero más útiles, de Azure App Service es la posibilidad de desplegar y servir una aplicación web directamente desde un archivo ZIP, sin necesidad de extraer sus contenidos al sistema de archivos del servidor. Esta característica se llama **Run From Package**, y en este post vamos a ver en qué consiste, sus ventajas, y cómo configurarla paso a paso.

## ¿Qué es Run From Package?

Normalmente, cuando desplegamos una aplicación en Azure App Service, el contenido se copia (mediante FTP, Git, Zip Deploy, o cualquier otro mecanismo) al directorio `wwwroot` del sitio, y el servidor sirve los archivos desde ahí, como en un hosting tradicional.

Con Run From Package, en cambio, el archivo ZIP nunca se extrae. En su lugar, Azure monta el ZIP directamente como un sistema de archivos de solo lectura, y la aplicación se ejecuta directamente contra ese contenido montado. Es una diferencia sutil, pero con implicaciones importantes.

## Ventajas de este enfoque

### Despliegues atómicos

Al copiar archivos de forma tradicional, existe una ventana de tiempo durante la cual algunos archivos ya se actualizaron y otros todavía no, lo que puede provocar comportamientos inconsistentes si hay peticiones llegando justo durante el despliegue. Con Run From Package, el cambio es atómico: en un instante se está sirviendo la versión anterior, y al siguiente, la nueva, sin estados intermedios inconsistentes.

### Sin bloqueo de archivos

Un problema clásico en Windows (y en App Service específicamente) es que ciertos archivos, como DLLs en uso, no se pueden sobrescribir mientras la aplicación está corriendo, lo que a veces obligaba a reiniciar el sitio antes de desplegar. Al no extraerse los archivos, este problema desaparece por completo.

### Garantía de contenido idéntico

Como el sistema de archivos montado es de solo lectura, se elimina la posibilidad de que algún proceso, script, o incluso un atacante, modifique archivos de la aplicación directamente en el servidor de producción sin pasar por un nuevo despliegue formal. Esto mejora tanto la seguridad como la trazabilidad de los cambios.

### Arranques más rápidos en Azure Functions

Para Azure Functions en particular, Run From Package resuelve un problema conocido de "cold start" relacionado con el escaneo de archivos que Azure hacía tradicionalmente para detectar los triggers de las funciones, acelerando notablemente los tiempos de arranque en escenarios con Consumption Plan.

## Configurando Run From Package

Existen dos formas principales de activar esta característica.

### Opción 1: Desde un archivo ZIP local, vía Zip Deploy

Podemos desplegar directamente un ZIP usando la CLI de Azure:

```bash
az webapp deployment source config-zip \
  --resource-group mi-grupo-recursos \
  --name mi-app-web \
  --src ./mi-app.zip
```

Para que este ZIP se sirva usando Run From Package (en lugar de extraerse), hay que configurar la variable de aplicación `WEBSITE_RUN_FROM_PACKAGE` con el valor `1`:

```bash
az webapp config appsettings set \
  --resource-group mi-grupo-recursos \
  --name mi-app-web \
  --settings WEBSITE_RUN_FROM_PACKAGE=1
```

### Opción 2: Desde un archivo ZIP alojado en Azure Blob Storage

Esta es la opción recomendada para escenarios de CI/CD más robustos. En lugar de subir el ZIP directamente al sitio, lo subimos a un contenedor de Azure Blob Storage, generamos una URL con SAS token (para acceso controlado y con expiración), y configuramos `WEBSITE_RUN_FROM_PACKAGE` con esa URL completa en lugar del valor `1`:

```bash
az webapp config appsettings set \
  --resource-group mi-grupo-recursos \
  --name mi-app-web \
  --settings WEBSITE_RUN_FROM_PACKAGE="https://miscuenta.blob.core.windows.net/paquetes/mi-app.zip?sv=..."
```

Con este enfoque, actualizar la aplicación es tan simple como subir una nueva versión del ZIP al blob storage y actualizar (o no, si se usa siempre el mismo nombre de blob con una URL fija) esta configuración, lo cual encaja muy bien con pipelines de integración continua.

## Consideraciones importantes

### El sistema de archivos es de solo lectura

Como el contenido se sirve directamente desde el ZIP montado, la aplicación no puede escribir archivos dentro de su propio directorio de contenido. Si tu aplicación necesita escribir archivos temporales, logs locales, o cachés en disco, debes usar el directorio `%TEMP%` (o su equivalente en Linux), que sí permite escritura, o mejor aún, usar un servicio externo como Azure Storage para persistencia real.

### No aplica automáticamente a todos los tipos de despliegue

Run From Package se activa mediante la configuración `WEBSITE_RUN_FROM_PACKAGE`; no es el comportamiento por defecto de cualquier despliegue. Si despliegas mediante Git, GitHub Actions con un despliegue de código fuente tradicional (sin generar y desplegar un ZIP), es posible que esta configuración no aplique o requiera pasos adicionales según el tipo de pipeline usado.

### Compatibilidad

Run From Package funciona tanto en Windows como en Linux App Service, y es totalmente compatible con Azure Functions, además de aplicaciones web tradicionales (ASP.NET, Node.js, Python, etc.).

## Integrándolo en un pipeline de CI/CD

Un flujo típico usando GitHub Actions podría verse así, generando el ZIP como artefacto de build y subiéndolo directamente vía Zip Deploy con Run From Package activado:

```yaml
- name: Empaquetar aplicación
  run: zip -r mi-app.zip ./publish

- name: Desplegar a Azure App Service
  uses: azure/webapps-deploy@v2
  with:
    app-name: mi-app-web
    package: mi-app.zip
```

Y con la variable `WEBSITE_RUN_FROM_PACKAGE=1` configurada previamente en el App Service, cada nuevo push que dispare este workflow generará un despliegue atómico y sin bloqueos.

## Conclusión

Run From Package es una de esas funcionalidades de Azure que, una vez configurada, pasa a ser prácticamente invisible en el día a día, pero que resuelve de raíz varios problemas clásicos del despliegue tradicional de archivos: inconsistencias durante el despliegue, bloqueos de archivos en uso, y falta de garantías sobre la integridad del contenido servido en producción. Si todavía despliegas tus aplicaciones en Azure App Service de la forma tradicional, vale la pena evaluar migrar a este enfoque, especialmente en proyectos donde la fiabilidad de los despliegues es crítica.
