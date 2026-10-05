#!/usr/bin/env python3
"""Arma UNA página HTML (sin dependencias, capturas embebidas) con los reportes.

Uso: armar.py <dir-base> <salida.html>

<dir-base>/sesion.json:
  {"titulo": "...", "contexto": "App X · Módulo Y · fecha", "intro": "...",
   "personas": [{"dir": "valeria", "nombre": "Valeria", "perfil": "17 años · prepa",
                 "cuenta": "rh@test.com", "modo": "Escritorio y celular"}]}
<dir-base>/<dir>/reporte.md       — lo que escribió cada persona (va completo)
<dir-base>/sintesis.html          — opcional: <tr> de la tabla «lo que se repite», 4 celdas:
                                    problema · principio (enlace) · dónde · quién lo vio
<dir-base>/verificacion.html      — opcional: notas <div class="nota mal|ojo|ver">
"""
import base64, html, io, json, os, re, sys
from PIL import Image

if len(sys.argv) != 3:
    sys.exit(__doc__)
BASE, DST = sys.argv[1], sys.argv[2]
AQUI = os.path.dirname(os.path.abspath(__file__))
sesion = json.load(open(os.path.join(BASE, 'sesion.json'), encoding='utf-8'))
imgs = {}  # (dir, nombre) -> (id, base64)


def img_id(d, nombre):
    k = (d, nombre)
    if k in imgs:
        return imgs[k][0]
    p = os.path.join(BASE, d, nombre)
    if not os.path.isfile(p):
        return None
    im = Image.open(p).convert('RGB')
    if im.width > 1000:
        im = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
    if im.height > 2400:  # capturas de página completa: basta el primer tramo
        im = im.crop((0, 0, im.width, 2400))
    b = io.BytesIO()
    im.save(b, 'JPEG', quality=68, optimize=True)
    imgs[k] = (f'i{len(imgs)}', base64.b64encode(b.getvalue()).decode())
    return imgs[k][0]


def inline(t, d):
    t = html.escape(t, quote=False)

    def capt(m):
        nombre = os.path.basename(m.group(0))
        i = img_id(d, nombre)
        if not i:
            return html.escape(nombre)
        return f'<button class="cap" data-i="{i}" type="button">📷 {html.escape(nombre)}</button>'

    t = re.sub(r'`([^`]*?\.png)`', lambda m: m.group(1), t)
    t = re.sub(r'(?:/[\w.-]+)*/?[\w.-]+\.png', capt, t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
    return t


def md(texto, d):
    """Markdown mínimo: encabezados, listas anidadas, párrafos, negritas, código."""
    out, pila, para = [], [], []

    def cerrar_para():
        if para:
            out.append('<p>' + inline(' '.join(para), d) + '</p>')
            para.clear()

    def cerrar_listas(hasta=-1):
        while pila and pila[-1][0] > hasta:
            out.append(f'</li></{pila.pop()[1]}>')

    for ln in texto.split('\n'):
        if ln.startswith('# '):  # el título lo pone la pestaña
            continue
        if not ln.strip():
            cerrar_para()
            continue
        m = re.match(r'^(#{2,4})\s+(.*)', ln)
        if m:
            cerrar_para(); cerrar_listas()
            n = len(m.group(1))
            out.append(f'<h{n + 1}>{inline(m.group(2), d)}</h{n + 1}>')
            continue
        m = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)', ln)
        if m:
            cerrar_para()
            ind, tag = len(m.group(1)), ('ol' if m.group(2)[0].isdigit() else 'ul')
            if pila and pila[-1][0] == ind:
                out.append('</li><li>')
            elif pila and ind < pila[-1][0]:
                cerrar_listas(ind)
                if pila and pila[-1][0] == ind:
                    out.append('</li><li>')
                else:
                    pila.append((ind, tag)); out.append(f'<{tag}><li>')
            else:
                pila.append((ind, tag)); out.append(f'<{tag}><li>')
            out.append(inline(m.group(3), d))
            continue
        if pila:
            out.append(' ' + inline(ln.strip(), d))
            continue
        para.append(ln.strip())
    cerrar_para(); cerrar_listas()
    return '\n'.join(out)


