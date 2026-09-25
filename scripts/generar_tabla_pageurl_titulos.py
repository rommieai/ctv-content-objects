# -*- coding: utf-8 -*-
"""Titulos emitidos por mas de un App Name.

Por titulo (titulo_clave del CSV de relleno) cuenta en cuantos App Name distintos aparece y arma:
    titulos-appname.json                       distribucion de titulos por numero de App Name y el
                                               top de titulos con >= 2 App Name (requests, eCPM
                                               ponderado y reparto por app)
    graficos-titulos-appname-requests-ecpm.svg top --top titulos en >= 2 App Name, doble eje Y: barra
                                               por app = requests totales del titulo en la app (eje
                                               izquierdo); linea = eCPM ponderado del titulo en
                                               cada app (eje derecho)

Las variantes de ViX (ViX: TV, Deportes y Noticias, ViX: TV, Sports and News, ViX: Cine y TV..., VIX - Filmes
e TV) se cuentan como una sola app "ViX".

Uso:
    python scripts/generar_tabla_pageurl_titulos.py inventory-consolidado-relleno.csv reportes/NN/recursos [--top 10]
"""
import argparse
import csv
import json
import os
from collections import Counter, defaultdict

INK, INK2, GRID = "#1f2933", "#5f6b76", "#e3e7ea"
PALETA = ["#2a78d6", "#eb6834", "#2e9e6b", "#8b5cf6", "#d64545", "#0e9aa7", "#a0622d", "#d6409f", "#c9a400", "#4b5563", "#7c3aed", "#0f766e"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def app_canonica(app):
    """Junta las variantes de ViX (ViX: TV, Deportes y Noticias / Sports and News / Cine y TV..., VIX - Filmes e TV)
    en una sola app "ViX"; el resto de App Name queda igual."""
    app = (app or "").strip() or "Not Available"
    return "ViX" if app.lower().startswith("vix") else app


def grafica(titulos, color, salida, min_share):
    """Barras agrupadas por titulo, una por app, con doble eje Y: barras = requests totales del titulo en la app
    (eje izquierdo, miles de millones); linea = eCPM ponderado del titulo en esa app (eje derecho)."""
    W, H = 1040, 620
    left, right, top_m, bottom = 60, 60, 140, 120
    pw, ph = W - left - right, H - top_m - bottom
    rmax = max(x["requests"] / 1e9 for t in titulos for x in t["apps_dibujadas"]) * 1.15
    emax = max(x["ecpm_ponderado"] for t in titulos for x in t["apps_dibujadas"]) * 1.15
    tit = f"Top {len(titulos)} títulos emitidos por más de un App Name: requests totales y eCPM ponderado por app"
    sub = ["Una barra por App Name dentro de cada título; su altura son los requests totales (vendidos o no) de ese título en esa app, en miles de millones (eje izquierdo).",
           "La línea une el eCPM ponderado de ese título en cada app (filas con eCPM &gt; 0, eje derecho).",
           f"Las 5 apps con más requests vendidos del título (y al menos el {min_share:g}%). Línea punteada gris: eCPM ponderado del título en todas sus apps."]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">{tit}</text>']
    for i, s in enumerate(sub):
        o.append(f'<text x="16" y="{44 + 16 * i}" font-size="12" fill="{INK2}">{s}</text>')
    lx, ly = 16, 92
    for app, c in color.items():
        ancho = 16 + 6.3 * len(app[:34]) + 18
        if lx + ancho > W - 16:
            lx, ly = 16, ly + 18
        o.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" rx="2" fill="{c}"/>')
        o.append(f'<text x="{lx + 16}" y="{ly + 10}" font-size="11" fill="{INK}">{esc(app[:34])}</text>')
        lx += ancho
    if lx + 190 > W - 16:
        lx, ly = 16, ly + 18
    o.append(f'<line x1="{lx}" y1="{ly + 6}" x2="{lx + 22}" y2="{ly + 6}" stroke="{INK}" stroke-width="2"/>'
             f'<circle cx="{lx + 11}" cy="{ly + 6}" r="3.5" fill="#ffffff" stroke="{INK}" stroke-width="2"/>')
    o.append(f'<text x="{lx + 28}" y="{ly + 10}" font-size="11" fill="{INK}">eCPM ponderado (eje derecho)</text>')
    ybase = top_m + ph
    rstep = next(s for s in (0.1, 0.25, 0.5, 1, 2, 5, 10, 20) if rmax / s <= 8)
    v = 0
    while v < rmax:
        y = ybase - ph * v / rmax
        o.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + pw}" y2="{y:.1f}" stroke="{GRID}"/>')
        o.append(f'<text x="{left - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="10.5" fill="{INK2}">{v:g}</text>')
        v += rstep
    v = 0
    while v < emax:
        y = ybase - ph * v / emax
        o.append(f'<line x1="{left + pw}" y1="{y:.1f}" x2="{left + pw + 4}" y2="{y:.1f}" stroke="{INK2}"/>')
        o.append(f'<text x="{left + pw + 7}" y="{y + 4:.1f}" font-size="10.5" fill="{INK2}">${v:g}</text>')
        v += 1 if emax <= 10 else 2
    o.append(f'<line x1="{left + pw}" y1="{top_m}" x2="{left + pw}" y2="{ybase}" stroke="{INK2}"/>')
    o.append(f'<text transform="translate(18,{top_m + ph / 2:.1f}) rotate(-90)" text-anchor="middle" fill="{INK}">'
             f'requests totales del título en la app (miles de millones)</text>')
    o.append(f'<text transform="translate({W - 14},{top_m + ph / 2:.1f}) rotate(90)" text-anchor="middle" fill="{INK}">eCPM ponderado del título ($)</text>')
    bw = pw / len(titulos)
    lineas, etiquetas = [], []
    for i, t in enumerate(titulos):
        gx0 = left + bw * (i + 0.08)
        gw = bw * 0.84
        apps_t = t["apps_dibujadas"]
        w = gw / len(apps_t)
        pts = []
        for j, x in enumerate(apps_t):
            h = ph * x["requests"] / 1e9 / rmax
            bx = gx0 + w * j
            o.append(f'<rect x="{bx + 1:.1f}" y="{ybase - h:.1f}" width="{max(w - 2, 1):.1f}" height="{h:.1f}" rx="2" fill="{color[x["app"]]}"/>')
            etiquetas.append(f'<text x="{bx + w / 2:.1f}" y="{ybase - h - 4:.1f}" text-anchor="middle" font-size="{9 if w < 22 else 10}" fill="{INK2}" '
                             f'stroke="#ffffff" stroke-width="3" paint-order="stroke">{x["requests"] / 1e9:.2f}</text>')
            pts.append((bx + w / 2, ybase - ph * x["ecpm_ponderado"] / emax, x["ecpm_ponderado"]))
        yt = ybase - ph * t["ecpm_ponderado"] / emax
        o.append(f'<line x1="{gx0:.1f}" y1="{yt:.1f}" x2="{gx0 + gw:.1f}" y2="{yt:.1f}" stroke="{INK2}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        lineas.append(pts)
        o.append(f'<text x="{gx0 + gw / 2:.1f}" y="{top_m - 6}" text-anchor="middle" font-size="10" fill="{INK2}">total {t["requests"] / 1e9:.2f}</text>')
        o.append(f'<text transform="translate({gx0 + gw / 2:.1f},{ybase + 10}) rotate(35)" font-size="10.5" fill="{INK}">{esc(t["titulo"][:26])}</text>')
        if i < len(titulos) - 1:
            o.append(f'<line x1="{left + bw * (i + 1):.1f}" y1="{top_m}" x2="{left + bw * (i + 1):.1f}" y2="{ybase}" stroke="{GRID}"/>')
    o += etiquetas
    # la linea de eCPM va encima de las barras, un tramo por titulo, con el valor sobre cada punto
    for pts in lineas:
        if len(pts) > 1:
            o.append(f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py, _ in pts)}" fill="none" stroke="{INK}" stroke-width="2"/>')
        for px, py, e in pts:
            o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#ffffff" stroke="{INK}" stroke-width="2"/>')
            o.append(f'<text x="{px:.1f}" y="{py - 7:.1f}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{INK}" '
                     f'stroke="#ffffff" stroke-width="3" paint-order="stroke">{e:.2f}</text>')
    o.append("</svg>")
    open(salida, "w", encoding="utf-8").write("\n".join(o))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida_dir")
    ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()
    csv.field_size_limit(10 ** 9)
    apps = defaultdict(set)
    req = Counter()
    vend = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))   # titulo -> app -> [req vendidos, sum q*e]
    req_app = defaultdict(Counter)                                # titulo -> app -> requests totales
    with open(a.entrada, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            k = r.get("titulo_clave")
            if not k:
                continue
            q = int(r["Total Requests"])
            e = float(r["eCPM"])
            app = app_canonica(r["App Name"])
            apps[k].add(app)
            req[k] += q
            req_app[k][app] += q
            if q > 0 and e > 0:
                v = vend[k][app]
                v[0] += q
                v[1] += q * e
    n = len(apps)
    tot_req = sum(req.values())
    dist = Counter(min(len(v), 5) for v in apps.values())
    rq = defaultdict(int)
    for k, v in apps.items():
        rq[min(len(v), 5)] += req[k]
    multi = [k for k in apps if len(apps[k]) >= 2 and sum(v[0] for v in vend[k].values()) > 0]
    top = sorted(multi, key=lambda k: -req[k])[:a.top]
    titulos = []
    for k in top:
        qv = sum(v[0] for v in vend[k].values())
        ecpm = sum(v[1] for v in vend[k].values()) / qv
        por_app = sorted(((app, v[0], v[1] / v[0]) for app, v in vend[k].items()), key=lambda t: -t[1])
        titulos.append({"titulo": k, "app_names": len(apps[k]), "requests": req[k], "requests_vendidos": qv,
                        "ecpm_ponderado": round(ecpm, 3),
                        "apps": [{"app": app, "requests": req_app[k][app], "pct_requests_vendidos": round(100 * q / qv, 1),
                                  "ecpm_ponderado": round(e, 3)}
                                 for app, q, e in por_app]})
    out = {"fuente": a.entrada, "titulos_reales": n, "requests_con_titulo": tot_req,
           "por_app_name": [{"n": ("5+" if i == 5 else str(i)), "titulos": dist[i], "pct_titulos": round(100 * dist[i] / n, 1),
                             "pct_requests": round(100 * rq[i] / tot_req, 1)} for i in range(1, 6)],
           "top_titulos_multi_app": titulos}
    json.dump(out, open(os.path.join(a.salida_dir, "titulos-appname.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- SVG: barras agrupadas por app (altura = eCPM ponderado del titulo en esa app)
    MIN_SHARE = 2.0   # apps con menos del 2% de los requests vendidos del titulo no se dibujan
    for t in titulos:
        top5 = [x for x in t["apps"] if x["pct_requests_vendidos"] >= MIN_SHARE][:5]   # top 5 apps del titulo por requests
        t["apps_dibujadas"] = sorted(top5, key=lambda x: -x["requests"])                 # barras de mayor a menor requests
    # solo las apps que se dibujan reciben color (en orden de peso); no hay grupo "otras"
    usadas = Counter()
    for t in titulos:
        for x in t["apps_dibujadas"]:
            usadas[x["app"]] += x["pct_requests_vendidos"] * t["requests_vendidos"]
    color = {app: PALETA[i % len(PALETA)] for i, (app, _) in enumerate(usadas.most_common())}
    grafica(titulos, color, os.path.join(a.salida_dir, "graficos-titulos-appname-requests-ecpm.svg"), MIN_SHARE)
    print(f"-> {a.salida_dir}: {n:,} titulos; {len(multi):,} en >=2 App Name; top {len(titulos)}")


if __name__ == "__main__":
    main()
