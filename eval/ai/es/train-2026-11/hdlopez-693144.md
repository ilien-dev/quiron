# ¿Cómo estructurar tu aplicación en Go?

Uno de los primeros problemas que enfrenta quien empieza con Go es decidir cómo organizar el proyecto. Go no impone una estructura de carpetas como otros frameworks, así que la libertad es total, y eso puede ser tanto una ventaja como una trampa. Este artículo presenta una organización práctica que funciona bien para APIs HTTP y servicios de tamaño mediano, junto con los principios detrás de ella.

No existe una estructura "correcta" única. Lo importante es que cumpla tres objetivos: que sea fácil saber dónde está cada cosa, que las dependencias fluyan en una sola dirección y que el código sea fácil de probar.

## Empieza por el módulo

Todo proyecto Go moderno comienza con un módulo:

```bash
mkdir tienda && cd tienda
go mod init github.com/tuusuario/tienda
```

El nombre del módulo es el prefijo de todos los imports internos, así que conviene elegirlo pensando en que quizá lo publiques algún día.

## Una estructura de referencia

Este es un esquema que funciona bien para una aplicación web:

```
tienda/
├── cmd/
│   └── api/
│       └── main.go
├── internal/
│   ├── config/
│   │   └── config.go
│   ├── producto/
│   │   ├── handler.go
│   │   ├── service.go
│   │   ├── repository.go
│   │   └── producto.go
│   ├── pedido/
│   │   ├── handler.go
│   │   ├── service.go
│   │   └── ...
│   └── platform/
│       ├── database/
│       └── httpserver/
├── go.mod
└── go.sum
```

Cada parte tiene un propósito concreto.

### `cmd/`: los puntos de entrada

El directorio `cmd/` contiene un subdirectorio por cada ejecutable. Si tu proyecto tiene una API y un worker que procesa colas, tendrás `cmd/api/` y `cmd/worker/`. Ambos pueden compartir código de `internal/`.

La regla es que `main.go` sea mínimo. Su única responsabilidad es leer la configuración, construir las dependencias y arrancar el servidor:

```go
// cmd/api/main.go
package main

import (
	"log"
	"net/http"

	"github.com/tuusuario/tienda/internal/config"
	"github.com/tuusuario/tienda/internal/platform/database"
	"github.com/tuusuario/tienda/internal/producto"
)

func main() {
	cfg, err := config.Cargar()
	if err != nil {
		log.Fatal(err)
	}

	db, err := database.Conectar(cfg.DatabaseURL)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	repo := producto.NewRepositorioPostgres(db)
	svc := producto.NewService(repo)
	handler := producto.NewHandler(svc)

	mux := http.NewServeMux()
	handler.Registrar(mux)

	log.Printf("escuchando en %s", cfg.Puerto)
	log.Fatal(http.ListenAndServe(":"+cfg.Puerto, mux))
}
```

Si `main.go` empieza a crecer con lógica de negocio, es señal de que algo debe moverse a `internal/`.

### `internal/`: el código privado

Go tiene una característica especial: cualquier paquete dentro de un directorio llamado `internal/` solo puede ser importado por código que esté en el mismo árbol padre. En la práctica, esto significa que nadie fuera de tu módulo puede depender de tus detalles de implementación. Es una herramienta poderosa para evitar que tu API interna se convierta en un contrato público sin querer.

Muchos proyectos usan `pkg/` para código reutilizable hacia afuera. Para una aplicación, normalmente no lo necesitas. Empieza con `internal/` y solo expón algo cuando tengas una razón real.

### Organiza por dominio, no por capa

Un error frecuente es organizar el proyecto en carpetas globales como `controllers/`, `models/` y `services/`. Esto obliga a saltar entre directorios para entender una sola funcionalidad, y con el tiempo esas carpetas se llenan de código no relacionado.

