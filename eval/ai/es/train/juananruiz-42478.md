# Generar Código Autonumérico con Reinicio Anual

Un patrón común en sistemas es generar códigos secuenciales que se reinician cada año. Números de factura, códigos de pedido, IDs de transacción. Si trabajas con una base de datos, aquí te muestro cómo hacerlo de manera confiable.

## El requisito

Necesitas un código que sea:
- Único dentro del año actual
- Secuencial (o al menos predecible)
- Que se reinicie en enero de cada año
- Generado al crear un nuevo registro

Por ejemplo: `INV-2024-001`, `INV-2024-002`, ... `INV-2025-001`, etc.

## Solución con SQL

La forma más confiable es usando la base de datos. SQL maneja concurrencia y garantiza unicidad.

### Estructura de tabla

```sql
CREATE TABLE invoices (
  id INT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(50) UNIQUE NOT NULL,
  amount DECIMAL(10, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  year INT GENERATED ALWAYS AS (YEAR(created_at)) STORED
);
```

Nota: Usamos una columna generada para el año. Esto evita inconsistencias.

### Función para generar el código

En MySQL:

```sql
DELIMITER //
CREATE FUNCTION next_invoice_code() RETURNS VARCHAR(50)
READS SQL DATA
BEGIN
  DECLARE year_val INT;
  DECLARE next_seq INT;
  DECLARE code VARCHAR(50);
  
  SET year_val = YEAR(NOW());
  SET next_seq = COALESCE((
    SELECT MAX(CAST(SUBSTRING_INDEX(code, '-', -1) AS UNSIGNED))
    FROM invoices
    WHERE YEAR(created_at) = year_val
  ), 0) + 1;
  
  SET code = CONCAT('INV-', year_val, '-', LPAD(next_seq, 3, '0'));
  RETURN code;
END //
DELIMITER ;
```

### Trigger automático

Usa un trigger para generar el código automáticamente:

```sql
CREATE TRIGGER generate_invoice_code
BEFORE INSERT ON invoices
FOR EACH ROW
BEGIN
  IF NEW.code IS NULL THEN
    SET NEW.code = next_invoice_code();
  END IF;
END;
```

Ahora cuando insertes un factura:

```sql
INSERT INTO invoices (amount) VALUES (99.99);
```

Se genera automáticamente: `INV-2024-001`.

## Solución con aplicación (Python)

Si prefieres hacerlo en tu código:

```python
from datetime import datetime
import sqlite3

def get_next_invoice_code():
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()
    
    year = datetime.now().year
    
    cursor.execute(
        "SELECT COUNT(*) FROM invoices WHERE strftime('%Y', created_at) = ?",
        (str(year),)
    )
    count = cursor.fetchone()[0]
    seq = count + 1
    
    code = f"INV-{year}-{seq:03d}"
    
    conn.close()
    return code

def create_invoice(amount):
    code = get_next_invoice_code()
    # Guardar invoice con code
    pass
```

Nota: Este enfoque tiene race conditions en aplicaciones de alta concurrencia. Si solo un proceso actualiza a la vez, funciona. Pero si múltiples procesos insertan simultáneamente, puedes duplicar códigos.

## Solución segura en aplicación (con lock)

Para evitar race conditions:

```python
import threading

lock = threading.Lock()

def get_next_invoice_code_safe():
    with lock:
        return get_next_invoice_code()
```

O mejor aún, usa transacciones:

```python
def create_invoice_safe(amount):
    conn = sqlite3.connect('mydb.db')
    conn.execute("BEGIN EXCLUSIVE")
    try:
        code = get_next_invoice_code()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO invoices (code, amount) VALUES (?, ?)",
            (code, amount)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()
```

## Manejo de reinicio anual

No necesitas hacer nada. Tu función/trigger automáticamente cuenta factura del año actual. Cuando llegue enero 1, `YEAR(NOW())` cambiará y el contador reiniciará.

Si alguna vez necesitas resincronizar (ej. después de una migración), limpia los códigos incorrectos:

```sql
DELETE FROM invoices WHERE year < 2024;
```

## Edge cases

**Fuera de orden:** ¿Qué pasa si borras una factura? El siguiente código salta un número. Es normal y aceptable.

**Concurrencia extrema:** Si tu sistema recibe miles de inserciones por segundo, incluso SQL puede tener problemas. En ese caso, considera UUID o Snowflake IDs.

**Resiliencia:** Si tu base de datos falla, puedes perder el secuencial. Para sistemas críticos, considera replicación o backups.

## Conclusión

Generar códigos autonuméricos que se reinician anualmente es un patrón común. SQL triggers son la forma más robusta. Si lo haces en aplicación, cuidado con concurrencia. Sea cual sea tu enfoque, pruébalo con múltiples inserciones simultáneas antes de ir a producción.
