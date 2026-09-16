# -*- coding: utf-8 -*-
"""Markdown "que se puede completar de cada content object: metodos y fuentes".

Cruza, para una tanda:
  * el detallado por pais (analizar.py) y requests/eCPM lleno-vacio (requests_ecpm_por_vacio.py):
    cuanto viene lleno hoy, en filas y en requests;
  * el JSON del relleno (enriquecer_externo.py): cuanto se llena con cada metodo y cuanto sigue vacio;
  * las validaciones de categoria (validar_categorias.py) y de genero/series (validar_genero_series.py)
    sobre el consolidado y sobre el relleno: que mas se puede afinar y que tan confiable es lo llenado.

Los textos de metodos, fuentes y limites son fijos (describen el pipeline); las cifras salen de los JSON.

Uso:
    python scripts/generar_reporte_completitud.py reportes/NN 19 \
        --detallado reportes/NN/reporte-content-objects-detallado-v19-consolidado.json \
        --vacio reportes/NN/reporte-requests-ecpm-por-vacio-v19.json \
        --relleno reportes/NN/reporte-relleno-v19.json \
        --cat-consolidado reportes/NN/validacion-categorias-consolidado.json \
        --cat-relleno reportes/NN/validacion-categorias-relleno.json \
        --gs-consolidado reportes/NN/validacion-genero-series-consolidado.json \
        --gs-relleno reportes/NN/validacion-genero-series-relleno.json
"""
import argparse
import json
import os

ORIGEN = {"original": "Venía del vendedor", "intra_titulo": "Copiado de otra ruta del mismo título",
          "app_default": "Valor habitual de la app", "imdb": "IMDb", "wikidata": "Wikidata", "tvmaze": "TVMaze",
          "derivado_genero": "Derivado del género", "derivado_tipo": "Derivado del tipo IMDb (película / serie)",
          "app_semantica": "Semántica de la app (curada a mano)", "sin_dato": "Sigue vacío"}
ORDEN_ORIGEN = ["original", "intra_titulo", "app_default", "imdb", "wikidata", "tvmaze", "derivado_genero",
                "derivado_tipo", "app_semantica", "sin_dato"]
MEJORA_CAT = [("rellena", "Se puede llenar (estaba vacía)"), ("sube", "Se puede afinar (estaba llena, pero genérica)"),
              ("corrige", "Se puede corregir (estaba incorrecta)"), ("mantiene", "Se queda igual (ya está bien)"),
              ("sin_propuesta", "Sin propuesta (vacía y sin evidencia)"),
              ("contradicha_sin_propuesta", "Incorrecta y sin reemplazo posible")]
MEJORA_GEN = [("rellena", "Se puede llenar (estaba vacía)"), ("sube", "Se pueden agregar géneros o uno más preciso"),
              ("corrige", "Se puede corregir (contradecía)"), ("corrige_parcial", "Se corrige en parte (acertaba en parte)"),
              ("mantiene", "Se queda igual (ya está bien)"), ("sin_propuesta", "Sin propuesta (sin evidencia)"),
              ("contradicha_sin_propuesta", "Contradice y no hay reemplazo")]
MEJORA_SER = [("ya_nombrada", "Serie con nombre"), ("serie_sin_nombre_recuperable", "Serie sin nombre, con nombre proponible"),
              ("serie_sin_nombre", "Serie sin nombre, sin nombre proponible"), ("pelicula_vacio_correcto", "Película: el vacío es correcto"),
              ("pelicula_con_serie_declarada", "Película con serie declarada (contradicción)"), ("contradicha", "Contradicha"),
              ("nombrada_sin_evidencia", "Con nombre, sin evidencia para juzgar"), ("sin_evidencia", "Sin evidencia")]
NIVEL_CAT = {"0": "Nivel 0 · nada", "1": "Nivel 1 · solo la vertical", "2": "Nivel 2 · vertical + película/TV (o deporte)",
             "3": "Nivel 3 · vertical + película/TV + género"}
NIVEL_GEN = {"0": "Nivel 0 · vacío", "1": "Nivel 1 · sin género comparable (solo \"entertainment\", \"other\"…)",
             "2": "Nivel 2 · un género", "3": "Nivel 3 · dos o más géneros"}
VER_CAT = [("coincide", "Coincide con la evidencia"), ("compatible", "Compatible (genérica, no contradice)"),
           ("contradice", "Contradice la evidencia"), ("no_evaluable", "No se pudo evaluar")]
