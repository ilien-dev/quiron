# Servidores: ¿Mascotas o Ganado?

Si trabajas en el mundo de la infraestructura, DevOps o la nube, es muy probable que te hayas cruzado con la analogía de **"pets vs. cattle"**, es decir, mascotas frente a ganado. Es una de esas metáforas que, aunque suene un poco brusca, explica de forma muy clara un cambio profundo en la manera en que gestionamos los servidores.

En este post te cuento de dónde viene, qué significa y por qué es importante para cualquier desarrollador que despliegue aplicaciones hoy en día.

## El origen de la metáfora

La analogía suele atribuirse a Bill Baker, ingeniero de Microsoft, que la usó alrededor de 2012 para explicar la diferencia entre escalar verticalmente y escalar horizontalmente. Más tarde Randy Bias la popularizó en el contexto de la computación en la nube, y desde entonces se ha convertido en un clásico de las charlas sobre infraestructura.

## Servidores mascota

Piensa en tu perro o tu gato. Tiene nombre. Lo conoces bien. Si se pone enfermo, lo llevas al veterinario y haces lo que sea necesario para que se recupere. Es único e irreemplazable.

Así se gestionaban (y en muchos sitios se siguen gestionando) los servidores tradicionales:

- Tienen nombres propios: `zeus`, `gandalf`, `produccion-principal`.
- Se configuran a mano, entrando por SSH e instalando paquetes o editando archivos.
- Con los años acumulan cambios que nadie documentó: un parche aquí, una librería allá, un cron que alguien añadió en 2016.
- Cuando fallan, alguien se conecta a medianoche para "curarlos".
- Nadie se atreve a reiniciarlos, y mucho menos a apagarlos, porque no se sabe muy bien qué pasaría.

El problema de fondo es que el servidor se convierte en un **copo de nieve** (*snowflake server*): una pieza única cuya configuración es imposible de reproducir con exactitud. Si se estropea el disco, recrearlo puede llevar días.

## Servidores ganado

Ahora piensa en una granja con cientos de reses. No tienen nombre, sino un número. Son todas prácticamente iguales. Si una enferma, no se detiene toda la granja: se sustituye y la operación continúa.

Aplicado a los servidores:

- Se identifican con números o identificadores generados: `web-01`, `web-02`, `i-0a1b2c3d4e`.
- Se crean de forma automatizada a partir de una definición: una imagen, un script o una plantilla.
- Son idénticos entre sí.
- Si uno falla, no se repara: **se destruye y se crea uno nuevo**.
- Se pueden añadir o quitar según la demanda.

La clave está en que el valor no reside en el servidor concreto, sino en **la receta** que permite crearlo.

## Las piezas que lo hacen posible

Tratar a los servidores como ganado no es solo un cambio de mentalidad. Requiere herramientas y prácticas concretas:

**Infraestructura como código (IaC)**: la infraestructura se describe en archivos versionados con herramientas como Terraform, Pulumi o CloudFormation. Crear un entorno completo es ejecutar un comando.

**Gestión de configuración**: herramientas como Ansible, Chef o Puppet aseguran que todos los servidores tengan exactamente la misma configuración.

**Infraestructura inmutable**: en lugar de actualizar un servidor existente, se construye una imagen nueva (por ejemplo, con Packer o como imagen de Docker) y se reemplazan los servidores antiguos. Nadie entra a modificar nada en caliente.

**Contenedores y orquestadores**: Docker y Kubernetes llevan la idea al extremo. Un pod que falla se reinicia automáticamente; si un nodo cae, sus cargas se reprograman en otros nodos sin intervención humana.

**Autoescalado**: grupos de autoescalado en AWS, GCP o Azure crean y destruyen instancias según la carga.

**Logs y métricas centralizados**: si los servidores son desechables, los logs no pueden vivir en ellos. Se envían a sistemas externos como ELK, Loki o Datadog.

## ¿Qué cambia para ti como desarrollador?

Aunque no gestiones la infraestructura directamente, este enfoque afecta a cómo escribes tus aplicaciones:

- **No guardes estado en el disco local**. Las sesiones van a Redis o a una base de datos; los archivos subidos, a un almacenamiento de objetos como S3.
- **Configura mediante variables de entorno**, no con archivos editados a mano en el servidor.
- **Diseña para que tu aplicación pueda morir en cualquier momento** y arrancar rápido.
- **Escribe logs a la salida estándar** para que la plataforma los recoja.

Si te suena, es porque muchas de estas ideas están recogidas en la metodología *The Twelve-Factor App*.

## ¿Siempre ganado?

No todo encaja perfectamente en la metáfora. Las bases de datos, por ejemplo, tienen estado y no se pueden destruir alegremente. Aun así, incluso ahí la tendencia es acercarse al modelo de ganado: réplicas, backups automatizados, servicios gestionados y la capacidad de recrear una instancia a partir de una copia.

Algunos incluso han ampliado la metáfora con una tercera categoría, los **insectos**: contenedores o funciones serverless que viven segundos o minutos.

## Conclusión

La pregunta "¿mascotas o ganado?" no es solo una curiosidad. Es una forma rápida de evaluar lo resiliente que es tu infraestructura. Si hay un servidor en tu empresa al que todos temen tocar, tienes una mascota, y tarde o temprano te dará un disgusto.

El objetivo es que cualquier servidor pueda desaparecer sin que nadie lo note. Y para eso, lo importante no es cuidar a cada máquina, sino cuidar la receta.
