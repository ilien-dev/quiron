# ¿Qué es lo mínimo que debes saber para considerarte full stack developer?

"Full stack" es una de esas etiquetas que todo el mundo usa y casi nadie define. Hay ofertas de trabajo que piden React, Node, Kubernetes, Terraform, machine learning y diez años de experiencia en un framework de hace tres. Con esas listas es normal sentir síndrome del impostor.

La pregunta útil no es "¿lo sé todo?", sino otra: **¿puedo llevar una idea desde cero hasta producción, yo solo, y mantenerla funcionando?** Si la respuesta es sí, eres full stack. Esto es lo mínimo que necesitas para conseguirlo.

## 1. Los fundamentos de la web

Antes de cualquier framework, entiende cómo funciona la web por debajo:

- **HTTP**: métodos (GET, POST, PUT, DELETE), códigos de estado, cabeceras, cookies.
- **Qué ocurre cuando escribes una URL**: DNS, TCP, TLS, petición y respuesta.
- **El modelo cliente-servidor**: qué se ejecuta en el navegador, qué en el servidor y por qué importa.

Si sabes explicar por qué tu petición falla con un error de CORS, ya vas por delante de mucha gente.

## 2. Frontend: HTML, CSS y JavaScript de verdad

No hace falta ser diseñador, pero sí:

- **HTML semántico** y nociones básicas de accesibilidad.
- **CSS** suficiente para maquetar con Flexbox y Grid, y para que tu app funcione en móvil.
- **JavaScript moderno**: promesas, `async/await`, módulos, manipulación del DOM y `fetch`.
- **Un framework** (React, Vue, Svelte, el que sea) a nivel de componentes, estado y enrutado.

La clave es que entiendas el JavaScript que hay debajo del framework. Los frameworks cambian; el lenguaje se queda.

## 3. Backend: un lenguaje y un framework

Elige uno y domínalo razonablemente: Node con Express o Fastify, Python con Django o FastAPI, Go, Java con Spring, PHP con Laravel... Da igual cuál. Lo importante es saber:

- Diseñar una **API REST** coherente (y conocer de qué va GraphQL).
- Manejar **autenticación y autorización**: sesiones, tokens, hash de contraseñas. Nunca guardes contraseñas en texto plano.
- **Validar la entrada** del usuario y gestionar errores sin filtrar información sensible.

## 4. Bases de datos

Aquí es donde muchos "full stack" flojean. Lo mínimo:

- **SQL**: `SELECT`, `JOIN`, índices y relaciones. PostgreSQL es una apuesta excelente.
- **Modelado de datos**: normalización básica y cuándo saltársela.
- Saber que existen **bases NoSQL** y en qué casos tienen sentido.
- Usar un ORM sin olvidar qué consultas genera por debajo. El problema N+1 te encontrará tarde o temprano.

## 5. Git y trabajo en equipo

No basta con `git add . && git commit -m "cambios"`. Necesitas ramas, merges, resolver conflictos, hacer pull requests y escribir mensajes de commit que tu yo del futuro entienda.

## 6. Despliegue: que exista fuera de tu portátil

Una app que solo funciona en `localhost` no es un producto. Aprende a:

- Desplegar en algún proveedor (Render, Fly.io, Vercel, un VPS...).
- Usar **variables de entorno** y no subir secretos al repositorio.
- Conocer lo básico de **Docker**.
- Configurar un dominio y HTTPS.
- Leer logs cuando algo se rompe en producción, porque se romperá.

## 7. Seguridad básica

No necesitas ser pentester, pero sí conocer el **OWASP Top 10**: inyección SQL, XSS, CSRF, control de acceso roto. Son los errores más comunes y los más fáciles de evitar si sabes que existen.

## Lo que NO necesitas (todavía)

Microservicios, Kubernetes, cinco frameworks de frontend, arquitecturas basadas en eventos... Todo eso tiene su lugar, pero no forma parte del mínimo. Aprende primero a construir un monolito bien hecho.

## La prueba definitiva

Construye un proyecto completo: una app con registro de usuarios, una base de datos, un frontend usable y desplegada con su propio dominio. Algo pequeño, como un gestor de tareas o un acortador de enlaces, pero terminado de verdad.

Si puedes hacerlo, explicar cada decisión y arreglarlo cuando falle, felicidades: eres full stack. Lo demás es profundidad, y esa se gana con los años.

---

*¿Qué añadirías o quitarías de esta lista? Te leo en los comentarios.* 👇
