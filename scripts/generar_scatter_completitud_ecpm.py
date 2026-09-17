# -*- coding: utf-8 -*-
"""Scatter fila a fila: completitud de content objects (0-8 campos con dato util) en x, eCPM
en escala logaritmica en y. Cada punto es un registro del consolidado con eCPM > 0 y
requests > 0; el tamano es su volumen de requests. Sobre cada nivel se marca el eCPM
ponderado (>0) de ese nivel, unido por una linea, con la etiqueta del valor.

Como el consolidado tiene cientos de miles de filas vendidas, por nivel y panel se dibuja una
muestra: las --top filas de mas requests (las que pesan en el ponderado) mas --muestra filas al
azar (semilla fija). El eCPM ponderado y las tablas se calculan con TODAS las filas.

Un panel por grupo: total y los paises pedidos. SVG sin dependencias.

Uso:
    python generar_scatter_completitud_ecpm.py consolidado.csv carpeta_salida \
        [--paises "Mexico,Colombia,Chile"] [--muestra 500] [--top 40]
Escribe graficos-ecpm-completitud-scatter.svg y graficos-ecpm-completitud-scatter.json.
"""
import argparse
import csv
import json
import math
import os
import random

SENT = {"not available", "not applicable", "unknown", "n/a", "null", "undefined", "none", "-", ""}
MD5 = "d41d8cd98f00b204e9800998ecf8427e"
CO = ["contentGenre", "contentCategory", "contentSeries", "contentLength", "contentLanguage",
      "contentIsLiveStream", "contentTitle", "contentRating"]
N = len(CO)
TITULO = {"(todos)": "Total consolidado", "Mexico": "México", "Colombia": "Colombia", "Chile": "Chile", "Peru": "Perú",
          "Argentina": "Argentina"}
INK, INK2, GRID, AZUL, NARANJA = "#1f2933", "#5f6b76", "#e3e7ea", "#2a78d6", "#eb6834"
YMIN, YMAX = 0.1, 200.0


def util(c, v):
    s = v.strip()
    if s.lower() in SENT:
        return False
    if c == "contentCategory" and s == "[-7]":
        return False
    if c == "contentSeries" and s.lower() == MD5:
        return False
    if c == "contentIsLiveStream" and s not in ("0", "1"):
        return False
    return True


