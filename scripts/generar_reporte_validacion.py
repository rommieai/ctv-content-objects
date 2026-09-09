# -*- coding: utf-8 -*-
"""Genera los reportes markdown de validacion de contentCategory a partir de los JSON de
validar_categorias.py (uno o varios datasets lado a lado).

    python scripts/generar_reporte_validacion.py reportes/15-validacion-categorias-v17 \
        consolidado=reportes/15-validacion-categorias-v17/validacion-consolidado.json \
        relleno=reportes/15-validacion-categorias-v17/validacion-relleno.json

Escribe en el directorio de salida:
    reporte-correctitud.md    parte 1: las filas llenas, ¿estan bien llenadas?
    reporte-completitud.md    parte 2: ¿se puede poner una categoria IAB mas fina?

Todo el texto con numeros sale del JSON; las lecturas narrativas (que significa) van en
el README del paquete, escrito a mano tras cada corrida.
"""
import json
import os
import sys
from collections import OrderedDict


def fmt_n(n):
    return f"{int(n):,}"


def fmt_p(p):
    return "—" if p is None else f"{p:.1f}%"


def tabla(headers, filas, align=None):
    align = align or ["---"] + ["---:"] * (len(headers) - 1)
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(align) + "|"]
    for f in filas:
        out.append("| " + " | ".join(str(x) for x in f) + " |")
    return "\n".join(out) + "\n"


def get(d, *ks, default=None):
    for k in ks:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


def celda(bloque, clave, campo="pct_filas"):
    v = get(bloque, clave, campo)
    if v is None:
        return "—"
    return fmt_p(v) if campo.startswith("pct") else fmt_n(v)


def celda_fr(bloque, clave):
    """'filas (pct_filas%) · req pct%'"""
    b = get(bloque, clave)
    if not b:
        return "—"
    return f"{fmt_n(b['filas'])} ({fmt_p(b['pct_filas'])}) · req {fmt_p(b['pct_requests'])}"


VEREDICTOS = ["coincide", "compatible", "contradice", "no_evaluable"]
EVIDENCIAS = ["externa", "interna", "ninguna"]


def resumen_veredicto(c):
    """Devuelve dict con % de las llenas por (evidencia, veredicto) y % de las evaluables."""
    v = c["veredicto"]
    tot_f = sum(x["filas"] for x in v.values())
    tot_r = sum(x["requests"] for x in v.values())
    ev_f = sum(x["filas"] for k, x in v.items() if not k.endswith("no_evaluable"))
    ev_r = sum(x["requests"] for k, x in v.items() if not k.endswith("no_evaluable"))
    out = {"llenas": tot_f, "llenas_req": tot_r, "evaluables": ev_f, "evaluables_req": ev_r,
           "pct_evaluables": 100.0 * ev_f / tot_f if tot_f else 0,
           "pct_evaluables_req": 100.0 * ev_r / tot_r if tot_r else 0}
    for ver in VEREDICTOS[:3]:
        f = sum(x["filas"] for k, x in v.items() if k.endswith("|" + ver))
        r = sum(x["requests"] for k, x in v.items() if k.endswith("|" + ver))
        out[ver] = f
        out[ver + "_req"] = r
        out["pct_" + ver] = 100.0 * f / ev_f if ev_f else 0
        out["pct_" + ver + "_req"] = 100.0 * r / ev_r if ev_r else 0
        for e in EVIDENCIAS[:2]:
            x = v.get(f"{e}|{ver}", {})
            fe = sum(y["filas"] for k, y in v.items() if k.startswith(e + "|"))
            out[f"pct_{e}_{ver}"] = 100.0 * x.get("filas", 0) / fe if fe else 0
    return out


def desglose_bloque(b, claves, pref=""):
    """De un bloque {clave: {filas, requests, pct...}} saca % de filas por clave."""
    tot = sum(x["filas"] for x in b.values()) if b else 0
    return {k: (100.0 * get(b, pref + k, "filas", default=0) / tot if tot else 0) for k in claves}


