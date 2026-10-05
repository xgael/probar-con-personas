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
<dir-base>/tareas.json            — opcional: {"tareas": [{"id", "tarea", "real": [rutas], "rol" (opcional),
                                    "clasificacion": "pavimentar|con barandilla|no pavimentar"}]}
<dir-base>/<dir>/huellas.jsonl    — una línea JSON por tarea (ver plantillas/huellas.md)
"""
import base64, html, io, json, os, re, sys
from urllib.parse import urlparse
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

def lugar(u):
    """Dónde cayó un clic: la ruta de la URL, sin dominio ni query."""
    u = (u or '').strip()
    if not u:
        return ''
    p = urlparse(u)
    return (p.path or '/').rstrip('/') or '/' if (p.scheme or u.startswith('/')) else u.lower()


def es_correcto(primer, reales):
    pl = lugar(primer)
    return bool(pl) and any(pl == lugar(r) or pl.startswith(lugar(r) + '/') for r in reales)


def senderos():
    """Tabla de senderos de deseo a partir de tareas.json + <dir>/huellas.jsonl."""
    p = os.path.join(BASE, 'tareas.json')
    if not os.path.isfile(p):
        return '', []
    tareas = json.load(open(p, encoding='utf-8'))['tareas']
    nombres = {x['dir']: x['nombre'] for x in sesion['personas']}
    huellas, avisos = {}, []
    for d in nombres:
        f = os.path.join(BASE, d, 'huellas.jsonl')
        if not os.path.isfile(f):
            avisos.append(f'{nombres[d]} no dejó huellas.jsonl')
            continue
        for n, ln in enumerate(open(f, encoding='utf-8'), 1):
            if not ln.strip():
                continue
            try:
                h = json.loads(ln)
                huellas.setdefault(h['tarea'], []).append((d, h))
            except (ValueError, KeyError):
                avisos.append(f'{nombres[d]}: línea {n} de huellas.jsonl ilegible, se omitió')
    resumen, detalle = [], []
    # Modo por roles: si las tareas traen "rol", se agrupan (orden estable de aparición).
    if any(t.get('rol') for t in tareas):
        orden = {}
        for t in tareas:
            orden.setdefault(t.get('rol') or 'Sin rol', len(orden))
        tareas = sorted(tareas, key=lambda t: orden[t.get('rol') or 'Sin rol'])
    rol_actual = None
    for t in tareas:
        if t.get('rol') and t['rol'] != rol_actual:
            rol_actual = t['rol']
            resumen.append(f'<tr class="grupo"><th colspan="6">{html.escape(rol_actual)}</th></tr>')
            detalle.append(f'<h3 class="grupo">{html.escape(rol_actual)}</h3>')
        hs = huellas.get(t['id'], [])
        reales = t['real'] if isinstance(t['real'], list) else [t['real']]
        acierto = sum(es_correcto(h.get('primer_clic'), reales) for _, h in hs)
        logrado = sum(str(h.get('resultado', '')).startswith('logrado') for _, h in hs)
        errados = {}
        for d, h in hs:
            if not es_correcto(h.get('primer_clic'), reales) and lugar(h.get('primer_clic')):
                errados.setdefault(lugar(h.get('primer_clic')), []).append(nombres[d])
        # Sendero de deseo = el mismo lugar equivocado elegido por 2 o más personas.
        sendas = sorted(((l, q) for l, q in errados.items() if len(q) >= 2), key=lambda x: -len(x[1]))
        clas = html.escape(t.get('clasificacion', '') or 'sin clasificar')
        senda_txt = '<br>'.join(f'<code>{html.escape(l)}</code> · {len(q)} de {len(hs)} ({html.escape(", ".join(q))})'
                                for l, q in sendas) or '—'
        resumen.append(f'<tr><td>{html.escape(t["tarea"])}</td><td><code>{html.escape(", ".join(reales))}</code></td>'
                       f'<td class="num">{acierto} de {len(hs)}</td><td class="num">{logrado} de {len(hs)}</td>'
                       f'<td>{senda_txt}</td><td>{clas if sendas else "—"}</td></tr>')
        filas = []
        for d, h in hs:
            ok = es_correcto(h.get('primer_clic'), reales)
            cap = ''
            if h.get('captura'):
                i = img_id(d, os.path.basename(h['captura']))
                cap = (f'<button class="cap" data-i="{i}" type="button">📷</button>' if i else '')
            filas.append(f'<tr><td>{html.escape(nombres[d])}</td><td>{html.escape(str(h.get("espera", "")))}'
                         f'<br><span class="quien">{html.escape(str(h.get("porque", "")))}</span></td>'
                         f'<td><code>{html.escape(lugar(h.get("primer_clic")) or "—")}</code> {cap}</td>'
                         f'<td>{"✔ a la primera" if ok else "✘ en otro lugar"}</td>'
                         f'<td>{html.escape(str(h.get("resultado", "")))} · {html.escape(str(h.get("pasos", "?")))} clics</td></tr>')
        detalle.append(f'<details><summary><strong>{html.escape(t["tarea"])}</strong> — {acierto} de {len(hs)} '
                       f'a la primera</summary><table><thead><tr><th>Persona</th><th>Dónde lo esperaba y por qué</th>'
                       f'<th>Primer clic</th><th>¿Era ahí?</th><th>Resultado</th></tr></thead>'
                       f'<tbody>{"".join(filas)}</tbody></table></details>')
    bloque = ('<h2 class="bloque">Senderos de deseo</h2>'
              '<p class="sub">Dónde buscó cada persona <em>primero</em> cada tarea, contra dónde vive de verdad. '
              'Cuando dos o más buscan en el mismo lugar equivocado, ahí está el camino que la gente quiere: '
              'se pavimenta, se pavimenta con barandilla (confirmar, deshacer) o se explica por qué no.</p>'
              '<table><thead><tr><th>Tarea</th><th>Dónde vive</th><th class="num">A la primera</th>'
              '<th class="num">Lo lograron</th><th>Sendero de deseo</th><th>Decisión</th></tr></thead>'
              f'<tbody>{"".join(resumen)}</tbody></table>' + ''.join(detalle))
    return bloque, avisos


bloque_senderos, avisos_huellas = senderos()
for a in avisos_huellas:
    print('AVISO:', a)
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
    '{{SINTESIS}}': bloque_senderos + bloque_sintesis,
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
