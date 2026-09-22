# Cómo crear un portafolio de tus proyectos en GitHub Pages

Si estás buscando tu primer trabajo como desarrollador, o simplemente quieres mostrar lo que sabes hacer, tener un portafolio online es casi obligatorio. Un reclutador puede leer en tu CV que sabes JavaScript, pero ver tus proyectos funcionando es mucho más convincente.

La buena noticia es que no necesitas pagar hosting ni comprar un dominio para empezar. **GitHub Pages** te permite publicar un sitio web estático de forma gratuita directamente desde un repositorio. En este post te explico paso a paso cómo hacerlo.

## ¿Qué es GitHub Pages?

GitHub Pages es un servicio de alojamiento gratuito de GitHub para sitios estáticos, es decir, páginas hechas con HTML, CSS y JavaScript (sin backend). Tu sitio quedará publicado en una dirección como:

```
https://tu-usuario.github.io
```

Es perfecto para portafolios, documentación de proyectos, blogs personales o landing pages.

## Paso 1: crear el repositorio

1. Inicia sesión en GitHub y pulsa **New repository**.
2. En el nombre del repositorio escribe exactamente `tu-usuario.github.io`, sustituyendo `tu-usuario` por tu nombre de usuario de GitHub. Este nombre es especial: le indica a GitHub que es tu sitio personal.
3. Márcalo como **público**.
4. Marca la opción de añadir un archivo README y pulsa **Create repository**.

## Paso 2: clonar el repositorio

En tu terminal:

```bash
git clone https://github.com/tu-usuario/tu-usuario.github.io.git
cd tu-usuario.github.io
```

## Paso 3: crear la página

Crea un archivo `index.html` con una estructura básica:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Portafolio de Ana Pérez</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header>
    <h1>Ana Pérez</h1>
    <p>Desarrolladora web frontend</p>
    <nav>
      <a href="#proyectos">Proyectos</a>
      <a href="#contacto">Contacto</a>
    </nav>
  </header>

  <main>
    <section id="sobre-mi">
      <h2>Sobre mí</h2>
      <p>Me apasiona crear interfaces accesibles y rápidas. Trabajo con HTML, CSS, JavaScript y React.</p>
    </section>

    <section id="proyectos">
      <h2>Proyectos</h2>
      <div class="proyectos">
        <article class="proyecto">
          <h3>App del clima</h3>
          <p>Consulta el pronóstico de cualquier ciudad usando la API de OpenWeather.</p>
          <a href="https://tu-usuario.github.io/app-clima">Ver demo</a>
          <a href="https://github.com/tu-usuario/app-clima">Código</a>
        </article>
        <article class="proyecto">
          <h3>Lista de tareas</h3>
          <p>Gestor de tareas con React y almacenamiento local.</p>
          <a href="https://tu-usuario.github.io/lista-tareas">Ver demo</a>
          <a href="https://github.com/tu-usuario/lista-tareas">Código</a>
        </article>
      </div>
    </section>

    <section id="contacto">
      <h2>Contacto</h2>
      <p>Escríbeme a <a href="mailto:ana@example.com">ana@example.com</a> o encuéntrame en
        <a href="https://www.linkedin.com/in/tu-usuario">LinkedIn</a>.</p>
    </section>
  </main>
</body>
</html>
```

Y un archivo `styles.css` con algo de diseño:

```css
body {
  font-family: system-ui, sans-serif;
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  line-height: 1.6;
  color: #222;
}

header {
  text-align: center;
  margin-bottom: 3rem;
}

nav a {
  margin: 0 0.5rem;
}

.proyectos {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.proyecto {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
}

.proyecto a {
  margin-right: 1rem;
}
```

## Paso 4: publicar

Sube los cambios:

```bash
git add .
git commit -m "Primera versión del portafolio"
git push origin main
```

En uno o dos minutos, tu portafolio estará disponible en `https://tu-usuario.github.io`. Puedes comprobar el estado del despliegue en la pestaña **Actions** del repositorio, o en **Settings → Pages**.

## Publicar también tus proyectos

Lo interesante es que cada proyecto puede tener su propia demo. En cualquier otro repositorio, ve a **Settings → Pages**, selecciona la rama `main` y la carpeta raíz (o `/docs`) y guarda. El proyecto quedará publicado en:

```
https://tu-usuario.github.io/nombre-del-repositorio
```

Así puedes enlazar desde el portafolio a demos que funcionan de verdad.

Si tus proyectos usan React o Vite, tendrás que generar el build y publicar la carpeta resultante. Una forma cómoda es usar el paquete `gh-pages` o configurar una GitHub Action que lo haga automáticamente en cada push.

## Usar un dominio propio (opcional)

Si más adelante compras un dominio, puedes configurarlo en **Settings → Pages → Custom domain** y añadir los registros DNS que indica GitHub. El certificado HTTPS se genera de forma gratuita.

## Consejos para un buen portafolio

- **Calidad antes que cantidad**: tres proyectos bien hechos valen más que diez tutoriales copiados.
- **Explica cada proyecto**: qué problema resuelve, qué tecnologías usaste y qué aprendiste.
- **Incluye demos y código**: que se pueda probar y revisar.
- **Cuida los README** de tus repositorios, porque los reclutadores también los leen.
- **Hazlo responsive**: muchas personas lo abrirán desde el móvil.
- **Mantenlo actualizado** a medida que termines nuevos proyectos.

## Conclusión

Con GitHub Pages puedes tener un portafolio profesional publicado en menos de una hora y sin gastar nada. Empieza con algo sencillo, publícalo y ve mejorándolo con el tiempo. Lo importante es que tus proyectos dejen de estar escondidos en tu ordenador y empiecen a hablar por ti.
