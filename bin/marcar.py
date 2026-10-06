#!/usr/bin/env python3
"""Marca el avance de un hallazgo y vuelve a generar la página.

Uso:
  marcar.py <dir-base> <id> resuelto   --commit <sha> [--por "quién"] [--nota "..."]
  marcar.py <dir-base> <id> en_curso   [--por "quién"] [--nota "..."]
  marcar.py <dir-base> <id> descartado --nota "por qué no es de la plataforma" [--por "quién"]
  marcar.py <dir-base> <id> pendiente                      (deshace la marca)
  marcar.py <dir-base> --lista                             (ids y estado)

«resuelto» exige el commit: la palomita enlaza al cambio, no es una promesa.
«descartado» exige la nota: decir por qué no se arregla.
Si sesion.json trae "salida" (ruta del HTML), la página se regenera ahí.
"""
import argparse, datetime, json, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADOS = ('pendiente', 'en_curso', 'resuelto', 'descartado')

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('base')
ap.add_argument('id', nargs='?')
ap.add_argument('estado', nargs='?', choices=ESTADOS)
ap.add_argument('--commit')
ap.add_argument('--por')
ap.add_argument('--nota')
ap.add_argument('--lista', action='store_true')
a = ap.parse_args()

sesion = json.load(open(os.path.join(a.base, 'sesion.json'), encoding='utf-8'))
ruta_estado = os.path.join(a.base, 'estado.json')
# Candado: leer-modificar-escribir bajo un lock exclusivo, para que dos agentes que
# marcan a la vez no se pisen (sin él, la segunda escritura borra la primera marca).
import fcntl
_candado = open(ruta_estado + '.lock', 'w')
fcntl.flock(_candado, fcntl.LOCK_EX)
estado = json.load(open(ruta_estado, encoding='utf-8')) if os.path.isfile(ruta_estado) else {}


def ids_validos():
    """Los mismos ids que pone armar.py: <dir>-<n> de cada hallazgo numerado."""
    v = []
    for p in sesion['personas']:
        f = os.path.join(a.base, p['dir'], 'reporte.md')
        if not os.path.isfile(f):
            continue
        for s in re.split(r'\n## ', open(f, encoding='utf-8').read()):
            if s.lower().startswith('hallazgos'):
                # Mismo patrón que armar.py: «### 3. …» o «### H3 · …».
                nums = re.findall(r'^### H?(\d+)\s*[.·:—-]', s, re.M) or re.findall(r'^(\d+)\.\s', s, re.M)
                v += [f'{p["dir"]}-{n}' for n in nums]
    return v


validos = ids_validos()
if a.lista:
    for hid in validos:
        e = estado.get(hid, {})
        print(f'{hid:16} {e.get("estado", "pendiente"):11} {e.get("commit", "")[:7]:8} {e.get("por", "")}')
    sys.exit(0)
if not a.id or not a.estado:
    ap.error('faltan <id> y <estado> (o usa --lista)')
if a.id not in validos:
    sys.exit(f'No existe el hallazgo «{a.id}». Ids válidos: {", ".join(validos)}')
if a.estado == 'resuelto' and not a.commit:
    sys.exit('«resuelto» necesita --commit <sha>: la palomita tiene que enlazar al cambio')
if a.estado == 'descartado' and not a.nota:
    sys.exit('«descartado» necesita --nota con el porqué')
if a.commit and not re.fullmatch(r'[0-9a-f]{7,40}', a.commit):
    sys.exit(f'Commit inválido: {a.commit}')

if a.estado == 'pendiente':
    estado.pop(a.id, None)
else:
    estado[a.id] = {k: v for k, v in {
        'estado': a.estado, 'commit': a.commit, 'por': a.por, 'nota': a.nota,
        'fecha': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}.items() if v}
tmp = ruta_estado + '.tmp'
json.dump(estado, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
os.replace(tmp, ruta_estado)  # escritura atómica: dos agentes marcando a la vez no dejan un JSON roto
print(f'{a.id}: {a.estado}')

if sesion.get('salida'):
    r = subprocess.run([sys.executable, os.path.join(AQUI, 'armar.py'), a.base, os.path.expanduser(sesion['salida'])],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
