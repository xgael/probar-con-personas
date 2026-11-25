#!/usr/bin/env bash
# Espera a que terminen las personas lanzadas y, mientras, vigila que la app siga arriba.
# Uso: vigilar.sh <dir-base> <url> [<minutos-máximo>=120]
# Pensado para correr en segundo plano (run_in_background): avisa al terminar con el conteo de cada persona.
# Si la URL deja de contestar, lo dice con la hora: una persona que no puede entrar reporta «no pude entrar» y su
# reporte no sirve (pasó en la segunda ronda de Comercial, 25-nov-2026: el frontend se cayó y tres personas
# entregaron «la aplicación no responde»).
set -uo pipefail
BASE="${1:?Uso: vigilar.sh <dir-base> <url> [minutos]}"; URL="${2:?Falta la URL}"; MAX="${3:-120}"
caida=0
for _ in $(seq 1 "$MAX"); do
  vivas=$(ps -Ao command | grep -c "^claude -p " || true)
  if ! curl -s -o /dev/null --max-time 10 "$URL"; then echo "APP CAÍDA $(date +%T): $URL no contesta"; caida=1; fi
  [ "$vivas" -eq 0 ] && break
  sleep 60
done
for d in "$BASE"/*/; do
  [ -f "$d/prompt.txt" ] || continue
  n=$(basename "$d")
  printf '%s: %s capturas · reporte %s líneas · huellas %s\n' "$n" \
    "$(find "$d" -maxdepth 2 -name '*.png' | wc -l | tr -d ' ')" \
    "$( [ -f "$d/reporte.md" ] && wc -l < "$d/reporte.md" | tr -d ' ' || echo 0)" \
    "$( [ -f "$d/huellas.jsonl" ] && wc -l < "$d/huellas.jsonl" | tr -d ' ' || echo 0)"
done
[ "$caida" -eq 1 ] && echo "OJO: la app se cayó durante la prueba; revisa si algún reporte dice que no pudo entrar." || true
