# -*- coding: utf-8 -*-
"""Graficas sobre los registros SIN contentTitle (SVG sin dependencias), a partir del consolidado tal
como llega (antes del relleno; el enriquecido solo le agrega genero_normalizado y rating_franja).

  graficos-sin-titulo-con-sin-dato.svg  por content object: eCPM ponderado de las filas (sin titulo) que
                                    traen dato util en la columna vs el de las que la traen vacia,
                                    dos marcas por columna unidas por una linea del color de la
                                    columna, con el % de filas de cada grupo
  graficos-sin-titulo-con-sin-dato-requests.svg  lo mismo con los requests totales de cada grupo en el eje x
  graficos-sin-titulo-genero-requests-ecpm.svg  top 20 generos (normalizados, sin el sufijo "(generico)") por
                                    requests en las filas sin titulo, doble eje Y: barras = requests
                                    totales (izquierdo), linea = eCPM ponderado (derecho)
  graficos-sin-titulo.json          los datos de las dos graficas

eCPM ponderado = sum(eCPM x requests) / sum(requests) de las filas con requests > 0 y eCPM > 0.

Uso:
    python scripts/generar_graficos_sin_titulo.py inventory-consolidado-enriquecido.csv reportes/NN/recursos
"""
import argparse
import csv
import json
import os
from collections import defaultdict

SENT = {"not available", "not applicable", "unknown", "n/a", "null", "undefined", "none", "-", ""}
MD5 = "d41d8cd98f00b204e9800998ecf8427e"
CO = ["contentGenre", "contentRating", "contentLanguage", "contentIsLiveStream", "contentCategory", "contentLength", "contentSeries"]
ABR = {"contentGenre": "Genre", "contentRating": "Rating", "contentLanguage": "Language", "contentIsLiveStream": "LiveStream",
       "contentCategory": "Category", "contentLength": "Length", "contentSeries": "Series"}
C_COL = {"contentGenre": "#eb6834", "contentRating": "#8b5cf6", "contentLanguage": "#d64545", "contentIsLiveStream": "#0e9aa7",
         "contentCategory": "#a0622d", "contentLength": "#d6409f", "contentSeries": "#6b7280"}
INK, INK2, GRID, AZUL = "#1f2933", "#5f6b76", "#e3e7ea", "#2a78d6"
TOP_GENEROS = 20   # generos (por requests totales) en la grafica de eCPM y requests por genero


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