def panel(o, x0, y0, w, h, g, agg, pts, tot_req_vendido):
    left, top, bottom = 52, 34, 56
    pw, ph = w - left - 16, h - top - bottom

    def X(sc):
        return x0 + left + pw * (sc + 0.5) / (N + 1)

    def Y(e):
        e = min(max(e, YMIN), YMAX)
        return y0 + top + ph * (1 - (math.log10(e) - math.log10(YMIN)) / (math.log10(YMAX) - math.log10(YMIN)))
    tot_req = sum(t[1] for t in agg)
    o.append(f'<text x="{x0 + left}" y="{y0 + 18}" font-size="13" font-weight="700" fill="{INK}">{TITULO.get(g, g)}</text>')
    # grid y (log)
    for e in (0.1, 0.3, 1, 3, 10, 30, 100):
        o.append(f'<line x1="{x0 + left}" y1="{Y(e):.1f}" x2="{x0 + left + pw}" y2="{Y(e):.1f}" stroke="{GRID}"/>')
        o.append(f'<text x="{x0 + left - 6}" y="{Y(e) + 4:.1f}" text-anchor="end" font-size="10.5" fill="{INK2}">${e:g}</text>')
    for sc in range(N + 1):
        o.append(f'<text x="{X(sc):.1f}" y="{y0 + top + ph + 16}" text-anchor="middle" font-size="10.5" fill="{INK2}">{sc}</text>')
        t = agg[sc]
        if tot_req:
            o.append(f'<text x="{X(sc):.1f}" y="{y0 + top + ph + 30}" text-anchor="middle" font-size="9.5" fill="{INK2}">{100 * t[1] / tot_req:.0f}% req</text>')
    o.append(f'<text x="{x0 + left + pw / 2:.1f}" y="{y0 + h - 2}" text-anchor="middle" font-size="10.5" fill="{INK}">content objects con dato útil (de 8) · debajo: % de los requests del grupo en ese nivel</text>')
    # puntos (muestra), tamano ~ sqrt(requests)
    qmax = max((q for _, _, q in pts), default=1)
    rnd = random.Random(7)
    for sc, e, q in pts:
        r = 1.6 + 7.0 * math.sqrt(q / qmax)
        jx = (rnd.random() - 0.5) * pw / (N + 1) * 0.72
        o.append(f'<circle cx="{X(sc) + jx:.1f}" cy="{Y(e):.1f}" r="{r:.1f}" fill="{AZUL}" fill-opacity="0.28" stroke="none"/>')
    # eCPM ponderado por nivel
    path = []
    for sc in range(N + 1):
        t = agg[sc]
        if t[3]:
            path.append((X(sc), Y(t[2] / t[3]), t[2] / t[3]))
    if len(path) > 1:
        o.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in path) + f'" fill="none" stroke="{NARANJA}" stroke-width="2"/>')
    for x, y, e in path:
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{NARANJA}" stroke="#ffffff" stroke-width="2"/>')
        o.append(f'<text x="{x:.1f}" y="{y - 10:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="{INK}">${e:.2f}</text>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida_dir")
    ap.add_argument("--paises", default="Mexico,Colombia,Chile")
    ap.add_argument("--muestra", type=int, default=300, help="filas al azar por nivel y panel")
    ap.add_argument("--top", type=int, default=40, help="filas de mas requests por nivel y panel (siempre se dibujan)")
    a = ap.parse_args()
    grupos = ["(todos)"] + [p.strip() for p in a.paises.split(",")]
    agg = {g: [[0, 0, 0.0, 0] for _ in range(N + 1)] for g in grupos}   # filas, req, sum e*req(>0), req_nz
    vend = {g: [[] for _ in range(N + 1)] for g in grupos}               # (e, q) de filas vendidas
    csv.field_size_limit(10 ** 9)
    with open(a.entrada, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            req = int(row["Total Requests"])
            e = float(row["eCPM"])
            sc = sum(1 for c in CO if util(c, row[c]))
            for g in ["(todos)"] + ([row["Country"]] if row["Country"] in agg else []):
                t = agg[g][sc]
                t[0] += 1
                t[1] += req
                if e > 0 and req > 0:
                    t[2] += e * req
                    t[3] += req
                    vend[g][sc].append((e, req))
    rnd = random.Random(19)
    muestra = {}
    for g in grupos:
        pts = []
        for sc in range(N + 1):
            filas = vend[g][sc]
            filas.sort(key=lambda t: -t[1])
            top = filas[:a.top]
            resto = filas[a.top:]
            sel = top + (rnd.sample(resto, a.muestra) if len(resto) > a.muestra else resto)
            pts += [(sc, e, q) for e, q in sel]
        muestra[g] = pts
    out = {"fuente": a.entrada, "campos": CO, "muestra_por_nivel": {"top_requests": a.top, "azar": a.muestra}, "grupos": {}}
    for g in grupos:
        tot_req = sum(t[1] for t in agg[g])
        tot_filas = sum(t[0] for t in agg[g])
        niveles = []
        for sc in range(N + 1):
            t = agg[g][sc]
            niveles.append({"campos_llenos": sc, "filas": t[0], "pct_filas": round(100 * t[0] / tot_filas, 2) if tot_filas else 0,
                            "requests": t[1], "pct_requests": round(100 * t[1] / tot_req, 2) if tot_req else 0,
                            "pct_req_monetizado": round(100 * t[3] / t[1], 2) if t[1] else None,
                            "ecpm_ponderado": round(t[2] / t[3], 3) if t[3] else None,
                            "filas_vendidas": len(vend[g][sc]), "puntos_dibujados": sum(1 for p in muestra[g] if p[0] == sc)})
        out["grupos"][g] = {"filas": tot_filas, "requests": tot_req, "niveles": niveles}
    json.dump(out, open(os.path.join(a.salida_dir, "graficos-ecpm-completitud-scatter.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # SVG: 2 x 2 paneles
    PW, PH, cols = 560, 360, 2
    rows = math.ceil(len(grupos) / cols)
    W, H = 16 + PW * cols, 70 + PH * rows
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">eCPM (escala log) según cuántos content objects trae cada registro</text>',
         f'<text x="16" y="44" font-size="12" fill="{INK2}">Cada punto es un registro con eCPM &gt; 0 (tamaño = requests; muestra: los {a.top} de más requests y {a.muestra} al azar por nivel). '
         f'Naranja: eCPM ponderado por requests de todos los registros de ese nivel.</text>',
         f'<circle cx="24" cy="60" r="5" fill="{AZUL}" fill-opacity="0.4"/><text x="34" y="64" font-size="11.5" fill="{INK}">registro (eCPM &gt; 0)</text>',
         f'<circle cx="190" cy="60" r="5" fill="{NARANJA}"/><text x="200" y="64" font-size="11.5" fill="{INK}">eCPM ponderado del nivel</text>']
    for i, g in enumerate(grupos):
        x0, y0 = 16 + PW * (i % cols), 70 + PH * (i // cols)
        panel(o, x0, y0, PW, PH, g, agg[g], muestra[g], None)
    o.append("</svg>")
    open(os.path.join(a.salida_dir, "graficos-ecpm-completitud-scatter.svg"), "w", encoding="utf-8").write("\n".join(o))
    for g in grupos:
        print(g, [(n["campos_llenos"], n["pct_requests"], n["ecpm_ponderado"]) for n in out["grupos"][g]["niveles"]])
    print("->", a.salida_dir)


if __name__ == "__main__":
    main()
