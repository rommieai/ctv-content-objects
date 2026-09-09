# -*- coding: utf-8 -*-
"""Genera el reporte markdown "content objects cuando X esta vacio".

Toma el JSON de analizar.py corrido con --solo-vacios-en X (subconjunto de filas donde
X no trae dato util) y el JSON del analisis completo (referencia), y arma un reporte con
la misma estructura del detallado por pais: comparativo de % de filas no vacias de las
DEMAS columnas (subconjunto vs dataset completo), visual, y secciones por pais con
Publisher / App Name / content objects. Las conclusiones narradas se agregan aparte
(--notas archivo.md: se inserta al final tal cual).

Uso:
    python generar_reporte_vacios.py vacios-X.json referencia.json salida.md \
        [--visual visual.svg] [--notas notas.md] [--fuente consolidado.csv]
"""
import argparse
import json

APP = ["Publisher", "App Name"]
CO = ["contentIsTitlePresent", "contentGenre", "contentTitle", "contentRating",
      "contentLanguage", "contentIsLiveStream", "contentCategory", "contentLength",
      "contentSeries"]
ETIQ = {"Mexico": "México", "Colombia": "Colombia", "Chile": "Chile"}
ABREVIAR = {"Not Available": "N/A", "Not Applicable": "N/A",
            "d41d8cd98f00b204e9800998ecf8427e": "md5-vacío",
            "MovieArk: Stream Movies & Live": "MovieArk",
            "Browser TV Web - BrowseHere": "BrowseHere",
            "Televisa Univision via SpringServe": "Televisa (SS)",
            "Televisa Univision via OB": "Televisa (OB)",
            "TCL ADS - Springserve": "TCL Springserve", "TCL ADs (APAC)": "TCL APAC",
            "Select Plus PTE LTD (CTV)": "Select Plus",
            "METAX SOFTWARE PTE. LTD. (Exchange)": "METAX",
            "Equativ (Formerly SMART AdServer) - oRTB CTV": "Equativ",
            "iion Pty Ltd": "iion", "OTTera.tv": "OTTera",
            "Coocaa, a SKYWORTH company": "Coocaa", "TV Azteca - Springserve": "TV Azteca",
            "OTT Studios Entertainment On Demand": "OTT Studios Ent.",
            "ViX: TV, Sports and News": "ViX (Sports and News)",
            "ViX: TV, Deportes y Noticias": "ViX (Deportes y Noticias)"}
VACIOS = {"N/A", "md5-vacío", "Unknown", "[-7]", "{{CONTENT_SERIES}}", "{{content_title}}"}


def ab(v):
    v = ABREVIAR.get(v, v)
    return v if len(v) <= 28 else v[:27] + "…"


def top3(items):
    out = []
    for v, n, p in items[:3]:
        s = f"{ab(v)} {p:.1f}%"
        out.append(f"*{s}*" if ab(v) in VACIOS else s)
    return ", ".join(out)


def pct1(x):
    return f"{x:.1f}%" if x < 99.95 else "100%"


