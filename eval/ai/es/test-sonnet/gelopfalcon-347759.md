# "Gateando" con GraphQL - Lo básico

GraphQL lleva ya varios años posicionándose como una alternativa seria a REST para construir APIs, pero para quienes recién empiezan puede resultar un poco abrumador entender qué problema resuelve realmente y por qué tanta gente lo prefiere. En este post vamos a dar los primeros pasos, sin asumir conocimiento previo.

## ¿Qué problema resuelve GraphQL?

En una API REST tradicional, cada recurso tiene su propio endpoint: `/usuarios`, `/usuarios/1`, `/usuarios/1/posts`, etc. Esto tiene dos problemas comunes:

- **Over-fetching**: el servidor devuelve más datos de los que realmente necesitamos. Si solo queremos el nombre de un usuario, pero el endpoint devuelve todos sus campos, estamos transfiriendo información innecesaria.
- **Under-fetching**: necesitamos hacer varias peticiones a distintos endpoints para reunir toda la información que necesita una sola pantalla (por ejemplo, el usuario, sus posts y los comentarios de cada post).

GraphQL resuelve ambos problemas dejando que sea el cliente quien decida exactamente qué campos necesita, en una sola petición.

## Un esquema, un solo endpoint

A diferencia de REST, en GraphQL normalmente hay un único endpoint (por ejemplo `/graphql`), y todas las peticiones se hacen contra él usando el método POST. Lo que cambia entre una petición y otra no es la URL, sino el contenido de la *query*.

## Tipos y esquema

Todo en GraphQL empieza por el **esquema**, que define qué tipos de datos existen y qué operaciones se pueden hacer sobre ellos. Un ejemplo sencillo:

```graphql
type Usuario {
  id: ID!
  nombre: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  titulo: String!
  contenido: String!
}

type Query {
  usuario(id: ID!): Usuario
  usuarios: [Usuario!]!
}
```

El signo de exclamación (`!`) indica que el campo es obligatorio (no puede ser `null`). Los corchetes (`[Post!]!`) indican una lista, en este caso una lista no nula de posts, donde cada post tampoco puede ser `null`.

## Haciendo una query

Una vez definido el esquema y su implementación en el servidor, el cliente puede pedir exactamente los campos que necesita:

```graphql
query {
  usuario(id: "1") {
    nombre
    posts {
      titulo
    }
  }
}
```

La respuesta tendrá exactamente esa forma:

```json
{
  "data": {
    "usuario": {
      "nombre": "Ana",
      "posts": [
        { "titulo": "Mi primer post" },
        { "titulo": "Aprendiendo GraphQL" }
      ]
    }
  }
}
```

Nótese que no pedimos el `email` del usuario ni el `contenido` de los posts, y el servidor no los devuelve. Esto es exactamente lo contrario del over-fetching que mencionábamos antes.

## Mutations: modificar datos

Para crear, actualizar o eliminar datos, GraphQL usa **mutations**, que se definen de forma similar a las queries pero bajo el tipo `Mutation`:

```graphql
type Mutation {
  crearUsuario(nombre: String!, email: String!): Usuario!
}
```

Y se ejecutan de forma parecida:

```graphql
mutation {
  crearUsuario(nombre: "Luis", email: "luis@ejemplo.com") {
    id
    nombre
  }
}
```

Una particularidad interesante es que, igual que en las queries, se puede especificar qué campos del resultado queremos recibir de vuelta, incluso en una operación de escritura.

## Resolvers

En el lado del servidor, cada campo del esquema necesita una función llamada **resolver**, que es la responsable de obtener el dato real (de una base de datos, otra API, un caché, etc.). Un ejemplo básico con Apollo Server:

```js
const resolvers = {
  Query: {
    usuario: (padre, args) => {
      return db.usuarios.find(u => u.id === args.id);
    },
    usuarios: () => db.usuarios
  },
  Usuario: {
    posts: (usuario) => {
      return db.posts.filter(p => p.usuarioId === usuario.id);
    }
  }
};
```

Es importante notar que también se pueden definir resolvers para campos anidados dentro de un tipo, como `posts` dentro de `Usuario`. Esto le da a GraphQL su flexibilidad característica: no importa cuán anidada esté la información solicitada, cada campo sabe cómo resolverse a sí mismo.

## Un servidor mínimo

Con Apollo Server, poner en marcha un servidor GraphQL básico es cuestión de pocas líneas:

```js
const { ApolloServer, gql } = require('apollo-server');

const typeDefs = gql`
  type Query {
    saludo: String
  }
`;

const resolvers = {
  Query: {
    saludo: () => '¡Hola desde GraphQL!'
  }
};

const server = new ApolloServer({ typeDefs, resolvers });

server.listen().then(({ url }) => {
  console.log(`Servidor listo en ${url}`);
});
```

## ¿REST o GraphQL?

No se trata de que uno sea estrictamente mejor que el otro. REST sigue siendo perfectamente válido para APIs simples, con recursos bien delimitados y necesidades de consulta predecibles. GraphQL brilla especialmente cuando el cliente necesita mucha flexibilidad sobre qué datos pedir (por ejemplo, en aplicaciones con múltiples pantallas que consumen los mismos datos de formas distintas), o cuando queremos reducir el número de peticiones necesarias para construir una vista compleja.

## Conclusión

Esto ha sido apenas un vistazo introductorio a GraphQL: queries, mutations, esquemas y resolvers son los cuatro pilares sobre los que se construye todo lo demás (suscripciones en tiempo real, fragmentos, directivas, paginación con cursores...). Si nunca has trabajado con GraphQL, te animo a montar un servidor mínimo como el del último ejemplo y empezar a experimentar desde ahí: es la mejor forma de perder el miedo inicial y entender por qué tantos equipos lo están adoptando.
