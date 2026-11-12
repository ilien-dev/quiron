Cada vez que inicias sesión, instalas una dependencia o publicas una API, estás tomando decisiones relacionadas con la seguridad. Algunas son evidentes; otras pasan desapercibidas hasta que algo falla.

La ciberseguridad busca proteger sistemas, redes y datos frente a accesos no autorizados, alteraciones e interrupciones. Aunque suele asociarse con personas encapuchadas frente a una terminal, gran parte del trabajo consiste en entender riesgos, prevenir errores y preparar respuestas.

Si estás empezando en desarrollo, estos conceptos te ayudarán a construir con mayor criterio.

## Los tres pilares de la seguridad 🔐

Una forma sencilla de entender la ciberseguridad es mediante la tríada **CIA**, por sus siglas en inglés:

- **Confidencialidad:** solo las personas autorizadas pueden acceder a la información. Por ejemplo, un usuario no debería consultar los mensajes privados de otro.
- **Integridad:** los datos se mantienen correctos y solo se modifican mediante acciones autorizadas. Piensa en evitar que alguien altere el importe de una compra.
- **Disponibilidad:** los servicios y la información están accesibles cuando se necesitan. Una aplicación segura también debe poder recuperarse de fallos.

Estos pilares se complementan. Proteger una base de datos sirve de poco si cualquiera puede modificarla o si nunca está disponible.

## Amenazas, vulnerabilidades y riesgos

Aunque suelen mezclarse, estos términos describen cosas distintas.

Una **vulnerabilidad** es una debilidad: por ejemplo, un endpoint que permite consultar documentos sin comprobar permisos.

Una **amenaza** es algo que podría aprovechar esa debilidad, como una persona que intenta acceder a documentos ajenos.

El **riesgo** considera la probabilidad de que eso ocurra y sus consecuencias.

Esta distinción ayuda a priorizar. Un error que expone datos personales suele merecer más atención que un fallo visual en una página pública.

## Ataques que conviene reconocer 🎣

El **phishing** utiliza mensajes o páginas engañosas para conseguir credenciales, dinero o acciones de la víctima. Puede llegar por correo, SMS o incluso mediante una conversación aparentemente legítima.

El **malware** es software diseñado para realizar acciones maliciosas. El ransomware, por ejemplo, puede cifrar archivos para exigir un pago.

En aplicaciones web también aparecen problemas como la **inyección SQL**, donde entradas manipuladas alteran consultas construidas de forma insegura, y el **control de acceso defectuoso**, que permite realizar acciones o consultar recursos sin autorización.

No todos los incidentes requieren técnicas sofisticadas. Una clave publicada en un repositorio puede abrir una puerta enorme.

## Seguridad aplicada al desarrollo 💻

Puedes incorporar seguridad desde tus primeras aplicaciones:

1. **Valida las entradas.** Define qué formatos, tamaños y valores acepta cada campo. Para consultas SQL, utiliza parámetros en lugar de concatenar entradas.
2. **Comprueba permisos en el servidor.** Ocultar un botón en la interfaz no impide que alguien envíe la petición directamente.
3. **Protege los secretos.** Evita incluir claves y tokens en el código o en los registros. Si se filtran, revócalos y reemplázalos.
4. **Reduce privilegios.** Cada cuenta o servicio debería tener únicamente los permisos necesarios para su función.
5. **Revisa las dependencias.** Conoce qué incorpora tu proyecto y atiende las vulnerabilidades relevantes.
6. **Prepara la recuperación.** Mantén copias de seguridad y comprueba que puedes restaurarlas.

La autenticación multifactor añade protección a las cuentas, pero ninguna medida aislada elimina todos los riesgos.

## Aprende practicando, con autorización 🧪

Para empezar, estudia redes, HTTP, sistemas operativos y permisos. Después, experimenta en laboratorios diseñados para aprender o en aplicaciones propias.

Una práctica útil es revisar un pequeño proyecto y preguntarte: ¿qué datos protege?, ¿quién puede acceder a ellos?, ¿qué ocurriría si alguien manipula esta petición?

**Prueba únicamente sistemas propios o aquellos para los que tengas autorización explícita.**

La seguridad se construye con preguntas, decisiones y mejoras constantes. Tu próximo proyecto puede ser también tu primer laboratorio para aprender a proteger lo que creas.

¿Qué concepto de ciberseguridad te gustaría explorar primero? 👇
