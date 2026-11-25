---
name: probar-con-personas
description: >
  Pone a varias personas sintéticas (agentes con edad, oficio y torpezas propias) a
  USAR una app web con un navegador real, sin contexto del producto ni acceso al
  código, y trae de vuelta lo que les confundió, frustró o asustó, cada hallazgo con
  su captura. Cubre preparar el terreno (una cuenta por persona, datos listos, foto
  de la base), lanzarlas desacopladas para que sobrevivan al cierre de la sesión,
  verificar cada hallazgo antes de entregarlo, armar una sola página HTML con los
  reportes y limpiar sólo lo que ellas crearon.

  También pone a una persona TRAMPOSA a intentar burlar el sistema y
mide si los demás roles la descubren, y cierra el ciclo: plan de arreglos por tandas con una sonda que repite cada
truco, y una segunda ronda sobre la base restaurada para confirmar. Úsala cuando pidan "pon a 3 personas a usar la plataforma", "que la prueben
  usuarios sin contexto", "manda agentes con distintas edades a revisar X",
  "prueba de usabilidad con personas", "que alguien que no sabe nada la use",
  "pruébalo por roles", "como jefe y como empleado", "con distintos permisos",
  "prueba el flujo de aprobación", "una persona que intente hacer trampa", "a ver si el sistema detecta a
quien no hace lo que debe", "simula el trabajo diario del equipo", "vuelve a lanzar a las personas".

  NO es una auditoría heurística (para eso está ux-audit) ni un test automatizado:
  encuentra dónde se rompe el camino de alguien que no conoce la app, no mide
  tiempos ni reemplaza a usuarios reales.
---

# probar-con-personas

Una persona que nunca vio la app encuentra lo que ningún test ve: un mensaje que
miente, un botón que no parece botón, una palabra de programador en la cara del
usuario, un camino que termina en nada. Esta skill pone a varias a usarla y trae
sus comentarios **con evidencia**.

Salió de una corrida real sobre el módulo de RH de un ERP (octubre de 2026):
3 personas, 61 hallazgos, 137 capturas. Dos de los hallazgos se confirmaron en la base y eran
peores de lo que se veía. Las reglas de abajo existen porque esa misma corrida
falló en cada una de ellas la primera vez.

## Las cinco reglas que no se negocian

1. **Usan el producto, no lo leen.** Navegador real con Playwright, capturas que
   ellas mismas miran con `Read`. Prohibido código, base de datos y API: leyendo
   código dan opiniones genéricas; usando la app encuentran bugs.
2. **Corren desacopladas de la sesión.** Se lanzan con `bin/lanzar.sh`
   (`pc-avisar … claude -p`), nunca con el Agent tool. En la corrida original la primera tanda
   murió con la sesión a los 50 minutos: 218 capturas y cero reportes.
3. **Escriben desde el primer hallazgo.** `reporte.md` se crea al empezar y crece
   hallazgo por hallazgo. Si las cortan, lo escrito queda.
4. **El navegador habla el idioma de la persona.** `locale` y `timezone_id` del
   país de cada una (`es-MX`, `es-CO`…). Con el default `en-US` las fechas salen
   mes/día y los avisos nativos en inglés, y eso parece bug de la plataforma.
5. **Al menos una es usuario común con datos listos.** Si todas entran como
   admin, nadie prueba el camino de la mayoría. Y si a nadie le cargaste los
   datos (días de vacaciones, saldo, inventario), el flujo principal no se puede
   recorrer y el reporte se llena de «está vacío».

## Paso 1 · Preparar el terreno (antes de lanzar nada)

- **Stack arriba** y la URL respondiendo. Mientras corran, **no edites el
  frontend**: el hot reload les cambia la app a media prueba.
- **Una cuenta por persona**, para que no se pisen. Mide qué ve cada cuenta (por
  la API de permisos o entrando), no lo supongas: en la corrida original las tres cuentas de
  RH veían las 10 pantallas y las de empleado sólo 5.
