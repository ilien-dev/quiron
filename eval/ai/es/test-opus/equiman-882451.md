# VSCode - Crear Archivos y Directorios sin usar el ratón

Cada vez que quitas la mano del teclado para ir al ratón, pierdes un poco de tiempo y, sobre todo, de concentración. Parece poca cosa, pero a lo largo de un día de trabajo esos pequeños saltos se acumulan. Una de las tareas que más repetimos en el editor es crear archivos y carpetas, así que vale la pena aprender a hacerlo solo con el teclado.

En este post te enseño varias formas de hacerlo en Visual Studio Code.

## 1. Desde el explorador de archivos

La forma más directa es usar el explorador lateral, pero sin tocar el ratón:

1. Pulsa `Ctrl + Shift + E` (`Cmd + Shift + E` en macOS) para poner el foco en el explorador.
2. Muévete con las flechas hasta la carpeta donde quieres crear el archivo.
3. Aquí viene el problema: por defecto, VSCode no tiene un atajo asignado para "Nuevo archivo" dentro del explorador. Vamos a solucionarlo.

### Asignar atajos personalizados

Abre la configuración de atajos con `Ctrl + K Ctrl + S` y pulsa el icono de "Abrir atajos de teclado (JSON)" en la esquina superior derecha. Añade lo siguiente:

```json
[
  {
    "key": "ctrl+alt+n",
    "command": "explorer.newFile",
    "when": "explorerViewletFocus"
  },
  {
    "key": "ctrl+alt+shift+n",
    "command": "explorer.newFolder",
    "when": "explorerViewletFocus"
  }
]
```

Ahora, con el foco en el explorador, `Ctrl + Alt + N` crea un archivo y `Ctrl + Alt + Shift + N` crea una carpeta, ambos dentro del elemento seleccionado. Escribe el nombre, pulsa `Enter` y listo.

El truco de la condición `when` es que el atajo solo se activa cuando estás en el explorador, así que no choca con otros atajos del editor.

## 2. Crear carpetas y archivo a la vez

Algo que mucha gente no sabe: al crear un archivo nuevo desde el explorador puedes escribir una ruta con barras, por ejemplo:

```
components/Button/Button.tsx
```

VSCode creará automáticamente las carpetas `components` y `Button` si no existen, y dentro el archivo `Button.tsx`. Esto funciona tanto con `explorer.newFile` como con el botón del explorador, y te ahorra varios pasos.

Si terminas el nombre con una barra (`utils/helpers/`) al crear una carpeta, obtendrás la estructura completa de directorios.

## 3. Desde la paleta de comandos

Otra opción es la paleta de comandos:

1. Pulsa `Ctrl + Shift + P` (`Cmd + Shift + P`).
2. Escribe `New File` y selecciona **Archivo: Nuevo archivo...**
3. VSCode te preguntará qué tipo de archivo quieres crear o te dejará escribir un nombre.

Por defecto, `Ctrl + N` crea un archivo sin título, pero tendrás que guardarlo con `Ctrl + S` y elegir la ubicación en el diálogo. Funciona, pero es más lento que las opciones anteriores.

## 4. Desde la terminal integrada

Si te sientes cómodo en la terminal, abre la integrada con `` Ctrl + ` `` y usa los comandos de siempre:

```bash
mkdir -p src/components/Header
touch src/components/Header/Header.js
code src/components/Header/Header.js
```

El comando `code` abre el archivo directamente en la ventana actual del editor. En Windows con PowerShell, puedes usar `New-Item`:

```powershell
New-Item -ItemType File -Path src/components/Header/Header.js -Force
```

La opción `-Force` crea también los directorios intermedios.

## 5. Extensiones

Si quieres ir más allá, hay extensiones como **Advanced New File** o **File Utils** que permiten crear archivos con autocompletado de rutas relativas a la carpeta actual o a la raíz del proyecto, todo desde un único cuadro de texto.

## Resumen

| Acción | Atajo |
|---|---|
| Enfocar el explorador | `Ctrl + Shift + E` |
| Nuevo archivo (personalizado) | `Ctrl + Alt + N` |
| Nueva carpeta (personalizado) | `Ctrl + Alt + Shift + N` |
| Paleta de comandos | `Ctrl + Shift + P` |
| Terminal integrada | `` Ctrl + ` `` |
| Volver al editor | `Ctrl + 1` |

Con un par de atajos personalizados y el truco de las rutas con barras, crear la estructura de un proyecto se vuelve mucho más rápido. Pruébalo durante una semana y verás cómo el ratón empieza a acumular polvo.
