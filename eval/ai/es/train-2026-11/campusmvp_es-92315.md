# 10 Diferencias entre .NET Core y .NET Framework

Si programas en C#, seguramente te has encontrado con esta pregunta: **¿qué diferencia hay entre .NET Core y .NET Framework?** Comparten lenguajes, conceptos y muchas bibliotecas, pero elegir uno u otro cambia dónde puedes ejecutar tu aplicación, cómo la despliegas y qué tecnologías tienes disponibles.

Antes de comparar, hay una aclaración necesaria: **desde .NET 5, la evolución de .NET Core se llama simplemente .NET**. Por eso, aquí utilizaremos “.NET moderno” para hablar de esa línea actual. Las versiones que conservaron el nombre .NET Core, como 3.1, ya están fuera de soporte. Puedes comprobarlo en la [política oficial de soporte](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core).

Con esa distinción clara, veamos diez diferencias y cómo afectan al trabajo diario.

## 1. Sistemas operativos: Windows frente a múltiples plataformas

.NET Framework está ligado a Windows. Es habitual encontrarlo en aplicaciones empresariales que dependen de ese sistema operativo y de sus servicios.

.NET Core nació con soporte multiplataforma, y .NET moderno mantiene esa capacidad. Puedes desarrollar y ejecutar aplicaciones compatibles en Windows, Linux y macOS. Esto permite, por ejemplo, trabajar desde Windows y desplegar una API en un servidor Linux. Microsoft describe esta portabilidad en su [introducción a .NET](https://learn.microsoft.com/en-us/dotnet/core/introduction).

La palabra clave es **compatibles**: usar .NET moderno no convierte automáticamente cualquier aplicación en multiplataforma. Si utilizas componentes COM, bibliotecas nativas exclusivas de Windows o rutas específicas del sistema, tendrás que revisar esas dependencias.

En la práctica, la portabilidad depende tanto del runtime como del código y las bibliotecas que elijas.

## 2. Evolución y soporte: dos ciclos diferentes

.NET Framework sigue teniendo soporte en las versiones y sistemas operativos correspondientes. Por ejemplo, el soporte de .NET Framework 4.8.1 está vinculado al de Windows donde se instala. Por tanto, sería incorrecto afirmar que toda aplicación basada en Framework está abandonada. Así lo explica su [política de soporte](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-framework).

.NET moderno tiene su propio calendario de versiones, con modalidades LTS y STS y fechas concretas de finalización del soporte. Su mantenimiento exige planificar actualizaciones del runtime, además de aplicar parches.

La consecuencia para un equipo es organizativa: al elegir una plataforma, también eliges una estrategia de mantenimiento. Conviene registrar qué versión utiliza cada servicio, cuándo termina su soporte y quién será responsable de actualizarlo.

## 3. Instalación y convivencia de versiones

En .NET Framework 4.x, las actualizaciones reemplazan versiones anteriores de esa misma familia. No puedes instalar varias versiones 4.x independientes para que cada aplicación seleccione libremente la suya.

.NET moderno permite instalar diferentes versiones del runtime en una misma máquina. Así, dos servicios pueden avanzar con calendarios de actualización distintos. Microsoft detalla esta diferencia en su [comparación para aplicaciones de servidor](https://learn.microsoft.com/en-us/dotnet/standard/choosing-core-framework-server).

Imagina un servidor con una API de facturación y otra de inventario. Si sus dependencias requieren versiones diferentes, esa convivencia facilita actualizar primero una de ellas.

Esto reduce el acoplamiento operativo entre aplicaciones, aunque sigue siendo necesario probar cada actualización y conocer las reglas de selección del runtime.

## 4. Despliegue: runtime compartido o incluido

Con .NET Framework, lo habitual es que el equipo de destino tenga instalada una versión compatible del framework.

.NET moderno ofrece dos modalidades principales:

- **Framework-dependent:** la aplicación utiliza un runtime compatible instalado en el entorno.
- **Self-contained:** la publicación incluye el runtime necesario para ejecutarse.

Por ejemplo:

```bash
dotnet publish -c Release -r linux-x64 --self-contained true
```

Este comando prepara una publicación autocontenida para Linux x64. No elimina las dependencias nativas que pueda exigir el sistema operativo.

La elección tiene consecuencias: incluir el runtime aumenta el tamaño del paquete y obliga a volver a publicar para incorporar sus parches. Compartirlo permite centralizar parte del mantenimiento. La [documentación de publicación](https://learn.microsoft.com/en-us/dotnet/core/deploying/) explica ambas opciones.

## 5. Desarrollo web: ASP.NET clásico y ASP.NET Core

En .NET Framework encontramos tecnologías como ASP.NET Web Forms y ASP.NET MVC 5. En .NET moderno, el desarrollo web se realiza con ASP.NET Core.

ASP.NET Core incorpora un modelo basado en middleware y ofrece mecanismos integrados para inyección de dependencias, configuración y registro de eventos. También incluye Kestrel, un servidor HTTP multiplataforma. Puedes consultar sus características en la [presentación oficial de ASP.NET Core](https://dotnet.microsoft.com/en-us/learn/aspnet/what-is-aspnet-core).

Esto cambia la forma de organizar una aplicación web. Por ejemplo, la autenticación y el tratamiento de errores participan en una cadena de procesamiento explícita.

Una aplicación Web Forms necesita una estrategia de migración específica: sus páginas y controles no se convierten en ASP.NET Core simplemente cambiando el framework de destino.

## 6. Rendimiento: una base con evolución continua

.NET moderno concentra mejoras continuas del runtime y de sus bibliotecas. En aplicaciones de servidor, Microsoft lo recomienda cuando el rendimiento y la escalabilidad son prioridades, según su [guía de elección de plataforma](https://learn.microsoft.com/en-us/dotnet/standard/choosing-core-framework-server).

Eso puede traducirse en atender más solicitudes con los mismos recursos o reducir el consumo de infraestructura. El resultado depende de la carga real.

Si una API tarda dos segundos porque ejecuta una consulta sin índices, cambiar de runtime difícilmente resolverá el problema principal.

Antes de migrar por rendimiento, mide latencia, uso de memoria, CPU y acceso a datos. Después, compara ambos entornos con una carga representativa. Un benchmark aislado ayuda a investigar; una prueba de tu aplicación ayuda a decidir.

## 7. Herramientas y trabajo desde la terminal

.NET Framework suele encontrarse en soluciones construidas alrededor de Visual Studio y herramientas de Windows. También permite automatizar compilaciones; esa capacidad no es exclusiva de .NET moderno.

La diferencia es que el SDK moderno proporciona una CLI multiplataforma como parte central del flujo de desarrollo:

```bash
dotnet new console -n MiAplicacion
cd MiAplicacion
dotnet build
dotnet run
```

La misma herramienta permite restaurar dependencias, ejecutar pruebas y publicar aplicaciones. Su funcionamiento está documentado en la [guía de la CLI de .NET](https://learn.microsoft.com/en-us/dotnet/core/tools/).

Para un equipo, esto facilita expresar el proceso de compilación mediante comandos reproducibles. Un desarrollador y un servidor de integración continua pueden seguir pasos equivalentes, reduciendo las diferencias entre entornos.

## 8. Bibliotecas y compatibilidad de APIs

Compartir C# no garantiza que una biblioteca funcione en ambas plataformas. Un paquete puede depender de APIs exclusivas de .NET Framework o de componentes específicos de Windows.

.NET Standard 2.0 puede servir como contrato común para determinadas bibliotecas que deban utilizarse desde .NET Framework y .NET moderno. **.NET Standard es una especificación de APIs**, no un runtime que instalas para ejecutar aplicaciones.

Además, .NET Framework no implementa .NET Standard 2.1. La [documentación de .NET Standard](https://learn.microsoft.com/en-us/dotnet/standard/net-standard) explica estas compatibilidades.

Si mantienes una biblioteca compartida, revisa qué frameworks soportan sus consumidores antes de elegir el destino. También puedes valorar múltiples destinos cuando necesites ofrecer capacidades distintas sin mantener proyectos completamente separados.

## 9. Aplicaciones de escritorio: diferencias con matices

.NET Framework tiene una larga trayectoria en aplicaciones Windows Forms y WPF. Sin embargo, ambas tecnologías también están disponibles en .NET moderno.

Por tanto, desarrollar escritorio no obliga a elegir Framework. Una aplicación existente puede estudiar su actualización para acceder a mejoras del runtime, nuevas APIs y herramientas más recientes.

El matiz es que **WPF y Windows Forms siguen siendo tecnologías para Windows**. Migrar una aplicación WPF a .NET moderno no permite ejecutarla directamente en Linux o macOS. Microsoft lo aclara en la [documentación de WPF](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/overview/).

Para planificar una migración, revisa también controles comerciales, instaladores, impresión e integraciones con el sistema. Con frecuencia, esas piezas determinan más trabajo que la lógica de negocio.

## 10. Tecnologías heredadas y esfuerzo de migración

.NET moderno no reproduce todas las capacidades de .NET Framework. Tecnologías como .NET Remoting, la creación de AppDomains adicionales y Code Access Security no tienen el mismo soporte.

Esto significa que algunas migraciones requieren cambios de diseño. Por ejemplo, un sistema que utiliza Remoting puede necesitar comunicación mediante HTTP, mecanismos entre procesos u otra alternativa adecuada. Microsoft mantiene una [lista de tecnologías no disponibles](https://learn.microsoft.com/en-us/dotnet/core/porting/net-framework-tech-unavailable).

Por eso, una evaluación inicial debería identificar dependencias, APIs incompatibles y pruebas necesarias antes de estimar plazos.

Una estrategia útil consiste en empezar por una biblioteca o servicio acotado. Ese primer paso permite descubrir obstáculos reales y calcular mejor el esfuerzo del resto, siguiendo un enfoque gradual como propone la [guía de actualización de aplicaciones](https://learn.microsoft.com/en-us/dotnet/core/porting/).

Para un proyecto nuevo, una versión soportada de .NET moderno suele ser la elección de partida. En una aplicación existente, conviene valorar el beneficio frente al coste y al riesgo de migración.

Si mantienes un sistema estable en .NET Framework, empieza por conocer sus dependencias y su situación de soporte. Si buscas desplegar en Linux, renovar el desarrollo web o actualizar componentes, ya tienes motivos concretos para evaluar .NET moderno.

**¿Cuál de estas diferencias ha pesado más en tus proyectos?**
