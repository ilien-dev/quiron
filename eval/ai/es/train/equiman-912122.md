# Mover el Sistema de Archivos de WSL a Otro Disco

Si usas Windows Subsystem for Linux (WSL), probablemente hayas notado que tu sistema de archivos de Linux vive dentro de una máquina virtual. Esto es conveniente, pero si tu disco C está lleno, mover WSL a otro disco es la solución.

La buena noticia es que es posible, y es más simple de lo que suena.

## Por qué quieres mover WSL

El problema es común: WSL ocupa espacio, y tu disco C tiene capacidad limitada. Especialmente si trabajas con proyectos grandes, Docker containers o bases de datos, WSL consume gigabytes rápidamente.

Mover a otro disco libera espacio en tu sistema operativo y da más sala para tus desarrollos.

## Paso 1: Listar tus distribuciones

Primero, necesitas saber qué distribuciones tienes instaladas. Abre PowerShell o Command Prompt y ejecuta:

```powershell
wsl --list --verbose
```

Verás algo como:

```
NAME      STATE   VERSION
Ubuntu    Running 2
```

Anota el nombre exacto (generalmente "Ubuntu", "Debian", etc.) y el estado.

## Paso 2: Exportar la distribución

Ahora vas a exportar tu distribución actual a un archivo. Esto es básicamente crear un backup que puedas restaurar en otro lugar.

```powershell
wsl --export Ubuntu D:\wsl-backup\ubuntu.tar
```

Reemplaza `Ubuntu` con tu distribución y `D:\` con la ruta donde quieres guardar el backup. Esto puede tardar un rato dependiendo del tamaño.

## Paso 3: Desinstalar la distribución antigua

Una vez que el backup esté completo, desinstala la versión antigua:

```powershell
wsl --unregister Ubuntu
```

Esto la elimina del registro de Windows. Tu disco C se libera.

## Paso 4: Importar en el nuevo disco

Ahora restaura tu distribución desde el backup en la nueva ubicación:

```powershell
wsl --import Ubuntu D:\wsl-distros\ D:\wsl-backup\ubuntu.tar --version 2
```

Aquí:
- `Ubuntu` es el nombre
- `D:\wsl-distros\` es donde WSL instalará la distribución
- `D:\wsl-backup\ubuntu.tar` es el archivo de backup
- `--version 2` indica que quieres WSL2 (la versión moderna)

## Paso 5: Verifica

Lista nuevamente tus distribuciones:

```powershell
wsl --list --verbose
```

Deberías ver tu distribución nuevamente, ahora apuntando al nuevo disco.

Abre WSL y verifica que todo funciona:

```powershell
wsl
```

Si logras entrar, todo está bien. Tu sistema de archivos, configuraciones y todo está intacto.

## Limpiar

Una vez que verifica que todo funciona, puedes eliminar el archivo de backup:

```powershell
Remove-Item D:\wsl-backup\ubuntu.tar
```

## Nota importante

Si tienes múltiples distribuciones (Ubuntu, Debian, etc.), repite el proceso para cada una.

También, es posible que tengas que actualizar tu distribución después de importarla. En WSL, ejecuta:

```bash
sudo apt update && sudo apt upgrade
```

## Conclusión

Mover WSL a otro disco es un proceso sencillo de exportar e importar. No pierdes nada, y ganas espacio en tu disco C. Si tienes WSL instalado hace tiempo y está ocupando mucho espacio, es una tarea que vale la pena hacer.
