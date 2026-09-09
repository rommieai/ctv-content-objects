# -*- coding: utf-8 -*-
"""Genera los reportes markdown de validacion de contentGenre y contentSeries a partir de
los JSON de validar_genero_series.py (uno o varios datasets lado a lado).

    python scripts/generar_reporte_genero_series.py reportes/16-validacion-genero-series-v17 \
        consolidado=.../validacion-consolidado.json relleno=.../validacion-relleno.json

Escribe reporte-genero.md (correctitud + completitud) y reporte-series.md (correctitud
basica + completitud). La lectura narrativa va en el README del paquete.
"""
import json
import os
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generar_reporte_validacion import fmt_n, fmt_p, tabla, get, celda_fr  # noqa: E402


def tabla_claves(bloque_por_dataset, nombres, titulo_col, orden=None, minimo=0.0):
    claves = orden or sorted({k for n in nombres for k in bloque_por_dataset[n]})
    claves = [k for k in claves if any((get(bloque_por_dataset[n], k, "pct_filas", default=0) or 0) >= minimo for n in nombres)]
    filas = [[f"`{k}`"] + [celda_fr(bloque_por_dataset[n], k) for n in nombres] for k in claves]
    return tabla([titulo_col] + nombres, filas)


def tabla_grupo(L, titulo, bloque, claves, orden=None, con_desglose=True):
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
        filas.append([k, fmt_n(tot)] + [fmt_p(100.0 * d.get(c, {"filas": 0})["filas"] / tot if tot else 0) for c in claves])
    L.append(tabla(["", "Filas"] + [f"`{c}`" for c in claves], filas))


