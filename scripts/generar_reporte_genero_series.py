# -*- coding: utf-8 -*-
"""Genera los reportes markdown de validacion de contentGenre y contentSeries a partir de
los JSON de validar_genero_series.py (uno o varios datasets lado a lado).

    python scripts/generar_reporte_genero_series.py reportes/NN \
        consolidado=.../validacion-consolidado.json relleno=.../validacion-relleno.json

Escribe reporte-genero.md (correctitud + completitud) y reporte-series.md (correctitud
basica + completitud). Las claves tecnicas del JSON se muestran con una etiqueta en
lenguaje claro y la clave entre parentesis, para cruzarlas con los CSV fila a fila.
"""
import json
import os
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar_reporte_validacion import fmt_n, fmt_p, tabla, get, celda_fr, DATASET, ORIGEN, lab, ds  # noqa: E402

VER_G = {"coincide": "Coincide", "afin": "Parecido (género vecino)", "parcial": "Acierta en parte",
         "contradice": "Contradice", "no_evaluable": "No se pudo evaluar"}
FORMATO_G = {"mapeado": "Género reconocido", "no_mapeado:genero_en_formato_sucio": "Género mal escrito o mal codificado",
             "no_mapeado:otros_no_reconocidos": "Texto que no es un género conocido",
             "no_mapeado:tipo_de_contenido": "Dice el tipo de contenido (movies, live), no el género",
             "no_mapeado:prefijo_tecnico": "Etiqueta técnica del vendedor (genre_…)",
             "no_mapeado:tema_no_genero": "Tema de interés, no género (outdoors, arts)",
             "no_mapeado:idioma_o_region": "Idioma o región, no género"}
MEJORA_G = {"rellena": "Se puede llenar (estaba vacía)", "sube": "Se pueden agregar géneros o uno más preciso",
            "corrige": "Se puede corregir (contradecía)", "corrige_parcial": "Se corrige en parte (acertaba en parte)",
            "mantiene": "Se queda igual (ya está bien)", "sin_propuesta": "Sin propuesta (sin evidencia)",
            "contradicha_sin_propuesta": "Contradice y no hay reemplazo"}
NIVEL_G = {"0": "Nivel 0 · vacío", "1": "Nivel 1 · sin género comparable (solo \"entertainment\", \"other\"…)",
           "2": "Nivel 2 · un género", "3": "Nivel 3 · dos o más géneros"}
VER_S = {"coincide": "Coincide", "otro_nombre": "Es serie, pero con otro nombre (compatible)",
         "contradice": "IMDb dice que es película", "no_evaluable": "No se pudo evaluar"}
QUE_ES = {"serie": "Serie", "pelicula": "Película", "ambiguo": "Ambiguo", "desconocido": "Desconocido"}
QUE_ES_EV = {"imdb": "según IMDb", "titulo": "el título trae temporada/episodio", "intra_titulo": "otras rutas nombran la serie",
             "declarado": "solo lo dice el vendedor", "-": "sin evidencia", "imdb:short": "corto según IMDb",
             "imdb:tvMovie": "película para TV según IMDb", "imdb:video": "video según IMDb", "imdb:tvSpecial": "especial de TV según IMDb",
             "placeholder_vod": "trae el relleno \"VOD\""}
MEJORA_S = {"ya_nombrada": "Serie con nombre", "serie_sin_nombre_recuperable": "Serie sin nombre, con nombre proponible",
            "serie_sin_nombre": "Serie sin nombre, sin nombre proponible", "pelicula_vacio_correcto": "Película: el vacío es correcto",
            "pelicula_con_serie_declarada": "Película con serie declarada (contradicción)", "contradicha": "Contradicha",
            "nombrada_sin_evidencia": "Con nombre, sin evidencia para juzgar", "sin_evidencia": "Sin evidencia"}
TEMP = {"temporada+episodio": "Temporada y episodio", "solo_temporada": "Solo temporada", "solo_episodio": "Solo episodio", "nada": "Nada"}


def lab_que_es(k):
    q, ev = k.split("|")
    return f"{QUE_ES.get(q, q)} · {QUE_ES_EV.get(ev, ev)} (`{k}`)"


