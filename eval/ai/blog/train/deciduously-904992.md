# Oops, I Did It Again... I Made a Rust Web API and It Was Not That Difficult

Every so often, I get the urge to build something in Rust. And every time, some part of my brain whispers: *Are you sure? Remember the borrow checker? Remember lifetimes?*

And every time, I do it anyway. And every time, it turns out to be a lot less painful than I feared.

This time, I built a small JSON web API for managing a todo list. Nothing fancy, just enough to have real routes, shared state, request parsing, and error handling. I want to walk through it, because if you've been intimidated by the idea of writing a web backend in Rust, I think you'll be pleasantly surprised.

## The stack

The Rust web ecosystem has matured a lot. There are several solid frameworks, including Actix Web, Rocket, Warp, and Axum. For this project, I went with **Axum**, for a few reasons:

- It's built by the Tokio team, so it plays nicely with the async runtime most of the ecosystem uses.
- It has very little macro magic. Handlers are just async functions.
- Its extractor pattern makes request parsing feel clean.

Here's the full dependency list:

```toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
uuid = { version = "1", features = ["v4", "serde"] }
```

That's it. No ORM, no database yet. We'll keep everything in memory to focus on the web parts.

## Hello, world

Let's start with the smallest thing that works:

```rust
use axum::{routing::get, Router};

#[tokio::main]
async fn main() {
    let app = Router::new().route("/", get(|| async { "Hello, world!" }));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

Run `cargo run`, hit `localhost:3000`, and you get a greeting. No lifetimes. No `Box<dyn Something>`. Just a router and a closure.

## Modeling the data

Our todo items need an ID, a title, and a completed flag:

```rust
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize)]
struct Todo {
    id: Uuid,
    title: String,
    completed: bool,
}

#[derive(Debug, Deserialize)]
struct CreateTodo {
    title: String,
}

#[derive(Debug, Deserialize)]
struct UpdateTodo {
    title: Option<String>,
    completed: Option<bool>,
}
```

Serde handles all the JSON conversion through those derive macros. `CreateTodo` is what we accept when creating an item, and `UpdateTodo` uses `Option` fields so clients can update just the parts they care about.

## Shared state

Here's where I expected the pain to start. A web server handles requests concurrently, so any shared data needs to be safe to access from multiple tasks. In a lot of languages, you'd just use a global variable and hope for the best. Rust won't let you do that, and honestly, that's a good thing.

The standard pattern is `Arc<RwLock<T>>`:

- `Arc` (atomic reference counting) lets multiple handlers share ownership of the same data.
- `RwLock` lets many readers or one writer access it at a time.

```rust
use std::{collections::HashMap, sync::Arc};
use tokio::sync::RwLock;

type Db = Arc<RwLock<HashMap<Uuid, Todo>>>;
```

Then we hand it to the router:

```rust
let db: Db = Arc::new(RwLock::new(HashMap::new()));

let app = Router::new()
    .route("/todos", get(list_todos).post(create_todo))
    .route("/todos/:id", get(get_todo).patch(update_todo).delete(delete_todo))
    .with_state(db);
```

That's the whole setup. Axum will clone the `Arc` for each request, which is cheap because it's just bumping a counter.

## Handlers

This is the part that really sold me on Axum. Handlers are async functions, and their arguments are *extractors*: types that know how to pull something out of the request.

### Listing todos

```rust
use axum::{extract::State, Json};

async fn list_todos(State(db): State<Db>) -> Json<Vec<Todo>> {
    let todos = db.read().await;
    Json(todos.values().cloned().collect())
}
```

`State(db)` pulls our shared state out. We take a read lock, clone the values into a `Vec`, and wrap it in `Json`, which serializes it and sets the right `Content-Type` header.

### Creating a todo

```rust
use axum::http::StatusCode;

async fn create_todo(
    State(db): State<Db>,
    Json(input): Json<CreateTodo>,
) -> (StatusCode, Json<Todo>) {
    let todo = Todo {
        id: Uuid::new_v4(),
        title: input.title,
        completed: false,
    };

    db.write().await.insert(todo.id, todo.clone());

    (StatusCode::CREATED, Json(todo))
}
```

`Json(input)` parses the request body into a `CreateTodo`. If the body is malformed or missing the `title` field, Axum automatically rejects the request with a 4xx error before our handler even runs. That's validation we get for free just by declaring the type.

Returning a tuple of `(StatusCode, Json<Todo>)` lets us set a `201 Created` status.

### Getting a single todo

```rust
use axum::extract::Path;

