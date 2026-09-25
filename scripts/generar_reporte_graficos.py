# -*- coding: utf-8 -*-
"""Markdown del reporte de graficas (solo tablas) a partir de los JSON de la tanda.

Lee, en <carpeta>/recursos/:
    graficos-ecpm-vacio-r2.json              (scripts/generar_graficos_ecpm_vacio.py)
    graficos-ecpm-completitud-scatter.json   (scripts/generar_scatter_completitud_ecpm.py)
y escribe <carpeta>/reporte-graficos-ecpm-vacio.md (los SVG se enlazan desde recursos/) con dos secciones: reparto del gasto
entre filas llenas y vacias, y scatter fila a fila de campos llenos vs eCPM (log). (Los scatter de eCPM llenas vs vacias
y de % llenas vs eCPM se quitaron el 2026-09-17: no mostraban relacion; el script de graficas los
sigue produciendo en recursos/ pero no se enlazan.) La parte de la ruta de venta (publisher y pais) va en un md aparte:
<carpeta>/recursos/reporte-drivers-ecpm-publisher-pais.md.

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


def r2_texto(st):
    """Parrafo de la 7.2: R2 del eCPM ponderado de las filas sin titulo por content object (graficos-sin-titulo.json).
    "solo" = % de la variacion que explican las medias por valor; "extra" = puntos que agrega sobre publisher x pais."""
    f = st["r2"]["factores"]
    lider = max(f, key=lambda k: f[k]["extra_sobre_ruta_pp"])
    resto = max(f[k]["extra_sobre_ruta_pp"] for k in ("livestream", "length", "categoria", "series"))
    return ("Género normalizado tal como llega. "
            + ("Es el content object que más separa el precio cuando no hay título: explica " if lider == "genero" else "Explica ")
            + f"el {f['genero']['solo_pct']:.1f} % de la variación del eCPM ponderado solo y aporta {f['genero']['extra_sobre_ruta_pp']:.1f} "
            f"puntos más controlando por publisher × país (rating: {f['rating']['solo_pct']:.1f} % y {f['rating']['extra_sobre_ruta_pp']:.1f} puntos; "
            f"livestream, length, categoría y series: {resto:.1f} puntos o menos).\n")


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
    # ---- drivers del eCPM: la ruta de venta (scripts/generar_graficos_drivers_ecpm.py) -> md aparte en recursos/ ----
    pdrv = os.path.join(R, "graficos-drivers-ecpm.json")
    if os.path.exists(pdrv):
        drv = json.load(open(pdrv, encoding="utf-8"))
        tot = drv["total"]
        M = [f"# Qué mueve el eCPM ponderado: la ruta de venta (publisher y país) (consolidado v10 a v{V})\n",
              "Sobre las filas con eCPM > 0 y requests > 0, la combinación publisher × país explica el "
              f"{drv['r2_publisher_pais_pct']:.1f} % de la variación del eCPM ponderado; los content objects, controlando por la ruta, aportan pocos puntos (género y rating "
              "los que más). Generado con `scripts/generar_graficos_drivers_ecpm.py` → `graficos-drivers-ecpm.json`.\n",
              "## 1. eCPM ponderado por publisher y país\n",
              "![eCPM por publisher y país](graficos-drivers-ecpm-heatmap-publisher-pais.svg)\n",
              "*Publishers ordenados por requests vendidos (top 12). En cada celda, eCPM ponderado y, debajo, % del tráfico vendido "
              "del consolidado que cae en esa combinación. Vacío = menos del 0.05 % del tráfico vendido.*\n",
              "| Publisher | " + " | ".join(drv["paises"]) + " |\n|---|" + "---:|" * len(drv["paises"])]
        for p, row in drv["heatmap"].items():
            cells = [f"${c['ecpm_ponderado']:.2f} ({c['share_trafico_vendido_pct']:.1f}%)" if c and c["share_trafico_vendido_pct"] >= 0.05 else "—"
                     for c in (row[x] for x in drv["paises"])]
            M.append(f"| {p} | " + " | ".join(cells) + " |")
        M += ["\n## 2. Publishers: % de requests vendidos vs eCPM ponderado\n",
              "![publishers: % vendido vs eCPM](graficos-drivers-ecpm-scatter-publisher.svg)\n",
              f"*Un punto por publisher (top 20 por requests); el tamaño es el total de requests. Líneas punteadas: promedio "
              f"ponderado del consolidado ({tot['pct_vendido']:.0f} % vendido, ${tot['ecpm_ponderado']:.2f}).*\n",
              "| Publisher | Requests | % vendido (eCPM > 0) | eCPM pond. | % del tráfico vendido |\n|---|---:|---:|---:|---:|"]
        for p, d in sorted(drv["publishers"].items(), key=lambda kv: -kv[1]["requests"]):
            M.append(f"| {p} | {n(d['requests'])} | {pct(d['pct_vendido'])} | ${d['ecpm_ponderado']:.2f} | {pct(d['share_trafico_vendido_pct'])} |")
        outd = os.path.join(R, "reporte-drivers-ecpm-publisher-pais.md")
        with open(outd, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(M).rstrip("\n") + "\n")
        print(f"-> {outd}")
    # ---- 3. por app: eCPM ponderado segun campos llenos (scripts/generar_barras_app_completitud.py) ----
    pbar = os.path.join(R, "graficos-app-completitud-barras.json")
    if os.path.exists(pbar):
        bar = json.load(open(pbar, encoding="utf-8"))
        L += ["## 3. Por app: eCPM ponderado según cuántos content objects trae el registro\n",
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
        psc = os.path.join(R, "graficos-app-requests-ecpm.json")
        if os.path.exists(psc):
            sa = json.load(open(psc, encoding="utf-8"))
            L += ["### 3.1 Apps: eCPM ponderado vs requests totales\n",
                  f"Un punto por App Name con requests vendidos ({n(sa['apps_con_venta'])} apps; otras {n(sa['apps_sin_venta'])} no vendieron nada y no "
                  "tienen eCPM). x = eCPM ponderado de la app (eCPM > 0); y = requests totales de la app; los dos ejes en escala logarítmica. "
                  f"Línea punteada: eCPM ponderado del consolidado (${sa['ecpm_ponderado_total']:.2f}). Tabla: las 30 apps de más requests; "
                  "todas están en `recursos/graficos-app-requests-ecpm.json`.\n",
                  "![apps: eCPM vs requests](recursos/graficos-app-requests-ecpm.svg)\n",
                  "| App | Requests | Requests vendidos | % vendido | eCPM pond. |\n|---|---:|---:|---:|---:|"]
            for d in sa["apps"][:30]:
                L.append(f"| {d['app']} | {n(d['requests'])} | {n(d['requests_vendidos'])} | {pct(d['pct_vendido'])} | ${d['ecpm_ponderado']:.2f} |")
            L.append("")
    # ---- 4. titulos en mas de un App Name (scripts/generar_tabla_pageurl_titulos.py) ----
    ptp = os.path.join(R, "titulos-appname.json")
    if os.path.exists(ptp):
        tp = json.load(open(ptp, encoding="utf-8"))
        L += ["## 4. Títulos emitidos por más de un App Name\n",
              f"{n(tp['titulos_reales'])} títulos reales, agrupados solo por App Name (sin pageURL). "
              "Generado con `scripts/generar_tabla_pageurl_titulos.py` → `recursos/titulos-appname.json`.\n",
              "| App Name distintos por título | % de títulos | % de requests |\n|---:|---:|---:|"]
        for b_ in tp["por_app_name"]:
            L.append(f"| {b_['n']} | {pct(b_['pct_titulos'])} | {pct(b_['pct_requests'])} |")
        invertida = os.path.exists(os.path.join(R, "graficos-titulos-appname-requests-ecpm.svg"))
        combinada = invertida or os.path.exists(os.path.join(R, "graficos-titulos-appname-ecpm-requests.svg"))
        if invertida:
            L += [f"\n**Top {len(tp['top_titulos_multi_app'])} títulos (por requests) en dos o más App Name:** una barra por App Name dentro de cada título, "
                  "con altura = requests totales (vendidos o no) de ese título en esa app, en miles de millones, en el eje izquierdo (las 5 apps "
                  "con más requests vendidos del título, de mayor a menor requests). La línea une el eCPM ponderado (eCPM > 0) de ese título en "
                  "cada app, en el eje derecho. Línea punteada = eCPM ponderado del título en todas sus apps; sobre cada grupo, los requests "
                  "totales del título. Las variantes de ViX (ViX: TV, Deportes y Noticias; ViX: TV, Sports and News; ViX: Cine y TV…; "
                  "VIX - Filmes e TV) cuentan como una sola app, ViX.\n",
                  "![títulos en varios App Name: requests totales (barras) y eCPM (línea) por app](recursos/graficos-titulos-appname-requests-ecpm.svg)\n"]
        elif combinada:
            # desde v20: una sola grafica de doble eje (barras = eCPM, linea = requests) y las variantes de ViX juntas
            L += [f"\n**Top {len(tp['top_titulos_multi_app'])} títulos (por requests) en dos o más App Name:** una barra por App Name dentro de cada título, "
                  "con altura = eCPM ponderado de ese título en esa app (eCPM > 0; las 5 apps con más requests vendidos del título), en el eje "
                  "izquierdo. La línea une los requests totales (vendidos o no) de ese título en cada app, en miles de millones, en el eje derecho. "
                  "Línea punteada = eCPM ponderado del título en todas sus apps; sobre cada grupo, los requests totales del título. Las variantes de "
                  "ViX (ViX: TV, Deportes y Noticias; ViX: TV, Sports and News; ViX: Cine y TV…; VIX - Filmes e TV) cuentan como una sola app, ViX.\n",
                  "![títulos en varios App Name: eCPM (barras) y requests totales (línea) por app](recursos/graficos-titulos-appname-ecpm-requests.svg)\n"]
        else:
            L += [f"\n**Top {len(tp['top_titulos_multi_app'])} títulos (por requests) en dos o más App Name:** una barra por App Name dentro de cada título, "
                  "con altura = eCPM ponderado de ese título en esa app (eCPM > 0; las 5 apps con más requests vendidos del título). "
                  "Línea punteada = eCPM ponderado del título en todas sus apps.\n",
                  "![títulos en varios App Name: eCPM y reparto por app](recursos/graficos-titulos-appname-barras.svg)\n"]
        L += ["| Título | App Name | Requests | eCPM pond. | Reparto por app (% de requests vendidos, eCPM pond. de la app) |\n|---|---:|---:|---:|---|"]
        for t_ in tp["top_titulos_multi_app"]:
            reparto = ", ".join(f"{x['app']} {x['pct_requests_vendidos']:.0f}% (${x['ecpm_ponderado']:.2f})" for x in t_["apps"][:5])
            L.append(f"| {t_['titulo']} | {t_['app_names']} | {n(t_['requests'])} | ${t_['ecpm_ponderado']:.2f} | {reparto} |")
        if combinada:
            L += ["\n| Título | Requests del título | Requests por app (% de los requests del título) |\n|---|---:|---|"]
            for t_ in tp["top_titulos_multi_app"]:
                top5 = [x for x in t_["apps"] if x["pct_requests_vendidos"] >= 2.0][:5]
                reparto = ", ".join(f"{x['app']} {n(x['requests'])} ({100 * x['requests'] / t_['requests']:.0f}%)"
                                    for x in sorted(top5, key=lambda x: -x["requests"]))
                L.append(f"| {t_['titulo']} | {n(t_['requests'])} | {reparto} |")
        elif os.path.exists(os.path.join(R, "graficos-titulos-appname-requests.svg")):
            L += ["\n**Los mismos títulos, con los requests totales en el eje Y:** mismas apps, orden de barras y colores que la gráfica anterior; "
                  "altura = requests totales (vendidos o no) de ese título en esa app, en miles de millones. Sobre cada grupo, los requests "
                  "totales del título en todas sus apps.\n",
                  "![títulos en varios App Name: requests totales por app](recursos/graficos-titulos-appname-requests.svg)\n",
                  "| Título | Requests del título | Requests por app (% de los requests del título) |\n|---|---:|---|"]
            for t_ in tp["top_titulos_multi_app"]:
                top5 = [x for x in t_["apps"] if x["pct_requests_vendidos"] >= 2.0][:5]
                reparto = ", ".join(f"{x['app']} {n(x['requests'])} ({100 * x['requests'] / t_['requests']:.0f}%)"
                                    for x in sorted(top5, key=lambda x: -x["requests"]))
                L.append(f"| {t_['titulo']} | {n(t_['requests'])} | {reparto} |")
        L.append("")
    # ---- 5. completitud por canal (scripts/generar_barras_canales_completitud.py) ----
    pcan = os.path.join(R, "graficos-canales-completitud-barras.json")
    if os.path.exists(pcan):
        can = json.load(open(pcan, encoding="utf-8"))
        cols = can["campos"]
        L += ["## 5. Completitud de los content objects por canal\n",
              "Canal = filas cuyo Publisher o App Name lo nombra (Caracol via OB / ditu por Caracol, RCN via OB / Canal RCN, Canal 13 OB, "
              "Televisa Univision via … / ViX, TV Azteca - Springserve / Azteca TV). Cada segmento de la barra es una columna, con altura = "
              "% de filas del canal con dato útil en esa columna dividido entre 8, apilados de mayor % (arriba) a menor (abajo); la barra "
              "completa es la completitud promedio de las 8 columnas. La tabla va ordenada por completitud promedio. Generado con `scripts/generar_barras_canales_completitud.py` → `recursos/graficos-canales-completitud-barras.json`.\n",
              "![completitud por canal](recursos/graficos-canales-completitud-barras.svg)\n",
              "| Canal | Promedio | Filas | Requests | " + " | ".join(c.replace("content", "") for c in cols) + " |\n|---|---:|---:|---:|" + "---:|" * len(cols)]
        for d in can["canales"]:
            if not d["filas"]:
                L.append(f"| {d['canal']} | — | 0 | 0 | " + " | ".join("—" for _ in cols) + " |")
                continue
            L.append(f"| {d['canal']} | {pct(d['completitud_promedio'])} | {n(d['filas'])} | {n(d['requests'])} | "
                     + " | ".join(pct(d["pct_llenas"][c]) for c in cols) + " |")
        L.append("\n*Win y Telefe no aparecen en el consolidado: ningún Publisher ni App Name los nombra.*\n")
        # ---- 6. canales: requests totales vs eCPM ponderado ----
        if os.path.exists(os.path.join(R, "graficos-canales-ecpm-requests.svg")):
            L += ["## 6. Canales: eCPM ponderado vs requests totales\n",
                  "Un punto por canal (mismos canales y misma definición de la sección 5). x = eCPM ponderado de sus filas con eCPM > 0; "
                  "un canal con requests pero sin ninguna fila vendida va en $0 con un punto hueco; y = requests totales del canal en escala "
                  "logarítmica. Junto al punto, requests totales y % de requests vendidos.\n",
                  "![canales: eCPM vs requests](recursos/graficos-canales-ecpm-requests.svg)\n"]
        else:
            L += ["## 6. Canales: requests totales vs eCPM ponderado\n",
                  "Un punto por canal (mismos canales y misma definición de la sección 5). x = requests totales del canal en escala "
                  "logarítmica; y = eCPM ponderado de sus filas con eCPM > 0; un canal con requests pero sin ninguna fila vendida va en $0 con "
                  "un punto hueco. Junto al punto, requests totales y % de requests vendidos.\n",
                  "![canales: requests vs eCPM](recursos/graficos-canales-requests-ecpm.svg)\n"]
        L += [
              "| Canal | Requests | Requests vendidos | % vendido | eCPM pond. |\n|---|---:|---:|---:|---:|"]
        for d in sorted(can["canales"], key=lambda d: -d["requests"]):
            if not d["requests"]:
                L.append(f"| {d['canal']} | 0 | 0 | — | — |")
            else:
                L.append(f"| {d['canal']} | {n(d['requests'])} | {n(d['requests_vendidos'])} | {pct(d['pct_vendido'])} | "
                         + (f"${d['ecpm_ponderado']:.2f}" if d["ecpm_ponderado"] is not None else "— (sin filas vendidas)") + " |")
        L.append("")
    # ---- 7. registros sin contentTitle (scripts/generar_graficos_sin_titulo.py) ----
    pst = os.path.join(R, "graficos-sin-titulo.json")
    if os.path.exists(pst):
        st = json.load(open(pst, encoding="utf-8"))
        L += ["## 7. Registros sin contentTitle: qué content objects se relacionan con el eCPM\n",
              f"{n(st['filas_sin_titulo'])} filas sin título ({n(st['requests'])} requests; {pct(st['pct_vendido'])} vendidos; "
              f"eCPM ponderado ${st['ecpm_ponderado']:.2f}). Generado con `scripts/generar_graficos_sin_titulo.py` → `recursos/graficos-sin-titulo.json`.\n",
              "### 7.1 eCPM ponderado con y sin dato en cada columna\n",
              "Filas sin título del consolidado tal como llega, antes del relleno. Por columna se parten en dos grupos: las que traen dato útil "
              "(círculo lleno) y las que la traen vacía (círculo hueco); de cada grupo, su % de las filas sin título, su % de requests vendidos "
              "y su eCPM ponderado. Diferencia = eCPM con dato − eCPM sin dato.\n",
              "![sin título: eCPM con y sin dato por columna](recursos/graficos-sin-titulo-con-sin-dato.svg)\n",
              "| Columna | % filas con dato | % vendido con dato | eCPM pond. con dato | % filas sin dato | % vendido sin dato | eCPM pond. sin dato | Diferencia |\n"
              "|---|---:|---:|---:|---:|---:|---:|---:|"]

        def dif(d):
            a_, b_ = d["con"]["ecpm_ponderado"], d["sin"]["ecpm_ponderado"]
            return a_ - b_ if a_ is not None and b_ is not None else float("-inf")
        for c, d in sorted(st["columnas"].items(), key=lambda kv: -dif(kv[1])):
            cel = []
            for k in ("con", "sin"):
                g = d[k]
                cel += [pct(g["pct_filas"]), pct(g["pct_vendido"]) if g["pct_vendido"] is not None else "—",
                        f"${g['ecpm_ponderado']:.2f}" if g["ecpm_ponderado"] is not None else "—"]
            df = dif(d)
            cel.append("—" if df == float("-inf") else f"{'+' if df >= 0 else '−'}${abs(df):.2f}")
            L.append(f"| {c} | " + " | ".join(cel) + " |")
        if os.path.exists(os.path.join(R, "graficos-sin-titulo-con-sin-dato-requests.svg")):
            L += ["\n### 7.2 Requests totales con y sin dato en cada columna\n",
                  "Las mismas filas sin título y los mismos dos grupos por columna que en 7.1 (mismo orden de columnas), con los requests "
                  "totales (vendidos o no) de cada grupo en el eje x, en miles de millones. En cada columna los dos puntos suman el total "
                  f"de requests sin título ({n(st['requests'])}).\n",
                  "![sin título: requests totales con y sin dato por columna](recursos/graficos-sin-titulo-con-sin-dato-requests.svg)\n",
                  "| Columna | Requests con dato | % requests con dato | Requests sin dato | % requests sin dato |\n|---|---:|---:|---:|---:|"]
            for c, d in sorted(st["columnas"].items(), key=lambda kv: -dif(kv[1])):
                L.append(f"| {c} | {n(d['con']['requests'])} | {pct(100 * d['con']['requests'] / st['requests'])} | "
                         f"{n(d['sin']['requests'])} | {pct(100 * d['sin']['requests'] / st['requests'])} |")
            sec_genero = "7.3"
        else:
            sec_genero = "7.2"
        if "requests" in st["genero"][0]:
            # desde v20: top 20 generos por requests, doble eje (barras = eCPM, linea = requests totales)
            gs = st["genero"][:20]   # ya viene de mayor a menor requests, el mismo orden de la grafica
            L += [f"\n### {sec_genero} Requests totales y eCPM ponderado por género en las filas sin título\n",
                  r2_texto(st),
                  f"Top {len(gs)} géneros por requests totales. Barras = requests totales (vendidos o no) del género, en miles de millones "
                  "(eje izquierdo), de mayor a menor; línea = eCPM ponderado del género (eje derecho). Línea punteada = eCPM ponderado de "
                  "todas las filas sin título.\n",
                  "![sin título: requests y eCPM por género](recursos/graficos-sin-titulo-genero-requests-ecpm.svg)\n",
                  "| Género | Filas | Requests | % vendido | % del tráfico vendido sin título | eCPM pond. |\n|---|---:|---:|---:|---:|---:|"]
            for g in gs:
                L.append(f"| {g['genero']} | {n(g['filas'])} | {n(g['requests'])} | {pct(g['pct_vendido'])} | {pct(g['share_trafico_vendido_pct'])} | "
                         + (f"${g['ecpm_ponderado']:.2f}" if g["ecpm_ponderado"] is not None else "— (sin venta)") + " |")
        else:
            L += [f"\n### {sec_genero} eCPM ponderado por género en las filas sin título\n",
                  r2_texto(st),
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
