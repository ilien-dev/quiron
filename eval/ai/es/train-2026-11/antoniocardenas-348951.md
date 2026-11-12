Angular 9 fue una de las versiones más esperadas del framework. Con ella, el equipo de Angular cumplió por fin una promesa de años: **Ivy**, el nuevo compilador y motor de renderizado, pasó a ser el predeterminado para todas las aplicaciones.

Lo interesante es que, para la mayoría de los proyectos, la actualización llega casi sin dolor. No hay que reescribir componentes ni aprender una nueva sintaxis. Aun así, lo que cambia por debajo es enorme y abre la puerta a muchas mejoras futuras.

En este post repaso qué es Ivy, por qué importa y qué otras novedades trae Angular 9.

## ¿Qué es Ivy?

Desde Angular 4, el framework usaba un motor llamado **View Engine**. Este motor tomaba tus plantillas HTML y decoradores, y generaba código JavaScript que el navegador ejecutaba para crear y actualizar el DOM.

View Engine funcionaba, pero tenía algunas limitaciones:

- El código generado era bastante voluminoso.
- El *tree-shaking* (eliminar código no usado) era limitado, porque el runtime necesitaba mucha información global.
- Compilar un componente requería conocer detalles de todo el módulo, lo que hacía las compilaciones incrementales más lentas.
- Depurar era complicado: los errores apuntaban a código generado difícil de entender.

**Ivy** es una reescritura completa de ese motor, basada en dos ideas principales.

### 1. Localidad

Con Ivy, cada componente se compila de forma independiente. El compilador solo necesita mirar el propio componente y sus dependencias directas, no todo el `NgModule`. Esto se traduce en compilaciones más rápidas y en un modelo mental más sencillo.

### 2. Instrucciones que se pueden eliminar

En lugar de generar estructuras de datos que un intérprete recorre, Ivy convierte cada plantilla en una serie de **instrucciones** (funciones) que crean y actualizan el DOM directamente. Si tu aplicación no usa cierta característica, la instrucción correspondiente nunca se importa y el *bundler* puede eliminarla.

Por ejemplo, una plantilla como esta:

```html
<h1>Hola, {{ nombre }}</h1>
```

se compila, de manera simplificada, a algo parecido a:

```ts
function AppComponent_Template(rf, ctx) {
  if (rf & 1) {
    ɵɵelementStart(0, 'h1');
    ɵɵtext(1);
    ɵɵelementEnd();
  }
  if (rf & 2) {
    ɵɵadvance(1);
    ɵɵtextInterpolate1('Hola, ', ctx.nombre, '');
  }
}
```

No necesitas escribir nunca este código, pero entenderlo ayuda a ver por qué Ivy es más eficiente: solo se incluye lo que realmente usas.

## Bundles más pequeños

Uno de los beneficios más visibles de Ivy es la reducción del tamaño de los *bundles*. Según los datos publicados por el equipo de Angular:

- Las **aplicaciones pequeñas** ven las mejoras más notables, con reducciones de hasta un 30 % en algunos casos.
- Las **aplicaciones medianas** obtienen mejoras moderadas.
- Las **aplicaciones grandes** se benefician sobre todo cuando usan *lazy loading*, ya que cada chunk incluye menos código del framework.

El resultado depende mucho de cada proyecto, así que lo mejor es medirlo tú mismo con `source-map-explorer` o `webpack-bundle-analyzer` antes y después de actualizar.

## AOT por defecto

Antes de Angular 9, la compilación *Ahead-of-Time* (AOT) solía reservarse para producción porque era más lenta. En desarrollo se usaba JIT, y eso provocaba una situación incómoda: había errores que solo aparecían al hacer el build de producción.

Gracias a Ivy, la compilación AOT es ahora lo bastante rápida como para activarla también en desarrollo. Al crear un proyecto nuevo, el `angular.json` incluye:

```json
"options": {
  "aot": true
}
```

Esto significa que lo que ves en desarrollo se parece mucho más a lo que se despliega en producción. Adiós a las sorpresas de última hora.

## Mejor verificación de tipos en las plantillas

Angular 9 mejora mucho la forma en que el compilador revisa los tipos dentro de las plantillas. Hay tres niveles:

- **Básico**: el comportamiento por defecto, que verifica lo esencial.
- **`fullTemplateTypeCheck`**: revisa con más profundidad, incluidas las vistas embebidas como `*ngIf` y `*ngFor`.
- **`strictTemplates`**: el modo más estricto, que aplica las mismas reglas de tipos que TypeScript.

Para activarlo, en `tsconfig.json`:

```json
"angularCompilerOptions": {
  "strictTemplates": true
}
```

Con `strictTemplates`, si pasas un `string` a un `@Input()` que espera un `number`, el compilador te avisará. Lo mismo con propiedades que no existen o con tipos de eventos incorrectos. Al principio puede generar bastantes errores en un proyecto existente, pero a largo plazo evita muchos bugs.

## Mensajes de error más claros

Los mensajes de error de Angular también mejoran. En lugar de un error genérico, el compilador ahora indica el archivo, la línea y el fragmento de plantilla donde está el problema:

```
ERROR in src/app/app.component.html:3:12 - error TS2339:
Property 'nombr' does not exist on type 'AppComponent'.

3   <h1>Hola, {{ nombr }}</h1>
             ~~~~~~~~~
```

