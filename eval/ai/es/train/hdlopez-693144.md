# ¿Cómo Estructurar tu Aplicación en Go? Una Guía Práctica

Go es simple, pero la simplicidad puede ser engañosa. Cuando empiezas un proyecto en Go, surge una pregunta inevitable: ¿cómo organizo mi código? No hay un framework que te fuerce a una estructura específica. Eso es libertad, pero también responsabilidad.

## El problema

Sin una estructura clara, tu código se convierte en un desastre. Carpetas y paquetes en todos lados, importes circulares, código acoplado que es imposible de testear. He visto proyectos Go que empezaron bien pero se volvieron un caos porque nadie pensó en arquitectura desde el principio.

## Principios básicos de Go

Antes de hablar de estructura, recuerda los principios de Go:

**Simplicity:** Go favorece lo simple sobre lo complejo.

**Claridad:** El código debe ser fácil de entender.

**Packages:** Go organiza código en packages. Usa esto a tu favor.

**Interfaces:** Permiten desacoplamiento. Úsalas strategicamente.

## Una estructura que funciona

Aquí te propongo una estructura que funciona bien para la mayoría de proyectos:

```
myapp/
├── cmd/
│   └── myapp/
│       └── main.go
├── internal/
│   ├── handlers/
│   ├── models/
│   ├── service/
│   └── store/
├── pkg/
│   ├── logger/
│   └── utils/
├── go.mod
├── go.sum
└── README.md
```

### La carpeta `cmd/`

Aquí va tu punto de entrada. Cada ejecutable que produces tiene su propia carpeta dentro de `cmd/`.

```go
// cmd/myapp/main.go
package main

import (
	"log"
	"myapp/internal/handlers"
	"myapp/internal/service"
	"myapp/internal/store"
)

func main() {
	// Inicializar dependencias
	db := store.NewDB()
	svc := service.NewService(db)
	h := handlers.NewHandlers(svc)
	
	// Iniciar servidor
	h.Start()
}
```

Mantén `main.go` limpio. Su único trabajo es wiring inicial y bootstrapping.

### La carpeta `internal/`

Todo aquí es privado a tu aplicación. Nada fuera de tu proyecto puede importar desde `internal/`. Go lo enforce automáticamente.

**handlers/:** Lógica de HTTP, gRPC, CLI. Las capas más externas que reciben requests.

**models/:** Estructuras de datos que representan tu dominio. Usuario, Producto, etc.

**service/:** Lógica de negocio. Aquí es donde sucede el trabajo real. Los handlers delegan a services.

**store/:** Acceso a datos. Base de datos, caché, APIs externas. Cualquier cosa que persista o recupere datos.

Ejemplo:

```go
// internal/models/user.go
package models

type User struct {
	ID    int
	Name  string
	Email string
}
```

```go
// internal/store/user.go
package store

import "myapp/internal/models"

type UserStore interface {
	GetUser(id int) (*models.User, error)
	SaveUser(u *models.User) error
}

type DBUserStore struct {
	// conexión a DB
}

func (s *DBUserStore) GetUser(id int) (*models.User, error) {
	// implementación
}
```

```go
// internal/service/user.go
package service

import "myapp/internal/models"
import "myapp/internal/store"

type UserService struct {
	store store.UserStore
}

func (s *UserService) GetUserInfo(id int) (*models.User, error) {
	return s.store.GetUser(id)
}
```

```go
// internal/handlers/user.go
package handlers

import (
	"net/http"
	"myapp/internal/service"
)

type UserHandlers struct {
	service *service.UserService
}

func (h *UserHandlers) GetUser(w http.ResponseWriter, r *http.Request) {
	id := extractID(r)
	user, err := h.service.GetUserInfo(id)
	// escribir respuesta
}
```

### La carpeta `pkg/`

Código reutilizable que podría ser útil en otros proyectos. Logging, utilidades, helpers.

A diferencia de `internal/`, `pkg/` es público. Otros pueden importar desde aquí. Úsalo para código que tiene valor fuera de tu aplicación específica.

```go
// pkg/logger/logger.go
package logger

import "log"

type Logger interface {
	Info(msg string)
	Error(msg string)
}

type SimpleLogger struct{}

func (l *SimpleLogger) Info(msg string) {
	log.Println("[INFO]", msg)
}
```

## Inyección de dependencias

Con esta estructura, la inyección de dependencias es natural:

```go
// En tu main.go
db := store.NewDB()
userStore := store.NewDBUserStore(db)
userService := service.NewUserService(userStore)
userHandlers := handlers.NewUserHandlers(userService)
```

Esto es explícito y testeable. Puedes pasar un mock de `userStore` a `userService` en tests.

## Testing

Con esta estructura, testing es fácil:

```go
// internal/service/user_test.go
package service

import (
	"testing"
	"myapp/internal/models"
)

type MockStore struct{}

func (m *MockStore) GetUser(id int) (*models.User, error) {
	return &models.User{ID: id, Name: "Test"}, nil
}

func TestGetUserInfo(t *testing.T) {
	svc := NewUserService(&MockStore{})
	user, _ := svc.GetUserInfo(1)
	if user.Name != "Test" {
		t.Fail()
	}
}
```

## Evitar errores comunes

**Importes circulares:** Si `models` importa `service` e `service` importa `models`, tendrás un problema. Mantén la dirección clara: handlers -> service -> store -> models.

**Packages enormes:** Si un package tiene 50 archivos, probablemente necesites subdivirlo.

**Interfaces prematuros:** No hagas interfaces de todo. Hazlas cuando realmente necesites múltiples implementaciones o testing.

**Todo en main.go:** Esto no escala. Distribuye código desde el inicio.

## Escala

A medida que crece tu proyecto:

- Subdivide `internal/service` en `internal/service/user`, `internal/service/product`, etc.
- Agrega `internal/middleware` para HTTP middleware.
- Agrega `internal/config` para configuración.
- Agrega `migrations/` si usas SQL.

Pero mantén los principios: claridad, desacoplamiento, packages cohesivos.

## Conclusión

No hay una "forma correcta de Go", pero hay formas que funcionan mejor que otras. La estructura que describí escala desde un pequeño proyecto a una aplicación compleja. Es clara, testeable y fácil de mantener. Úsala como punto de partida y adapta según tus necesidades. El código que escribes hoy alguien (probablemente tú) lo tendrá que mantener mañana. Hazle un favor al futuro y organiza bien.
