# -*- coding: utf-8 -*-
"""Markdown del reporte de graficas (solo tablas) a partir de los JSON de la tanda.

Lee, en <carpeta>/recursos/:
    graficos-ecpm-vacio-r2.json              (scripts/generar_graficos_ecpm_vacio.py)
    graficos-ecpm-completitud-scatter.json   (scripts/generar_scatter_completitud_ecpm.py)
y escribe <carpeta>/reporte-graficos-ecpm-vacio.md (los SVG se enlazan desde recursos/) con dos secciones: reparto del gasto
entre filas llenas y vacias, y scatter fila a fila de campos llenos vs eCPM (log). (Los scatter de eCPM llenas vs vacias
y de % llenas vs eCPM se quitaron el 2026-09-17: no mostraban relacion; el script de graficas los
sigue produciendo en recursos/ pero no se enlazan.)

Uso:
    python scripts/generar_reporte_graficos.py reportes/NN 19
"""
import argparse
import json
import os

GRUPOS = [("(todos)", "Total consolidado"), ("Mexico", "México"), ("Colombia", "Colombia"), ("Chile", "Chile")]
COLS = ["App Name", "contentGenre", "contentTitle", "contentRating", "contentLanguage",
        "contentIsLiveStream", "contentCategory", "contentLength", "contentSeries"]


def pct(x):
    return f"{x:.1f}%"


