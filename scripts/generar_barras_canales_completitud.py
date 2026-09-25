# -*- coding: utf-8 -*-
"""Completitud de los content objects por canal (barras apiladas, una por canal).

Un canal se identifica por su Publisher o su App Name (patrones en CANALES, ampliables). Para
cada canal se calcula el % de filas con dato util en cada uno de los 8 content objects. La barra
del canal apila un segmento por columna con altura = % de esa columna / 8, de modo que la altura
total es la completitud promedio de las 8 columnas (0-100 %). Dentro de cada segmento va el
nombre de la columna y su % propio. Los canales sin filas en el consolidado quedan marcados.

Uso:
    python scripts/generar_barras_canales_completitud.py inventory-consolidado.csv reportes/NN/recursos
Escribe graficos-canales-completitud-barras.svg y graficos-canales-completitud-barras.json.
"""
import argparse
import csv
import json
import os
import re

SENT = {"not available", "not applicable", "unknown", "n/a", "null", "undefined", "none", "-", ""}
MD5 = "d41d8cd98f00b204e9800998ecf8427e"
CO = ["contentTitle", "contentGenre", "contentRating", "contentLanguage", "contentIsLiveStream",
      "contentCategory", "contentLength", "contentSeries"]
ABR = {"contentTitle": "Title", "contentGenre": "Genre", "contentRating": "Rating", "contentLanguage": "Language",
       "contentIsLiveStream": "LiveStream", "contentCategory": "Category", "contentLength": "Length", "contentSeries": "Series"}
C_COL = {"contentTitle": "#2e9e6b", "contentGenre": "#eb6834", "contentRating": "#8b5cf6", "contentLanguage": "#d64545",
         "contentIsLiveStream": "#0e9aa7", "contentCategory": "#a0622d", "contentLength": "#d6409f", "contentSeries": "#6b7280"}
# canal -> (patron sobre Publisher, patron sobre App Name); una fila pertenece al canal si cumple cualquiera
CANALES = [("Caracol", r"^caracol\b", r"caracol"),
           ("Win", r"\bwin\b", r"\bwin\b"),
           ("RCN", r"^rcn\b", r"\brcn\b"),
           ("Canal 13", r"^canal 13\b", r"^canal ?13\b|^t13\b"),
           ("Telefe", r"telefe", r"telefe"),
           ("Televisa", r"^televisa", r"^vix\b|^vix:|televisa"),
           ("TV Azteca", r"^tv azteca", r"^azteca")]
INK, INK2, GRID = "#1f2933", "#5f6b76", "#e3e7ea"


