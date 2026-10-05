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

  Úsala cuando pidan "pon a 3 personas a usar la plataforma", "que la prueben
  usuarios sin contexto", "manda agentes con distintas edades a revisar X",
  "prueba de usabilidad con personas", "que alguien que no sabe nada la use".

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
- **Datos listos** para el flujo principal de la persona común.
- **Marca por persona** (`[prueba-<nombre>]`) para todo lo que escriban. Es lo
  único que permite limpiar después sin tocar datos ajenos.
- **Foto de la base** si es local: conteo por tabla del módulo, para saber
  después qué escribieron. Nunca contra producción.

## Paso 2 · Elegir las personas

Por omisión, **cinco** (`plantillas/perfiles.md`): tres de **opinión** que
difieren en *cómo fallan* (vista y pulso, prisa, miedo a romper, vocabulario) y
dos de **huellas** que sólo hacen las tareas, para que los patrones salgan de
cinco caminos y no de tres. Una de las de huellas va con cuenta de empleado
común. Si el usuario pide otras, respeta sus perfiles y conserva las dos de
huellas. Cada persona cuesta de 30 a 60 minutos.

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

## Modo por roles (opcional)

Cuando la app tiene roles (empleado, jefe, administrador…), cada persona
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

No confundir con una auditoría de permisos (quién puede ver o hacer qué, y si
un candado se puede saltar): eso es seguridad, se prueba como atacante y no es
lo que mide esta skill.

## Paso 3 · Lanzar

Por persona, una carpeta con su `rol.md` y un `prompt.txt` armado desde
`plantillas/persona.md` (opinión) o `plantillas/persona-huellas.md` (huellas).
`__HUELLAS__` se sustituye por `plantillas/huellas.md`, y dentro de él
`__TAREAS__` (lista numerada sólo con el campo `tarea`) y `__IDS__`.
`__AJENO__` va vacío, salvo en modo por roles (ver arriba). Verifica
con `grep -c __ prompt.txt` que quede en 0. Luego:

```bash
bash ~/.claude/skills/probar-con-personas/bin/lanzar.sh /tmp/personas-<app> valeria rogelio lupita directo costumbre
```

Cada persona corre aparte y, al terminar, `pc-avisar` manda su `reporte.md` por
el canal del bot. Si `pc-avisar` no existe, el script cae a `nohup` y avisa.

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

## Paso 6 · Limpiar

Borra sólo lo que lleve la marca de cada persona, en la base local, comparando
contra la foto del paso 1. Nada por posición ni por fecha.

## Límites honestos

- Son agentes actuando un papel, no personas: a veces se les escapa el
  personaje (un «señor de 71 años» que reporta píxeles medidos). Encuentran
  dónde se rompe el camino; no miden tiempo ni frustración real.
- Si el producto necesita datos que no existen, reportarán vacíos. Eso es un
  hallazgo de preparación, no de UX.
- Escriben en la base: sólo sobre una base de desarrollo, nunca producción.
- **Esto es la nieve, no el pasto.** Las huellas de cinco personas en una hora
  son una foto rápida de por dónde *empezaría* la gente. El pasto gastado se
  mide en producción con usuarios reales: búsquedas sin resultado, clics
  repetidos en botones deshabilitados, idas y vueltas entre pantallas. Conviene
  recomendar instrumentarlo; queda fuera de esta skill.

## Requisitos

`claude` CLI, `pc-avisar` (o `nohup`), un Python con `playwright` + Chromium
(indícalo en `__PYTHON__` de la plantilla) y `pillow` para `armar.py`.