- **Esa medición decide el modo.** Si las cuentas disponibles ven pantallas
  distintas (permisos distintos), se usa el **modo por roles** por omisión, aunque
  nadie lo haya pedido. Si todas ven lo mismo, el modo normal. Anota en la
  entrega cuál se usó y la medición que lo decidió.
- **Datos listos** para el flujo principal de la persona común.
- **Marca por persona** (`[prueba-<nombre>]`) para todo lo que escriban. Es lo
  único que permite limpiar después sin tocar datos ajenos.
- **Foto de la base** si es local: conteo por tabla del módulo, para saber
  después qué escribieron. Nunca contra producción.
- **Respaldo completo** (`pg_dump -Fc … -f <dir-base>/antes-de-personas.dump`) cuando alguna persona puede escribir sobre
  lo ajeno (la tramposa, quien aprueba): la limpieza por marca no alcanza, y es la base de la segunda ronda.
- **Cuentas nuevas por el mecanismo del propio proyecto** (su script de usuarios de prueba, no `INSERT` a mano): un rol
  que falta (quien captura, la tramposa) se crea con el mismo servicio que hashea contraseñas y asigna roles.
- **Python con Playwright, aparte del proyecto**: `python3 -m venv ~/.venvs/personas && ~/.venvs/personas/bin/pip install
  playwright pillow && ~/.venvs/personas/bin/python -m playwright install chromium` (va en `__PYTHON__`).
- **Prueba de humo** antes de lanzar: entrar con una cuenta en escritorio y en celular y mirar la captura. En celular la
  entrada puede pedir un toque antes del formulario («Iniciar sesión»): dilo en el prompt o la persona de celular se atora.
- **Datos para la cadena**: lo que cada rol debe resolver tiene que estar esperando (un descuento por aprobar, leads por
  repartir, un lead a punto de vencer, una venta vieja de la tramposa). Si mueves fechas para simularlo («entregado hace
  20 h»), anótalo en la verificación: las personas lo reportarán como dato raro.
- **Una configuración vacía que apaga un flujo es un hallazgo**: si el tarifario no tiene topes, nadie pide aprobar
  descuentos y el rol que aprueba no tiene nada que probar. Lo mínimo se siembra con marca y se dice en la entrega.

## Paso 2 · Elegir las personas

Por omisión, **cinco** (`plantillas/perfiles.md`): tres de **opinión** que
difieren en *cómo fallan* (vista y pulso, prisa, miedo a romper, vocabulario) y
dos de **huellas** que sólo hacen las tareas, para que los patrones salgan de
cinco caminos y no de tres. Una de las de huellas va con cuenta de empleado
común. Si el usuario pide otras, respeta sus perfiles y conserva las dos de
huellas. Cada persona cuesta de 30 a 60 minutos.

Si piden saber si el sistema descubre a quien hace trampa, suma una **persona tramposa** (ver su sección) a las cinco:
no reemplaza a ninguna, porque las demás son las que tienen que descubrirla.

## Paso 2b · Tareas y mapa real (los senderos de deseo)

La idea viene del Oval de Ohio State: el plan geométrico de 1914 no se terminó
y los estudiantes abrieron sus propios senderos, que con los años se
pavimentaron. Aquí se mide eso en una hora: **dónde busca la gente primero**.

Escribe `<dir-base>/tareas.json` con 3 a 5 tareas comunes a todas las personas:

```json
{"tareas": [
  {"id": "vacaciones", "tarea": "Pide unos días de vacaciones",
   "real": ["/rh/vacaciones"], "clasificacion": ""}
]}
```

- `tarea` va en palabras de quien usa la app, **nunca** con el nombre de la
  pantalla («ve a Mi espacio» ya le da el camino).
- `real` es el mapa: dónde vive de verdad la función (una o varias rutas). Lo
  sabes tú; a las personas sólo se les da `tarea` e `id`.
