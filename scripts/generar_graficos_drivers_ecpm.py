# -*- coding: utf-8 -*-
"""Graficas SVG (sin dependencias) de lo que mueve el eCPM ponderado: la ruta de venta.

Sobre el consolidado, con eCPM ponderado = sum(eCPM x requests) / sum(requests) de las filas con
requests > 0 y eCPM > 0, y "% vendido" = requests con eCPM > 0 / requests totales:

  graficos-drivers-ecpm-heatmap-publisher-pais.svg   Publisher (filas, top N por requests vendidos)
                                                      x Pais (columnas): color = eCPM ponderado,
                                                      etiqueta = eCPM y share del trafico vendido
  graficos-drivers-ecpm-scatter-publisher.svg        un punto por publisher: % vendido (x) vs eCPM
                                                      ponderado (y), tamano = requests; lineas en
                                                      el promedio ponderado global de cada eje
  graficos-drivers-ecpm.json                          los datos de las dos graficas

Uso:
    python scripts/generar_graficos_drivers_ecpm.py inventory-consolidado.csv reportes/NN/recursos \
        [--top-publishers 12] [--paises "Mexico,Argentina,Colombia,Chile,Peru,Costa Rica"]
"""
import argparse
import csv
import json
import math
import os
from collections import defaultdict

csv.field_size_limit(10 ** 8)

INK, INK2, GRID = "#1f2933", "#5f6b76", "#e3e7ea"
ABR = {"MovieArk: Stream Movies & Live": "MovieArk", "Televisa Univision via SpringServe": "Televisa (SS)",
       "Televisa Univision via OB": "Televisa (OB)", "TCL ADS - Springserve": "TCL Springserve",
       "TCL ADs (APAC)": "TCL APAC", "Select Plus PTE LTD (CTV)": "Select Plus", "iion Pty Ltd": "iion",
       "OTTera.tv": "OTTera", "Equativ (Formerly SMART AdServer) - oRTB CTV": "Equativ",
       "Coocaa, a SKYWORTH company": "Coocaa", "TV Azteca - Springserve": "TV Azteca (SS)",
       "Browser TV Web - BrowseHere": "BrowseHere", "Roku - oRTB": "Roku", "Pluto LATAM via SpringServe": "Pluto (SS)",
       "METAX SOFTWARE PTE. LTD. (Exchange)": "METAX", "Zeasn Europe B.V.": "Zeasn", "Xapads Media - CTV": "Xapads",
       "Plex TV via SSHB": "Plex (SSHB)", "OneFox - Tubi": "Tubi (OneFox)", "PML Digital": "PML",
       "METAX SOFTWARE PTE. LTD.": "METAX (PTE)", "Kivi via Springserve": "Kivi (SS)", "Vidaa APAC Hisense": "Vidaa APAC"}
PAIS = {"Mexico": "México", "Argentina": "Argentina", "Colombia": "Colombia", "Chile": "Chile", "Peru": "Perú",
        "Costa Rica": "Costa Rica", "Panama": "Panamá", "Ecuador": "Ecuador", "Guatemala": "Guatemala"}


def abr(p):
    p = " ".join(p.split())
    if p in ABR:
        return ABR[p]
    for k, v in ABR.items():
        if p.startswith(k):
            return v
    return p[:18]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# Rampa secuencial de un solo tono (azul), claro -> oscuro
RAMPA = ["#e8f1fb", "#c5dbf4", "#9dc1ea", "#6fa3dd", "#4386cf", "#2a6fb8", "#1f568f", "#173f68"]


def color_seq(v, lo, hi):
    if hi <= lo:
        return RAMPA[0]
    t = max(0.0, min(1.0, (v - lo) / (hi - lo)))
    return RAMPA[min(len(RAMPA) - 1, int(t * len(RAMPA)))]


def texto_sobre(color):
    return "#ffffff" if RAMPA.index(color) >= 4 else INK


def agregar(csv_path):
    pub = defaultdict(lambda: [0, 0, 0.0])        # requests, requests vendidos, sum q*e
    pp = defaultdict(lambda: [0, 0, 0.0])         # (publisher, pais)
    pais = defaultdict(lambda: [0, 0, 0.0])
    tot = [0, 0, 0.0]
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            q = int(r["Total Requests"])
            if q <= 0:
                continue
            e = float(r["eCPM"])
            for a in (pub[r["Publisher"]], pp[(r["Publisher"], r["Country"])], pais[r["Country"]], tot):
                a[0] += q
                if e > 0:
                    a[1] += q
                    a[2] += q * e
    return pub, pp, pais, tot


def ecpm(a):
    return a[2] / a[1] if a[1] else None


