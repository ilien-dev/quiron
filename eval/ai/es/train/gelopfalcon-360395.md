# RBAC en Kubernetes: Control de Acceso basado en Roles en Minikube

Kubernetes es poderoso, pero también es permisivo por defecto. Si trabajas en un cluster compartido o quieres practicar seguridad, necesitas entender RBAC: Role-Based Access Control. Aquí te mostraré cómo funciona y cómo implementarlo en Minikube.

## ¿Qué es RBAC?

RBAC es un mecanismo de seguridad que controla qué usuarios y servicios pueden hacer qué en tu cluster de Kubernetes. En lugar de dar acceso total a todos, defines roles específicos con permisos granulares.

Por ejemplo, puedes crear un role que permita solo leer pods, pero no crearlos o borrarlos. O puedes dar permisos limitados a un usuario específico en un namespace específico.

## Conceptos clave

**Role:** Define un conjunto de permisos. Por ejemplo, "leer pods" o "crear deployments".

**RoleBinding:** Vincula un Role a un usuario o grupo. Por ejemplo, "el usuario Alice tiene el role 'lector-de-pods'".

**ServiceAccount:** En Kubernetes, los pods no usan usuarios del SO. En cambio, usan ServiceAccounts.

**Namespace:** Los roles pueden ser globales (ClusterRole) o limitados a un namespace (Role).

## Habilitar RBAC en Minikube

Minikube viene con RBAC habilitado por defecto en versiones recientes, así que probablemente ya esté activo. Para verificar:

```bash
kubectl api-versions | grep rbac
```

Si ves `rbac.authorization.k8s.io`, está habilitado.

## Crear tu primer Role

Aquí creamos un Role que permite leer pods y servicios:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: lector-pods
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

Crea un archivo `role.yaml` con esto y aplícalo:

```bash
kubectl apply -f role.yaml
```

## Crear un ServiceAccount

Ahora creas un ServiceAccount que usará este role:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  namespace: default
  name: usuario-lectura
```

```bash
kubectl apply -f serviceaccount.yaml
```

## Vincular el Role al ServiceAccount

Con RoleBinding conectas el Role y el ServiceAccount:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: default
  name: vinculo-lectura
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: lector-pods
subjects:
- kind: ServiceAccount
  name: usuario-lectura
  namespace: default
```

```bash
kubectl apply -f rolebinding.yaml
```

## Probar los permisos

Ahora pruebas si funciona. Primero, obtén el token del ServiceAccount:

```bash
kubectl describe secret $(kubectl get secret -n default | grep usuario-lectura | awk '{print $1}') -n default
```

Copia el token. Luego configura un nuevo contexto para usar este ServiceAccount.

Alternativamente, crea un pod con este ServiceAccount y verifica que solo puede leer pods:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: prueba-rbac
spec:
  serviceAccountName: usuario-lectura
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
```

Entra al pod y intenta listar pods:

```bash
kubectl exec -it prueba-rbac -- sh
```

Dentro del pod:

```bash
kubectl get pods
```

Esto debería funcionar. Ahora intenta crear un pod:

```bash
kubectl run prueba --image=nginx
```

Esto debería fallar porque el ServiceAccount no tiene permiso de crear.

## Roles comunes

**viewer:** Leer la mayoría de recursos, pero no modificarlos.

**editor:** Leer y modificar, pero no borrar.

**admin:** Control total en un namespace.

**cluster-admin:** Control total en todo el cluster.

Kubernetes proporciona estos roles predefinidos, así que no siempre necesitas crearlos desde cero.

## ClusterRole vs Role

**Role:** Permisos limitados a un namespace específico.

**ClusterRole:** Permisos válidos en todo el cluster.

Usa Role para aislamiento, ClusterRole para permisos globales.

## Mejores prácticas

**Principio de mínimo privilegio:** Da solo los permisos que necesitas. Si un usuario solo necesita leer pods, no le des permisos de escritura.

**Usa namespaces:** Agrupa recursos por namespace y asigna roles por namespace. Evita dar permisos a nivel de cluster cuando sea posible.

**Auditoría:** Kubernetes registra todos los intentos de acceso. Revísalos ocasionalmente.

**ServiceAccounts por aplicación:** Cada aplicación debería tener su propio ServiceAccount. No compartas credenciales.

## Conclusión

RBAC es esencial en Kubernetes si quieres seguridad. En Minikube es fácil de probar y entender. Familiarízate con Roles, RoleBindings y ServiceAccounts, porque estos conceptos escalan directamente a clusters de producción. La seguridad no es opcional; es un requisito.
