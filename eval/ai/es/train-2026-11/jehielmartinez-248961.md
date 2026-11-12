Si eres desarrollador, tarde o temprano alguien te va a pedir que le muestres lo que sabes hacer. Un CV en PDF está bien, pero nada convence tanto como un enlace donde se vean tus proyectos funcionando. La buena noticia es que no necesitas pagar hosting ni configurar servidores: **GitHub Pages** te permite publicar un sitio estático gratis, directamente desde un repositorio.

En este post vamos a construir un portafolio sencillo, desplegarlo y dejarlo listo para crecer.

## ¿Qué es GitHub Pages?

GitHub Pages es un servicio de alojamiento de sitios estáticos integrado en GitHub. Tomas un repositorio con archivos HTML, CSS y JavaScript, activas Pages, y GitHub lo sirve en una URL del tipo `https://tu-usuario.github.io`.

Sus ventajas principales:

- **Es gratis** para repositorios públicos.
- **HTTPS incluido** sin configurar nada.
- **Despliegue automático**: cada `git push` actualiza el sitio.
- **Soporta dominios personalizados**.

La limitación es que solo sirve contenido estático. No hay backend, ni bases de datos, ni PHP. Para un portafolio, eso es más que suficiente.

## Paso 1: Crear el repositorio

GitHub distingue entre dos tipos de sitios:

1. **Sitio de usuario**: se publica en `tu-usuario.github.io`. Solo puedes tener uno.
2. **Sitio de proyecto**: se publica en `tu-usuario.github.io/nombre-repo`. Puedes tener tantos como repositorios.

Para un portafolio lo ideal es el sitio de usuario. Crea un repositorio nuevo y llámalo **exactamente** `tu-usuario.github.io`, sustituyendo `tu-usuario` por tu nombre de usuario de GitHub. Márcalo como público.

Luego clónalo en tu máquina:

```bash
git clone https://github.com/tu-usuario/tu-usuario.github.io.git
cd tu-usuario.github.io
```

## Paso 2: La estructura básica

Empecemos con algo mínimo. Crea esta estructura:

```
tu-usuario.github.io/
├── index.html
├── style.css
└── img/
```

En `index.html`:

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ana García | Desarrolladora Web</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>Ana García</h1>
    <p>Desarrolladora frontend. Me gusta construir interfaces rápidas y accesibles.</p>
  </header>

  <main>
    <h2>Proyectos</h2>
    <section class="proyectos">
      <article class="tarjeta">
        <img src="img/tareas.png" alt="Captura de la app de tareas">
        <h3>App de tareas</h3>
        <p>Gestor de tareas con almacenamiento local y modo oscuro.</p>
        <a href="https://github.com/tu-usuario/app-tareas">Código</a>
        <a href="https://tu-usuario.github.io/app-tareas">Demo</a>
      </article>
      <!-- Repite la tarjeta para cada proyecto -->
    </section>
  </main>

  <footer>
    <a href="https://github.com/tu-usuario">GitHub</a> ·
    <a href="https://linkedin.com/in/tu-usuario">LinkedIn</a>
  </footer>
</body>
</html>
```

Y un CSS sencillo en `style.css`:

```css
body {
  font-family: system-ui, sans-serif;
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
  line-height: 1.6;
}

.proyectos {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.tarjeta {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
}

.tarjeta img {
  width: 100%;
  border-radius: 4px;
}
```

Con `grid` y `auto-fit`, las tarjetas se reorganizan solas en móviles, sin media queries.

## Paso 3: Publicar

Sube los cambios:

```bash
git add .
git commit -m "Primera versión del portafolio"
git push origin main
```

Ahora ve a tu repositorio en GitHub, entra en **Settings → Pages** y, en **Source**, selecciona **Deploy from a branch**, rama `main` y carpeta `/ (root)`. Guarda.

En uno o dos minutos tu sitio estará disponible en `https://tu-usuario.github.io`. Puedes seguir el progreso en la pestaña **Actions**.

## Paso 4: Publicar las demos de tus proyectos

Aquí está el truco que convierte un portafolio normal en uno muy bueno: **cada proyecto puede tener su propia demo en Pages**.

Si tienes un repositorio `app-tareas` con un frontend estático, activa Pages en ese repositorio igual que antes. Quedará publicado en `https://tu-usuario.github.io/app-tareas`. Enlázalo desde tu tarjeta y quien visite tu portafolio podrá probarlo con un clic.

Si usas un framework como Vite, React o Vue, recuerda configurar la ruta base. En Vite, por ejemplo:

```js
// vite.config.js
export default {
  base: '/app-tareas/',
}
```

Para estos casos, lo más cómodo es elegir **GitHub Actions** como fuente en Settings → Pages y usar un workflow que compile el proyecto y despliegue la carpeta `dist`. GitHub te sugiere plantillas listas para usar.

## Paso 5: Dominio personalizado (opcional)

Si tienes un dominio propio, como `anagarcia.dev`:

1. En **Settings → Pages → Custom domain**, escribe tu dominio y guarda. GitHub creará un archivo `CNAME` en el repositorio.
2. En tu proveedor de DNS, crea un registro `CNAME` para `www` apuntando a `tu-usuario.github.io`, y registros `A` para el dominio raíz apuntando a las IPs que indica la documentación oficial de GitHub.
3. Cuando el DNS se propague, activa **Enforce HTTPS**.

## Consejos para que tu portafolio destaque

- **Menos es más.** Mejor cuatro proyectos sólidos que quince tutoriales a medio terminar.
- **Explica el problema, no solo la tecnología.** "Hice una app para que mi equipo dejara de perder tareas en el chat" dice más que "React + Firebase".
- **Incluye capturas o GIFs.** La gente decide en segundos si sigue leyendo.
- **Cuida los README** de cada repositorio: instrucciones de instalación, capturas y decisiones técnicas.
- **Prueba en móvil.** Muchos reclutadores abren enlaces desde el teléfono.
- **Añade metadatos Open Graph** para que el enlace se vea bien al compartirlo en LinkedIn o X.

## Conclusión

Con un repositorio, un par de archivos y cinco minutos de configuración, tienes un portafolio en línea, gratuito y con HTTPS. A partir de ahí puedes iterar: añadir un generador estático como Astro o Jekyll, un blog, o animaciones. Lo importante es publicarlo hoy y mejorarlo mañana.

¿Ya tienes tu portafolio en GitHub Pages? Déjalo en los comentarios, me encantará verlo. 🚀
