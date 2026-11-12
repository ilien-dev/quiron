# Room — Un Vistazo a los ‘Android Architecture Components’

Guardar información en un dispositivo Android parece sencillo hasta que la aplicación empieza a crecer. Una lista de tareas puede convertirse en un conjunto de proyectos, recordatorios y etiquetas. Entonces aparecen preguntas: ¿cómo organizamos los datos?, ¿cómo evitamos escribir consultas repetitivas? y ¿cómo mantenemos la interfaz actualizada cuando algo cambia?

Room es una biblioteca de persistencia que forma parte de Android Jetpack y se apoya en SQLite. Su objetivo es facilitar el acceso a una base de datos local sin ocultar por completo sus fundamentos. En lugar de construir cada consulta y convertir manualmente cada resultado en un objeto, podemos describir la estructura con clases de Kotlin y definir las operaciones que necesita la aplicación.

Veamos sus componentes y cómo encajan en un ejemplo de tareas.

## Las tres piezas de Room

Una implementación de Room suele organizarse alrededor de tres elementos:

- **Entidad:** representa una tabla y sus columnas.
- **DAO:** define las operaciones para leer y modificar los datos.
- **Base de datos:** reúne las entidades y proporciona acceso a los DAO.

Esta separación ayuda a que cada parte tenga una responsabilidad clara. La entidad describe los datos, el DAO describe cómo acceder a ellos y la clase de base de datos configura el conjunto.

## 1. Crear una entidad

Empecemos con una tarea sencilla:

```kotlin
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "tasks")
data class Task(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val completed: Boolean = false
)
```

La anotación `@Entity` indica que `Task` representa una tabla. Cada propiedad se convierte en una columna, mientras que `@PrimaryKey` identifica de forma única cada fila. Con `autoGenerate = true`, Room puede generar el identificador al insertar una tarea.

El nombre de la tabla, `tasks`, aparecerá en nuestras consultas SQL. Si no especificamos `tableName`, Room usará el nombre de la clase.

## 2. Definir el DAO

DAO significa *Data Access Object*. Es la interfaz donde declaramos las operaciones disponibles para una entidad:

```kotlin
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

@Dao
interface TaskDao {
    @Query("SELECT * FROM tasks ORDER BY id DESC")
    fun observeAll(): Flow<List<Task>>

    @Insert
    suspend fun insert(task: Task)

    @Update
    suspend fun update(task: Task)

    @Query("DELETE FROM tasks WHERE id = :taskId")
    suspend fun deleteById(taskId: Long)
}
```

Las anotaciones `@Insert` y `@Update` indican operaciones habituales que Room puede implementar a partir de la entidad. Para consultas específicas usamos `@Query` y escribimos SQL.

Una ventaja es que Room comprueba las consultas durante la compilación. Si una consulta hace referencia a una tabla o columna que no existe, podemos detectar el problema antes de ejecutar la aplicación.

La consulta `observeAll()` devuelve un `Flow`: una secuencia que emite la lista inicial y puede emitir nuevos valores cuando cambian los datos observados. Las operaciones de escritura, por su parte, usan `suspend` para integrarse con corrutinas.

## 3. Declarar la base de datos

Ahora reunimos las piezas:

```kotlin
import androidx.room.Database
import androidx.room.RoomDatabase

@Database(
    entities = [Task::class],
    version = 1,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun taskDao(): TaskDao
}
```

La anotación `@Database` enumera las entidades y establece una versión del esquema. La clase también expone el DAO que utilizaremos para acceder a las tareas.

Para crear una instancia, necesitamos un contexto de aplicación:

```kotlin
val database = Room.databaseBuilder(
    applicationContext,
    AppDatabase::class.java,
    "tasks.db"
).build()

val taskDao = database.taskDao()
```

En una aplicación real conviene compartir una única instancia de `AppDatabase`, por ejemplo mediante un contenedor de dependencias. Crear varias instancias innecesariamente puede consumir recursos y complicar la gestión de la base de datos.

## Room y la arquitectura de la aplicación

Room resuelve el acceso local a los datos, pero no tiene por qué comunicarse directamente con la interfaz. Una organización habitual introduce un repositorio entre el DAO y el `ViewModel`:

```kotlin
class TaskRepository(private val taskDao: TaskDao) {
    val tasks: Flow<List<Task>> = taskDao.observeAll()

    suspend fun addTask(title: String) {
        taskDao.insert(Task(title = title))
    }
}
```

El repositorio ofrece a otras partes de la aplicación una forma de trabajar con tareas. En un proyecto más grande también podría coordinar una fuente remota y una local, o aplicar reglas antes de guardar información.

El `ViewModel` puede observar los datos y exponerlos a la pantalla. Así, la interfaz se concentra en mostrarlos y responder a las acciones del usuario, mientras Room se ocupa de persistirlos.

```kotlin
class TaskViewModel(
    private val repository: TaskRepository
) : ViewModel() {
    val tasks = repository.tasks

    fun addTask(title: String) {
        viewModelScope.launch {
            repository.addTask(title)
        }
    }
}
```

Este ejemplo omite la creación del `ViewModel` y la configuración de dependencias para mantener el foco en la relación entre los componentes.

## ¿Qué ocurre cuando cambia el esquema?

Las aplicaciones evolucionan. Quizá mañana una tarea necesite una fecha límite o una prioridad. Si cambiamos una entidad de una aplicación ya instalada, también debemos considerar cómo pasar de la versión anterior de la base de datos a la nueva.

Room admite migraciones para describir esos cambios. Algunas pueden generarse automáticamente; otras requieren instrucciones explícitas, especialmente cuando hay transformaciones de datos más complejas. Exportar y conservar los esquemas facilita revisar esos cambios y probar las migraciones.

Diseñar este paso importa: los datos locales pueden ser valiosos para el usuario, incluso si la aplicación también se conecta a un servidor.

## Cuándo usar Room

Room resulta útil cuando necesitamos datos estructurados, consultas relacionales y persistencia local: listas, inventarios, contenido disponible sin conexión o cachés son ejemplos habituales. Para preferencias pequeñas, como una opción de tema, una solución como DataStore puede resultar más apropiada.

La principal ventaja de Room es que combina SQL con herramientas de Kotlin y comprobaciones en compilación. No elimina la necesidad de pensar en tablas, consultas y migraciones, pero ofrece una base cómoda para hacerlo. Si tu aplicación necesita guardar datos localmente, es un buen punto de partida dentro del ecosistema Android.
