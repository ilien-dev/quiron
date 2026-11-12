Cada vez que quitas la mano del teclado para buscar el ratón pierdes unos segundos y, lo que es peor, la concentración. Crear archivos y carpetas es una de las tareas más repetitivas del día a día. En VSCode puedes hacerlo todo sin tocar el ratón.

En este post te muestro varias formas, de la más básica a la más cómoda.

## 1. Moverse al Explorador con el teclado

Lo primero es saber llegar al Explorador de archivos:

- **`Ctrl + Shift + E`** (`Cmd + Shift + E` en macOS): pone el foco en el Explorador.
- **Flechas arriba/abajo**: te mueves entre archivos y carpetas.
- **Flecha derecha/izquierda**: expande o colapsa una carpeta.
- **`Ctrl + 1`**: vuelve al editor.

El archivo o carpeta que tengas seleccionado determina **dónde** se creará el nuevo elemento. Si seleccionas una carpeta, se creará dentro de ella. Si seleccionas un archivo, se creará junto a él.

## 2. La Paleta de Comandos

Con el foco en el Explorador, abre la Paleta de Comandos con **`Ctrl + Shift + P`** y escribe:

- `File: New File` para crear un archivo.
- `File: New Folder` para crear una carpeta.

Aparecerá un campo de texto en línea dentro del Explorador. Escribe el nombre, pulsa `Enter` y listo.

Funciona, pero escribir el comando cada vez es lento. Vamos a mejorarlo.

## 3. El truco de las barras: crear carpetas anidadas de golpe

Este es el truco que más tiempo me ha ahorrado. Al crear un archivo, **puedes escribir una ruta completa con barras**:

```
src/components/Button/Button.tsx
```

VSCode creará automáticamente las carpetas `components` y `Button` si no existen, y el archivo `Button.tsx` dentro. Lo mismo sirve para `New Folder`: escribe `docs/api/v2` y tendrás las tres carpetas en un solo paso.

## 4. Asigna tus propios atajos

VSCode no trae atajos por defecto para crear archivos o carpetas desde el Explorador, pero puedes crearlos tú. Abre la Paleta de Comandos y busca `Preferences: Open Keyboard Shortcuts (JSON)`. Añade esto:

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

La condición `when` hace que el atajo solo funcione cuando el foco está en el Explorador, así no choca con otros atajos del editor. Elige las combinaciones que te resulten cómodas y que no uses ya.

Ahora el flujo queda así:

1. `Ctrl + Shift + E` para ir al Explorador.
2. Flechas hasta la carpeta destino.
3. `Ctrl + Alt + N`.
4. Escribes `utils/format.ts` y pulsas `Enter`.

Cuatro pasos, cero ratón.

## 5. Usar la terminal integrada

Si ya vives en la terminal, abre la integrada con **`` Ctrl + ` ``** y usa los comandos de siempre:

```bash
# Bash / Zsh
mkdir -p src/hooks
touch src/hooks/useAuth.ts
```

```powershell
# PowerShell
New-Item -ItemType File -Path src/hooks/useAuth.ts -Force
```

El `-Force` de PowerShell crea las carpetas intermedias que falten.

Y un extra: si tienes el comando `code` en el PATH, `code src/hooks/useAuth.ts` abre el archivo en el editor (y se crea al guardarlo).

## 6. Otros atajos útiles del Explorador

Ya que estás en el Explorador, aprovecha estos:

| Acción | Windows/Linux | macOS |
|---|---|---|
| Renombrar | `F2` | `Enter` |
| Eliminar | `Supr` | `Cmd + Backspace` |
| Copiar / Pegar | `Ctrl + C` / `Ctrl + V` | `Cmd + C` / `Cmd + V` |
| Abrir archivo | `Enter` | `Cmd + ↓` |
| Nuevo archivo sin guardar | `Ctrl + N` | `Cmd + N` |

## Conclusión

No necesitas extensiones para dejar de usar el ratón al crear archivos y carpetas. Con `Ctrl + Shift + E`, un par de atajos personalizados y el truco de escribir rutas con barras, tu flujo será mucho más rápido y fluido.

Mi recomendación: configura los atajos del punto 4 hoy mismo y oblígate a usarlos durante una semana. En pocos días los harás sin pensar.

¿Tienes algún otro truco para trabajar en VSCode sin ratón? ¡Déjalo en los comentarios! 👇
