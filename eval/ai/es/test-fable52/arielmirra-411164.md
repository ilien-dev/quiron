Si alguna vez has escrito una consulta SQL con cinco `JOIN` encadenados para responder a algo tan simple como «¿qué amigos de mis amigos viven en Madrid?», ya conoces el problema que las bases de datos orientadas a grafos vienen a resolver. En este post vemos qué son, cómo funcionan y, sobre todo, cuándo merece la pena usarlas y cuándo no.

## Qué es una base de datos de grafos

Una base de datos orientada a grafos almacena la información como una red: **nodos** conectados por **relaciones**. En lugar de tablas, filas y claves foráneas, el modelo se parece mucho a lo que dibujarías en una pizarra para explicar tu dominio.

El modelo más extendido es el *grafo de propiedades* (property graph), que tiene tres piezas:

- **Nodos**: las entidades, como una persona, un producto o una cuenta bancaria. Suelen llevar etiquetas (`Persona`, `Producto`) que indican su tipo.
- **Relaciones**: las conexiones entre nodos. Tienen dirección y tipo (`SIGUE_A`, `COMPRÓ`, `TRABAJA_EN`).
- **Propiedades**: pares clave-valor que pueden vivir tanto en los nodos como en las relaciones. Una relación `COMPRÓ` puede guardar la fecha y el importe.

La idea clave es que **las relaciones son ciudadanos de primera clase**. No se calculan en tiempo de consulta cruzando claves, sino que se almacenan como parte de los datos.

Existe otro modelo, RDF, basado en tripletas sujeto-predicado-objeto y consultado con SPARQL, muy usado en web semántica. Aquí nos centramos en el grafo de propiedades, que es el que encontrarás en la mayoría de aplicaciones.

## En qué se diferencia de una base de datos relacional

En una base relacional, las conexiones entre entidades se resuelven con `JOIN`. Cada salto implica buscar en un índice y, en relaciones muchos a muchos, pasar por una tabla intermedia. Con uno o dos saltos funciona de maravilla. Con seis, la consulta se vuelve difícil de leer y su coste crece con el tamaño de las tablas.

Las bases de datos de grafos nativas usan lo que se conoce como *adyacencia sin índices*: cada nodo guarda referencias directas a sus vecinos. Recorrer una relación es seguir un puntero, así que el coste depende de la parte del grafo que visitas, no del volumen total de datos. Preguntar por los amigos de los amigos de alguien cuesta casi lo mismo con mil usuarios que con cien millones.

La otra diferencia es la flexibilidad del esquema. Añadir un tipo nuevo de relación no exige migraciones ni tablas adicionales: simplemente empiezas a crearla.

## Un ejemplo con Cypher

Cypher es el lenguaje de consulta de Neo4j y la principal inspiración de GQL, el estándar ISO para grafos publicado en 2024. Su sintaxis dibuja el patrón que buscas: paréntesis para los nodos y flechas para las relaciones.

Creamos algunos datos:

```cypher
CREATE (ana:Persona {nombre: 'Ana', ciudad: 'Sevilla'})
CREATE (luis:Persona {nombre: 'Luis', ciudad: 'Bilbao'})
CREATE (marta:Persona {nombre: 'Marta', ciudad: 'Madrid'})
CREATE (ana)-[:AMIGO_DE {desde: 2019}]->(luis)
CREATE (luis)-[:AMIGO_DE {desde: 2021}]->(marta)
```

Y ahora la pregunta del principio, los amigos de los amigos de Ana que viven en Madrid:

```cypher
MATCH (ana:Persona {nombre: 'Ana'})-[:AMIGO_DE*2]-(fof:Persona)
WHERE fof.ciudad = 'Madrid'
RETURN DISTINCT fof.nombre
```

El `*2` indica dos saltos. Si mañana quieres llegar hasta tres niveles, lo cambias por `*1..3` y listo. El equivalente en SQL supondría añadir más `JOIN` o recurrir a una CTE recursiva.

## Para qué se usan

Los grafos brillan cuando el valor está en las conexiones más que en los registros aislados. Estos son los casos de uso más habituales:

**Redes sociales y recomendaciones.** «Gente que quizá conozcas» o «quienes compraron esto también compraron aquello» son, literalmente, recorridos de un grafo.

**Detección de fraude.** Los defraudadores rara vez actúan solos: comparten teléfonos, direcciones, dispositivos o cuentas. En tablas, esos anillos son casi invisibles; en un grafo aparecen como ciclos y grupos densamente conectados.

**Grafos de conocimiento e IA.** Conectar entidades, documentos y conceptos permite a buscadores y asistentes responder con contexto. Técnicas como GraphRAG combinan la búsqueda vectorial con recorridos del grafo para recuperar información relacionada, no solo textos parecidos.

**Redes e infraestructura.** Dependencias entre servicios, topologías de red y análisis de impacto: «si cae este servidor, ¿qué deja de funcionar?».

**Control de acceso.** Usuarios, grupos, roles y recursos con permisos heredados forman jerarquías que se consultan de forma natural como caminos.

**Logística.** Rutas más cortas, cadenas de suministro y trazabilidad de productos.

## Cuándo no usarlas

No son la respuesta a todo. Conviene evitarlas, o al menos pensárselo, en estos casos:

- **Datos tabulares con pocas relaciones.** Facturas, inventarios o formularios encajan mejor en una base relacional.
- **Analítica masiva.** Si necesitas sumar o promediar millones de registros, un motor columnar lo hará mucho mejor.
- **Acceso simple por clave.** Para sesiones o cachés basta con un almacén clave-valor.

También tienen sus propios retos. Los *supernodos*, nodos con millones de relaciones, pueden degradar los recorridos. Repartir un grafo entre varias máquinas es difícil, porque cualquier corte separa nodos que están conectados. Y el ecosistema de herramientas y perfiles con experiencia es más pequeño que el del mundo SQL.

## Qué opciones hay

- **Neo4j**: la más popular, con edición comunitaria y servicio gestionado (Aura).
- **Memgraph**: en memoria, compatible con Cypher y orientada a tiempo real.
- **Amazon Neptune**: servicio gestionado en AWS que admite Gremlin, openCypher y SPARQL.
- **ArangoDB**: multimodelo, combina documentos y grafos.
- **Apache AGE**: extensión que añade consultas Cypher a PostgreSQL, ideal para probar sin cambiar de base de datos.

Además, el estándar SQL:2023 incorpora SQL/PGQ, que permite consultar grafos de propiedades definidos sobre tablas relacionales, así que la frontera entre ambos mundos es cada vez más difusa.

## Conclusión

Una base de datos de grafos no sustituye a tu base relacional: la complementa. La pregunta útil no es «¿cuál es mejor?», sino «¿mis consultas tratan sobre los datos o sobre cómo se conectan?». Si tu problema se explica dibujando círculos y flechas, y tus consultas encadenan saltos de profundidad variable, probablemente tengas un grafo entre manos.

¿Has usado alguna en producción? Cuéntame tu experiencia en los comentarios.
