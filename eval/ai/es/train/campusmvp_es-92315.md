# 10 Diferencias entre .NET Core y .NET Framework

Durante muchos años, elegir tecnología dentro del ecosistema Microsoft significaba trabajar con .NET Framework. Sin embargo, la llegada de .NET Core cambió el panorama: introdujo soporte multiplataforma, despliegues más flexibles, mejor rendimiento y un modelo de desarrollo abierto.

Antes de comparar ambas plataformas, conviene aclarar un detalle de nombres. **.NET Core** fue la denominación utilizada hasta la versión 3.1. A partir de .NET 5, Microsoft eliminó la palabra “Core” y continuó la plataforma simplemente como **.NET**. Por tanto, cuando hoy hablamos de migrar desde .NET Framework, normalmente el destino es una versión moderna de .NET, no una nueva versión llamada .NET Core.

Aunque comparten C#, bibliotecas y muchos conceptos, .NET moderno y .NET Framework no son dos versiones equivalentes del mismo producto. Estas son sus diez diferencias principales.

## 1. Sistemas operativos compatibles

La diferencia más visible es el sistema operativo sobre el que puede ejecutarse cada plataforma.

**.NET Framework funciona únicamente en Windows**. Está estrechamente integrado con el sistema operativo y con tecnologías históricas de Microsoft, como Internet Information Services, Windows Forms, WPF y el Registro de Windows.

.NET Core y sus sucesores, en cambio, son **multiplataforma**. Una aplicación puede ejecutarse en:

- Windows
- Linux
- macOS
- Imágenes de contenedor
- Diferentes arquitecturas, como x64 y ARM64

Esto no significa que todas las aplicaciones modernas de .NET funcionen automáticamente en cualquier sistema. Una aplicación WPF, por ejemplo, continúa dependiendo de Windows. Sin embargo, bibliotecas, servicios web, procesos de consola y muchas aplicaciones de servidor pueden compartir el mismo código entre plataformas.

Para una API que debe ejecutarse en Linux o Kubernetes, .NET moderno es la elección natural.

## 2. Modelo de instalación y despliegue

.NET Framework se instala como un componente de Windows. Generalmente, las aplicaciones utilizan la versión disponible en la máquina, por lo que actualizar el entorno puede afectar a varios programas instalados.

.NET moderno ofrece alternativas más flexibles.

En un despliegue **dependiente del framework**, el servidor debe tener instalado el runtime correspondiente. El paquete de la aplicación es más pequeño, pero depende de ese componente compartido.

En un despliegue **autocontenido**, la aplicación incluye el runtime que necesita. Esto aumenta el tamaño del paquete, pero evita depender de una instalación global.

También existe la publicación como archivo único y, para determinados escenarios, la compilación nativa mediante Native AOT.

Gracias a este modelo, diferentes aplicaciones pueden utilizar versiones distintas de .NET en la misma máquina. Esta ejecución *side by side* facilita actualizar un servicio sin obligar a todos los demás a cambiar al mismo tiempo.

## 3. Código abierto y desarrollo de la plataforma

.NET moderno se desarrolla de forma abierta. El runtime, los compiladores, numerosas bibliotecas y los frameworks principales se encuentran en repositorios públicos de GitHub. Es posible consultar propuestas, seguir cambios, reportar problemas y contribuir al proyecto.

.NET Framework dispone de código de referencia y Microsoft continúa publicando actualizaciones de seguridad y confiabilidad. Sin embargo, ya no es la plataforma donde se concentran las grandes innovaciones del ecosistema.

Esta diferencia tiene consecuencias prácticas. Las nuevas versiones del lenguaje, optimizaciones del runtime, mejoras de ASP.NET Core y nuevas APIs llegan principalmente a .NET moderno.

.NET Framework sigue siendo una tecnología válida para mantener sistemas existentes, pero no representa el rumbo principal para proyectos nuevos.

## 4. Rendimiento y uso de recursos

El rendimiento fue una prioridad desde el diseño inicial de .NET Core. Su runtime, sus bibliotecas y ASP.NET Core han recibido optimizaciones continuas relacionadas con:

- Recolección de basura
- Compilación JIT
- Asignación de memoria
- Entrada y salida asíncrona
- Serialización
- Operaciones de red
- Tiempo de inicio

El resultado depende de cada aplicación, pero los servicios creados con .NET moderno suelen manejar más solicitudes utilizando menos recursos que soluciones equivalentes basadas en tecnologías web clásicas de .NET Framework.

Esto es especialmente importante en la nube. Una reducción de memoria o CPU puede traducirse en menos instancias, contenedores más pequeños y una factura menor.

No obstante, migrar no garantiza por sí solo una aplicación rápida. Las consultas a la base de datos, el diseño de la arquitectura, la caché y los algoritmos continúan siendo factores decisivos.

## 5. Tecnologías para aplicaciones web

En .NET Framework, el desarrollo web tradicional gira alrededor de **ASP.NET**, que incluye tecnologías como:

- ASP.NET Web Forms
- ASP.NET MVC 5
- ASP.NET Web API 2
- SignalR clásico
- Integración con `System.Web`

.NET moderno utiliza **ASP.NET Core**, una implementación rediseñada, modular y multiplataforma. ASP.NET Core unificó los modelos de MVC y Web API, incorporó un sistema de configuración moderno, inyección de dependencias integrada y un pipeline de middleware configurable.

Aunque algunos conceptos son similares, ASP.NET y ASP.NET Core no son intercambiables. Una aplicación basada en Web Forms o dependiente de `System.Web` no puede cambiar de runtime modificando únicamente el archivo del proyecto.

Migrarla suele requerir una transformación progresiva de la interfaz, la autenticación, la configuración y el procesamiento de solicitudes.

