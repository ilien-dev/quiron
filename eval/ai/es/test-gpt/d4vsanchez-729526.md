# ¿Qué hay de nuevo en Next.js?

Next.js ha cambiado bastante desde que el App Router se estabilizó. La evolución más reciente no introduce otro paradigma completamente distinto: intenta hacer que las piezas existentes —Server Components, Suspense, caché y Turbopack— sean más rápidas, explícitas y fáciles de utilizar.

La versión que concentra estas novedades es [Next.js 16.3](https://nextjs.org/blog/next-16-3). A continuación repasaremos qué cambia, qué funciones requieren activación y qué debes revisar antes de actualizar.

## Turbopack consume menos memoria y acelera los builds

Turbopack ya es el empaquetador predeterminado tanto para `next dev` como para `next build`. En Next.js 16.3 incorpora dos mejoras especialmente importantes: caché persistente en disco y expulsión de datos de memoria.

La combinación puede reducir hasta un 90 % el consumo de RAM durante sesiones largas de desarrollo. Es una mejora relevante para monorepos y aplicaciones con cientos de rutas, donde el servidor de desarrollo podía terminar ocupando varios gigabytes.

La caché persistente también llega a los builds de producción. Turbopack puede recuperar del disco artefactos que no cambiaron, evitando repetir trabajo entre compilaciones. Según los casos publicados por el equipo, algunos builds en CI llegan a ser hasta 5,5 veces más rápidos, aunque el resultado real dependerá del proyecto y de cuánto pueda reutilizarse.

Otra novedad es `import.meta.glob`, una API compatible con el patrón popularizado por Vite:

```tsx
const posts = import.meta.glob('./posts/*.md', {
  eager: true,
});
```

Esto permite importar conjuntos de archivos sin mantener manualmente una lista, algo útil para contenido Markdown, historias de componentes o sistemas de plugins.

## Navegaciones con respuesta inmediata

La gran apuesta de 16.3 se llama **Instant Navigations**. Su objetivo es que una aplicación basada en Server Components responda inmediatamente al hacer clic, como una SPA, sin renunciar al renderizado del servidor.

Hasta ahora, una ruta dinámica podía quedarse esperando la respuesta del servidor antes de mostrar algún cambio. Era posible evitarlo con `loading.tsx`, Suspense o un prefetch completo, pero resultaba fácil terminar con navegaciones bloqueantes o demasiadas solicitudes.

El nuevo modelo permite extraer una interfaz parcial reutilizable —el *shell* de la ruta— y enviarla al cliente anticipadamente. Cuando el usuario navega, ese shell aparece de inmediato y el contenido dinámico llega mediante streaming.

Para probarlo hay que activar dos opciones:

```ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
};

export default nextConfig;
```

Son funciones optativas en 16.3, aunque el equipo planea convertir estos comportamientos en predeterminados en una futura versión principal.

### Partial Prefetching

El prefetch deja de ser una decisión de “todo o nada”. Next.js puede precargar solamente la estructura necesaria para responder al clic y reutilizar segmentos compartidos entre distintas rutas.

Además, los payloads pequeños de varios enlaces pueden agruparse para reducir el número total de solicitudes. Los segmentos grandes permanecen separados cuando compartirlos entre rutas aporta una ventaja.

El resultado esperado es menos transferencia innecesaria y una interfaz que siempre tiene algo útil que mostrar mientras espera datos.

### Herramientas para detectar navegaciones lentas

Los DevTools incluyen **Instant Insights**, que señala las rutas incapaces de responder inmediatamente y explica por qué. Dependiendo del caso, propone tres estrategias:

- Colocar la operación dinámica dentro de un límite de `<Suspense>`.
- Guardar el resultado mediante `"use cache"`.
- Declarar que la ruta debe bloquearse con `export const instant = false`.

También aparece un **Navigation Inspector** para detener una navegación en su estado intermedio y observar exactamente qué verá el usuario.

Por último, el helper `instant()` para Playwright permite convertir la velocidad percibida en una prueba automatizada:

```tsx
await instant(page, async () => {
  await page.click('a[href="/productos/sombreros"]');
  await expect(page.locator('h1')).toContainText('Sombrero');
});
```

Así, un cambio en Suspense, cookies o acceso a datos no puede volver silenciosamente más lenta una ruta.

## Una caché más explícita

Cache Components continúa la transición iniciada en Next.js 16: el código dinámico se ejecuta durante la petición salvo que decidamos almacenarlo explícitamente.

La directiva `"use cache"` puede aplicarse a una función, un componente o una página. El compilador genera las claves necesarias y la combina con Suspense y Partial Prerendering.

```tsx
async function ProductList() {
  'use cache';

  const products = await getProducts();
  return <List products={products} />;
}
```

Esta aproximación resulta más predecible que depender de reglas implícitas alrededor de `fetch`. También permite combinar en una misma ruta contenido estático, datos almacenados y secciones personalizadas por petición.

La regeneración incremental mejora con este modelo. Si `generateStaticParams` solo genera parte de un catálogo, la primera visita a una URL restante puede recibir inmediatamente su shell. La página completa se crea en segundo plano y queda disponible para visitantes posteriores.

## Mejor rendimiento del servidor y TypeScript 7

Next.js sustituyó Web Streams por streams nativos de Node.js dentro de la capa de renderizado del App Router. Sus benchmarks muestran hasta un 22 % más solicitudes atendidas bajo carga, sin cambios en el código de la aplicación.

El build también puede utilizar TypeScript 7 para comprobar tipos:

```bash
pnpm add -D typescript@^7
```

Esta versión nativa de TypeScript promete comprobaciones considerablemente más rápidas, algo que puede recortar una parte importante del tiempo de CI en bases de código grandes.

## APIs pequeñas que mejoran el día a día

Next.js 16.3 introduce `catchError`, una forma de crear límites de error compatibles con `notFound()` y `redirect()`. El fallback recibe una función `retry()` capaz de volver a solicitar Server Components que fallaron durante el renderizado.

También llegan los **root params**. Un parámetro superior, como `[lang]`, puede consultarse desde cualquier Server Component sin pasarlo a través de múltiples niveles de props:

```tsx
import { lang } from 'next/root-params';

export default async function Page() {
  const locale = await lang();
  return <p>Idioma: {locale}</p>;
}
```

Por ahora funcionan en Server Components; el soporte para Route Handlers y Server Actions llegará más adelante.

## Next.js se prepara para agentes de IA

La [integración con agentes](https://nextjs.org/blog/next-16-3-ai-improvements) deja de depender únicamente del conocimiento previo del modelo. Al ejecutar `next dev`, Next.js puede mantener un bloque en `AGENTS.md` que dirige al agente hacia la documentación incluida en la versión instalada.

Esto reduce un problema frecuente: recibir código válido para otra versión del framework. También existen diagnósticos de compilación, errores con soluciones estructuradas y documentación disponible en Markdown añadiendo `.md` a una URL de las docs.

No reemplaza la revisión humana, pero sí mejora la información con la que trabajan herramientas como Codex, Claude Code o Cursor.

## Funciones experimentales

La versión incluye un React Compiler escrito en Rust e integrado directamente en Turbopack. Evita el paso adicional por Babel y, en las mediciones publicadas, reduce notablemente el tiempo hasta obtener una página lista.

Otra función experimental es `useOffline`. Cuando se pierde la conexión, una navegación, Server Action o solicitud puede mantenerse pendiente y reintentarse al volver la red. Un nuevo hook permite mostrar el estado al usuario:

```tsx
'use client';

import { useOffline } from 'next/offline';

export function OfflineBanner() {
  return useOffline() ? <p>Sin conexión. Reintentando…</p> : null;
}
```

Ambas funciones deben tratarse como experimentales: son interesantes para pruebas, pero no conviene asumir todavía estabilidad de API.

## ¿Cómo actualizar?

Next.js incluye ahora un comando de actualización:

```bash
pnpm next upgrade
```

Para versiones anteriores a 16.1 puede utilizarse el codemod:

```bash
npx @next/codemod@canary upgrade latest
```

Antes de migrar, recuerda que Next.js 16 requiere Node.js 20.9 o superior, eliminó el acceso síncrono a `cookies()`, `headers()`, `params` y `searchParams`, y sustituyó progresivamente `middleware.ts` por `proxy.ts`. Turbopack también puede descubrir incompatibilidades en configuraciones personalizadas de Webpack.

Finalmente, instala siempre el parche más reciente de la rama 16.3. Las mejoras de rendimiento son atractivas, pero las correcciones de seguridad publicadas después de una versión menor son una razón todavía más importante para mantenerse al día.

Next.js 16.3 no reinventa el framework. Hace algo más útil: reduce memoria, acelera builds y renderizado, vuelve explícita la caché y proporciona herramientas concretas para que las navegaciones se sientan instantáneas. Para proyectos existentes, esa combinación hace que la actualización merezca una prueba seria.