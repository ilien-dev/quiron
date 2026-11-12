# ¿Qué son API's? (para dummies)

Si estás empezando en programación, seguro has escuchado frases como "consume la API", "expón una API" o "necesitas una API key". Suena complicado, pero la idea es muy simple. Vamos a verlo sin tecnicismos.

## Una API es un mesero

Imagina que estás en un restaurante. Tú eres el cliente, la cocina es donde ocurre la magia, y entre ambos está el **mesero**.

No entras a la cocina a preparar tu comida. Le dices al mesero qué quieres, él se lo pasa a la cocina y te regresa tu plato.

Eso es una **API** (*Application Programming Interface*, o Interfaz de Programación de Aplicaciones):

- **Tú** = tu aplicación (el cliente)
- **Mesero** = la API
- **Cocina** = otro sistema, servidor o base de datos

La API es el intermediario que te permite pedir cosas a otro programa sin saber cómo funciona por dentro.

## El menú: las reglas del juego

En un restaurante no puedes pedir cualquier cosa, solo lo que está en el menú. Con las APIs pasa igual: cada una define qué puedes pedir y cómo hacerlo. Esa lista se llama **documentación**.

Por ejemplo, una API del clima podría decirte: "Si me envías el nombre de una ciudad, te devuelvo la temperatura actual".

## Ejemplos de la vida real

Usas APIs todos los días sin darte cuenta:

- **La app del clima** en tu celular le pide los datos a un servicio meteorológico mediante una API.
- **"Iniciar sesión con Google"** funciona porque la página se comunica con la API de Google.
- **Pagar en línea**: la tienda no procesa tu tarjeta, le pide a una API de pagos (como Stripe o PayPal) que lo haga.
- **Mapas en una página web**: casi siempre vienen de la API de Google Maps u OpenStreetMap.

## Cómo se ve una petición

La mayoría de las APIs web usan HTTP, el mismo protocolo con el que tu navegador abre páginas. Tú haces una **petición** (*request*) y recibes una **respuesta** (*response*).

Estos son los verbos más comunes:

| Verbo | Qué hace | Analogía |
|--------|----------|----------|
| GET | Pedir información | "Tráeme el menú" |
| POST | Enviar datos nuevos | "Quiero hacer un pedido" |
| PUT | Actualizar algo | "Cambia mi pedido" |
| DELETE | Eliminar algo | "Cancela mi pedido" |

Un ejemplo en JavaScript:

```javascript
fetch("https://api.ejemplo.com/clima?ciudad=Madrid")
  .then(respuesta => respuesta.json())
  .then(datos => console.log(datos));
```

Y la respuesta podría ser algo así:

```json
{
  "ciudad": "Madrid",
  "temperatura": 22,
  "condicion": "soleado"
}
```

Ese formato se llama **JSON**: texto ordenado que tanto humanos como programas pueden leer fácilmente.

## ¿Y la API key?

Muchas APIs piden una **clave** para saber quién eres y cuánto la usas. Es como la reservación en el restaurante: te identifica. Trátala como una contraseña y **nunca la subas a un repositorio público**.

## ¿Por qué son tan importantes?

1. **Ahorran tiempo**: no tienes que construir todo desde cero.
2. **Separan responsabilidades**: cada sistema hace lo suyo.
3. **Permiten integrar servicios**: tu app puede mandar correos, cobrar o mostrar mapas sin que tú construyas esas funciones.
4. **Protegen**: el otro sistema solo expone lo que quiere, no todo su interior.

## Para practicar

Prueba con APIs públicas y gratuitas, sin registro:

- [PokéAPI](https://pokeapi.co): datos de Pokémon
- [JSONPlaceholder](https://jsonplaceholder.typicode.com): datos falsos para practicar
- [Open-Meteo](https://open-meteo.com): clima

Abre tu navegador, pega una de sus URLs y verás la respuesta en JSON. Ya hiciste tu primera petición.

## En resumen

Una API es un **intermediario** que permite que dos programas se comuniquen siguiendo unas reglas claras. Tú pides, ella traduce y te devuelve lo que necesitas.

La próxima vez que alguien diga "solo consume la API", ya sabes que se trata de pedirle algo al mesero.

¿Te quedó alguna duda? Cuéntame en los comentarios y lo vemos. 👇

---

Nota: dejé el título tal como lo pediste, pero en español lo correcto es "APIs" sin apóstrofo. Si quieres, lo cambio. También dejé `published: false` en el encabezado para que lo revises antes de publicarlo.