- `clasificacion` se llena en el paso 4.

## Modo por roles (se enciende solo)

Se activa cuando la medición del paso 1 encuentra cuentas con permisos
distintos, o cuando lo piden. Cuando la app tiene roles (empleado, jefe,
administrador…), cada persona
recibe además un **rol**, y las tareas son las de ese rol. El perfil (cómo
falla) y el rol (qué puede hacer) son independientes: una jefa puede ser la que
casi no usa internet. Cinco cosas que el modo normal no necesita:

1. **Persona → rol → cuenta, medido.** Antes de lanzar, entra con cada cuenta
   (o pregunta a la API de permisos) y cuenta qué pantallas ve. Una cuenta que
   no ve la pantalla de su tarea produce un «me rendí» que no es de UX.
2. **Tareas con `rol` en `tareas.json`** (`"rol": "Jefa de equipo"`). Cada
   persona recibe sólo las de su rol; dos personas del mismo rol comparten
   tareas para que sus senderos se puedan comparar. `armar.py` agrupa la tabla
   de senderos por rol.
3. **La cadena necesita algo esperando.** Quien aprueba sólo prueba algo si hay
   pendientes reales de su gente: créalos en la preparación (con marca) o
   lanza primero a quien pide. Anota en `tareas.json` qué tarea depende de cuál.
4. **Permiso explícito sobre lo ajeno.** La regla «no toques lo que no creaste»
   choca con tareas como aprobar o editar la ficha de otro: la persona se rinde
   por respetarla y el hallazgo es falso. Sustituye `__AJENO__` en la plantilla
   por la lista exacta de registros de prueba que sí puede aprobar, rechazar o
   editar (por nombre o marca). En el modo normal, `__AJENO__` va vacío.
5. **Verificación cruzada.** Además de cada hallazgo, busca los casos que
   **ningún** rol puede resolver: una solicitud que «resuelve RH» cuando la
   única persona de RH es quien la pidió; un aviso que llega a quien no puede
   actuar. Eso no lo ve ninguna persona sola: sale de cruzar los roles.

## Persona tramposa (modo adversario)

Cuando la pregunta es «¿el sistema descubre a quien no hace lo que debe?», agrega una persona con
`plantillas/persona-tramposa.md`: alguien de un rol común (un vendedor bajo su cuota) que intenta verse mejor de lo que es
**desde la pantalla**: cerrar ventas que no existen, decir que llamó o mandó cuando no, fechas atrasadas, quedarse con lo
de otros, aprobarse lo propio, mandarle basura a un compañero, borrar el rastro. `__TRUCOS__` lleva esa lista en
palabras del oficio; sus tareas (`tareas.json`, rol «… tramposo») son los mismos trucos, para que deje huellas. Su
reporte termina con dos tablas: **Trucos que funcionaron** (¿deja rastro?, ¿dónde lo vería el jefe?) y **Trucos que el
sistema frenó**.

- Lánzala en la primera tanda y a quien debe descubrirla (la líder, con la tarea «sospechas que alguien te maquilla los
  números: búscalo») después.
- **Verifica cada truco en la base con sus marcas de tiempo**: la orden «enviada» y confirmada con segundos de diferencia,
  el contacto con `fecha` de hace semanas y `created_at` de hoy. Esas diferencias son las reglas que el sistema puede
  vigilar solo.
- El hallazgo no es sólo «pasó»: es **quién se enteró y dónde**. «La directora lo encontró leyendo renglón por renglón»
  es un hallazgo tan grave como el truco.
- No es una prueba de penetración: no usa la API, el código ni la base (eso es la revisión adversarial del proyecto).

No confundir con una auditoría de permisos (quién puede ver o hacer qué, y si
un candado se puede saltar): eso es seguridad, se prueba como atacante y no es
lo que mide esta skill.

