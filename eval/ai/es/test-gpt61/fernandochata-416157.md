# NodeJS, la vida de los procesos.

Ejecutas `node app.js`, la terminal se queda esperando y tu servidor empieza a recibir peticiones. Parece sencillo: el programa arranca y hace su trabajo. Pero entre ese primer comando y el momento en que termina existe una historia que conviene conocer.

Entender la vida de un proceso en Node.js ayuda a responder preguntas muy prácticas: ¿por qué mi aplicación no termina?, ¿por qué se bloquea si todo es asíncrono?, ¿qué ocurre cuando reinicio un contenedor?

Vamos por partes.

## El nacimiento: algo más que ejecutar JavaScript

Cuando ejecutamos un archivo con Node.js, el sistema operativo crea un proceso. Este tiene un identificador, memoria, variables de entorno y acceso a recursos como archivos o conexiones de red.

Podemos consultar parte de esa información mediante el objeto `process`:

```js
console.log("PID:", process.pid);
console.log("Argumentos:", process.argv);
console.log("Entorno:", process.env.NODE_ENV);
```

Node inicializa su entorno, carga nuestro código y ejecuta las instrucciones iniciales. En esa etapa podemos registrar temporizadores, abrir un servidor o iniciar operaciones de entrada y salida.

Aquí aparece un protagonista habitual: el **event loop**.

## La vida cotidiana: trabajo, esperas y callbacks

El event loop permite coordinar trabajo asíncrono. Cuando una operación está lista para continuar, Node puede ejecutar el callback correspondiente.

Eso no significa que todo ocurra en un único hilo. El código JavaScript de una instancia normalmente se ejecuta en un hilo principal, mientras que Node también utiliza mecanismos del sistema operativo y, para determinadas tareas, un conjunto de hilos gestionado por libuv.

La diferencia importa porque **asíncrono no significa que cualquier trabajo deje de bloquear**.

```js
setTimeout(() => {
  console.log("Por fin me toca");
}, 100);

const inicio = Date.now();

while (Date.now() - inicio < 2000) {
  // Ocupamos el hilo principal durante dos segundos.
}
```

El temporizador no interrumpe el bucle. Su callback tendrá que esperar hasta que el hilo principal quede disponible. Los cien milisegundos indican un umbral mínimo, no una cita exacta.

Para cálculos intensivos podemos recurrir a `worker_threads`, otros procesos o servicios especializados.

## ¿Qué mantiene vivo al proceso?

Un servidor HTTP sigue funcionando porque mantiene un recurso activo esperando conexiones. También pueden mantener vivo al proceso ciertos temporizadores y operaciones pendientes.

En cambio, una promesa pendiente, por sí sola, no garantiza que Node continúe ejecutándose:

```js
new Promise(() => {
  // Nunca se resuelve.
});

console.log("Terminé mi trabajo");
```

Este programa puede finalizar después del mensaje. La promesa no crea automáticamente un recurso que mantenga activo el event loop.

Esta distinción resulta útil cuando una aplicación termina antes de lo esperado o permanece abierta sin motivo aparente. Conviene revisar servidores, conexiones y temporizadores, además de las promesas.

## El final: salir también requiere diseño

Un proceso puede terminar naturalmente cuando ya no tiene trabajo que lo mantenga vivo. También puede finalizar por un error fatal, una llamada explícita o una señal del sistema operativo.

En servidores, una estrategia habitual es escuchar `SIGTERM` para iniciar un cierre ordenado:

```js
const server = app.listen(3000);

process.on("SIGTERM", () => {
  server.close(() => {
    process.exitCode = 0;
  });
});
```

El ejemplo supone una aplicación HTTP llamada `app`. Al recibir la señal, dejamos de aceptar conexiones y esperamos a que el servidor termine de cerrarse.

En una aplicación real también debemos cerrar conexiones a bases de datos, detener consumidores y establecer un tiempo máximo de espera. El comportamiento de las señales, además, puede variar entre plataformas.

Llamar a `process.exit()` inmediatamente puede interrumpir operaciones pendientes, incluidas escrituras de salida. Cuando sea posible, es preferible liberar recursos y permitir que el proceso termine naturalmente.

La vida de un proceso no acaba cuando responde la última petición. Acaba cuando entrega sus recursos, completa el trabajo pendiente y permite que el siguiente proceso ocupe su lugar. Diseñar ese final también es programar.