def contar(texto):
    """Hallazgos = ítems numerados (o ### N.) dentro de la sección «Hallazgos»."""
    for s in re.split(r'\n## ', texto):
        if s.lower().startswith('hallazgos'):
            return (len(re.findall(r'^### \d+\.', s, re.M))
                    or len(re.findall(r'^\d+\.\s', s, re.M)))
    return 0


def leer(nombre):
    p = os.path.join(BASE, nombre)
    return open(p, encoding='utf-8').read() if os.path.isfile(p) else ''


filas, tabs, secciones, total = [], [], [], 0
for p in sesion['personas']:
    rep = os.path.join(BASE, p['dir'], 'reporte.md')
    if not os.path.isfile(rep):
        sys.exit(f'Falta {rep}')
    t = open(rep, encoding='utf-8').read()
    n = contar(t)
    total += n
    e = {k: html.escape(str(p.get(k, ''))) for k in ('dir', 'nombre', 'perfil', 'cuenta', 'modo')}
    filas.append(f'<tr><td>{e["nombre"]}</td><td>{e["perfil"]}</td><td><code>{e["cuenta"]}</code></td>'
                 f'<td>{e["modo"]}</td><td class="num">{n}</td></tr>')
    tabs.append(f'<button role="tab" class="tab" data-p="{e["dir"]}" aria-selected="false">'
                f'<span class="tn">{e["nombre"]}</span><span class="tm">{e["perfil"]}</span>'
                f'<span class="tc">{n} hallazgos</span></button>')
    secciones.append(f'<section id="{e["dir"]}" class="persona" hidden>{md(t, p["dir"])}</section>')

sintesis, verif = leer('sintesis.html'), leer('verificacion.html')
bloque_sintesis = ('<h2 class="bloque">Lo que se repite entre personas</h2>'
                   '<p class="sub">Mi lectura de los reportes: junta lo que vio más de una. '
                   'Lo que dicen ellas está abajo, completo y sin editar.</p>'
                   '<table><thead><tr><th>Problema</th><th>Principio</th><th>Dónde</th><th>Quién lo vio</th></tr></thead>'
                   f'<tbody>{sintesis}</tbody></table>') if sintesis.strip() else ''
bloque_verif = ('<h2 class="bloque">Lo que verifiqué antes de entregar</h2>' + verif) if verif.strip() else ''

datos = ','.join(f'"{i}":"data:image/jpeg;base64,{b}"' for i, b in imgs.values())
rep = {
    '{{TITULO}}': html.escape(sesion.get('titulo', 'Prueba con personas')),
    '{{CONTEXTO}}': html.escape(sesion.get('contexto', '')),
    '{{INTRO}}': sesion.get('intro', ''),
    '{{NPERSONAS}}': str(len(sesion['personas'])),
    '{{TOTAL}}': str(total),
    '{{CAPTURAS}}': str(len(imgs)),
    '{{CUENTAS}}': ''.join(filas),
    '{{SINTESIS}}': bloque_sintesis,
    '{{VERIFICACION}}': bloque_verif,
    '{{TABS}}': ''.join(tabs),
    '{{SECCIONES}}': '\n'.join(secciones),
    '{{PIE}}': sesion.get('pie', ''),
    '{{IMGS}}': datos,
}
salida = open(os.path.join(AQUI, 'plantilla.html'), encoding='utf-8').read()
for k, v in rep.items():
    salida = salida.replace(k, v)
os.makedirs(os.path.dirname(os.path.abspath(DST)), exist_ok=True)
open(DST, 'w', encoding='utf-8').write(salida)
print(f'{DST} · {len(sesion["personas"])} personas · {total} hallazgos · '
      f'{len(imgs)} capturas · {os.path.getsize(DST) / 1e6:.1f} MB')