## 6. Compatibilidad con aplicaciones de escritorio y tecnologías heredadas

.NET Framework continúa siendo importante porque soporta tecnologías empresariales que no fueron trasladadas completamente a .NET moderno.

Entre los casos que pueden justificar su uso se encuentran:

- ASP.NET Web Forms
- Servicios WCF del lado del servidor
- Windows Workflow Foundation
- Bibliotecas antiguas que dependen de APIs exclusivas
- Integraciones complejas con componentes heredados

Windows Forms y WPF sí están disponibles en versiones modernas de .NET, aunque siguen siendo tecnologías exclusivas de Windows. Esto permite modernizar muchas aplicaciones de escritorio, mejorar su rendimiento y utilizar versiones recientes de C# sin reconstruir toda la interfaz.

Antes de migrar, conviene analizar las dependencias con herramientas como [.NET Upgrade Assistant](https://learn.microsoft.com/dotnet/core/porting/upgrade-assistant-overview). El lenguaje puede ser compatible mientras una biblioteca de terceros, un control visual o una integración específica impide completar el cambio.

## 7. Herramientas y formato de proyecto

Los proyectos de .NET Framework suelen utilizar formatos de archivo `.csproj` extensos, con listas explícitas de archivos y numerosas configuraciones XML. Tradicionalmente, su flujo de trabajo está muy ligado a Visual Studio y a herramientas disponibles en Windows.

.NET moderno introdujo proyectos con formato SDK, mucho más compactos:

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>
</Project>
```

Además, la CLI permite crear, compilar, probar, ejecutar y publicar aplicaciones desde cualquier terminal:

```bash
dotnet new webapi
dotnet build
dotnet test
dotnet publish
```

Visual Studio continúa ofreciendo una experiencia excelente, pero deja de ser obligatorio. También pueden utilizarse Visual Studio Code, Rider o pipelines que trabajen directamente con `dotnet`.

Esta uniformidad simplifica la automatización y reduce las diferencias entre el entorno local y el servidor de integración continua.

## 8. Administración de dependencias

.NET Framework utiliza NuGet, pero muchos sistemas heredados también dependen del Global Assembly Cache, referencias instaladas en la máquina o archivos DLL copiados manualmente.

.NET moderno favorece dependencias declaradas explícitamente mediante `PackageReference`. NuGet restaura los paquetes a partir del proyecto, lo que facilita reproducir una compilación en diferentes entornos.

Otra diferencia importante es el aislamiento. En lugar de asumir que una biblioteca global estará disponible, cada aplicación define las versiones que necesita. Esto reduce los conflictos conocidos popularmente como *DLL Hell*.

Aun así, NuGet no elimina todos los riesgos. Las versiones transitivas, paquetes abandonados y vulnerabilidades de la cadena de suministro deben administrarse mediante actualizaciones, archivos de bloqueo cuando sean necesarios y análisis de seguridad.

## 9. Contenedores, microservicios y nube

.NET Framework puede ejecutarse en contenedores de Windows, pero esas imágenes suelen ser grandes y mantienen una dependencia directa con ese sistema operativo.

.NET moderno está mejor preparado para contenedores Linux, arquitecturas distribuidas y plataformas de orquestación. Permite crear imágenes más pequeñas, elegir diferentes distribuciones base y ejecutar el mismo servicio en proveedores de nube distintos.

ASP.NET Core incluye características muy útiles para estos entornos: configuración por variables de entorno, registro estructurado, comprobaciones de salud y servidores web de alto rendimiento.

Esto no significa que todos los proyectos deban convertirse en microservicios. Un monolito modular puede ser más sencillo y económico. La ventaja real es que .NET moderno ofrece más opciones de despliegue sin imponer una arquitectura determinada.

## 10. Ciclo de vida y futuro

.NET Framework se mantiene como parte del ecosistema de Windows. Microsoft continúa proporcionando correcciones de seguridad y confiabilidad de acuerdo con el ciclo de vida del sistema operativo, pero no publica nuevas versiones principales orientadas a expandir la plataforma.

.NET moderno tiene un ritmo regular de lanzamientos y versiones con distintos periodos de soporte, incluyendo ediciones LTS. Esto permite planificar actualizaciones frecuentes y acceder a nuevas funciones del runtime, C# y las bibliotecas.

La diferencia puede resumirse así:

| Aspecto | .NET Framework | .NET moderno |
|---|---|---|
| Objetivo principal | Compatibilidad con sistemas Windows existentes | Desarrollo nuevo y multiplataforma |
| Evolución | Mantenimiento y seguridad | Innovación activa |
| Actualización | Vinculada a Windows | Versiones independientes |
| Estrategia habitual | Conservar cuando existe una dependencia heredada | Utilizar en proyectos nuevos |

## ¿Cuál deberías elegir?

Para un proyecto nuevo, la recomendación general es utilizar una versión soportada de **.NET moderno**. Ofrece mejor rendimiento, soporte multiplataforma, despliegues flexibles, herramientas actuales y un futuro más claro.

.NET Framework sigue teniendo sentido cuando una aplicación depende de Web Forms, WCF del lado del servidor, componentes empresariales antiguos o integraciones exclusivas de Windows cuya sustitución no resulta viable.

La decisión no debería reducirse a “viejo contra nuevo”. En sistemas existentes hay que comparar el coste de migración con los beneficios operativos y técnicos. A veces será razonable mantener la aplicación mientras recibe soporte; en otros casos, la deuda tecnológica justificará una modernización gradual.

Lo importante es entender que .NET Framework permanece principalmente como una plataforma de compatibilidad, mientras que .NET moderno es el destino estratégico para el desarrollo actual.