# ----------------------------------------------------------------------------
def reporte_correctitud(datasets, out_dir):
    L = []
    nombres = list(datasets.keys())
    D = datasets
    m0 = D[nombres[0]]["meta"]
    L.append("# Reporte — Correctitud de contentCategory: las filas llenas, ¿están bien llenadas?\n")
    L.append("**Fuentes:** " + "; ".join(f"`{D[n]['meta']['archivo']}` ({fmt_n(D[n]['meta']['filas'])} filas, "
                                        f"columna `{D[n]['meta']['columna']}`)" for n in nombres) + ".  ")
    L.append(f"**Generado con:** `scripts/validar_categorias.py` (un JSON por dataset) + "
             f"`scripts/generar_reporte_validacion.py`. Corrida del {m0['fecha']}. "
             f"Evidencia externa: match IMDb de confianza ≥ {m0['confianza_min']} más géneros de Wikidata, "
             f"desde `cache-enriquecimiento/titulos.json` ({fmt_n(m0['titulos_en_cache'])} títulos); taxonomías "
             f"IAB Content Taxonomy 1.0 ({m0['taxonomias']['1.0']} nodos), 2.2 ({m0['taxonomias']['2.2']}) "
             f"y 3.0 ({m0['taxonomias']['3.0']}) oficiales de IAB Tech Lab.\n")
    L.append("**Convención:** salvo que se diga otra cosa, los % son **% de las filas que traen categoría** "
             "(no del total del consolidado); cuando se dice \"de las evaluables\" es sobre las filas con categoría "
             "que además tienen evidencia para juzgarla. Cada tabla trae también el % de requests cuando aporta.\n")
    L.append("---\n")

    # ---- 1. universo ---------------------------------------------------------------------
    L.append("## 1. Universo: qué se pudo evaluar\n")
    L.append("Una fila solo se puede juzgar si hay contra qué. La evidencia **externa** (título real con match "
             "IMDb/Wikidata) prueba vertical, forma (película/TV) y género; la **interna** (el `contentGenre` de la "
             "misma fila) solo prueba lo que un género implica: que un drama no es noticias, que un talk show no "
             "es película. Sin ninguna de las dos, la fila queda `no_evaluable`.\n")
    filas = []
    for n in nombres:
        m, c = D[n]["meta"], D[n]["correctitud"]
        rv = resumen_veredicto(c)
        filas.append([f"**{n}**", fmt_n(m["filas"]),
                      f"{fmt_n(m['filas_con_categoria'])} ({fmt_p(m['pct_filas_con_categoria'])})",
                      fmt_p(m["pct_requests_con_categoria"]),
                      f"{fmt_n(m['filas_con_match_externo'])} ({fmt_p(m['pct_filas_con_match_externo'])})",
                      celda_fr(c["evidencia"], "externa"), celda_fr(c["evidencia"], "interna"),
                      celda_fr(c["evidencia"], "ninguna")])
    L.append(tabla(["Dataset", "Filas", "Con categoría (% total)", "% requests con categoría",
                    "Con match externo (% total)", "Evidencia externa (de las llenas)",
                    "Evidencia interna", "Sin evidencia"], filas))

    # ---- 2. formato ----------------------------------------------------------------------
    L.append("## 2. Formato: qué taxonomía usan los valores declarados\n")
    L.append("Antes de juzgar el contenido, el continente: un valor cuenta como **estándar** si todos sus códigos "
             "existen en IAB 1.0 (`IAB1-5`) o en 2.2/3.0 (`333`); **no_estandar** si tiene la forma de un código "
             "pero no existe (`IAB1-22`, `IAB-7`, `IAB1-6-3`); **texto_libre** si no es un código (`sports`, "
             "`Live`, `Entertainment`). Los códigos 1000+ de 2.2 (`1070` = Content Language > Spanish, `1004` = "
             "Content Channel > Game) existen pero **no son categorías de contenido**: se reportan como metadato.\n")
    claves = sorted({k for n in nombres for k in D[n]["correctitud"]["formato"]})
    filas = [[f"`{k}`"] + [celda_fr(D[n]["correctitud"]["formato"], k) for n in nombres] for k in claves]
    L.append(tabla(["Formato"] + nombres, filas))
    claves = sorted({k for n in nombres for k in D[n]["correctitud"]["taxonomia"]})
    filas = [[f"`{k}`"] + [celda_fr(D[n]["correctitud"]["taxonomia"], k) for n in nombres] for k in claves]
    L.append("Por taxonomía (un valor puede mezclar varias):\n")
    L.append(tabla(["Taxonomía"] + nombres, filas))
    c0 = D[nombres[0]]["correctitud"]
    L.append(f"Los 20 valores más frecuentes en **{nombres[0]}** (de {fmt_n(resumen_veredicto(c0)['llenas'])} filas con categoría):\n")
    filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_p(v["pct_filas"]), fmt_p(v["pct_requests"])]
             for k, v in list(c0["valores_top"].items())[:20]]
    L.append(tabla(["Valor", "Filas", "% filas", "% requests"], filas))

    # ---- 3. veredicto --------------------------------------------------------------------
    L.append("## 3. Veredicto\n")
    L.append("Sobre las filas **evaluables**: `coincide` = algún código declarado acierta en lo más fino que declara "
             "(la forma o el género) y ninguno contradice; `compatible` = no contradice pero es genérico (solo "
             "`[IAB1]`, o las dos formas a la vez `[IAB1-5, IAB1-7]`); `contradice` = al menos un código choca con "
             "la evidencia.\n")
    filas = []
    for n in nombres:
        rv = resumen_veredicto(D[n]["correctitud"])
        filas.append([f"**{n}**", f"{fmt_n(rv['evaluables'])} ({fmt_p(rv['pct_evaluables'])} de las llenas)",
                      f"{fmt_p(rv['pct_coincide'])} · req {fmt_p(rv['pct_coincide_req'])}",
                      f"{fmt_p(rv['pct_compatible'])} · req {fmt_p(rv['pct_compatible_req'])}",
                      f"**{fmt_p(rv['pct_contradice'])}** · req {fmt_p(rv['pct_contradice_req'])}",
                      fmt_n(rv["contradice"])])
    L.append(tabla(["Dataset", "Evaluables", "coincide", "compatible", "contradice", "Filas que contradicen"], filas))
    L.append("Desglosado por tipo de evidencia (% de las filas con esa evidencia):\n")
    filas = []
    for n in nombres:
        rv = resumen_veredicto(D[n]["correctitud"])
        for e in EVIDENCIAS[:2]:
            filas.append([f"**{n}** · {e}", fmt_p(rv[f"pct_{e}_coincide"]), fmt_p(rv[f"pct_{e}_compatible"]),
                          f"**{fmt_p(rv[f'pct_{e}_contradice'])}**",
                          fmt_n(get(D[n]["correctitud"]["veredicto"], f"{e}|contradice", "filas", default=0))])
    L.append(tabla(["Dataset · evidencia", "coincide", "compatible", "contradice", "Filas"], filas))

    L.append("### 3.1 En qué contradicen\n")
    L.append("`vertical` = la categoría nombra otra vertical (Noticias, Deportes, Tecnología…) para un contenido "
             "que la evidencia dice que es ficción de entretenimiento, o una vertical fuerte distinta de la que dice "
             "el género; `forma` = dice Películas y es serie (o al revés); `genero` = el código nombra un género "
             "(Drama Movies, Horror…) que la evidencia no trae; `sub` = el código nombra un deporte concreto "
             "(`IAB17-1` Auto Racing) y el género declarado nombra otro (Soccer). Un programa de no ficción (documental, reality) "
             "**no** se contradice por vertical temática: IMDb no registra de qué trata.\n")
    claves = sorted({k for n in nombres for k in D[n]["correctitud"]["contradice_tipo"]})
    filas = [[f"`{k}`"] + [celda_fr(D[n]["correctitud"]["contradice_tipo"], k) for n in nombres] for k in claves]
    L.append(tabla(["Evidencia · tipo de choque"] + nombres, filas))

    L.append("### 3.2 ¿Es error del vendedor o del match? (solo evidencia externa)\n")
    L.append("Un match IMDb de confianza B acierta ~75%: parte de las contradicciones externas son matches "
             "equivocados. Para separarlas, se mira si el `contentGenre` declarado coincide con los géneros IMDb "
             "del match: si coincide, el match es creíble y la categoría contradictoria es muy probablemente un "
             "error del vendedor; si tampoco coincide, sospechar del match.\n")
    claves = ["coincide", "no_coincide", "sin_genero_declarado", "no_comparable"]
    filas = []
    for k in claves:
        fila = [f"género declarado `{k}` con IMDb"]
        for n in nombres:
            b = D[n]["correctitud"]["contradice_externa_por_genero_vs_imdb"]
            tot = sum(x["filas"] for x in b.values()) or 1
            x = b.get(k, {"filas": 0})
            fila.append(f"{fmt_n(x['filas'])} ({100.0 * x['filas'] / tot:.1f}%)")
        filas.append(fila)
    L.append(tabla(["Contradicciones externas según…"] + nombres, filas))

    # ---- 4. por pais / publisher / origen ---------------------------------------------------
    L.append("## 4. Quién acierta y quién no\n")

    def bloque_tabla(titulo, bloque, claves_orden=None):
        if not bloque:
            return
        L.append(f"### {titulo}\n")
        filas = []
        for k in (claves_orden or bloque.keys()):
            b = bloque.get(k)
            if not b:
                continue
            d = b["desglose"]
            tot = b["filas"]
            ev = sum(x["filas"] for kk, x in d.items() if not kk.endswith("no_evaluable"))
            co = sum(x["filas"] for kk, x in d.items() if kk.endswith("|coincide"))
            cp = sum(x["filas"] for kk, x in d.items() if kk.endswith("|compatible"))
            ct = sum(x["filas"] for kk, x in d.items() if kk.endswith("|contradice"))
            ct_r = sum(x["requests"] for kk, x in d.items() if kk.endswith("|contradice"))
            filas.append([k, fmt_n(tot), fmt_p(100.0 * ev / tot if tot else 0),
                          fmt_p(100.0 * co / ev if ev else 0), fmt_p(100.0 * cp / ev if ev else 0),
                          f"**{fmt_p(100.0 * ct / ev if ev else 0)}**", fmt_n(ct),
                          fmt_p(100.0 * ct_r / b["requests"] if b["requests"] else 0)])
        L.append(tabla(["", "Filas con categoría", "% evaluables", "coincide (de evaluables)",
                        "compatible", "contradice", "Filas que contradicen", "% req del grupo que contradice"], filas))

    for n in nombres:
        c = D[n]["correctitud"]
        bloque_tabla(f"Por país — {n}", c["por_pais"], D[n]["meta"]["paises"])
        bloque_tabla(f"Por publisher (top {len(D[n]['meta']['publishers_top'])} por filas) — {n}",
                     c["por_publisher"], D[n]["meta"]["publishers_top"])
        if c.get("por_origen"):
            L.append("En el relleno, `original` son las filas que ya traían categoría (las mismas del consolidado); "
                     "las demás son las que el pipeline de relleno llenó y de dónde las sacó.\n")
            bloque_tabla(f"Por origen del valor — {n}", c["por_origen"])

    # ---- 5. intra-titulo -------------------------------------------------------------------
    L.append("## 5. Consistencia entre rutas: el mismo título con categorías distintas\n")
    L.append("No requiere fuentes externas: si el mismo título (normalizado) llega con `[IAB12]` por una ruta y "
             "`[IAB1]` por otra, al menos una está mal. Un título tiene conflicto de **vertical** cuando sus filas "
             "declaran verticales distintas, y de **forma** cuando unas dicen solo Películas y otras solo "
             "Televisión. Las **filas minoritarias** son las que declaran algo distinto de lo que declara la "
             "mayoría de las filas de ese título: son las candidatas a estar mal (sin decidir aquí quién tiene "
             "razón).\n")
    filas = []
    for n in nombres:
        ci = D[n]["correctitud"]["conflicto_intra_titulo"]
        fm = ci["filas_minoritarias"]
        filas.append([f"**{n}**", fmt_n(ci["titulos_con_categoria"]),
                      f"{fmt_n(ci['titulos_conflicto_vertical'])} ({100.0 * ci['titulos_conflicto_vertical'] / max(ci['titulos_con_categoria'], 1):.1f}%)",
                      fmt_n(ci["filas_en_titulos_con_conflicto"]["vertical"]),
                      celda_fr(fm, "vertical"),
                      f"{fmt_n(ci['titulos_conflicto_forma'])} ({100.0 * ci['titulos_conflicto_forma'] / max(ci['titulos_con_categoria'], 1):.1f}%)",
                      fmt_n(ci["filas_en_titulos_con_conflicto"]["forma"]),
                      celda_fr(fm, "forma"), celda_fr(fm, "vertical;forma")])
    L.append(tabla(["Dataset", "Títulos con categoría", "Títulos con conflicto de vertical", "Filas en esos títulos",
                    "Filas minoritarias de vertical (de las llenas)", "Títulos con conflicto de forma",
                    "Filas en esos títulos", "Filas minoritarias de forma", "…ambas"], filas))
    ci0 = D[nombres[0]]["correctitud"]["conflicto_intra_titulo"]
    if ci0["ejemplos_vertical"]:
        L.append(f"Ejemplos de conflicto de vertical en **{nombres[0]}** (título → filas por vertical):\n")
        L.append("\n".join(f"- `{k}` → " + ", ".join(f"{vv} ×{cc}" for vv, cc in sorted(v.items(), key=lambda x: -x[1]))
                           for k, v in list(ci0["ejemplos_vertical"].items())[:12]) + "\n")
    if ci0["ejemplos_forma"]:
        L.append("Ejemplos de conflicto de forma:\n")
        L.append("\n".join(f"- `{k}` → " + ", ".join(f"{vv} ×{cc}" for vv, cc in sorted(v.items(), key=lambda x: -x[1]))
                           for k, v in list(ci0["ejemplos_forma"].items())[:12]) + "\n")

    # ---- 6. top contradicciones -----------------------------------------------------------
    L.append("## 6. Las contradicciones con más tráfico\n")
    for n in nombres:
        top = D[n]["correctitud"]["contradicciones_top_titulos"]
        if not top:
            continue
        L.append(f"**{n}** — un título por fila, ordenados por requests de las filas que contradicen "
                 f"(muestra completa en `validacion-{n}-muestra-contradicciones.csv`):\n")
        filas = []
        for t in top[:25]:
            filas.append([f"`{(t['titulo'] or '')[:40]}`", f"`{t['declarado']}`", t["esperado"],
                          f"{t['imdb']} {(t['imdb_titulo'] or '')[:30]}".strip(), t["genero_declarado"][:25],
                          t["genero_vs_imdb"], t["detalle"], t["publisher"][:30], fmt_n(t["filas"]), fmt_n(t["requests"])])
        L.append(tabla(["Título", "Declarado", "Esperado (forma/géneros)", "IMDb", "Género declarado",
                        "Género vs IMDb", "Choque", "Publisher (ej.)", "Filas (todas las rutas)", "Requests"], filas,
                       ["---"] * 8 + ["---:", "---:"]))
        L.append(f"Pares declarado → esperado más frecuentes ({n}):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_n(v["requests"])]
                 for k, v in list(D[n]["correctitud"]["contradicciones_top_pares"].items())[:15]]
        L.append(tabla(["Declarado → esperado", "Filas", "Requests"], filas))

    # ---- 7. contentGenre --------------------------------------------------------------------
    L.append("## 7. De paso: contentGenre contra IMDb\n")
    L.append("La misma evidencia externa permite validar el género declarado (que es el insumo del relleno de "
             "categoría). Sobre las filas con match externo y género declarado: `coincide` = al menos un género "
             "declarado está entre los de IMDb/Wikidata; `no_coincide` = ninguno.\n")
    filas = []
    for n in nombres:
        g = D[n]["correctitud"]["genero_vs_imdb"]["total"]
        tot = sum(x["filas"] for x in g.values()) or 1
        comp = g.get("coincide", {"filas": 0})["filas"] + g.get("no_coincide", {"filas": 0})["filas"]
        filas.append([f"**{n}**", fmt_n(tot), fmt_n(comp),
                      fmt_p(100.0 * g.get("coincide", {"filas": 0})["filas"] / max(comp, 1)),
                      fmt_p(100.0 * g.get("no_coincide", {"filas": 0})["filas"] / max(comp, 1)),
                      fmt_p(100.0 * g.get("sin_genero_declarado", {"filas": 0})["filas"] / tot)])
    L.append(tabla(["Dataset", "Filas con match externo", "…y con género declarado", "coincide (de las comparables)",
                    "no_coincide", "sin género declarado (de las con match)"], filas))
    gp = D[nombres[0]]["correctitud"]["genero_vs_imdb"]["por_publisher"]
    if gp:
        filas = []
        for p, g in gp.items():
            comp = g.get("coincide", {"filas": 0})["filas"] + g.get("no_coincide", {"filas": 0})["filas"]
            filas.append([p, fmt_n(comp), fmt_p(100.0 * g.get("coincide", {"filas": 0})["filas"] / max(comp, 1)),
                          fmt_p(100.0 * g.get("no_coincide", {"filas": 0})["filas"] / max(comp, 1))])
        L.append(f"Por publisher ({nombres[0]}):\n")
        L.append(tabla(["Publisher", "Filas comparables", "coincide", "no_coincide"], filas))

    # ---- 8. limites ---------------------------------------------------------------------------
    L.append("## 8. Límites del método\n")
    L.append("- **La evidencia externa cubre lo que tiene título real y match**: el catálogo FAST con títulos "
             "placeholder (`epg`, `roku`) o de canal no se puede juzgar contra IMDb; para esas filas solo queda la "
             "evidencia interna o la consistencia entre rutas.\n"
             "- **Un match B se equivoca 1 de cada 4 veces.** Por eso las contradicciones externas se parten según si "
             "el género declarado respalda el match (§3.2); la cifra defendible es la de \"género coincide\". Con "
             "`--confianza-min A` el pipeline se vuelve más estricto (menos cobertura, más precisión).\n"
             "- **IMDb no dice de qué trata la no ficción**: un documental etiquetado Viajes o Tecnología queda "
             "`compatible`, no `coincide`. Para validar verticales temáticas haría falta TMDB (keywords) o Wikidata "
             "P921 (main subject), no incluidos en esta corrida.\n"
             "- **El género es opinable**: IMDb trae hasta 3 géneros y Wikidata los suyos; el choque de `genero` se "
             "declara solo si el código nombra un género que ninguna de las dos fuentes trae. Es el choque más "
             "débil de los tres y por eso se reporta aparte.\n")
    open(os.path.join(out_dir, "reporte-correctitud.md"), "w", encoding="utf-8").write("\n".join(L))