def util(c, v):
    s = (v or "").strip()
    if s.lower() in SENT:
        return False
    if c == "contentCategory" and s == "[-7]":
        return False
    if c == "contentSeries" and (s.lower() == MD5 or s.startswith("{{")):
        return False
    if c == "contentTitle" and s.startswith("{{"):
        return False
    if c == "contentIsLiveStream" and s not in ("0", "1"):
        return False
    return True


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida_dir")
    a = ap.parse_args()
    csv.field_size_limit(10 ** 9)
    pats = [(nombre, re.compile(pp, re.I), re.compile(pa, re.I)) for nombre, pp, pa in CANALES]
    acc = {nombre: {"filas": 0, "requests": 0, "req_vend": 0, "sum_qe": 0.0, "llenas": {c: 0 for c in CO}, "publishers": {}, "apps": {}}
           for nombre, _, _ in CANALES}
    with open(a.entrada, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            pub, app = (r["Publisher"] or "").strip(), (r["App Name"] or "").strip()
            for nombre, rp, ra in pats:
                if rp.search(pub) or ra.search(app):
                    d = acc[nombre]
                    q, e = int(r["Total Requests"]), float(r["eCPM"])
                    d["filas"] += 1
                    d["requests"] += q
                    if q > 0 and e > 0:
                        d["req_vend"] += q
                        d["sum_qe"] += q * e
                    d["publishers"][pub] = d["publishers"].get(pub, 0) + 1
                    d["apps"][app] = d["apps"].get(app, 0) + 1
                    for c in CO:
                        if util(c, r[c]):
                            d["llenas"][c] += 1
    out = {"fuente": a.entrada, "campos": CO, "canales": []}
    for nombre, _, _ in CANALES:
        d = acc[nombre]
        pct = {c: (round(100 * d["llenas"][c] / d["filas"], 1) if d["filas"] else None) for c in CO}
        out["canales"].append({"canal": nombre, "filas": d["filas"], "requests": d["requests"],
                               "requests_vendidos": d["req_vend"],
                               "pct_vendido": round(100 * d["req_vend"] / d["requests"], 1) if d["requests"] else None,
                               "ecpm_ponderado": round(d["sum_qe"] / d["req_vend"], 3) if d["req_vend"] else None,
                               "pct_llenas": pct,
                               "completitud_promedio": round(sum(pct.values()) / len(CO), 1) if d["filas"] else None,
                               "publishers": sorted(d["publishers"], key=d["publishers"].get, reverse=True)[:4],
                               "apps": sorted(d["apps"], key=d["apps"].get, reverse=True)[:4]})
    # de mayor a menor completitud promedio; los canales sin filas al final
    out["canales"].sort(key=lambda d: -(d["completitud_promedio"] if d["completitud_promedio"] is not None else -1))
    json.dump(out, open(os.path.join(a.salida_dir, "graficos-canales-completitud-barras.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # ---- SVG
    W, H = 1040, 600
    left, right, top_m, bottom = 60, 30, 96, 70
    pw, ph = W - left - right, H - top_m - bottom
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">Completitud de los content objects por canal</text>',
         f'<text x="16" y="44" font-size="12" fill="{INK2}">Cada segmento es una columna: su altura es el % de filas del canal con dato útil en esa columna, dividido entre 8; '
         f'la barra completa es la completitud promedio de las 8 columnas.</text>',
         f'<text x="16" y="60" font-size="12" fill="{INK2}">Canal = filas cuyo Publisher o App Name lo nombra. Segmentos de mayor a menor % de arriba hacia abajo; debajo de cada barra, filas del canal.</text>']
    lx = 16
    for c in CO:
        o.append(f'<rect x="{lx}" y="72" width="12" height="12" rx="2" fill="{C_COL[c]}"/>')
        o.append(f'<text x="{lx + 16}" y="82" font-size="11" fill="{INK}">{ABR[c]}</text>')
        lx += 16 + 6.5 * len(ABR[c]) + 18
    for v in range(0, 101, 20):
        y = top_m + ph * (1 - v / 100)
        o.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + pw}" y2="{y:.1f}" stroke="{GRID}"/>')
        o.append(f'<text x="{left - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="10.5" fill="{INK2}">{v}%</text>')
    o.append(f'<text transform="translate(18,{top_m + ph / 2:.1f}) rotate(-90)" text-anchor="middle" fill="{INK}">% de completitud (promedio de las 8 columnas)</text>')
    n = len(out["canales"])
    bw = pw / n
    ybase = top_m + ph
    for i, d in enumerate(out["canales"]):
        x0 = left + bw * (i + 0.18)
        w = bw * 0.64
        if not d["filas"]:
            o.append(f'<rect x="{x0:.1f}" y="{ybase - 4}" width="{w:.1f}" height="4" fill="{GRID}"/>')
            o.append(f'<text x="{x0 + w / 2:.1f}" y="{ybase - 12}" text-anchor="middle" font-size="10.5" fill="{INK2}">sin filas en el consolidado</text>')
        else:
            acum = 0.0
            # de abajo hacia arriba, de menor a mayor % de filas llenas: la columna mas llena queda arriba
            for c in sorted(CO, key=lambda c: d["pct_llenas"][c]):
                h = ph * d["pct_llenas"][c] / 100 / len(CO)
                if h <= 0:
                    continue
                o.append(f'<rect x="{x0:.1f}" y="{ybase - acum - h:.1f}" width="{w:.1f}" height="{max(h - 1, 0.5):.1f}" fill="{C_COL[c]}"/>')
                if h >= 13:
                    o.append(f'<text x="{x0 + w / 2:.1f}" y="{ybase - acum - h / 2 + 4:.1f}" text-anchor="middle" font-size="10.5" fill="#ffffff">{ABR[c]} {d["pct_llenas"][c]:.0f}%</text>')
                acum += h
            o.append(f'<text x="{x0 + w / 2:.1f}" y="{ybase - acum - 6:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="{INK}">{d["completitud_promedio"]:.0f}%</text>')
        o.append(f'<text x="{x0 + w / 2:.1f}" y="{ybase + 18}" text-anchor="middle" font-size="12" font-weight="600" fill="{INK}">{esc(d["canal"])}</text>')
        o.append(f'<text x="{x0 + w / 2:.1f}" y="{ybase + 33}" text-anchor="middle" font-size="10.5" fill="{INK2}">{d["filas"]:,} filas</text>')
    o.append("</svg>")
    open(os.path.join(a.salida_dir, "graficos-canales-completitud-barras.svg"), "w", encoding="utf-8").write("\n".join(o))
    svg_scatter(out, os.path.join(a.salida_dir, "graficos-canales-requests-ecpm.svg"))
    for d in out["canales"]:
        print(f'{d["canal"]:10} filas {d["filas"]:>7,}  promedio {d["completitud_promedio"]}  eCPM {d["ecpm_ponderado"]}  pubs {d["publishers"][:2]}')


def svg_scatter(out, path):
    """Un punto por canal: requests totales (x, escala log) vs eCPM ponderado (y)."""
    import math
    pts = [d for d in out["canales"] if d["requests"] and d["ecpm_ponderado"] is not None]
    sin = [d["canal"] for d in out["canales"] if not d["requests"]]
    sin_venta = [d["canal"] for d in out["canales"] if d["requests"] and d["ecpm_ponderado"] is None]
    W, H = 900, 540
    left, right, top_m, bottom = 64, 40, 86, 70
    pw, ph = W - left - right, H - top_m - bottom
    xs = [math.log10(d["requests"]) for d in pts]
    lo, hi = math.floor(min(xs)) , math.ceil(max(xs))
    ymax = max(d["ecpm_ponderado"] for d in pts) * 1.2

    def X(q):
        return left + pw * (math.log10(q) - lo) / (hi - lo)

    def Y(e):
        return top_m + ph * (1 - e / ymax)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">Canales: requests totales vs eCPM ponderado</text>',
         f'<text x="16" y="44" font-size="12" fill="{INK2}">Un punto por canal (Publisher o App Name que lo nombra). x = requests totales del canal en escala logarítmica;</text>',
         f'<text x="16" y="60" font-size="12" fill="{INK2}">y = eCPM ponderado de sus filas con eCPM &gt; 0. Junto al punto, requests totales y % de requests vendidos.</text>']
    for k in range(lo, hi + 1):
        q = 10 ** k
        o.append(f'<line x1="{X(q):.1f}" y1="{top_m}" x2="{X(q):.1f}" y2="{top_m + ph}" stroke="{GRID}"/>')
        lab = {6: "1 M", 7: "10 M", 8: "100 M", 9: "1,000 M", 10: "10,000 M", 11: "100,000 M"}.get(k, f"1e{k}")
        o.append(f'<text x="{X(q):.1f}" y="{top_m + ph + 18}" text-anchor="middle" font-size="10.5" fill="{INK2}">{lab}</text>')
    step = 1 if ymax <= 8 else 2
    v = 0
    while v < ymax:
        o.append(f'<line x1="{left}" y1="{Y(v):.1f}" x2="{left + pw}" y2="{Y(v):.1f}" stroke="{GRID}"/>')
        o.append(f'<text x="{left - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="10.5" fill="{INK2}">${v}</text>')
        v += step
    o.append(f'<text x="{left + pw / 2:.1f}" y="{H - 30}" text-anchor="middle" fill="{INK}">requests totales del canal (escala log)</text>')
    o.append(f'<text transform="translate(18,{top_m + ph / 2:.1f}) rotate(-90)" text-anchor="middle" fill="{INK}">eCPM ponderado ($)</text>')
    for d in pts:
        x, y = X(d["requests"]), Y(d["ecpm_ponderado"])
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#2a78d6" stroke="#ffffff" stroke-width="2"/>')
        # etiqueta a la derecha del punto, o a la izquierda si queda cerca del borde derecho
        izq = x > left + pw * 0.72
        tx, anc = (x - 12, "end") if izq else (x + 12, "start")
        o.append(f'<text x="{tx:.1f}" y="{y - 2:.1f}" text-anchor="{anc}" font-size="12" font-weight="600" fill="{INK}">{esc(d["canal"])} · ${d["ecpm_ponderado"]:.2f}</text>')
        o.append(f'<text x="{tx:.1f}" y="{y + 12:.1f}" text-anchor="{anc}" font-size="10.5" fill="{INK2}">{d["requests"]:,} req · {d["pct_vendido"]:.0f}% vendidos</text>')
    notas = []
    if sin:
        notas.append(f"Sin filas en el consolidado: {', '.join(sin)}.")
    if sin_venta:
        notas.append(f"Con requests pero sin ninguna fila vendida (eCPM > 0), por eso no tienen punto: {', '.join(sin_venta)}.")
    if notas:
        o.append(f'<text x="{left}" y="{H - 10}" font-size="10.5" fill="{INK2}">{esc(" ".join(notas))}</text>')
    o.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(o))


if __name__ == "__main__":
    main()
