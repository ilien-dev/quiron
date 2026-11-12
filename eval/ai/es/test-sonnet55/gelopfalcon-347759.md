Antes de caminar, todos gateamos. Con GraphQL pasa igual: no hace falta dominar federación, subscriptions ni caché avanzado para sacarle provecho. En este post vemos lo básico, sin humo, para que des tus primeros pasos si vienes de REST.

## ¿Qué es GraphQL?

GraphQL es un lenguaje de consulta para APIs y un runtime que las ejecuta contra tus datos. Lo creó Facebook en 2012 y lo liberó en 2015. Su idea central es simple: **el cliente pide exactamente lo que necesita, ni más ni menos.**

En REST sueles tener muchos endpoints (`/users/1`, `/users/1/posts`...). En GraphQL hay un único endpoint, normalmente `/graphql`, y la forma de la respuesta la defines tú con la consulta.

## El problema que resuelve

REST suele darnos dos dolores de cabeza:

- **Over-fetching:** el endpoint devuelve 30 campos y tú solo necesitas 2.
- **Under-fetching:** un endpoint no basta y encadenas varias peticiones.

GraphQL ataca ambos: una petición, los campos justos.

## El esquema: tu contrato

Todo empieza con el *schema*, una descripción tipada de tu API:

```graphql
type User {
  id: ID!
  name: String!
  email: String
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  author: User!
}

type Query {
  user(id: ID!): User
  posts: [Post!]!
}
```

El `!` significa "no nulo". Así, `[Post!]!` es una lista no nula de posts no nulos. Los escalares básicos son `Int`, `Float`, `String`, `Boolean` e `ID`.

## Queries: leer datos

Para pedir datos escribes una *query*:

```graphql
query {
  user(id: "1") {
    name
    posts {
      title
    }
  }
}
```

Y la respuesta tiene la misma forma que la consulta:

```json
{
  "data": {
    "user": {
      "name": "Ana",
      "posts": [{ "title": "Hola GraphQL" }]
    }
  }
}
```

Si mañana necesitas también el `email`, solo lo añades a la consulta. No hay que tocar el backend ni crear otro endpoint.

### Variables

No concatenes valores dentro del texto de la consulta. Usa variables:

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    name
  }
}
```

Envías `{ "id": "1" }` aparte, y el servidor se encarga de validarlo según el tipo.

## Mutations: modificar datos

Para crear, actualizar o borrar se usan *mutations*. Se definen en el schema igual que las queries:

```graphql
type Mutation {
  createPost(title: String!, authorId: ID!): Post!
}
```

Y se llaman así:

```graphql
mutation {
  createPost(title: "Mi primer post", authorId: "1") {
    id
    title
  }
}
```

Fíjate en que también eliges qué campos quieres recibir de vuelta.

## Resolvers: de dónde salen los datos

El schema describe *qué* se puede pedir; los *resolvers* son funciones que dicen *cómo* obtenerlo. Un servidor mínimo con Apollo Server:

```js
import { ApolloServer } from "@apollo/server";
import { startStandaloneServer } from "@apollo/server/standalone";

const users = [{ id: "1", name: "Ana", email: "ana@example.com" }];

const typeDefs = `#graphql
  type User { id: ID!, name: String!, email: String }
  type Query { user(id: ID!): User }
`;

const resolvers = {
  Query: {
    user: (_, { id }) => users.find((u) => u.id === id),
  },
};

const server = new ApolloServer({ typeDefs, resolvers });
const { url } = await startStandaloneServer(server, { listen: { port: 4000 } });
console.log(`Servidor listo en ${url}`);
```

Cada campo del schema puede tener su resolver. Si no defines uno, GraphQL usa por defecto la propiedad con el mismo nombre del objeto padre.

## Probándolo

Al abrir `http://localhost:4000` Apollo te ofrece un explorador donde puedes escribir consultas, ver el schema y consultar la documentación generada automáticamente. Esa introspección es una de las mejores cosas de GraphQL: la API se documenta sola.

## Cuándo sí y cuándo no

**Sí:**
- Clientes diversos (web, móvil) con necesidades de datos distintas.
- Datos muy relacionados entre sí.
- Equipos de frontend que quieren iterar sin esperar nuevos endpoints.

**Quizá no:**
- APIs muy simples o con pocos recursos.
- Subida de archivos o streaming como caso principal.
- Cuando el caché HTTP sencillo de REST te resuelve todo.

Ojo también con el problema de las consultas N+1 en los resolvers; herramientas como DataLoader existen para eso, pero es tema de otro post.

## Conclusión

Ya sabes lo esencial: un **schema** tipado, **queries** para leer, **mutations** para escribir y **resolvers** que conectan todo con tus datos. Con eso puedes montar tu primera API y empezar a experimentar.

Gatear es el primer paso. Cuando te sientas cómodo, vendrán la paginación, la autenticación, los fragments y las subscriptions. ¿Y tú, ya probaste GraphQL o sigues fiel a REST? Cuéntame en los comentarios.
