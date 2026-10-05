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

Usa los perfiles de `plantillas/perfiles.md` o los que pida el usuario. Que
difieran en **cómo fallan**, no sólo en la edad: vista y pulso, prisa e
impaciencia, miedo a romper, vocabulario. Tres a cuatro bastan; cada una cuesta
de 30 a 60 minutos.

## Paso 3 · Lanzar

Por persona, una carpeta con su `rol.md` y un `prompt.txt` armado desde
`plantillas/persona.md` (sustituye los `__MARCADORES__`; verifica con
`grep -c __ prompt.txt` que quede en 0). Luego:

```bash
bash ~/.claude/skills/probar-con-personas/bin/lanzar.sh /tmp/personas-<app> valeria rogelio lupita
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

## Paso 5 · Entregar

Una sola página HTML, sin dependencias, con las capturas embebidas:

```bash
python3 ~/.claude/skills/probar-con-personas/bin/armar.py /tmp/personas-<app> <salida.html>
```

Lee `sesion.json` (título, personas, cuentas) y los `reporte.md` de cada carpeta.
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

## Requisitos

`claude` CLI, `pc-avisar` (o `nohup`), un Python con `playwright` + Chromium
(indícalo en `__PYTHON__` de la plantilla) y `pillow` para `armar.py`.
