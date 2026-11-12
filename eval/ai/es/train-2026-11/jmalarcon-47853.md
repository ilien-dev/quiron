# Servir sitios y aplicaciones web en Azure usando un archivo ZIP (Run From Package)

Cuando despliegas una aplicación en Azure App Service, lo habitual es copiar archivos sueltos a `wwwroot`. Funciona, pero trae problemas conocidos: despliegues a medias, archivos bloqueados por el proceso en ejecución, arranques lentos y diferencias entre lo que subiste y lo que realmente se ejecuta.

Hay una alternativa más limpia: **Run From Package**. En lugar de extraer archivos, App Service monta un ZIP como directorio de la aplicación. En este artículo veremos cómo funciona, cómo activarlo y qué trampas evitar.

## ¿Qué es Run From Package?

Es una característica de Azure App Service y Azure Functions. En vez de copiar los archivos a `wwwroot`, la plataforma monta el contenido del ZIP directamente como un sistema de archivos **de solo lectura**, y tu aplicación se ejecuta desde ahí.

Se controla con un único app setting, `WEBSITE_RUN_FROM_PACKAGE`, que acepta dos tipos de valor:

- **`1`**: el ZIP vive en el almacenamiento local de la aplicación (`/home/data/SitePackages`). Es el modo que se configura al usar el despliegue ZIP.
- **Una URL**: apunta a un ZIP alojado en Blob Storage u otro lugar accesible por HTTPS.

## ¿Por qué usarlo?

- **Despliegues atómicos.** El paquete se monta completo o no se monta. Adiós a los estados intermedios en los que la mitad de los archivos son de la versión anterior.
- **Sin bloqueos de archivos.** Al no haber copia sobre `wwwroot`, no hay conflictos con archivos en uso.
- **Arranques en frío más rápidos**, sobre todo en aplicaciones con miles de archivos (típico en Node.js con `node_modules`).
- **Inmutabilidad.** Nadie puede modificar archivos en producción por accidente, ni por FTP ni desde la consola Kudu.
- **Versionado sencillo.** Cada versión es un artefacto ZIP que puedes guardar, auditar o restaurar.

## Cómo preparar el ZIP

Un error muy común es comprimir la carpeta contenedora. El contenido de la aplicación debe estar **en la raíz del ZIP**, no dentro de una subcarpeta.

Para una aplicación .NET:

```powershell
dotnet publish -c Release -o ./publish
Compress-Archive -Path ./publish/* -DestinationPath app.zip -Force
```

Para un sitio estático o una app Node.js:

```bash
cd dist
zip -r ../app.zip .
```

Fíjate en `./publish/*` y en `zip -r ../app.zip .`: ambos comprimen el contenido, no la carpeta.

## Opción 1: despliegue ZIP con Azure CLI

Es la forma más rápida. Con `az webapp deploy`, App Service guarda el paquete y lo monta:

```bash
az webapp config appsettings set \
  --resource-group mi-grupo \
  --name mi-webapp \
  --settings WEBSITE_RUN_FROM_PACKAGE=1

az webapp deploy \
  --resource-group mi-grupo \
  --name mi-webapp \
  --src-path app.zip \
  --type zip
```

Cada nuevo despliegue sustituye el paquete anterior y reinicia la aplicación con el contenido nuevo.

## Opción 2: ZIP en Blob Storage con URL

Aquí el ZIP vive en una cuenta de almacenamiento y la aplicación lo descarga al arrancar. Es útil cuando varios entornos comparten el mismo artefacto o quieres desacoplar la compilación del despliegue.

```bash
# Crear contenedor y subir el paquete
az storage container create \
  --account-name mialmacenamiento \
  --name paquetes

az storage blob upload \
  --account-name mialmacenamiento \
  --container-name paquetes \
  --name app-v1.zip \
  --file app.zip

# Generar una URL con SAS (válida hasta la fecha indicada)
az storage blob generate-sas \
  --account-name mialmacenamiento \
  --container-name paquetes \
  --name app-v1.zip \
  --permissions r \
  --expiry 2027-12-31T23:59Z \
  --https-only \
  --full-uri
```

Con la URL resultante, configura la aplicación:

```bash
az webapp config appsettings set \
  --resource-group mi-grupo \
  --name mi-webapp \
  --settings WEBSITE_RUN_FROM_PACKAGE="<URL-con-SAS>"
```

Para publicar una nueva versión, sube un nuevo blob, actualiza el setting y reinicia la aplicación (el cambio de setting ya provoca el reinicio).

### Cuidado con la caducidad del SAS

Si el token SAS caduca, la aplicación **no podrá descargar el paquete** la próxima vez que se reinicie. Es una de las causas más comunes de "mi web dejó de funcionar sin que tocara nada". Pon caducidades largas y monitoriza la fecha, o mejor aún, usa identidad administrada.

## Evitar SAS: identidad administrada

En lugar de incrustar un token en la URL, puedes dejar que la aplicación se autentique con su identidad administrada:

1. Activa una identidad administrada en la aplicación (de sistema o de usuario).
2. Asígnale el rol **Storage Blob Data Reader** sobre la cuenta o el contenedor.
3. Usa la URL del blob **sin SAS** en `WEBSITE_RUN_FROM_PACKAGE`.
4. Si usas una identidad asignada por el usuario, indica cuál con `WEBSITE_RUN_FROM_PACKAGE_BLOB_MI_RESOURCE_ID`.

Así no hay secretos en la configuración y no hay tokens que caduquen.

## Integración con GitHub Actions

Un flujo típico: compilar, generar el ZIP y desplegarlo.

```yaml
name: deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - name: Compilar
        run: |
          npm ci
          npm run build
          cd dist && zip -r ../app.zip .

      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Desplegar
        run: |
          az webapp deploy \
            --resource-group mi-grupo \
            --name mi-webapp \
            --src-path app.zip \
            --type zip
```

La autenticación usa OIDC, así que no necesitas guardar contraseñas ni perfiles de publicación.

## Limitaciones a tener en cuenta

- **`wwwroot` es de solo lectura.** Si tu aplicación escribe en disco (cargas de usuarios, cachés, SQLite), debe hacerlo en otra ubicación, como `/home` o `/tmp`, o mejor, en un servicio externo como Blob Storage.
- **No combines métodos de despliegue.** Si activas Run From Package, los despliegues que escriben en `wwwroot` (FTP, copia de archivos) fallarán o se ignorarán.
- **El tamaño del paquete importa.** Un ZIP enorme alarga la descarga en cada arranque cuando se usa una URL.
- **Compilación en el servidor.** Las opciones como Oryx (`SCM_DO_BUILD_DURING_DEPLOYMENT`) no encajan bien: compila antes y sube el resultado ya listo.
- **Diferencias por plan y sistema operativo.** Revisa la documentación oficial para tu combinación concreta (por ejemplo, Functions en Linux Consumption exige el modo URL).

## Solución de problemas

**La aplicación muestra la página por defecto o un 404.** Casi siempre el ZIP tiene una carpeta contenedora en la raíz. Revisa la estructura.

**Error tras reiniciar con URL.** Comprueba que el SAS no ha caducado, que la URL es accesible y que la identidad administrada tiene el rol correcto.

**Los cambios no se reflejan.** Confirma que el setting apunta al paquete correcto y reinicia la aplicación. Con `WEBSITE_RUN_FROM_PACKAGE=1`, verifica que el despliegue terminó sin errores en los logs.

**No puedo editar archivos desde Kudu.** Es lo esperado: el sistema es de solo lectura. Genera un nuevo paquete y despliégalo.

## Conclusión

Run From Package convierte tu despliegue en algo simple y predecible: un artefacto ZIP, una versión, un montaje atómico. Para la mayoría de aplicaciones en App Service o Functions es una mejora gratuita en fiabilidad y velocidad de arranque, y encaja de forma natural en cualquier pipeline de CI/CD.

Mi recomendación: empieza con `WEBSITE_RUN_FROM_PACKAGE=1` y `az webapp deploy`, y pasa al modo URL con identidad administrada cuando necesites compartir artefactos entre entornos.

¿Ya lo usas en producción? Cuéntame en los comentarios qué problemas te encontraste. 👇
