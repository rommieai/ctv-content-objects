# -*- coding: utf-8 -*-
"""Markdown del detallado por pais (solo tablas) a partir de los JSON de la tanda.

Lee, en <carpeta>/recursos/:
    reporte-content-objects-detallado-v<N>-consolidado.json   (scripts/analizar.py --grupos MX,CO,CL)
    reporte-requests-ecpm-por-vacio-v<N>.json                 (scripts/requests_ecpm_por_vacio.py)
y escribe <carpeta>/reporte-content-objects-detallado-v<N>-consolidado.md: total consolidado + un bloque
por pais con, por columna, % de filas llenas, top 3 referencias y requests / eCPM ponderado de
las filas llenas vs vacias.

Uso:
    python scripts/generar_reporte_detallado.py reportes/NN 19 "31 ago-14 sep 2026" \
        --corte 60333-...-v19-....csv --prev-filas 1071840
"""
import argparse
import csv
import json
import os

PAISES = ["Mexico", "Colombia", "Chile"]
NOMBRE = {"Mexico": "México", "Colombia": "Colombia", "Chile": "Chile"}
APP = ["Publisher", "App Name"]
CO = ["contentIsTitlePresent", "contentGenre", "contentTitle", "contentRating", "contentLanguage",
      "contentIsLiveStream", "contentCategory", "contentLength", "contentSeries"]
SENT = {"Not Available": "N/A", "Not Applicable": "N/A", "Unknown": "Unknown", "[-7]": "[-7]",
        "d41d8cd98f00b204e9800998ecf8427e": "md5-vacío"}
ABR = {"MovieArk: Stream Movies & Live": "MovieArk", "Televisa Univision via SpringServe": "Televisa (SS)",
       "TCL ADS - Springserve": "TCL Springserve", "TCL ADs (APAC)": "TCL APAC",
       "Select Plus PTE LTD (CTV)": "Select Plus", "iion Pty Ltd": "iion", "OTTera.tv": "OTTera",
       "Equativ (Formerly SMART AdServer) - oRTB CTV": "Equativ", "Coocaa, a SKYWORTH company": "Coocaa",
       "OTT Studios Entertainment On Demand": "OTT Studios Ent.", "Browser TV Web - BrowseHere": "BrowseHere"}


def pct(x, d=1):
    return f"{x:.{d}f}%"


def n(x):
    return f"{x:,}"


def f100(x):
    return "100%" if x >= 99.95 else pct(x)


def dol(d):
    return f"${d['ecpm_ponderado']:.2f}" if d["ecpm_ponderado"] is not None else "—"


def top3(col):
    out = []
    for row in (col.get("top") or col.get("distribucion"))[:3]:
        v, p = row[0], row[2]
        lab = SENT.get(v)
        out.append(f"*{lab} {pct(p)}*" if lab else f"{ABR.get(v, v)} {pct(p)}")
    return ", ".join(out)


def corte_stats(path):
    filas = req = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) != 16:
                continue
            filas += 1
            req += int(row[14])
    return filas, req


