# Inicializando AWS CloudShell 3/3

En esta última entrega vamos a dejar AWS CloudShell listo para trabajar: comprobaremos nuestra identidad, revisaremos la región activa y prepararemos una configuración sencilla que podremos reutilizar en futuras sesiones.

AWS CloudShell es una terminal accesible desde la consola de AWS. Incluye AWS CLI y otras herramientas, y utiliza las credenciales de la sesión con la que accediste a la consola. Esto permite empezar a ejecutar comandos sin instalar software en tu computadora. [Documentación de AWS CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/)

## 1. Abre CloudShell y comprueba tu identidad

Inicia sesión en la consola de AWS, selecciona una región compatible y abre **CloudShell** desde el icono de la barra de herramientas. Una vez que aparezca la terminal, ejecuta:

```bash
aws sts get-caller-identity
```

La respuesta incluye la cuenta de AWS y el ARN de la identidad que estás utilizando. Este paso es especialmente útil si trabajas con varias cuentas o roles: antes de ejecutar comandos, asegúrate de estar en el lugar correcto.

CloudShell usa los permisos de tu identidad. Si un comando devuelve `AccessDenied`, revisa las políticas de IAM aplicables o consulta con el administrador de la cuenta.

## 2. Revisa la región y las herramientas

Para conocer la región configurada y la versión de AWS CLI, ejecuta:

```bash
aws configure get region
aws --version
```

CloudShell configura la región predeterminada a partir de la región seleccionada en la consola. También puedes indicar una región explícitamente en un comando:

```bash
aws ec2 describe-regions --region us-east-1
```

El parámetro `--region` afecta a ese comando. Recuerda que muchos recursos de AWS son regionales: si buscas una instancia o un bucket en un contexto distinto al esperado, podrías no obtener el resultado que buscas. [Conceptos de AWS CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/working-with-aws-cloudshell.html)

## 3. Prepara tu espacio de trabajo

Crea un directorio para tus ejercicios y entra en él:

```bash
mkdir -p ~/proyectos/cloudshell
cd ~/proyectos/cloudshell
```

Ahora crea un pequeño archivo de bienvenida:

```bash
cat > bienvenida.sh <<'EOF'
#!/usr/bin/env bash
echo "¡CloudShell está listo!"
echo "Directorio actual: $(pwd)"
EOF

chmod +x bienvenida.sh
./bienvenida.sh
```

Ya tienes un script que puedes modificar y volver a ejecutar. Es un buen punto de partida para guardar comandos frecuentes o pequeñas automatizaciones.

## 4. Personaliza Bash

Si utilizas Bash, puedes añadir alias a `~/.bashrc`. Primero crea una copia de seguridad:

```bash
cp ~/.bashrc ~/.bashrc.bak
```

Después abre `~/.bashrc` con tu editor favorito y agrega estas líneas al final:

```bash
alias c='clear'
alias aws-id='aws sts get-caller-identity'
```

Guarda el archivo y carga los cambios:

```bash
source ~/.bashrc
```

A partir de ahora, `aws-id` mostrará la identidad activa. Si algo falla al editar la configuración de inicio, la copia de seguridad te ayudará a recuperar el archivo anterior. AWS también recomienda tener cuidado al modificar `.bashrc`, ya que un error puede impedir que la sesión se inicie correctamente. [Personalización del entorno](https://docs.aws.amazon.com/cloudshell/latest/userguide/vm-specs.html)

## 5. Ten en cuenta la persistencia

En un entorno público de CloudShell, dispones de **1 GB de almacenamiento persistente por región** en tu directorio personal (`$HOME`). Los archivos que guardes allí permanecen entre sesiones, pero el almacenamiento no es una copia de seguridad permanente: AWS puede eliminar sus datos si no vuelves a iniciar CloudShell en esa región durante 120 días.

Los entornos de CloudShell conectados a una VPC funcionan de forma diferente: **no tienen almacenamiento persistente** y su directorio personal se elimina cuando el entorno caduca, se reinicia o se elimina. Consulta las [cuotas y restricciones de CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/limits.html) antes de depender de archivos guardados allí.

Con esto terminamos la serie. Ya puedes abrir CloudShell, verificar tu contexto y comenzar a trabajar con AWS CLI desde el navegador. ¿Qué comando o alias añadirías a tu configuración?

**Etiquetas:** `#aws` `#cloudshell` `#cloud` `#devops`
