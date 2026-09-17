# -*- coding: utf-8 -*-
"""Barras por app: eCPM ponderado (>0) segun cuantos content objects trae el registro (0-8).

Un panel por app (las --top-apps con mas requests vendidos). En cada panel, x = numero de
content objects con dato util, y = eCPM ponderado por requests de los registros de ese nivel
(solo filas con eCPM > 0 y requests > 0). Debajo de cada barra, el % de los requests vendidos
de la app que cae en ese nivel; los niveles con menos de --min-share % no se dibujan (una
barra hecha con pocas filas engana). La linea punteada es el eCPM ponderado de toda la app.

Uso:
    python scripts/generar_barras_app_completitud.py inventory-consolidado.csv reportes/NN/recursos \
        [--top-apps 12] [--min-share 2]
Escribe graficos-app-completitud-barras.svg y graficos-app-completitud-barras.json.
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida_dir")
    ap.add_argument("--top-apps", type=int, default=12)
    ap.add_argument("--min-share", type=float, default=2.0)
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


if __name__ == "__main__":
    main()
