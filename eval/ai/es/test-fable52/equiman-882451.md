Cada vez que levantas la mano del teclado para hacer clic derecho en el explorador y elegir "Nuevo archivo", pierdes unos segundos y, peor aún, la concentración. Parece poco, pero crear archivos y carpetas es algo que hacemos decenas de veces al día.

VSCode permite hacerlo todo desde el teclado, aunque no lo pone especialmente fácil de descubrir. Estas son las formas que uso, de la más simple a la más cómoda.

> Los atajos son para Windows/Linux. En macOS, cambia `Ctrl` por `Cmd`.

## 1. La paleta de comandos

Es la opción que funciona sin configurar nada:

1. Pulsa `Ctrl+Shift+P`.
2. Escribe `new file` y elige **File: New File** (o **File: New Folder** para una carpeta).
3. Escribe el nombre y pulsa `Enter`.

El archivo se crea en la carpeta que tengas seleccionada en el explorador. Funciona, pero son demasiadas pulsaciones para algo tan frecuente.

## 2. El truco de las rutas anidadas

Este es el detalle que más tiempo ahorra y que mucha gente no conoce. Cuando VSCode te pide el nombre del archivo, puedes escribir una ruta completa:

```
src/components/Button/Button.tsx
```

VSCode crea todas las carpetas intermedias que no existan y, al final, el archivo. No hace falta crear `components`, luego `Button` y luego el archivo: todo va en un solo paso.

Lo mismo sirve para carpetas: con **New Folder** puedes escribir `assets/images/icons` y se crea toda la jerarquía.

## 3. Atajos propios en el explorador

Por defecto, VSCode no asigna ningún atajo a "nuevo archivo" ni a "nueva carpeta" dentro del explorador. Se puede arreglar en un minuto.

Abre la paleta (`Ctrl+Shift+P`), busca **Preferences: Open Keyboard Shortcuts (JSON)** y añade:

```json
[
  {
    "key": "a",
    "command": "explorer.newFile",
    "when": "filesExplorerFocus && !inputFocus"
  },
  {
    "key": "shift+a",
    "command": "explorer.newFolder",
    "when": "filesExplorerFocus && !inputFocus"
  }
]
```

La clave está en la condición `when`: los atajos solo se activan cuando el foco está en el explorador y no estás escribiendo en un campo de texto. Así, la tecla `a` sigue funcionando con normalidad en el editor.

El flujo completo queda así:

1. `Ctrl+Shift+E` lleva el foco al explorador.
2. Te mueves con las flechas hasta la carpeta de destino.
3. `a` para un archivo, `Shift+A` para una carpeta.
4. Escribes el nombre (o una ruta anidada) y pulsas `Enter`.

El archivo se abre directamente en el editor, listo para escribir. Si creaste una carpeta, `Ctrl+1` te devuelve al editor.

Ya dentro del explorador, hay otros atajos que sí vienen de serie: `F2` renombra, `Supr` borra y `Ctrl+C` / `Ctrl+V` duplican archivos.

## 4. La terminal integrada

Si te sientes más cómodo en la línea de comandos, abre la terminal integrada con `` Ctrl+` `` (`Ctrl+ñ` en teclados en español).

En bash o zsh:

```bash
mkdir -p src/utils && touch src/utils/format.ts
```

En PowerShell:

```powershell
New-Item -ItemType File -Path src/utils/format.ts -Force
```

El parámetro `-Force` crea las carpetas intermedias si no existen. Para abrir el archivo recién creado en el editor:

```bash
code src/utils/format.ts
```

La terminal gana cuando necesitas crear varios archivos a la vez:

```bash
touch src/utils/{format,parse,validate}.ts
```

## ¿Cuál usar?

- **Un archivo suelto**: atajo propio en el explorador más ruta anidada.
- **Varios archivos de golpe**: terminal integrada.
- **Un equipo que no es el tuyo**: paleta de comandos, que siempre está disponible.

Lo más rentable es dedicar un minuto a configurar los dos atajos del punto 3. A los pocos días se vuelve automático y el clic derecho en el explorador deja de hacer falta.

¿Tienes algún otro truco para moverte por VSCode sin ratón? Te leo en los comentarios.
