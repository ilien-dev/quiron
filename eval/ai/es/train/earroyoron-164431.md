# El Teorema CAP: por qué los bancos usan mainframes

Es una pregunta que muchos desarrolladores jóvenes se hacen cuando entran a trabajar en una entidad financiera: ¿por qué, en pleno auge de la nube, los microservicios y las bases de datos distribuidas, los bancos siguen confiando su núcleo en mainframes con décadas de historia y programas en COBOL?

La respuesta fácil es "por inercia" o "porque migrar es carísimo", y ambas cosas son ciertas. Pero hay una razón técnica de fondo que tiene mucho que ver con un resultado teórico de los sistemas distribuidos: el **teorema CAP**.

## ¿Qué dice el teorema CAP?

El teorema CAP fue formulado por Eric Brewer en el año 2000 y demostrado formalmente por Seth Gilbert y Nancy Lynch en 2002. Afirma que un sistema de datos distribuido no puede garantizar simultáneamente estas tres propiedades:

- **C (Consistency / Consistencia)**: todos los nodos ven los mismos datos al mismo tiempo. Cualquier lectura devuelve la escritura más reciente.
- **A (Availability / Disponibilidad)**: toda petición recibe una respuesta (no un error), aunque no necesariamente con el dato más reciente.
- **P (Partition tolerance / Tolerancia a particiones)**: el sistema sigue funcionando aunque se pierdan mensajes entre nodos o la red se divida en partes aisladas.

La formulación popular es "elige dos de tres", pero es un poco engañosa. En un sistema distribuido real, **las particiones de red van a ocurrir**: cables que se cortan, switches que fallan, centros de datos que pierden conectividad. No puedes renunciar a P. Así que la elección real es: **cuando haya una partición, ¿prefieres consistencia o disponibilidad?**

- Un sistema **CP** rechazará peticiones (o esperará) antes que arriesgarse a dar datos incorrectos.
- Un sistema **AP** seguirá respondiendo, aunque algunos nodos tengan datos desactualizados, y los reconciliará más tarde.

## El caso de una red social frente a un banco

Imagina que publicas una foto en una red social y, durante unos segundos, un amigo en otro continente no la ve. No pasa nada. Es más, es preferible que la aplicación siga funcionando para todo el mundo aunque los datos tarden un poco en propagarse. Es el terreno de la **consistencia eventual**, y bases de datos como Cassandra o DynamoDB están diseñadas para ello.

Ahora imagina una cuenta bancaria con 100 €. Dos operaciones de retirada de 100 € llegan al mismo tiempo a dos nodos distintos que, por una partición de red, no pueden comunicarse. Si el sistema prioriza la disponibilidad, ambos nodos aprobarán la operación y el banco habrá entregado 200 € de una cuenta que tenía 100.

En banca, **la consistencia no es negociable**. Es preferible que un cajero muestre "servicio no disponible temporalmente" antes que permitir un saldo incorrecto.

## ¿Y qué pinta aquí el mainframe?

Aquí está el truco: la mejor forma de no tener que elegir entre C y A frente a las particiones es **no tener particiones**, o al menos minimizarlas al máximo. Y la forma más directa de conseguirlo es no distribuir.

Un mainframe como los IBM Z es, en esencia, una máquina gigantesca y extremadamente redundante que se comporta como un único sistema. En lugar de repartir la carga entre cientos de servidores pequeños conectados por una red que puede fallar, concentra el procesamiento en un solo equipo con:

- Procesadores, memoria, fuentes de alimentación y canales de E/S redundantes.
- Capacidad de sustituir componentes en caliente sin detener el sistema.
- Disponibilidades que IBM sitúa en torno a los "cinco nueves" (99,999%) o más.
- Un rendimiento transaccional enorme: miles de millones de transacciones al día.

Cuando se necesita más de una máquina, tecnologías como **Parallel Sysplex** permiten agrupar varios mainframes con un mecanismo de coordinación (el *Coupling Facility*) que proporciona bloqueos y caché compartidos a muy baja latencia. Siguen siendo un sistema distribuido, pero en un entorno tan controlado que las particiones son extremadamente raras.

Dicho de otro modo: el mainframe es un sistema **CA en la práctica**, porque invierte muchísimo dinero en hacer que P sea casi imposible.

## Transacciones ACID a escala

A esto se suma que los sistemas transaccionales del mainframe, como CICS o IMS, y bases de datos como DB2, llevan décadas ofreciendo transacciones **ACID** (atomicidad, consistencia, aislamiento y durabilidad) con un rendimiento y una fiabilidad muy probados. Para un banco, cuyo negocio consiste literalmente en mover datos que representan dinero, esa garantía vale más que la flexibilidad de escalar horizontalmente.

## ¿Entonces el mainframe es eterno?

No necesariamente. Hoy existen bases de datos distribuidas que ofrecen consistencia fuerte, como Google Spanner (con relojes atómicos y GPS para sincronizar el tiempo), CockroachDB o YugabyteDB. Y muchos bancos ya operan sus canales digitales, como apps móviles o banca online, en la nube, mientras el núcleo contable sigue en el mainframe.

Lo que no cambia es la lección del teorema CAP: **no existe el sistema distribuido perfecto**. Cada arquitectura hace una apuesta, y la de los bancos, durante más de cincuenta años, ha sido pagar lo que haga falta para no tener que elegir.

## Conclusión

La próxima vez que alguien se ría del mainframe o del COBOL, recuerda que detrás hay una decisión de ingeniería muy razonable: cuando lo que está en juego es el saldo de millones de personas, la consistencia manda, y la forma más fiable de conseguirla es evitar que la red te obligue a elegir.