Es un cambio pequeño, pero ahorra mucho tiempo en el día a día.

## Depuración más sencilla

Ivy añade un conjunto de utilidades globales disponibles en modo desarrollo a través del objeto `ng`. Desde la consola del navegador puedes inspeccionar componentes directamente:

```js
// Selecciona un elemento en el inspector y luego:
const comp = ng.getComponent($0);

// Modifica su estado
comp.nombre = 'Mundo';

// Fuerza la detección de cambios
ng.applyChanges($0);
```

Otras funciones útiles son `ng.getContext`, `ng.getInjector`, `ng.getListeners` y `ng.getOwningComponent`. Para quien está aprendiendo Angular, esto hace mucho más fácil entender qué está pasando.

Además, los *stack traces* son más legibles, porque el código generado por Ivy está más cerca de tus plantillas originales.

## Pruebas más rápidas

Con Ivy, `TestBed` fue reimplementado y ya no recompila todos los componentes entre cada test, salvo que sobrescribas algo manualmente. El equipo de Angular reportó mejoras de alrededor de un **40 %** en la velocidad de ejecución de las pruebas.

También llega una nueva API con tipado seguro para obtener dependencias:

```ts
// Antes
const service = TestBed.get(MiServicio); // devuelve any

// Angular 9
const service = TestBed.inject(MiServicio); // devuelve MiServicio
```

`TestBed.get` queda obsoleto, así que conviene migrar a `TestBed.inject`.

## Internacionalización con `$localize`

Angular 9 introduce el paquete `@angular/localize`, que añade una función global `$localize` para marcar textos traducibles. Se integra con la sintaxis `i18n` de las plantillas y además permite marcar mensajes desde el propio código TypeScript:

```ts
const saludo = $localize`:@@saludo:Hola, bienvenido`;
```

Para añadirlo al proyecto:

```bash
ng add @angular/localize
```

Una de las ventajas de este nuevo sistema es que las traducciones se aplican **después** de la compilación, por lo que generar varias versiones del idioma es mucho más rápido.

## Nuevas opciones para `providedIn`

El decorador `@Injectable` admite ahora dos valores nuevos en `providedIn`:

- **`'platform'`**: el servicio se comparte entre todas las aplicaciones de la página, útil en escenarios con varias apps Angular o *micro frontends*.
- **`'any'`**: cada módulo cargado de forma *lazy* recibe su propia instancia del servicio.

```ts
@Injectable({ providedIn: 'any' })
export class ConfigService {}
```

## Adiós a `entryComponents`

Con View Engine, los componentes creados dinámicamente (por ejemplo, los diálogos de Angular Material) debían declararse en `entryComponents`. Con Ivy esto ya no es necesario: el compilador detecta los componentes de forma automática. La propiedad sigue funcionando, pero en versiones futuras quedará obsoleta.

## Novedades en Angular Components

El repositorio de componentes también trae cosas nuevas:

- **`@angular/youtube-player`**: un componente para incrustar vídeos de YouTube.
- **`@angular/google-maps`**: componentes para integrar Google Maps de forma sencilla.
- **Component harnesses**: una API para escribir pruebas que interactúan con componentes de Material sin depender de los detalles de su DOM interno.

## Soporte para TypeScript 3.6 y 3.7

Angular 9 es compatible con TypeScript 3.6 y 3.7, lo que permite usar dos características muy esperadas:

```ts
// Optional chaining
const ciudad = usuario?.direccion?.ciudad;

// Nullish coalescing
const limite = config.limite ?? 10;
```

## Cómo actualizar

La forma recomendada es usar `ng update`. Primero actualiza a la última versión de Angular 8 y después a la 9:

```bash
ng update @angular/cli@8 @angular/core@8
ng update @angular/cli @angular/core
```

El CLI aplica varias migraciones automáticas, entre ellas:

- Añadir `@Directive()` a las clases base sin decorador que usan características de Angular.
- Añadir el tipo genérico a `ModuleWithProviders`.
- Migrar algunos patrones antiguos que ya no son compatibles con Ivy.

Para las librerías de terceros que todavía están compiladas con View Engine, Angular incluye **ngcc** (*Angular Compatibility Compiler*), que las convierte automáticamente para que funcionen con Ivy. Se ejecuta tras la instalación de dependencias, así que normalmente no tienes que hacer nada.

Si encuentras un problema grave, puedes desactivar Ivy temporalmente en `tsconfig.json`:

```json
"angularCompilerOptions": {
  "enableIvy": false
}
```

Eso sí, tómalo como una solución temporal: el futuro de Angular pasa por Ivy.

## Conclusión

Angular 9 no trae grandes cambios en la API que usas a diario, pero sí una base completamente nueva. Ivy ofrece *bundles* más pequeños, compilaciones más rápidas, mejores errores, depuración más cómoda y pruebas más ágiles.

Lo más importante es lo que viene después: con Ivy, el equipo de Angular tiene un motor mucho más flexible sobre el que construir nuevas características en las próximas versiones.

Si todavía no has actualizado, es un buen momento para hacerlo. Y si ya lo hiciste, cuéntame en los comentarios qué cambios notaste en tu proyecto. 🚀
