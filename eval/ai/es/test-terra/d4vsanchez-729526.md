# ¿Qué hay de nuevo en Next.js?

Si llevas un tiempo trabajando con Next.js, probablemente conoces la sensación: acabas de entender cómo funciona la caché y aparece una nueva versión con otra forma de configurarla. La buena noticia es que las últimas actualizaciones apuntan en una dirección más clara: hacer explícitas las decisiones de caché, acelerar la navegación y reducir el trabajo que hacemos durante el desarrollo.

A noviembre de 2026, la versión más reciente de la familia es **Next.js 16.4**, publicada en octubre. Veamos qué trae y cómo se relaciona con los cambios que han llegado a lo largo de Next.js 16. [Anuncio oficial de Next.js 16.4](https://nextjs.org/blog/next-16-4).

## Cache Components: tú decides qué guardar

Uno de los cambios más relevantes de Next.js 16 es el modelo de **Cache Components**. La idea es sencilla: puedes indicar qué partes de tu aplicación deben almacenarse en caché mediante la directiva `use cache`.

Esto resulta útil en páginas que combinan contenido compartido con información específica de cada usuario. Imagina una tienda: la descripción de un producto puede permanecer en caché, mientras que el carrito debe reflejar la sesión actual.

En un proyecto existente puedes activar el modelo en `next.config.ts`:

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
}

export default nextConfig
```

La configuración incluye *Partial Prefetching*, que permite preparar partes de una ruta antes de que el usuario navegue hacia ella. Los proyectos nuevos creados con `create-next-app` ya habilitan Cache Components por defecto desde Next.js 16.4; en aplicaciones existentes, conviene planificar la migración y revisar el comportamiento de las rutas. [Más información sobre Cache Components](https://nextjs.org/blog/next-16-4).

Aquí tienes una función que guarda un catálogo en caché y define su duración:

```ts
import { cacheLife } from 'next/cache'

export async function obtenerProductos() {
  'use cache'

  cacheLife('hours')

  const respuesta = await fetch('https://ejemplo.com/api/productos')

  if (!respuesta.ok) {
    throw new Error('No se pudieron cargar los productos')
  }

  return respuesta.json()
}
```

La ventaja es que la política queda cerca del código al que afecta. Aun así, guardar datos en caché implica decidir cuándo deben actualizarse: un catálogo puede tolerar cierto retraso; el saldo de una cuenta, quizá no. Para invalidar contenido cuando cambia, Next.js ofrece APIs como `revalidateTag` y `updateTag`. [Guía de revalidación](https://nextjs.org/docs/app/getting-started/revalidating).

## Páginas rápidas con contenido dinámico

Cache Components también permite combinar una estructura prerenderizada con contenido que se obtiene durante la solicitud. Mediante React Suspense, una página puede mostrar primero una parte disponible y completar después otra que necesita consultar datos.

Por ejemplo, un artículo puede servirse como contenido preparado de antemano, mientras se carga el avatar de la persona que ha iniciado sesión. Esto ayuda a mejorar la percepción de velocidad sin renunciar a la personalización.

La clave está en elegir bien los límites de Suspense. Si toda la página espera a una consulta lenta, el usuario seguirá esperando. Si divides la interfaz en secciones independientes, puedes mostrar antes lo que ya está listo.

## Más control sobre lo estático

Next.js 16.4 incorpora `ensureStatic`, una opción para proteger las rutas que deben seguir siendo estáticas. Por ejemplo:

```tsx
// app/blog/page.tsx

export const ensureStatic = 'navigation'

