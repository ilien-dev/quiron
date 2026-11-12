# NodeJS, la vida de los procesos.

Cuando ejecutamos `node app.js`, algo aparentemente sencillo sucede: una aplicación comienza a funcionar. Pero detrás de esa instrucción hay un proceso con memoria, variables de entorno, recursos abiertos y un ciclo de vida que tarde o temprano llegará a su fin.

Entender ese ciclo es útil para desarrollar aplicaciones más estables. No basta con saber cómo arrancan: también debemos saber cómo reciben señales, cómo manejan errores y cómo se despiden.

## Todo comienza con un proceso

Un proceso es una instancia de un programa en ejecución. Cuando iniciamos Node.js, el sistema operativo crea uno y le asigna un identificador, conocido como PID.

Podemos consultarlo mediante el objeto global `process`:

```js
console.log(`Mi PID es ${process.pid}`);
console.log(`Versión de Node.js: ${process.version}`);
```

Este objeto también nos permite acceder a información del entorno, argumentos de línea de comandos y eventos relacionados con la vida del proceso.

Por ejemplo, si ejecutamos:

```bash
node app.js desarrollo
```

Podemos leer el argumento así:

```js
const entorno = process.argv[2];

console.log(`Entorno seleccionado: ${entorno}`);
```

Los dos primeros elementos de `process.argv` contienen, normalmente, la ruta del ejecutable de Node.js y la del archivo ejecutado. Los argumentos que agregamos empiezan después.

## ¿Qué mantiene vivo a Node.js?

Node.js no termina necesariamente cuando llega a la última línea del archivo. El proceso sigue activo mientras existan tareas o recursos pendientes que mantengan ocupado su ciclo de eventos.

Un temporizador es un ejemplo sencillo:

```js
setTimeout(() => {
  console.log("Han pasado tres segundos");
}, 3000);

console.log("Esperando...");
```

Aunque `console.log("Esperando...")` se ejecuta primero, el proceso permanece vivo hasta que se ejecuta el temporizador. Algo similar ocurre con un servidor que escucha conexiones o con ciertas operaciones de entrada y salida pendientes.

Cuando ya no queda trabajo que mantener activo, Node.js puede finalizar de forma natural.

## Escuchar la despedida

El objeto `process` emite eventos que nos permiten observar algunos momentos de la salida. Uno de ellos es `exit`:

```js
process.on("exit", (codigo) => {
  console.log(`El proceso termina con código ${codigo}`);
});
```

En este evento solo debemos realizar trabajo **síncrono**. No es el lugar adecuado para esperar una consulta a la base de datos ni para programar un temporizador: el proceso ya está en camino de terminar.

También existe `beforeExit`, que se emite cuando Node.js se queda sin trabajo pendiente en su ciclo de eventos. Un manejador puede programar trabajo adicional y hacer que el proceso continúe. No se emite en todas las formas de terminación, así que no conviene depender de él como único mecanismo de limpieza.

## Señales y cierre ordenado

En un servidor real, el proceso puede recibir una señal para detenerse. En muchos entornos, `SIGTERM` se utiliza para solicitar un cierre ordenado.

La idea es dejar de aceptar conexiones nuevas, terminar el trabajo en curso y liberar recursos:

```js
const http = require("node:http");

const servidor = http.createServer((req, res) => {
  res.end("Hola desde Node.js");
});

servidor.listen(3000);

process.on("SIGTERM", () => {
  console.log("Cerrando el servidor...");

  servidor.close(() => {
    console.log("Servidor cerrado");
    process.exitCode = 0;
  });
});
```

Una aplicación con una base de datos o una cola de mensajes también debería cerrar esas conexiones. En producción suele ser útil establecer un tiempo límite para evitar que una conexión pendiente retrase el cierre indefinidamente. El comportamiento de las señales puede variar según el sistema operativo y el entorno de ejecución.

## Los errores también forman parte de la vida

Si una excepción no se captura, Node.js normalmente imprime el error y finaliza con un código distinto de cero. Esto permite que el sistema o una herramienta de supervisión detecte el fallo.

Aunque es posible escuchar `uncaughtException`, continuar como si nada hubiera pasado puede ser peligroso: la aplicación podría haber quedado en un estado inconsistente. Es preferible usar ese evento para registrar información crítica y preparar la salida, dejando que un supervisor gestione el reinicio cuando corresponda.

Un proceso de Node.js nace, trabaja y termina. Conocer esas etapas nos ayuda a diseñar aplicaciones que no solo responden correctamente cuando todo va bien, sino que también saben cerrar sus conexiones y comunicar sus fallos cuando llega el momento de detenerse.