Es mejor agrupar por dominio. Todo lo relacionado con productos vive en `internal/producto/`: su modelo, su lógica, su acceso a datos y su handler HTTP. Si quieres entender cómo funciona la gestión de productos, abres una sola carpeta.

## Las capas dentro de un dominio

Dentro de cada paquete de dominio conviene separar tres responsabilidades:

1. **Handler**: traduce HTTP a llamadas de servicio y viceversa.
2. **Service**: contiene la lógica de negocio.
3. **Repository**: habla con la base de datos o cualquier otra fuente de datos.

Las dependencias deben fluir en una sola dirección: handler depende de service, y service depende de repository. Nunca al revés.

### El modelo

Empieza definiendo tus tipos de dominio, sin etiquetas de base de datos ni de JSON si no son necesarias:

```go
// internal/producto/producto.go
package producto

import "errors"

type Producto struct {
	ID     int64
	Nombre string
	Precio int64 // en centavos, para evitar problemas con flotantes
	Stock  int
}

var ErrNoEncontrado = errors.New("producto no encontrado")
var ErrStockInsuficiente = errors.New("stock insuficiente")
```

Definir los errores de dominio aquí permite que las capas superiores los identifiquen con `errors.Is` sin conocer detalles de la base de datos.

### El repositorio como interfaz

Aquí entra uno de los principios más importantes de Go: **define las interfaces donde se consumen**, no donde se implementan. El servicio es quien necesita el repositorio, así que la interfaz vive en el mismo paquete que el servicio:

```go
// internal/producto/repository.go
package producto

import "context"

type Repositorio interface {
	Obtener(ctx context.Context, id int64) (Producto, error)
	Guardar(ctx context.Context, p Producto) error
}
```

La implementación concreta, con PostgreSQL por ejemplo, puede vivir en el mismo paquete o en uno separado. Lo importante es que el servicio no sepa nada de SQL.

```go
// internal/producto/repositorio_postgres.go
package producto

import (
	"context"
	"database/sql"
	"errors"
)

type RepositorioPostgres struct {
	db *sql.DB
}

func NewRepositorioPostgres(db *sql.DB) *RepositorioPostgres {
	return &RepositorioPostgres{db: db}
}

func (r *RepositorioPostgres) Obtener(ctx context.Context, id int64) (Producto, error) {
	var p Producto
	err := r.db.QueryRowContext(ctx,
		`SELECT id, nombre, precio, stock FROM productos WHERE id = $1`, id,
	).Scan(&p.ID, &p.Nombre, &p.Precio, &p.Stock)

	if errors.Is(err, sql.ErrNoRows) {
		return Producto{}, ErrNoEncontrado
	}
	return p, err
}

func (r *RepositorioPostgres) Guardar(ctx context.Context, p Producto) error {
	_, err := r.db.ExecContext(ctx,
		`UPDATE productos SET nombre = $1, precio = $2, stock = $3 WHERE id = $4`,
		p.Nombre, p.Precio, p.Stock, p.ID,
	)
	return err
}
```

Observa que traducimos `sql.ErrNoRows` a nuestro propio `ErrNoEncontrado`. Así, el resto de la aplicación no depende de detalles de `database/sql`.

### El servicio

El servicio contiene las reglas de negocio. Es la parte más valiosa del código y la que más conviene probar:

```go
// internal/producto/service.go
package producto

import "context"

type Service struct {
	repo Repositorio
}

func NewService(repo Repositorio) *Service {
	return &Service{repo: repo}
}

func (s *Service) Vender(ctx context.Context, id int64, cantidad int) error {
	p, err := s.repo.Obtener(ctx, id)
	if err != nil {
		return err
	}

	if p.Stock < cantidad {
		return ErrStockInsuficiente
	}

	p.Stock -= cantidad
	return s.repo.Guardar(ctx, p)
}
```

Fíjate que el servicio recibe un `Repositorio`, no un `*RepositorioPostgres`. Esto permite pasarle una implementación falsa durante las pruebas.

