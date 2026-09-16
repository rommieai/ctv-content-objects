# -*- coding: utf-8 -*-
"""Markdown del reporte de graficas (solo tablas) a partir de los JSON de la tanda.

Lee, en la carpeta de la tanda:
    graficos-ecpm-vacio-r2.json              (scripts/generar_graficos_ecpm_vacio.py)
    graficos-ecpm-completitud-heatmap.json   (scripts/generar_heatmap_completitud_ecpm.py)
y escribe reporte-graficos-ecpm-vacio.md con las cuatro secciones: scatter llenas vs vacias
(OLS/R2), % llenas vs eCPM por serie, reparto del gasto y heatmap de campos llenos vs eCPM.

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
    r2 = json.load(open(os.path.join(D, "graficos-ecpm-vacio-r2.json"), encoding="utf-8"))["grupos"]
    hm = json.load(open(os.path.join(D, "graficos-ecpm-completitud-heatmap.json"), encoding="utf-8"))

    L = [f"# Gráficos: eCPM de las filas llenas vs vacías (consolidado v10 a v{V})\n",
         f"**Fuente:** `reporte-requests-ecpm-por-vacio-v{V}.json` (mismos datos de las tablas por país del detallado). "
         "Generado con `scripts/generar_graficos_ecpm_vacio.py` → `graficos-ecpm-vacio-r2.json`; tablas con "
         "`scripts/generar_reporte_graficos.py`.\n",
         "*eCPM ponderado = Σ(eCPM × requests) / Σ requests, sin las filas con requests = 0 o eCPM = 0. Un punto por content "
         "object (9 columnas: App Name y los 8 content objects con filas vacías; contentIsTitlePresent y Publisher vienen al "
         "100% y no entran). R² es el de la recta de mínimos cuadrados (OLS) sobre esos 9 puntos.*\n",
         "## 1. eCPM llenas (x) vs eCPM vacías (y)\n",
         "![eCPM llenas vs vacías](graficos-ecpm-vacio-scatter.svg)\n",
         "| Grupo | R² | Pendiente | Intercepto | Columnas que pagan más vacías |\n|---|---:|---:|---:|---:|"]
    for k, lab in GRUPOS:
        s = r2[k]["scatter_lleno_vs_vacio"]
        o = s["ols"]
        L.append(f"| {lab} | {o['r2']:.3f} | {o['pendiente']:.3f} | {o['intercepto']:.2f} | {s['columnas_vacio_paga_mas']} de {s['columnas']} |")
    L += ["\n## 2. % de filas llenas (x) vs eCPM (y), por serie\n",
          "![completitud vs eCPM](graficos-ecpm-vacio-scatter-fill.svg)\n",
          "| Grupo | Serie | R² | Pendiente ($ por punto de %) | Intercepto |\n|---|---|---:|---:|---:|"]
    for k, lab in GRUPOS:
        s = r2[k]["scatter_fill_vs_ecpm"]
        for serie, key in (("eCPM filas llenas", "llenas"), ("eCPM filas vacías", "vacias")):
            o = s[key]
            L.append(f"| {lab} | {serie} | {o['r2']:.3f} | {o['pendiente']:.4f} | {o['intercepto']:.2f} |")
    L += ["\n## 3. Reparto del gasto (eCPM × requests / 1000) entre filas llenas y vacías\n",
          "![reparto del gasto](graficos-ecpm-vacio-pies.svg)\n",
          "*% del gasto del grupo que cae en filas donde la columna trae dato útil. El gasto se calcula solo sobre filas con eCPM > 0.*\n",
          "| Columna | " + " | ".join(lab for _, lab in GRUPOS) + " |\n|---|" + "---:|" * len(GRUPOS)]
    for c in COLS:
        L.append(f"| {c} | " + " | ".join(pct(r2[k]["gasto"][c]["pct_gasto_llenas"]) for k, _ in GRUPOS) + " |")
    L += ["\n## 4. Completitud de la fila vs eCPM: densidad de requests (fila a fila)\n",
          "Cada fila del consolidado se clasifica por cuántos de los 8 content objects trae con dato útil (contentGenre, "
          "contentCategory, contentSeries, contentLength, contentLanguage, contentIsLiveStream, contentTitle, contentRating; "
          "contentIsTitlePresent no cuenta porque siempre viene). El heatmap acumula los requests de las filas en cada celda de "
          "(campos llenos, bin logarítmico de eCPM); la banda inferior son las filas con eCPM = 0. El punto naranja es el eCPM "
          "ponderado (>0) de cada nivel. Generado con `scripts/generar_heatmap_completitud_ecpm.py` → "
          "`graficos-ecpm-completitud-heatmap.json`.\n",
          "![completitud vs eCPM, densidad](graficos-ecpm-completitud-heatmap.svg)\n"]
    for k, lab in GRUPOS:
        g = hm["grupos"][k]
        L.append(f"**{lab}** — {n(g['filas'])} filas · {n(g['requests'])} requests\n")
        L.append("| Campos llenos (de 8) | % filas | % requests | % requests vendidos (eCPM > 0) | eCPM pond. (>0) |\n|---:|---:|---:|---:|---:|")
        for x in g["niveles"]:
            L.append(f"| {x['campos_llenos']} | {pct(x['pct_filas'])} | {pct(x['pct_requests'])} | {pct(x['pct_req_monetizado'])} | ${x['ecpm_ponderado']:.2f} |")
        L.append("")
    out = os.path.join(D, "reporte-graficos-ecpm-vacio.md")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L).rstrip("\n") + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
