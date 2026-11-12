Cada vez que alguien descubre que su banco sigue funcionando sobre un mainframe, la reacción suele ser la misma: "¿En pleno 2026? ¿No se han enterado de que existe la nube?". Es una pregunta razonable, pero la respuesta tiene menos que ver con nostalgia o inercia y más con un resultado teórico que todo desarrollador backend debería conocer: el **Teorema CAP**.

## ¿Qué dice el Teorema CAP?

Formulado por Eric Brewer en el año 2000 y demostrado formalmente por Seth Gilbert y Nancy Lynch en 2002, el teorema establece que un sistema distribuido no puede garantizar simultáneamente estas tres propiedades:

- **Consistency (Consistencia):** todos los nodos ven los mismos datos al mismo tiempo. Una lectura siempre devuelve la escritura más reciente.
- **Availability (Disponibilidad):** toda petición recibe una respuesta, aunque algunos nodos hayan caído.
- **Partition tolerance (Tolerancia a particiones):** el sistema sigue funcionando aunque se pierdan mensajes entre nodos.

La versión popular dice "elige dos de tres", pero es engañosa. En un sistema distribuido real, **las particiones de red van a ocurrir**: cables que se cortan, switches que fallan, centros de datos que pierden conectividad. Por tanto, P no es opcional. La elección real es: **cuando hay una partición, ¿sacrificas consistencia o disponibilidad?**

- Los sistemas **CP** prefieren rechazar peticiones antes que devolver datos incorrectos.
- Los sistemas **AP** prefieren responder siempre, aunque la respuesta pueda estar desactualizada.

## El dilema del banco

Imagina una red social. Si das un "me gusta" y tu amigo en otro continente lo ve dos segundos más tarde, nadie sale perjudicado. Cassandra, DynamoDB y compañía brillan en este escenario: priorizan la disponibilidad y aceptan **consistencia eventual**.

Ahora imagina tu cuenta bancaria con 100 €. Durante una partición de red, dos nodos distintos aceptan cada uno una retirada de 100 €. Cuando la red se recupera, el sistema "converge"... y tienes -100 €. El banco ha perdido dinero, o peor, ha permitido un fraude.

Para un banco, la consistencia no es negociable. Un saldo incorrecto no es un bug molesto: es un problema regulatorio, legal y reputacional. Por eso la banca vive en el mundo **CP**, con transacciones ACID estrictas.

Pero aquí está la trampa: los bancos **tampoco pueden permitirse dejar de estar disponibles**. Un cajero que no responde o una pasarela de pagos caída durante el Black Friday cuesta millones. Necesitan consistencia fuerte *y* disponibilidad altísima.

¿Cómo se sale de ese callejón?

## El truco del mainframe: minimizar la P

El Teorema CAP habla de lo que ocurre **cuando hay una partición**. No dice nada sobre la frecuencia con la que ocurren. Y ahí es donde el mainframe juega su mejor carta.

En lugar de repartir el estado entre cientos de nodos baratos conectados por una red poco fiable, un mainframe como IBM Z concentra una enorme capacidad de cómputo en un sistema **fuertemente acoplado**:

- **Redundancia interna en todo:** procesadores de reserva, memoria con corrección de errores, fuentes de alimentación duplicadas. Muchos componentes pueden sustituirse en caliente sin detener el sistema.
- **Escalado vertical:** miles de transacciones por segundo en una sola máquina, sin necesidad de coordinar estado a través de una red.
- **Parallel Sysplex:** cuando hace falta más de una máquina, varias se agrupan mediante un *Coupling Facility*, un componente dedicado que gestiona bloqueos y cachés compartidas con latencias de microsegundos. DB2 en modo *data sharing* permite que varias instancias escriban sobre los mismos datos manteniendo consistencia fuerte.

El resultado es un sistema que es técnicamente CP, pero en el que las particiones son tan improbables que, en la práctica, la disponibilidad alcanza cifras de "cinco nueves" o más. No has vencido al Teorema CAP; simplemente has hecho que su peor caso casi nunca se active.

## ¿Y la recuperación ante desastres?

Ningún hardware sobrevive a un incendio en el centro de datos. Para eso existen soluciones como **GDPS**, que replican datos entre sitios. Y aquí CAP vuelve a aparecer con toda su crudeza:

- La **replicación síncrona** (por ejemplo, Metro Mirror) mantiene consistencia total, pero solo es viable a distancias limitadas, típicamente decenas de kilómetros, porque la latencia de la luz penaliza cada escritura.
- Para distancias mayores se usa **replicación asíncrona**, aceptando que en un desastre real podrían perderse unos segundos de transacciones.

Es exactamente la extensión que propone el modelo **PACELC**: incluso sin particiones (*Else*), hay que elegir entre latencia (*Latency*) y consistencia (*Consistency*).

## Seamos honestos: no es solo CAP

Sería injusto decir que el teorema explica todo. Los bancos también usan mainframes porque:

- Tienen décadas de lógica de negocio en COBOL, probada y auditada, que nadie quiere reescribir.
- Migrar un *core* bancario es uno de los proyectos de mayor riesgo que existen.
- Los reguladores valoran la estabilidad por encima de la modernidad.

Además, hoy existen bases de datos distribuidas con consistencia fuerte, como Google Spanner o CockroachDB, que usan consenso (Paxos, Raft) y relojes precisos para ofrecer garantías similares en arquitecturas horizontales. Algunos bancos nuevos ya las usan.

## Conclusión

El mainframe no es una reliquia: es una respuesta de ingeniería coherente a un problema concreto. Si no puedes renunciar a la consistencia y tampoco a la disponibilidad, la estrategia más pragmática es reducir al mínimo la probabilidad de particiones. Y eso, durante décadas, ha significado una sola cosa: una máquina enorme, redundante y fuertemente acoplada.

La próxima vez que veas un mainframe en una arquitectura bancaria, no pienses "legacy". Piensa "alguien leyó el Teorema CAP muy en serio".

---

*Nota:* he escrito "por qué" separado en el título, ya que en ese uso (equivalente a "por qué razón") es la forma correcta; "porqué" junto es un sustantivo ("el porqué de las cosas"). Si prefieres mantener el título original, cámbialo sin problema.