def tablas(cols, vp, tot_req, pond, etiqueta, fillkey):
    hdr = (f"| Columna | % de filas llenas | Top 3 referencias (% filas {etiqueta}) | Requests llenas | "
           f"eCPM pond. llenas | Requests vacías | eCPM pond. vacías |\n|---|---:|---|---:|---:|---:|---:|")

    def fila(c):
        s = f100(cols[c][fillkey])
        if c in vp:
            a, b = vp[c]["lleno"], vp[c]["vacio"]
            return f"| {c} | {s} | {top3(cols[c])} | {n(a['requests'])} | {dol(a)} | {n(b['requests'])} | {dol(b)} |"
        return f"| {c} | {s} | {top3(cols[c])} | {n(tot_req)} | ${pond:.2f} | 0 | — |"

    out = ["**Campos de app / vendedor:**\n\n" + hdr] + [fila(c) for c in APP]
    out += ["\n**Content objects:**\n\n" + hdr] + [fila(c) for c in CO] + [""]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpeta")
    ap.add_argument("version", type=int)
    ap.add_argument("ventana", help='ej. "31 ago-14 sep 2026"')
    ap.add_argument("--corte", required=True, help="CSV crudo del corte vigente (para filas/requests solo del corte)")
    ap.add_argument("--prev-filas", type=int, required=True, help="filas del consolidado anterior (para las combinaciones nuevas)")
    a = ap.parse_args()
    V, D = a.version, a.carpeta
    R = os.path.join(D, "recursos")
    det = json.load(open(os.path.join(R, f"reporte-content-objects-detallado-v{V}-consolidado.json"), encoding="utf-8"))
    vac = json.load(open(os.path.join(R, f"reporte-requests-ecpm-por-vacio-v{V}.json"), encoding="utf-8"))
    filas, req = det["filas"], det["total_requests"]
    c_filas, c_req = corte_stats(a.corte)

    L = [f"# Content Objects por país: México, Colombia y Chile (consolidado v10 a v{V})\n",
         f"**Fuente:** `inventory-consolidado-v10-a-v{V}.csv` — {n(filas)} filas únicas, {n(req)} requests "
         f"(métricas del corte v{V}, ventana {a.ventana}; v{V} aportó {n(filas - a.prev_filas)} combinaciones nuevas). "
         f"Solo v{V}: {n(c_filas)} filas, {n(c_req)} requests.",
         f"**Data completa:** `recursos/reporte-content-objects-detallado-v{V}-consolidado.json` (top-15 de valores por columna "
         f"para cada país). Generado con `scripts/analizar.py`; tablas con `scripts/generar_reporte_detallado.py`.\n",
         '*Nota: "llenas" excluye centinelas — una fila cuenta como vacía tanto si la celda no trae valor como si trae '
         '`Not Available`, `Not Applicable`, `Unknown` o basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, '
         'macros sin reemplazar).*\n',
         '*Nota sobre las columnas de requests y eCPM: "Requests llenas" / "Requests vacías" es el total de requests de '
         'las filas del grupo donde esa columna trae dato útil / viene vacía. "eCPM pond." = Σ(eCPM × requests) / Σ requests '
         'de esas filas, sin contar las que tienen requests = 0 o eCPM = 0. Calculado con `scripts/requests_ecpm_por_vacio.py` '
         f'→ `recursos/reporte-requests-ecpm-por-vacio-v{V}.json`.*\n',
         "*Nota sobre `md5-vacío`: en `contentSeries` algunos vendedores mandan un hash MD5 en vez del nombre de la serie. "
         "El valor `d41d8cd98f00b204e9800998ecf8427e` es el MD5 de la cadena vacía, es decir, el vendedor hasheó un texto "
         "en blanco; se cuenta como vacío.*\n"]
    ge = det["columnas"]["eCPM"]
    L.append(f"## Total consolidado (todos los países) — {n(filas)} filas · {n(req)} requests\n")
    L.append(f"eCPM: {pct(ge['pct_filas_cero'])} de filas en cero · media no-cero ${ge['media_no_cero']:.2f} · "
             f"ponderado ${ge['ecpm_ponderado_por_requests']:.2f}\n")
    L += tablas(det["columnas"], vac["paises"]["(todos)"]["columnas"], req, ge["ecpm_ponderado_por_requests"],
                "del total", "fill_rate_filas_pct")
    for p in PAISES:
        g = det["grupos"][p]
        e = g["ecpm"]
        L.append(f"## {NOMBRE[p]} — {n(g['filas'])} filas ({pct(g['pct_filas'])}) · {pct(g['pct_requests'])} de los requests\n")
        L.append(f"eCPM: {pct(e['pct_filas_cero'])} de filas en cero · media no-cero ${e['media_no_cero']:.2f} · "
                 f"ponderado ${e['ponderado_requests']:.2f}\n")
        L += tablas(g["columnas"], vac["paises"][p]["columnas"], g["requests"], e["ponderado_requests"], "del país", "fill_rate_pct")
    out = os.path.join(D, f"reporte-content-objects-detallado-v{V}-consolidado.md")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L).rstrip("\n") + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
