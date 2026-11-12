"Full stack" es probablemente el título más inflado de nuestra industria. Hay ofertas que piden dominar doce tecnologías y perfiles de LinkedIn que lo usan tras completar un tutorial de to-do list. Entre ambos extremos hay una definición razonable, y es más sencilla de lo que parece.

Mi propuesta: **eres full stack si puedes llevar una funcionalidad desde la idea hasta producción sin que nadie tenga que rescatarte en ninguna capa.** No hace falta ser experto en todas; hace falta ser autónomo en todas.

Esto es lo mínimo que eso implica.

## 1. Los fundamentos de la web

Antes de cualquier framework, necesitas entender cómo funciona HTTP: métodos, códigos de estado, cabeceras, cookies, CORS. Si no sabes explicar qué ocurre entre que escribes una URL y aparece la página, todo lo demás se construye sobre arena.

## 2. Frontend: HTML, CSS, JavaScript y un framework

- **HTML semántico** y nociones básicas de accesibilidad.
- **CSS** suficiente para maquetar un diseño responsive con Flexbox y Grid sin pelearte durante horas.
- **JavaScript** de verdad: asincronía, closures, manipulación del DOM, módulos. TypeScript ya es prácticamente el estándar, así que cuenta con él.
- **Un framework** (React, Vue, Svelte, Angular; el que sea). Con uno basta, siempre que entiendas los conceptos que comparten todos: componentes, estado, renderizado y ciclo de vida.

## 3. Backend: un lenguaje y una API bien hecha

Elige un lenguaje de servidor (Node.js, Python, Java, C#, Go, PHP) y aprende a construir con él una API REST que:

- Valide los datos de entrada.
- Gestione errores de forma coherente.
- Implemente autenticación y autorización (sesiones o tokens, y saber cuándo usar cada uno).
- Separe razonablemente rutas, lógica de negocio y acceso a datos.

## 4. Bases de datos: SQL sin miedo

Puedes usar un ORM, pero debes poder escribir SQL a mano: `JOIN`, agregaciones, índices, transacciones. También modelar un esquema relacional sencillo y entender por qué una consulta va lenta. Saber cuándo tiene sentido una base NoSQL es un extra; saber SQL no lo es.

## 5. Git y trabajo en equipo

Ramas, merges, rebase, resolución de conflictos y pull requests. No hay proyecto profesional sin esto, y es donde más se nota quién ha trabajado en equipo y quién no.

## 6. Despliegue: que funcione fuera de tu máquina

No necesitas ser DevOps, pero sí saber:

- Desplegar una aplicación en algún proveedor.
- Manejar variables de entorno y secretos.
- Lo básico de Docker.
- Leer logs para diagnosticar un fallo en producción.
- Qué hace un pipeline de CI/CD, aunque no lo hayas montado tú.

## 7. Seguridad y testing básicos

Conoce las vulnerabilidades clásicas (inyección SQL, XSS, CSRF) y cómo las previene tu stack. Nunca guardes contraseñas en texto plano. Y escribe al menos tests unitarios y de integración para la lógica crítica: no por dogma, sino para poder cambiar código sin miedo.

## Lo que NO necesitas

- Kubernetes.
- Microservicios.
- Cinco frameworks de frontend.
- Dominar cada capa al nivel de un especialista.

El perfil realista es en forma de T: una base amplia y una zona donde profundizas más. Casi todos los full stack tiran hacia el front o hacia el back, y no pasa nada.

## La prueba definitiva

Construye una aplicación completa: registro de usuarios, un CRUD con relaciones entre datos, desplegada en una URL pública y con tests. Si puedes hacerlo solo, depurando lo que falle en cualquier capa, eres full stack. Júnior, quizá, pero full stack.

El título no va de saberlo todo. Va de no quedarte bloqueado cuando el problema cruza la frontera entre el navegador y el servidor.

¿Y tú? ¿Qué añadirías o quitarías de la lista? Te leo en los comentarios. 👇