### El handler

El handler se encarga de HTTP: parsea la petición, llama al servicio y traduce los errores a códigos de respuesta:

```go
// internal/producto/handler.go
package producto

import (
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
)

type Handler struct {
	svc *Service
}

func NewHandler(svc *Service) *Handler {
	return &Handler{svc: svc}
}

func (h *Handler) Registrar(mux *http.ServeMux) {
	mux.HandleFunc("POST /productos/{id}/vender", h.vender)
}

func (h *Handler) vender(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
	if err != nil {
		http.Error(w, "id inválido", http.StatusBadRequest)
		return
	}

	var body struct {
		Cantidad int `json:"cantidad"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		http.Error(w, "cuerpo inválido", http.StatusBadRequest)
		return
	}

	err = h.svc.Vender(r.Context(), id, body.Cantidad)
	switch {
	case errors.Is(err, ErrNoEncontrado):
		http.Error(w, err.Error(), http.StatusNotFound)
	case errors.Is(err, ErrStockInsuficiente):
		http.Error(w, err.Error(), http.StatusConflict)
	case err != nil:
		http.Error(w, "error interno", http.StatusInternalServerError)
	default:
		w.WriteHeader(http.StatusNoContent)
	}
}
```

Desde Go 1.22, `http.ServeMux` soporta métodos y parámetros de ruta como `{id}`, así que muchas aplicaciones ya no necesitan un router externo.

Nota también que los errores internos no se exponen al cliente. Registrarlos en un log es responsabilidad del código que los ve por primera vez, o de un middleware.

## Inyección de dependencias sin frameworks

Probablemente te preguntes dónde está el contenedor de inyección de dependencias. En Go, la respuesta más idiomática es: no lo necesitas. Las dependencias se pasan explícitamente por constructores, como vimos en `main.go`:

```go
repo := producto.NewRepositorioPostgres(db)
svc := producto.NewService(repo)
handler := producto.NewHandler(svc)
```

Son tres líneas, fáciles de leer y de seguir con el depurador. Cuando la aplicación crezca mucho, existen herramientas como `google/wire` que generan este código por ti, pero empieza sin ellas. Muchos proyectos reales nunca las necesitan.

## Configuración

Lee la configuración una sola vez, al arrancar, y pásala como un struct tipado. Evita llamar a `os.Getenv` en medio de la lógica de negocio:

```go
// internal/config/config.go
package config

import (
	"errors"
	"os"
)

type Config struct {
	Puerto      string
	DatabaseURL string
}

func Cargar() (Config, error) {
	cfg := Config{
		Puerto:      getEnv("PUERTO", "8080"),
		DatabaseURL: os.Getenv("DATABASE_URL"),
	}
	if cfg.DatabaseURL == "" {
		return Config{}, errors.New("DATABASE_URL es obligatoria")
	}
	return cfg, nil
}

func getEnv(clave, valorPorDefecto string) string {
	if v := os.Getenv(clave); v != "" {
		return v
	}
	return valorPorDefecto
}
```

Así, si falta una variable obligatoria, la aplicación falla al arrancar y no a las tres horas, cuando alguien ejecuta una ruta concreta.

## Pruebas

Esta estructura brilla a la hora de probar. El servicio se prueba con un repositorio falso, sin base de datos:

```go
// internal/producto/service_test.go
package producto

import (
	"context"
	"errors"
	"testing"
)

type repoFalso struct {
	producto Producto
	guardado bool
}

func (r *repoFalso) Obtener(_ context.Context, _ int64) (Producto, error) {
	return r.producto, nil
}

func (r *repoFalso) Guardar(_ context.Context, p Producto) error {
	r.producto = p
	r.guardado = true
	return nil
}

