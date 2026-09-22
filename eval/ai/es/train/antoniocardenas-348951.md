# Angular 9, Ivy y más

Angular 9 ha llegado y, a diferencia de algunas versiones anteriores que se centraban en pequeñas mejoras, esta trae consigo uno de los cambios más importantes de la historia del framework: **Ivy**, el nuevo compilador y motor de renderizado, pasa a estar activado por defecto en todas las aplicaciones.

El equipo de Angular llevaba más de dos años trabajando en Ivy y, aunque para el desarrollador el cambio es casi transparente, las consecuencias son enormes: bundles más pequeños, compilación más rápida, mejores mensajes de error y una base sólida para futuras funcionalidades.

En este artículo vamos a repasar qué es Ivy, qué mejoras concretas aporta, qué otras novedades incluye Angular 9 y cómo actualizar tu proyecto.

## ¿Qué es Ivy?

Para entender Ivy conviene recordar cómo funciona Angular por dentro. Los componentes que escribimos (clases con decoradores y plantillas HTML) no se ejecutan tal cual en el navegador. El compilador de Angular transforma las plantillas en código JavaScript que crea y actualiza el DOM.

Hasta Angular 8, ese trabajo lo hacía **View Engine**. Ivy es su sustituto: una reescritura completa del compilador y del runtime de renderizado.

La principal diferencia de diseño está en dos principios:

### 1. Localidad

Con View Engine, para compilar un componente el compilador necesitaba información global de toda la aplicación: los módulos, las dependencias y los componentes que se usaban. Eso generaba archivos auxiliares (como los `.ngfactory.js`) y obligaba a recompilar mucho más de lo necesario.

Ivy sigue el principio de **localidad**: cada componente se compila usando solo la información que tiene él mismo, es decir, su decorador y su plantilla. El resultado se añade como propiedades estáticas de la propia clase:

```typescript
export class SaludoComponent {
  nombre = 'mundo';

  static ɵcmp = defineComponent({
    type: SaludoComponent,
    selectors: [['app-saludo']],
    template: function (rf, ctx) {
      if (rf & 1) {
        elementStart(0, 'h1');
        text(1);
        elementEnd();
      }
      if (rf & 2) {
        advance(1);
        textInterpolate1('Hola ', ctx.nombre, '');
      }
    },
  });
}
```

(Esto es una versión simplificada de lo que genera el compilador; nunca tendrás que escribirlo a mano).

Gracias a la localidad, la compilación es más rápida y más predecible: si cambias un componente, solo hay que recompilar ese componente.

### 2. Tree-shaking

View Engine generaba estructuras de datos que luego un intérprete recorría en tiempo de ejecución. Ese intérprete tenía que incluir soporte para todas las funcionalidades de Angular, se usaran o no.

Ivy, en cambio, genera instrucciones que llaman directamente a funciones del runtime (`elementStart`, `text`, `listener`...). Si tu aplicación no usa una funcionalidad determinada, la función correspondiente nunca se importa, y las herramientas de tree-shaking como Terser pueden eliminarla del bundle final.

En otras palabras: **pagas solo por lo que usas**.

## Las mejoras en la práctica

### Bundles más pequeños

Según los datos publicados por el equipo de Angular, las aplicaciones pequeñas pueden ver reducciones de tamaño de hasta un 30-40%, gracias a que se elimina el código del framework que no se utiliza. Las aplicaciones grandes se benefician menos en términos relativos (entre un 2% y un 25%), porque su propio código pesa más que el del framework, pero la mejora sigue ahí.

### Compilación AOT por defecto

Hasta ahora, lo habitual era usar compilación **JIT** (*Just in Time*) en desarrollo y **AOT** (*Ahead of Time*) en producción. JIT era más rápido para compilar, pero significaba que algunos errores de plantilla solo aparecían al hacer el build de producción, con la consiguiente sorpresa.

Con Ivy, AOT es tan rápido que pasa a ser la opción por defecto también en desarrollo. Esto significa que el entorno de desarrollo se comporta igual que producción, y los errores aparecen antes.

### Mejor comprobación de tipos en plantillas

Angular 9 introduce un modo de comprobación de tipos más estricto para las plantillas. Se activa en `tsconfig.json`:

```json
{
  "angularCompilerOptions": {
    "strictTemplates": true
  }
}
```

Con esta opción, el compilador detecta errores como pasar un `string` a un `@Input()` que espera un `number`, o acceder a una propiedad que no existe en un objeto dentro de un `*ngFor`. Errores que antes solo descubrías en tiempo de ejecución.

### Mensajes de error más claros

Los errores de compilación ahora indican con más precisión dónde está el problema, incluyendo el archivo, la línea y un fragmento de la plantilla. Por ejemplo:

```
src/app/app.component.html:3:12 - error NG8002: Can't bind to 'titulo'
since it isn't a known property of 'app-cabecera'.
```

Parece un detalle menor, pero en el día a día se nota mucho.

### Depuración más sencilla

Ivy expone un objeto global `ng` en modo desarrollo que puedes usar desde la consola del navegador:

```javascript
// Selecciona un elemento en las DevTools y luego:
const componente = ng.getComponent($0);
componente.nombre = 'Angular';
ng.applyChanges($0);
```