export default function BlogPage() {
  return <h1>Mi blog</h1>
}
```

Con el valor `navigation`, la compilación falla si se introduce contenido dinámico que impida cumplir esa garantía. También existen los niveles `shell` y `prefetch`, para aplicar controles más específicos.

Esto puede ser útil en un blog o una página de marketing: si alguien añade una dependencia que requiere renderizado en cada solicitud, el problema aparece durante la compilación, antes de llegar a producción. [Detalles de `ensureStatic`](https://nextjs.org/blog/next-16-4).

## Navegaciones más fluidas

¿Alguna vez hiciste clic en un enlace y dudaste de si había funcionado? Next.js ha dedicado varias mejoras a reducir esa espera.

Next.js 16.3 presentó **Instant Navigations**, un conjunto de herramientas para inspeccionar y mejorar las transiciones entre rutas. Incluye información sobre navegaciones lentas, un inspector de la estructura de carga y herramientas para probar que futuras modificaciones no introduzcan regresiones.

El precargado también es más inteligente: prepara contenido antes del clic y puede reutilizar partes compartidas de las rutas. Eso sí, precargar tiene un costo. Si una página muestra cientos de enlaces, descargar demasiada información que quizá nadie consulte puede aumentar el tráfico y el trabajo del servidor.

La recomendación es medir: revisa tanto la rapidez percibida como el número de solicitudes y el volumen de datos. [Novedades de navegación en Next.js 16.3](https://nextjs.org/blog/next-16-3).

## Turbopack sigue ganando terreno

Turbopack es el empaquetador predeterminado desde Next.js 16. Las versiones posteriores han seguido mejorando la velocidad y el consumo de recursos, tanto en desarrollo como durante la compilación.

Por ejemplo, Next.js 16.3 incorporó caché de compilación en disco para reutilizar resultados que no han cambiado. También mejoró la gestión de memoria del servidor de desarrollo. Los resultados dependen del proyecto, pero pueden ser especialmente relevantes en aplicaciones grandes.

Next.js 16.4 añade mejoras adicionales, como una menor caché en disco y paquetes de producción más pequeños. Si tu proyecto depende de una configuración específica de webpack, puedes seguir utilizándolo mientras evalúas la migración:

```bash
next dev --webpack
next build --webpack
```

Antes de cambiar el proceso de compilación de un proyecto complejo, compara tiempos y verifica que tus plugins y transformaciones funcionen como esperas. [Cambios de Turbopack en Next.js 16](https://nextjs.org/blog/next-16).

## `middleware.ts` pasa a ser `proxy.ts`

Otro cambio que encontrarás al actualizar es la convención `proxy.ts`, que sustituye progresivamente a `middleware.ts` para dejar más clara su función como punto de entrada para interceptar solicitudes.

Un ejemplo de redirección:

```ts
import { NextResponse, type NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  return NextResponse.redirect(new URL('/inicio', request.url))
}
```

La lógica puede resultar familiar, pero revisa el entorno de ejecución antes de migrar: `proxy.ts` utiliza Node.js. La convención anterior sigue disponible para casos que necesitan Edge Runtime, aunque está obsoleta. [Guía de actualización a Next.js 16](https://nextjs.org/docs/app/guides/upgrading/version-16).

## Mejoras para depurar y trabajar con agentes

Next.js también ha ampliado sus herramientas de diagnóstico. DevTools MCP permite que agentes compatibles accedan a información contextual de la aplicación, como errores, rutas y registros. Esto puede ayudar a investigar un fallo sin copiar manualmente cada mensaje entre herramientas.

Además, Next.js 16.4 presenta `next upgrade --agent`, pensado para proporcionar orientación específica de versión durante una actualización asistida. Es una ayuda para recorrer el proceso, pero sigue siendo importante revisar los cambios generados y ejecutar las pruebas del proyecto. [Anuncio de Next.js 16.4](https://nextjs.org/blog/next-16-4).

## ¿Cómo actualizar?

Si quieres probar la versión más reciente, la guía oficial ofrece un codemod para automatizar parte de la migración:

```bash
npx @next/codemod@canary upgrade latest
```

Después, revisa especialmente las APIs asíncronas, la configuración de caché, las dependencias de webpack y las rutas que usan middleware. Ejecuta las pruebas, genera una compilación de producción y comprueba los flujos críticos.

Next.js 16.4 apuesta por aplicaciones rápidas con decisiones de renderizado y caché más explícitas. No hace falta adoptar cada novedad de inmediato: empieza por medir tu aplicación, identifica sus cuellos de botella y prueba los cambios donde puedan aportar más valor.

**¿Qué novedad te interesa probar primero: Cache Components, Instant Navigations o las mejoras de Turbopack?**