def lab_formato_series(k):
    if k == "serie_real":
        return "Nombre de serie real (`serie_real`)"
    if k.startswith("placeholder:"):
        return f"Relleno \"{k.split(':', 1)[1]}\" (no es una serie) (`{k}`)"
    return f"`{k}`"


def tabla_claves(bloque_por_dataset, nombres, titulo_col, orden=None, minimo=0.0, etiqueta=None):
    claves = orden or sorted({k for n in nombres for k in bloque_por_dataset[n]})
    claves = [k for k in claves if any((get(bloque_por_dataset[n], k, "pct_filas", default=0) or 0) >= minimo for n in nombres)]
    filas = [[etiqueta(k) if etiqueta else f"`{k}`"] + [celda_fr(bloque_por_dataset[n], k) for n in nombres] for k in claves]
    return tabla([titulo_col] + [DATASET.get(n, n) for n in nombres], filas)


def tabla_grupo(L, titulo, primera_col, bloque, claves, cols, orden=None, con_desglose=True, etiqueta=None):
    if not bloque:
        return
    L.append(f"### {titulo}\n")
    filas = []
    for k in (orden or bloque.keys()):
        b = bloque.get(k)
        if not b:
            continue
        d = b["desglose"] if con_desglose else b
        tot = sum(x["filas"] for x in d.values())
        filas.append([etiqueta(k) if etiqueta else k, fmt_n(tot)] + [fmt_p(100.0 * d.get(c, {"filas": 0})["filas"] / tot if tot else 0) for c in claves])
    L.append(tabla([primera_col, "Filas"] + cols, filas))


def glosario(D, nombres, columna):
    m0 = D[nombres[0]]["meta"]
    L = ["## Cómo leer este reporte\n"]
    L.append("- **Fila**: cada fila del inventario es una combinación de país, publisher, app y metadata de contenido, no un programa. "
             "**Requests** son las solicitudes de anuncio de esa fila; cada cifra se da en filas y en requests.")
    if len(nombres) > 1:
        L.append(f"- **{DATASET.get(nombres[0], nombres[0])}** es el inventario tal como lo mandan los vendedores. "
                 f"**{DATASET.get(nombres[1], nombres[1])}** es el mismo inventario después de que el pipeline de relleno completó los valores vacíos.")
    L.append(f"- **Evidencia**: el título de la fila se busca en IMDb y Wikidata. Cuando se encuentra (un **match**), esas bases dicen si es película o serie y qué "
             f"géneros tiene. Cubre {fmt_n(m0['filas_con_match_externo'])} filas ({fmt_p(100.0 * m0['filas_con_match_externo'] / m0['filas'])} del total). "
             f"Confianza del match: A = sin ambigüedad; B = podría ser un título homónimo (acierta ~3 de cada 4). Se usan matches de confianza {m0['confianza_min']} o mejor.")
    L.append("- **Formato de las celdas**: `12,345 filas (12.3%) · 4.5% req` = cantidad de filas, % de filas y % de requests sobre la base que indica cada tabla.")
    return L


