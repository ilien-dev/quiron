# ¿Qué son las API's? (para dummies)

Si estás empezando en el mundo de la programación o simplemente quieres entender de qué hablan los desarrolladores cuando mencionan "la API de tal servicio", este post es para ti. Vamos a explicar el concepto desde cero, sin asumir ningún conocimiento técnico previo.

## Empecemos por lo básico

API significa *Application Programming Interface*, que en español sería algo así como "Interfaz de Programación de Aplicaciones". Suena complicado, pero la idea es en realidad muy sencilla: una API es una forma en la que dos programas de computadora pueden "hablar" entre sí.

## La analogía del enchufe

Imagina un enchufe eléctrico en la pared de tu casa. No sabes (ni te importa) cómo está generada la electricidad, ni cómo llega hasta ese punto de la pared. Lo único que necesitas saber es cómo conectar tu aparato: qué forma tiene el enchufe, qué voltaje entrega. El enchufe es una "interfaz" entre la complejidad de la red eléctrica y tu simple lámpara de noche.

Una API funciona de forma parecida, pero entre programas: te da una forma estandarizada de pedir algo (datos, una acción, un servicio) sin que necesites saber cómo funciona por dentro el sistema que te lo está dando.

## Un ejemplo con el clima

Cuando abres una aplicación del clima en tu celular, la aplicación no "sabe" el clima por sí misma. Lo que hace es preguntarle a otro sistema (un servicio meteorológico) a través de su API: "oye, ¿qué clima hace ahora mismo en esta ciudad?". El servicio meteorológico le responde con esa información, y la aplicación simplemente la muestra en pantalla de forma bonita, con íconos, colores, gráficos.

Lo interesante es que esa misma API del clima la puede usar cualquier otra aplicación: un widget de escritorio, un asistente de voz, otra app de clima completamente distinta. Todas hacen la misma "pregunta" y reciben la misma información, aunque después la muestren de forma diferente.

## ¿Cómo se ve esto "por dentro"?

No hace falta entender el código para comprender la idea general, pero para quien tenga curiosidad: cuando una aplicación usa una API, generalmente le manda un mensaje a una dirección específica (parecida a una URL de internet), y recibe de vuelta la información, casi siempre en un formato de texto ordenado llamado JSON. Algo como esto:

```
Petición: "dame el clima de Madrid"
Respuesta: { "ciudad": "Madrid", "temperatura": "22°C", "clima": "soleado" }
```

La aplicación toma ese texto, extrae los datos que le interesan, y los presenta de forma visual al usuario.

## ¿Por qué son tan importantes?

### No hay que reinventar la rueda

Si quieres crear una aplicación que muestre mapas, no necesitas construir tú mismo un sistema de mapas desde cero (algo carísimo y complejísimo). Puedes usar la API de Google Maps, que ya hace ese trabajo pesado, y tú solo te encargas de la parte que le da valor único a tu aplicación.

### Permiten que las cosas se conecten entre sí

Gracias a las APIs, aplicaciones completamente distintas, hechas por empresas distintas, pueden trabajar juntas. Un ejemplo cotidiano: cuando compras algo en una tienda online y pagas con tu tarjeta, probablemente esa tienda esté usando la API de una empresa especializada en pagos (como Stripe o PayPal) en lugar de manejar ella misma los datos de tu tarjeta, lo cual sería mucho más riesgoso e ineficiente.

### Hacen posible todo un ecosistema

Muchas de las aplicaciones que usas a diario en realidad son "capas" construidas sobre APIs de otras empresas. Aplicaciones que te ayudan a reservar vuelos, comparar precios de hoteles, o publicar automáticamente en varias redes sociales a la vez, suelen depender de decenas de APIs distintas trabajando juntas por detrás de escena.

## ¿Y si quiero "usar" una API?

Si en algún momento te interesa dar el salto a la programación, vas a descubrir que muchísimos servicios ofrecen APIs públicas que cualquier desarrollador puede usar, a veces de forma gratuita (con ciertos límites) y a veces mediante un pago según el uso. Prácticamente cualquier cosa que se te ocurra —clima, mapas, traducción de idiomas, noticias, criptomonedas— tiene alguna API pública disponible para consultarla.

## En resumen

Una API es, básicamente, un "mensajero" entre dos programas: uno pide algo de una forma específica y acordada de antemano, y el otro responde con la información o el resultado solicitado. No necesitas ser programador para beneficiarte de las APIs (las usas constantemente sin darte cuenta cada vez que usas tu celular), pero entender la idea básica te ayuda a comprender mejor cómo funciona, por debajo, buena parte de la tecnología que usamos todos los días.
