# Novedades en Angular 8

Angular 8 llegó con una serie de cambios que, aunque no son tan disruptivos como los de versiones anteriores (recordemos el salto de AngularJS a Angular 2), sí introducen mejoras importantes en rendimiento, tooling y preparación para el futuro del framework, especialmente de cara a Ivy. En este post repasamos las novedades más relevantes de esta versión.

## Differential Loading

Una de las características más celebradas de Angular 8 es el **differential loading** (carga diferencial). Hasta ahora, Angular CLI generaba un único bundle de JavaScript compatible con navegadores antiguos, usando sintaxis ES5. Esto significaba que incluso los navegadores modernos, capaces de ejecutar ES2015+ de forma nativa, tenían que descargar y procesar código transpilado y con polyfills innecesarios.

Con Angular 8, el CLI genera automáticamente dos bundles:

- Uno en formato ES2015, más ligero y rápido de ejecutar, para navegadores modernos.
- Otro en ES5, con los polyfills necesarios, para navegadores más antiguos.

El navegador elige automáticamente cuál cargar gracias a los atributos `type="module"` y `nomodule` en las etiquetas `<script>`. El resultado práctico es una reducción notable en el tamaño de los bundles para la mayoría de usuarios, sin necesidad de configuración adicional.

## Soporte para Web Workers

Angular 8 añade soporte de primera clase para **Web Workers** a través del CLI. Ahora se puede generar un worker con:

```bash
ng generate web-worker my-worker
```

Esto crea un archivo `my-worker.worker.ts` y configura automáticamente el `tsconfig` y el `angular.json` necesarios para que Webpack lo empaquete correctamente. Los Web Workers son útiles cuando tenemos tareas computacionalmente costosas (procesamiento de datos, cálculos complejos) que no queremos que bloqueen el hilo principal y, por tanto, la interfaz de usuario.

## Dynamic imports para lazy loading

Antes de Angular 8, el lazy loading de módulos se configuraba usando una sintaxis de string especial en las rutas:

```ts
{
  path: 'admin',
  loadChildren: './admin/admin.module#AdminModule'
}
```

A partir de Angular 8, se recomienda usar la sintaxis de **dynamic import** estándar de JavaScript/TypeScript:

```ts
{
  path: 'admin',
  loadChildren: () => import('./admin/admin.module').then(m => m.AdminModule)
}
```

Esta forma es más segura porque el compilador de TypeScript puede verificar los tipos y detectar errores en tiempo de compilación, algo que la sintaxis de string no permitía. El CLI incluye además un *schematic* para migrar automáticamente el código antiguo al nuevo formato.

## Vista previa de Ivy

Ivy es el nuevo motor de renderizado y compilación de Angular, diseñado para generar bundles más pequeños, mejorar los tiempos de compilación y facilitar el *tree-shaking*. En Angular 8 se incluye como **opt-in**, es decir, no viene activado por defecto, pero se puede probar añadiendo la siguiente configuración al `tsconfig.json`:

```json
{
  "angularCompilerOptions": {
    "enableIvy": true
  }
}
```

Es importante destacar que en esta versión Ivy todavía se considera experimental y no se recomienda para proyectos en producción, pero es una buena oportunidad para empezar a familiarizarse con él antes de que se convierta en el motor por defecto en Angular 9.

## Builder API para el CLI

Angular 8 estabiliza la **Builder API**, que permite personalizar y extender el comportamiento de comandos del CLI como `build`, `serve` o `test`. Esto abre la puerta a que herramientas de terceros (como Angular Universal, NativeScript o incluso Bazel) se integren de forma más limpia con el ecosistema de Angular CLI, sin necesidad de recurrir a hacks o configuraciones manuales de Webpack.

## Mejoras en `@angular/service-worker`

El soporte de service workers para Progressive Web Apps también recibe mejoras, incluyendo una mejor gestión de la navegación y de las estrategias de cacheo, lo que se traduce en aplicaciones offline más confiables.

## Deprecaciones a tener en cuenta

Como es habitual, cada versión mayor trae consigo una lista de deprecaciones que conviene revisar:

- El módulo `@angular/http` queda definitivamente deprecado en favor de `@angular/common/http`, que se introdujo hace ya varias versiones.
- Algunas APIs de `ReflectiveInjector` quedan marcadas como obsoletas en favor de `StaticInjector`.
- Se recomienda actualizar los `entryComponents` y otras configuraciones que serán relevantes de cara a la migración a Ivy.

## Actualizando a Angular 8

Como siempre, la forma recomendada de actualizar es usar la herramienta oficial:

```bash
ng update @angular/cli @angular/core
```

El CLI se encarga de ejecutar los *schematics* necesarios para migrar automáticamente buena parte del código, incluyendo la migración de lazy loading a dynamic imports mencionada antes. Aun así, es recomendable revisar el [Angular Update Guide](https://update.angular.io/) antes de actualizar un proyecto grande, ya que puede haber dependencias de terceros que todavía no sean compatibles con TypeScript 3.4, requisito mínimo de esta versión.

## Conclusión

Angular 8 no es una versión que rompa con lo anterior, sino más bien una que consolida el camino hacia Ivy y mejora sustancialmente el rendimiento de las aplicaciones gracias al differential loading. Si tienes un proyecto en Angular 7, la actualización debería ser relativamente sencilla usando `ng update`, y vale la pena aprovechar, aunque sea de forma experimental, las mejoras que trae esta versión antes de que lleguen los cambios más grandes en Angular 9.
