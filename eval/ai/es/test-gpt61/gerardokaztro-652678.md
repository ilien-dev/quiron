# Inicializando AWS CloudShell 3/3

Abrir una terminal en el navegador es apenas el comienzo. Para trabajar con comodidad necesitamos reconocer nuestra sesión, organizar archivos y conservar una configuración que podamos reutilizar.

En esta última entrega vamos a preparar AWS CloudShell para el uso cotidiano con Bash. El objetivo es terminar con un entorno sencillo y un pequeño script para verificar el contexto antes de ejecutar comandos.

### Primero: identifica dónde estás

CloudShell incluye AWS CLI y utiliza las credenciales de la sesión de la consola. Por eso, para comenzar no necesitas ejecutar `aws configure` ni introducir claves de acceso. Puedes consultar estos detalles en la [introducción oficial de AWS CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/welcome.html).

Comprueba tu identidad:

```bash
aws sts get-caller-identity
```

La respuesta muestra el identificador de cuenta y el ARN del usuario o rol activo. Revísalos antes de modificar recursos, especialmente si trabajas con varias cuentas.

Después, inspecciona la configuración disponible:

```bash
aws configure list
```

Para los comandos de este artículo indicaremos la región explícitamente. Así resulta más fácil reconocer hacia dónde se dirige cada operación.

### Dale un lugar a tus archivos

Crea una estructura básica dentro de tu directorio personal:

```bash
mkdir -p ~/proyectos ~/scripts ~/respaldos
```

Puedes reservar `proyectos` para repositorios, `scripts` para automatizaciones y `respaldos` para copias temporales.

En los entornos estándar, CloudShell ofrece **1 GB de almacenamiento persistente por región**, ubicado en `$HOME`. Los archivos de ese directorio permanecen entre sesiones, pero no se sincronizan entre regiones. Los entornos de CloudShell dentro de una VPC no cuentan con esa persistencia. Consulta las [cuotas y restricciones oficiales](https://docs.aws.amazon.com/cloudshell/latest/userguide/limits.html).

Esto también significa que instalar una herramienta fuera de `$HOME` no garantiza que siga disponible en una sesión futura.

### Personaliza Bash

Abre tu archivo de configuración:

```bash
nano ~/.bashrc
```

Agrega al final:

```bash
export PATH="$HOME/scripts:$PATH"

alias ll='ls -lah'
alias proyectos='cd ~/proyectos'
alias identidad='aws sts get-caller-identity'
```

Guarda los cambios y carga la configuración:

```bash
source ~/.bashrc
```

Ahora `proyectos` te lleva directamente a tu carpeta de trabajo e `identidad` permite comprobar la cuenta activa.

La variable `PATH` también permite ejecutar por su nombre los scripts guardados en `~/scripts`. Mantén las personalizaciones agrupadas y evita agregar varias veces las mismas líneas.

### Crea una verificación reutilizable

Vamos a guardar un script que consulte identidad y región antes de trabajar:

```bash
cat > ~/scripts/contexto-aws <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

region="${1:?Uso: contexto-aws REGION}"

printf 'Identidad activa:\n'
aws sts get-caller-identity --output json

printf '\nRegión seleccionada: %s\n' "$region"
printf '\nZonas de disponibilidad:\n'
aws ec2 describe-availability-zones \
  --region "$region" \
  --query 'AvailabilityZones[].ZoneName' \
  --output table \
  --no-cli-pager
EOF

chmod +x ~/scripts/contexto-aws
```

Ejecútalo indicando una región:

```bash
contexto-aws us-east-1
```

Las consultas no crean recursos. Sin embargo, listar zonas requiere el permiso `ec2:DescribeAvailabilityZones`. Si recibes `AccessDenied`, revisa los permisos de tu identidad: disponer de una terminal no concede permisos adicionales.

### Conserva lo que importa

Antes de terminar, revisa cuánto espacio ocupas:

```bash
du -sh ~/proyectos ~/scripts ~/respaldos
```

Guarda el código y la configuración reutilizable en un repositorio, excluyendo secretos y archivos sensibles.

La persistencia tiene un límite: AWS puede eliminar los datos de una región tras **120 días sin utilizar CloudShell en ella**, según su [política de almacenamiento](https://docs.aws.amazon.com/cloudshell/latest/userguide/limits.html). Mantén una copia externa de cualquier archivo importante.

Con esto cerramos la serie: ya tienes una estructura de trabajo, atajos útiles y una comprobación reproducible del contexto. La próxima vez que abras CloudShell, empieza por confirmar tu identidad y seleccionar la región; después, ejecuta tu tarea con ese contexto claro.
