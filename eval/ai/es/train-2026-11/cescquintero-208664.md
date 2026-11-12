# Servidores: ¿Mascotas o Ganado?

Si llevas un tiempo en el mundo de la infraestructura, seguramente has escuchado esta analogía. Puede sonar un poco cruda la primera vez, pero resume con mucha precisión uno de los cambios de mentalidad más importantes de la última década en operaciones y DevOps. Vamos a desmenuzarla, ver de dónde viene, qué implica en la práctica y por qué no siempre es tan blanco o negro como parece.

## El origen de la metáfora

La idea suele atribuirse a Bill Baker, que la usaba al hablar de escalar SQL Server, y fue popularizada después por Randy Bias en el contexto de la nube y OpenStack. La premisa es sencilla:

- **Mascotas (pets):** servidores únicos, con nombre propio, cuidados a mano. Cuando enferman, los llevas al veterinario. Haces todo lo posible por salvarlos.
- **Ganado (cattle):** servidores idénticos, numerados, intercambiables. Cuando uno enferma, lo sacas del rebaño y lo reemplazas por otro.

Dicho así parece cruel, pero hablamos de máquinas, no de animales. Lo que la metáfora pone sobre la mesa es una pregunta clave: **¿tu sistema depende de que una máquina concreta siga viva?**

## Cómo reconocer una mascota

Seguro que conoces alguno. Quizá incluso tienes uno ahora mismo en producción:

- Se llama `zeus`, `gandalf` o `servidor-de-juan`.
- Nadie sabe exactamente qué tiene instalado, pero "funciona, no lo toques".
- Se configuró a mano hace años, conectándose por SSH y ejecutando comandos que nadie documentó.
- Tiene un uptime de 1.400 días y todos tienen miedo de reiniciarlo.
- Si se cae, alguien recibe una llamada a las 3 de la madrugada y pasa horas reviviéndolo.

El problema no es que el servidor sea valioso. El problema es que **es irremplazable**. Su estado vive dentro de él: configuración, parches aplicados a mano, archivos temporales que alguien acabó usando como base de datos… Es lo que se conoce como *configuration drift*: con el tiempo, cada mascota se vuelve un copo de nieve distinto a todos los demás.

## Cómo es el ganado

En el modelo de ganado, los servidores son desechables por diseño:

- Se llaman `web-01`, `web-02`, `web-03`… o directamente `i-0a1b2c3d4e5f`.
- Se crean a partir de una imagen o una definición declarativa (Terraform, Ansible, Packer, un Dockerfile, un manifiesto de Kubernetes).
- No se modifican en caliente: si necesitas un cambio, construyes una nueva versión y reemplazas las instancias antiguas.
- Si uno falla, un health check lo detecta y el orquestador o el grupo de autoescalado levanta otro.
- Nadie se entera, o como mucho aparece una línea en un dashboard.

Este enfoque se apoya en varias prácticas que hoy damos casi por sentadas:

1. **Infraestructura como código.** Si la infraestructura está definida en un repositorio, se puede reproducir, revisar en un pull request y versionar.
2. **Infraestructura inmutable.** En lugar de parchear servidores en marcha, se reemplazan. Esto elimina el drift de raíz.
3. **Estado fuera del servidor.** Los datos viven en bases de datos gestionadas, almacenamiento de objetos o volúmenes persistentes. La instancia de cómputo no guarda nada que no se pueda perder.
4. **Observabilidad y automatización.** Los logs se envían a un sistema centralizado y las métricas permiten detectar fallos sin entrar a la máquina.

## Un ejemplo concreto

Imagina que tienes que actualizar la versión de Node.js de tu aplicación.

**Con mascotas:** te conectas a cada servidor, ejecutas el gestor de paquetes, reinicias el servicio, cruzas los dedos y, si algo va mal en el tercer servidor, ahora tienes una flota con versiones mezcladas y un rollback manual por delante.

**Con ganado:** cambias una línea en tu `Dockerfile` (por ejemplo, `FROM node:22` a `FROM node:24`), el pipeline de CI construye una nueva imagen, y el despliegue va sustituyendo contenedores de forma gradual. Si las métricas empeoran, el rollback consiste en volver a la imagen anterior. Mismo resultado en todos los nodos, siempre.

## Entonces, ¿las mascotas son malas?

No necesariamente. Aquí es donde conviene matizar.

Hay sistemas que, por naturaleza, tienen estado y son difíciles de tratar como ganado: bases de datos primarias, ciertos sistemas legados, hardware especializado o equipos en entornos con restricciones físicas. Incluso en la nube, tu clúster de PostgreSQL tiene algo de mascota, aunque esté gestionado por un servicio.

La clave no es eliminar todas las mascotas, sino:

- **Reducir su número al mínimo** y saber exactamente cuáles son.
- **Protegerlas bien:** backups probados (un backup que nunca has restaurado no es un backup), réplicas, monitorización y runbooks claros.
- **Empujar el estado hacia ellas** para que todo lo demás pueda ser ganado.

Además, el ganado tiene sus costes. Requiere inversión inicial en automatización, pipelines, imágenes y herramientas de orquestación. Para un proyecto personal con un único VPS, montar un clúster de Kubernetes probablemente sea matar moscas a cañonazos. Aun así, incluso en ese caso, tener un script o un archivo de Ansible que reconstruya tu servidor desde cero te ahorrará más de un disgusto.

## Más allá del ganado

La metáfora ha seguido evolucionando. Con serverless y las funciones como servicio, hay quien habla de **"insectos"**: unidades de cómputo tan efímeras que viven milisegundos y ni siquiera las ves. Otros mencionan los **"pollos"** para referirse a los contenedores: más pequeños y numerosos que el ganado tradicional. Más allá del zoológico, la tendencia es clara: cuanto menos te importe una instancia concreta, más resiliente y escalable será tu sistema.

## Una prueba rápida

Hazte estas preguntas sobre tu infraestructura actual:

- Si borro este servidor ahora mismo, ¿cuánto tardo en tener otro idéntico funcionando?
- ¿Podría hacerlo alguien del equipo que no sea yo?
- ¿Está su configuración en un repositorio o solo en la cabeza de alguien?
- ¿Me da miedo reiniciarlo?

Si las respuestas te incomodan, ya sabes dónde tienes una mascota.

## Conclusión

Tratar los servidores como ganado no va de frialdad, sino de **reproducibilidad, resiliencia y tranquilidad**. Significa que un fallo de hardware es un evento rutinario y no una crisis. Significa poder escalar sin miedo y desplegar varias veces al día. Y, sobre todo, significa dormir mejor.

Guarda tu cariño para tus mascotas de verdad. A los servidores, dales un número y un buen pipeline.

---

*¿Y tú? ¿Tienes alguna mascota en producción que nadie se atreve a tocar? Cuéntamelo en los comentarios.* 🐄
