# Novedades en Angular 8

Angular 8 llegó en mayo de 2019 con una idea clara: preparar el terreno para el futuro del framework (Ivy) sin romper las aplicaciones existentes, y al mismo tiempo mejorar la experiencia de desarrollo y el rendimiento. No es una versión de cambios dramáticos, pero sí trae mejoras que se notan en el día a día. Repasemos las más importantes.

## 1. Differential loading

Una de las novedades más prácticas. Hasta ahora, las aplicaciones Angular se compilaban a un único bundle ES5 para dar soporte a navegadores antiguos, lo que significaba que los navegadores modernos descargaban código que no necesitaban (polyfills y transformaciones innecesarias).

Con Angular 8, el CLI genera **dos bundles**:

- Uno en **ES2015+** para navegadores modernos, más pequeño y rápido.
- Uno en **ES5** para navegadores antiguos.

El navegador elige automáticamente cuál cargar mediante los atributos `type="module"` y `nomodule` en el `index.html`. El resultado es una reducción del tamaño de bundle de entre un 7 % y un 20 % en navegadores modernos, sin que tengas que hacer nada especial.

La configuración depende del `target` en `tsconfig.json` y de la lista `browserslist`.

## 2. Lazy loading con import dinámico

Antes, el lazy loading de rutas se escribía con una cadena de texto:

```typescript
{
  path: 'admin',
  loadChildren: './admin/admin.module#AdminModule'
}
```

Este formato era propio de Angular y no se podía analizar bien con herramientas estándar. Ahora se usa la sintaxis estándar de **import dinámico** de ECMAScript:

```typescript
{
  path: 'admin',
  loadChildren: () => import('./admin/admin.module').then(m => m.AdminModule)
}
```

Ventajas: mejor soporte de editores, comprobación de tipos, y compatibilidad con el estándar del lenguaje. La sintaxis antigua sigue funcionando pero queda marcada como obsoleta, y `ng update` puede migrarla automáticamente.

## 3. Vista previa de Ivy

Ivy es el nuevo motor de renderizado y compilación de Angular. En la versión 8 se ofrece como **vista previa opcional**, todavía no como valor por defecto. Se activa al crear un proyecto:

```bash
ng new mi-app --enable-ivy
```

O en un proyecto existente, con `"enableIvy": true` en `angularCompilerOptions` dentro de `tsconfig.app.json`.

Los objetivos de Ivy son:

- Bundles más pequeños.
- Compilación incremental más rápida.
- Mejor depuración.
- Mayor facilidad para extender el framework.

Como era una vista previa, no se recomendaba usarlo en producción en esta versión. Aun así, probarlo permitía detectar incompatibilidades pronto.

## 4. Web Workers en el CLI

Angular CLI 8 añade soporte para generar y empaquetar **Web Workers**, útiles para tareas pesadas que bloquearían el hilo principal (procesado de datos, cálculos, parseo).

```bash
ng generate web-worker mi-worker
```

El comando crea el archivo del worker y la configuración necesaria. Después lo usas así:

```typescript
if (typeof Worker !== 'undefined') {
  const worker = new Worker('./app.worker', { type: 'module' });
  worker.onmessage = ({ data }) => console.log('Resultado:', data);
  worker.postMessage('datos');
}
```

Mantener la interfaz fluida mientras se procesan datos pesados es ahora mucho más sencillo.

## 5. Opción `static` en `@ViewChild` y `@ContentChild`

Angular 8 hace explícito cuándo se resuelven las consultas. Ahora se debe indicar la opción `static`:

```typescript
@ViewChild('miElemento', { static: true }) elemento: ElementRef;
```

- `static: true`: la consulta se resuelve antes de la detección de cambios (disponible en `ngOnInit`). Solo válido si el elemento no está dentro de `*ngIf` o `*ngFor`.
- `static: false`: se resuelve después de la detección de cambios (disponible en `ngAfterViewInit`), y se actualiza si el elemento cambia.

Es un cambio preparatorio para Ivy, donde el comportamiento implícito anterior desaparece. Una buena noticia: `ng update` ajusta tu código automáticamente.

## 6. Mejoras en el CLI y las APIs de compilación

El CLI incorpora una **API de builders** más estable, que permite extender comandos como `ng build`, `ng test` y `ng deploy`. Esto abrió la puerta a que terceros ofrezcan despliegues con un solo comando, por ejemplo hacia Firebase, Azure o Netlify.

También se mejoraron las herramientas de actualización: `ng update` es más fiable y automatiza muchas migraciones.

## 7. Compatibilidad y dependencias

Angular 8 requiere **TypeScript 3.4** y **Node.js 10.9** o superior. Además, se actualizan las dependencias principales como RxJS 6.4. Antes de migrar, conviene revisar que tu entorno cumpla los requisitos.

Otro cambio importante: `@angular/http` desaparece en favor de `@angular/common/http`. Si todavía usas el antiguo `HttpModule`, es momento de migrar a `HttpClient`.

## 8. Cómo actualizar a Angular 8

El proceso es sencillo:

```bash
ng update @angular/cli @angular/core
```

Recomendaciones:

1. Haz un commit limpio antes de empezar.
2. Revisa la guía oficial en `update.angular.io`, que genera pasos específicos según tu versión de origen.
3. Ejecuta tus tests tras la migración.
4. Prueba la compilación de producción y comprueba el tamaño de los bundles.
5. Considera activar Ivy en una rama aparte para evaluar su compatibilidad.

## Conclusión

Angular 8 es una versión de transición inteligente. El **differential loading** mejora el rendimiento de inmediato, el **import dinámico** alinea el framework con los estándares, y **Ivy** asoma como el gran cambio que definirá las siguientes versiones. A eso se suman los Web Workers, la opción `static` en las consultas y un CLI más extensible.

Si mantienes una aplicación en Angular 7, actualizar a la 8 es un paso de bajo riesgo y alto valor. Y si estás empezando, es una buena oportunidad para entender hacia dónde se dirige el ecosistema.

¿Ya migraste a Angular 8? ¿Probaste Ivy? Cuéntame tu experiencia en los comentarios.

---

*Etiquetas sugeridas para dev.to: `#angular` `#javascript` `#typescript` `#webdev`*
