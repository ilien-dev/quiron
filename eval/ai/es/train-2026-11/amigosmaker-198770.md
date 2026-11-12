# PyQt vs Tkinter (Spanish)

Si alguna vez te has preguntado qué biblioteca usar para crear una interfaz gráfica en Python, seguramente te has encontrado con dos nombres: **Tkinter** y **PyQt**. Ambas permiten construir aplicaciones de escritorio, pero con filosofías distintas. En este post las comparamos para que elijas la que mejor se adapte a tu proyecto.

## Tkinter: la opción incluida

Tkinter es la biblioteca estándar de Python para GUI. Viene incluida en la mayoría de instalaciones, así que no necesitas instalar nada extra. Está basada en Tk, un toolkit gráfico con décadas de uso.

Sus principales ventajas:

- **Cero dependencias externas.** Basta con importarla.
- **Curva de aprendizaje suave.** Un programa básico cabe en pocas líneas.
- **Ligereza.** Los ejecutables resultantes suelen ser más pequeños.
- **Abundante documentación** y muchos tutoriales.

Un ejemplo mínimo:

```python
import tkinter as tk

ventana = tk.Tk()
ventana.title("Hola")

etiqueta = tk.Label(ventana, text="¡Hola, mundo!")
etiqueta.pack(padx=20, pady=20)

boton = tk.Button(ventana, text="Cerrar", command=ventana.destroy)
boton.pack(pady=10)

ventana.mainloop()
```

Sin embargo, Tkinter tiene limitaciones. Sus widgets se ven anticuados por defecto y personalizarlos requiere esfuerzo. Bibliotecas como `ttkbootstrap` o `customtkinter` mejoran la apariencia, pero el resultado no siempre alcanza el nivel de las aplicaciones modernas. En proyectos grandes, además, la organización del código puede complicarse si no se aplica una arquitectura clara.

## PyQt: potencia profesional

PyQt son los enlaces de Python para Qt, un framework multiplataforma escrito en C++ y muy usado en la industria. La versión actual es PyQt6. Existe también PySide6, su equivalente oficial, con una licencia más permisiva.

Sus puntos fuertes:

- **Widgets sofisticados:** tablas, árboles, gráficos y vistas modelo-vista.
- **Diseño visual** con Qt Designer, que genera archivos `.ui`.
- **Sistema de señales y slots**, que desacopla la lógica de la interfaz.
- **Apariencia nativa y consistente** en Windows, macOS y Linux.
- **Módulos avanzados** para multimedia, redes y OpenGL.

El mismo ejemplo con PyQt6:

```python
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout

app = QApplication(sys.argv)

ventana = QWidget()
ventana.setWindowTitle("Hola")

layout = QVBoxLayout(ventana)
layout.addWidget(QLabel("¡Hola, mundo!"))

boton = QPushButton("Cerrar")
boton.clicked.connect(ventana.close)
layout.addWidget(boton)

ventana.show()
sys.exit(app.exec())
```

El código es algo más extenso, pero la estructura es clara y escala bien.

También tiene desventajas. Es más pesado, y la biblioteca añade varios megabytes a tu proyecto. La licencia requiere atención: PyQt está disponible bajo GPL o licencia comercial, mientras que PySide6 usa LGPL, que suele ser más conveniente para proyectos cerrados. Además, la curva de aprendizaje es más pronunciada, sobre todo si no conoces conceptos como el bucle de eventos o el modelo-vista.

## Comparativa rápida

| Aspecto | Tkinter | PyQt6 |
|---|---|---|
| Instalación | Incluida en Python | `pip install` |
| Apariencia | Básica, personalizable con esfuerzo | Moderna y nativa |
| Widgets avanzados | Limitados | Extensos |
| Curva de aprendizaje | Suave | Moderada a alta |
| Tamaño | Ligero | Más pesado |
| Licencia | PSF (permisiva) | GPL / comercial |

## ¿Cuál elegir?

Usa **Tkinter** si:

- Estás aprendiendo a programar interfaces gráficas.
- Necesitas una herramienta sencilla, como un formulario o una utilidad interna.
- No quieres añadir dependencias al proyecto.

Usa **PyQt** (o PySide6) si:

- Vas a desarrollar una aplicación de escritorio profesional y compleja.
- Necesitas widgets avanzados, gráficos o trabajo con datos tabulares.
- Quieres una apariencia moderna sin invertir mucho tiempo en estilos.

## Conclusión

No hay una respuesta universal. Tkinter es ideal para empezar y para proyectos pequeños; PyQt ofrece una potencia que justifica su complejidad cuando la aplicación crece. Si tienes dudas, prueba ambas con el mismo ejercicio: una ventana con un formulario y una tabla. La experiencia te dirá más que cualquier comparación.

¿Tú qué usas? Cuéntanos en los comentarios.