func TestVender_StockInsuficiente(t *testing.T) {
	repo := &repoFalso{producto: Producto{ID: 1, Stock: 2}}
	svc := NewService(repo)

	err := svc.Vender(context.Background(), 1, 5)

	if !errors.Is(err, ErrStockInsuficiente) {
		t.Fatalf("esperaba ErrStockInsuficiente, obtuve %v", err)
	}
	if repo.guardado {
		t.Error("no debería haber guardado el producto")
	}
}

func TestVender_DescuentaStock(t *testing.T) {
	repo := &repoFalso{producto: Producto{ID: 1, Stock: 10}}
	svc := NewService(repo)

	if err := svc.Vender(context.Background(), 1, 3); err != nil {
		t.Fatalf("error inesperado: %v", err)
	}
	if repo.producto.Stock != 7 {
		t.Errorf("stock = %d, quiero 7", repo.producto.Stock)
	}
}
```

Las pruebas del servicio son rápidas, no necesitan infraestructura y documentan las reglas de negocio mejor que cualquier comentario. Las pruebas de integración del repositorio pueden ir aparte, usando una base de datos real, quizá con Docker o `testcontainers`.

## Errores comunes

Estos son los problemas que más veo al revisar proyectos en Go:

**Paquetes demasiado grandes o demasiado pequeños.** Un paquete `utils` con cincuenta funciones no relacionadas es un cajón de sastre. Del otro lado, un paquete por cada struct genera fricción innecesaria. Agrupa por concepto del dominio.

**Dependencias circulares.** Si dos paquetes necesitan importarse mutuamente, normalmente hay una responsabilidad mal ubicada. Extrae el tipo compartido a un tercer paquete o invierte la dependencia con una interfaz.

**Interfaces gigantes definidas en el lugar equivocado.** Si defines una interfaz con veinte métodos en el paquete del implementador, todos los consumidores quedan atados a ella. Define interfaces pequeñas, en el paquete que las usa.

**Modelos de base de datos filtrados a la API.** Tener un solo struct con etiquetas `json` y `db` mezcladas puede parecer práctico, pero acopla tu contrato HTTP al esquema de la tabla. Separar los DTOs de los modelos de dominio cuesta un poco más de código y te ahorra muchos dolores de cabeza.

**Usar `context.Background()` en medio de la aplicación.** El contexto debe llegar desde la petición HTTP y pasarse hacia abajo. Así, si el cliente cancela, las consultas a la base de datos también se cancelan.

## Cuándo simplificar

Esta estructura es útil para aplicaciones con varios dominios y un equipo que necesita orientarse rápido. Para un script de un solo archivo o una utilidad de línea de comandos, no tiene sentido. Un `main.go` con unos cientos de líneas es perfectamente válido.

La regla práctica es: empieza simple y separa cuando sientas el dolor. Si ya tienes que buscar en cinco archivos para cambiar una sola regla, es momento de introducir capas. Si tu proyecto tiene cuatro funciones, no necesitas repositorios ni servicios.

## Conclusión

Estructurar una aplicación en Go no requiere magia. Algunas ideas bastan para tomar buenas decisiones: organizar por dominio, mantener `main.go` pequeño, usar `internal/` para encapsular, definir interfaces donde se consumen, pasar dependencias por constructores y mantener la lógica de negocio libre de detalles de infraestructura.

Con eso, tu código será fácil de leer, de probar y de cambiar. Y cuando el proyecto crezca, esas decisiones te darán una base sólida sobre la que construir.

Si tienes tu propia forma de organizar proyectos en Go, cuéntamela en los comentarios. Siempre es interesante ver cómo lo resuelve cada equipo.

---

*Nota: corregí el título a "¿Cómo estructurar tu aplicación en Go?" con tilde en la "o", que es la forma correcta en español. Si prefieres mantenerlo sin tilde, dímelo y lo cambio. El texto tiene unas 1.700 palabras contando el código; sin los bloques de código queda en torno a 1.300–1.400.*
