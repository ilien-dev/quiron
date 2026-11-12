# RBAC con Kubernetes en Minikube

Cuando empiezas con Kubernetes, es tentador usar siempre el usuario administrador que crea el clúster. Funciona, pero en cuanto varias personas o aplicaciones comparten un clúster, ese atajo se convierte en un problema: cualquiera con acceso puede borrar namespaces, leer secretos o modificar despliegues ajenos.

RBAC (*Role-Based Access Control*) es el mecanismo que Kubernetes usa para decidir qué puede hacer cada identidad. En este post lo montaremos en local con Minikube: crearemos una identidad de solo lectura para un namespace concreto y comprobaremos que los permisos se cumplen.

## Requisitos

- Minikube y kubectl instalados.
- Un driver de contenedores disponible (Docker, por ejemplo).
- Conocimientos básicos de YAML y de `kubectl`.

## Conceptos clave

RBAC se basa en cuatro recursos:

- **Role**: un conjunto de permisos (verbos sobre recursos) limitado a un namespace.
- **ClusterRole**: lo mismo, pero válido en todo el clúster o reutilizable entre namespaces.
- **RoleBinding**: asocia un Role o un ClusterRole a un sujeto dentro de un namespace.
- **ClusterRoleBinding**: asocia un ClusterRole a un sujeto en todo el clúster.

Los sujetos pueden ser usuarios, grupos o *ServiceAccounts*. Para una aplicación que corre dentro del clúster, lo habitual es usar ServiceAccounts.

## 1. Arrancar Minikube

```bash
minikube start --driver=docker
kubectl get nodes
```

Si el nodo aparece como `Ready`, el clúster está listo.

## 2. Crear un namespace y una ServiceAccount

Aislamos el trabajo en un namespace propio:

```bash
kubectl create namespace dev-team
kubectl create serviceaccount ci-reader -n dev-team
```

Esta ServiceAccount será la identidad que usaremos. Por defecto no tiene permisos para casi nada, que es justo el punto de partida que queremos.

## 3. Definir un Role de solo lectura

Creamos `role-reader.yaml`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: dev-team
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log", "services"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch"]
```

Fíjate en que no hemos usado comodines (`*`). Cuanto más específicas son las reglas, menor es la superficie de un posible fallo.

Aplicamos el manifiesto:

```bash
kubectl apply -f role-reader.yaml
```

## 4. Vincular el Role a la ServiceAccount

Guardamos el binding en `rolebinding.yaml`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ci-reader-binding
  namespace: dev-team
subjects:
  - kind: ServiceAccount
    name: ci-reader
    namespace: dev-team
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f rolebinding.yaml
```

Un detalle que suele generar confusión: `roleRef` es inmutable. Si necesitas cambiarlo, hay que borrar y recrear el binding.

## 5. Comprobar los permisos

Esta es la parte más útil. `kubectl auth can-i` permite simular peticiones como si las hiciera otra identidad, usando `--as`:

```bash
kubectl auth can-i list pods -n dev-team \
  --as=system:serviceaccount:dev-team:ci-reader
# yes

kubectl auth can-i delete pods -n dev-team \
  --as=system:serviceaccount:dev-team:ci-reader
# no

kubectl auth can-i get secrets -n dev-team \
  --as=system:serviceaccount:dev-team:ci-reader
# no

kubectl auth can-i list pods -n default \
  --as=system:serviceaccount:dev-team:ci-reader
# no
```

Las dos últimas líneas son las importantes: el permiso no se extiende a otros namespaces ni a recursos sensibles como los secretos.

Para una prueba real, podemos generar un token temporal y usarlo en un kubeconfig separado:

```bash
kubectl create token ci-reader -n dev-team --duration=1h
```

Con ese token se puede construir un kubeconfig mínimo y comprobar el acceso desde la perspectiva de la aplicación, en lugar de la del administrador.

## 6. Cuándo usar ClusterRole

Si necesitas el mismo conjunto de permisos en varios namespaces, define un ClusterRole y reutilízalo con RoleBindings en cada uno. Si la identidad necesita acceso transversal (por ejemplo, un agente de monitorización que lee nodos), usa un ClusterRoleBinding. Este último merece más cuidado, porque concede permisos a todo el clúster.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list"]
```

## 7. Limpieza

```bash
kubectl delete namespace dev-team
kubectl delete clusterrole node-reader --ignore-not-found
minikube delete
```

Borrar el namespace elimina la ServiceAccount, el Role y el RoleBinding asociados. El ClusterRole es un recurso de ámbito global, así que hay que borrarlo aparte. Si no quieres conservar nada más, `minikube delete` cierra el clúster completo.

## Buenas prácticas

- **Principio de mínimo privilegio**: empieza sin permisos y añade solo lo necesario.
- **Evita comodines** en `verbs` y `resources` salvo que tengas un motivo claro.
- **Usa una ServiceAccount por aplicación**, no compartas una entre servicios.
- **Revisa periódicamente** qué puede hacer cada identidad con `kubectl auth can-i --list --as=...`.
- **Desactiva el montaje automático del token** (`automountServiceAccountToken: false`) en pods que no necesitan hablar con la API.

## Conclusión

RBAC no es complicado una vez entiendes la relación entre sujetos, roles y bindings. Minikube permite experimentar sin riesgo, y `kubectl auth can-i` ofrece una forma rápida de verificar que la configuración hace exactamente lo que pretendes. Probar los permisos negativos, es decir, lo que la identidad *no* puede hacer, es tan importante como probar los positivos.

En el próximo post veremos cómo combinar RBAC con NetworkPolicies para reforzar el aislamiento dentro del namespace.