# ----------------------------------------------------------------------------
def reporte_completitud(datasets, out_dir):
    L = []
    nombres = list(datasets.keys())
    D = datasets
    m0 = D[nombres[0]]["meta"]
    L.append("# Reporte — Completitud de contentCategory: ¿se puede poner una categoría IAB más fina?\n")
    L.append("**Fuentes:** " + "; ".join(f"`{D[n]['meta']['archivo']}` ({fmt_n(D[n]['meta']['filas'])} filas, "
                                        f"columna `{D[n]['meta']['columna']}`)" for n in nombres) + ".  ")
    L.append(f"**Generado con:** `scripts/validar_categorias.py` + `scripts/generar_reporte_validacion.py`. "
             f"Corrida del {m0['fecha']}. Propuestas en IAB Content Taxonomy **2.2** (la última con géneros bajo "
             f"Movies/Television y ~70 deportes) y su equivalente en **1.0** (la que usa la mayoría de las filas llenas).\n")
    L.append("**Convención:** aquí los % son **% del total de filas** del dataset (llenas y vacías), salvo en las "
             "tablas por grupo, donde son % de las filas del grupo. El **nivel** de granularidad cuenta atributos "
             "conocidos: 0 = nada; 1 = solo vertical (`[IAB1]`, `[IAB12]`, `[324]`); 2 = vertical + forma "
             "(`[IAB1-5]` Películas, `[640]` Televisión) o vertical + sub-deporte (`[IAB17-44]` Soccer); "
             "3 = vertical + forma + género (`[333]` Drama Movies, `[651]` Reality TV). Es comparable entre "
             "taxonomías porque mide información, no profundidad del árbol.\n")
    L.append("---\n")

    # ---- 1. estado actual ----------------------------------------------------------------
    L.append("## 1. Punto de partida\n")
    L.append("`vacia` = sin categoría útil; `contradicha` = trae categoría pero la evidencia la contradice "
             "(ver reporte de correctitud); `llena` = trae categoría y no está contradicha.\n")
    filas = []
    for n in nombres:
        e = D[n]["completitud"]["estado"]
        filas.append([f"**{n}**", fmt_n(D[n]["meta"]["filas"]), celda_fr(e, "vacia"), celda_fr(e, "llena"), celda_fr(e, "contradicha")])
    L.append(tabla(["Dataset", "Filas", "vacia", "llena", "contradicha"], filas))
    L.append("Nivel actual de las filas llenas o contradichas (% del total de filas):\n")
    claves = sorted({k for n in nombres for k in D[n]["completitud"]["nivel_actual"]})
    filas = [[f"`{k}`"] + [celda_fr(D[n]["completitud"]["nivel_actual"], k) for n in nombres] for k in claves]
    L.append(tabla(["Estado · nivel actual"] + nombres, filas))

    # ---- 2. propuesta ------------------------------------------------------------------------
    L.append("## 2. Hasta dónde llega la evidencia\n")
    L.append("Para cada fila se calcula la categoría más fina que la evidencia permite. La **evidencia** es "
             "`externa` (tipo y géneros IMDb/Wikidata del título), `interna` (el género declarado en la fila), "
             "`serie` (solo `contentSeries` con nombre real → es TV) o `ninguna`. La **forma** (película/TV) sale, "
             "en orden, de: tipo IMDb > `contentSeries` real > lo ya declarado > género que la implica (telenovela, "
             "reality, talk show → TV).\n")
    claves = sorted({k for n in nombres for k in D[n]["completitud"]["evidencia"]})
    filas = [[f"`{k}`"] + [celda_fr(D[n]["completitud"]["evidencia"], k) for n in nombres] for k in claves]
    L.append("Evidencia disponible por fila:\n")
    L.append(tabla(["Evidencia"] + nombres, filas))
    claves = sorted({k for n in nombres for k in D[n]["completitud"]["forma_origen"]})
    filas = [[f"`{k}`"] + [celda_fr(D[n]["completitud"]["forma_origen"], k) for n in nombres] for k in claves]
    L.append("De dónde sale la forma (película/TV):\n")
    L.append(tabla(["Origen de la forma"] + nombres, filas))
    L.append("Nivel propuesto (% del total de filas). En las filas ya llenas que no se contradicen y cuyo nivel "
             "actual iguala o supera al alcanzable, se **mantiene** lo declarado (el nivel propuesto es el actual):\n")
    claves = sorted({k for n in nombres for k in D[n]["completitud"]["nivel_propuesto"]})
    filas = [[f"nivel `{k}`"] + [celda_fr(D[n]["completitud"]["nivel_propuesto"], k) for n in nombres] for k in claves]
    L.append(tabla(["Nivel propuesto"] + nombres, filas))

    # ---- 3. mejora -------------------------------------------------------------------------------
    L.append("## 3. Qué cambia fila a fila\n")
    L.append("`rellena` = estaba vacía y hay propuesta; `sube` = estaba llena y la propuesta es más fina; "
             "`mantiene` = estaba llena y ya es igual o más fina que lo alcanzable; `corrige` = estaba contradicha y "
             "hay propuesta que la reemplaza; `sin_propuesta` = vacía sin evidencia.\n")
    claves = [k for k in ["rellena", "sube", "mantiene", "corrige", "contradicha_sin_propuesta", "sin_propuesta"]
              if any(get(D[n]["completitud"]["mejora"], k, "pct_filas", default=0) >= 0.05 for n in nombres)]
    filas = [[f"`{k}`"] + [celda_fr(D[n]["completitud"]["mejora"], k) for n in nombres] for k in claves]
    L.append(tabla(["Mejora"] + nombres, filas))
    L.append("Matriz estado actual · nivel actual → nivel propuesto (% del total de filas; solo celdas con ≥ 0.5%):\n")
    for n in nombres:
        mt = D[n]["completitud"]["matriz"]
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_p(v["pct_filas"]), fmt_p(v["pct_requests"])]
                 for k, v in mt.items() if v["pct_filas"] >= 0.5]
        L.append(f"**{n}**:\n")
        L.append(tabla(["estado · actual → propuesto", "Filas", "% filas", "% requests"], filas))

    # ---- 4. por grupo --------------------------------------------------------------------------
    L.append("## 4. Por país, publisher y origen\n")
    L.append("Cada fila de estas tablas es un grupo; los % son sobre las filas del grupo.\n")

    def tabla_grupo(titulo, bloque, orden=None):
        if not bloque:
            return
        L.append(f"### {titulo}\n")
        filas = []
        for k in (orden or bloque.keys()):
            b = bloque.get(k)
            if not b:
                continue
            tot = sum(x["filas"] for x in b.values())
            filas.append([k, fmt_n(tot)] + [fmt_p(100.0 * b.get(c, {"filas": 0})["filas"] / tot if tot else 0)
                                             for c in claves])
        L.append(tabla(["", "Filas"] + [f"`{c}`" for c in claves], filas))

    for n in nombres:
        cp = D[n]["completitud"]
        tabla_grupo(f"Por país — {n}", cp["por_pais"], D[n]["meta"]["paises"])
        tabla_grupo(f"Por publisher — {n}", cp["por_publisher"], D[n]["meta"]["publishers_top"])
        if cp.get("por_origen"):
            L.append("En el relleno, el origen dice de dónde salió el valor actual de la categoría; interesa sobre "
                     "todo `derivado_genero` y `app_default`, que llenan con `[IAB1]` genérico (nivel 1) y son "
                     "los que más pueden subir.\n")
            tabla_grupo(f"Por origen del valor actual — {n}", cp["por_origen"])

    # ---- 5. propuestas ------------------------------------------------------------------------
    L.append("## 5. Qué categorías se propondrían\n")
    for n in nombres:
        L.append(f"**{n}** — las 25 propuestas más frecuentes (IAB 2.2; % del total de filas):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_p(v["pct_filas"]), fmt_p(v["pct_requests"])]
                 for k, v in list(D[n]["completitud"]["propuestas_top"].items())[:25]]
        L.append(tabla(["Propuesta (ruta 2.2)", "Filas", "% filas", "% requests"], filas))
    L.append(f"Reglas que generaron las propuestas en **{nombres[0]}** (evidencia · vertical · forma · origen de la forma):\n")
    filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_p(v["pct_filas"])]
             for k, v in list(D[nombres[0]]["completitud"]["reglas"].items())[:20]]
    L.append(tabla(["Regla", "Filas", "% filas"], filas))

    # ---- 6. limites -------------------------------------------------------------------------------
    L.append("## 6. Qué haría falta para llegar más lejos\n")
    L.append("- **Las filas sin título real** (placeholders `epg`/`roku`, canales, macros) solo pueden subir por "
             "el género declarado: a nivel 2 (par película+TV del género) o 1. La forma real de esas filas solo la "
             "sabe el vendedor.\n"
             "- **Sub-deporte**: se detecta por palabra en el género o el título (`soccer`, `boxeo`, `NBA`…). "
             "\"Football\" se mapea a fútbol americano como manda IAB 1.0 (`IAB17-12`); si el vendedor lo usa como "
             "fútbol, corregirlo aquí es una decisión de negocio, no de dato.\n"
             "- **Verticales temáticas de la no ficción** (viajes, cocina, tecnología): no salen de IMDb. Se "
             "conservan cuando el vendedor las declara; para proponerlas desde cero haría falta TMDB keywords o "
             "Wikidata P921.\n"
             "- **IAB 3.0** separa forma y género en ramas distintas (`Entertainment > Movies` + `Genres > Drama`); "
             "la propuesta 2.2 se traduce directo (`333` → `324` + `647`) si el comprador la pide.\n")
    open(os.path.join(out_dir, "reporte-completitud.md"), "w", encoding="utf-8").write("\n".join(L))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out_dir = sys.argv[1]
    datasets = OrderedDict()
    for arg in sys.argv[2:]:
        nombre, path = arg.split("=", 1)
        datasets[nombre] = json.load(open(path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    reporte_correctitud(datasets, out_dir)
    reporte_completitud(datasets, out_dir)
    print(f"escritos {out_dir}/reporte-correctitud.md y reporte-completitud.md")


if __name__ == "__main__":
    main()
