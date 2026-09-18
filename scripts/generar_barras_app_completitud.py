# -*- coding: utf-8 -*-
"""Barras por app: eCPM ponderado (>0) segun cuantos content objects trae el registro (0-8).

Un panel por app (las --top-apps con mas requests vendidos). En cada panel, x = numero de
content objects con dato util, y = eCPM ponderado por requests de los registros de ese nivel
(solo filas con eCPM > 0 y requests > 0). Debajo de cada barra, el % de los requests vendidos
de la app que cae en ese nivel; los niveles con menos de --min-share % no se dibujan (una
barra hecha con pocas filas engana). La linea punteada es el eCPM ponderado de toda la app.

Uso:
    python scripts/generar_barras_app_completitud.py inventory-consolidado.csv reportes/NN/recursos \
        [--top-apps 12] [--min-share 2] [--etiquetas 15]
Escribe graficos-app-completitud-barras.svg y graficos-app-completitud-barras.json, y ademas un
scatter con todas las apps que vendieron algo (un punto por app: x = eCPM ponderado, y = requests
totales, los dos en escala log): graficos-app-requests-ecpm.svg y graficos-app-requests-ecpm.json.
"""
import argparse
import csv
import json
import math
import os
from collections import defaultdict

SENT = {"not available", "not applicable", "unknown", "n/a", "null", "undefined", "none", "-", ""}
MD5 = "d41d8cd98f00b204e9800998ecf8427e"
CO = ["contentGenre", "contentCategory", "contentSeries", "contentLength", "contentLanguage",
      "contentIsLiveStream", "contentTitle", "contentRating"]
N = len(CO)
INK, INK2, GRID, AZUL = "#1f2933", "#5f6b76", "#e3e7ea", "#2a78d6"
ABR = {"MovieArk: Stream Movies & Live": "MovieArk", "ViX: TV, Deportes y Noticias": "ViX Deportes y Noticias",
       "ViX: TV, Sports and News": "ViX Sports and News", "Browser TV Web - BrowseHere": "BrowseHere",
       "Tubi: Free Movies & Live TV": "Tubi", "Not Available": "(App Name vacío)"}


