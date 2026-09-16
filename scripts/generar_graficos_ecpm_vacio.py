# -*- coding: utf-8 -*-
"""Graficos (SVG, sin dependencias) del eCPM ponderado de las filas con dato util
("llenas") vs las filas vacias, por columna y por grupo (total y paises), a partir
del JSON de requests_ecpm_por_vacio.py.

Salidas (en la carpeta indicada):
  graficos-ecpm-vacio-scatter.svg       por grupo: eCPM llenas (x) vs eCPM vacias (y),
                                        un punto por columna, diagonal y=x, recta OLS y R2
  graficos-ecpm-vacio-scatter-fill.svg  por grupo: % filas llenas (x) vs eCPM (y), dos
                                        series (llenas / vacias), recta OLS y R2 por serie
  graficos-ecpm-vacio-pies.svg          por grupo y columna: reparto del gasto
                                        (eCPM x requests / 1000) entre filas llenas y vacias
  graficos-ecpm-vacio-r2.json           los R2, pendientes y datos usados

Uso:
    python generar_graficos_ecpm_vacio.py reporte-requests-ecpm-por-vacio.json carpeta_salida
"""
import json, math, os, sys

if len(sys.argv) != 3:
    print(__doc__); sys.exit(1)
SRC, OUT = sys.argv[1], sys.argv[2]
J = json.load(open(SRC, encoding="utf-8"))

GRUPOS = [g for g in ["(todos)", "Mexico", "Colombia", "Chile"] if g in J["paises"]]
TITULO = {"(todos)": "Total consolidado", "Mexico": "México", "Colombia": "Colombia", "Chile": "Chile"}
COLS = ["App Name", "contentGenre", "contentTitle", "contentRating", "contentLanguage",
        "contentIsLiveStream", "contentCategory", "contentLength", "contentSeries"]
ABR = {"App Name": "App Name", "contentGenre": "Genre", "contentTitle": "Title", "contentRating": "Rating",
       "contentLanguage": "Language", "contentIsLiveStream": "LiveStream", "contentCategory": "Category",
       "contentLength": "Length", "contentSeries": "Series"}

# paleta (references/palette.md del skill dataviz, modo claro)
C_LLENO, C_VACIO = "#2a78d6", "#eb6834"
SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
FONT = 'font-family="system-ui,-apple-system,Segoe UI,sans-serif"'

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")

def ols(xs, ys):
    n = len(xs)
    if n < 2: return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0: return None
    b = sxy / sxx; a = my - b * mx
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)); ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    return {"pendiente": round(b, 4), "intercepto": round(a, 4), "r2": round(r2, 4), "n": n}

def datos(g):
    out = []
    for c in COLS:
        d = J["paises"][g]["columnas"][c]; a, b = d["lleno"], d["vacio"]
        if not a["requests"] or not b["requests"] or a["ecpm_ponderado"] is None or b["ecpm_ponderado"] is None:
            continue
        gasto = lambda z: z["ecpm_ponderado"] * z["requests"] * z["pct_req_monetizado"] / 100 / 1000
        out.append({"col": c, "fill": a["pct_filas"], "e_lleno": a["ecpm_ponderado"], "e_vacio": b["ecpm_ponderado"],
                    "req_lleno": a["requests"], "req_vacio": b["requests"],
                    "gasto_lleno": gasto(a), "gasto_vacio": gasto(b)})
    return out

def ticks(lo, hi, n=5):
    span = hi - lo or 1
    raw = span / n; mag = 10 ** math.floor(math.log10(raw)); step = min([1, 2, 2.5, 5, 10], key=lambda s: abs(s * mag - raw)) * mag
    t0 = math.floor(lo / step) * step; t = []
    while t0 <= hi + 1e-9: t.append(round(t0, 6)); t0 += step
    return t

def fmt(v): return f"{v:g}"

