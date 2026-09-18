# -*- coding: utf-8 -*-
"""Titulos emitidos por mas de un App Name.

Por titulo (titulo_clave del CSV de relleno) cuenta en cuantos App Name distintos aparece y arma:
    titulos-appname.json                       distribucion de titulos por numero de App Name y el
                                               top de titulos con >= 2 App Name (requests, eCPM
                                               ponderado y reparto por app)
    graficos-titulos-appname-barras.svg        top --top titulos en >= 2 App Name: barra = eCPM
                                               ponderado del titulo (eCPM > 0), rellena por app
                                               segun el % de los requests vendidos del titulo

Uso:
    python scripts/generar_tabla_pageurl_titulos.py inventory-consolidado-relleno.csv reportes/NN/recursos [--top 10]
"""
import argparse
import csv
import json
import os
from collections import Counter, defaultdict

INK, INK2, GRID = "#1f2933", "#5f6b76", "#e3e7ea"
PALETA = ["#2a78d6", "#eb6834", "#2e9e6b", "#8b5cf6", "#d64545", "#0e9aa7", "#a0622d", "#d6409f"]
OTRAS = "#9aa3ad"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
    with open(a.entrada, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            k = r.get("titulo_clave")
            if not k:
                continue
            q = int(r["Total Requests"])
            e = float(r["eCPM"])
            app = (r["App Name"] or "").strip() or "Not Available"
            apps[k].add(app)
            req[k] += q
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
                        "apps": [{"app": app, "pct_requests_vendidos": round(100 * q / qv, 1), "ecpm_ponderado": round(e, 3)}
                                 for app, q, e in por_app]})
    out = {"fuente": a.entrada, "titulos_reales": n, "requests_con_titulo": tot_req,
           "por_app_name": [{"n": ("5+" if i == 5 else str(i)), "titulos": dist[i], "pct_titulos": round(100 * dist[i] / n, 1),
                             "pct_requests": round(100 * rq[i] / tot_req, 1)} for i in range(1, 6)],
           "top_titulos_multi_app": titulos}
    json.dump(out, open(os.path.join(a.salida_dir, "titulos-appname.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- SVG: barras apiladas por app (altura = eCPM ponderado del titulo)
    # colores fijos por app, en orden de peso dentro del top; a partir de la 9a app, "Otras"
    peso = Counter()
    for t in titulos:
        for x in t["apps"]:
            peso[x["app"]] += x["pct_requests_vendidos"] * t["requests_vendidos"]
    color = {app: PALETA[i] for i, (app, _) in enumerate(peso.most_common(len(PALETA)))}
    W, H = 1000, 600
    left, right, top_m, bottom = 60, 30, 130, 120
    pw, ph = W - left - right, H - top_m - bottom
    MIN_SHARE = 2.0   # apps con menos del 2% de los requests vendidos del titulo no se dibujan
    for t in titulos:
        t["apps_dibujadas"] = [x for x in t["apps"] if x["pct_requests_vendidos"] >= MIN_SHARE][:6]
    ymax = max(x["ecpm_ponderado"] for t in titulos for x in t["apps_dibujadas"]) * 1.15
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">Top {len(titulos)} títulos emitidos por más de un App Name: eCPM ponderado por app para el mismo título</text>',
         f'<text x="16" y="44" font-size="12" fill="{INK2}">Una barra por App Name dentro de cada título; su altura es el eCPM ponderado de ese título en esa app (filas con eCPM &gt; 0).</text>',
         f'<text x="16" y="60" font-size="12" fill="{INK2}">Solo apps con ≥ {MIN_SHARE:g}% de los requests vendidos del título. Línea punteada: eCPM ponderado del título en todas sus apps.</text>']
    lx, ly = 16, 74
    for app, c in list(color.items()) + [("Otras apps", OTRAS)]:
        ancho = 16 + 6.3 * len(app[:34]) + 18
        if lx + ancho > W - 16:
            lx, ly = 16, ly + 18
        o.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" rx="2" fill="{c}"/>')
        o.append(f'<text x="{lx + 16}" y="{ly + 10}" font-size="11" fill="{INK}">{esc(app[:34])}</text>')
        lx += ancho
    step = 1 if ymax <= 8 else 2
    v = 0
    while v < ymax:
        y = top_m + ph * (1 - v / ymax)
        o.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + pw}" y2="{y:.1f}" stroke="{GRID}"/>')
        o.append(f'<text x="{left - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="10.5" fill="{INK2}">${v}</text>')
        v += step
    o.append(f'<text transform="translate(18,{top_m + ph / 2:.1f}) rotate(-90)" text-anchor="middle" fill="{INK}">eCPM ponderado del título ($)</text>')
    bw = pw / len(titulos)
    ybase = top_m + ph
    for i, t in enumerate(titulos):
        gx0 = left + bw * (i + 0.08)
        gw = bw * 0.84
        apps_t = t["apps_dibujadas"]
        w = gw / len(apps_t)
        for j, x in enumerate(apps_t):
            h = ph * x["ecpm_ponderado"] / ymax
            c = color.get(x["app"], OTRAS)
            bx = gx0 + w * j
            o.append(f'<rect x="{bx + 1:.1f}" y="{ybase - h:.1f}" width="{max(w - 2, 1):.1f}" height="{h:.1f}" rx="2" fill="{c}"/>')
            o.append(f'<text x="{bx + w / 2:.1f}" y="{ybase - h - 4:.1f}" text-anchor="middle" font-size="{9 if w < 22 else 10}" fill="{INK}">{x["ecpm_ponderado"]:.2f}</text>')
        yt = ybase - ph * t["ecpm_ponderado"] / ymax
        o.append(f'<line x1="{gx0:.1f}" y1="{yt:.1f}" x2="{gx0 + gw:.1f}" y2="{yt:.1f}" stroke="{INK2}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        o.append(f'<text transform="translate({gx0 + gw / 2:.1f},{ybase + 10}) rotate(35)" font-size="10.5" fill="{INK}">{esc(t["titulo"][:26])}</text>')
        if i < len(titulos) - 1:
            o.append(f'<line x1="{left + bw * (i + 1):.1f}" y1="{top_m}" x2="{left + bw * (i + 1):.1f}" y2="{ybase}" stroke="{GRID}"/>')
    o.append("</svg>")
    open(os.path.join(a.salida_dir, "graficos-titulos-appname-barras.svg"), "w", encoding="utf-8").write("\n".join(o))
    print(f"-> {a.salida_dir}: {n:,} titulos; {len(multi):,} en >=2 App Name; top {len(titulos)}")


if __name__ == "__main__":
    main()