def util(c, v):
    s = (v or "").strip()
    if s.lower() in SENT:
        return False
    if c == "contentCategory" and s == "[-7]":
        return False
    if c == "contentSeries" and s.lower() == MD5:
        return False
    if c == "contentIsLiveStream" and s not in ("0", "1"):
        return False
    return True


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def scatter_apps(app_q, top, salida_dir, n_etiquetas):
    """Un punto por app: eCPM ponderado (x, escala log) vs requests totales (y, escala log)."""
    pts = [{"app": p, "requests": t[0], "requests_vendidos": t[1], "pct_vendido": round(100 * t[1] / t[0], 1),
            "ecpm_ponderado": round(t[2] / t[1], 3)} for p, t in app_q.items() if t[1]]
    pts.sort(key=lambda d: -d["requests"])
    sin_venta = sum(1 for t in app_q.values() if not t[1])
    tq = sum(t[0] for t in app_q.values())
    mu = sum(t[2] for t in app_q.values()) / sum(t[1] for t in app_q.values())
    json.dump({"apps_con_venta": len(pts), "apps_sin_venta": sin_venta, "ecpm_ponderado_total": round(mu, 3), "apps": pts},
              open(os.path.join(salida_dir, "graficos-app-requests-ecpm.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    W, H = 900, 800
    left, right, top_m, bottom = 84, 30, 136, 56
    pw, ph = W - left - right, H - top_m - bottom
    x_lo = math.floor(math.log10(min(d["ecpm_ponderado"] for d in pts)) * 2) / 2
    x_hi = math.ceil(math.log10(max(d["ecpm_ponderado"] for d in pts)) * 2) / 2
    y_lo = math.floor(math.log10(min(d["requests"] for d in pts)))
    y_hi = math.ceil(math.log10(max(d["requests"] for d in pts)) * 2) / 2

    def X(e):
        return left + pw * (math.log10(e) - x_lo) / (x_hi - x_lo)

    def Y(q):
        return top_m + ph * (1 - (math.log10(q) - y_lo) / (y_hi - y_lo))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">Apps: eCPM ponderado vs requests totales</text>',
         f'<text x="16" y="44" font-size="12" fill="{INK2}">Un punto por App Name con requests vendidos ({len(pts)} apps; otras {sin_venta} no vendieron nada y no tienen eCPM).</text>',
         f'<text x="16" y="60" font-size="12" fill="{INK2}">x = eCPM ponderado de la app (eCPM &gt; 0); y = requests totales de la app. Los dos ejes en escala logarítmica.</text>',
         f'<text x="16" y="76" font-size="12" fill="{INK2}">En azul, las {len(top)} apps de las barras de arriba; con nombre, las {n_etiquetas} de más requests. '
         f'Línea punteada: eCPM ponderado del consolidado (${mu:.2f}).</text>',
         f'<circle cx="24" cy="96" r="5" fill="{AZUL}"/><text x="34" y="100" font-size="11" fill="{INK}">top {len(top)} por requests vendidos</text>',
         f'<circle cx="200" cy="96" r="4" fill="#9aa5b1"/><text x="210" y="100" font-size="11" fill="{INK}">resto de apps</text>']
    for v in (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100):
        if x_lo - 1e-9 <= math.log10(v) <= x_hi + 1e-9:
            o.append(f'<line x1="{X(v):.1f}" y1="{top_m}" x2="{X(v):.1f}" y2="{top_m + ph}" stroke="{GRID}"/>')
            o.append(f'<text x="{X(v):.1f}" y="{top_m + ph + 16}" text-anchor="middle" font-size="10.5" fill="{INK2}">${v:g}</text>')
    k = int(y_lo)
    while k <= y_hi:
        lab = {3: "1 mil", 4: "10 mil", 5: "100 mil", 6: "1 M", 7: "10 M", 8: "100 M", 9: "1,000 M", 10: "10,000 M", 11: "100,000 M"}.get(k, f"1e{k}")
        o.append(f'<line x1="{left}" y1="{Y(10 ** k):.1f}" x2="{left + pw}" y2="{Y(10 ** k):.1f}" stroke="{GRID}"/>')
        o.append(f'<text x="{left - 6}" y="{Y(10 ** k) + 4:.1f}" text-anchor="end" font-size="10.5" fill="{INK2}">{lab}</text>')
        k += 1
    o.append(f'<line x1="{X(mu):.1f}" y1="{top_m}" x2="{X(mu):.1f}" y2="{top_m + ph}" stroke="{INK2}" stroke-dasharray="5 4"/>')
    o.append(f'<text x="{left + pw / 2:.1f}" y="{H - 10}" text-anchor="middle" fill="{INK}">eCPM ponderado de la app ($, escala log)</text>')
    o.append(f'<text transform="translate(18,{top_m + ph / 2:.1f}) rotate(-90)" text-anchor="middle" fill="{INK}">requests totales de la app (escala log)</text>')
    for d in reversed(pts):   # las de mas requests, encima
        es_top = d["app"] in top
        o.append(f'<circle cx="{X(d["ecpm_ponderado"]):.1f}" cy="{Y(d["requests"]):.1f}" r="{5.5 if es_top else 4}" '
                 f'fill="{AZUL if es_top else "#9aa5b1"}" fill-opacity="{0.95 if es_top else 0.6}" stroke="#ffffff" stroke-width="1"/>')
    # etiquetas: alrededor del punto, a 9, 24 y 40 px (con linea guia si queda lejos); se queda la primera posicion
    # que no pisa otra etiqueta ni otro punto con nombre
    cajas = [(X(d["ecpm_ponderado"]) - 7, Y(d["requests"]) - 7, X(d["ecpm_ponderado"]) + 7, Y(d["requests"]) + 7) for d in pts[:n_etiquetas]]
    for d in pts[:n_etiquetas]:
        nombre = ABR.get(d["app"], d["app"][:26])
        cx, cy, w = X(d["ecpm_ponderado"]), Y(d["requests"]), 6.3 * len(nombre) + 6
        propia = (cx - 7, cy - 7, cx + 7, cy + 7)
        ops = []
        for r in (9, 24, 40):
            k = r * 0.72
            ops += [("start", cx + r, cy + 4, r), ("end", cx - r, cy + 4, r), ("middle", cx, cy - r - 2, r), ("middle", cx, cy + r + 10, r),
                    ("start", cx + k, cy - k, r), ("end", cx - k, cy - k, r), ("start", cx + k, cy + k + 8, r), ("end", cx - k, cy + k + 8, r)]
        for anc, tx, ty, r in ops:
            x1 = tx if anc == "start" else tx - w if anc == "end" else tx - w / 2
            caja = (x1, ty - 12, x1 + w, ty + 4)
            if caja[0] < left or caja[2] > W - 4 or caja[1] < top_m - 16:
                continue
            if not any(caja[0] < c[2] and c[0] < caja[2] and caja[1] < c[3] and c[1] < caja[3] for c in cajas if c != propia):
                break
        cajas.append(caja)
        if r > 9:
            gx = tx + (-3 if anc == "start" else 3 if anc == "end" else 0)
            gy = ty - 4 if anc != "middle" else (ty + 3 if ty < cy else ty - 11)
            o.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{gx:.1f}" y2="{gy:.1f}" stroke="{INK2}" stroke-width="0.8"/>')
        o.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anc}" font-size="10.5" font-weight="600" fill="{INK}" '
                 f'stroke="#ffffff" stroke-width="3" paint-order="stroke">{esc(nombre)}</text>')
    o.append("</svg>")
    open(os.path.join(salida_dir, "graficos-app-requests-ecpm.svg"), "w", encoding="utf-8").write("\n".join(o))
    print(f"-> {salida_dir}: scatter de {len(pts)} apps")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida_dir")
    ap.add_argument("--top-apps", type=int, default=12)
    ap.add_argument("--min-share", type=float, default=2.0)
    ap.add_argument("--etiquetas", type=int, default=15)
    a = ap.parse_args()
    csv.field_size_limit(10 ** 9)
    app_q = defaultdict(lambda: [0, 0, 0.0])                 # requests, requests vendidos, sum q*e
    niv = defaultdict(lambda: [[0, 0, 0.0] for _ in range(N + 1)])   # app -> por nivel: filas, req vendidos, sum q*e
    with open(a.entrada, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            q = int(row["Total Requests"])
            if q <= 0:
                continue
            e = float(row["eCPM"])
            app = row["App Name"]
            app_q[app][0] += q
            if e <= 0:
                continue
            app_q[app][1] += q
            app_q[app][2] += q * e
            n = sum(1 for c in CO if util(c, row[c]))
            t = niv[app][n]
            t[0] += 1
            t[1] += q
            t[2] += q * e
    tot_vend = sum(v[1] for v in app_q.values())
    apps = [p for p, _ in sorted(app_q.items(), key=lambda kv: -kv[1][1])[:a.top_apps]]
    out = {"fuente": a.entrada, "campos": CO, "min_share_pct": a.min_share, "apps": {}}
    for app in apps:
        Q = app_q[app][1]
        out["apps"][app] = {"requests": app_q[app][0], "pct_vendido": round(100 * Q / app_q[app][0], 1),
                            "share_trafico_vendido_pct": round(100 * Q / tot_vend, 2),
                            "ecpm_ponderado": round(app_q[app][2] / Q, 3),
                            "niveles": [{"campos_llenos": n, "filas": t[0], "pct_requests_vendidos": round(100 * t[1] / Q, 1),
                                         "ecpm_ponderado": round(t[2] / t[1], 3) if t[1] else None}
                                        for n, t in enumerate(niv[app])]}
    json.dump(out, open(os.path.join(a.salida_dir, "graficos-app-completitud-barras.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # ---- SVG: paneles en 3 columnas
    cols = 3
    PW, PH = 380, 230
    rows = math.ceil(len(apps) / cols)
    W, H = 16 + PW * cols, 84 + PH * rows
    ymax = max(x["ecpm_ponderado"] for d in out["apps"].values() for x in d["niveles"]
               if x["ecpm_ponderado"] and x["pct_requests_vendidos"] >= a.min_share) * 1.18
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">eCPM ponderado por app según cuántos content objects trae el registro</text>',
         f'<text x="16" y="42" font-size="12" fill="{INK2}">Top {len(apps)} apps por requests vendidos. Barra = eCPM ponderado (eCPM &gt; 0) de los registros con ese número de campos llenos; '
         f'debajo, % de los requests vendidos de la app en ese nivel.</text>',
         f'<text x="16" y="58" font-size="12" fill="{INK2}">Sin barra: el nivel tiene menos del {a.min_share:g}% de los requests vendidos de la app. Línea punteada: eCPM ponderado de toda la app.</text>']
    for i, app in enumerate(apps):
        d = out["apps"][app]
        x0, y0 = 16 + PW * (i % cols), 84 + PH * (i // cols)
        left, top, bottom = 44, 34, 44
        pw, ph = PW - left - 14, PH - top - bottom

        def Y(v):
            return y0 + top + ph * (1 - v / ymax)
        nombre = ABR.get(app, app[:26])
        o.append(f'<text x="{x0 + left}" y="{y0 + 16}" font-size="13" font-weight="700" fill="{INK}">{esc(nombre)}</text>')
        o.append(f'<text x="{x0 + left}" y="{y0 + 29}" font-size="10.5" fill="{INK2}">eCPM ${d["ecpm_ponderado"]:.2f} · {d["share_trafico_vendido_pct"]:.1f}% del tráfico vendido · vende {d["pct_vendido"]:.0f}% de sus requests</text>')
        step = 2 if ymax > 8 else 1
        v = 0
        while v < ymax:
            o.append(f'<line x1="{x0 + left}" y1="{Y(v):.1f}" x2="{x0 + left + pw}" y2="{Y(v):.1f}" stroke="{GRID}"/>')
            o.append(f'<text x="{x0 + left - 5}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="10" fill="{INK2}">${v}</text>')
            v += step
        bw = pw / (N + 1)
        for x in d["niveles"]:
            n = x["campos_llenos"]
            cx = x0 + left + bw * (n + 0.5)
            o.append(f'<text x="{cx:.1f}" y="{y0 + top + ph + 14}" text-anchor="middle" font-size="10.5" fill="{INK2}">{n}</text>')
            if x["ecpm_ponderado"] is None or x["pct_requests_vendidos"] < a.min_share:
                if x["pct_requests_vendidos"] > 0:
                    o.append(f'<text x="{cx:.1f}" y="{y0 + top + ph + 27}" text-anchor="middle" font-size="9" fill="{INK2}">&lt;{a.min_share:g}%</text>')
                continue
            e = x["ecpm_ponderado"]
            h = (y0 + top + ph) - Y(e)
            o.append(f'<rect x="{cx - bw * 0.36:.1f}" y="{Y(e):.1f}" width="{bw * 0.72:.1f}" height="{h:.1f}" rx="3" fill="{AZUL}"/>')
            o.append(f'<text x="{cx:.1f}" y="{Y(e) - 4:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="{INK}">${e:.2f}</text>')
            o.append(f'<text x="{cx:.1f}" y="{y0 + top + ph + 27}" text-anchor="middle" font-size="9" fill="{INK2}">{x["pct_requests_vendidos"]:.0f}%</text>')
        o.append(f'<line x1="{x0 + left}" y1="{Y(d["ecpm_ponderado"]):.1f}" x2="{x0 + left + pw}" y2="{Y(d["ecpm_ponderado"]):.1f}" stroke="{INK2}" stroke-dasharray="4 3"/>')
        o.append(f'<text x="{x0 + left + pw / 2:.1f}" y="{y0 + PH - 4}" text-anchor="middle" font-size="10" fill="{INK}">content objects con dato útil (de 8)</text>')
    o.append("</svg>")
    open(os.path.join(a.salida_dir, "graficos-app-completitud-barras.svg"), "w", encoding="utf-8").write("\n".join(o))
    print(f"-> {a.salida_dir}: {len(apps)} apps")
    scatter_apps(app_q, set(apps), a.salida_dir, a.etiquetas)


if __name__ == "__main__":
    main()