Puedes inspeccionar el estado de cualquier componente, modificarlo y forzar la detección de cambios sin tocar el código. Muy útil para diagnosticar problemas.

### Estilos más predecibles

Ivy define un orden de precedencia claro cuando se combinan `[style]`, `[class]`, `[ngStyle]`, `[ngClass]` y los host bindings. Antes, el último enlace evaluado ganaba, lo que podía dar resultados inesperados. Ahora las reglas son consistentes, y además se admiten variables CSS en los bindings de estilo:

```html
<div [style.--color-principal]="color"></div>
```

## Otras novedades de Angular 9

Más allá de Ivy, esta versión trae algunas mejoras interesantes.

### `providedIn: 'any'` y `'platform'`

El decorador `@Injectable` admitía `providedIn: 'root'`. Ahora hay dos opciones nuevas:

- **`'platform'`**: el servicio es un singleton compartido por todas las aplicaciones Angular de la página (útil en escenarios con Angular Elements o microfrontends).
- **`'any'`**: se crea una instancia distinta por cada módulo cargado de forma diferida (*lazy*), y una compartida para los módulos cargados de forma normal.

```typescript
@Injectable({ providedIn: 'any' })
export class ConfiguracionService {}
```

### `TestBed.inject`

En las pruebas, `TestBed.get()` devolvía `any`, lo que obligaba a hacer castings. Ahora se reemplaza por `TestBed.inject()`, que está correctamente tipado:

```typescript
// Antes
const servicio = TestBed.get(UsuarioService) as UsuarioService;

// Ahora
const servicio = TestBed.inject(UsuarioService);
```

### Component harnesses

Angular CDK introduce los **component harnesses**, una API para interactuar con los componentes en las pruebas sin depender de detalles internos del DOM. Angular Material ya incluye harnesses para sus componentes:

```typescript
const boton = await loader.getHarness(MatButtonHarness);
await boton.click();
```

Si el equipo de Material cambia la estructura interna del botón, tus pruebas seguirán funcionando.

### Nuevos componentes oficiales

Se añaden dos paquetes muy esperados: `@angular/youtube-player` y `@angular/google-maps`, que envuelven las APIs de YouTube y Google Maps como componentes de Angular.

### Internacionalización

La internacionalización se ha rediseñado para funcionar mejor con Ivy. Se introduce el paquete `@angular/localize` y la función `$localize`, que permite marcar textos traducibles también desde el código TypeScript, no solo en las plantillas. Además, el build genera todas las versiones idiomáticas de forma mucho más rápida, ya que la traducción se hace después de compilar.

### TypeScript 3.7

Angular 9 soporta TypeScript 3.6 y 3.7, lo que significa que ya puedes usar **optional chaining** y **nullish coalescing** en tu código:

```typescript
const ciudad = usuario?.direccion?.ciudad ?? 'Desconocida';
```

## Cómo actualizar

Como siempre, la forma recomendada de actualizar es con `ng update`. Primero, asegúrate de estar en la última versión de Angular 8:

```bash
ng update @angular/core@8 @angular/cli@8
```

Y después:

```bash
ng update @angular/core @angular/cli
```

El CLI aplica migraciones automáticas que modifican tu código para adaptarlo a los cambios (por ejemplo, añade decoradores `@Injectable` o `@Directive` donde falten, o reemplaza `TestBed.get`). Consulta también la guía oficial en update.angular.io, donde puedes seleccionar tu versión de origen y destino para ver los pasos concretos.

### ¿Y si algo falla?

Algunas librerías de terceros pueden no ser compatibles con Ivy todavía. Angular 9 incluye un **compilador de compatibilidad** (`ngcc`) que convierte automáticamente las librerías compiladas con View Engine al formato de Ivy, así que en la mayoría de los casos funcionarán sin problemas.

Si aun así encuentras algún error, puedes desactivar Ivy temporalmente en `tsconfig.app.json`:

```json
{
  "angularCompilerOptions": {
    "enableIvy": false
  }
}
```

Es una buena vía de escape mientras investigas el problema o esperas a que la librería se actualice, pero no conviene quedarse ahí mucho tiempo: View Engine está marcado como obsoleto y desaparecerá en futuras versiones.

## ¿Qué viene después?

Ivy no es solo una mejora de rendimiento: es la base sobre la que el equipo de Angular construirá las próximas funcionalidades. Algunas de las que se han mencionado son la posibilidad de tener componentes sin `NgModule`, carga diferida de componentes individuales de forma más sencilla, metaprogramación con componentes de orden superior y mejoras en la detección de cambios.

## Conclusión

Angular 9 es una de esas versiones que marcan un antes y un después. Con Ivy activado por defecto, las aplicaciones son más pequeñas, compilan más rápido, detectan más errores en tiempo de compilación y son más fáciles de depurar. Y todo ello sin que tengas que reescribir tu código.

Si tienes una aplicación en Angular 8, la actualización debería ser bastante sencilla gracias a `ng update` y a las migraciones automáticas. Te recomiendo hacerla cuanto antes: los beneficios se notan desde el primer día, y te dejará preparado para todo lo que está por venir.

¿Ya has migrado tu proyecto? Cuéntame en los comentarios cómo te ha ido y si has notado diferencias en el tamaño de tus bundles.
