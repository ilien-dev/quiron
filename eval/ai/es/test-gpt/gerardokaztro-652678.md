# Inicializando AWS CloudShell 3/3

En las dos entregas anteriores conocimos AWS CloudShell, revisamos su interfaz y preparamos un entorno básico de trabajo. En esta tercera y última parte vamos a convertirlo en una herramienta realmente útil: validaremos nuestra identidad, definiremos variables, ejecutaremos operaciones con AWS CLI y dejaremos algunos consejos para trabajar de forma segura y reproducible.

## Verifica tu identidad

CloudShell utiliza automáticamente las credenciales de la sesión iniciada en la consola de AWS. Por eso no necesitas ejecutar `aws configure` ni guardar claves de acceso manualmente.

Antes de realizar cualquier operación, confirma qué identidad estás utilizando:

```bash
aws sts get-caller-identity
```

El resultado incluirá el identificador de la cuenta, el ARN del usuario o rol y su ID interno:

```json
{
  "UserId": "AROAXXXXXXXXXXXXX:user",
  "Account": "123456789012",
  "Arn": "arn:aws:sts::123456789012:assumed-role/Developer/user"
}
```

Este paso parece sencillo, pero evita ejecutar comandos en la cuenta equivocada. Es especialmente importante cuando trabajas con varios ambientes, como desarrollo, pruebas y producción.

También conviene revisar la región activa:

```bash
aws configure get region
```

Si necesitas cambiarla temporalmente, puedes definir la variable `AWS_REGION`:

```bash
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION="$AWS_REGION"
```

## Crea un pequeño contexto de trabajo

Las variables de entorno ayudan a reducir errores y hacen que los comandos sean más fáciles de reutilizar:

```bash
export PROJECT_NAME="cloudshell-demo"
export ENVIRONMENT="dev"
export BUCKET_NAME="${PROJECT_NAME}-${ENVIRONMENT}-$(aws sts get-caller-identity \
  --query Account \
  --output text)"
```

Comprueba el resultado:

```bash
printf 'Proyecto: %s\nAmbiente: %s\nBucket: %s\n' \
  "$PROJECT_NAME" \
  "$ENVIRONMENT" \
  "$BUCKET_NAME"
```

Ahora podemos utilizar estas variables en lugar de repetir valores manualmente.

## Ejecuta una operación real

Como ejemplo, crearemos un archivo y lo copiaremos a Amazon S3. Primero genera el contenido:

```bash
cat > bienvenida.txt <<EOF
Proyecto: ${PROJECT_NAME}
Ambiente: ${ENVIRONMENT}
Creado desde AWS CloudShell
EOF
```

Después crea el bucket. El comando puede variar según la región. Para `us-east-1`:

```bash
aws s3api create-bucket \
  --bucket "$BUCKET_NAME" \
  --region "$AWS_REGION"
```

Para otras regiones debes indicar la configuración de ubicación:

```bash
aws s3api create-bucket \
  --bucket "$BUCKET_NAME" \
  --region "$AWS_REGION" \
  --create-bucket-configuration LocationConstraint="$AWS_REGION"
```

Sube el archivo:

```bash
aws s3 cp bienvenida.txt "s3://${BUCKET_NAME}/bienvenida.txt"
```

Y verifica que exista:

```bash
aws s3 ls "s3://${BUCKET_NAME}/"
```

CloudShell usa los permisos asociados a tu identidad actual. Si recibes un error `AccessDenied`, no significa que la terminal esté mal configurada: probablemente tu usuario o rol no tiene autorización para crear buckets o escribir en S3.

## Aprovecha las consultas de AWS CLI

AWS CLI puede filtrar respuestas sin depender de herramientas adicionales. Por ejemplo, para mostrar solamente los nombres de los buckets:

```bash
aws s3api list-buckets \
  --query 'Buckets[].Name' \
  --output table
```

También puedes utilizar `json`, `text`, `table` o `yaml` como formatos de salida. Para scripts, `json` y `text` suelen ser las opciones más prácticas; para una revisión rápida, `table` resulta más legible.

## Limpia los recursos de prueba

Cuando termines, elimina primero el archivo y después el bucket:

```bash
aws s3 rm "s3://${BUCKET_NAME}/bienvenida.txt"

aws s3api delete-bucket \
  --bucket "$BUCKET_NAME" \
  --region "$AWS_REGION"
```

Verifica que ya no aparezca:

```bash
aws s3api head-bucket --bucket "$BUCKET_NAME"
```

Si fue eliminado correctamente, el comando devolverá un error indicando que el recurso no está disponible.

## Recomendaciones finales

No almacenes claves de acceso, contraseñas ni secretos directamente en archivos de CloudShell. Utiliza roles de IAM y servicios como AWS Secrets Manager o Systems Manager Parameter Store.

Antes de ejecutar comandos destructivos, valida siempre la identidad, la región y los valores de tus variables. También es buena idea comenzar los scripts con:

```bash
set -euo pipefail
```

Esta configuración detiene la ejecución ante errores, variables inexistentes o fallos dentro de tuberías.

Con esto completamos la inicialización de AWS CloudShell. Ya tienes un entorno listo para explorar servicios, automatizar tareas y ejecutar scripts sin instalar herramientas localmente. La terminal está preparada; el siguiente paso es convertir tus comandos frecuentes en automatizaciones reutilizables.