# ---------- scatter generico ----------
W, H = 520, 400
ML, MR, MT, MB = 62, 20, 82, 54
def panel_scatter(x0, y0, titulo, series, xlab, ylab, diagonal=False, notas=()):
    """series: lista de dict(color, nombre, puntos=[(x,y,label)], ols)"""
    xs = [p[0] for s in series for p in s["puntos"]]; ys = [p[1] for s in series for p in s["puntos"]]
    lo_x, hi_x = 0, max(xs) * 1.12; lo_y, hi_y = 0, max(ys) * 1.15
    if diagonal: hi_x = hi_y = max(hi_x, hi_y)
    pw, ph = W - ML - MR, H - MT - MB
    sx = lambda v: x0 + ML + (v - lo_x) / (hi_x - lo_x) * pw
    sy = lambda v: y0 + MT + ph - (v - lo_y) / (hi_y - lo_y) * ph
    o = [f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{SURF}"/>']
    o.append(f'<text x="{x0+ML}" y="{y0+22}" font-size="15" font-weight="600" fill="{INK}">{esc(titulo)}</text>')
    for t in ticks(lo_x, hi_x):
        if t > hi_x: break
        o.append(f'<line x1="{sx(t):.1f}" y1="{y0+MT}" x2="{sx(t):.1f}" y2="{y0+MT+ph}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{sx(t):.1f}" y="{y0+MT+ph+16}" font-size="11" text-anchor="middle" fill="{MUTED}">{fmt(t)}</text>')
    for t in ticks(lo_y, hi_y):
        if t > hi_y: break
        o.append(f'<line x1="{x0+ML}" y1="{sy(t):.1f}" x2="{x0+ML+pw}" y2="{sy(t):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{x0+ML-6}" y="{sy(t)+4:.1f}" font-size="11" text-anchor="end" fill="{MUTED}">{fmt(t)}</text>')
    o.append(f'<line x1="{x0+ML}" y1="{y0+MT+ph}" x2="{x0+ML+pw}" y2="{y0+MT+ph}" stroke="{AXIS}" stroke-width="1"/>')
    o.append(f'<line x1="{x0+ML}" y1="{y0+MT}" x2="{x0+ML}" y2="{y0+MT+ph}" stroke="{AXIS}" stroke-width="1"/>')
    o.append(f'<text x="{x0+ML+pw/2:.1f}" y="{y0+H-14}" font-size="11.5" text-anchor="middle" fill="{INK2}">{esc(xlab)}</text>')
    o.append(f'<text transform="translate({x0+16},{y0+MT+ph/2:.1f}) rotate(-90)" font-size="11.5" text-anchor="middle" fill="{INK2}">{esc(ylab)}</text>')
    cid = f"clip{x0}_{y0}_{abs(hash(titulo)) % 10000}"
    o.append(f'<clipPath id="{cid}"><rect x="{x0+ML}" y="{y0+MT}" width="{pw}" height="{ph}"/></clipPath>')
    if diagonal:
        m = min(hi_x, hi_y)
        o.append(f'<line x1="{sx(0):.1f}" y1="{sy(0):.1f}" x2="{sx(m):.1f}" y2="{sy(m):.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 4"/>')
        o.append(f'<text x="{sx(m*0.3)+6:.1f}" y="{sy(m*0.3)+12:.1f}" font-size="10.5" fill="{MUTED}">y = x (paga igual)</text>')
    for s in series:
        r = s.get("ols")
        if r:
            ya, yb = r["intercepto"] + r["pendiente"] * lo_x, r["intercepto"] + r["pendiente"] * hi_x
            o.append(f'<line clip-path="url(#{cid})" x1="{sx(lo_x):.1f}" y1="{sy(ya):.1f}" x2="{sx(hi_x):.1f}" y2="{sy(yb):.1f}" stroke="{s["color"]}" stroke-width="2" stroke-opacity="0.55"/>')
    for s in series:
        for x, y, lab in s["puntos"]:
            o.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="5" fill="{s["color"]}" stroke="{SURF}" stroke-width="2"/>')
            if lab:
                o.append(f'<text x="{sx(x)+7:.1f}" y="{sy(y)-6:.1f}" font-size="10" fill="{INK2}">{esc(lab)}</text>')
    yy = y0 + 34
    for s in series:
        r = s.get("ols")
        txt = f'{s["nombre"]}: R² = {r["r2"]:.2f}, pendiente {r["pendiente"]:.3f}' if r else s["nombre"]
        o.append(f'<circle cx="{x0+ML+4}" cy="{yy+5}" r="4" fill="{s["color"]}"/>')
        o.append(f'<text x="{x0+ML+12}" y="{yy+9}" font-size="11" fill="{INK}">{esc(txt)}</text>')
        yy += 15
    for nt in notas:
        o.append(f'<text x="{x0+ML+12}" y="{yy+9}" font-size="10.5" fill="{INK2}">{esc(nt)}</text>'); yy += 14
    return "\n".join(o)

def svg_grid(paneles, cols=2, titulo="", sub=""):
    filas = math.ceil(len(paneles) / cols); top = 56 if titulo else 0
    w, h = cols * W + (cols - 1) * 16, filas * H + (filas - 1) * 16 + top
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FONT}>',
         f'<rect width="{w}" height="{h}" fill="{SURF}"/>']
    if titulo:
        o.append(f'<text x="0" y="22" font-size="17" font-weight="700" fill="{INK}">{esc(titulo)}</text>')
        o.append(f'<text x="0" y="42" font-size="12" fill="{INK2}">{esc(sub)}</text>')
    for i, p in enumerate(paneles):
        o.append(f'<g transform="translate({(i % cols) * (W + 16)},{top + (i // cols) * (H + 16)})">{p}</g>')
    o.append("</svg>")
    return "\n".join(o)

