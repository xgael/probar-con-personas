<!-- Bloque que sustituye a __HUELLAS__ en persona.md y persona-huellas.md.
     __TAREAS__ = lista numerada con el campo "tarea" de tareas.json (NUNCA el campo "real"). -->
**Tareas: haz cada una y deja tu huella**

__TAREAS__

Para cada tarea, empieza desde la pantalla de inicio (la que sale al entrar) y sigue este protocolo:

1. **Antes de tocar nada**, mira la captura de inicio y escribe dónde esperas encontrarlo y por qué (lo que viste que te hizo pensar eso).
2. Haz el **primer clic** donde lo esperabas. Ese primer lugar es lo más importante de toda la prueba: no lo corrijas aunque después veas que era otro.
3. Sigue hasta lograrlo o rendirte. Ríndete si en 10 clics no lo encuentras o si te frustras como se frustraría tu persona.
4. **En cuanto termines la tarea**, agrega UNA línea a `__DIR__/huellas.jsonl` (un objeto JSON por línea, no un arreglo):

```json
{"tarea": "<id de la tarea>", "espera": "<dónde lo esperabas, en tus palabras>", "porque": "<qué viste que te hizo pensar eso>", "primer_clic": "<dirección (URL) a la que llegaste con el primer clic>", "llego_a": "<dirección donde lo lograste, o vacío si te rendiste>", "pasos": <número de clics>, "resultado": "logrado|rendido|logrado_con_dudas", "captura": "<nombre.png del primer clic>"}
```

Los ids de las tareas son: __IDS__. Copia las direcciones tal como salen en la barra del navegador (`page.url`).
