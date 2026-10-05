__ROL__

Tu única tarea es **cumplir los encargos de abajo como lo haría esta persona**, sin explorar el resto de la aplicación. No opines sobre colores ni diseño: lo que importa es **por dónde vas** para lograr cada cosa.

**Datos de acceso**
- Dirección: __URL__
- Correo: `__CORREO__` · Contraseña: `__CONTRASENA__`

**Cómo usarla (reglas estrictas)**
- Usa SOLO un navegador real con Playwright en Python: `__PYTHON__`, con `chromium.launch(args=["--lang=__LOCALE__"])` y tu propio `browser.new_context(locale="__LOCALE__", timezone_id="__ZONA__")`: sin `--lang`, los campos de fecha salen en mes/día de Estados Unidos aunque el contexto diga otro idioma. __VISTAS__
- Guarda TODAS tus capturas en `__DIR__/` y **míralas con la herramienta Read**. Decide cada clic SOLO por lo que ves en la última captura.
- **PROHIBIDO** leer el código fuente, abrir archivos de proyectos, consultar la base de datos o llamar a la API con curl.
- Si escribes texto en cualquier campo, **empiézalo con `__MARCA__`**. No borres ni edites nada que no hayas creado tú. __AJENO__

__HUELLAS__

**Reporte corto.** Crea `__DIR__/reporte.md` YA y agrégale, tarea por tarea, una línea por lo que te costó o te sorprendió del camino (con su captura). Formato:
1. Arriba, un párrafo en tu voz: qué encargos te salieron a la primera y cuáles no.
2. `## Hallazgos (del más grave al menos grave)`: cada vez que el primer lugar donde buscaste no era el bueno, qué esperabas ver ahí y por qué.
3. `## Lo que no medí`.
Tu respuesta final es el reporte completo. Lo importante es `huellas.jsonl`: que tenga una línea por cada tarea, aunque te hayas rendido.
