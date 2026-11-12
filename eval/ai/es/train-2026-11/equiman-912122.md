# Mover el Sistema de Archivos de WSL a otro disco

Si usas WSL (Windows Subsystem for Linux), probablemente hayas notado que su sistema de archivos crece sin parar en la unidad `C:`. Cada distribución vive en un archivo `ext4.vhdx` dentro de `AppData`, y ese archivo no se encoge solo. Si tu disco principal es pequeño o te has quedado sin espacio, mover la distribución a otra unidad es una buena solución. Aquí te explico cómo hacerlo.

## Antes de empezar

Haz una copia de seguridad. Mover una distribución implica exportarla e importarla de nuevo, y un error puede dejarte sin tus datos. Revisa también el espacio libre en la unidad de destino: necesitarás al menos el tamaño actual del `.vhdx` más margen para exportar.

Comprueba tus distribuciones y su versión de WSL:

```powershell
wsl --list --verbose
```

Si la columna VERSION muestra `2`, la distribución usa el formato que vamos a mover. Las distribuciones WSL 1 no tienen un `.vhdx`, así que este proceso no aplica.

## Opción 1: el comando `--manage --move` (la más sencilla)

En versiones recientes de WSL 2 existe un comando que mueve la distribución directamente. Primero, comprueba si lo tienes:

```powershell
wsl --version
```

Si la versión es reciente, puedes usar:

```powershell
wsl --shutdown
wsl --manage Ubuntu --move D:\WSL\Ubuntu
```

Sustituye `Ubuntu` por el nombre de tu distribución y `D:\WSL\Ubuntu` por la carpeta de destino. Si el comando no existe en tu versión, pasa a la opción 2.

## Opción 2: exportar e importar

Este método funciona en cualquier versión de WSL 2.

**1. Apaga WSL:**

```powershell
wsl --shutdown
```

**2. Exporta la distribución a un archivo `.tar`:**

```powershell
wsl --export Ubuntu D:\Backups\ubuntu.tar
```

Si quieres exportar directamente el disco virtual, que conserva el formato `.vhdx` y evita el paso por `.tar`, puedes usar la opción `--vhd` en versiones de WSL que la soporten:

```powershell
wsl --export Ubuntu D:\Backups\ubuntu.vhdx --vhd
```

**3. Elimina la distribución original:**

Este paso borra el `.vhdx` de `C:`, así que confirma antes que el respaldo está completo.

```powershell
wsl --unregister Ubuntu
```

**4. Importa la distribución en la nueva ubicación:**

```powershell
wsl --import Ubuntu D:\WSL\Ubuntu D:\Backups\ubuntu.tar
```

Si exportaste en formato `.vhdx`, usa `--import-in-place` en su lugar:

```powershell
wsl --import-in-place Ubuntu D:\WSL\Ubuntu\ext4.vhdx
```

## Restaurar tu usuario por defecto

Al importar, WSL entra como `root`. Para volver a tu usuario habitual, edita `/etc/wsl.conf` dentro de la distribución:

```ini
[user]
default=tu_usuario
```

Después, reinicia WSL con `wsl --shutdown` para que el cambio surta efecto.

Otra opción es usar el comando `wsl --set-default-user` cuando la distribución esté activa, aunque esto requiere que el usuario ya exista en el sistema.

## Comprueba el resultado

Verifica que la distribución arranca correctamente y que el archivo está en la nueva unidad:

```powershell
wsl -d Ubuntu
df -h /
```

Después, en el Explorador o en PowerShell, comprueba que `D:\WSL\Ubuntu\ext4.vhdx` existe y que el espacio liberado en `C:` es el esperado. Cuando estés seguro de que todo funciona, puedes borrar el `.tar` de respaldo.

## Conclusión

Mover WSL a otra unidad lleva apenas unos minutos y libera espacio en el disco del sistema sin reinstalar nada. Lo más importante es hacer la copia de seguridad antes de desregistrar la distribución. Si tienes dudas sobre tu versión o te encuentras con un error, comparte la salida de `wsl --version` en los comentarios.