def svg_heatmap(pubs, paises, pp, pais_tot, tot, out):
    cw, ch, left, top = 112, 44, 150, 96
    W = left + cw * len(paises) + 24
    H = top + ch * len(pubs) + 60
    vals = [ecpm(pp[(p, c)]) for p in pubs for c in paises if 100 * pp[(p, c)][1] / tot[1] >= 0.05]
    lo, hi = min(vals), max(vals)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="26" font-size="17" font-weight="700" fill="{INK}">eCPM ponderado por publisher y país (filas con eCPM &gt; 0)</text>',
         f'<text x="16" y="46" font-size="12" fill="{INK2}">Color = eCPM ponderado (más oscuro, más caro). En cada celda: eCPM y % del tráfico vendido del consolidado que cae ahí. '
         f'Gris: menos de 0.05% del tráfico vendido.</text>']
    # encabezados de columna: pais + % del trafico vendido total
    for j, c in enumerate(paises):
        x = left + j * cw + cw / 2
        o.append(f'<text x="{x}" y="{top - 26}" text-anchor="middle" font-weight="600" fill="{INK}">{esc(PAIS.get(c, c))}</text>')
        o.append(f'<text x="{x}" y="{top - 10}" text-anchor="middle" fill="{INK2}">{100 * pais_tot[c][1] / tot[1]:.1f}% vendido</text>')
    for i, p in enumerate(pubs):
        y = top + i * ch
        o.append(f'<text x="{left - 8}" y="{y + ch / 2 + 4}" text-anchor="end" fill="{INK}">{esc(abr(p))}</text>')
        for j, c in enumerate(paises):
            a = pp[(p, c)]
            x = left + j * cw
            share = 100 * a[1] / tot[1]
            if a[1] == 0 or share < 0.05:
                o.append(f'<rect x="{x + 1}" y="{y + 1}" width="{cw - 2}" height="{ch - 2}" rx="4" fill="#f3f4f6"/>')
                continue
            e = ecpm(a)
            col = color_seq(e, lo, hi)
            tc = texto_sobre(col)
            o.append(f'<rect x="{x + 1}" y="{y + 1}" width="{cw - 2}" height="{ch - 2}" rx="4" fill="{col}"/>')
            o.append(f'<text x="{x + cw / 2}" y="{y + ch / 2 - 2}" text-anchor="middle" font-weight="700" fill="{tc}">${e:.2f}</text>')
            o.append(f'<text x="{x + cw / 2}" y="{y + ch / 2 + 13}" text-anchor="middle" font-size="10.5" fill="{tc}">{share:.1f}%</text>')
    # leyenda de la rampa
    ly = top + ch * len(pubs) + 22
    o.append(f'<text x="{left}" y="{ly + 11}" fill="{INK2}">eCPM ponderado: ${lo:.2f}</text>')
    lx = left + 150
    for k, col in enumerate(RAMPA):
        o.append(f'<rect x="{lx + k * 22}" y="{ly}" width="22" height="14" fill="{col}"/>')
    o.append(f'<text x="{lx + 22 * len(RAMPA) + 8}" y="{ly + 11}" fill="{INK2}">${hi:.2f}</text>')
    o.append("</svg>")
    open(out, "w", encoding="utf-8").write("\n".join(o))


