# NodeJS, la vida de los procesos

Cuando ejecutamos un archivo con `node app.js`, parece que ocurre algo sencillo: Node.js interpreta el código, muestra algún resultado y termina. Sin embargo, detrás de esa aparente simplicidad existe todo un ciclo de vida gobernado por el proceso, el *event loop* y los recursos que nuestra aplicación mantiene activos.

Entender este ciclo es fundamental para construir servicios confiables, evitar procesos “zombis” y cerrar correctamente conexiones antes de apagar una aplicación.

## El objeto `process`

Cada aplicación de Node.js se ejecuta dentro de un proceso del sistema operativo. Node expone información y mecanismos de control mediante el objeto global `process`, que no necesita importarse.

```js
console.log(process.pid);
console.log(process.platform);
console.log(process.version);
```

También podemos acceder a los argumentos utilizados al iniciar el programa:

```js
const args = process.argv.slice(2);

console.log(args);
```

Si ejecutamos:

```bash
node app.js producción 3000
```

`args` contendrá `["producción", "3000"]`.

Otro elemento importante son las variables de entorno, disponibles en `process.env`:

```js
const port = process.env.PORT || 3000;
```

Estas variables permiten configurar una aplicación sin modificar su código, algo especialmente útil en contenedores, servidores y plataformas de despliegue.

## ¿Cuándo termina un proceso?

Un proceso de Node.js termina naturalmente cuando ya no queda trabajo pendiente en el *event loop*. Eso significa que no existen temporizadores, servidores, conexiones, operaciones de entrada y salida ni otros recursos activos.

Este programa termina inmediatamente:

```js
console.log("Hola");
```

En cambio, este permanece vivo:

```js
setInterval(() => {
  console.log("Sigo aquí");
}, 1000);
```

El intervalo mantiene trabajo pendiente y, por tanto, evita que el proceso finalice.

Podemos llamar a `process.exit()` para forzar la terminación:

```js
process.exit(0);
```

El argumento es el código de salida. Por convención, `0` representa una ejecución correcta y cualquier otro valor indica un error.

Aun así, conviene utilizar `process.exit()` con cuidado. Su ejecución es inmediata: las escrituras pendientes, los registros y otras operaciones asíncronas podrían quedar incompletos. Normalmente es mejor asignar el código y permitir que el proceso termine por sí mismo:

```js
process.exitCode = 1;
```

## Señales y cierre controlado

En producción, una aplicación puede recibir señales del sistema operativo. Por ejemplo, `SIGINT` suele enviarse al presionar `Ctrl+C`, mientras que `SIGTERM` es común cuando un orquestador solicita detener un servicio.

Podemos escucharlas para realizar un cierre controlado:

```js
const server = app.listen(3000);

process.on("SIGTERM", () => {
  console.log("Cerrando servidor...");

  server.close(() => {
    console.log("Servidor cerrado");
    process.exitCode = 0;
  });
});
```

Este patrón permite dejar de aceptar nuevas solicitudes mientras se completan las que ya están en curso. También es el momento adecuado para cerrar conexiones a bases de datos, liberar archivos o detener consumidores de mensajes.

## Errores que alcanzan al proceso

Node.js permite observar errores no capturados:

```js
process.on("uncaughtException", (error) => {
  console.error("Error no capturado:", error);
});
```

También podemos detectar promesas rechazadas sin manejo:

```js
process.on("unhandledRejection", (reason) => {
  console.error("Promesa rechazada:", reason);
});
```

Estos eventos son útiles para registrar información antes de finalizar, pero no deberían convertirse en una estrategia para continuar ejecutando la aplicación. Después de un error no capturado, el estado interno podría ser inconsistente. Lo más seguro suele ser registrar el problema, cerrar recursos y permitir que un supervisor reinicie el proceso.

## Procesos preparados para producción

La vida de un proceso no termina en el código. Herramientas como systemd, Docker, Kubernetes o administradores especializados pueden iniciar, vigilar y reiniciar aplicaciones Node.js.

Nuestra responsabilidad es hacer que el proceso sea predecible: configurar mediante variables de entorno, reportar errores con códigos de salida, responder a señales y cerrar recursos correctamente.

Un buen proceso no es aquel que nunca termina. Es aquel que sabe cuándo seguir trabajando, cuándo detenerse y cómo despedirse sin dejar asuntos pendientes.