resumen = {}
# ---------- 1. scatter eCPM llenas vs vacias ----------
paneles = []
for g in GRUPOS:
    d = datos(g); pts = [(r["e_lleno"], r["e_vacio"], ABR[r["col"]]) for r in d]
    r = ols([p[0] for p in pts], [p[1] for p in pts])
    arriba = sum(1 for p in pts if p[1] > p[0])
    resumen.setdefault(g, {})["scatter_lleno_vs_vacio"] = {"ols": r, "columnas_vacio_paga_mas": arriba, "columnas": len(pts)}
    paneles.append(panel_scatter(0, 0, TITULO[g], [{"color": C_LLENO, "nombre": "columnas", "puntos": pts, "ols": r}],
                                 "eCPM pond. de las filas LLENAS ($)", "eCPM pond. de las filas vacías ($)", diagonal=True,
                                 notas=[f"{arriba} de {len(pts)} columnas pagan más vacías"]))
open(os.path.join(OUT, "graficos-ecpm-vacio-scatter.svg"), "w", encoding="utf-8").write(
    svg_grid(paneles, 2, "eCPM ponderado: filas llenas vs filas vacías, por columna",
             "Un punto por content object. Encima de la diagonal: la columna paga más cuando viene vacía. eCPM ponderado por requests, sin filas con eCPM = 0."))

# ---------- 2. scatter % llenas vs eCPM (dos series) ----------
paneles = []
for g in GRUPOS:
    d = datos(g)
    p1 = [(r["fill"], r["e_lleno"], ABR[r["col"]]) for r in d]; p2 = [(r["fill"], r["e_vacio"], "") for r in d]
    r1 = ols([p[0] for p in p1], [p[1] for p in p1]); r2 = ols([p[0] for p in p2], [p[1] for p in p2])
    resumen[g]["scatter_fill_vs_ecpm"] = {"llenas": r1, "vacias": r2}
    paneles.append(panel_scatter(0, 0, TITULO[g],
                                 [{"color": C_LLENO, "nombre": "eCPM filas llenas", "puntos": p1, "ols": r1},
                                  {"color": C_VACIO, "nombre": "eCPM filas vacías", "puntos": p2, "ols": r2}],
                                 "% de filas llenas de la columna", "eCPM ponderado ($)"))
open(os.path.join(OUT, "graficos-ecpm-vacio-scatter-fill.svg"), "w", encoding="utf-8").write(
    svg_grid(paneles, 2, "¿La completitud de la columna se relaciona con el precio?",
             "x = % de filas del grupo donde la columna trae dato útil; y = eCPM ponderado de esas filas (azul) y de las vacías (naranja). Recta OLS y R² por serie."))