def svg_scatter(pubs, pub, tot, out):
    W, H = 960, 580
    left, right, top, bottom = 70, 130, 84, 60
    pw, ph = W - left - right, H - top - bottom
    pts = [(p, 100 * pub[p][1] / pub[p][0], ecpm(pub[p]), pub[p][0]) for p in pubs]
    ymax = max(pt[2] for pt in pts) * 1.12
    qmax = max(pt[3] for pt in pts)
    gx = 100 * tot[1] / tot[0]
    gy = tot[2] / tot[1]

    def X(v):
        return left + pw * v / 100

    def Y(v):
        return top + ph * (1 - v / ymax)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="26" font-size="17" font-weight="700" fill="{INK}">Publishers: % de requests vendidos vs eCPM ponderado</text>',
         f'<text x="16" y="46" font-size="12" fill="{INK2}">Un punto por publisher (top {len(pts)} por requests); el tamaño es el total de requests. '
         f'Las líneas punteadas son el promedio ponderado del consolidado: {gx:.0f}% vendido y ${gy:.2f}.</text>']
    for k in range(0, 101, 20):
        o.append(f'<line x1="{X(k)}" y1="{top}" x2="{X(k)}" y2="{top + ph}" stroke="{GRID}"/>')
        o.append(f'<text x="{X(k)}" y="{top + ph + 18}" text-anchor="middle" fill="{INK2}">{k}%</text>')
    step = 1 if ymax <= 8 else 2
    v = 0
    while v <= ymax - 0.6:
        o.append(f'<line x1="{left}" y1="{Y(v)}" x2="{left + pw}" y2="{Y(v)}" stroke="{GRID}"/>')
        o.append(f'<text x="{left - 8}" y="{Y(v) + 4}" text-anchor="end" fill="{INK2}">${v:.0f}</text>')
        v += step
    o.append(f'<text x="{left + pw / 2}" y="{H - 14}" text-anchor="middle" fill="{INK}">% de requests vendidos (eCPM &gt; 0)</text>')
    o.append(f'<text transform="translate(18,{top + ph / 2}) rotate(-90)" text-anchor="middle" fill="{INK}">eCPM ponderado ($)</text>')
    o.append(f'<line x1="{X(gx)}" y1="{top}" x2="{X(gx)}" y2="{top + ph}" stroke="{INK2}" stroke-dasharray="4 4"/>')
    o.append(f'<line x1="{left}" y1="{Y(gy)}" x2="{left + pw}" y2="{Y(gy)}" stroke="{INK2}" stroke-dasharray="4 4"/>')
    for p, x, y, q in sorted(pts, key=lambda t: -t[3]):
        r = 6 + 26 * math.sqrt(q / qmax)
        o.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{r:.1f}" fill="#2a78d6" fill-opacity="0.55" stroke="#ffffff" stroke-width="2"/>')
    # etiquetas directas con anticolision: se recorren de arriba a abajo y, si dos etiquetas
    # cercanas en x se pisan, la segunda baja 13 px (y queda unida al punto con una guia)
    labels = []
    for p, x, y, q in sorted(pts, key=lambda t: Y(t[2])):
        r = 6 + 26 * math.sqrt(q / qmax)
        lx, ly = X(x) + r + 4, Y(y) + 4
        for _, ox, oy, ow in labels:
            if abs(oy - ly) < 13 and lx < ox + ow and ox < lx + 7 * len(abr(p)):
                ly = oy + 13
        labels.append((p, lx, ly, 7 * len(abr(p))))
        if abs(ly - (Y(y) + 4)) > 6:
            o.append(f'<line x1="{X(x) + r:.1f}" y1="{Y(y):.1f}" x2="{lx - 2:.1f}" y2="{ly - 4:.1f}" stroke="{INK2}" stroke-width="1"/>')
        o.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{INK}">{esc(abr(p))}</text>')
    o.append("</svg>")
    open(out, "w", encoding="utf-8").write("\n".join(o))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida_dir")
    ap.add_argument("--top-publishers", type=int, default=12)
    ap.add_argument("--paises", default="Mexico,Argentina,Colombia,Chile,Peru,Costa Rica")
    a = ap.parse_args()
    os.makedirs(a.salida_dir, exist_ok=True)
    pub, pp, pais, tot = agregar(a.entrada)
    paises = [c.strip() for c in a.paises.split(",")]
    pubs = [p for p, _ in sorted(pub.items(), key=lambda kv: -kv[1][1])[:a.top_publishers]]   # por requests vendidos
    pubs_sc = [p for p, _ in sorted(pub.items(), key=lambda kv: -kv[1][0])[:20] if pub[p][1] > 0]  # por requests
    res = {"fuente": a.entrada, "total": {"requests": tot[0], "requests_vendidos": tot[1],
                                          "pct_vendido": round(100 * tot[1] / tot[0], 1), "ecpm_ponderado": round(tot[2] / tot[1], 3)},
           "paises": paises,
           "heatmap": {p: {c: ({"ecpm_ponderado": round(ecpm(pp[(p, c)]), 3), "share_trafico_vendido_pct": round(100 * pp[(p, c)][1] / tot[1], 2),
                               "pct_vendido": round(100 * pp[(p, c)][1] / pp[(p, c)][0], 1)} if pp[(p, c)][1] else None)
                           for c in paises} for p in pubs},
           "publishers": {p: {"requests": pub[p][0], "pct_vendido": round(100 * pub[p][1] / pub[p][0], 1),
                              "ecpm_ponderado": round(ecpm(pub[p]), 3), "share_trafico_vendido_pct": round(100 * pub[p][1] / tot[1], 2)}
                          for p in pubs_sc}}
    json.dump(res, open(os.path.join(a.salida_dir, "graficos-drivers-ecpm.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    svg_heatmap(pubs, paises, pp, pais, tot, os.path.join(a.salida_dir, "graficos-drivers-ecpm-heatmap-publisher-pais.svg"))
    svg_scatter(pubs_sc, pub, tot, os.path.join(a.salida_dir, "graficos-drivers-ecpm-scatter-publisher.svg"))
    print(f"-> {a.salida_dir}: {len(pubs)} publishers x {len(paises)} paises; scatter de {len(pubs_sc)} publishers")


if __name__ == "__main__":
    main()
