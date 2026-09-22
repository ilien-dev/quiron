# ¿Qué es lo mínimo que debes saber para considerarte full stack developer?

"Full stack developer" es uno de esos títulos que aparecen en todas partes: en ofertas de trabajo, en perfiles de LinkedIn y en bootcamps que prometen convertirte en uno en tres meses. Pero, ¿qué significa realmente? ¿Tienes que dominar diez lenguajes, cinco frameworks y saber configurar un clúster de Kubernetes?

La respuesta corta es no. Ser full stack no significa saberlo todo, sino ser capaz de construir una aplicación completa, de principio a fin, por tu cuenta. En este post te cuento cuál es, en mi opinión, el mínimo razonable.

## 1. Frontend: HTML, CSS y JavaScript

Todo empieza en el navegador. Como mínimo, deberías:

- Escribir **HTML semántico** y entender la estructura de un documento.
- Maquetar con **CSS**, incluyendo Flexbox, Grid y diseño responsive con media queries.
- Manejar **JavaScript** con soltura: variables, funciones, arrays, objetos, manipulación del DOM, eventos y, muy importante, asincronía (`Promise`, `async/await`, `fetch`).

No necesitas ser un experto en animaciones ni en accesibilidad avanzada, pero sí saber crear una interfaz funcional y decente.

## 2. Un framework de frontend

Hoy en día casi ningún proyecto se hace con JavaScript puro. Aprende **uno** de los frameworks populares: React, Vue o Angular. Da igual cuál elijas; lo importante es entender los conceptos que comparten:

- Componentes.
- Estado y props.
- Renderizado condicional y listas.
- Comunicación con una API.

Una vez que dominas uno, pasar a otro es cuestión de semanas.

## 3. Backend: un lenguaje y un framework

En el lado del servidor necesitas un lenguaje y un framework para construir APIs. Algunas combinaciones comunes:

- JavaScript/TypeScript con **Node.js** y Express o NestJS.
- Python con **Django** o FastAPI.
- Ruby con **Rails**.
- PHP con **Laravel**.

Lo mínimo aquí es saber crear una **API REST**: definir rutas, recibir y validar datos, devolver respuestas JSON con los códigos de estado HTTP adecuados y gestionar errores.

## 4. Bases de datos

Toda aplicación real guarda datos. Deberías saber:

- **SQL básico**: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `JOIN` y cómo diseñar tablas con relaciones.
- Usar una base de datos relacional como **PostgreSQL** o MySQL.
- Trabajar con un ORM (Prisma, Sequelize, SQLAlchemy, ActiveRecord...).

Conocer una base de datos NoSQL como MongoDB es un plus, pero no imprescindible al principio.

## 5. Autenticación

Casi cualquier aplicación necesita usuarios. Es fundamental entender cómo funciona un registro e inicio de sesión: guardar contraseñas con hash (nunca en texto plano), sesiones o tokens JWT y cómo proteger rutas.

## 6. HTTP y cómo funciona la web

Suena básico, pero mucha gente lo pasa por alto. Entiende qué pasa cuando escribes una URL en el navegador: DNS, peticiones y respuestas HTTP, métodos (`GET`, `POST`, `PUT`, `DELETE`), cabeceras, cookies y CORS. Te ahorrará muchas horas de depuración.

## 7. Git

No es negociable. Debes saber crear repositorios, hacer commits, trabajar con ramas, resolver conflictos y usar GitHub o GitLab para colaborar mediante pull requests.

## 8. Despliegue

Una aplicación que solo funciona en `localhost` no está terminada. Aprende a desplegar tu proyecto en algún servicio como Vercel, Netlify, Render, Railway o un VPS. Entiende qué son las variables de entorno y cómo configurar un dominio.

Docker y CI/CD son muy recomendables, pero puedes ir aprendiéndolos sobre la marcha.

## Lo que no necesitas (todavía)

- Microservicios.
- Kubernetes.
- Saber todos los frameworks del momento.
- GraphQL, WebSockets, colas de mensajes...

Todo eso es útil y lo aprenderás cuando un proyecto lo requiera.

## La prueba definitiva

Si quieres saber si ya eres full stack, hazte esta pregunta: **¿puedo construir y publicar una aplicación con usuarios, base de datos y una interfaz, sin ayuda de nadie?** Por ejemplo, un gestor de tareas con registro, login y CRUD completo, desplegado en internet.

Si la respuesta es sí, felicidades: ya lo eres. El resto es seguir aprendiendo, que en esta profesión no se termina nunca.
