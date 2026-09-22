# Qué son las bases de datos orientadas a grafos y para qué se usan

Durante décadas, las bases de datos relacionales han sido la opción por defecto para casi cualquier aplicación. Tablas, filas, columnas y claves foráneas: un modelo probado y muy bien entendido. Sin embargo, hay un tipo de problema en el que el modelo relacional empieza a sufrir: cuando lo más importante de tus datos no son los datos en sí, sino **las relaciones entre ellos**.

Ahí es donde entran las bases de datos orientadas a grafos.

## ¿Qué es un grafo?

Un grafo, en su definición más simple, es un conjunto de **nodos** (también llamados vértices) conectados por **aristas** (también llamadas relaciones). Si alguna vez has dibujado un mapa de amigos con círculos y flechas, ya has dibujado un grafo.

La mayoría de bases de datos de grafos siguen el modelo de **grafo de propiedades**, que tiene estos elementos:

- **Nodos**: representan entidades, como una persona, un producto o una ciudad.
- **Etiquetas**: clasifican los nodos (`Persona`, `Producto`, `Ciudad`).
- **Relaciones**: conectan dos nodos, tienen una dirección y un tipo (`SIGUE_A`, `COMPRÓ`, `VIVE_EN`).
- **Propiedades**: pares clave-valor que pueden estar tanto en los nodos como en las relaciones (`nombre: "Ana"`, `desde: 2019`).

Lo interesante es que las relaciones son ciudadanas de primera clase. No son una columna con un ID que apunta a otra tabla: son objetos almacenados físicamente que conectan directamente un nodo con otro.

## ¿Por qué no usar simplemente SQL?

Imagina que tienes una red social y quieres encontrar "los amigos de los amigos de los amigos de Ana". En una base de datos relacional tendrías algo así:

```sql
SELECT DISTINCT u4.nombre
FROM usuarios u1
JOIN amistades a1 ON u1.id = a1.usuario_id
JOIN usuarios u2 ON a1.amigo_id = u2.id
JOIN amistades a2 ON u2.id = a2.usuario_id
JOIN usuarios u3 ON a2.amigo_id = u3.id
JOIN amistades a3 ON u3.id = a3.usuario_id
JOIN usuarios u4 ON a3.amigo_id = u4.id
WHERE u1.nombre = 'Ana';
```

Funciona, pero cada nivel de profundidad añade más `JOIN`s, y cada `JOIN` implica buscar en índices. Con millones de usuarios y varios niveles de profundidad, el rendimiento se degrada rápidamente.

En una base de datos de grafos como Neo4j, la misma consulta en Cypher se ve así:

```cypher
MATCH (ana:Persona {nombre: 'Ana'})-[:AMIGO_DE*3]->(amigo)
RETURN DISTINCT amigo.nombre
```

Más allá de que sea más legible, la diferencia clave está en cómo se ejecuta. Las bases de datos de grafos nativas usan lo que se conoce como **adyacencia sin índices** (*index-free adjacency*): cada nodo guarda referencias directas a sus vecinos. Recorrer una relación es básicamente seguir un puntero, y el coste depende de la parte del grafo que recorres, no del tamaño total de la base de datos.

## Casos de uso habituales

Las bases de datos de grafos brillan en escenarios donde las conexiones son el centro del problema. Algunos ejemplos:

### Redes sociales

Es el ejemplo más obvio. Sugerencias de amistad, "personas que quizá conozcas", detección de comunidades o cálculo de grados de separación son consultas naturales sobre un grafo.

### Motores de recomendación

"Los usuarios que compraron este producto también compraron..." es, en el fondo, un recorrido por un grafo: del usuario a sus compras, de esas compras a otros usuarios que las hicieron y de ahí a los productos que compraron esos usuarios. Empresas de comercio electrónico y plataformas de contenido usan este enfoque para generar recomendaciones en tiempo real.

### Detección de fraude

Los defraudadores suelen crear redes de cuentas que comparten datos: el mismo teléfono, la misma dirección, la misma tarjeta o el mismo dispositivo. Vistas por separado, cada cuenta parece legítima. Vistas como un grafo, aparecen anillos de cuentas conectadas que resultan muy sospechosos. Bancos y aseguradoras usan bases de datos de grafos precisamente para detectar estos patrones.

### Grafos de conocimiento

Google usa un grafo de conocimiento para entender que "Madrid" es una ciudad, que es la capital de España y que tiene un equipo de fútbol llamado Real Madrid. Este tipo de estructuras permiten representar información semántica y hacer razonamientos sobre ella.

### Redes e infraestructura

En telecomunicaciones o en la gestión de infraestructura de TI, los elementos (servidores, routers, servicios) dependen unos de otros. Un grafo permite responder rápidamente preguntas como "si este servidor cae, ¿qué servicios se ven afectados?".

### Gestión de identidades y accesos

Usuarios que pertenecen a grupos, grupos que heredan permisos de otros grupos, recursos con reglas de acceso... Averiguar si un usuario tiene acceso a un recurso implica recorrer una jerarquía que encaja perfectamente en un grafo.

## Principales bases de datos de grafos

Algunas de las opciones más conocidas son:

- **Neo4j**: probablemente la más popular. Usa el lenguaje Cypher y tiene una comunidad muy grande.
- **Amazon Neptune**: servicio gestionado de AWS que soporta tanto grafos de propiedades (con Gremlin y openCypher) como RDF (con SPARQL).
- **ArangoDB**: base de datos multimodelo que combina documentos, clave-valor y grafos.
- **JanusGraph**: de código abierto, pensada para grafos muy grandes distribuidos sobre backends como Cassandra o HBase.
- **Memgraph**: orientada a análisis en memoria y en tiempo real, compatible con Cypher.

## ¿Cuándo no usar una base de datos de grafos?

Como toda tecnología, no es una bala de plata. Probablemente no la necesitas si:

- Tus datos son principalmente tabulares y las relaciones son simples.
- La mayoría de tus consultas son agregaciones sobre grandes volúmenes (sumas, medias, reportes), donde una base de datos relacional o columnar funciona mejor.
- Necesitas hacer muchas escrituras masivas de datos independientes entre sí.

Un buen criterio es preguntarte: ¿mis consultas más importantes consisten en recorrer relaciones de profundidad variable? Si la respuesta es sí, un grafo merece la pena.

## Conclusión

Las bases de datos orientadas a grafos no vienen a reemplazar a las relacionales, sino a cubrir un hueco en el que estas no son eficientes: datos muy conectados donde las relaciones importan tanto como las entidades. Redes sociales, recomendaciones, fraude o grafos de conocimiento son algunos de los terrenos donde han demostrado su valor.

Si nunca has trabajado con una, te recomiendo descargar Neo4j Desktop o probar su sandbox online y jugar un rato con Cypher. Es de esas tecnologías que, cuando la entiendes, empiezas a ver grafos en todas partes.
