# -*- coding: utf-8 -*-
"""Heatmap de densidad fila a fila: completitud de content objects (0-8 campos con dato
util) en x, eCPM en escala logaritmica en y, color = requests acumulados en cada celda.
Las filas con eCPM = 0 van en una banda aparte abajo ("no vendido"). Sobre cada columna
se marca el eCPM ponderado (>0) de ese nivel de completitud y arriba el % de requests del
grupo que cae en ese nivel y que % de ellos se vendio.

Un panel por grupo: total y los paises pedidos. SVG sin dependencias.

Uso:
    python generar_heatmap_completitud_ecpm.py consolidado.csv carpeta_salida [--paises "Mexico,Colombia,Chile"]
Escribe graficos-ecpm-completitud-heatmap.svg y graficos-ecpm-completitud-heatmap.json.
"""
import argparse, csv, json, math, os

SENT = {"not available", "not applicable", "unknown", "n/a", "null", "undefined", "none", "-", ""}
MD5 = "d41d8cd98f00b204e9800998ecf8427e"
CO = ["contentGenre", "contentCategory", "contentSeries", "contentLength", "contentLanguage",
      "contentIsLiveStream", "contentTitle", "contentRating"]
N = len(CO)
# bins logaritmicos de eCPM: 0.1 .. 200, 5 bins por decada (33 bins)
EDGES = [10 ** (-1 + i / 5) for i in range(0, 17)]  # 0.1 ... 158.5 (16 bins) + overflow
NB = len(EDGES)

def util(c, v):
    s = v.strip()
    if s.lower() in SENT: return False
    if c == "contentCategory" and s == "[-7]": return False
    if c == "contentSeries" and s.lower() == MD5: return False
    if c == "contentIsLiveStream" and s not in ("0", "1"): return False
    return True

