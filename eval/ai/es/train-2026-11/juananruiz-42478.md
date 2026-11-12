Casi todos los sistemas que emiten documentos necesitan identificadores legibles: facturas, expedientes, pedidos. Un formato habitual es `FAC-2026-00042`: un prefijo, el año y un número correlativo que vuelve a 1 cada enero. Parece trivial, pero hay trampas que conviene conocer desde el principio.

## Por qué no usar un IDENTITY o SERIAL

Una columna autoincremental sirve para una clave interna, pero no para este caso por tres motivos:

1. No se reinicia por año.
2. Los huecos aparecen cuando una transacción falla, porque el valor se consume igualmente.
3. El formato con prefijo y año tiene que construirse aparte.

Lo que necesitamos es un contador independiente, por ámbito y por año, que se incremente de forma atómica.

## Tabla de secuencias

```sql
CREATE TABLE secuencia_documento (
    ambito  VARCHAR(20) NOT NULL,   -- p. ej. 'FAC', 'PED'
    anio    INTEGER     NOT NULL,
    ultimo  INTEGER     NOT NULL DEFAULT 0,
    PRIMARY KEY (ambito, anio)
);
```

Cada combinación de ámbito y año tiene su fila. Cuando llega el 1 de enero no hay que hacer nada: la fila del nuevo año se crea sola la primera vez que se pide un número. El reinicio es implícito, lo que evita un job programado que pueda fallar.

## Obtener el siguiente número de forma atómica

En PostgreSQL, un único `INSERT ... ON CONFLICT` resuelve la creación y el incremento sin condiciones de carrera:

```sql
INSERT INTO secuencia_documento (ambito, anio, ultimo)
VALUES ('FAC', EXTRACT(YEAR FROM CURRENT_DATE), 1)
ON CONFLICT (ambito, anio)
DO UPDATE SET ultimo = secuencia_documento.ultimo + 1
RETURNING anio, ultimo;
```

La fila se bloquea durante el `UPDATE`, así que dos peticiones simultáneas reciben números distintos. No hagas nunca un `SELECT` seguido de un `UPDATE` desde la aplicación: entre ambas instrucciones otro proceso puede leer el mismo valor.

## Formatear el código

Con el número devuelto, el formato se construye en la capa de aplicación:

```python
def siguiente_codigo(cursor, ambito: str = "FAC") -> str:
    cursor.execute(SQL_SIGUIENTE, (ambito,))  # la consulta de arriba, parametrizada
    anio, numero = cursor.fetchone()
    return f"{ambito}-{anio}-{numero:05d}"
```

El resultado será `FAC-2026-00001`. Mantén el formato en un único punto del código, porque cambiar el número de dígitos más adelante afecta a todos los documentos que se generen.

## Consideraciones prácticas

- **Zona horaria.** El año depende de la fecha que use el servidor. Si operas en varios países, decide en qué zona cambia el año y documéntalo. Un documento emitido a las 00:30 del 1 de enero en Madrid es del 31 de diciembre en UTC, así que puede caer en el año anterior si el servidor trabaja en UTC.
- **Transacciones.** Si el número se pide dentro de una transacción que luego hace rollback, el contador ya se ha incrementado y queda un hueco. En la mayoría de sistemas es aceptable. Si la normativa exige correlatividad estricta, como algunas facturaciones fiscales, necesitas bloqueos más estrictos o registrar el hueco como documento anulado.
- **Rendimiento.** Una fila muy disputada puede convertirse en cuello de botella. Para volúmenes altos puedes reservar bloques de números, pero un reinicio o la caída del proceso dejará huecos.
- **Unicidad.** Añade una restricción `UNIQUE` sobre la columna del código en la tabla de documentos. Es la última red de seguridad si algo falla.

## Resumen

- Un contador por ámbito y año, con clave compuesta `(ambito, anio)`.
- El reinicio anual ocurre solo, al crearse la fila del nuevo año.
- Incremento atómico con `INSERT ... ON CONFLICT ... RETURNING`.
- El formato del código vive en la aplicación, en un solo sitio.

Con esto tienes un autonumérico legible, correlativo dentro de cada año y resistente a la concurrencia. En SQL Server o MySQL la idea es la misma; cambia solo la sintaxis del upsert (`MERGE` u `ON DUPLICATE KEY UPDATE`).

¿Lo has implementado de otra forma? Cuéntamelo en los comentarios.