def fmt_int(n):
    return f"{n:,}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sub_json")
    ap.add_argument("ref_json")
    ap.add_argument("salida_md")
    ap.add_argument("--visual", default="")
    ap.add_argument("--notas", default="")
    ap.add_argument("--fuente", default="inventory-consolidado-v10-a-v17.csv")
    ap.add_argument("--titulo-tanda", default="consolidado v10 a v17")
    args = ap.parse_args()

    S = json.load(open(args.sub_json, encoding="utf-8"))
    R = json.load(open(args.ref_json, encoding="utf-8"))
    col = S["filtro"]["solo_vacios_en"]
    f = S["filtro"]
    paises = list(S["grupos"].keys())
    otras_app = [c for c in APP]
    otras_co = [c for c in CO if c != col]

    L = []
    L.append(f"# Reporte — Content objects cuando **{col}** viene vacío: México, Colombia y Chile ({args.titulo_tanda})\n")
    L.append(f"**Fuente:** `{args.fuente}` — {fmt_int(f['filas_dataset'])} filas, {fmt_int(f['requests_dataset'])} requests. "
             f"**Subconjunto analizado: las {fmt_int(S['filas'])} filas ({f['pct_filas_dataset']}% del total) donde `{col}` no trae dato útil**, "
             f"que concentran {fmt_int(S['total_requests'])} requests ({f['pct_requests_dataset']}% del total).")
    L.append(f"**Data completa:** `{args.sub_json.split('/')[-1]}` (top-15 de valores por columna para cada país). "
             f"Generado con `scripts/analizar.py --solo-vacios-en {col}`; las columnas de referencia (\"todo el dataset\") salen de `{args.ref_json.split('/')[-1]}`.\n")
    L.append(f"*Una fila cuenta como vacía en `{col}` tanto si la celda no trae valor como si trae `Not Available`, `Not Applicable`, `Unknown` "
             f"o basura equivalente a vacío (`[-7]` en categoría, hash MD5 de cadena vacía en serie). Los porcentajes de este reporte son "
             f"**sobre las filas del subconjunto** (las que tienen `{col}` vacío), salvo donde se indique \"todo el dataset\".*\n")

    # tamaño del subconjunto por pais
    L.append("## Tamaño del subconjunto por país\n")
    L.append("| País | Filas con la columna vacía | % de las filas del país | % de los requests del país | eCPM pond. del subconjunto (todo el país) |")
    L.append("|---|---:|---:|---:|---:|")
    for p in paises:
        g = S["grupos"][p]; rg = R["grupos"][p]
        L.append(f"| {ETIQ.get(p, p)} | {fmt_int(g['filas'])} | {100 * g['filas'] / rg['filas']:.1f}% | "
                 f"{100 * g['requests'] / rg['requests']:.1f}% | {g['ecpm']['ponderado_requests']} ({rg['ecpm']['ponderado_requests']}) |")
    L.append("")

    # comparativo
    L.append("## Comparativo de % de filas no vacías de las demás columnas\n")
    L.append(f"Porcentaje de filas del subconjunto con dato útil en cada una de las otras columnas. Entre paréntesis, el mismo porcentaje en **todo el dataset** del país: la diferencia dice si el vacío de `{col}` viene acompañado de otros vacíos o no.\n")
    L.append("**Campos de app / vendedor:**\n")
    L.append("| Columna | " + " | ".join(ETIQ.get(p, p) for p in paises) + " |")
    L.append("|---|" + "---:|" * len(paises))
    for c in otras_app:
        L.append(f"| {c} | " + " | ".join(
            f"{pct1(S['grupos'][p]['columnas'][c]['fill_rate_pct'])} ({pct1(R['grupos'][p]['columnas'][c]['fill_rate_pct'])})"
            for p in paises) + " |")
    L.append("\n**Content objects:**\n")
    L.append("| Columna | " + " | ".join(ETIQ.get(p, p) for p in paises) + " |")
    L.append("|---|" + "---:|" * len(paises))
    for c in otras_co:
        cells = []
        for p in paises:
            a = S['grupos'][p]['columnas'][c]['fill_rate_pct']; b = R['grupos'][p]['columnas'][c]['fill_rate_pct']
            s = f"{pct1(a)} ({pct1(b)})"
            if b - a >= 10: s = f"**{s}**"
            cells.append(s)
        L.append(f"| {c} | " + " | ".join(cells) + " |")
    L.append("\n*En negrilla, las columnas que pierden 10 puntos o más de completitud dentro del subconjunto respecto a todo el dataset.*\n")

    if args.visual:
        L.append("Versión visual con los tres países lado a lado (semáforo por % de filas no vacías dentro del subconjunto):\n")
        L.append(f"![Tablas de los tres países lado a lado]({args.visual.split('/')[-1]})\n")
        L.append("*(Generada con `scripts/generar_visual_paises.py` a partir del JSON de este reporte.)*\n")

    # por pais
    for p in paises:
        g = S["grupos"][p]; rg = R["grupos"][p]
        L.append(f"## {ETIQ.get(p, p)} — {fmt_int(g['filas'])} filas con `{col}` vacío ({100 * g['filas'] / rg['filas']:.1f}% del país) · "
                 f"{100 * g['requests'] / rg['requests']:.1f}% de los requests del país\n")
        L.append(f"eCPM del subconjunto: {g['ecpm']['pct_filas_cero']}% de filas en cero (todo el país: {rg['ecpm']['pct_filas_cero']}%) · "
                 f"media no-cero {g['ecpm']['media_no_cero']} · **ponderado {g['ecpm']['ponderado_requests']}** (todo el país: {rg['ecpm']['ponderado_requests']})\n")
        L.append("**Campos de app / vendedor:**\n")
        L.append("| Columna | % de filas no vacías | Top 3 referencias (% filas del subconjunto) |")
        L.append("|---|---:|---|")
        for c in otras_app:
            x = g["columnas"][c]
            L.append(f"| {c} | {pct1(x['fill_rate_pct'])} | {top3(x['top'])} |")
        L.append("\n**Content objects:**\n")
        L.append("| Columna | % de filas no vacías | Top 3 referencias (% filas del subconjunto) |")
        L.append("|---|---:|---|")
        for c in otras_co:
            x = g["columnas"][c]
            L.append(f"| {c} | {pct1(x['fill_rate_pct'])} | {top3(x['top'])} |")
        L.append("")

    if args.notas:
        L.append("---\n")
        L.append(open(args.notas, encoding="utf-8").read().rstrip() + "\n")

    with open(args.salida_md, "w", encoding="utf-8") as out:
        out.write("\n".join(L))
    print(f"-> {args.salida_md}")


if __name__ == "__main__":
    main()