def bin_ecpm(e):
    if e <= 0: return -1
    for i in range(NB - 1):
        if e < EDGES[i + 1]: return i
    return NB - 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada"); ap.add_argument("salida_dir")
    ap.add_argument("--paises", default="Mexico,Colombia,Chile")
    a = ap.parse_args()
    grupos = ["(todos)"] + [p.strip() for p in a.paises.split(",")]
    # celdas[g][score][bin] = requests ; bin -1 = eCPM 0
    celdas = {g: [[0] * (NB + 1) for _ in range(N + 1)] for g in grupos}
    filas = {g: [[0] * (NB + 1) for _ in range(N + 1)] for g in grupos}
    agg = {g: [[0, 0, 0.0, 0] for _ in range(N + 1)] for g in grupos}  # filas, req, sum e*req(>0), req_nz
    csv.field_size_limit(10 ** 9)
    with open(a.entrada, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            req = int(row["Total Requests"]); e = float(row["eCPM"])
            sc = sum(1 for c in CO if util(c, row[c])); b = bin_ecpm(e)
            for g in ["(todos)"] + ([row["Country"]] if row["Country"] in celdas else []):
                celdas[g][sc][b + 1] += req; filas[g][sc][b + 1] += 1
                t = agg[g][sc]; t[0] += 1; t[1] += req
                if e > 0 and req > 0: t[2] += e * req; t[3] += req
    out = {"fuente": a.entrada, "campos": CO, "bordes_ecpm": [round(x, 4) for x in EDGES], "grupos": {}}
    for g in grupos:
        tot_req = sum(t[1] for t in agg[g]); tot_filas = sum(t[0] for t in agg[g])
        niveles = []
        for sc in range(N + 1):
            t = agg[g][sc]
            niveles.append({"campos_llenos": sc, "filas": t[0], "pct_filas": round(100 * t[0] / tot_filas, 2) if tot_filas else 0,
                            "requests": t[1], "pct_requests": round(100 * t[1] / tot_req, 2) if tot_req else 0,
                            "pct_req_monetizado": round(100 * t[3] / t[1], 2) if t[1] else None,
                            "ecpm_ponderado": round(t[2] / t[3], 3) if t[3] else None})
        out["grupos"][g] = {"filas": tot_filas, "requests": tot_req, "niveles": niveles,
                            "celdas_requests": celdas[g], "celdas_filas": filas[g]}
    json.dump(out, open(os.path.join(a.salida_dir, "graficos-ecpm-completitud-heatmap.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(a.salida_dir, "graficos-ecpm-completitud-heatmap.svg"), "w", encoding="utf-8").write(svg(out, grupos))
    for g in grupos:
        print(g, [(n["campos_llenos"], n["pct_requests"], n["ecpm_ponderado"]) for n in out["grupos"][g]["niveles"]])
    print("->", a.salida_dir)

# ---------------- SVG ----------------
SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
RAMP = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
ACC = "#eb6834"
FONT = 'font-family="system-ui,-apple-system,Segoe UI,sans-serif"'
TIT = {"(todos)": "Total consolidado", "Mexico": "México", "Colombia": "Colombia", "Chile": "Chile"}
W, H = 560, 470
ML, MR, MT, MB = 64, 18, 96, 50
CELL_W = (W - ML - MR) / (N + 1)
BAND0 = 26  # alto de la banda eCPM = 0
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def color(v, vmax):
    if v <= 0: return SURF
    # escala log: 4 ordenes de magnitud por debajo del maximo del panel
    t = 1 + (math.log10(v) - math.log10(vmax)) / 4 if vmax > 1 else 0
    t = max(0.0, min(0.999, t))
    return RAMP[min(len(RAMP) - 1, int(t * len(RAMP)))]

def panel(x0, y0, g, d):
    ph = H - MT - MB; hh = ph - BAND0 - 6; cell_h = hh / NB
    top = y0 + MT; y_band = top + hh + 6
    def sy(e): return top + hh - (math.log10(e) - math.log10(EDGES[0])) / (math.log10(EDGES[-1]) - math.log10(EDGES[0])) * hh
    vmax = max(v for fila in d["celdas_requests"] for v in fila) or 1
    o = [f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{SURF}"/>',
         f'<text x="{x0+ML}" y="{y0+22}" font-size="15" font-weight="600" fill="{INK}">{esc(TIT.get(g, g))} — {d["filas"]:,} filas · {d["requests"]:,} requests</text>']
    o.append(f'<text x="{x0+ML}" y="{y0+40}" font-size="10.5" fill="{INK2}">arriba de cada columna: % de los requests del grupo en ese nivel · % de esos requests con eCPM &gt; 0</text>')
    for sc in range(N + 1):
        cx = x0 + ML + sc * CELL_W
        for b in range(NB):
            v = d["celdas_requests"][sc][b + 1]
            if v: o.append(f'<rect x="{cx:.1f}" y="{top + hh - (b + 1) * cell_h:.1f}" width="{CELL_W - 1:.1f}" height="{cell_h - 1:.1f}" fill="{color(v, vmax)}"/>')
        v0 = d["celdas_requests"][sc][0]
        o.append(f'<rect x="{cx:.1f}" y="{y_band:.1f}" width="{CELL_W - 1:.1f}" height="{BAND0}" fill="{color(v0, vmax)}"/>')
        n = d["niveles"][sc]
        o.append(f'<text x="{cx + CELL_W / 2:.1f}" y="{top + hh + BAND0 + 24:.1f}" font-size="11" text-anchor="middle" fill="{INK}">{sc}</text>')
        o.append(f'<text x="{cx + CELL_W / 2:.1f}" y="{y0 + MT - 30:.1f}" font-size="10" text-anchor="middle" fill="{INK}">{n["pct_requests"]:.1f}%</text>')
        if n["pct_req_monetizado"] is not None:
            o.append(f'<text x="{cx + CELL_W / 2:.1f}" y="{y0 + MT - 17:.1f}" font-size="10" text-anchor="middle" fill="{INK2}">{n["pct_req_monetizado"]:.0f}% vend.</text>')
        if n["ecpm_ponderado"]:
            e = min(max(n["ecpm_ponderado"], EDGES[0]), EDGES[-1])
            o.append(f'<circle cx="{cx + CELL_W / 2:.1f}" cy="{sy(e):.1f}" r="5" fill="{ACC}" stroke="{SURF}" stroke-width="2"/>')
            o.append(f'<text x="{cx + CELL_W / 2:.1f}" y="{sy(e) - 8:.1f}" font-size="9.5" text-anchor="middle" fill="{INK}">${n["ecpm_ponderado"]:.2f}</text>')
    for e in [0.1, 0.3, 1, 3, 10, 30, 100]:
        o.append(f'<line x1="{x0+ML-4}" y1="{sy(e):.1f}" x2="{x0+ML}" y2="{sy(e):.1f}" stroke="{AXIS}"/>')
        o.append(f'<text x="{x0+ML-7}" y="{sy(e)+4:.1f}" font-size="10.5" text-anchor="end" fill="{MUTED}">${e:g}</text>')
    o.append(f'<text x="{x0+ML-7}" y="{y_band + BAND0 / 2 + 4:.1f}" font-size="10.5" text-anchor="end" fill="{MUTED}">$0</text>')
    o.append(f'<line x1="{x0+ML}" y1="{top}" x2="{x0+ML}" y2="{y_band + BAND0}" stroke="{AXIS}"/>')
    o.append(f'<text x="{x0+ML+(W-ML-MR)/2:.1f}" y="{y0+H-10}" font-size="11.5" text-anchor="middle" fill="{INK2}">content objects con dato útil en la fila (de 8)</text>')
    o.append(f'<text transform="translate({x0+16},{top+hh/2:.1f}) rotate(-90)" font-size="11.5" text-anchor="middle" fill="{INK2}">eCPM de la fila (escala log)</text>')
    return "\n".join(o)

def svg(out, grupos):
    cols = 2; filas = math.ceil(len(grupos) / cols); top = 78
    w, h = cols * W + (cols - 1) * 16, filas * H + (filas - 1) * 16 + top
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {FONT}>', f'<rect width="{w}" height="{h}" fill="{SURF}"/>',
         f'<text x="0" y="22" font-size="17" font-weight="700" fill="{INK}">Completitud de la fila vs eCPM: densidad de requests</text>',
         f'<text x="0" y="41" font-size="12" fill="{INK2}">Cada celda acumula los requests de las filas con ese número de content objects llenos y ese eCPM (bins logarítmicos). Banda inferior: filas con eCPM = 0 (no vendidas).</text>',
         f'<text x="0" y="57" font-size="12" fill="{INK2}">Punto naranja: eCPM ponderado por requests de las filas vendidas de ese nivel. Color en escala logarítmica de requests; el máximo de cada panel es el azul más oscuro.</text>']
    for i, c in enumerate(RAMP):
        o.append(f'<rect x="{i*18}" y="63" width="18" height="9" fill="{c}"/>')
    o.append(f'<text x="{len(RAMP)*18+6}" y="71" font-size="10.5" fill="{INK2}">menos → más requests (escala log, 4 órdenes de magnitud bajo el máximo del panel)</text>')
    for i, g in enumerate(grupos):
        o.append(f'<g transform="translate({(i % cols) * (W + 16)},{top + (i // cols) * (H + 16)})">{panel(0, 0, g, out["grupos"][g])}</g>')
    o.append("</svg>")
    return "\n".join(o)

if __name__ == "__main__":
    main()
