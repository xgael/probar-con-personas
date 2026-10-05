# probar-con-personas

Skill de Claude Code que pone a varias **personas sintéticas** (agentes con edad,
oficio y torpezas propias) a **usar** una app web con un navegador real, sin
contexto del producto ni acceso al código, y trae lo que les confundió, frustró
o asustó, cada hallazgo con su captura.

No es una auditoría heurística ni un test automatizado: encuentra dónde se rompe
el camino de alguien que no conoce la app.

## Qué trae

| Archivo | Para qué |
|---|---|
| `SKILL.md` | El método: preparar, elegir personas, lanzar, verificar, entregar, limpiar |
| `plantillas/perfiles.md` | Perfiles probados y cómo falla cada uno |
| `plantillas/persona.md` | Instrucciones de cada persona, con marcadores a sustituir |
| `plantillas/principios.md` | Del síntoma que reportan al principio de NN/g que lo explica |
| `bin/lanzar.sh` | Lanza cada persona como sesión `claude -p` desacoplada |
| `bin/armar.py` | Una sola página HTML con los reportes y las capturas embebidas |

## Instalación

```bash
git clone https://github.com/xgael/probar-con-personas ~/.claude/skills/probar-con-personas
```

Requiere el CLI `claude`, Python con `playwright` + Chromium y `pillow`.

## Licencia

MIT