## Paso 3 · Lanzar

Por persona, una carpeta con su `rol.md` y un `prompt.txt` armado desde
`plantillas/persona.md` (opinión) o `plantillas/persona-huellas.md` (huellas).
`__HUELLAS__` se sustituye por `plantillas/huellas.md`, y dentro de él
`__TAREAS__` (lista numerada sólo con el campo `tarea`) y `__IDS__`.
`__AJENO__` va vacío, salvo en modo por roles (ver arriba). `__SESION__` lleva la regla de **entrar una
sola vez** (la pantalla de entrada suele tener límite por minuto y cinco personas lo agotan):

> Entra una vez, guarda la sesión con `context.storage_state(path="__DIR__/sesion.json")` y en los scripts siguientes ábrela
> con `browser.new_context(storage_state="__DIR__/sesion.json", ...)`. Si te saca, vuelve a entrar y guárdala otra vez.

Verifica con `grep -c __ prompt.txt` que quede en 0. Luego:

```bash
bash ~/.claude/skills/probar-con-personas/bin/lanzar.sh /tmp/personas-<app> valeria rogelio lupita directo costumbre
```

Cada persona corre aparte y, al terminar, `pc-avisar` manda su `reporte.md` por
el canal del bot. Si `pc-avisar` no existe, el script cae a `nohup` y avisa.

- **Chequeo de vida**: con `PC_URL=<url> bash …/lanzar.sh …` no lanza si la app no contesta. Y mientras corren,
  `bash …/bin/vigilar.sh <dir-base> <url>` en segundo plano espera a que terminen, avisa si la app se cae y deja el conteo
  de capturas, reporte y huellas. No esperes con `sleep` encadenados.
- **Una corrida que no pudo entrar no cuenta**: si un reporte dice «no pude entrar», levanta la app, mueve lo que dejó
  cada persona a `<dir-base>/fallidas/<persona>/` (deja `prompt.txt` y `rol.md`) y relánzala. `lanzar.sh` no relanza a
  quien ya tiene `reporte.md`.
- **Tandas cuando un rol depende de lo que hace otro**: primero quienes generan (la tramposa, quien captura, quien pide) y,
  al terminar, quien revisa o descubre (la líder). Así la líder encuentra lo que dejó la tramposa.

**No predigas resultados mientras corren.** Si preguntan, di cuántas capturas y
cuántas líneas de reporte llevan (`ls`, `wc -l`), nada más.

## Paso 4 · Verificar antes de entregar

Cada hallazgo grave se comprueba **en la app o en la base**, no se copia:

- Lo que dicen que pasó, ¿pasó? (En la corrida original, «llegó a 146 personas» llegó a 4.)
- ¿Es de la plataforma o de la prueba? Separa: idioma del navegador, datos de
  demo, la propia marca `[prueba-…]` en un avatar.
- ¿Lo vieron varias? Lo que coincide entre personas que no hablaron entre sí es
  la señal más fuerte para priorizar.
- **Clasifica cada sendero de deseo** (2 o más personas buscando primero en el
  mismo lugar equivocado; `armar.py` los marca solo) y escríbelo en
  `clasificacion` de `tareas.json`. No todo atajo se pavimenta:
  - `pavimentar`: llevar o duplicar la función donde la buscan.
  - `con barandilla`: pavimentar, pero con confirmación o deshacer, porque el
    atajo puede hacer daño (un aviso a cientos de personas en un clic).
  - `no pavimentar`: el atajo se salta algo necesario; se explica en la
    pantalla en vez de abrirlo.

## Paso 5 · Entregar

Una sola página HTML, sin dependencias, con las capturas embebidas:

```bash
python3 ~/.claude/skills/probar-con-personas/bin/armar.py /tmp/personas-<app> <salida.html>
```

