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
    # ---- 5. titulos en mas de un App Name (scripts/generar_tabla_pageurl_titulos.py) ----
    ptp = os.path.join(R, "titulos-appname.json")
    if os.path.exists(ptp):
        tp = json.load(open(ptp, encoding="utf-8"))
        L += ["## 5. Títulos emitidos por más de un App Name\n",
              f"{n(tp['titulos_reales'])} títulos reales, agrupados solo por App Name (sin pageURL). "
              "Generado con `scripts/generar_tabla_pageurl_titulos.py` → `recursos/titulos-appname.json`.\n",
              "| App Name distintos por título | % de títulos | % de requests |\n|---:|---:|---:|"]
        for b_ in tp["por_app_name"]:
            L.append(f"| {b_['n']} | {pct(b_['pct_titulos'])} | {pct(b_['pct_requests'])} |")
        L += [f"\n**Top {len(tp['top_titulos_multi_app'])} títulos (por requests) en dos o más App Name:** una barra por App Name dentro de cada título, "
              "con altura = eCPM ponderado de ese título en esa app (eCPM > 0; las 5 apps con más requests vendidos del título). "
              "Línea punteada = eCPM ponderado del título en todas sus apps.\n",
              "![títulos en varios App Name: eCPM y reparto por app](recursos/graficos-titulos-appname-barras.svg)\n",
              "| Título | App Name | Requests | eCPM pond. | Reparto por app (% de requests vendidos, eCPM pond. de la app) |\n|---|---:|---:|---:|---|"]
        for t_ in tp["top_titulos_multi_app"]:
            reparto = ", ".join(f"{x['app']} {x['pct_requests_vendidos']:.0f}% (${x['ecpm_ponderado']:.2f})" for x in t_["apps"][:5])
            L.append(f"| {t_['titulo']} | {t_['app_names']} | {n(t_['requests'])} | ${t_['ecpm_ponderado']:.2f} | {reparto} |")
        L.append("")
    # ---- 6. completitud por canal (scripts/generar_barras_canales_completitud.py) ----
    pcan = os.path.join(R, "graficos-canales-completitud-barras.json")
    if os.path.exists(pcan):
        can = json.load(open(pcan, encoding="utf-8"))
        cols = can["campos"]
        L += ["## 6. Completitud de los content objects por canal\n",
              "Canal = filas cuyo Publisher o App Name lo nombra (Caracol via OB / ditu por Caracol, RCN via OB / Canal RCN, Canal 13 OB, "
              "Televisa Univision via … / ViX, TV Azteca - Springserve / Azteca TV). Cada segmento de la barra es una columna, con altura = "
              "% de filas del canal con dato útil en esa columna dividido entre 8; la barra completa es la completitud promedio de las 8 "
              "columnas. Generado con `scripts/generar_barras_canales_completitud.py` → `recursos/graficos-canales-completitud-barras.json`.\n",
              "![completitud por canal](recursos/graficos-canales-completitud-barras.svg)\n",
              "| Canal | Filas | Requests | Promedio | " + " | ".join(c.replace("content", "") for c in cols) + " |\n|---|---:|---:|---:|" + "---:|" * len(cols)]
        for d in can["canales"]:
            if not d["filas"]:
                L.append(f"| {d['canal']} | 0 | 0 | — | " + " | ".join("—" for _ in cols) + " |")
                continue
            L.append(f"| {d['canal']} | {n(d['filas'])} | {n(d['requests'])} | {pct(d['completitud_promedio'])} | "
                     + " | ".join(pct(d["pct_llenas"][c]) for c in cols) + " |")
        L.append("\n*Win y Telefe no aparecen en el consolidado: ningún Publisher ni App Name los nombra.*\n")
        # ---- 7. canales: requests totales vs eCPM ponderado ----
        L += ["## 7. Canales: requests totales vs eCPM ponderado\n",
              "Un punto por canal (mismos canales y misma definición de la sección 6). x = requests totales del canal en escala "
              "logarítmica; y = eCPM ponderado de sus filas con eCPM > 0. Junto al punto, requests totales y % de requests vendidos.\n",
              "![canales: requests vs eCPM](recursos/graficos-canales-requests-ecpm.svg)\n",
              "| Canal | Requests | Requests vendidos | % vendido | eCPM pond. |\n|---|---:|---:|---:|---:|"]
        for d in sorted(can["canales"], key=lambda d: -d["requests"]):
            if not d["requests"]:
                L.append(f"| {d['canal']} | 0 | 0 | — | — |")
            else:
                L.append(f"| {d['canal']} | {n(d['requests'])} | {n(d['requests_vendidos'])} | {pct(d['pct_vendido'])} | "
                         + (f"${d['ecpm_ponderado']:.2f}" if d["ecpm_ponderado"] is not None else "— (sin filas vendidas)") + " |")
        L.append("")
    # ---- 8. registros sin contentTitle (scripts/generar_graficos_sin_titulo.py) ----
    pst = os.path.join(R, "graficos-sin-titulo.json")
    if os.path.exists(pst):
        st = json.load(open(pst, encoding="utf-8"))
        L += ["## 8. Registros sin contentTitle: qué content objects se relacionan con el eCPM\n",
              f"{n(st['filas_sin_titulo'])} filas sin título ({n(st['requests'])} requests; {pct(st['pct_vendido'])} vendidos; "
              f"eCPM ponderado ${st['ecpm_ponderado']:.2f}). Generado con `scripts/generar_graficos_sin_titulo.py` → `recursos/graficos-sin-titulo.json`.\n",
              "### 8.1 % de filas llenas vs eCPM por columna, sin y con relleno\n",
              "Como en la gráfica de completitud vs eCPM de la tanda v18, pero solo con las filas sin título y con dos marcas por columna: "
              "círculo = tal como llega, rombo = tras el pipeline de relleno. Sin título no hay `titulo_clave`, así que ni `intra_titulo` "
              "ni IMDb aplican; solo cambian las columnas que se derivan de la misma fila (categoría desde el género) o de la app (livestream).\n",
              "![sin título: % llenas vs eCPM, sin y con relleno](recursos/graficos-sin-titulo-columnas.svg)\n",
              "| Columna | % llenas sin relleno | eCPM pond. sin relleno | % llenas con relleno | eCPM pond. con relleno |\n|---|---:|---:|---:|---:|"]
        for c, d in st["columnas"].items():
            a_, b_ = d["orig"], d["rell"]
            fa = f"${a_['ecpm_ponderado']:.2f}" if a_["ecpm_ponderado"] is not None else "—"
            fb = f"${b_['ecpm_ponderado']:.2f}" if b_["ecpm_ponderado"] is not None else "—"
            L.append(f"| {c} | {pct(a_['pct_filas_llenas'])} | {fa} | {pct(b_['pct_filas_llenas'])} | {fb} |")
        L += ["\n### 8.2 eCPM ponderado por género en las filas sin título\n",
              "Género normalizado tal como llega. Es el content object que más separa el precio cuando no hay título: explica el 20.6 % de la "
              "variación del eCPM ponderado solo y aporta 6.9 puntos más controlando por publisher × país (rating: 17.1 % y 4.7 puntos; "
              "livestream, length, categoría y series: menos de 1.5 puntos).\n",
              "![sin título: eCPM por género](recursos/graficos-sin-titulo-genero.svg)\n",
              "| Género | Filas | % del tráfico vendido sin título | eCPM pond. |\n|---|---:|---:|---:|"]
        for g in sorted([g for g in st["genero"] if g["share_trafico_vendido_pct"] >= 0.5], key=lambda g: -g["ecpm_ponderado"]):
            L.append(f"| {g['genero']} | {n(g['filas'])} | {pct(g['share_trafico_vendido_pct'])} | ${g['ecpm_ponderado']:.2f} |")
        L.append("")
    out = os.path.join(D, "reporte-graficos-ecpm-vacio.md")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L).rstrip("\n") + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