async fn get_todo(
    State(db): State<Db>,
    Path(id): Path<Uuid>,
) -> Result<Json<Todo>, StatusCode> {
    let todos = db.read().await;
    todos
        .get(&id)
        .cloned()
        .map(Json)
        .ok_or(StatusCode::NOT_FOUND)
}
```

`Path(id)` extracts the `:id` segment from the URL and parses it as a UUID. If it's not a valid UUID, the request is rejected automatically.

Returning a `Result` is where Rust's error handling shines. If the todo exists, we return `Ok(Json(todo))`. If not, we return `Err(StatusCode::NOT_FOUND)`. Axum knows how to turn both into responses.

### Updating a todo

```rust
async fn update_todo(
    State(db): State<Db>,
    Path(id): Path<Uuid>,
    Json(input): Json<UpdateTodo>,
) -> Result<Json<Todo>, StatusCode> {
    let mut todos = db.write().await;
    let todo = todos.get_mut(&id).ok_or(StatusCode::NOT_FOUND)?;

    if let Some(title) = input.title {
        todo.title = title;
    }
    if let Some(completed) = input.completed {
        todo.completed = completed;
    }

    Ok(Json(todo.clone()))
}
```

The `?` operator makes the not-found case a one-liner. Then we update only the fields that were provided.

### Deleting a todo

```rust
async fn delete_todo(
    State(db): State<Db>,
    Path(id): Path<Uuid>,
) -> StatusCode {
    if db.write().await.remove(&id).is_some() {
        StatusCode::NO_CONTENT
    } else {
        StatusCode::NOT_FOUND
    }
}
```

Short and sweet.

## Better errors

Returning bare status codes works, but real APIs usually want a JSON error body. Axum makes this easy with the `IntoResponse` trait:

```rust
use axum::response::{IntoResponse, Response};
use serde_json::json;

enum ApiError {
    NotFound,
    BadRequest(String),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, message) = match self {
            ApiError::NotFound => (StatusCode::NOT_FOUND, "Todo not found".to_string()),
            ApiError::BadRequest(msg) => (StatusCode::BAD_REQUEST, msg),
        };
        (status, Json(json!({ "error": message }))).into_response()
    }
}
```

Now handlers can return `Result<Json<Todo>, ApiError>`, and every error comes back as consistent JSON. Adding simple validation is easy too:

```rust
async fn create_todo(
    State(db): State<Db>,
    Json(input): Json<CreateTodo>,
) -> Result<(StatusCode, Json<Todo>), ApiError> {
    if input.title.trim().is_empty() {
        return Err(ApiError::BadRequest("Title cannot be empty".into()));
    }
    // ... same as before
}
```

## Trying it out

```bash
curl -X POST localhost:3000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Write a Rust API"}'

curl localhost:3000/todos

curl -X PATCH localhost:3000/todos/<id> \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

Everything works as expected, and the compiled binary starts instantly and uses a few megabytes of memory.

## So where was the hard part?

Honestly, it mostly wasn't there. Here's what I think made it smooth:

- **Axum hides the async plumbing.** I never had to name a future type or write a lifetime annotation.
- **Serde is excellent.** JSON serialization is basically free.
- **The compiler caught my mistakes early.** At one point I tried to hold a read lock while taking a write lock in the same handler. Well, actually, the compiler didn't catch that one, since it would have deadlocked at runtime, but it did catch several cases where I forgot to clone data out of a lock guard before returning it. Those errors pointed right at the problem.
- **Types doubled as validation.** Declaring `Path<Uuid>` and `Json<CreateTodo>` meant bad input never reached my code.

The places where I did slow down were mostly about learning Axum's specific patterns, like figuring out the order of extractors (the body extractor has to come last) and getting the error type to implement `IntoResponse`. Once I'd seen those patterns once, they stuck.

## What's next

An in-memory `HashMap` isn't going to cut it for anything real. The natural next steps are:

- Swapping the `HashMap` for **SQLx** with Postgres or SQLite, which gives you compile-time checked SQL queries.
- Adding **tower-http** middleware for logging, CORS, and request tracing.
- Writing integration tests using Axum's ability to call the router directly without spinning up a server.
- Adding authentication with JWTs or sessions.

Each of those is its own post, but none of them change the basic shape of what we built here.

## Wrapping up

If you've been avoiding Rust for web development because you've heard it's hard, I'd encourage you to give it another look. The language still has a learning curve, and you'll bump into the borrow checker eventually. But the modern web frameworks have done a lot of work to keep the common path simple.

I set out expecting a fight. What I got was about 150 lines of code, a fast binary, and a compiler that had my back the whole way. Oops, I did it again, and I'll probably do it again next time too.
