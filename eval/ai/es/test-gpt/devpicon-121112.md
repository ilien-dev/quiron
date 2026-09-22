# Room — Un Vistazo a los ‘Android Architecture Components’

Guardar información localmente es una necesidad habitual en las aplicaciones Android. Perfiles, favoritos, notas, configuraciones o contenido disponible sin conexión son algunos ejemplos de datos que deben sobrevivir al cierre de la app. Aunque Android incluye SQLite, trabajar directamente con esta base de datos implica escribir bastante código repetitivo y gestionar consultas, cursores y conversiones manualmente.

Room simplifica este proceso. Forma parte de Android Jetpack y proporciona una capa de abstracción sobre SQLite que permite definir bases de datos mediante clases, anotaciones y consultas verificadas. No sustituye a SQLite: lo utiliza internamente, pero ofrece una API más segura y cómoda.

## ¿Qué aporta Room?

Una implementación tradicional con SQLite requiere crear tablas, ejecutar consultas, recorrer cursores y transformar cada fila en un objeto de Kotlin o Java. También debemos controlar conexiones, versiones del esquema y posibles errores en las sentencias SQL.

Room reduce esa complejidad mediante tres piezas principales:

- **Entity:** representa una tabla.
- **DAO:** define las operaciones de acceso a los datos.
- **Database:** conecta las entidades con sus DAO y configura la base de datos.

Además, Room comprueba las consultas SQL durante la compilación. Si una columna no existe o el tipo devuelto no coincide con el esperado, el problema puede detectarse antes de ejecutar la aplicación.

## Nuestra primera entidad

Supongamos que desarrollamos una aplicación para guardar tareas. El modelo podría definirse de esta forma:

```kotlin
@Entity(tableName = "tasks")
data class Task(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val completed: Boolean = false
)
```

La anotación `@Entity` indica que la clase representa una tabla. Cada propiedad se convierte, de manera predeterminada, en una columna. Con `tableName` podemos asignar un nombre diferente al de la clase.

La propiedad `id` está marcada con `@PrimaryKey`, por lo que identifica cada registro de manera única. `autoGenerate = true` permite que SQLite genere su valor automáticamente al insertar una tarea.

Room también incluye anotaciones como `@ColumnInfo`, para personalizar el nombre de una columna, e `@Ignore`, para excluir propiedades que no deben persistirse.

## Acceso a datos mediante un DAO

El DAO —*Data Access Object*— concentra las operaciones realizadas sobre la tabla. En lugar de repartir consultas por toda la aplicación, las declaramos en una interfaz:

```kotlin
@Dao
interface TaskDao {

    @Insert
    suspend fun insert(task: Task): Long

    @Update
    suspend fun update(task: Task)

    @Delete
    suspend fun delete(task: Task)

    @Query("SELECT * FROM tasks ORDER BY id DESC")
    fun observeAll(): Flow<List<Task>>

    @Query("SELECT * FROM tasks WHERE id = :taskId LIMIT 1")
    suspend fun findById(taskId: Long): Task?
}
```

Las anotaciones `@Insert`, `@Update` y `@Delete` cubren las operaciones más comunes. Para consultas personalizadas utilizamos `@Query` y escribimos SQL.

Los parámetros pueden incluirse en la consulta mediante la sintaxis `:nombre`. Room se encarga de enlazar sus valores correctamente, evitando la concatenación manual de cadenas.

Las operaciones puntuales están declaradas como funciones `suspend`, por lo que pueden ejecutarse desde una corrutina sin bloquear el hilo principal. La consulta que devuelve todas las tareas utiliza `Flow`: cada cambio relevante en la tabla genera un nuevo valor y permite actualizar la interfaz de forma reactiva.

## Creación de la base de datos

El siguiente paso consiste en crear una clase abstracta que extienda `RoomDatabase`:

```kotlin
@Database(
    entities = [Task::class],
    version = 1,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun taskDao(): TaskDao
}
```

La anotación `@Database` declara las entidades incluidas y la versión actual del esquema. La clase expone los DAO que utilizará la aplicación.

Podemos construir una instancia así:

