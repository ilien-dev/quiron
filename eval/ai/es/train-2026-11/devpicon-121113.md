Hace unos meses, nuestro proyecto era una carpeta llena de ejercicios para clase. Hoy es un APK que instalamos en nuestros teléfonos y que alguien que no conoce nuestra facultad puede usar sin problemas. Este post cuenta cómo llegamos hasta ahí, qué salió mal por el camino y qué nos gustaría que supieras si estás en una situación parecida.

## El punto de partida

Empezamos como cualquier grupo de estudiantes: un trabajo final con una consigna clara y un plazo ajustado. La idea era simple, una aplicación que resolviera un problema concreto que vivíamos en el día a día de la carrera. Nadie en el equipo había publicado una app antes, y solo dos de nosotros habíamos tocado código fuera de los ejercicios guiados.

Decidimos usar [TECNOLOGÍA PRINCIPAL, por ejemplo Flutter / Kotlin / React Native] porque era lo que se veía en clase y porque prometía un solo código para varias plataformas. Para el backend usamos [BACKEND O SERVICIO, por ejemplo Firebase], que nos permitió avanzar sin montar un servidor propio.

## Lo que aprendimos en las primeras semanas

Las primeras versiones eran un desastre. Cada pantalla tenía su propia lógica, los datos se guardaban de cualquier manera y nadie se animaba a tocar el código del compañero. Lo que más nos ayudó fue algo muy básico: **separar la interfaz de la lógica**. Cuando una pantalla solo mostraba datos y otra capa se encargaba de consultarlos, dejamos de romper cosas cada vez que cambiábamos algo.

También aprendimos a usar Git de verdad. Al principio hacíamos commits del tipo "cambios" y trabajábamos todos en la misma rama. Pasamos a ramas por funcionalidad y revisiones de código antes de unir cambios. Parece un detalle, pero nos ahorró muchas horas de discusiones.

## El momento de compilar el APK

Hasta que no intentamos generar el APK, no nos dimos cuenta de cuánto nos faltaba. Algunos problemas que nos encontramos:

- **Permisos mal declarados** en el manifiesto. La app funcionaba en el emulador y fallaba en el teléfono real.
- **Claves y configuraciones sensibles** en el código fuente. Tuvimos que moverlas a variables de entorno y rotar credenciales que ya habían quedado expuestas en el repositorio.
- **Firma de la aplicación.** Entender la diferencia entre una build de depuración y una de release, y cómo firmar el APK con un keystore que guardáramos bien, nos tomó más tiempo del que esperábamos.
- **Versiones de dependencias** que no eran compatibles entre sí. Fijarlas y documentarlas fue tedioso, pero evitó que la compilación se rompiera de un día para otro.

Cada uno de estos problemas nos enseñó algo que no aparece en los ejercicios de clase.

## Probar con gente real

Lo que más cambió el proyecto fue mostrarlo a personas fuera del grupo. Un compañero de otra carrera encontró en cinco minutos un flujo que para nosotros era obvio y que estaba roto. Un familiar nos preguntó por qué un botón no hacía lo que decía. Esas observaciones valieron más que cualquier revisión interna.

Armamos una versión de prueba y la distribuimos por enlace. Recibimos reportes de errores, sugerencias y, sobre todo, la confirmación de que la app resolvía un problema real.

## Lo que haríamos distinto

- **Definir el alcance antes de programar.** Tuvimos que recortar funcionalidades varias veces. Una versión mínima que funcione es mejor que una lista larga a medio hacer.
- **Automatizar la build desde el principio.** Generar el APK manualmente cada vez nos hizo perder tiempo y nos llevó a errores.
- **Escribir un README decente.** Cuando alguien nuevo se unió al equipo, tardó demasiado en levantar el proyecto.
- **No guardar secretos en el repositorio nunca,** ni siquiera en una rama de prueba.

## Para quien esté empezando

Si tienes un proyecto de clase que te gustaría llevar más lejos, mi consejo es simple: elige un problema pequeño, muéstralo a alguien lo antes posible y no tengas miedo de rehacer partes del código. La distancia entre "funciona en mi computadora" y "lo instalo en mi teléfono y lo uso" es más corta de lo que parece, pero tiene pasos que vale la pena conocer de antemano.

Si quieres ver el código o probar la app, dejamos el enlace al repositorio y a la última versión en los comentarios. Y si tropiezas con algo que nosotros también sufrimos, escríbenos. Seguramente ya lo hemos resuelto.

---

*Nota: el texto asume un proyecto de equipo universitario que pasó de un trabajo de clase a un APK instalable. Los campos entre corchetes son los que necesito que completes con los datos reales (tecnologías, nombre de la app, enlaces). Si me dices el nombre del proyecto y su stack, o me dejas revisar el repositorio en `svipall/`, ajusto el texto a lo que realmente hicieron y lo dejo cerca de las 600 palabras.*