Lee `sesion.json` (título, personas, cuentas) y los `reporte.md` de cada carpeta.
Si hay `tareas.json`, cruza el `huellas.jsonl` de cada persona y arma la sección
**Senderos de deseo**: por tarea, cuántas acertaron al primer clic, cuántas lo
lograron, qué lugar equivocado eligieron 2 o más y tu decisión; con el detalle
por persona (qué esperaba, por qué, a dónde fue). Avisa en consola si a alguien
le falta el archivo o tiene líneas ilegibles.
Antes de correrlo escribe tú, en la misma carpeta:

- `sintesis.html`: la tabla de lo que se repite entre personas (problema,
  **principio**, dónde, quién lo vio). El principio sale de
  `plantillas/principios.md`, con su enlace a NN/g; si ninguno encaja sin
  forzarlo, la celda queda vacía.
- `verificacion.html`: lo que comprobaste, en notas `mal` (confirmado),
  `ojo` (matiz) y `ver` (no es de la plataforma).

Los reportes van **completos y en su voz**: tu lectura va aparte, rotulada como
tuya. Abre la página en un navegador y mide: pestañas, visor de capturas, Esc,
consola sin errores y sin scroll horizontal en 390 px.

## Paso 5b · Seguimiento: palomitas de lo que se va arreglando

Cada hallazgo sale en la página con una **casilla y un id estable**
(`<persona>-<n>`, p. ej. `valeria-3`), y `armar.py` deja junto a los reportes
`pendientes.md`: la lista de ids con el comando para marcarlos. Quien arregla
(una persona o un agente) marca así, y la página se regenera sola si
`sesion.json` trae `"salida"` (ruta del HTML); con `"repo"` (URL de GitHub), la
palomita enlaza al commit:

```bash
python3 ~/.claude/skills/probar-con-personas/bin/marcar.py <dir-base> valeria-3 en_curso --por "quién"
python3 ~/.claude/skills/probar-con-personas/bin/marcar.py <dir-base> valeria-3 resuelto --commit <sha> --por "quién"
python3 ~/.claude/skills/probar-con-personas/bin/marcar.py <dir-base> directo-5 descartado --nota "no es de la plataforma: …"
python3 ~/.claude/skills/probar-con-personas/bin/marcar.py <dir-base> --lista
```

- **«resuelto» exige el commit**: la palomita verde enlaza al cambio, no es una
  promesa. **«descartado» exige la nota** con el porqué.
- Varios agentes pueden marcar a la vez: `marcar.py` escribe con candado.
- Al entregar a quien va a arreglar, pásale la ruta de `pendientes.md`.
- Una palomita no sustituye a la siguiente vuelta: lo resuelto se confirma
  volviendo a lanzar a las personas.
- **Hallazgos visuales** («se corta», «no veo la columna», «está encima», «letra
  chica»): antes de arreglarlos, reprodúcelos con la skill `pulir-interfaz` en el
  tamaño de la persona (zoom, celular). Los vuelve número, encuentra la primitiva
  que los causa y, al re-medir, las regresiones que el arreglo dejó en otro tamaño.

## Paso 6 · Limpiar

Borra sólo lo que lleve la marca de cada persona, en la base local, comparando
contra la foto del paso 1. Nada por posición ni por fecha.

## Paso 7 · Del hallazgo al arreglo y la segunda ronda

Las personas no son el final, y **arreglar no espera a que lo pidan**: en cuanto la verificación y la página están
entregadas, se arregla en el mismo turno. Pedir permiso hallazgo por hallazgo retrasa y quita visibilidad. El ciclo que
sirvió en Comercial (24-25 nov 2026, 54 y 61 hallazgos):