def reporte_genero(D, out_dir):
    nombres = list(D.keys())
    m0 = D[nombres[0]]["meta"]
    L = ["# Reporte — contentGenre: correctitud de lo declarado y géneros adicionales alcanzables\n"]
    L.append("**Fuentes:** " + "; ".join(f"`{D[n]['meta']['archivo']}` ({fmt_n(D[n]['meta']['filas'])} filas, columna `{D[n]['meta']['columna_genero']}`)" for n in nombres) + ".  ")
    L.append(f"**Generado con:** `scripts/validar_genero_series.py` + `scripts/generar_reporte_genero_series.py`. Corrida del {m0['fecha']}. "
             f"Evidencia: géneros IMDb (match de confianza ≥ {m0['confianza_min']}) y géneros Wikidata (P136) de `cache-enriquecimiento/titulos.json` "
             f"({fmt_n(m0['titulos_en_cache'])} títulos); cubre {fmt_n(m0['filas_con_match_externo'])} filas ({fmt_p(100.0 * m0['filas_con_match_externo'] / m0['filas'])}).\n")
    L.append("**Convención:** en la parte de correctitud los % son **% de las filas con género declarado**; en la de completitud, **% del total de filas**. "
             "Los géneros declarados se normalizan con el diccionario del proyecto y se colapsan a conceptos comparables con IMDb "
             "(thriller/misterio/crimen → crimen-misterio; acción/aventura/bélico → acción-aventura; anime → animación). "
             "Lo que IMDb no puede expresar (lifestyle, viajes, cocina, religión, educación, videojuegos, \"entertainment\", \"other\", \"movies\", \"tv\") no se juzga.\n")
    L.append("---\n")

    L.append("## 1. Correctitud\n")
    L.append("Por cada género comparable declarado: **acierta** si está entre los de IMDb/Wikidata del título; **afín** si no está pero es vecino "
             "(telenovela ~ drama/romance, thriller ~ terror, infantil ~ animación, documental ~ reality); **choca** si ni lo uno ni lo otro. "
             "Veredicto de la fila: `coincide` (todo acierta), `afin` (nada choca, nada acierta), `parcial` (aciertos y choques), `contradice` (choca y nada acierta), "
             "`no_evaluable` (sin match, o sin género comparable).\n")
    filas = []
    for n in nombres:
        g = D[n]["genero"]
        v = g["veredicto"]
        ev = sum(x["filas"] for k, x in v.items() if k != "no_evaluable")
        evr = sum(x["requests"] for k, x in v.items() if k != "no_evaluable")
        fila = [f"**{n}**", f"{fmt_n(g['filas_con_genero'])} ({fmt_p(g['pct_filas_con_genero'])} del total)",
                f"{fmt_n(ev)} ({fmt_p(100.0 * ev / max(g['filas_con_genero'], 1))})"]
        for k in ("coincide", "afin", "parcial", "contradice"):
            x = v.get(k, {"filas": 0, "requests": 0})
            fila.append(f"{fmt_p(100.0 * x['filas'] / max(ev, 1))} · req {fmt_p(100.0 * x['requests'] / max(evr, 1))}")
        fila.append(fmt_n(v.get("contradice", {"filas": 0})["filas"]))
        filas.append(fila)
    L.append(tabla(["Dataset", "Con género", "Evaluables", "coincide", "afin", "parcial", "contradice", "Filas que contradicen"], filas))
    L.append("Los % de coincide/afín/parcial/contradice son sobre las evaluables.\n")

    L.append("### 1.1 Formato de lo declarado\n")
    L.append("`mapeado` = al menos un token del valor está en el diccionario de géneros; `no_mapeado:*` = ninguno, clasificado por lo que es "
             "(tipo de contenido como \"movies\"/\"live\", idioma o región, tema que no es género, formato sucio).\n")
    L.append(tabla_claves({n: D[n]["genero"]["formato"] for n in nombres}, nombres, "Formato"))
    L.append("Cuántos géneros comparables declara cada fila (0 = solo genéricos como \"entertainment\"):\n")
    L.append(tabla_claves({n: D[n]["genero"]["n_declarados"] for n in nombres}, nombres, "Géneros comparables declarados", ["0", "1", "2", "3"]))

    L.append("### 1.2 Qué género choca y con qué\n")
    for n in nombres:
        g = D[n]["genero"]
        L.append(f"**{n}** — género declarado que choca (filas en veredicto parcial o contradice):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_n(v["requests"])] for k, v in list(g["choque_por_genero"].items())[:12]]
        L.append(tabla(["Género declarado", "Filas", "Requests"], filas))
        L.append(f"Confusiones más frecuentes ({n}: declarado → lo que dice IMDb/Wikidata):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_n(v["requests"])] for k, v in list(g["confusiones_top"].items())[:15]]
        L.append(tabla(["Declarado → esperado", "Filas", "Requests"], filas))

    L.append("### 1.3 Quién acierta y quién no\n")
    claves = ["coincide", "afin", "parcial", "contradice", "no_evaluable"]
    for n in nombres:
        g = D[n]["genero"]
        tabla_grupo(L, f"Por país — {n}", g["por_pais"], claves, D[n]["meta"]["paises"])
        tabla_grupo(L, f"Por publisher — {n}", g["por_publisher"], claves, D[n]["meta"]["publishers_top"])
        if g.get("por_origen"):
            L.append("En el relleno, `original` es lo que venía; `imdb` se validaría contra sí mismo (circular) y por eso su `coincide` no prueba nada.\n")
            tabla_grupo(L, f"Por origen del valor — {n}", g["por_origen"], claves)

    L.append("### 1.4 Las contradicciones con más tráfico\n")
    for n in nombres:
        top = D[n]["genero"]["contradicciones_top_titulos"]
        if not top:
            continue
        L.append(f"**{n}** (un título por fila; muestra completa en `validacion-{n}-muestra-genero-contradicciones.csv`):\n")
        filas = [[f"`{(t['titulo'] or '')[:40]}`", f"`{t['declarado'][:30]}`", t["generos_imdb"][:30], t["wikidata"][:20],
                  f"{t['imdb']} {(t['imdb_titulo'] or '')[:25]}", t["confianza"], t["publisher"][:28], fmt_n(t["filas"]), fmt_n(t["requests"])]
                 for t in top[:20]]
        L.append(tabla(["Título", "Declarado", "IMDb", "Wikidata extra", "Match", "Conf.", "Publisher (ej.)", "Filas", "Requests"], filas,
                       ["---"] * 7 + ["---:", "---:"]))

    L.append("## 2. Completitud\n")
    L.append("Nivel de granularidad: 0 = vacío; 1 = sin género comparable (solo \"entertainment\"/\"other\"/tipo de contenido); 2 = un género comparable; "
             "3 = dos o más. La **propuesta** conserva lo declarado que no choca (incluido lo no comparable) y agrega los géneros IMDb (hasta 3) y los extra "
             "de Wikidata (telenovela, holiday, indie…) en el vocabulario canónico del proyecto.\n")
    L.append("Estado de partida (% del total de filas):\n")
    L.append(tabla_claves({n: D[n]["genero"]["completitud"]["estado"] for n in nombres}, nombres, "Estado", ["vacia", "llena", "contradicha"]))
    L.append("Distribución del nivel actual y del nivel propuesto (% del total de filas):\n")
    filas = []
    for k in ("0", "1", "2", "3"):
        fila = [f"nivel `{k}`"]
        for n in nombres:
            fila += [celda_fr(D[n]["genero"]["completitud"]["nivel_actual"], k), celda_fr(D[n]["genero"]["completitud"]["nivel_propuesto"], k)]
        filas.append(fila)
    cols = ["Nivel"]
    for n in nombres:
        cols += [f"{n} · actual", f"{n} · propuesto"]
    L.append(tabla(cols, filas))
    L.append("Qué cambia fila a fila: `rellena` (vacía con propuesta), `sube` (más géneros o uno más preciso), `corrige` / `corrige_parcial` (estaba contradicha o parcial), "
             "`mantiene` (ya está igual o mejor), `sin_propuesta` (sin evidencia):\n")
    L.append(tabla_claves({n: D[n]["genero"]["completitud"]["mejora"] for n in nombres}, nombres, "Mejora",
                          ["rellena", "sube", "corrige", "corrige_parcial", "mantiene", "sin_propuesta", "contradicha_sin_propuesta"], 0.05))
    L.append("**Telenovela** es el caso concreto de \"género más preciso\": Wikidata lo marca como género propio y ningún vendedor lo declara así. "
             "Filas de títulos que Wikidata clasifica como telenovela:\n")
    L.append(tabla_claves({n: D[n]["genero"]["completitud"]["telenovela_wikidata"] for n in nombres}, nombres, "Telenovela según Wikidata"))
    claves_c = ["rellena", "sube", "corrige", "corrige_parcial", "mantiene", "sin_propuesta"]
    for n in nombres:
        c = D[n]["genero"]["completitud"]
        tabla_grupo(L, f"Por país — {n}", c["por_pais"], claves_c, D[n]["meta"]["paises"], con_desglose=False)
        tabla_grupo(L, f"Por publisher — {n}", c["por_publisher"], claves_c, D[n]["meta"]["publishers_top"], con_desglose=False)
        if c.get("por_origen"):
            tabla_grupo(L, f"Por origen del valor — {n}", c["por_origen"], claves_c, con_desglose=False)
        L.append(f"Propuestas más frecuentes ({n}, % del total de filas):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_p(v["pct_filas"]), fmt_p(v["pct_requests"])] for k, v in list(c["propuestas_top"].items())[:20]]
        L.append(tabla(["Propuesta", "Filas", "% filas", "% requests"], filas))

    L.append("## 3. Límites\n")
    L.append("- El género es opinable y IMDb trae hasta tres: por eso hay una categoría `afin` y la cifra dura es `contradice` (nada de lo declarado cabe).\n"
             "- Un match B falla 1 de cada 4 veces; una contradicción de género con confianza B puede ser el match. La muestra trae la confianza para filtrar.\n"
             "- Lo no comparable (lifestyle, viajes, cocina, religión, videojuegos) no se valida ni se propone: IMDb no lo registra.\n"
             "- En el relleno, el origen `imdb` de contentGenre se valida contra la misma fuente: su `coincide` es circular.\n")
    open(os.path.join(out_dir, "reporte-genero.md"), "w", encoding="utf-8").write("\n".join(L))


def reporte_series(D, out_dir):
    nombres = list(D.keys())
    m0 = D[nombres[0]]["meta"]
    L = ["# Reporte — contentSeries: correctitud básica y cuántas filas son serie sin decirlo\n"]
    L.append("**Fuentes:** " + "; ".join(f"`{D[n]['meta']['archivo']}` ({fmt_n(D[n]['meta']['filas'])} filas, columna `{D[n]['meta']['columna_series']}`)" for n in nombres) + ".  ")
    L.append(f"**Generado con:** `scripts/validar_genero_series.py` + `scripts/generar_reporte_genero_series.py`. Corrida del {m0['fecha']}. "
             f"Evidencia: tipo IMDb (movie / tvSeries / tvMiniSeries; match ≥ {m0['confianza_min']}), el título crudo (\"season 2\", \"S01E03\", \"ep 4\") y las demás rutas del "
             f"mismo título (≥ {m0['min_filas_serie']} filas con serie y ≥ {m0['min_rutas_serie']} publishers, como en el relleno).\n")
    L.append("**Convención:** \"serie real\" = un `contentSeries` que no es vacío, ni centinela, ni el hash MD5 de cadena vacía, ni un placeholder (`VOD`, `No Series`, `OTT Studios …`). "
             "En correctitud los % son sobre las filas con serie real; en completitud, sobre el total de filas.\n")
    L.append("---\n")

    L.append("## 1. Correctitud (básica)\n")
    L.append("Solo se juzga lo que IMDb puede juzgar: `coincide` = IMDb dice serie y la serie declarada es el título canónico o el título de la fila; "
             "`otro_nombre` = IMDb dice serie pero la serie declarada se llama distinto (episodio con nombre propio, o error; compatible); "
             "`contradice` = IMDb (A/B) dice película y el título no trae temporada/episodio; `no_evaluable` = sin match o tipo ambiguo (short, video, tvMovie).\n")
    filas = []
    for n in nombres:
        s = D[n]["series"]
        v = s["veredicto"]
        fila = [f"**{n}**", f"{fmt_n(s['filas_con_serie_real'])} ({fmt_p(s['pct_filas_con_serie_real'])} del total; req {fmt_p(s['pct_requests_con_serie_real'])})"]
        for k in ("coincide", "otro_nombre", "contradice", "no_evaluable"):
            fila.append(celda_fr(v, k))
        filas.append(fila)
    L.append(tabla(["Dataset", "Filas con serie real", "coincide", "otro_nombre", "contradice", "no_evaluable"], filas))
    L.append("Qué trae la columna (% del total de filas): serie real vs placeholders:\n")
    L.append(tabla_claves({n: D[n]["series"]["formato"] for n in nombres}, nombres, "Contenido de contentSeries", minimo=0.01))
    claves = ["coincide", "otro_nombre", "contradice", "no_evaluable"]
    for n in nombres:
        s = D[n]["series"]
        tabla_grupo(L, f"Por publisher — {n}", s["por_publisher"], claves, D[n]["meta"]["publishers_top"])
        if s.get("por_origen"):
            L.append("En el relleno, `imdb` se valida contra sí mismo (circular): su `coincide` solo prueba consistencia.\n")
            tabla_grupo(L, f"Por origen del valor — {n}", s["por_origen"], claves)
        top = s["contradicciones_top_titulos"]
        if top:
            L.append(f"Series declaradas en títulos que IMDb dice que son película ({n}; muestra en `validacion-{n}-muestra-series-contradicciones.csv`):\n")
            filas = [[f"`{(t['titulo'] or '')[:35]}`", f"`{t['serie_declarada'][:30]}`", f"{t['imdb']} {(t['imdb_titulo'] or '')[:30]}", t["confianza"], t["publisher"][:28], fmt_n(t["filas"]), fmt_n(t["requests"])]
                     for t in top[:15]]
            L.append(tabla(["Título", "Serie declarada", "IMDb (película)", "Conf.", "Publisher (ej.)", "Filas", "Requests"], filas, ["---"] * 5 + ["---:", "---:"]))

    L.append("## 2. Completitud: qué ES cada fila y qué se le puede poner\n")
    L.append("Para todas las filas se decide si el contenido es **serie**, **película**, **ambiguo** o **desconocido**, y con qué evidencia: `titulo` (trae temporada/episodio), "
             "`imdb` (tipo), `intra_titulo` (otras rutas nombran la serie), `declarado` (solo lo dice el vendedor). Para las series sin nombre se propone `serie_propuesta` "
             "(el título de la fila sin sufijos de temporada/episodio; si no, el nombre que traen las otras rutas; si no, el título canónico IMDb).\n")
    L.append("Qué es cada fila (% del total):\n")
    L.append(tabla_claves({n: D[n]["series"]["completitud"]["que_es"] for n in nombres}, nombres, "Qué es · evidencia", minimo=0.05))
    L.append("Qué implica para la columna: `pelicula_vacio_correcto` (no hay nada que llenar), `ya_nombrada`, `serie_sin_nombre_recuperable` (es serie y hay nombre para proponer), "
             "`serie_sin_nombre` (es serie pero no hay nombre), `pelicula_con_serie_declarada` (contradicción), `nombrada_sin_evidencia`, `sin_evidencia`:\n")
    L.append(tabla_claves({n: D[n]["series"]["completitud"]["mejora"] for n in nombres}, nombres, "Situación",
                          ["ya_nombrada", "serie_sin_nombre_recuperable", "serie_sin_nombre", "pelicula_vacio_correcto", "pelicula_con_serie_declarada", "contradicha", "nombrada_sin_evidencia", "sin_evidencia"], 0.01))
    L.append("**Temporada y episodio.** OpenRTB tiene `content.season` y `content.episode`, que el reporte no expone; pero el título sí los trae a veces "
             "(\"animacars season 2\", \"transplant s4 ep 7\"). Filas donde el título permite extraerlos (% del total):\n")
    L.append(tabla_claves({n: D[n]["series"]["completitud"]["temporada_episodio"] for n in nombres}, nombres, "En el título", ["temporada+episodio", "solo_temporada", "solo_episodio", "nada"]))
    claves_c = ["ya_nombrada", "serie_sin_nombre_recuperable", "pelicula_vacio_correcto", "sin_evidencia"]
    for n in nombres:
        c = D[n]["series"]["completitud"]
        tabla_grupo(L, f"Por país — {n}", c["por_pais"], claves_c, D[n]["meta"]["paises"], con_desglose=False)
        tabla_grupo(L, f"Por publisher — {n}", c["por_publisher"], claves_c, D[n]["meta"]["publishers_top"], con_desglose=False)
        if c.get("por_origen"):
            tabla_grupo(L, f"Por origen del valor — {n}", c["por_origen"], claves_c, con_desglose=False)
        L.append(f"Series propuestas con más filas ({n}; nombre [evidencia]; muestra aleatoria en `validacion-{n}-muestra-series-propuestas.csv`):\n")
        filas = [[f"`{k}`", fmt_n(v["filas"]), fmt_p(v["pct_filas"]), fmt_p(v["pct_requests"])] for k, v in list(c["propuestas_top"].items())[:25]]
        L.append(tabla(["Serie propuesta", "Filas", "% filas", "% requests"], filas))

    L.append("## 3. Límites\n")
    L.append("- La correctitud es deliberadamente básica: IMDb solo sabe si el título es serie o película, no cómo se llama la serie de un episodio con nombre propio; "
             "por eso `otro_nombre` es compatible y no error.\n"
             "- Un match B que cae en una película homónima convierte una serie en `contradice`; el título con temporada/episodio manda sobre IMDb para evitarlo, pero no todos lo traen.\n"
             "- `serie_propuesta` toma el título de la fila (en su idioma) antes que el canónico IMDb (a veces en inglés: *True Love* por *amores verdaderos*).\n"
             "- Temporada/episodio salen de patrones en el título; \"season two\" en letras no se detecta.\n")
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