VER_GEN = [("coincide", "Coincide"), ("afin", "Parecido (género vecino)"), ("parcial", "Acierta en parte"),
           ("contradice", "Contradice"), ("no_evaluable", "No se pudo evaluar")]
VER_SER = [("coincide", "Coincide"), ("otro_nombre", "Es serie, pero con otro nombre (compatible)"),
           ("contradice", "IMDb dice que es película"), ("no_evaluable", "No se pudo evaluar")]
QUE_ES = {"serie": "Serie", "pelicula": "Película", "ambiguo": "Ambiguo (corto, tv movie, video, especial)",
          "desconocido": "Desconocido (sin evidencia)"}
TEMP = [("temporada+episodio", "Temporada y episodio"), ("solo_temporada", "Solo temporada"),
        ("solo_episodio", "Solo episodio"), ("nada", "Nada")]
SENT = {"Not Available": "N/A", "Not Applicable": "N/A", "Unknown": "Unknown", "[-7]": "[-7]",
        "d41d8cd98f00b204e9800998ecf8427e": "md5-vacío"}


def pct(x):
    return f"{x:.1f}%"


def n(x):
    return f"{x:,}"


def J(p):
    return json.load(open(p, encoding="utf-8"))


def top3(col):
    out = []
    for row in col["distribucion"][:3]:
        v, p = row[0], row[2]
        lab = SENT.get(v)
        out.append(f"*{lab} {pct(p)}*" if lab else f"{v} {pct(p)}")
    return ", ".join(out)


def tabla_kv(dic, orden, titulo_k, con_req=True):
    if con_req:
        L = [f"| {titulo_k} | % filas | % requests |\n|---|---:|---:|"]
    else:
        L = [f"| {titulo_k} | % filas |\n|---|---:|"]
    for k, lab in orden:
        d = dic.get(k)
        if not d or not d.get("filas"):
            continue
        if con_req:
            L.append(f"| {lab} (`{k}`) | {pct(d['pct_filas'])} | {pct(d['pct_requests'])} |")
        else:
            L.append(f"| {lab} (`{k}`) | {pct(d['pct_filas'])} |")
    return L


def niveles(dic_actual, dic_prop, etiquetas):
    """Agrega nivel_actual (claves 'estado|nivel' o 'nivel') y nivel_propuesto por nivel 0-3."""
    act = {}
    for k, d in dic_actual.items():
        lv = k.split("|")[-1]
        act[lv] = act.get(lv, 0) + d["pct_filas"]
    L = ["| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |\n|---|---:|---:|"]
    for lv in "0123":
        L.append(f"| {etiquetas[lv]} | {pct(act.get(lv, 0))} | {pct(dic_prop.get(lv, {}).get('pct_filas', 0))} |")
    return L


