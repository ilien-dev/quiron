# Room — Un Vistazo a los ‘Android Architecture Components’

Guardar información localmente parece sencillo hasta que una aplicación empieza a crecer. Una lista de favoritos se convierte en varias tablas relacionadas; aparecen consultas, actualizaciones y cambios de esquema. Entonces, ese pequeño módulo de persistencia comienza a exigir bastante atención.

Si has trabajado directamente con SQLite en Android, probablemente recuerdes los cursores, las sentencias SQL y el código necesario para transformar resultados en objetos. Todo funciona, pero también hay muchas oportunidades para equivocarse.

Room ayuda a simplificar ese trabajo. En este artículo veremos sus piezas principales mediante una pequeña aplicación de notas.

### ¿Qué es Room?

Room es una biblioteca de persistencia que proporciona una capa de abstracción sobre SQLite. Surgió dentro de los Android Architecture Components y forma parte del ecosistema Jetpack.

Su propuesta resulta práctica: describimos nuestros datos y las operaciones que necesitamos mediante clases, interfaces y anotaciones. A partir de esas definiciones, Room genera buena parte del código de acceso.

Seguimos utilizando SQL cuando necesitamos consultar información, pero contamos con validación durante la compilación. Una consulta que referencia una columna inexistente puede detectarse antes de ejecutar la aplicación. La [documentación oficial de Room](https://developer.android.com/training/data-storage/room) explica este enfoque.

### Tres piezas para comenzar

Para entender Room conviene identificar tres elementos:

- **Entity:** representa una tabla y describe sus columnas.
- **DAO:** declara las operaciones disponibles sobre los datos.
- **Database:** reúne las entidades y proporciona acceso a los DAO.

Imagina una libreta digital: la entidad define cómo es una nota, el DAO establece cómo guardarla o buscarla, y la base de datos conecta ambas partes.

Esta separación también facilita encontrar responsabilidades. Si cambia una consulta, sabemos dónde buscar; si cambia la estructura almacenada, empezamos por la entidad.

### Nuestra primera entidad

Una nota necesita un identificador, un título y un contenido. Podemos representarla así en Kotlin:

```kotlin
@Entity(tableName = "notas")
data class Nota(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val titulo: String,
    val contenido: String
)
```

La anotación `@Entity` indica que esta clase representa una tabla. Con `tableName` elegimos explícitamente su nombre.

`@PrimaryKey` identifica la clave primaria. Al activar `autoGenerate`, permitimos que se genere el identificador cuando insertamos una nota nueva.

Las propiedades restantes se convierten en columnas. Por ahora usamos tipos sencillos; cuando necesitemos almacenar objetos más complejos, tendremos que decidir cómo representarlos mediante relaciones o conversiones.

Conviene diseñar estas entidades pensando en los datos que realmente queremos conservar. No todos los objetos utilizados por la interfaz necesitan terminar almacenados.

### El DAO: nuestras operaciones

DAO significa *Data Access Object*. En Room suele ser una interfaz o una clase abstracta donde declaramos consultas y operaciones de escritura.

```kotlin
@Dao
interface NotaDao {
    @Insert
    suspend fun insertar(nota: Nota)

    @Query("SELECT * FROM notas ORDER BY id DESC")
    fun observarTodas(): Flow<List<Nota>>

    @Query("SELECT * FROM notas WHERE id = :id")
    suspend fun buscarPorId(id: Long): Nota?

    @Delete
    suspend fun eliminar(nota: Nota)
}
```

Aquí aparecen dos estilos de acceso. `insertar`, `buscarPorId` y `eliminar` realizan operaciones puntuales mediante funciones suspendidas. `observarTodas` devuelve un flujo que permite recibir resultados actualizados cuando cambia la tabla observada.

El parámetro `:id` vincula el argumento de la función con la consulta. Así evitamos construir sentencias concatenando valores.

También es útil observar el resultado nullable de `buscarPorId`: buscar una nota no garantiza encontrarla. Expresar esa posibilidad en el contrato obliga al código consumidor a contemplarla.

Room ofrece soporte para corrutinas y consultas observables, como describe su [guía de consultas asíncronas](https://developer.android.com/training/data-storage/room/async-queries).

### La clase de base de datos

Ahora necesitamos reunir nuestras definiciones:

```kotlin
@Database(
    entities = [Nota::class],
    version = 1
)
abstract class NotasDatabase : RoomDatabase() {
    abstract fun notaDao(): NotaDao
}
```

`entities` enumera las tablas que pertenecen a la base de datos. `version` identifica la versión de su esquema.

La función `notaDao()` permite obtener el objeto que implementará las operaciones declaradas anteriormente. Esa implementación la genera Room.

Para incorporar el ejemplo a un proyecto, hay que añadir las dependencias correspondientes y configurar su compilador siguiendo la documentación de la versión elegida. Después se construye la instancia de la base de datos y se comparte desde el contenedor de dependencias de la aplicación.

### ¿Dónde encaja en la arquitectura?

Una organización habitual coloca un repositorio entre los DAO y el ViewModel. El repositorio coordina el acceso a los datos; el ViewModel prepara el estado que consume la interfaz.

En nuestra aplicación, la pantalla puede observar las notas expuestas por el ViewModel. Cuando alguien guarda una nueva, la operación llega al DAO y el flujo observado permite reflejar los cambios.

Esta distribución evita concentrar consultas, almacenamiento y presentación dentro de una Activity. También ofrece puntos claros para sustituir dependencias durante las pruebas.

El repositorio debe tener una responsabilidad concreta: por ejemplo, decidir cómo combinar datos locales con respuestas de una API.

### Las migraciones también cuentan

Tarde o temprano querremos añadir una fecha o marcar notas como favoritas. Ese cambio afecta al esquema y requiere planificar cómo conservar los datos existentes.

Room admite migraciones automáticas y manuales. La elección depende del cambio; algunas transformaciones necesitan instrucciones adicionales. Su [guía de migraciones](https://developer.android.com/training/data-storage/room/migrating-db-versions) desarrolla ambas opciones.

Probar únicamente instalaciones nuevas deja fuera a quienes ya utilizan la aplicación. También debemos verificar actualizaciones desde versiones anteriores.

Room reduce trabajo repetitivo y hace más explícito el acceso a SQLite. Para empezar, una entidad, un DAO y una base de datos bastan para explorar su funcionamiento. Después podremos incorporar relaciones, transacciones y migraciones según las necesidades reales de nuestra aplicación.
