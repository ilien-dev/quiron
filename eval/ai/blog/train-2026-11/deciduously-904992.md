# Oops, I Did It Again...I Made A Rust Web API And It Was Not That Difficult

I have a confession: I keep doing this. Every few months I tell myself Rust is "for systems people," the kind of folks who write databases and argue about cache lines. Then a weekend comes, I open a terminal, type `cargo new`, and a few hours later I have a working web API.

This is my second time, and I want to say the thing I wish someone had told me before the first one: **building a web API in Rust is not that difficult.** It isn't effortless, and the compiler will absolutely humble you. But "humbled" and "difficult" are different, and once you see the shape of it, most of the work feels like any other backend framework.

Let's build a small one together. It's a reading list API where you can add books, list them, mark them as read, and delete them. No database yet, just enough to see how the pieces fit.

## The Stack

We're using:

- **[Axum](https://github.com/tokio-rs/axum)**, a web framework from the Tokio team. It's ergonomic, modular, and doesn't hide much magic.
- **Tokio**, the async runtime that actually runs our code.
- **Serde** to turn Rust structs into JSON and back.
- **uuid** for IDs, because auto-incrementing integers in a `HashMap` is a story for another day.

Start a project:

```bash
cargo new reading-list
cd reading-list
```

Then add dependencies to `Cargo.toml`:

```toml
[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
uuid = { version = "1", features = ["v4", "serde"] }
```

That's the entire dependency list.

## Step 1: Describe Your Data

In Rust, you start by telling the compiler what your data looks like. This is the part that felt like busywork the first time and felt like a superpower the second time.

```rust
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone, Serialize)]
struct Book {
    id: Uuid,
    title: String,
    author: String,
    read: bool,
}

#[derive(Deserialize)]
struct NewBook {
    title: String,
    author: String,
}
```

Two structs: `Book` is what we store and return, and `NewBook` is what a client sends when creating one. Notice that the client can't send an `id` or a `read` flag. That isn't validation code I wrote. The type simply doesn't have those fields, so they can't sneak in.

The `#[derive(Serialize)]` and `#[derive(Deserialize)]` attributes are Serde doing the heavy lifting. You never write JSON parsing by hand.

## Step 2: Shared State

Our "database" is a `HashMap` living in memory. Since a web server handles many requests at once, potentially on several threads, we need to share it safely:

```rust
use std::{
    collections::HashMap,
    sync::{Arc, RwLock},
};

type Db = Arc<RwLock<HashMap<Uuid, Book>>>;
```

Read that type from the inside out:

- `HashMap<Uuid, Book>` is our storage.
- `RwLock<...>` allows many readers *or* one writer at a time.
- `Arc<...>` is an atomically reference-counted pointer, so multiple handlers can hold a reference to the same map.

This is the moment where Rust newcomers usually panic, and I did too. But this pattern is nearly universal for simple shared state. You write it once, give it a type alias, and stop thinking about it. The payoff is that **data races are a compile error**. If you forget the lock, your code won't build. In other languages, you find that bug in production at 2 a.m.

## Step 3: Handlers

A handler in Axum is just an async function. Its arguments are "extractors" that pull data out of the request, and its return type is anything that can become a response.

Listing books:

```rust
use axum::{extract::State, Json};

async fn list_books(State(db): State<Db>) -> Json<Vec<Book>> {
    let books = db.read().unwrap().values().cloned().collect();
    Json(books)
}
```

`State(db)` extracts our shared map. We take a read lock, clone the books into a `Vec`, and wrap it in `Json`, which handles serialization and sets the `Content-Type` header for us.

Creating a book:

```rust
use axum::http::StatusCode;

async fn create_book(
    State(db): State<Db>,
    Json(input): Json<NewBook>,
) -> (StatusCode, Json<Book>) {
    let book = Book {
        id: Uuid::new_v4(),
        title: input.title,
        author: input.author,
        read: false,
    };

    db.write().unwrap().insert(book.id, book.clone());
    (StatusCode::CREATED, Json(book))
}
```

This is my favorite part of Axum. `Json(input): Json<NewBook>` means "parse the request body as a `NewBook`." If the body is malformed or missing a field, Axum rejects the request with an error status before your function runs. You get a fully typed, guaranteed-valid `NewBook` or you don't get called at all.

Returning a tuple of `(StatusCode, Json<Book>)` gives us a `201 Created` with the new book as the body.

## Step 4: Errors That Don't Hurt

Fetching a single book introduces a real question: what if the ID doesn't exist? Rust doesn't have exceptions, so we model failure explicitly with `Result`. To make our own error type work as an HTTP response, we implement `IntoResponse`:

```rust
use axum::response::{IntoResponse, Response};

enum ApiError {
    NotFound,
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        match self {
            ApiError::NotFound => (StatusCode::NOT_FOUND, "book not found").into_response(),
        }
    }
}
```

Now handlers can return `Result<T, ApiError>`, and Axum turns either branch into a proper response:

```rust
use axum::extract::Path;

async fn get_book(
    State(db): State<Db>,
    Path(id): Path<Uuid>,
) -> Result<Json<Book>, ApiError> {
    db.read()
        .unwrap()
        .get(&id)
        .cloned()
        .map(Json)
        .ok_or(ApiError::NotFound)
}
```

`Path(id): Path<Uuid>` parses the URL segment as a UUID. Send garbage like `/books/banana` and Axum returns a `400` for you.

Marking as read and deleting follow the same pattern:

```rust
async fn mark_read(
    State(db): State<Db>,
    Path(id): Path<Uuid>,
) -> Result<Json<Book>, ApiError> {
    let mut books = db.write().unwrap();
    let book = books.get_mut(&id).ok_or(ApiError::NotFound)?;
    book.read = true;
    Ok(Json(book.clone()))
}

async fn delete_book(
    State(db): State<Db>,
    Path(id): Path<Uuid>,
) -> Result<StatusCode, ApiError> {
    db.write()
        .unwrap()
        .remove(&id)
        .map(|_| StatusCode::NO_CONTENT)
        .ok_or(ApiError::NotFound)
}
```

That little `?` in `mark_read` is doing a lot: if the book isn't found, it returns `ApiError::NotFound` early. It's the cleanest error propagation I've used in any language, and as your API grows you just add variants to `ApiError`, like `BadRequest` or `Database(sqlx::Error)`, and match on them in one place.

## Step 5: Wire It Up

Finally, the router and the server:

```rust
use axum::{routing::get, Router};

#[tokio::main]
async fn main() {
    let db: Db = Arc::new(RwLock::new(HashMap::new()));

    let app = Router::new()
        .route("/books", get(list_books).post(create_book))
        .route(
            "/books/{id}",
            get(get_book).patch(mark_read).delete(delete_book),
        )
        .with_state(db);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("listening on http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}
```

Routes read almost like a spec: `/books` handles `GET` and `POST`, while `/books/{id}` handles `GET`, `PATCH`, and `DELETE`. `.with_state(db)` hands our shared map to every handler that asks for it.

Run it:

```bash
cargo run
```

## Try It Out

```bash
# Create a book
curl -X POST localhost:3000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "The Left Hand of Darkness", "author": "Ursula K. Le Guin"}'

# List all books
curl localhost:3000/books

# Mark one as read (use the id from the create response)
curl -X PATCH localhost:3000/books/<id>

# Delete it
curl -X DELETE localhost:3000/books/<id>
```

And just like that, you have a working, type-safe, concurrent REST API in roughly 100 lines.

## So Why Was It "Not That Difficult"?

Looking back, the hard parts of Rust mostly *didn't show up*. Here's why:

**Axum leans on the type system instead of fighting it.** Extractors, `Json`, `Path`, and `IntoResponse` mean the framework uses types to do the parsing, validating, and response-building. You describe what you want, and the plumbing appears.

**Ownership mostly stayed out of the way.** In a request/response API, data flows in, gets processed, and flows out. There are very few long-lived references to juggle. The one place shared ownership matters, the state, is handled by a single `Arc<RwLock<...>>` you write once.

**The compiler is a pair programmer, not a gatekeeper.** Yes, I hit errors. Forgot a `.clone()`, mismatched a return type, forgot to derive `Clone`. But every error message told me exactly what was wrong and usually how to fix it. Compare that to a runtime `undefined is not a function` in a request handler nobody tested.

**When it compiles, it tends to work.** This is the cliché everyone repeats, and it's a cliché because it's true. I ran every curl command above on the first try after the build succeeded.

## Where to Go Next

This is a toy, but the jump to something real is smaller than you'd think:

- Swap the `HashMap` for **SQLx** with Postgres or SQLite. Your handlers barely change; they just `await` a query instead of taking a lock.
- Add **tower-http** for logging, CORS, and timeouts as middleware layers.
- Use **validator** or custom checks to reject empty titles.
- Write integration tests by calling your `Router` directly with `tower::ServiceExt::oneshot`, with no server needed.

If you've been putting off Rust for web work because it seems intimidating, give it one weekend. Worst case, you learn a few things about types and concurrency that make you better in every other language.

Best case? You'll be writing a post like this one, admitting you did it again.

---

*Have you built a web API in Rust? What tripped you up, or what surprised you? Let me know in the comments!*