def veredictos(a, b, orden, nombre_a="Consolidado (tal como llega)", nombre_b="Relleno (tras el pipeline)"):
    L = [f"| Veredicto | {nombre_a} | {nombre_b} |\n|---|---:|---:|"]
    for k, lab in orden:
        L.append(f"| {lab} (`{k}`) | {pct(a.get(k, {}).get('pct_filas', 0))} | {pct(b.get(k, {}).get('pct_filas', 0))} |")
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("carpeta")
    ap.add_argument("version", type=int)
    for k in ("detallado", "vacio", "relleno", "cat-consolidado", "cat-relleno", "gs-consolidado", "gs-relleno"):
        ap.add_argument(f"--{k}", required=True)
    a = ap.parse_args()
    V = a.version
    det, vac, rel = J(a.detallado), J(a.vacio), J(a.relleno)
    catc, catr, gsc, gsr = J(a.cat_consolidado), J(a.cat_relleno), J(a.gs_consolidado), J(a.gs_relleno)
    filas, req = det["filas"], det["total_requests"]
    cols, vt = det["columnas"], vac["paises"]["(todos)"]["columnas"]
    R = rel["columnas"]

    def hoy(c):
        return cols[c]["fill_rate_filas_pct"], (vt[c]["lleno"]["pct_requests"] if c in vt else 100.0)

    L = [f"# Qué se puede completar de cada content object: métodos y fuentes (consolidado v10 a v{V})\n",
         f"**Fuente:** `inventory-consolidado-v10-a-v{V}.csv` — {n(filas)} filas únicas, {n(req)} requests (métricas del corte v{V}). "
         f"**Relleno:** `inventory-consolidado-v10-a-v{V}-relleno.csv` (no versionado), generado con `scripts/enriquecer_externo.py --wikidata`, "
         f"corrida del {rel['fecha']} → `reporte-relleno-v{V}.json`. Títulos distintos: {n(rel['titulos_distintos'])}; con match en IMDb: "
         f"{n(rel['titulos_con_imdb'])}; consultados por primera vez en esta corrida: {n(rel['titulos_nuevos_consultados'])}.",
         "**Validaciones:** `scripts/validar_categorias.py` y `scripts/validar_genero_series.py` sobre el consolidado y sobre el relleno "
         "(`validacion-*.json` en esta carpeta). Tablas generadas con `scripts/generar_reporte_completitud.py`.\n",
         "## Cómo leer este reporte\n",
         "- Cada fila del consolidado es una **combinación** de 14 dimensiones (país × publisher × app × género × …), no un programa. "
         "El mismo contenido llega por varias rutas de venta y cada ruta manda la metadata que quiere: por eso la respuesta a un vacío "
         "muchas veces ya está escrita en otra fila del mismo título.",
         "- Una celda cuenta como **llena** solo si trae dato útil: no cuentan los centinelas (`Not Available`, `Unknown`, `[-7]`, el MD5 de "
         "cadena vacía, macros sin reemplazar).",
         "- Los % son sobre el total de filas del consolidado (y, cuando se indica, sobre el total de requests). \"Hoy\" es como llega; "
         "\"tras el relleno\" es después de correr el pipeline con los candados por defecto.",
         "- **Se puede completar** tiene dos lecturas: (1) lo que el pipeline **ya llena** automáticamente (tabla de orígenes por columna) y "
         "(2) lo que la validación contra fuentes abiertas dice que **se podría afinar o corregir** además (nivel de detalle alcanzable, "
         "géneros adicionales, nombre de serie proponible). Lo segundo no se escribe al CSV: son propuestas fila a fila en los `validacion-*.json` "
         "y en los CSV `*-filas.csv` de la raíz.\n",
         "## Fuentes\n",
         "| Fuente | Qué aporta | Cómo se usa | Licencia / límite |\n|---|---|---|---|",
         "| **El propio consolidado** (otras filas del mismo título; el comportamiento de cada app) | Categoría, serie, duración, idioma, rating, género | Se normaliza el título a `titulo_clave` (url-decode, mojibake, sin \": trailer\", \"season N\", SxxEyy) y se agrupan las filas; por app se mide qué valor manda cuando manda | Sin costo. Es la fuente más precisa (mismo contenido, otra ruta) y la que más aporta |",
         "| **Semántica de apps curada a mano** (`cache-enriquecimiento/semantica_apps.csv`) | Modo de entrega (lineal / VOD) por app | Ficha de tienda y evidencia del dataset, revisada a mano; solo las filas con `aplicar=si` rellenan | 16 apps revisadas; solo 2 (Live TV de TCL, Coolita Channel) son lineales puras y se aplican |",
         "| **IMDb Non-Commercial Datasets** (`title.basics`, `title.akas` es/pt/en, `title.ratings`, `title.episode`) | Tipo (película / serie / corto…), géneros, título canónico, año, duración | Match offline por título normalizado y alias en español/portugués/inglés; confianza A–D (A ≈ 90 %+, B ≈ 75 %; se usa hasta B) | Solo uso no comercial; ~750 MB descargados a `cache-enriquecimiento/imdb/` |",
         "| **Wikidata** (SPARQL, vía el id IMDb `P345`) | Idioma original (`P364`), duración (`P2047`), géneros (`P136`, p. ej. telenovela), clasificación (`P3834`, rara) | Solo para títulos con match IMDb; resultado cacheado por título | CC0, sin API key; el idioma es el **original**, no el de emisión |",
         "| **TVMaze** (opcional, `--tvmaze`) | Idioma, géneros, duración de series | Series sin match IMDb | CC BY-SA, ~20 req/10 s. **No se usó en esta corrida** |",
         "| **Taxonomías IAB Tech Lab** (Content Taxonomy 1.0, 2.2, 3.0) | Si un código declarado existe y qué significa; códigos propuestos | Descargadas a `cache-enriquecimiento/iab/`; cada código se traduce a (vertical, forma, género) para comparar entre taxonomías | Abiertas (GitHub de IAB Tech Lab) |",
         "\n*Cache incremental: `cache-enriquecimiento/titulos.json` guarda el resultado de cada título; en cada tanda solo se consultan los títulos nuevos.*\n",
         "## Métodos (en orden: el primero que llena gana, y queda anotado en `<columna>_origen`)\n",
         "| Método (`origen`) | Qué hace | Candado | Columnas donde aplica |\n|---|---|---|---|",
         "| `intra_titulo` | Copia el valor que otra fila del **mismo título** ya trae (misma película, otra ruta de venta) | El valor debe dominar ≥ 80 % de las filas con dato de ese título; en contentSeries además ≥ 30 filas y ≥ 2 publishers | category, series, length, language, rating, genre |",
         "| `app_default` | Para títulos donde ninguna ruta manda el dato, usa el valor **constante** que esa app manda cuando sí lo manda | La app debe mandar el mismo valor ≥ 95 % de las veces y tener ≥ 200 filas con dato | category, length, language, rating, genre (no livestream) |",
         "| `imdb` | Match del título contra IMDb: tipo, géneros, título canónico | Confianza A o B | series (tvSeries → título canónico), genre |",
         "| `wikidata` | Idioma original, duración, géneros y clasificación del ítem ligado al id IMDb | Solo títulos con match IMDb | language, rating (y genre vía telenovela) |",
         "| `derivado_genero` | Traduce el género de la misma fila a categoría IAB (mapa aprendido de las filas que traen ambas columnas: deportes → `[IAB17]`, noticias → `[IAB12]`…) | Solo géneros que definen vertical | category |",
         "| `derivado_tipo` | Desempata con el tipo IMDb cuando el género no define categoría: movie → `[IAB1-5]`, tvSeries → `[IAB1-7]` | Match IMDb A/B | category (y livestream = 0 solo con flag explícito) |",
         "| `app_semantica` + señales del vendedor | Modo de entrega: `contentSeries = \"VOD\"` → 0, `\"… Livestream\"` → 1; app lineal pura → 1, VOD pura → 0 | Solo apps con `aplicar=si` en la tabla curada | livestream |",
         "\n## Resumen: cuánto viene lleno hoy y cuánto queda tras el relleno\n",
         "| Columna | Hoy (% filas) | Hoy (% requests) | Tras el relleno (% filas) | Ganancia | Sigue vacío | Método que más aporta |\n|---|---:|---:|---:|---:|---:|---|"]
    for c in ["contentGenre", "contentTitle", "contentRating", "contentLanguage", "contentIsLiveStream",
              "contentCategory", "contentLength", "contentSeries"]:
        hf, hr = hoy(c)
        if c in R:
            d = R[c]
            org = {k: v for k, v in d["origen"].items() if k not in ("original", "sin_dato")}
            mejor = max(org, key=org.get) if org else "—"
            L.append(f"| {c} | {pct(hf)} | {pct(hr)} | {pct(d['pct_final'])} | +{d['pct_final'] - d['pct_original']:.1f} pp | "
                     f"{pct(d['origen'].get('sin_dato', 0))} | {ORIGEN.get(mejor, mejor)} (`{mejor}`) |")
        else:
            L.append(f"| {c} | {pct(hf)} | {pct(hr)} | {pct(hf)} | — | {pct(100 - hf)} | No se rellena (ver abajo) |")
    L.append("\n*contentIsTitlePresent y Publisher vienen al 100 % y no entran. \"Ganancia\" son puntos porcentuales de filas del consolidado.*\n")

    def bloque(c, metodo, limites, extra=None):
        hf, hr = hoy(c)
        L.append(f"## {c}\n")
        L.append(f"**Hoy:** {pct(hf)} de las filas y {pct(hr)} de los requests traen dato útil. Top 3 referencias: {top3(cols[c])}.\n")
        if c in R:
            d = R[c]
            L.append(f"**Tras el relleno:** {pct(d['pct_final'])} de las filas (de {pct(d['pct_original'])}). "
                     "Origen del valor final, sobre todas las filas del consolidado:\n")
            L.append("| Origen | % filas |\n|---|---:|")
            for k in ORDEN_ORIGEN:
                if k in d["origen"] and d["origen"][k] > 0:
                    L.append(f"| {ORIGEN[k]} (`{k}`) | {pct(d['origen'][k])} |")
            L.append("")
        L.append("**Método y fuentes:** " + metodo + "\n")
        if extra:
            L.extend(extra)
        L.append("**Límites:** " + limites + "\n")

    # ---- contentCategory ----
    cc = catc["completitud"]
    extra = ["**Qué más se puede afinar (validación del consolidado contra IMDb / Wikidata / taxonomías IAB):**\n"]
    extra += tabla_kv(cc["mejora"], MEJORA_CAT, "Mejora posible")
    extra.append("")
    extra += niveles(cc["nivel_actual"], cc["nivel_propuesto"], NIVEL_CAT)
    extra.append("\n*El nivel mide cuántos atributos conoce la categoría: vertical (entretenimiento, deportes…), forma (película / TV) y género. "
                 "La propuesta usa Content Taxonomy 2.2 (p. ej. `Movies > Drama Movies`) porque es la que permite los tres.*\n")
    ev = cc["evidencia"]
    extra.append("Evidencia disponible por fila: " +
                 ", ".join(f"{k} {pct(v['pct_filas'])}" for k, v in sorted(ev.items(), key=lambda kv: -kv[1]['pct_filas'])) +
                 " (*externa* = match IMDb; *interna* = el género de la misma fila; *serie* = trae nombre de serie; *ninguna* = sin nada que cruzar).\n")
    top = sorted(cc["propuestas_top"].items(), key=lambda kv: -kv[1]["pct_filas"])[:5]
    extra.append("Categorías más propuestas: " + "; ".join(f"`{k}` {pct(v['pct_filas'])}" for k, v in top) + ".\n")
    extra.append("**Confiabilidad de lo que trae y de lo que se llena (filas con categoría, % sobre esas filas):**\n")
    extra += veredictos(catc["correctitud"]["veredicto_total"], catr["correctitud"]["veredicto_total"], VER_CAT)
    extra.append("")
    bloque("contentCategory",
           "cuatro escalones. `intra_titulo` copia la categoría que otra ruta del mismo título ya manda (Vidaa o Equativ suelen mandarla; OTTera y TCL mandan `[-7]`). "
           "`app_default` aplica el valor constante de la app (OTTera → MovieArk manda `[IAB1]` el 99 % de las veces). `derivado_genero` traduce el contentGenre de la misma fila "
           "con el mapa IAB 1.0 aprendido del propio dataset (~150k filas traen ambas columnas). `derivado_tipo` usa el tipo IMDb para separar película (`[IAB1-5]`) de serie (`[IAB1-7]`). "
           "La validación va un paso más allá y propone, con la taxonomía 2.2, la categoría más fina que la evidencia permite (forma + género).",
           "el consolidado mezcla tres taxonomías (1.0, 2.2, 3.0) y texto libre (`[sports]`, `[Live]`); lo declarado es en su mayoría genérico (nivel 1, solo la vertical). "
           "Los defaults por app (`[IAB12]` de Vidaa, `[IAB1]` de OTTera) son correctos como vertical pero no como género, y `intra_titulo` los propaga. "
           "Un match IMDb de confianza B acierta ~75 %, así que parte de las \"contradicciones\" son matches equivocados; se separan con `genero_vs_imdb` en el CSV fila a fila.",
           extra)

    # ---- contentGenre ----
    gc, gr = gsc["genero"], gsr["genero"]
    extra = ["**Qué más se puede afinar (validación del consolidado):**\n"]
    extra += tabla_kv(gc["completitud"]["mejora"], MEJORA_GEN, "Mejora posible")
    extra.append("")
    extra += niveles(gc["completitud"]["nivel_actual"], gc["completitud"]["nivel_propuesto"], NIVEL_GEN)
    tw = gc["completitud"].get("telenovela_wikidata", {}).get("propuesta")
    if tw:
        extra.append(f"\n*Wikidata (`P136`) permite etiquetar como telenovela {pct(tw['pct_filas'])} de las filas "
                     f"({pct(tw['pct_requests'])} de los requests) que hoy solo dicen drama/romance.*")
    top = sorted(gc["completitud"]["propuestas_top"].items(), key=lambda kv: -kv[1]["pct_filas"])[:5]
    extra.append("\nCombinaciones más propuestas: " + "; ".join(f"`{k}` {pct(v['pct_filas'])}" for k, v in top) + ".\n")
    extra.append("**Confiabilidad (filas con género comparable, % sobre esas filas):**\n")
    extra += veredictos(gc["veredicto"], gr["veredicto"], VER_GEN)
    extra.append("")
    bloque("contentGenre",
           "`intra_titulo` y `app_default` como en las demás columnas; para lo que sigue vacío, los géneros del match IMDb (`title.basics`, hasta tres) traducidos al vocabulario "
           "canónico del proyecto (`norm_genre`), y los géneros de Wikidata (`P136`) para lo que IMDb no expresa (telenovela, holiday). La validación compara cada género declarado "
           "con IMDb/Wikidata por *conceptos* (thriller/misterio/crimen → crimen-misterio, anime → animación) y propone géneros adicionales o más precisos.",
           "es la columna que mejor viene (>90 %), así que el margen es afinar, no llenar. El vocabulario del vendedor es libre (`Drama` y `drama` son valores distintos en la fuente; "
           "`entertainment`, `other`, `movies` no son géneros comparables) y géneros que IMDb no maneja (lifestyle, viajes, religión, videojuegos) no se pueden juzgar. "
           "Solo la mitad de las filas tiene match externo; el resto queda como \"no evaluable\".",
           extra)

    # ---- contentSeries ----
    sc, sr = gsc["series"], gsr["series"]
    qe = {}
    for k, d in sc["completitud"]["que_es"].items():
        q = k.split("|")[0]
        qe[q] = qe.get(q, 0) + d["pct_filas"]
    extra = ["**Qué es cada fila según la evidencia (consolidado):**\n", "| Qué es | % filas |\n|---|---:|"]
    for q in ("serie", "pelicula", "ambiguo", "desconocido"):
        extra.append(f"| {QUE_ES[q]} | {pct(qe.get(q, 0))} |")
    extra.append("\n**Qué se puede hacer con cada fila:**\n")
    extra += tabla_kv(sc["completitud"]["mejora"], MEJORA_SER, "Situación")
    extra.append("\n**Temporada / episodio que trae el título** (candidatos a `content.season` / `content.episode`):\n")
    extra += tabla_kv(sc["completitud"]["temporada_episodio"], TEMP, "El título trae", con_req=False)
    top = sorted(sc["completitud"]["propuestas_top"].items(), key=lambda kv: -kv[1]["pct_filas"])[:5]
    extra.append("\nNombres de serie más propuestos (`[titulo]` = del propio título sin sufijos, `[imdb]` = título canónico): " +
                 "; ".join(f"`{k}` {pct(v['pct_filas'])}" for k, v in top) + ".\n")
    extra.append("**Confiabilidad de las series declaradas (filas con nombre de serie real, % sobre esas filas):**\n")
    extra += veredictos(sc["veredicto"], sr["veredicto"], VER_SER)
    extra.append("")
    bloque("contentSeries",
           "el pipeline llena solo lo seguro: `imdb` cuando el match (A/B) dice tvSeries o tvMiniSeries, con el título canónico de IMDb; `intra_titulo` cuando otras rutas del mismo "
           "título nombran la serie (≥ 30 filas y ≥ 2 publishers, porque un episodio puede llamarse igual que una película). La validación identifica además qué filas **son** serie "
           "sin decirlo (IMDb, el título con \"season N\" / S01E03 / \"ep N\", o las otras rutas) y propone un nombre: el título sin sufijos de temporada/episodio, el que traen las otras rutas, o el canónico IMDb.",
           "la mayor parte del vacío es correcta: las películas no pertenecen a ninguna serie. Casi la mitad de las filas no tiene evidencia (títulos sin match, placeholders como `roku` / `epg`). "
           "Roku manda un hash MD5 en vez del nombre y algunos vendedores mandan `VOD` o macros sin reemplazar; todo eso cuenta como vacío.",
           extra)

    # ---- contentLength ----
    bloque("contentLength",
           "`intra_titulo` (otra ruta del mismo título trae el código) y `app_default`. IMDb (`runtimeMinutes`) y Wikidata (`P2047`) traen la duración en minutos de la mayoría de los "
           "títulos con match, pero esa duración solo se escribe con `--length-desde-runtime`, apagado por defecto.",
           "contentLength no es una duración: es un **código 1–8** (rangos de duración; el mapa por defecto del pipeline es 1: ≤ 1 min, 2: ≤ 5, 3: ≤ 15, 4: ≤ 30, 5: ≤ 60, 6: ≤ 120, 7: ≤ 180, 8: más). "
           "Mientras PubMatic no confirme los cortes de cada código, convertir minutos a código es una suposición y por eso no se aplica. Con esa confirmación, el runtime externo cubriría "
           "buena parte de lo que sigue vacío (títulos con match IMDb).")

    # ---- contentLanguage ----
    bloque("contentLanguage",
           "`intra_titulo` (canonizando `English` → `en`, `Spanish` → `es`, porque desde v16 conviven el código ISO y el nombre), `app_default` y, para lo que sigue vacío, el idioma "
           "**original** del título según Wikidata (`P364`).",
           "el idioma original no siempre es el de emisión (una película en inglés doblada al español en un canal FAST). Por eso Wikidata se usa al final y aporta poco; casi todo el relleno "
           "viene de otras rutas del mismo título.")

    # ---- contentIsLiveStream ----
    bloque("contentIsLiveStream",
           "mide el **modo de entrega** (canal lineal vs on demand), no el contenido, así que no se propaga por título (la misma película puede ir en un canal lineal y en VOD) ni por app "
           "(MovieArk marca 1 todo su catálogo). Solo se usan dos señales: lo que el vendedor deja en contentSeries (`VOD` → 0, `… Livestream` → 1) y la semántica de la app validada a mano "
           "(`semantica_apps.csv`: ficha de tienda + evidencia del dataset). El tipo IMDb (película → 0) existe como opción pero está apagado: una película en un canal lineal es livestream = 1.",
           "todo lo declarado por los vendedores es `1`; el `0` nunca llega. De 16 apps revisadas solo dos son lineales puras; las 13 mixtas (MovieArk, TCL CHANNEL…) no se pueden resolver "
           "sin saber por qué ruta se sirvió cada request. La mitad del consolidado seguirá vacía hasta que el vendedor lo mande.")

    # ---- contentRating ----
    bloque("contentRating",
           "`intra_titulo` (canonizando la escala nueva: `All Ages` = g, `Teen` = tv-pg, `Teen Plus` = tv-14, `Adults` = tv-ma, `Unrated` = nr), `app_default` y, marginalmente, la "
           "clasificación de Wikidata (`P3834`).",
           "no hay fuente abierta de clasificaciones por edad con cobertura: los datasets públicos de IMDb no traen la Parental Guide y en Wikidata `P3834` es rara. Lo que queda vacío "
           "son títulos que ninguna ruta clasifica; solo el vendedor puede completarlo. El consolidado mezcla dos escalas (`tv-14` y `Teen Plus` para el mismo título); `rating_franja` "
           "de `normalizar_monetizar.py` las unifica en franjas de edad.")

    # ---- contentTitle ----
    hf, hr = hoy("contentTitle")
    reales = catc["meta"]["filas_con_titulo_real"]
    L.append("## contentTitle\n")
    L.append(f"**Hoy:** {pct(hf)} de las filas y {pct(hr)} de los requests traen algo. Top 3 referencias: {top3(cols['contentTitle'])}.\n")
    L.append("**Método y fuentes:** no se rellena. El título es la **llave** de todo lo demás: es lo que se normaliza (`titulo_clave`) y se busca en IMDb/Wikidata, y es lo que agrupa las rutas "
             "de venta para `intra_titulo`. Lo que sí se hace es medir cuánto de lo \"lleno\" es un título de verdad: se descuentan placeholders (`roku`, `epg`, `vod`), nombres de canal "
             "(`las estrellas`, `canal 5`), slugs técnicos (`*_trailer`), macros sin reemplazar (`{{content_title}}`), texto sin letras o de una o dos letras y encoding roto "
             f"(en esta tanda, {n(reales)} filas, {pct(100 * reales / filas)} del consolidado, pasan el filtro).\n")
    L.append("**Límites:** sin título no hay nada que cruzar afuera: una fila vacía en contentTitle solo la puede completar el vendedor. Y el vacío pesa más en tráfico que en catálogo "
             f"({pct(100 - hr)} de los requests vs {pct(100 - hf)} de las filas): son pocas combinaciones con muchos requests.\n")

    out = os.path.join(a.carpeta, f"reporte-completitud-content-objects-v{V}.md")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L).rstrip("\n") + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
