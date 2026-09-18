# -*- coding: utf-8 -*-
"""Graficas sobre los registros SIN contentTitle (SVG sin dependencias), a partir del CSV de relleno.

  graficos-sin-titulo-columnas.svg  por content object: % de filas (sin titulo) con dato util (x) vs
                                    eCPM ponderado de esas filas (y), con dos marcas por columna:
                                    tal como llega (sin relleno) y tras el pipeline (con relleno),
                                    unidas por una linea del color de la columna
  graficos-sin-titulo-genero.svg    eCPM ponderado por genero (normalizado) en las filas sin titulo,
                                    barras ordenadas de mayor a menor, con el % del trafico vendido
  graficos-sin-titulo.json          los datos de las dos graficas

eCPM ponderado = sum(eCPM x requests) / sum(requests) de las filas con requests > 0 y eCPM > 0.

Uso:
    python scripts/generar_graficos_sin_titulo.py inventory-consolidado-relleno.csv reportes/NN/recursos
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
    n_filas = 0
    req_tot = req_vend = 0
    qe_tot = 0.0
    col = {c: {"orig": [0, 0, 0.0], "rell": [0, 0, 0.0]} for c in CO}   # filas llenas, req vendidos, sum q*e
    gen = defaultdict(lambda: [0, 0, 0.0])                                # filas, req vendidos, sum q*e
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
                for k, v in (("orig", r[c]), ("rell", r.get(c + "_relleno", ""))):
                    if util(c, v):
                        t = col[c][k]
                        t[0] += 1
                        if vend:
                            t[1] += q
                            t[2] += q * e
            g = (r.get("genero_normalizado") or "").split(";")[0].strip() or "(sin género)"
            t = gen[g]
            t[0] += 1
            if vend:
                t[1] += q
                t[2] += q * e
    mu = qe_tot / req_vend
    out = {"fuente": a.entrada, "filas_sin_titulo": n_filas, "requests": req_tot, "requests_vendidos": req_vend,
           "pct_vendido": round(100 * req_vend / req_tot, 1), "ecpm_ponderado": round(mu, 3), "columnas": {}, "genero": []}
    for c in CO:
        out["columnas"][c] = {k: {"pct_filas_llenas": round(100 * t[0] / n_filas, 1),
                                  "requests_vendidos": t[1], "ecpm_ponderado": round(t[2] / t[1], 3) if t[1] else None}
                              for k, t in col[c].items()}
    for g, t in sorted(gen.items(), key=lambda kv: -kv[1][1]):
        if t[1] > 0:
            out["genero"].append({"genero": g, "filas": t[0], "requests_vendidos": t[1], "share_trafico_vendido_pct": round(100 * t[1] / req_vend, 1),
                                  "ecpm_ponderado": round(t[2] / t[1], 3)})
    json.dump(out, open(os.path.join(a.salida_dir, "graficos-sin-titulo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---- 1. scatter % llenas vs eCPM, sin y con relleno
    W, H = 900, 580
    left, right, top_m, bottom = 64, 30, 120, 62
    pw, ph = W - left - right, H - top_m - bottom
    ys = [v["ecpm_ponderado"] for c in CO for v in out["columnas"][c].values() if v["ecpm_ponderado"]]
    ymax = max(ys) * 1.18

    def X(p):
        return left + pw * p / 100

    def Y(e):
        return top_m + ph * (1 - e / ymax)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">Registros sin contentTitle: % de filas llenas vs eCPM, sin y con relleno</text>',
         f'<text x="16" y="44" font-size="12" fill="{INK2}">{n_filas:,} filas sin título ({req_tot:,} requests; {out["pct_vendido"]}% vendidos; eCPM ponderado ${mu:.2f}).</text>',
         f'<text x="16" y="60" font-size="12" fill="{INK2}">Por columna: x = % de esas filas con dato útil, y = eCPM ponderado de esas filas. Círculo = tal como llega; rombo = tras el relleno; '
         f'la línea une los dos estados.</text>',
         f'<text x="16" y="76" font-size="12" fill="{INK2}">Si el círculo y el rombo coinciden, el relleno no cambió esa columna en las filas sin título. Línea punteada: eCPM ponderado de todas las filas sin título.</text>',
         f'<circle cx="24" cy="96" r="5" fill="{INK2}"/><text x="34" y="100" font-size="11" fill="{INK}">sin relleno</text>',
         f'<polygon points="118,90 124,96 118,102 112,96" fill="{INK2}"/><text x="130" y="100" font-size="11" fill="{INK}">con relleno</text>']
    lx = 230
    for c in CO:
        o.append(f'<rect x="{lx}" y="90" width="12" height="12" rx="2" fill="{C_COL[c]}"/>')
        o.append(f'<text x="{lx + 16}" y="100" font-size="11" fill="{INK}">{ABR[c]}</text>')
        lx += 16 + 6.5 * len(ABR[c]) + 16
    for p in range(0, 101, 20):
        o.append(f'<line x1="{X(p):.1f}" y1="{top_m}" x2="{X(p):.1f}" y2="{top_m + ph}" stroke="{GRID}"/>')
        o.append(f'<text x="{X(p):.1f}" y="{top_m + ph + 16}" text-anchor="middle" font-size="10.5" fill="{INK2}">{p}%</text>')
        o.append(f'<text x="{X(p):.1f}" y="{top_m + ph + 29}" text-anchor="middle" font-size="9.5" fill="{INK2}">{round(n_filas * p / 100):,}</text>')
    step = 1 if ymax <= 8 else 2
    v = 0
    while v < ymax:
        o.append(f'<line x1="{left}" y1="{Y(v):.1f}" x2="{left + pw}" y2="{Y(v):.1f}" stroke="{GRID}"/>')
        o.append(f'<text x="{left - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="10.5" fill="{INK2}">${v}</text>')
        v += step
    o.append(f'<line x1="{left}" y1="{Y(mu):.1f}" x2="{left + pw}" y2="{Y(mu):.1f}" stroke="{INK2}" stroke-dasharray="5 4"/>')
    o.append(f'<text x="{left + pw / 2:.1f}" y="{H - 8}" text-anchor="middle" fill="{INK}">% de filas llenas de la columna (debajo: cuántas filas sin título son ese %)</text>')
    o.append(f'<text transform="translate(18,{top_m + ph / 2:.1f}) rotate(-90)" text-anchor="middle" fill="{INK}">eCPM ponderado de las filas llenas ($)</text>')
    for c in CO:
        a_, b_ = out["columnas"][c]["orig"], out["columnas"][c]["rell"]
        if not a_["ecpm_ponderado"] or not b_["ecpm_ponderado"]:
            continue
        xa, ya = X(a_["pct_filas_llenas"]), Y(a_["ecpm_ponderado"])
        xb, yb = X(b_["pct_filas_llenas"]), Y(b_["ecpm_ponderado"])
        col_ = C_COL[c]
        if abs(xa - xb) > 1 or abs(ya - yb) > 1:
            o.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="{col_}" stroke-width="2" stroke-opacity="0.7"/>')
        o.append(f'<circle cx="{xa:.1f}" cy="{ya:.1f}" r="6" fill="{col_}" stroke="#ffffff" stroke-width="2"/>')
        o.append(f'<polygon points="{xb:.1f},{yb - 8:.1f} {xb + 8:.1f},{yb:.1f} {xb:.1f},{yb + 8:.1f} {xb - 8:.1f},{yb:.1f}" fill="{col_}" stroke="#ffffff" stroke-width="2"/>')
        if abs(xa - xb) > 10 or abs(ya - yb) > 10:
            o.append(f'<text x="{xa:.1f}" y="{ya - 11:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{INK}">${a_["ecpm_ponderado"]:.2f}</text>')
            o.append(f'<text x="{xb:.1f}" y="{yb - 12:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{INK}">${b_["ecpm_ponderado"]:.2f}</text>')
        else:   # los dos estados casi coinciden: una sola etiqueta "sin / con"
            lab = f'${a_["ecpm_ponderado"]:.2f}' if abs(a_["ecpm_ponderado"] - b_["ecpm_ponderado"]) < 0.005 else f'${a_["ecpm_ponderado"]:.2f} → ${b_["ecpm_ponderado"]:.2f}'
            o.append(f'<text x="{xb:.1f}" y="{yb - 12:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{INK}">{lab}</text>')
    o.append("</svg>")
    open(os.path.join(a.salida_dir, "graficos-sin-titulo-columnas.svg"), "w", encoding="utf-8").write("\n".join(o))

    # ---- 2. barras: eCPM ponderado por genero (filas sin titulo)
    gs = [g for g in out["genero"] if g["share_trafico_vendido_pct"] >= 0.5][:14]
    gs.sort(key=lambda g: -g["ecpm_ponderado"])
    W2, H2 = 900, 76 + 26 * len(gs) + 50
    left2, right2, top2 = 150, 250, 76
    pw2 = W2 - left2 - right2
    emax = max(g["ecpm_ponderado"] for g in gs) * 1.05
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}" '
         f'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W2}" height="{H2}" fill="#ffffff"/>',
         f'<text x="16" y="24" font-size="17" font-weight="700" fill="{INK}">Registros sin contentTitle: eCPM ponderado por género</text>',
         f'<text x="16" y="44" font-size="12" fill="{INK2}">Género normalizado tal como llega (sin relleno). A la derecha, el % del tráfico vendido sin título que cae en ese género y sus filas.</text>',
         f'<text x="16" y="60" font-size="12" fill="{INK2}">Géneros con menos del 0.5% del tráfico vendido no se muestran. Línea punteada: ${mu:.2f}, el ponderado de todas las filas sin título.</text>']
    for v in range(0, int(emax) + 1, 1):
        x = left2 + pw2 * v / emax
        o.append(f'<line x1="{x:.1f}" y1="{top2}" x2="{x:.1f}" y2="{top2 + 26 * len(gs)}" stroke="{GRID}"/>')
        o.append(f'<text x="{x:.1f}" y="{top2 + 26 * len(gs) + 16}" text-anchor="middle" font-size="10.5" fill="{INK2}">${v}</text>')
    xm = left2 + pw2 * mu / emax
    o.append(f'<line x1="{xm:.1f}" y1="{top2}" x2="{xm:.1f}" y2="{top2 + 26 * len(gs)}" stroke="{INK2}" stroke-dasharray="5 4"/>')
    for i, g in enumerate(gs):
        y = top2 + 26 * i
        w = pw2 * g["ecpm_ponderado"] / emax
        o.append(f'<text x="{left2 - 8}" y="{y + 17}" text-anchor="end" font-size="11.5" fill="{INK}">{esc(g["genero"])}</text>')
        o.append(f'<rect x="{left2}" y="{y + 4}" width="{w:.1f}" height="18" rx="3" fill="{AZUL}"/>')
        o.append(f'<text x="{left2 + w + 6:.1f}" y="{y + 17}" font-size="11" font-weight="600" fill="{INK}">${g["ecpm_ponderado"]:.2f}</text>')
        o.append(f'<text x="{W2 - 16}" y="{y + 17}" text-anchor="end" font-size="10.5" fill="{INK2}">{g["share_trafico_vendido_pct"]:.1f}% del tráfico vendido · {g["filas"]:,} filas</text>')
    o.append("</svg>")
    open(os.path.join(a.salida_dir, "graficos-sin-titulo-genero.svg"), "w", encoding="utf-8").write("\n".join(o))
    print(f"-> {a.salida_dir}: {n_filas:,} filas sin titulo; eCPM {mu:.3f}; {len(gs)} generos")


if __name__ == "__main__":
    main()
