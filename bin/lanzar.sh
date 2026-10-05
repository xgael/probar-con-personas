#!/usr/bin/env bash
# Lanza cada persona como una sesión `claude -p` DESACOPLADA de la sesión actual.
# Uso: lanzar.sh <dir-base> <persona> [<persona> ...]
# Cada <dir-base>/<persona>/ debe traer prompt.txt (sin __MARCADORES__ sueltos).
set -euo pipefail

BASE="${1:?Uso: lanzar.sh <dir-base> <persona> [<persona> ...]}"; shift
[ "$#" -gt 0 ] || { echo "Falta al menos una persona" >&2; exit 2; }
command -v claude >/dev/null || { echo "No está el CLI claude en el PATH" >&2; exit 1; }

for p in "$@"; do
  D="$BASE/$p"
  [ -f "$D/prompt.txt" ] || { echo "Falta $D/prompt.txt" >&2; exit 1; }
  # Candado: relanzar sobre una persona que ya terminó la vuelve a poner a
  # escribir en la app y sobre su reporte. Sólo con RETOMAR=1, a propósito.
  if [ -s "$D/reporte.md" ] && [ "${RETOMAR:-0}" != "1" ]; then
    echo "$p ya tiene reporte.md: no la relanzo. Si de verdad quieres que retome, RETOMAR=1." >&2; exit 1
  fi
  if grep -q '__[A-Z]*__' "$D/prompt.txt"; then
    echo "$D/prompt.txt tiene marcadores sin sustituir:" >&2
    grep -o '__[A-Z]*__' "$D/prompt.txt" | sort -u >&2; exit 1
  fi
done

for p in "$@"; do
  D="$BASE/$p"
  CMD=(claude -p "$(cat "$D/prompt.txt")" --allowedTools "Bash Read Write Edit Glob" --add-dir "$D")
  if command -v pc-avisar >/dev/null; then
    ( cd "$D" && nohup pc-avisar --nombre "persona-$p" --adjunto "$D/reporte.md" -- "${CMD[@]}" \
        > "$D/salida.log" 2>&1 < /dev/null & )
  else
    echo "AVISO: sin pc-avisar; $p corre con nohup y no avisará al terminar" >&2
    ( cd "$D" && nohup "${CMD[@]}" > "$D/salida.log" 2>&1 < /dev/null & )
  fi
  echo "lanzada: $p -> $D"
done

sleep 5
echo "--- vivas ---"
ps -Ao pid,etime,command | grep -E "claude -p" | grep -v grep | cut -c1-100 || true