```kotlin
val database = Room.databaseBuilder(
    context.applicationContext,
    AppDatabase::class.java,
    "tasks.db"
).build()
```

Normalmente debe existir una sola instancia de la base de datos durante la vida del proceso. Podemos proporcionarla mediante un contenedor de dependencias o implementarla como *singleton*. Crear múltiples instancias innecesarias aumenta el consumo de recursos y complica la coordinación de las conexiones.

## Room dentro de una arquitectura moderna

Room funciona especialmente bien junto con el patrón de repositorio. El DAO conoce los detalles de almacenamiento, mientras que el repositorio ofrece una API orientada al dominio:

```kotlin
class TaskRepository(
    private val taskDao: TaskDao
) {
    val tasks: Flow<List<Task>> = taskDao.observeAll()

    suspend fun addTask(title: String) {
        taskDao.insert(Task(title = title))
    }

    suspend fun toggle(task: Task) {
        taskDao.update(task.copy(completed = !task.completed))
    }
}
```

Un `ViewModel` puede consumir este flujo y exponerlo como estado para la interfaz:

```kotlin
class TaskViewModel(
    private val repository: TaskRepository
) : ViewModel() {

    val tasks = repository.tasks
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = emptyList()
        )

    fun addTask(title: String) {
        viewModelScope.launch {
            repository.addTask(title)
        }
    }
}
```

Esta separación facilita las pruebas y evita que la UI dependa directamente de la implementación de persistencia.

## Relaciones y objetos complejos

Las bases de datos reales suelen contener varias tablas relacionadas. Room permite representar relaciones mediante anotaciones como `@Embedded`, `@Relation` y `@Junction`. Aun así, conviene recordar que SQLite sigue siendo una base relacional: no debemos tratarla como si almacenara automáticamente árboles completos de objetos.

Para tipos que SQLite no soporta directamente —por ejemplo, una fecha o un tipo propio— podemos utilizar `@TypeConverter`:

```kotlin
class Converters {

    @TypeConverter
    fun fromTimestamp(value: Long?): Instant? =
        value?.let(Instant::ofEpochMilli)

    @TypeConverter
    fun toTimestamp(value: Instant?): Long? =
        value?.toEpochMilli()
}
```

Estos conversores deben registrarse para que Room sepa cómo transformar el valor antes de escribirlo y después de leerlo.

## Migraciones: el detalle que no debemos ignorar

Cuando cambia una entidad, también puede cambiar el esquema de la base de datos. Incrementar simplemente el número de versión no conserva los datos por arte de magia. Debemos describir cómo pasar de una versión a otra:

```kotlin
val migration1To2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL(
            "ALTER TABLE tasks ADD COLUMN priority INTEGER NOT NULL DEFAULT 0"
        )
    }
}
```

Después, la migración se añade al constructor de la base de datos con `addMigrations`.

Existe la opción de recrear la base ante una migración ausente, pero destruye la información almacenada. Puede servir para prototipos o datos regenerables, no como solución predeterminada en producción.

## Pruebas

Los DAO pueden probarse mediante una base en memoria:

```kotlin
database = Room.inMemoryDatabaseBuilder(
    context,
    AppDatabase::class.java
).build()
```

Estas pruebas permiten insertar registros, ejecutar consultas y comprobar resultados sin conservar archivos entre ejecuciones. Las migraciones también deberían probarse utilizando esquemas exportados, especialmente cuando una aplicación ya cuenta con usuarios y varias versiones publicadas.

## Conclusión

Room no elimina la necesidad de entender SQL ni el diseño relacional, pero hace que ambos encajen mejor en una aplicación Android moderna. Sus entidades documentan el esquema, los DAO centralizan las consultas y su integración con corrutinas y `Flow` permite reaccionar a los cambios de manera natural.

Para bases pequeñas o medianas, contenido sin conexión, cachés estructuradas y aplicaciones que necesitan persistencia fiable, Room suele ser el punto de partida más práctico. La clave está en mantener responsabilidades claras, diseñar cuidadosamente las migraciones y aprovechar la verificación que Room realiza durante la compilación.