def reporte_genero(D, out_dir):
    nombres = list(D.keys())
    m0 = D[nombres[0]]["meta"]
    cab = [DATASET.get(n, n) for n in nombres]
    L = ["# contentGenre: ¿el género declarado es correcto y se puede completar?\n"]
    L.append("**Fuentes:** " + "; ".join(f"`{D[n]['meta']['archivo']}` ({fmt_n(D[n]['meta']['filas'])} filas, columna `{D[n]['meta']['columna_genero']}`)" for n in nombres) + ".  ")
    L.append(f"**Generado con:** `scripts/validar_genero_series.py` + `scripts/generar_reporte_genero_series.py`. Corrida del {m0['fecha']}. "
             f"Evidencia: géneros de IMDb y de Wikidata desde `cache-enriquecimiento/titulos.json` ({fmt_n(m0['titulos_en_cache'])} títulos).\n")
    L += glosario(D, nombres, "contentGenre")
    L.append("- **Géneros comparables**: los géneros declarados se traducen al vocabulario del proyecto y se agrupan en conceptos que IMDb también usa "
             "(thriller, misterio y crimen → crimen-misterio; acción, aventura y bélico → acción-aventura; anime → animación). Lo que IMDb no maneja "
             "(lifestyle, viajes, cocina, religión, educación, videojuegos, \"entertainment\", \"other\", \"movies\", \"tv\") no se juzga.\n")
    L.append("**Base de los porcentajes:** en la parte 1 (correctitud) son sobre las **filas con género declarado**; en la parte 2 (completitud), sobre el **total de filas**.\n")
    L.append("---\n")

    L.append("## 1. Correctitud: ¿el género declarado coincide con IMDb/Wikidata?\n")
    L.append("Cada género comparable que declara la fila se compara con los del título en IMDb/Wikidata: **acierta** si está entre ellos; **es vecino** si no está "
             "pero es un género cercano (telenovela y drama/romance, thriller y terror, infantil y animación, documental y reality); **choca** si ni lo uno ni lo otro. "
             "El veredicto de la fila junta todos sus géneros:\n")
    L.append("- **Coincide** (`coincide`): todo lo declarado acierta.\n- **Parecido** (`afin`): nada choca, pero tampoco acierta; son géneros vecinos.\n"
             "- **Acierta en parte** (`parcial`): hay géneros que aciertan y otros que chocan.\n- **Contradice** (`contradice`): choca y nada acierta.\n"
             "- **No se pudo evaluar** (`no_evaluable`): sin match, o sin género comparable.\n")
    filas = []
    for n in nombres:
        g = D[n]["genero"]
        v = g["veredicto"]
        ev = sum(x["filas"] for k, x in v.items() if k != "no_evaluable")
        evr = sum(x["requests"] for k, x in v.items() if k != "no_evaluable")
        fila = [ds(n), f"{fmt_n(g['filas_con_genero'])} ({fmt_p(g['pct_filas_con_genero'])} del total)",
                f"{fmt_n(ev)} ({fmt_p(100.0 * ev / max(g['filas_con_genero'], 1))})"]
        for k in ("coincide", "afin", "parcial", "contradice"):
            x = v.get(k, {"filas": 0, "requests": 0})
            fila.append(f"{fmt_p(100.0 * x['filas'] / max(ev, 1))} · {fmt_p(100.0 * x['requests'] / max(evr, 1))} req")
        fila.append(fmt_n(v.get("contradice", {"filas": 0})["filas"]))
        filas.append(fila)
    L.append(tabla(["Dataset", "Filas con género", "Evaluables (% de las con género)", "Coincide", "Parecido", "Acierta en parte", "Contradice", "Filas que contradicen"], filas))
    L.append("*Los % de las cuatro columnas de veredicto son sobre las filas evaluables.*\n")

    L.append("### 1.1 Cómo vienen escritos los géneros\n")
    L.append("Un valor cuenta como **género reconocido** si al menos una de sus palabras está en el diccionario de géneros del proyecto. Lo demás se clasifica según qué es:\n")
    L.append(tabla_claves({n: D[n]["genero"]["formato"] for n in nombres}, nombres, "Tipo de valor", etiqueta=lambda k: lab(FORMATO_G, k)))
    L.append("Cuántos géneros comparables declara cada fila (0 = solo valores genéricos como \"entertainment\"):\n")
    L.append(tabla_claves({n: D[n]["genero"]["n_declarados"] for n in nombres}, nombres, "Géneros comparables por fila", ["0", "1", "2", "3"],
                          etiqueta=lambda k: f"{k} género{'s' if k != '1' else ''}"))

    L.append("### 1.2 Qué género choca y con qué se confunde\n")
    for n in nombres:
        g = D[n]["genero"]
        L.append(f"{ds(n)} — género declarado que choca con la evidencia (filas con veredicto \"acierta en parte\" o \"contradice\"):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_n(v["requests"])] for k, v in list(g["choque_por_genero"].items())[:12]]
        L.append(tabla(["Género declarado", "Filas", "Requests"], filas))
        L.append(f"Confusiones más frecuentes en {DATASET.get(n, n)} (género declarado → lo que dice IMDb/Wikidata):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_n(v["requests"])] for k, v in list(g["confusiones_top"].items())[:15]]
        L.append(tabla(["Declarado → lo que dice la evidencia", "Filas", "Requests"], filas))

    L.append("### 1.3 Quién acierta y quién no\n")
    L.append("Los % son sobre las filas con género de cada grupo.\n")
    claves = ["coincide", "afin", "parcial", "contradice", "no_evaluable"]
    cols = [VER_G[c] for c in claves]
    for n in nombres:
        g = D[n]["genero"]
        tabla_grupo(L, f"Por país — {DATASET.get(n, n)}", "País", g["por_pais"], claves, cols, D[n]["meta"]["paises"])
        tabla_grupo(L, f"Por publisher — {DATASET.get(n, n)}", "Publisher", g["por_publisher"], claves, cols, D[n]["meta"]["publishers_top"])
        if g.get("por_origen"):
            L.append("En el dataset rellenado, el **origen** dice de dónde salió el género. El origen IMDb se juzga contra la misma fuente que lo generó, "
                     "así que su acierto solo prueba consistencia.\n")
            tabla_grupo(L, f"Por origen del valor — {DATASET.get(n, n)}", "Origen del valor", g["por_origen"], claves, cols, etiqueta=lambda k: lab(ORIGEN, k))

    L.append("### 1.4 Las contradicciones con más tráfico\n")
    for n in nombres:
        top = D[n]["genero"]["contradicciones_top_titulos"]
        if not top:
            continue
        L.append(f"{ds(n)} (un título por fila; lista completa en `validacion-{n}-muestra-genero-contradicciones.csv`):\n")
        filas = [[f"`{(t['titulo'] or '')[:40]}`", f"`{t['declarado'][:30]}`", t["generos_imdb"][:30], t["wikidata"][:20],
                  f"{t['imdb']} {(t['imdb_titulo'] or '')[:25]}", t["confianza"], t["publisher"][:28], fmt_n(t["filas"]), fmt_n(t["requests"])]
                 for t in top[:20]]
        L.append(tabla(["Título", "Género declarado", "Géneros IMDb", "Extra de Wikidata", "Match IMDb", "Confianza", "Publisher (ejemplo)", "Filas", "Requests"], filas,
                       ["---"] * 7 + ["---:", "---:"]))

    L.append("## 2. Completitud: ¿se pueden agregar géneros?\n")
    L.append("Nivel de detalle del género: **nivel 0** = vacío; **nivel 1** = sin género comparable (solo \"entertainment\", \"other\" o un tipo de contenido); "
             "**nivel 2** = un género; **nivel 3** = dos o más. La **propuesta** conserva lo declarado que no choca y agrega los géneros de IMDb (hasta 3) "
             "y los extra de Wikidata (telenovela, holiday, indie…), en el vocabulario del proyecto.\n")
    L.append("Punto de partida (% del total de filas):\n")
    L.append(tabla_claves({n: D[n]["genero"]["completitud"]["estado"] for n in nombres}, nombres, "Estado", ["vacia", "llena", "contradicha"],
                          etiqueta=lambda k: {"vacia": "Sin género (`vacia`)", "llena": "Con género que no contradice (`llena`)", "contradicha": "Con género que contradice (`contradicha`)"}[k]))
    L.append("Nivel de detalle actual y nivel alcanzable (% del total de filas):\n")
    filas = []
    for k in ("0", "1", "2", "3"):
        fila = [NIVEL_G[k]]
        for n in nombres:
            fila += [celda_fr(D[n]["genero"]["completitud"]["nivel_actual"], k), celda_fr(D[n]["genero"]["completitud"]["nivel_propuesto"], k)]
        filas.append(fila)
    cols = ["Nivel"]
    for n in nombres:
        cols += [f"{DATASET.get(n, n)} · hoy", f"{DATASET.get(n, n)} · alcanzable"]
    L.append(tabla(cols, filas))
    L.append("Qué cambiaría fila a fila:\n")
    L.append(tabla_claves({n: D[n]["genero"]["completitud"]["mejora"] for n in nombres}, nombres, "Qué pasa con la fila",
                          ["rellena", "sube", "corrige", "corrige_parcial", "mantiene", "sin_propuesta", "contradicha_sin_propuesta"], 0.05,
                          etiqueta=lambda k: lab(MEJORA_G, k)))
    L.append("**Telenovela** es el caso concreto de \"un género más preciso\": Wikidata la marca como género propio y los vendedores declaran solo \"drama\". "
             "Filas de títulos que Wikidata clasifica como telenovela:\n")
    L.append(tabla_claves({n: D[n]["genero"]["completitud"]["telenovela_wikidata"] for n in nombres}, nombres, "Telenovela según Wikidata",
                          etiqueta=lambda k: {"ya_declarada": "Ya declarada como telenovela (`ya_declarada`)", "propuesta": "Se puede proponer telenovela (`propuesta`)"}.get(k, f"`{k}`")))
    claves_c = ["rellena", "sube", "corrige", "corrige_parcial", "mantiene", "sin_propuesta"]
    cols_c = [MEJORA_G[c] for c in claves_c]
    L.append("Por grupo (% sobre las filas del grupo):\n")
    for n in nombres:
        c = D[n]["genero"]["completitud"]
        tabla_grupo(L, f"Por país — {DATASET.get(n, n)}", "País", c["por_pais"], claves_c, cols_c, D[n]["meta"]["paises"], con_desglose=False)
        tabla_grupo(L, f"Por publisher — {DATASET.get(n, n)}", "Publisher", c["por_publisher"], claves_c, cols_c, D[n]["meta"]["publishers_top"], con_desglose=False)
        if c.get("por_origen"):
            tabla_grupo(L, f"Por origen del valor — {DATASET.get(n, n)}", "Origen del valor", c["por_origen"], claves_c, cols_c, con_desglose=False, etiqueta=lambda k: lab(ORIGEN, k))
        L.append(f"Propuestas más frecuentes en {DATASET.get(n, n)} (% del total de filas):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_p(v["pct_filas"]), fmt_p(v["pct_requests"])] for k, v in list(c["propuestas_top"].items())[:20]]
        L.append(tabla(["Géneros propuestos", "Filas", "% de filas", "% de requests"], filas))

    L.append("## 3. Límites\n")
    L.append("- El género es opinable y IMDb trae hasta tres: por eso existe \"parecido\" y la cifra dura es \"contradice\" (nada de lo declarado cabe).\n"
             "- Un match de confianza B falla 1 de cada 4 veces; una contradicción con confianza B puede ser culpa del match. La muestra trae la confianza para filtrar.\n"
             "- Lo no comparable (lifestyle, viajes, cocina, religión, videojuegos) no se valida ni se propone: IMDb no lo registra.\n"
             "- En el dataset rellenado, el origen IMDb del género se valida contra la misma fuente: su acierto es circular.\n")
    open(os.path.join(out_dir, "reporte-genero.md"), "w", encoding="utf-8").write("\n".join(L))


def reporte_series(D, out_dir):
    nombres = list(D.keys())
    m0 = D[nombres[0]]["meta"]
    L = ["# contentSeries: ¿la serie declarada es correcta y cuántas filas son serie sin decirlo?\n"]
    L.append("**Fuentes:** " + "; ".join(f"`{D[n]['meta']['archivo']}` ({fmt_n(D[n]['meta']['filas'])} filas, columna `{D[n]['meta']['columna_series']}`)" for n in nombres) + ".  ")
    L.append(f"**Generado con:** `scripts/validar_genero_series.py` + `scripts/generar_reporte_genero_series.py`. Corrida del {m0['fecha']}. "
             f"Evidencia: el tipo que da IMDb (película, serie, miniserie), el título crudo (\"season 2\", \"S01E03\", \"ep 4\") y las demás rutas del mismo título "
             f"(se exige que al menos {m0['min_filas_serie']} filas y {m0['min_rutas_serie']} publishers nombren la serie, igual que en el relleno).\n")
    L += glosario(D, nombres, "contentSeries")
    L.append("- **Nombre de serie real**: un `contentSeries` que no está vacío, ni es un centinela, ni el hash MD5 de cadena vacía, ni un relleno como `VOD` o `No Series`.\n")
    L.append("**Base de los porcentajes:** en la parte 1 (correctitud) sobre las **filas con nombre de serie real**; en la parte 2 (completitud) sobre el **total de filas**.\n")
    L.append("---\n")

    L.append("## 1. Correctitud (básica): ¿lo que dice ser serie lo es?\n")
    L.append("Solo se juzga lo que IMDb puede juzgar:\n")
    L.append("- **Coincide** (`coincide`): IMDb dice que es serie y el nombre declarado es el título canónico o el título de la fila.\n"
             "- **Es serie, pero con otro nombre** (`otro_nombre`): IMDb dice que es serie, pero la serie declarada se llama distinto (un episodio con nombre propio, o un error). Se considera compatible.\n"
             "- **IMDb dice que es película** (`contradice`): el título es una película según IMDb (confianza A o B) y no trae temporada ni episodio.\n"
             "- **No se pudo evaluar** (`no_evaluable`): sin match, o el tipo es ambiguo (corto, video, película para TV).\n")
    filas = []
    for n in nombres:
        s = D[n]["series"]
        v = s["veredicto"]
        fila = [ds(n), f"{fmt_n(s['filas_con_serie_real'])} ({fmt_p(s['pct_filas_con_serie_real'])} del total; {fmt_p(s['pct_requests_con_serie_real'])} req)"]
        for k in ("coincide", "otro_nombre", "contradice", "no_evaluable"):
            fila.append(celda_fr(v, k))
        filas.append(fila)
    L.append(tabla(["Dataset", "Filas con nombre de serie real", "Coincide", "Es serie con otro nombre", "IMDb dice que es película", "No se pudo evaluar"], filas))
    L.append("Qué trae la columna (% del total de filas): nombres reales frente a rellenos:\n")
    L.append(tabla_claves({n: D[n]["series"]["formato"] for n in nombres}, nombres, "Contenido de contentSeries", minimo=0.01, etiqueta=lab_formato_series))
    claves = ["coincide", "otro_nombre", "contradice", "no_evaluable"]
    cols = [VER_S[c] for c in claves]
    L.append("Por grupo (% sobre las filas con nombre de serie real del grupo):\n")
    for n in nombres:
        s = D[n]["series"]
        tabla_grupo(L, f"Por publisher — {DATASET.get(n, n)}", "Publisher", s["por_publisher"], claves, cols, D[n]["meta"]["publishers_top"])
        if s.get("por_origen"):
            L.append("En el dataset rellenado, el origen IMDb se juzga contra la misma fuente que lo generó: su acierto solo prueba consistencia.\n")
            tabla_grupo(L, f"Por origen del valor — {DATASET.get(n, n)}", "Origen del valor", s["por_origen"], claves, cols, etiqueta=lambda k: lab(ORIGEN, k))
        top = s["contradicciones_top_titulos"]
        if top:
            L.append(f"Series declaradas en títulos que IMDb dice que son película ({DATASET.get(n, n)}; lista completa en `validacion-{n}-muestra-series-contradicciones.csv`):\n")
            filas = [[f"`{(t['titulo'] or '')[:35]}`", f"`{t['serie_declarada'][:30]}`", f"{t['imdb']} {(t['imdb_titulo'] or '')[:30]}", t["confianza"], t["publisher"][:28], fmt_n(t["filas"]), fmt_n(t["requests"])]
                     for t in top[:15]]
            L.append(tabla(["Título", "Serie declarada", "Película según IMDb", "Confianza", "Publisher (ejemplo)", "Filas", "Requests"], filas, ["---"] * 5 + ["---:", "---:"]))

    L.append("## 2. Completitud: qué es cada fila y qué se le puede poner\n")
    L.append("Para todas las filas se decide si el contenido es **serie**, **película**, **ambiguo** o **desconocido**, y con qué evidencia: el título trae temporada/episodio, "
             "el tipo de IMDb, otras rutas del mismo título nombran la serie, o solo lo dice el vendedor. Para las series sin nombre se propone uno: el título de la fila "
             "sin los sufijos de temporada/episodio; si no, el nombre que traen las otras rutas; si no, el título canónico de IMDb.\n")
    L.append("Qué es cada fila (% del total):\n")
    L.append(tabla_claves({n: D[n]["series"]["completitud"]["que_es"] for n in nombres}, nombres, "Qué es · con qué evidencia", minimo=0.05, etiqueta=lab_que_es))
    L.append("Qué implica eso para la columna contentSeries (% del total):\n")
    L.append(tabla_claves({n: D[n]["series"]["completitud"]["mejora"] for n in nombres}, nombres, "Situación de la fila",
                          ["ya_nombrada", "serie_sin_nombre_recuperable", "serie_sin_nombre", "pelicula_vacio_correcto", "pelicula_con_serie_declarada", "contradicha", "nombrada_sin_evidencia", "sin_evidencia"], 0.01,
                          etiqueta=lambda k: lab(MEJORA_S, k)))
    L.append("**Temporada y episodio.** OpenRTB tiene los campos `content.season` y `content.episode`, que el reporte de inventario no expone; pero a veces el título los trae "
             "(\"animacars season 2\", \"transplant s4 ep 7\"). Filas donde se pueden extraer del título (% del total):\n")
    L.append(tabla_claves({n: D[n]["series"]["completitud"]["temporada_episodio"] for n in nombres}, nombres, "Qué trae el título",
                          ["temporada+episodio", "solo_temporada", "solo_episodio", "nada"], etiqueta=lambda k: lab(TEMP, k)))
    claves_c = ["ya_nombrada", "serie_sin_nombre_recuperable", "pelicula_vacio_correcto", "sin_evidencia"]
    cols_c = [MEJORA_S[c] for c in claves_c]
    L.append("Por grupo (% sobre las filas del grupo):\n")
    for n in nombres:
        c = D[n]["series"]["completitud"]
        tabla_grupo(L, f"Por país — {DATASET.get(n, n)}", "País", c["por_pais"], claves_c, cols_c, D[n]["meta"]["paises"], con_desglose=False)
        tabla_grupo(L, f"Por publisher — {DATASET.get(n, n)}", "Publisher", c["por_publisher"], claves_c, cols_c, D[n]["meta"]["publishers_top"], con_desglose=False)
        if c.get("por_origen"):
            tabla_grupo(L, f"Por origen del valor — {DATASET.get(n, n)}", "Origen del valor", c["por_origen"], claves_c, cols_c, con_desglose=False, etiqueta=lambda k: lab(ORIGEN, k))
        L.append(f"Series propuestas con más filas en {DATASET.get(n, n)} (nombre propuesto y, entre corchetes, de dónde salió; muestra aleatoria en `validacion-{n}-muestra-series-propuestas.csv`):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_p(v["pct_filas"]), fmt_p(v["pct_requests"])] for k, v in list(c["propuestas_top"].items())[:25]]
        L.append(tabla(["Serie propuesta [evidencia]", "Filas", "% de filas", "% de requests"], filas))

    L.append("## 3. Límites\n")
    L.append("- La correctitud es deliberadamente básica: IMDb solo sabe si el título es serie o película, no cómo se llama la serie de un episodio con nombre propio; "
             "por eso \"es serie con otro nombre\" cuenta como compatible y no como error.\n"
             "- Un match B que cae en una película homónima convierte una serie en \"IMDb dice que es película\"; para evitarlo, el título con temporada/episodio manda sobre IMDb, pero no todos lo traen.\n"
             "- El nombre propuesto toma el título de la fila (en su idioma) antes que el canónico de IMDb (a veces en inglés: *True Love* por *amores verdaderos*).\n"
             "- Temporada y episodio salen de patrones en el título; \"season two\" en letras no se detecta.\n")
    open(os.path.join(out_dir, "reporte-series.md"), "w", encoding="utf-8").write("\n".join(L))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out_dir = sys.argv[1]
    D = OrderedDict()
    for arg in sys.argv[2:]:
        nombre, path = arg.split("=", 1)
        D[nombre] = json.load(open(path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    reporte_genero(D, out_dir)
    reporte_series(D, out_dir)
    print(f"escritos {out_dir}/reporte-genero.md y reporte-series.md")


if __name__ == "__main__":
    main()