def n(x):
    return f"{x:,}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpeta")
    ap.add_argument("version", type=int)
    a = ap.parse_args()
    V, D = a.version, a.carpeta
    R = os.path.join(D, "recursos")
    r2 = json.load(open(os.path.join(R, "graficos-ecpm-vacio-r2.json"), encoding="utf-8"))["grupos"]
    hm = json.load(open(os.path.join(R, "graficos-ecpm-completitud-scatter.json"), encoding="utf-8"))

    L = [f"# Gráficos: eCPM de las filas llenas vs vacías (consolidado v10 a v{V})\n",
         f"**Fuente:** `recursos/reporte-requests-ecpm-por-vacio-v{V}.json` (mismos datos de las tablas por país del detallado). "
         "Generado con `scripts/generar_graficos_ecpm_vacio.py` → `recursos/graficos-ecpm-vacio-r2.json`; tablas con "
         "`scripts/generar_reporte_graficos.py`.\n",
         "*eCPM ponderado = Σ(eCPM × requests) / Σ requests, sin las filas con requests = 0 o eCPM = 0. Columnas: App Name y "
         "los 8 content objects con filas vacías; contentIsTitlePresent y Publisher vienen al 100% y no entran.*\n"]
    L += ["## 1. Reparto del gasto (eCPM × requests / 1000) entre filas llenas y vacías\n",
          "![reparto del gasto](recursos/graficos-ecpm-vacio-pies.svg)\n",
          "*% del gasto del grupo que cae en filas donde la columna trae dato útil. El gasto se calcula solo sobre filas con eCPM > 0.*\n",
          "| Columna | " + " | ".join(lab for _, lab in GRUPOS) + " |\n|---|" + "---:|" * len(GRUPOS)]
    for c in COLS:
        L.append(f"| {c} | " + " | ".join(pct(r2[k]["gasto"][c]["pct_gasto_llenas"]) for k, _ in GRUPOS) + " |")
    sc = hm["muestra_por_nivel"]
    L += ["\n## 2. % de columnas llenas de la fila vs eCPM (fila a fila)\n",
          "Cada registro del consolidado se clasifica por el % de los 8 content objects que trae con dato útil (contentGenre, "
          "contentCategory, contentSeries, contentLength, contentLanguage, contentIsLiveStream, contentTitle, contentRating; "
          "contentIsTitlePresent no cuenta porque siempre viene). Cada punto es un registro con eCPM > 0, con el eCPM en escala "
          f"logarítmica y el tamaño según sus requests (por nivel y panel se dibujan los {sc['top_requests']} registros de más requests "
          f"y {sc['azar']} al azar). El punto naranja es el eCPM ponderado por requests de todos los registros del nivel. Generado con "
          "`scripts/generar_scatter_completitud_ecpm.py` → `recursos/graficos-ecpm-completitud-scatter.json`.\n",
          "![completitud vs eCPM, registro a registro](recursos/graficos-ecpm-completitud-scatter.svg)\n"]
    for k, lab in GRUPOS:
        g = hm["grupos"][k]
        L.append(f"**{lab}** — {n(g['filas'])} filas · {n(g['requests'])} requests\n")
        L.append("| % de columnas llenas (de 8) | % filas | % requests | % requests vendidos (eCPM > 0) | eCPM pond. (>0) |\n|---:|---:|---:|---:|---:|")
        for x in g["niveles"]:
            L.append(f"| {100 * x['campos_llenos'] / 8:g}% ({x['campos_llenos']}) | {pct(x['pct_filas'])} | {pct(x['pct_requests'])} | {pct(x['pct_req_monetizado'])} | ${x['ecpm_ponderado']:.2f} |")
        L.append("")
    # ---- 3. drivers del eCPM: la ruta de venta (scripts/generar_graficos_drivers_ecpm.py) ----
    pdrv = os.path.join(R, "graficos-drivers-ecpm.json")
    if os.path.exists(pdrv):
        drv = json.load(open(pdrv, encoding="utf-8"))
        tot = drv["total"]
        L += ["## 3. Qué mueve el eCPM ponderado: la ruta de venta (publisher y país)\n",
              "Sobre las filas con eCPM > 0 y requests > 0, la combinación publisher × país explica cerca de dos tercios de la "
              "variación del eCPM ponderado; los content objects, controlando por la ruta, aportan pocos puntos (género y rating "
              "los que más). Generado con `scripts/generar_graficos_drivers_ecpm.py` → `recursos/graficos-drivers-ecpm.json`.\n",
              "### 3.1 eCPM ponderado por publisher y país\n",
              "![eCPM por publisher y país](recursos/graficos-drivers-ecpm-heatmap-publisher-pais.svg)\n",
              "*Publishers ordenados por requests vendidos (top 12). En cada celda, eCPM ponderado y, debajo, % del tráfico vendido "
              "del consolidado que cae en esa combinación. Vacío = menos del 0.05 % del tráfico vendido.*\n",
              "| Publisher | " + " | ".join(drv["paises"]) + " |\n|---|" + "---:|" * len(drv["paises"])]
        for p, row in drv["heatmap"].items():
            cells = [f"${c['ecpm_ponderado']:.2f} ({c['share_trafico_vendido_pct']:.1f}%)" if c and c["share_trafico_vendido_pct"] >= 0.05 else "—"
                     for c in (row[x] for x in drv["paises"])]
            L.append(f"| {p} | " + " | ".join(cells) + " |")
        L += ["\n### 3.2 Publishers: % de requests vendidos vs eCPM ponderado\n",
              "![publishers: % vendido vs eCPM](recursos/graficos-drivers-ecpm-scatter-publisher.svg)\n",
              f"*Un punto por publisher (top 20 por requests); el tamaño es el total de requests. Líneas punteadas: promedio "
              f"ponderado del consolidado ({tot['pct_vendido']:.0f} % vendido, ${tot['ecpm_ponderado']:.2f}).*\n",
              "| Publisher | Requests | % vendido (eCPM > 0) | eCPM pond. | % del tráfico vendido |\n|---|---:|---:|---:|---:|"]
        for p, d in sorted(drv["publishers"].items(), key=lambda kv: -kv[1]["requests"]):
            L.append(f"| {p} | {n(d['requests'])} | {pct(d['pct_vendido'])} | ${d['ecpm_ponderado']:.2f} | {pct(d['share_trafico_vendido_pct'])} |")
        L.append("")
    # ---- 4. por app: eCPM ponderado segun campos llenos (scripts/generar_barras_app_completitud.py) ----
    pbar = os.path.join(R, "graficos-app-completitud-barras.json")
    if os.path.exists(pbar):
        bar = json.load(open(pbar, encoding="utf-8"))
        L += ["## 4. Por app: eCPM ponderado según cuántos content objects trae el registro\n",
              f"Top {len(bar['apps'])} apps por requests vendidos. Para cada app, barra = eCPM ponderado (eCPM > 0) de los registros "
              "con ese número de content objects con dato útil (de 8); debajo de cada barra, el % de los requests vendidos de la app en "
              f"ese nivel. Los niveles con menos del {bar['min_share_pct']:g} % de los requests vendidos de la app no se dibujan ni se tabulan. "
              "Generado con `scripts/generar_barras_app_completitud.py` → `recursos/graficos-app-completitud-barras.json`.\n",
              "![eCPM por app y campos llenos](recursos/graficos-app-completitud-barras.svg)\n",
              "| App | eCPM pond. app | % tráfico vendido | " + " | ".join(str(k) for k in range(9)) + " |\n|---|---:|---:|" + "---:|" * 9]
        for app, d in bar["apps"].items():
            cells = [f"${x['ecpm_ponderado']:.2f} ({x['pct_requests_vendidos']:.0f}%)"
                     if x["ecpm_ponderado"] is not None and x["pct_requests_vendidos"] >= bar["min_share_pct"] else "—"
                     for x in d["niveles"]]
            L.append(f"| {app} | ${d['ecpm_ponderado']:.2f} | {pct(d['share_trafico_vendido_pct'])} | " + " | ".join(cells) + " |")
        L.append("\n*Entre paréntesis, el % de los requests vendidos de la app que cae en ese nivel de campos llenos.*\n")
    # ---- 5. titulos en mas de un pageURL / emisor (scripts/generar_tabla_pageurl_titulos.py) ----
    ptp = os.path.join(R, "titulos-pageurl.json")
    if os.path.exists(ptp):
        tp = json.load(open(ptp, encoding="utf-8"))
        L += ["## 5. Títulos emitidos por más de un pageURL\n",
              f"Publisher = ruta de venta; pageURL = app que emite; emisor = pageURL agrupados por App Name "
              f"(`recursos/pageurl-emisores.csv`). {n(tp['titulos_reales'])} títulos reales. "
              "Generado con `scripts/generar_tabla_pageurl_titulos.py` → `recursos/titulos-pageurl.json`.\n",
              "**Según cuántos pageURL distintos emiten el título:**\n",
              "| pageURL distintos por título | % de títulos | % de requests |\n|---:|---:|---:|"]
        for a_ in tp["por_pageurl"]:
            L.append(f"| {a_['n']} | {pct(a_['pct_titulos'])} | {pct(a_['pct_requests'])} |")
        L += ["\n**Según cuántos emisores distintos lo emiten (pageURL agrupados por App Name):**\n",
              "| Emisores distintos por título | % de títulos | % de requests |\n|---:|---:|---:|"]
        for b_ in tp["por_emisor"]:
            L.append(f"| {b_['n']} | {pct(b_['pct_titulos'])} | {pct(b_['pct_requests'])} |")
        L += ["\n| Título (top por requests, ≥ 2 emisores) | pageURL | publishers | emisores | países | Emisores principales (% de sus requests) |\n|---|---:|---:|---:|---:|---|"]
        for t in tp["top_titulos_multi_emisor"]:
            L.append(f"| {t['titulo']} | {t['pageurls']} | {t['publishers']} | {t['emisores']} | {t['paises']} | {', '.join(t['emisores_principales'])} |")
        L.append("")
    out = os.path.join(D, "reporte-graficos-ecpm-vacio.md")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L).rstrip("\n") + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
