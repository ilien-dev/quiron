# Qué es PolymerJs y porqué tenés que saberlo

Imaginá que pudieras crear tus propias etiquetas HTML. Que, además de `<button>` o `<input>`, tuvieras un `<perfil-usuario>` con su diseño, sus datos y su comportamiento. Después podrías reutilizarlo en distintas pantallas sin copiar y pegar la misma estructura.

Esa es la idea que ayuda a entender PolymerJs: construir componentes reutilizables apoyándose en las capacidades del navegador.

Pero antes de entusiasmarte con una nueva herramienta, hay un dato clave: **Polymer está en modo de mantenimiento y su documentación recomienda Lit para desarrollos nuevos**. Entonces, ¿por qué dedicarle tiempo? Porque entender su propuesta te permite comprender mejor los Web Components y trabajar con proyectos que todavía lo utilizan. [Fuente: Polymer Project](https://library.polymer-project.org/3.0/docs/first-element/intro).

Polymer es una biblioteca de JavaScript que facilita la creación de elementos HTML personalizados. Agrega herramientas para declarar propiedades, vincular datos con una plantilla y reaccionar a cambios. Su objetivo es simplificar la construcción de componentes que puedas usar como elementos del DOM. [Documentación oficial](https://polymer-library.polymer-project.org/3.0/docs/devguide/feature-overview).

Para visualizarlo, pensá en una tarjeta de producto:

```html
<tarjeta-producto
  nombre="Teclado mecánico"
  precio="120">
</tarjeta-producto>
```

Esa etiqueta es un ejemplo de la interfaz que podrías diseñar. Por dentro, el componente tendría el marcado de la tarjeta, sus estilos y la lógica necesaria para mostrar información o responder a una interacción.

Desde afuera, quien lo usa solo necesita conocer sus propiedades y eventos. Esa separación permite cambiar detalles internos sin obligar a revisar cada pantalla que incorpora la tarjeta.

La propuesta se apoya en conceptos que conviene distinguir:

- **Custom Elements:** permiten registrar etiquetas personalizadas y definir su comportamiento mediante JavaScript.
- **Shadow DOM:** permite encapsular la estructura interna de un componente y delimitar el alcance de sus estilos.
- **Plantillas HTML:** sirven como base para definir estructuras que después se instancian.

Polymer combina esas capacidades con su propio sistema de datos, que incluye enlaces entre propiedades y vistas, observadores y propiedades calculadas. Podés consultar cómo encajan estas piezas en su [guía de funcionalidades](https://polymer-library.polymer-project.org/3.0/docs/devguide/feature-overview).

Hay una distinción fundamental: **Polymer es una biblioteca; los Web Components son tecnologías de la plataforma web**. Aprender la biblioteca implica conocer convenciones particulares. Aprender las bases del navegador te da conocimientos que también podés aplicar al trabajar con otras herramientas.

Esto tiene consecuencias prácticas. Si diseñás un componente reutilizable, necesitás decidir qué información recibe, qué eventos emite y qué responsabilidades resuelve. Esas decisiones importan tanto como la sintaxis que elegís para implementarlo.

Por ejemplo, una tarjeta podría emitir un evento cuando alguien quiere agregar un producto al carrito. La aplicación que la contiene decidiría cómo actualizar la compra. El componente presenta una interacción; la aplicación coordina el proceso.

También vale la pena conocer Polymer cuando te toca mantener código existente. Reconocer su sistema de propiedades, sus plantillas y sus mecanismos de actualización te ayuda a investigar errores y estimar cambios. Antes de proponer una migración, necesitás entender qué comportamiento sostiene la aplicación y cuánto costaría conservarlo.

Ahora bien, si estás empezando un proyecto, la recomendación oficial de explorar Lit merece atención. Estudiar Polymer puede servirte como contexto histórico o como preparación para una tarea concreta; la profundidad dependerá del código con el que vayas a trabajar.

El título dice que tenés que saberlo, y hay un matiz: conocer su propuesta puede ser suficiente. No necesitás dominar cada API para llevarte una pregunta útil a tu próximo proyecto: ¿qué partes de esta interfaz podrían tener un contrato claro y funcionar como componentes reutilizables?

Probá empezar por una tarjeta, un selector o una alerta. Definí qué recibe y qué comunica. Ahí empieza buena parte del trabajo de diseñar componentes.