def R2_FACTORES(r):
    """Valores (tal como llegan) de cada content object para el R2; genero y rating normalizados."""
    g = r.get
    return {"genero": g("genero_normalizado") or "", "rating": g("rating_franja") or "",
            "livestream": g("contentIsLiveStream") or "", "length": g("contentLength") or "",
            "categoria": g("contentCategory") or "", "series": g("contentSeries") or ""}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida_dir")
    a = ap.parse_args()
    csv.field_size_limit(10 ** 9)
    n_filas = 0
    req_tot = req_vend = 0
    qe_tot = 0.0
    col = {c: {"con": [0, 0, 0, 0.0], "sin": [0, 0, 0, 0.0]} for c in CO}   # filas, requests, req vendidos, sum q*e
    gen = defaultdict(lambda: [0, 0, 0.0, 0])                             # filas, req vendidos, sum q*e, requests totales
    # R2 del eCPM (ponderado por requests, filas vendidas): cuanto explica cada content object solo y
    # cuanto agrega por encima de la ruta de venta (publisher x pais)
    r2s = [0, 0.0, 0.0]                                                   # W, S, sum q*e^2
    r2g = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))              # factor -> valor -> [W, S]
    with open(a.entrada, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if util("contentTitle", r["contentTitle"]):
                continue
            q = int(r["Total Requests"])
            if q <= 0:
                continue
            e = float(r["eCPM"])
            n_filas += 1
            req_tot += q
            vend = e > 0
            if vend:
                req_vend += q
                qe_tot += q * e
            for c in CO:
                t = col[c]["con" if util(c, r[c]) else "sin"]
                t[0] += 1
                t[1] += q
                if vend:
                    t[2] += q
                    t[3] += q * e
            if vend:
                ruta = (r["Publisher"], r["Country"])
                r2s[0] += q
                r2s[1] += q * e
                r2s[2] += q * e * e
                r2g["ruta"][ruta][0] += q
                r2g["ruta"][ruta][1] += q * e
                for fac, v in R2_FACTORES(r).items():
                    for k in ((fac, v), (fac + "+ruta", (ruta, v))):
                        x = r2g[k[0]][k[1]]
                        x[0] += q
                        x[1] += q * e
            # sin el sufijo "(generico)" del normalizador: "pelicula (generico)" -> "pelicula"
            g = (r.get("genero_normalizado") or "").split(";")[0].replace("(generico)", "").strip() or "(sin género)"
            t = gen[g]
            t[0] += 1
            t[3] += q
            if vend:
                t[1] += q
                t[2] += q * e
    mu = qe_tot / req_vend
    out = {"fuente": a.entrada, "filas_sin_titulo": n_filas, "requests": req_tot, "requests_vendidos": req_vend,
           "pct_vendido": round(100 * req_vend / req_tot, 1), "ecpm_ponderado": round(mu, 3), "columnas": {}, "genero": []}
    for c in CO:
        out["columnas"][c] = {k: {"filas": t[0], "pct_filas": round(100 * t[0] / n_filas, 1), "requests": t[1],
                                  "requests_vendidos": t[2], "pct_vendido": round(100 * t[2] / t[1], 1) if t[1] else None,
                                  "ecpm_ponderado": round(t[3] / t[2], 3) if t[2] else None}
                              for k, t in col[c].items()}
    for g, t in sorted(gen.items(), key=lambda kv: -kv[1][3]):   # de mas a menos requests totales
        out["genero"].append({"genero": g, "filas": t[0], "requests": t[3], "requests_vendidos": t[1],
                              "pct_vendido": round(100 * t[1] / t[3], 1) if t[3] else None,
                              "share_trafico_vendido_pct": round(100 * t[1] / req_vend, 1),
                              "ecpm_ponderado": round(t[2] / t[1], 3) if t[1] else None})
    base = r2s[1] ** 2 / r2s[0]

    def r2(fac):
        return 100 * (sum(S * S / W for W, S in r2g[fac].values()) - base) / (r2s[2] - base)
    r_ruta = r2("ruta")
    out["r2"] = {"ruta_publisher_pais_pct": round(r_ruta, 1),
                 "factores": {fac: {"solo_pct": round(r2(fac), 1), "extra_sobre_ruta_pp": round(r2(fac + "+ruta") - r_ruta, 1)}
                              for fac in R2_FACTORES({}).keys()}}
    json.dump(out, open(os.path.join(a.salida_dir, "graficos-sin-titulo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- 1. dumbbell: eCPM ponderado con dato vs sin dato, por columna
    cols = [c for c in CO if out["columnas"][c]["con"]["ecpm_ponderado"] and out["columnas"][c]["sin"]["ecpm_ponderado"]]
    cols.sort(key=lambda c: out["columnas"][c]["sin"]["ecpm_ponderado"] - out["columnas"][c]["con"]["ecpm_ponderado"])
    RH = 56
    W, top_m = 900, 116
    ph = RH * len(cols)
    H = top_m + ph + 50
    left, right = 120, 40
    pw = W - left - right
    xmax = max(v["ecpm_ponderado"] for c in cols for v in out["columnas"][c].values()) * 1.15

    def X(e):
        return left + pw * e / xmax
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">Registros sin contentTitle: eCPM ponderado con y sin dato en cada columna</text>',
         f'<text x="16" y="44" font-size="12" fill="{INK2}">{n_filas:,} filas sin título del consolidado tal como llega, antes del relleno ({req_tot:,} requests; {out["pct_vendido"]}% vendidos; eCPM ponderado ${mu:.2f}).</text>',
         f'<text x="16" y="60" font-size="12" fill="{INK2}">Por columna, esas filas se parten en dos grupos: las que traen dato útil y las que la traen vacía. Bajo cada eCPM, el % de las filas sin título en ese grupo.</text>',
         f'<text x="16" y="76" font-size="12" fill="{INK2}">Columnas ordenadas por la diferencia (con dato − sin dato), de mayor a menor. Línea punteada: eCPM ponderado de todas las filas sin título.</text>',
         f'<circle cx="24" cy="96" r="6" fill="{INK2}"/><text x="36" y="100" font-size="11" fill="{INK}">con dato en la columna</text>',
         f'<circle cx="190" cy="96" r="5" fill="#ffffff" stroke="{INK2}" stroke-width="2.5"/><text x="202" y="100" font-size="11" fill="{INK}">columna vacía</text>']
    v = 0
    while v < xmax:
        o.append(f'<line x1="{X(v):.1f}" y1="{top_m}" x2="{X(v):.1f}" y2="{top_m + ph}" stroke="{GRID}"/>')
        o.append(f'<text x="{X(v):.1f}" y="{top_m + ph + 16}" text-anchor="middle" font-size="10.5" fill="{INK2}">${v}</text>')
        v += 1
    o.append(f'<line x1="{X(mu):.1f}" y1="{top_m}" x2="{X(mu):.1f}" y2="{top_m + ph}" stroke="{INK2}" stroke-dasharray="5 4"/>')
    o.append(f'<text x="{left + pw / 2:.1f}" y="{H - 8}" text-anchor="middle" fill="{INK}">eCPM ponderado ($)</text>')
    for i, c in enumerate(cols):
        a_, b_ = out["columnas"][c]["con"], out["columnas"][c]["sin"]
        y = top_m + RH * i + RH / 2 - 4
        xa, xb = X(a_["ecpm_ponderado"]), X(b_["ecpm_ponderado"])
        col_ = C_COL[c]
        o.append(f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" font-size="12" font-weight="600" fill="{INK}">{ABR[c]}</text>')
        o.append(f'<line x1="{xa:.1f}" y1="{y:.1f}" x2="{xb:.1f}" y2="{y:.1f}" stroke="{col_}" stroke-width="3" stroke-opacity="0.55"/>')
        o.append(f'<circle cx="{xb:.1f}" cy="{y:.1f}" r="6" fill="#ffffff" stroke="{col_}" stroke-width="3"/>')
        o.append(f'<circle cx="{xa:.1f}" cy="{y:.1f}" r="7.5" fill="{col_}" stroke="#ffffff" stroke-width="2"/>')
        for x, d, fuera in ((xa, a_, xa >= xb), (xb, b_, xb > xa)):   # etiquetas hacia afuera del tramo, para que no se pisen
            anc, dx = ("start", 13) if fuera else ("end", -13)
            o.append(f'<text x="{x + dx:.1f}" y="{y + 1:.1f}" text-anchor="{anc}" font-size="11.5" font-weight="700" fill="{INK}">${d["ecpm_ponderado"]:.2f}</text>')
            o.append(f'<text x="{x + dx:.1f}" y="{y + 15:.1f}" text-anchor="{anc}" font-size="10" fill="{INK2}">{d["pct_filas"]:.1f}% de las filas</text>')
    o.append("</svg>")
    open(os.path.join(a.salida_dir, "graficos-sin-titulo-con-sin-dato.svg"), "w", encoding="utf-8").write("\n".join(o))

    # ---- 1b. dumbbell: requests totales con dato vs sin dato, por columna (mismo orden de columnas que la anterior)
    rmax = max(v["requests"] for c in cols for v in out["columnas"][c].values()) / 1e9 * 1.15

    def XR(q):
        return left + pw * q / 1e9 / rmax
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">Registros sin contentTitle: requests totales con y sin dato en cada columna</text>',
         f'<text x="16" y="44" font-size="12" fill="{INK2}">{n_filas:,} filas sin título del consolidado tal como llega, antes del relleno ({req_tot:,} requests; {out["pct_vendido"]}% vendidos).</text>',
         f'<text x="16" y="60" font-size="12" fill="{INK2}">Por columna, esas filas se parten en dos grupos: las que traen dato útil y las que la traen vacía. Bajo cada valor, el % de los requests sin título en ese grupo.</text>',
         f'<text x="16" y="76" font-size="12" fill="{INK2}">Requests totales (vendidos o no), en miles de millones. Mismo orden de columnas que la gráfica de eCPM; en cada columna los dos puntos suman el total.</text>',
         f'<circle cx="24" cy="96" r="6" fill="{INK2}"/><text x="36" y="100" font-size="11" fill="{INK}">con dato en la columna</text>',
         f'<circle cx="190" cy="96" r="5" fill="#ffffff" stroke="{INK2}" stroke-width="2.5"/><text x="202" y="100" font-size="11" fill="{INK}">columna vacía</text>']
    rstep = next(s for s in (5, 10, 20, 25, 50, 100, 200) if rmax / s <= 10)
    v = 0
    while v < rmax:
        o.append(f'<line x1="{XR(v * 1e9):.1f}" y1="{top_m}" x2="{XR(v * 1e9):.1f}" y2="{top_m + ph}" stroke="{GRID}"/>')
        o.append(f'<text x="{XR(v * 1e9):.1f}" y="{top_m + ph + 16}" text-anchor="middle" font-size="10.5" fill="{INK2}">{v:g}</text>')
        v += rstep
    o.append(f'<text x="{left + pw / 2:.1f}" y="{H - 8}" text-anchor="middle" fill="{INK}">requests totales (miles de millones)</text>')
    for i, c in enumerate(cols):
        a_, b_ = out["columnas"][c]["con"], out["columnas"][c]["sin"]
        y = top_m + RH * i + RH / 2 - 4
        xa, xb = XR(a_["requests"]), XR(b_["requests"])
        col_ = C_COL[c]
        o.append(f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" font-size="12" font-weight="600" fill="{INK}">{ABR[c]}</text>')
        o.append(f'<line x1="{xa:.1f}" y1="{y:.1f}" x2="{xb:.1f}" y2="{y:.1f}" stroke="{col_}" stroke-width="3" stroke-opacity="0.55"/>')
        o.append(f'<circle cx="{xb:.1f}" cy="{y:.1f}" r="6" fill="#ffffff" stroke="{col_}" stroke-width="3"/>')
        o.append(f'<circle cx="{xa:.1f}" cy="{y:.1f}" r="7.5" fill="{col_}" stroke="#ffffff" stroke-width="2"/>')
        for x, d, fuera in ((xa, a_, xa >= xb), (xb, b_, xb > xa)):
            # hacia afuera del tramo; si la etiqueta de la izquierda chocaria con el nombre de la columna, va a la derecha del punto
            anc, dx = ("start", 13) if fuera or x - 110 < left else ("end", -13)
            o.append(f'<text x="{x + dx:.1f}" y="{y + 1:.1f}" text-anchor="{anc}" font-size="11.5" font-weight="700" fill="{INK}" stroke="#ffffff" stroke-width="3" paint-order="stroke">{d["requests"] / 1e9:,.1f}</text>')
            o.append(f'<text x="{x + dx:.1f}" y="{y + 15:.1f}" text-anchor="{anc}" font-size="10" fill="{INK2}" stroke="#ffffff" stroke-width="3" paint-order="stroke">{100 * d["requests"] / req_tot:.1f}% de los requests</text>')
    o.append("</svg>")
    open(os.path.join(a.salida_dir, "graficos-sin-titulo-con-sin-dato-requests.svg"), "w", encoding="utf-8").write("\n".join(o))

    # ---- 2. barras + linea: top 20 generos por requests; barras = requests totales (eje izquierdo),
    #      linea = eCPM ponderado (eje derecho). Barras de mayor a menor requests.
    gs = out["genero"][:TOP_GENEROS]
    W2, H2 = 1040, 600
    left2, right2, top2, bottom2 = 60, 60, 110, 130
    pw2, ph2 = W2 - left2 - right2, H2 - top2 - bottom2
    emax = max(g["ecpm_ponderado"] or 0 for g in gs) * 1.15
    rmax = max(g["requests"] for g in gs) / 1e9 * 1.15
    yb = top2 + ph2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W2}" height="{H2}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">Registros sin contentTitle: requests totales y eCPM ponderado por género</text>',
         f'<text x="16" y="44" font-size="12" fill="{INK2}">Top {len(gs)} géneros (normalizados, tal como llegan, antes del relleno) por requests totales. Barras: requests totales (vendidos o no),</text>',
         f'<text x="16" y="60" font-size="12" fill="{INK2}">en miles de millones (eje izquierdo). Línea: eCPM ponderado del género (eje derecho). Línea punteada: ${mu:.2f}, el ponderado de todas las filas sin título.</text>',
         f'<rect x="16" y="72" width="12" height="12" rx="2" fill="{AZUL}"/><text x="32" y="82" font-size="11" fill="{INK}">requests totales (eje izquierdo)</text>',
         f'<line x1="210" y1="78" x2="232" y2="78" stroke="{INK}" stroke-width="2"/><circle cx="221" cy="78" r="3.5" fill="#ffffff" stroke="{INK}" stroke-width="2"/>'
         f'<text x="238" y="82" font-size="11" fill="{INK}">eCPM ponderado (eje derecho)</text>']
    rstep = next(s for s in (1, 2, 5, 10, 20, 25, 50, 100) if rmax / s <= 8)
    v = 0
    while v < rmax:
        y = yb - ph2 * v / rmax
        o.append(f'<line x1="{left2}" y1="{y:.1f}" x2="{left2 + pw2}" y2="{y:.1f}" stroke="{GRID}"/>')
        o.append(f'<text x="{left2 - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="10.5" fill="{INK2}">{v:g}</text>')
        v += rstep
    v = 0
    while v < emax:
        y = yb - ph2 * v / emax
        o.append(f'<line x1="{left2 + pw2}" y1="{y:.1f}" x2="{left2 + pw2 + 4}" y2="{y:.1f}" stroke="{INK2}"/>')
        o.append(f'<text x="{left2 + pw2 + 7}" y="{y + 4:.1f}" font-size="10.5" fill="{INK2}">${v:g}</text>')
        v += 1 if emax <= 10 else 2
    o.append(f'<line x1="{left2 + pw2}" y1="{top2}" x2="{left2 + pw2}" y2="{yb}" stroke="{INK2}"/>')
    o.append(f'<text transform="translate(18,{top2 + ph2 / 2:.1f}) rotate(-90)" text-anchor="middle" fill="{INK}">requests totales (miles de millones)</text>')
    o.append(f'<text transform="translate({W2 - 14},{top2 + ph2 / 2:.1f}) rotate(90)" text-anchor="middle" fill="{INK}">eCPM ponderado ($)</text>')
    ym = yb - ph2 * mu / emax
    o.append(f'<line x1="{left2}" y1="{ym:.1f}" x2="{left2 + pw2}" y2="{ym:.1f}" stroke="{INK2}" stroke-dasharray="5 4"/>')
    bw = pw2 / len(gs)
    pts, etiquetas = [], []
    for i, g in enumerate(gs):
        cx = left2 + bw * (i + 0.5)
        w = bw * 0.62
        h = ph2 * g["requests"] / 1e9 / rmax
        o.append(f'<rect x="{cx - w / 2:.1f}" y="{yb - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" fill="{AZUL}"/>')
        etiquetas.append(f'<text x="{cx:.1f}" y="{yb - h - 4:.1f}" text-anchor="middle" font-size="9.5" fill="{INK2}" '
                         f'stroke="#ffffff" stroke-width="3" paint-order="stroke">{g["requests"] / 1e9:.1f}</text>')
        if g["ecpm_ponderado"] is not None:
            pts.append((cx, yb - ph2 * g["ecpm_ponderado"] / emax, g["ecpm_ponderado"]))
        o.append(f'<text transform="translate({cx - 3:.1f},{yb + 12}) rotate(40)" font-size="10.5" fill="{INK}">{esc(g["genero"][:24])}</text>')
    o += etiquetas
    o.append(f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py, _ in pts)}" fill="none" stroke="{INK}" stroke-width="2"/>')
    for px, py, e in pts:
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#ffffff" stroke="{INK}" stroke-width="2"/>')
        o.append(f'<text x="{px:.1f}" y="{py - 8:.1f}" text-anchor="middle" font-size="10" font-weight="700" fill="{INK}" '
                 f'stroke="#ffffff" stroke-width="3" paint-order="stroke">{e:.2f}</text>')
    o.append("</svg>")
    open(os.path.join(a.salida_dir, "graficos-sin-titulo-genero-requests-ecpm.svg"), "w", encoding="utf-8").write("\n".join(o))
    print(f"-> {a.salida_dir}: {n_filas:,} filas sin titulo; eCPM {mu:.3f}; top {len(gs)} generos")


if __name__ == "__main__":
    main()