1. **Persona por persona, en el orden de la página.** Se toma el reporte de UNA persona, se arregla todo lo suyo que es
   de la plataforma, se mide, se hace su commit y se marca cada id con `marcar.py` (`resuelto` con el commit; `descartado`
   con la nota si es de la prueba o del ambiente). Sólo entonces se pasa a la siguiente persona: así cada quien ve su
   reporte cerrado y lo que se repite entre personas se arregla una vez (en la segunda se marca con el mismo commit).
   - **Sólo se detiene** en lo que no es de quien arregla: una decisión de negocio («¿qué pide el sistema para dar por
     ganada una venta?»), subir a un servidor o mandar algo afuera. Esas preguntas se juntan y se hacen una vez, al
     empezar, sin frenar lo demás; lo que dependa de la respuesta queda `en_curso` con su nota.
   - Cada hallazgo queda en un estado: resuelto (con commit), descartado (con razón) o pendiente con lo que le falta. Al
     final, «¿ya parchaste todo?» se contesta con `marcar.py --lista`, no de memoria.
   - Si hay varias personas con mucho trabajo, cada una puede ir en un subagente, **una tras otra** (tocan los mismos
     archivos), con el reporte, los ids y las reglas del proyecto en su encargo.
2. **Cada persona (o tanda) trae una sonda que repite lo que hicieron las personas** por la API (los trucos de la tramposa, el flujo
   de quien aprueba) y comprueba que ahora se frena o queda marcado, más las sondas viejas del módulo (un arreglo cambia
   contratos: confirmar ahora pide un archivo y las sondas viejas también).
3. **Pantallas** de lo tocado en escritorio, celular y zoom, recorridas con el rol de quien lo usa.
4. **Segunda ronda** con las mismas personas, roles y tareas, sobre la base **restaurada** desde `antes-de-personas.dump`
   (más las migraciones nuevas) y respaldando antes lo que dejó la primera. Refresca lo que caducó en la preparación (un
   lead que debía estar a 20 h de vencer ya venció).
5. **Compara**: en `verificacion.html`, una nota con lo que mejoró (tareas logradas, clics, quién arrancó dónde) y lo que
   sigue; en la síntesis, lo nuevo. Una segunda ronda encuentra **lo que rompió el arreglo** (en Comercial: poner en sólo
   lectura las líneas de quien aprueba le quitó el precio de lista) y **trucos nuevos** contra las reglas nuevas.
6. **Entrega honesta**: lo arreglado con su medición y lo que sigue abierto, con su razón. Marca cada hallazgo con
   `marcar.py` mientras arreglas: «¿ya parchaste todo?» se contesta con la lista, no de memoria.

Para que el usuario lea todo, copia los `reporte.md` de cada ronda a su carpeta de documentos (`rondaN/<persona>.md`)
junto a las páginas: las capturas viven en `<dir-base>` y las páginas ya las traen dentro.

## Límites honestos

- Son agentes actuando un papel, no personas: a veces se les escapa el
  personaje (un «señor de 71 años» que reporta píxeles medidos). Encuentran
  dónde se rompe el camino; no miden tiempo ni frustración real.
- Si el producto necesita datos que no existen, reportarán vacíos. Eso es un
  hallazgo de preparación, no de UX.
- La tramposa prueba lo que un usuario astuto haría en la pantalla. Lo que el sistema no puede saber (si un archivo
  «del cliente» es auténtico, si una llamada declarada ocurrió) no se cierra con reglas: se hace visible a quien revisa.
- Escriben en la base: sólo sobre una base de desarrollo, nunca producción.
- **Esto es la nieve, no el pasto.** Las huellas de cinco personas en una hora
  son una foto rápida de por dónde *empezaría* la gente. El pasto gastado se
  mide en producción con usuarios reales: búsquedas sin resultado, clics
  repetidos en botones deshabilitados, idas y vueltas entre pantallas. Conviene
  recomendar instrumentarlo; queda fuera de esta skill.

## Requisitos

`claude` CLI, `pc-avisar` (o `nohup`), `curl` (chequeo de vida), un Python con `playwright` + Chromium
(indícalo en `__PYTHON__` de la plantilla; ver Paso 1) y `pillow` para `armar.py`.