# ---------- 3. pies: reparto del gasto ----------
R, CW, CH = 44, 118, 150
def donut(cx, cy, frac, label, sub):
    o = []
    a = frac * 2 * math.pi
    if frac >= 0.999: o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{C_LLENO}"/>')
    elif frac <= 0.001: o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{C_VACIO}"/>')
    else:
        x1, y1 = cx, cy - R; x2, y2 = cx + R * math.sin(a), cy - R * math.cos(a); big = 1 if a > math.pi else 0
        o.append(f'<path d="M{cx},{cy} L{x1},{y1} A{R},{R} 0 {big},1 {x2:.2f},{y2:.2f} Z" fill="{C_LLENO}" stroke="{SURF}" stroke-width="2"/>')
        o.append(f'<path d="M{cx},{cy} L{x2:.2f},{y2:.2f} A{R},{R} 0 {1-big},1 {x1},{y1} Z" fill="{C_VACIO}" stroke="{SURF}" stroke-width="2"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R*0.55:.1f}" fill="{SURF}"/>')
    o.append(f'<text x="{cx}" y="{cy+4}" font-size="12" font-weight="600" text-anchor="middle" fill="{INK}">{frac*100:.0f}%</text>')
    o.append(f'<text x="{cx}" y="{cy+R+16}" font-size="11" text-anchor="middle" fill="{INK}">{esc(label)}</text>')
    o.append(f'<text x="{cx}" y="{cy+R+30}" font-size="10" text-anchor="middle" fill="{INK2}">{esc(sub)}</text>')
    return "\n".join(o)

top = 70; rowh = CH + 30; w = 40 + len(COLS) * CW; h = top + len(GRUPOS) * rowh + 10
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FONT}>', f'<rect width="{w}" height="{h}" fill="{SURF}"/>']
o.append(f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">Reparto del gasto (eCPM × requests / 1000) entre filas llenas y vacías, por columna</text>')
o.append(f'<text x="16" y="44" font-size="12" fill="{INK2}">El número del centro es la parte del gasto del grupo que cae en filas donde la columna trae dato útil. Debajo: eCPM ponderado llenas / vacías.</text>')
o.append(f'<circle cx="24" cy="60" r="5" fill="{C_LLENO}"/><text x="34" y="64" font-size="11.5" fill="{INK}">filas llenas</text>')
o.append(f'<circle cx="140" cy="60" r="5" fill="{C_VACIO}"/><text x="150" y="64" font-size="11.5" fill="{INK}">filas vacías</text>')
for gi, g in enumerate(GRUPOS):
    y = top + gi * rowh
    o.append(f'<text x="16" y="{y+18}" font-size="14" font-weight="600" fill="{INK}">{esc(TITULO[g])}</text>')
    d = {r["col"]: r for r in datos(g)}; resumen[g]["gasto"] = {}
    for ci, c in enumerate(COLS):
        cx = 40 + ci * CW + CW / 2; cy = y + 34 + R
        if c not in d:
            o.append(f'<text x="{cx}" y="{cy}" font-size="11" text-anchor="middle" fill="{MUTED}">{ABR[c]}: sin vacías</text>'); continue
        r = d[c]; tot = r["gasto_lleno"] + r["gasto_vacio"]; frac = r["gasto_lleno"] / tot if tot else 1
        resumen[g]["gasto"][c] = {"pct_gasto_no_vacias": round(frac * 100, 1), "gasto_no_vacias": round(r["gasto_lleno"], 2), "gasto_vacias": round(r["gasto_vacio"], 2)}
        o.append(donut(cx, cy, frac, ABR[c], f"${r['e_lleno']:.2f} / ${r['e_vacio']:.2f}"))
o.append("</svg>")
open(os.path.join(OUT, "graficos-ecpm-vacio-pies.svg"), "w", encoding="utf-8").write("\n".join(o))

json.dump({"fuente": SRC, "grupos": resumen}, open(os.path.join(OUT, "graficos-ecpm-vacio-r2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for g in GRUPOS:
    s = resumen[g]
    print(f"{TITULO[g]:18} lleno-vs-vacio R2={s['scatter_lleno_vs_vacio']['ols']['r2']:.3f} ({s['scatter_lleno_vs_vacio']['columnas_vacio_paga_mas']}/{s['scatter_lleno_vs_vacio']['columnas']} vacio paga mas) | fill-vs-eCPM R2 llenas={s['scatter_fill_vs_ecpm']['llenas']['r2']:.3f} vacias={s['scatter_fill_vs_ecpm']['vacias']['r2']:.3f}")
print("->", OUT)
