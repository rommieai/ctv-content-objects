# -*- coding: utf-8 -*-
"""Genera los reportes markdown de validacion de contentCategory a partir de los JSON de
validar_categorias.py (uno o varios datasets lado a lado).

    python scripts/generar_reporte_validacion.py reportes/NN \
        consolidado=reportes/NN/validacion-consolidado.json \
        relleno=reportes/NN/validacion-relleno.json

Escribe en el directorio de salida:
    reporte-correctitud.md    parte 1: las filas con categoria, ¿la traen bien?
    reporte-completitud.md    parte 2: ¿se puede poner una categoria IAB mas fina?

Todo el texto con numeros sale del JSON. Las claves tecnicas del JSON (coincide,
compatible, rellena, sube...) se muestran con una etiqueta en lenguaje claro y la
clave entre parentesis, para poder cruzarlas con los CSV fila a fila.
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


def celda_fr(bloque, clave):
    """'12,345 filas (12.3%) · 4.5% req'"""
    b = get(bloque, clave)
    if not b:
        return "—"
    return f"{fmt_n(b['filas'])} filas ({fmt_p(b['pct_filas'])}) · {fmt_p(b['pct_requests'])} req"


# ---------------------------------------------------------------------------
# Etiquetas en lenguaje claro para las claves tecnicas del JSON
# ---------------------------------------------------------------------------
DATASET = {"consolidado": "Tal como llega (consolidado)", "relleno": "Después del relleno"}
VEREDICTO = {"coincide": "Correcta y precisa", "compatible": "Correcta pero genérica",
             "contradice": "Incorrecta", "no_evaluable": "No se pudo evaluar"}
EVIDENCIA = {"externa": "IMDb / Wikidata", "interna": "Solo el género de la fila",
             "ninguna": "Sin evidencia", "serie": "Solo el nombre de serie"}
FORMATO = {"estandar": "Código IAB válido", "no_estandar": "Código con forma IAB pero inexistente",
           "texto_libre": "Texto libre (no es un código)", "metadato": "Metadato, no categoría"}
TAXONOMIA = {"1.0": "IAB 1.0", "2.2": "IAB 2.2 / 3.0", "ninguna": "ninguna"}
CHOQUE = {"vertical": "la vertical (Noticias, Deportes… para ficción)", "forma": "película vs serie",
          "genero": "el género", "sub": "el sub-deporte"}
GEN_VS_IMDB = {"coincide": "coincide con IMDb → el match es creíble, la categoría es error del vendedor",
               "no_coincide": "no coincide con IMDb → sospechar del match",
               "sin_genero_declarado": "la fila no declara género",
               "no_comparable": "el género declarado no es comparable"}
ORIGEN = {"original": "Venía del vendedor", "intra_titulo": "Copiado de otra ruta del mismo título",
          "app_default": "Valor habitual de la app", "imdb": "IMDb", "wikidata": "Wikidata", "tvmaze": "TVMaze",
          "derivado_genero": "Derivado del género", "derivado_tipo": "Derivado del tipo IMDb (película / serie)",
          "app_semantica": "Semántica de la app"}
ESTADO = {"vacia": "Sin categoría", "llena": "Con categoría (correcta o genérica)", "contradicha": "Con categoría incorrecta"}
NIVEL = {"0": "Nivel 0 · nada", "1": "Nivel 1 · solo la vertical", "2": "Nivel 2 · vertical + película/TV (o deporte)",
         "3": "Nivel 3 · vertical + película/TV + género"}
MEJORA = {"rellena": "Se puede llenar (estaba vacía)", "sube": "Se puede afinar (estaba llena)",
          "mantiene": "Se queda igual (ya está bien)", "corrige": "Se puede corregir (estaba incorrecta)",
          "sin_propuesta": "Sin propuesta (vacía y sin evidencia)",
          "contradicha_sin_propuesta": "Incorrecta y sin reemplazo posible"}
FORMA_ORIGEN = {"imdb": "El tipo de IMDb", "contentSeries": "Trae nombre de serie → TV", "declarado": "Ya lo decía la categoría",
                "genero": "Lo implica el género (telenovela, reality → TV)", "titulo": "El título trae temporada/episodio → TV",
                "sin_forma": "No se sabe"}
VERTICAL = {"entretenimiento": "Entretenimiento", "deportes": "Deportes", "musica": "Música", "noticias": "Noticias",
            "viajes": "Viajes", "videojuegos": "Videojuegos", "-": "—"}
FORMA = {"pelicula": "película", "tv": "TV", "-": "sin forma"}


def lab(dic, k):
    """Etiqueta clara + clave tecnica entre parentesis."""
    return f"{dic[k]} (`{k}`)" if k in dic else f"`{k}`"


def lab_combo(dic, k, sep=";"):
    if k in dic:
        return lab(dic, k)
    partes = k.split(sep)
    if all(p in dic for p in partes):
        return " + ".join(dic[p] for p in partes) + f" (`{k}`)"
    return f"`{k}`"


def ds(n):
    return f"**{DATASET.get(n, n)}**"


VEREDICTOS = ["coincide", "compatible", "contradice", "no_evaluable"]
EVIDENCIAS = ["externa", "interna", "ninguna"]


def resumen_veredicto(c):
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


def glosario_comun(D, nombres):
    m0 = D[nombres[0]]["meta"]
    L = ["## Cómo leer este reporte\n"]
    L.append("- **Fila**: cada fila del inventario es una combinación de país, publisher, app y metadata de contenido, no un programa ni un evento. "
             "**Requests** son las solicitudes de anuncio que trae esa fila; por eso cada cifra se da en filas y en requests.")
    if len(nombres) > 1:
        L.append(f"- **{DATASET.get(nombres[0], nombres[0])}** es el inventario tal como lo mandan los vendedores. "
                 f"**{DATASET.get(nombres[1], nombres[1])}** es el mismo inventario después de que el pipeline de relleno "
                 "(`enriquecer_externo.py`) completó las categorías vacías; se validan los dos para saber si el relleno acierta.")
    L.append("- **Categoría IAB**: el código de `contentCategory` (por ejemplo `[IAB1-5]` = Entretenimiento > Películas). "
             "Una categoría afirma hasta tres cosas: la **vertical** (entretenimiento, noticias, deportes…), la **forma** "
             "(película o televisión) y el **género** (drama, terror…).")
    L.append(f"- **Evidencia**: contra qué se compara la categoría. *IMDb / Wikidata*: el título de la fila se encontró en esas bases "
             f"(un **match**), que dicen si es película o serie y qué géneros tiene; cubre {fmt_n(m0['filas_con_match_externo'])} filas "
             f"({fmt_p(m0['pct_filas_con_match_externo'])} del total). *Solo el género de la fila*: no hay match, pero el `contentGenre` "
             "de la misma fila permite juzgar (un drama no es Noticias). *Sin evidencia*: no hay contra qué comparar.")
    L.append(f"- **Confianza del match**: A = el título coincide sin ambigüedad; B = coincide pero podría ser otro título homónimo "
             f"(acierta ~3 de cada 4). Se usan matches de confianza {m0['confianza_min']} o mejor.")
    L.append("- **Formato de las celdas**: `12,345 filas (12.3%) · 4.5% req` = cantidad de filas, % de filas y % de requests sobre la base que indica cada tabla.")
    return L


# ----------------------------------------------------------------------------
def reporte_correctitud(datasets, out_dir):
    L = []
    nombres = list(datasets.keys())
    D = datasets
    m0 = D[nombres[0]]["meta"]
    cab = [DATASET.get(n, n) for n in nombres]
    L.append("# contentCategory, parte 1: las filas que traen categoría, ¿la traen bien?\n")
    L.append("**Fuentes:** " + "; ".join(f"`{D[n]['meta']['archivo']}` ({fmt_n(D[n]['meta']['filas'])} filas, "
                                        f"columna `{D[n]['meta']['columna']}`)" for n in nombres) + ".  ")
    L.append(f"**Generado con:** `scripts/validar_categorias.py` + `scripts/generar_reporte_validacion.py`. Corrida del {m0['fecha']}. "
             f"Evidencia externa: IMDb (match de confianza ≥ {m0['confianza_min']}) y géneros de Wikidata, desde "
             f"`cache-enriquecimiento/titulos.json` ({fmt_n(m0['titulos_en_cache'])} títulos); taxonomías oficiales de IAB Tech Lab: "
             f"1.0 ({m0['taxonomias']['1.0']} códigos), 2.2 ({m0['taxonomias']['2.2']}) y 3.0 ({m0['taxonomias']['3.0']}).\n")
    L += glosario_comun(D, nombres)
    L.append("")
    L.append("**Base de los porcentajes en este reporte:** salvo que la tabla diga otra cosa, los % son sobre las **filas que traen categoría** "
             "(no sobre todo el inventario). \"Evaluables\" son las filas con categoría que además tienen evidencia para juzgarla.\n")
    L.append("---\n")

    # ---- 1. universo ------------------------------------------------------------------
    L.append("## 1. Cuántas filas traen categoría y cuántas se pudieron evaluar\n")
    filas = []
    for n in nombres:
        m, c = D[n]["meta"], D[n]["correctitud"]
        filas.append([ds(n), fmt_n(m["filas"]),
                      f"{fmt_n(m['filas_con_categoria'])} ({fmt_p(m['pct_filas_con_categoria'])})",
                      fmt_p(m["pct_requests_con_categoria"]),
                      f"{fmt_n(m['filas_con_match_externo'])} ({fmt_p(m['pct_filas_con_match_externo'])})",
                      celda_fr(c["evidencia"], "externa"), celda_fr(c["evidencia"], "interna"),
                      celda_fr(c["evidencia"], "ninguna")])
    L.append(tabla(["Dataset", "Filas totales", "Filas con categoría (% del total)", "% de requests con categoría",
                    "Filas cuyo título está en IMDb/Wikidata (% del total)",
                    "Con categoría y evidencia IMDb/Wikidata (% de las que traen categoría)",
                    "Con categoría y solo el género como evidencia", "Con categoría y sin evidencia"], filas))
    L.append("*Cómo leerla: las tres últimas columnas reparten las filas con categoría según qué se puede usar para juzgarla. "
             "Las de la última columna quedan como \"no se pudo evaluar\" en el resto del reporte.*\n")

    # ---- 2. formato -------------------------------------------------------------------
    L.append("## 2. Cómo vienen escritos los valores\n")
    L.append("Antes de juzgar si la categoría es correcta se mira si el valor es un código válido. Un valor es un **código IAB válido** si "
             "todos sus códigos existen en IAB 1.0 (`IAB1-5`) o en 2.2/3.0 (`333`); es un **código inexistente** si tiene forma de código pero "
             "no está en ninguna taxonomía (`IAB1-22`, `IAB-7`); es **texto libre** si no es un código (`sports`, `Live`, `Entertainment`). "
             "Los códigos 1000+ de IAB 2.2 (`1070` = idioma español, `1004` = canal de juegos) existen pero no describen el contenido: se cuentan como **metadato**.\n")
    claves = sorted({k for n in nombres for k in D[n]["correctitud"]["formato"]})
    filas = [[lab_combo(FORMATO, k)] + [celda_fr(D[n]["correctitud"]["formato"], k) for n in nombres] for k in claves]
    L.append(tabla(["Tipo de valor"] + cab, filas))
    claves = sorted({k for n in nombres for k in D[n]["correctitud"]["taxonomia"]})
    filas = [[lab_combo(TAXONOMIA, k)] + [celda_fr(D[n]["correctitud"]["taxonomia"], k) for n in nombres] for k in claves]
    L.append("Qué taxonomía IAB usan (un valor puede mezclar varias):\n")
    L.append(tabla(["Taxonomía"] + cab, filas))
    c0 = D[nombres[0]]["correctitud"]
    L.append(f"Los 20 valores más frecuentes en {ds(nombres[0])} (sobre {fmt_n(resumen_veredicto(c0)['llenas'])} filas con categoría):\n")
    filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_p(v["pct_filas"]), fmt_p(v["pct_requests"])]
             for k, v in list(c0["valores_top"].items())[:20]]
    L.append(tabla(["Valor tal como viene", "Filas", "% de filas con categoría", "% de requests con categoría"], filas))

    # ---- 3. veredicto -----------------------------------------------------------------
    L.append("## 3. Veredicto: ¿la categoría es correcta?\n")
    L.append("Sobre las filas **evaluables**, cada una recibe un veredicto:\n")
    L.append("- **Correcta y precisa** (`coincide`): algún código acierta en lo más fino que declara (la forma o el género) y ninguno contradice la evidencia.\n"
             "- **Correcta pero genérica** (`compatible`): no contradice nada, pero solo dice la vertical (`[IAB1]`) o las dos formas a la vez (`[IAB1-5, IAB1-7]`, \"película o TV\").\n"
             "- **Incorrecta** (`contradice`): al menos un código choca con la evidencia.\n")
    filas = []
    for n in nombres:
        rv = resumen_veredicto(D[n]["correctitud"])
        filas.append([ds(n), f"{fmt_n(rv['evaluables'])} ({fmt_p(rv['pct_evaluables'])} de las que traen categoría)",
                      f"{fmt_p(rv['pct_coincide'])} · {fmt_p(rv['pct_coincide_req'])} req",
                      f"{fmt_p(rv['pct_compatible'])} · {fmt_p(rv['pct_compatible_req'])} req",
                      f"**{fmt_p(rv['pct_contradice'])}** · {fmt_p(rv['pct_contradice_req'])} req",
                      fmt_n(rv["contradice"])])
    L.append(tabla(["Dataset", "Filas evaluables", "Correcta y precisa", "Correcta pero genérica", "Incorrecta", "Filas incorrectas"], filas))
    L.append("*Los % de las tres columnas de veredicto son sobre las filas evaluables (filas y requests).*\n")
    L.append("Lo mismo separado según la evidencia con que se juzgó (% de las filas con esa evidencia):\n")
    filas = []
    for n in nombres:
        rv = resumen_veredicto(D[n]["correctitud"])
        for e in EVIDENCIAS[:2]:
            filas.append([f"{ds(n)} · {EVIDENCIA[e]}", fmt_p(rv[f"pct_{e}_coincide"]), fmt_p(rv[f"pct_{e}_compatible"]),
                          f"**{fmt_p(rv[f'pct_{e}_contradice'])}**",
                          fmt_n(get(D[n]["correctitud"]["veredicto"], f"{e}|contradice", "filas", default=0))])
    L.append(tabla(["Dataset · evidencia usada", "Correcta y precisa", "Correcta pero genérica", "Incorrecta", "Filas incorrectas"], filas))

    L.append("### 3.1 En qué se equivocan las incorrectas\n")
    L.append("Qué parte de la categoría choca con la evidencia: **la vertical** (dice Noticias, Deportes o Tecnología para algo que es ficción, "
             "o una vertical distinta de la que implica el género), **película vs serie** (dice Películas y es una serie, o al revés), "
             "**el género** (el código nombra un género que ninguna fuente trae) o **el sub-deporte** (dice Auto Racing y el género dice fútbol). "
             "Un documental o reality no se marca incorrecto por su tema: IMDb no registra de qué trata.\n")
    claves = sorted({k for n in nombres for k in D[n]["correctitud"]["contradice_tipo"]})
    filas = []
    for k in claves:
        e, t = k.split("|")
        filas.append([f"{EVIDENCIA.get(e, e)} · choca en {CHOQUE.get(t, t)} (`{k}`)"] +
                     [celda_fr(D[n]["correctitud"]["contradice_tipo"], k) for n in nombres])
    L.append(tabla(["Evidencia · qué choca"] + cab, filas))

    L.append("### 3.2 ¿Se equivocó el vendedor o el match de IMDb?\n")
    L.append("Solo para las incorrectas juzgadas con IMDb/Wikidata. Un match de confianza B acierta unas 3 de cada 4 veces, así que parte de "
             "estas contradicciones puede ser un match equivocado. Para separarlas se mira si el género que declara el propio vendedor coincide "
             "con los géneros IMDb del título encontrado: si coincide, el match es creíble y la categoría es la que está mal.\n")
    claves = ["coincide", "no_coincide", "sin_genero_declarado", "no_comparable"]
    filas = []
    for k in claves:
        fila = [f"El género declarado {GEN_VS_IMDB[k]} (`{k}`)"]
        for n in nombres:
            b = D[n]["correctitud"]["contradice_externa_por_genero_vs_imdb"]
            tot = sum(x["filas"] for x in b.values()) or 1
            x = b.get(k, {"filas": 0})
            fila.append(f"{fmt_n(x['filas'])} ({100.0 * x['filas'] / tot:.1f}%)")
        filas.append(fila)
    L.append(tabla(["Filas incorrectas con evidencia IMDb/Wikidata, según…"] + cab, filas))

    # ---- 4. por pais / publisher / origen ------------------------------------------------
    L.append("## 4. Quién acierta y quién no\n")
    L.append("Cada fila de estas tablas es un grupo (país, publisher u origen del valor). Los % de veredicto son sobre las filas evaluables del grupo; "
             "la última columna dice qué parte de **todos** los requests del grupo cae en filas con categoría incorrecta.\n")

    def bloque_tabla(titulo, primera_col, bloque, claves_orden=None, etiqueta=None):
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
            filas.append([etiqueta(k) if etiqueta else k, fmt_n(tot), fmt_p(100.0 * ev / tot if tot else 0),
                          fmt_p(100.0 * co / ev if ev else 0), fmt_p(100.0 * cp / ev if ev else 0),
                          f"**{fmt_p(100.0 * ct / ev if ev else 0)}**", fmt_n(ct),
                          fmt_p(100.0 * ct_r / b["requests"] if b["requests"] else 0)])
        L.append(tabla([primera_col, "Filas con categoría", "% evaluables", "Correcta y precisa", "Correcta pero genérica",
                        "Incorrecta", "Filas incorrectas", "% de los requests del grupo en filas incorrectas"], filas))

    for n in nombres:
        c = D[n]["correctitud"]
        bloque_tabla(f"Por país — {DATASET.get(n, n)}", "País", c["por_pais"], D[n]["meta"]["paises"])
        bloque_tabla(f"Por publisher (los {len(D[n]['meta']['publishers_top'])} con más filas) — {DATASET.get(n, n)}", "Publisher",
                     c["por_publisher"], D[n]["meta"]["publishers_top"])
        if c.get("por_origen"):
            L.append("En el dataset rellenado, el **origen** dice de dónde salió cada categoría: las que venían del vendedor son las mismas del "
                     "consolidado; las demás las puso el pipeline de relleno. Ojo: las derivadas de IMDb se juzgan contra la misma fuente que las generó, "
                     "así que su acierto solo prueba consistencia.\n")
            bloque_tabla(f"Por origen del valor — {DATASET.get(n, n)}", "Origen del valor", c["por_origen"], etiqueta=lambda k: lab(ORIGEN, k))

    # ---- 5. intra-titulo ----------------------------------------------------------------
    L.append("## 5. El mismo título con categorías distintas según la ruta\n")
    L.append("No necesita fuentes externas: si el mismo título llega con `[IAB12]` Noticias por una ruta de venta y con `[IAB1]` Entretenimiento por otra, "
             "al menos una está mal. Un título tiene **conflicto de vertical** cuando sus filas declaran verticales distintas, y **conflicto de forma** "
             "cuando unas dicen solo Películas y otras solo Televisión. Las **filas minoritarias** son las que dicen algo distinto de la mayoría "
             "de las filas de ese título: son las candidatas a estar mal.\n")
    filas = []
    for n in nombres:
        ci = D[n]["correctitud"]["conflicto_intra_titulo"]
        fm = ci["filas_minoritarias"]
        filas.append([ds(n), fmt_n(ci["titulos_con_categoria"]),
                      f"{fmt_n(ci['titulos_conflicto_vertical'])} ({100.0 * ci['titulos_conflicto_vertical'] / max(ci['titulos_con_categoria'], 1):.1f}%)",
                      fmt_n(ci["filas_en_titulos_con_conflicto"]["vertical"]),
                      celda_fr(fm, "vertical"),
                      f"{fmt_n(ci['titulos_conflicto_forma'])} ({100.0 * ci['titulos_conflicto_forma'] / max(ci['titulos_con_categoria'], 1):.1f}%)",
                      fmt_n(ci["filas_en_titulos_con_conflicto"]["forma"]),
                      celda_fr(fm, "forma"), celda_fr(fm, "vertical;forma")])
    L.append(tabla(["Dataset", "Títulos con categoría", "Títulos con conflicto de vertical", "Filas en esos títulos",
                    "Filas minoritarias de vertical (% de las que traen categoría)", "Títulos con conflicto de forma",
                    "Filas en esos títulos", "Filas minoritarias de forma", "Minoritarias en ambas"], filas))
    ci0 = D[nombres[0]]["correctitud"]["conflicto_intra_titulo"]
    if ci0["ejemplos_vertical"]:
        L.append(f"Ejemplos de conflicto de vertical en {ds(nombres[0])} (título → cuántas filas declaran cada vertical):\n")
        L.append("\n".join(f"- `{k}` → " + ", ".join(f"{VERTICAL.get(vv, vv)} ×{cc}" for vv, cc in sorted(v.items(), key=lambda x: -x[1]))
                           for k, v in list(ci0["ejemplos_vertical"].items())[:12]) + "\n")
    if ci0["ejemplos_forma"]:
        L.append("Ejemplos de conflicto de forma (título → cuántas filas dicen película y cuántas TV):\n")
        L.append("\n".join(f"- `{k}` → " + ", ".join(f"{FORMA.get(vv, vv)} ×{cc}" for vv, cc in sorted(v.items(), key=lambda x: -x[1]))
                           for k, v in list(ci0["ejemplos_forma"].items())[:12]) + "\n")

    # ---- 6. top contradicciones ---------------------------------------------------------
    L.append("## 6. Las categorías incorrectas con más tráfico\n")
    L.append("Un título por fila, ordenados por los requests de sus filas incorrectas. \"Declarado\" es la categoría que manda el vendedor; "
             "\"Esperado\" es lo que dice la evidencia; \"Género vs IMDb\" indica si el género declarado respalda el match (ver 3.2).\n")
    for n in nombres:
        top = D[n]["correctitud"]["contradicciones_top_titulos"]
        if not top:
            continue
        L.append(f"{ds(n)} (lista completa en `validacion-{n}-muestra-contradicciones.csv`):\n")
        filas = []
        for t in top[:25]:
            filas.append([f"`{(t['titulo'] or '')[:40]}`", f"`{t['declarado']}`", t["esperado"],
                          f"{t['imdb']} {(t['imdb_titulo'] or '')[:30]}".strip(), t["genero_declarado"][:25],
                          t["genero_vs_imdb"], CHOQUE.get(t["detalle"], t["detalle"]), t["publisher"][:30], fmt_n(t["filas"]), fmt_n(t["requests"])])
        L.append(tabla(["Título", "Declarado", "Esperado (forma / géneros)", "Match IMDb", "Género declarado",
                        "Género vs IMDb", "Qué choca", "Publisher (ejemplo)", "Filas (todas las rutas)", "Requests"], filas,
                       ["---"] * 8 + ["---:", "---:"]))
        L.append(f"Pares \"declarado → esperado\" más frecuentes ({DATASET.get(n, n)}):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_n(v["requests"])]
                 for k, v in list(D[n]["correctitud"]["contradicciones_top_pares"].items())[:15]]
        L.append(tabla(["Declarado → esperado", "Filas", "Requests"], filas))

    # ---- 7. contentGenre ------------------------------------------------------------------
    L.append("## 7. De paso: ¿el género declarado coincide con IMDb?\n")
    L.append("La misma evidencia sirve para validar `contentGenre`, que es el insumo del relleno de categoría. Sobre las filas con match y con género declarado: "
             "**coincide** = al menos un género declarado está entre los de IMDb/Wikidata; **no coincide** = ninguno.\n")
    filas = []
    for n in nombres:
        g = D[n]["correctitud"]["genero_vs_imdb"]["total"]
        tot = sum(x["filas"] for x in g.values()) or 1
        comp = g.get("coincide", {"filas": 0})["filas"] + g.get("no_coincide", {"filas": 0})["filas"]
        filas.append([ds(n), fmt_n(tot), fmt_n(comp),
                      fmt_p(100.0 * g.get("coincide", {"filas": 0})["filas"] / max(comp, 1)),
                      fmt_p(100.0 * g.get("no_coincide", {"filas": 0})["filas"] / max(comp, 1)),
                      fmt_p(100.0 * g.get("sin_genero_declarado", {"filas": 0})["filas"] / tot)])
    L.append(tabla(["Dataset", "Filas con match IMDb/Wikidata", "…de las cuales declaran género", "Coincide (% de las comparables)",
                    "No coincide", "Sin género declarado (% de las con match)"], filas))
    gp = D[nombres[0]]["correctitud"]["genero_vs_imdb"]["por_publisher"]
    if gp:
        filas = []
        for p, g in gp.items():
            comp = g.get("coincide", {"filas": 0})["filas"] + g.get("no_coincide", {"filas": 0})["filas"]
            filas.append([p, fmt_n(comp), fmt_p(100.0 * g.get("coincide", {"filas": 0})["filas"] / max(comp, 1)),
                          fmt_p(100.0 * g.get("no_coincide", {"filas": 0})["filas"] / max(comp, 1))])
        L.append(f"Por publisher ({DATASET.get(nombres[0], nombres[0])}):\n")
        L.append(tabla(["Publisher", "Filas comparables", "Coincide", "No coincide"], filas))

    # ---- 8. limites -----------------------------------------------------------------------
    L.append("## 8. Límites del método\n")
    L.append("- **Solo se puede juzgar lo que tiene título real y match.** El catálogo con títulos de relleno (`epg`, `roku`) o nombres de canal no está en IMDb; "
             "para esas filas solo queda el género de la fila o la comparación entre rutas.\n"
             "- **Un match de confianza B falla 1 de cada 4 veces.** Por eso las incorrectas con evidencia externa se separan según si el género declarado "
             "respalda el match (3.2); la cifra defendible es la de \"género coincide\". Con `--confianza-min A` el método es más estricto (menos cobertura, más precisión).\n"
             "- **IMDb no dice de qué trata la no ficción**: un documental etiquetado Viajes o Tecnología queda como \"correcta pero genérica\", no como \"correcta y precisa\". "
             "Para validar esas verticales haría falta TMDB (keywords) o Wikidata P921 (tema principal).\n"
             "- **El género es opinable**: IMDb trae hasta 3 géneros y Wikidata los suyos. El choque de género solo se declara si el código nombra un género que ninguna fuente trae; "
             "es el choque más débil y por eso se reporta aparte.\n")
    open(os.path.join(out_dir, "reporte-correctitud.md"), "w", encoding="utf-8").write("\n".join(L))


# ----------------------------------------------------------------------------
def reporte_completitud(datasets, out_dir):
    L = []
    nombres = list(datasets.keys())
    D = datasets
    m0 = D[nombres[0]]["meta"]
    cab = [DATASET.get(n, n) for n in nombres]
    L.append("# contentCategory, parte 2: ¿se puede poner una categoría más fina?\n")
    L.append("**Fuentes:** " + "; ".join(f"`{D[n]['meta']['archivo']}` ({fmt_n(D[n]['meta']['filas'])} filas, "
                                        f"columna `{D[n]['meta']['columna']}`)" for n in nombres) + ".  ")
    L.append(f"**Generado con:** `scripts/validar_categorias.py` + `scripts/generar_reporte_validacion.py`. Corrida del {m0['fecha']}. "
             "Las propuestas se escriben en IAB Content Taxonomy **2.2** (la última que tiene géneros bajo Películas/Televisión y unos 70 deportes) "
             "y traen su equivalente en **1.0** (la que usan casi todas las filas que ya vienen con categoría).\n")
    L += glosario_comun(D, nombres)
    L.append("- **Nivel de detalle** de una categoría: cuenta cuántas cosas dice. **Nivel 0** = nada. **Nivel 1** = solo la vertical (`[IAB1]` Entretenimiento, `[IAB12]` Noticias). "
             "**Nivel 2** = vertical + forma (`[IAB1-5]` Películas, `[640]` Televisión) o vertical + deporte concreto (`[IAB17-44]` Soccer). "
             "**Nivel 3** = vertical + forma + género (`[333]` Drama Movies, `[651]` Reality TV). Se mide así para poder comparar categorías escritas en distintas taxonomías.\n")
    L.append("**Base de los porcentajes en este reporte:** sobre el **total de filas** del dataset (con y sin categoría), salvo en las tablas por país, "
             "publisher u origen, donde son sobre las filas del grupo.\n")
    L.append("---\n")

    # ---- 1. estado actual -------------------------------------------------------------
    L.append("## 1. Punto de partida\n")
    L.append("Cada fila está en uno de tres estados: **sin categoría** (vacía o con basura como `[-7]`), **con categoría correcta o genérica**, "
             "o **con categoría incorrecta** (la evidencia la contradice; ver el reporte de la parte 1).\n")
    filas = []
    for n in nombres:
        e = D[n]["completitud"]["estado"]
        filas.append([ds(n), fmt_n(D[n]["meta"]["filas"]), celda_fr(e, "vacia"), celda_fr(e, "llena"), celda_fr(e, "contradicha")])
    L.append(tabla(["Dataset", "Filas totales", "Sin categoría", "Con categoría correcta o genérica", "Con categoría incorrecta"], filas))
    L.append("Qué nivel de detalle tienen hoy (% del total de filas):\n")
    claves = sorted({k for n in nombres for k in D[n]["completitud"]["nivel_actual"]})
    filas = []
    for k in claves:
        est, niv = k.split("|")
        filas.append([f"{ESTADO.get(est, est)} · {NIVEL.get(niv, niv)} (`{k}`)"] + [celda_fr(D[n]["completitud"]["nivel_actual"], k) for n in nombres])
    L.append(tabla(["Estado · nivel de detalle actual"] + cab, filas))

    # ---- 2. propuesta ---------------------------------------------------------------------
    L.append("## 2. Hasta dónde llega la evidencia\n")
    L.append("Para cada fila se calcula la categoría más detallada que la evidencia permite justificar. Primero, qué evidencia hay:\n")
    claves = sorted({k for n in nombres for k in D[n]["completitud"]["evidencia"]})
    filas = [[lab(EVIDENCIA, k)] + [celda_fr(D[n]["completitud"]["evidencia"], k) for n in nombres] for k in claves]
    L.append(tabla(["Evidencia disponible para la fila"] + cab, filas))
    L.append("Segundo, de dónde sale la **forma** (película o TV), que es lo que separa el nivel 1 del 2. Se toma la primera fuente disponible en este orden: "
             "el tipo que da IMDb, un nombre de serie real en la fila, lo que ya decía la categoría, un género que la implica, o temporada/episodio en el título.\n")
    claves = sorted({k for n in nombres for k in D[n]["completitud"]["forma_origen"]})
    filas = [[lab(FORMA_ORIGEN, k)] + [celda_fr(D[n]["completitud"]["forma_origen"], k) for n in nombres] for k in claves]
    L.append(tabla(["De dónde sale la forma"] + cab, filas))
    L.append("Tercero, el nivel de detalle que se podría alcanzar (% del total de filas). Si una fila ya trae una categoría correcta con nivel igual o mejor que el "
             "alcanzable, se conserva lo que trae:\n")
    claves = sorted({k for n in nombres for k in D[n]["completitud"]["nivel_propuesto"]})
    filas = [[NIVEL.get(k, k)] + [celda_fr(D[n]["completitud"]["nivel_propuesto"], k) for n in nombres] for k in claves]
    L.append(tabla(["Nivel de detalle alcanzable"] + cab, filas))

    # ---- 3. mejora -----------------------------------------------------------------------------
    L.append("## 3. Qué cambiaría fila a fila\n")
    L.append("Comparando lo que trae cada fila con lo que la evidencia permite:\n")
    claves = [k for k in ["rellena", "sube", "mantiene", "corrige", "contradicha_sin_propuesta", "sin_propuesta"]
              if any(get(D[n]["completitud"]["mejora"], k, "pct_filas", default=0) >= 0.05 for n in nombres)]
    filas = [[lab(MEJORA, k)] + [celda_fr(D[n]["completitud"]["mejora"], k) for n in nombres] for k in claves]
    L.append(tabla(["Qué pasa con la fila"] + cab, filas))
    L.append("Detalle de los movimientos de nivel: estado actual y nivel actual → nivel alcanzable (% del total de filas; solo combinaciones con al menos 0.5%):\n")
    for n in nombres:
        mt = D[n]["completitud"]["matriz"]
        filas = []
        for k, v in mt.items():
            if v["pct_filas"] < 0.5:
                continue
            est, resto = k.split("|")
            a, b = resto.split("->")
            filas.append([f"{ESTADO.get(est, est)}, nivel {a} → nivel {b} (`{k}`)", fmt_n(v["filas"]), fmt_p(v["pct_filas"]), fmt_p(v["pct_requests"])])
        L.append(f"{ds(n)}:\n")
        L.append(tabla(["Movimiento", "Filas", "% de filas", "% de requests"], filas))

    # ---- 4. por grupo ---------------------------------------------------------------------------
    L.append("## 4. Por país, publisher y origen\n")
    L.append("Cada fila de estas tablas es un grupo; los % son sobre las filas del grupo. Las columnas son los mismos movimientos de la sección 3.\n")
    cols_mejora = [MEJORA.get(c, c) for c in claves]

    def tabla_grupo(titulo, primera_col, bloque, orden=None, etiqueta=None):
        if not bloque:
            return
        L.append(f"### {titulo}\n")
        filas = []
        for k in (orden or bloque.keys()):
            b = bloque.get(k)
            if not b:
                continue
            tot = sum(x["filas"] for x in b.values())
            filas.append([etiqueta(k) if etiqueta else k, fmt_n(tot)] + [fmt_p(100.0 * b.get(c, {"filas": 0})["filas"] / tot if tot else 0)
                                                                          for c in claves])
        L.append(tabla([primera_col, "Filas"] + cols_mejora, filas))

    for n in nombres:
        cp = D[n]["completitud"]
        tabla_grupo(f"Por país — {DATASET.get(n, n)}", "País", cp["por_pais"], D[n]["meta"]["paises"])
        tabla_grupo(f"Por publisher — {DATASET.get(n, n)}", "Publisher", cp["por_publisher"], D[n]["meta"]["publishers_top"])
        if cp.get("por_origen"):
            L.append("En el dataset rellenado, el **origen** dice de dónde salió la categoría actual. Los orígenes que llenan con una vertical genérica "
                     "(`[IAB1]`, nivel 1) son los que más pueden subir.\n")
            tabla_grupo(f"Por origen del valor actual — {DATASET.get(n, n)}", "Origen del valor", cp["por_origen"], etiqueta=lambda k: lab(ORIGEN, k))

    # ---- 5. propuestas ------------------------------------------------------------------------
    L.append("## 5. Qué categorías se propondrían\n")
    L.append("Cuando aparecen dos rutas separadas por `|` (por ejemplo `Movies > Drama Movies | Television > Drama TV`) es porque no se sabe si la fila es "
             "película o TV y se propone el par del mismo género.\n")
    for n in nombres:
        L.append(f"{ds(n)} — las 25 propuestas más frecuentes (IAB 2.2; % del total de filas):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_p(v["pct_filas"]), fmt_p(v["pct_requests"])]
                 for k, v in list(D[n]["completitud"]["propuestas_top"].items())[:25]]
        L.append(tabla(["Categoría propuesta (ruta IAB 2.2)", "Filas", "% de filas", "% de requests"], filas))
    L.append(f"Con qué evidencia se generaron las propuestas en {ds(nombres[0])}. Cada regla dice: qué evidencia se usó, qué vertical se propuso, "
             "qué forma (película / TV / sin forma) y de dónde salió esa forma:\n")
    filas = []
    for k, v in list(D[nombres[0]]["completitud"]["reglas"].items())[:20]:
        ev, vert, forma, fo = k.split("|")
        filas.append([EVIDENCIA.get(ev, ev), VERTICAL.get(vert, vert), FORMA.get(forma, forma),
                      FORMA_ORIGEN.get(fo, "—") if fo != "-" else "—", fmt_n(v["filas"]), fmt_p(v["pct_filas"])])
    L.append(tabla(["Evidencia", "Vertical propuesta", "Forma", "De dónde sale la forma", "Filas", "% de filas"], filas,
                   ["---"] * 4 + ["---:", "---:"]))

    # ---- 6. limites -------------------------------------------------------------------------------
    L.append("## 6. Qué haría falta para llegar más lejos\n")
    L.append("- **Las filas sin título real** (rellenos como `epg` o `roku`, nombres de canal, macros) solo pueden subir por el género declarado: "
             "a nivel 2 (el par película + TV del género) o a nivel 1. Si son película o TV solo lo sabe el vendedor.\n"
             "- **Deporte concreto**: se detecta por palabras en el género o el título (`soccer`, `boxeo`, `NBA`…). \"Football\" se mapea a fútbol americano "
             "como manda IAB 1.0 (`IAB17-12`); si el vendedor lo usa como fútbol, corregirlo es una decisión de negocio, no de dato.\n"
             "- **Temas de la no ficción** (viajes, cocina, tecnología): IMDb no los registra. Se conservan cuando el vendedor los declara; para proponerlos "
             "desde cero haría falta TMDB (keywords) o Wikidata P921.\n"
             "- **IAB 3.0** separa forma y género en ramas distintas (`Entertainment > Movies` + `Genres > Drama`); la propuesta 2.2 se traduce directo "
             "(`333` → `324` + `647`) si un comprador la pide.\n")
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
