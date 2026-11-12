# Lo que Necesitas Saber sobre Electroestática (al menos para Selectividad)

Imagínate que frotas un globo contra tu pelo y después lo acercas a la pared. El globo se queda pegado, tú pareces haber discutido con un enchufe y, sin darte cuenta, acabas de hacer un experimento de electrostática.

Pero en Selectividad no suelen preguntarte por tu peinado. Te ponen cargas, distancias y un punto donde debes calcular algo. Hoy vamos a conectar esas ideas para que sepas qué fórmula usar, qué significa y cómo evitar los errores típicos.

Vamos allá.

**[En pantalla: «1. La carga eléctrica»]**

La carga eléctrica es una propiedad de la materia. Hay cargas positivas y negativas: las del mismo signo se repelen y las de signos opuestos se atraen.

Su unidad en el Sistema Internacional es el culombio. El electrón tiene carga negativa y el protón, positiva, con el mismo valor absoluto: aproximadamente uno coma seis por diez elevado a menos diecinueve culombios.

Cuando electrizamos un objeto por frotamiento, normalmente transferimos electrones. No estamos creando carga: la carga total de un sistema aislado se conserva.

Y cuidado con las unidades: un microculombio son diez elevado a menos seis culombios; un nanoculombio, diez elevado a menos nueve. Convierte antes de calcular.

**[En pantalla: «2. Ley de Coulomb»]**

La fuerza eléctrica entre dos cargas puntuales se calcula con la ley de Coulomb:

\[
F=k\frac{|q_1q_2|}{r^2}
\]

En el vacío, y aproximadamente en el aire, usamos un valor de k de nueve por diez elevado a nueve, en unidades del Sistema Internacional.

La fuerza aumenta con las cargas y disminuye con el cuadrado de la distancia. Si duplicas la distancia, la fuerza se reduce a la cuarta parte.

Esta fórmula te da el módulo. La dirección es la recta que une ambas cargas, y el sentido depende de si se atraen o se repelen.

Si hay varias cargas, aplica superposición: calcula cada fuerza por separado y después suma los vectores. No sumes los módulos salvo que la geometría lo permita.

**[En pantalla: «3. Campo eléctrico»]**

El campo eléctrico describe qué fuerza experimentaría una carga situada en un punto:

\[
\vec E=\frac{\vec F}{q}
\]

Para una carga puntual, su módulo es:

\[
E=k\frac{|Q|}{r^2}
\]

Se mide en newtons por culombio, equivalentes a voltios por metro.

El campo creado por una carga positiva apunta hacia fuera; el de una negativa, hacia ella. Ese sentido se define usando una carga de prueba positiva.

Por eso, cuando calcules la fuerza sobre una carga mediante:

\[
\vec F=q\vec E
\]

recuerda que, si q es negativa, la fuerza apunta en sentido contrario al campo.

En problemas con varias cargas, dibuja los campos en el punto de estudio, descompón en ejes cuando haga falta y suma componentes.

Primero el dibujo; después las cuentas.

**[En pantalla: «4. Potencial eléctrico»]**

Aquí llega una distinción fundamental: el campo es vectorial; el potencial es escalar.

Tomando el potencial cero en el infinito, el potencial creado por una carga puntual es:

\[
V=k\frac{Q}{r}
\]

Aquí sí conservamos el signo de la carga. Una carga positiva produce potencial positivo; una negativa, potencial negativo.

Con varias cargas, los potenciales se suman algebraicamente. No necesitas descomponerlos en ejes.

Esto explica una pregunta clásica: ¿puede ser cero el potencial en un punto y no ser cero el campo?

Sí. En el punto medio entre dos cargas iguales y opuestas, los potenciales se cancelan, pero los campos tienen el mismo sentido y se suman.

Potencial cero no significa campo cero. Son magnitudes diferentes.

**[En pantalla: «5. Energía potencial y trabajo»]**

Una carga situada en un potencial tiene energía potencial eléctrica:

\[
U=qV
\]

Para dos cargas puntuales:

\[
U=k\frac{q_1q_2}{r}
\]

Con el cero de energía en el infinito, será positiva para cargas del mismo signo y negativa para cargas de signos opuestos.

El trabajo realizado por la fuerza eléctrica al mover una carga desde A hasta B es:

\[
W_{\mathrm{eléctrico}}=-\Delta U=q(V_A-V_B)
\]

Si la fuerza eléctrica realiza trabajo positivo, disminuye la energía potencial.

La fuerza electrostática es conservativa: su trabajo depende de los extremos, no del camino.

Si solo actúa esta fuerza, se conserva la energía mecánica:

\[
\Delta K=-\Delta U
\]

Esta relación es especialmente útil para calcular la velocidad de una partícula acelerada por una diferencia de potencial.

Y distingue siempre el trabajo eléctrico del trabajo de un agente externo: si mueve la carga sin cambiar su energía cinética, su trabajo es igual al aumento de energía potencial.

**[En pantalla: «6. Campo y potencial están relacionados»]**

El campo apunta hacia donde el potencial disminuye más rápidamente.

En una dimensión:

\[
E_x=-\frac{dV}{dx}
\]

En un campo uniforme, entre dos puntos:

\[
V_B-V_A=-\vec E\cdot\Delta\vec r
\]

Por tanto, avanzar en el sentido del campo implica ir hacia potenciales menores.

Pero una carga negativa no tiene por qué moverse en ese sentido: su fuerza apunta al contrario.

Las superficies equipotenciales contienen puntos con el mismo potencial. Desplazar una carga sobre ellas no requiere trabajo de la fuerza eléctrica, y las líneas de campo las cortan perpendicularmente.

**[En pantalla: «7. Conductores y ley de Gauss»]**

En un conductor en equilibrio electrostático, el campo dentro del material conductor es cero y todo el conductor está al mismo potencial. El exceso de carga se distribuye por su superficie.

Si entra en tu temario, recuerda también la ley de Gauss:

\[
\oint \vec E\cdot d\vec S=\frac{Q_{\mathrm{interior}}}{\varepsilon_0}
\]

Relaciona el flujo eléctrico por una superficie cerrada con la carga encerrada. Es especialmente útil cuando existe suficiente simetría para simplificar la integral.

No significa que cualquier superficie permita calcular fácilmente el campo.

**[En pantalla: «Cómo enfrentarte al examen»]**

Antes de sustituir números, identifica qué te piden: fuerza, campo, potencial, energía o trabajo.

Después dibuja la situación y convierte todas las unidades al Sistema Internacional.

Si buscas una magnitud vectorial, fija los ejes y justifica los sentidos. Si buscas potencial o energía, conserva los signos de las cargas.

Finalmente, comprueba las unidades y pregúntate si el resultado tiene sentido físico.

Por ejemplo: si te alejas de una carga puntual aislada, el módulo del campo debe disminuir. Si tus cuentas dicen lo contrario, revisa.

Quédate con estas conexiones: las cargas crean campo y potencial; el campo determina fuerzas; el potencial permite calcular energías y trabajos.

Entender esa estructura vale más que memorizar cinco fórmulas sueltas.

Y ahora sí: cuando veas dos cargas en un examen, empieza por dibujarlas. El primer punto puede estar escondido en una flecha bien puesta.
