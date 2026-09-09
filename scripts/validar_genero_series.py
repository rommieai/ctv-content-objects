# -*- coding: utf-8 -*-
"""Validacion de contentGenre y contentSeries contra fuentes abiertas — pipeline repetible.

Hermano de validar_categorias.py (misma evidencia, mismo caché, misma estructura de salida):

  contentGenre    correctitud (los generos declarados, ¿coinciden con IMDb/Wikidata?) y
                  completitud (¿se pueden declarar mas generos, o mas precisos?)
  contentSeries   correctitud basica (la serie declarada, ¿es una serie segun IMDb? ¿es la
                  misma?) y completitud (¿que filas SON serie y no lo dicen, con que nombre
                  se podria llenar, y que temporada/episodio trae el titulo?)

EVIDENCIA (solo externa + el propio titulo; aqui no hay evidencia "interna" porque el genero
ES la columna que se valida):
  * cache-enriquecimiento/titulos.json: match IMDb (tipo, generos, titulo canonico,
    confianza A-D) y generos Wikidata (P136) por titulo normalizado.
  * el titulo crudo: "x season 2", "S01E03", "ep 4" -> es serie, y de paso trae la
    temporada/episodio.
  * las demas filas del mismo titulo (contentSeries): si otras rutas nombran la serie.

GENERO — como se compara
  Los generos declarados se normalizan con el diccionario del proyecto (norm_genre) y se
  colapsan a CONCEPTOS comparables con IMDb (thriller/misterio/crimen -> crimen-misterio,
  accion/aventura/belico -> accion-aventura, anime -> animacion...). Generos que IMDb no
  puede expresar (lifestyle, viajes, gastronomia, religion, educacion, videojuegos,
  "entertainment", "other", "movies", "tv") no se juzgan. Por cada genero comparable:
      acierta   esta entre los generos IMDb/Wikidata del titulo
      afin      no esta, pero es vecino (telenovela~drama/romance, thriller~terror,
                infantil~animacion, documental~reality...)
      choca     no esta ni es vecino
  Veredicto de la fila: coincide (todo acierta) | afin (nada choca, nada acierta) |
  parcial (aciertos y choques) | contradice (choca y nada acierta) | no_evaluable.
  Nivel de granularidad: 0 vacio, 1 sin genero comparable (solo "entertainment"/"other"),
  2 un genero comparable, 3 dos o mas. Propuesta: los generos IMDb (hasta 3) + los extra de
  Wikidata (telenovela, holiday...) en el vocabulario canonico del proyecto.

SERIES — como se compara
  Correctitud (filas con serie declarada real, es decir ni placeholder ni hash):
      coincide     IMDb dice serie y el nombre declarado es el titulo canonico o el titulo
                   de la fila
      otro_nombre  IMDb dice serie pero la serie declarada se llama distinto (episodio con
                   nombre propio, o error): compatible, se lista
      contradice   IMDb (A/B) dice pelicula y el titulo no trae temporada/episodio
      no_evaluable sin match, o tipo ambiguo (short, video, tvMovie)
  Completitud (todas las filas): que ES cada fila —
      pelicula     IMDb movie (sin marcas de serie en el titulo): el vacio es correcto
      serie        por IMDb (tvSeries/tvMiniSeries), por el titulo (season/S01E03/ep N) o
                   porque otras rutas del mismo titulo nombran la serie (>= --min-filas-serie
                   filas y >= --min-rutas-serie publishers, como en enriquecer_externo.py)
      desconocido  sin evidencia
  Para las series sin nombre se propone `serie_propuesta` (titulo de la fila sin sufijos de
  temporada/episodio > nombre que traen las otras rutas > titulo canonico IMDb) y, si el
  titulo lo trae, `temporada` y `episodio` (candidatos a content.season / content.episode).

SALIDAS
  <prefijo>.json, <prefijo>-filas.csv (--filas), y muestras:
  <prefijo>-muestra-genero-contradicciones.csv, <prefijo>-muestra-series-contradicciones.csv,
  <prefijo>-muestra-series-propuestas.csv

Uso:
    python scripts/validar_genero_series.py inventory-consolidado-v10-a-v17.csv \
        reportes/16-validacion-genero-series-v17/validacion-consolidado --nombre consolidado \
        --filas validacion-genero-series-v17-consolidado-filas.csv
    (con el relleno se validan contentGenre_relleno / contentSeries_relleno y se desglosa por _origen)
"""
import argparse
import csv
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enriquecer_externo import (es_util, normalizar_titulo, titulo_real, SERIES_PLACEHOLDER,  # noqa: E402
                                IMDB_GENERO_MAP, RE_TRAILER, RE_SXXEXX, RE_EPREFIX, RE_EP)
from analizar_genero_titulo_paises import norm_genre, clasificar_genero_no_mapeado  # noqa: E402
from validar_categorias import (WIKIDATA_GENERO, forma_por_titulo, Agg, pct,  # noqa: E402
                                CONFIANZA_ORDEN)

csv.field_size_limit(10 ** 8)

# genero canonico del proyecto -> concepto comparable con IMDb (None = no comparable)
CONCEPTO = {
    "drama": "drama", "comedia": "comedia", "romance": "romance", "terror": "terror",
    "thriller": "crimen-misterio", "misterio": "crimen-misterio", "crimen": "crimen-misterio",
    "accion": "accion-aventura", "aventura": "accion-aventura", "belico": "accion-aventura",
    "western": "western", "sci-fi": "sci-fi", "fantasia": "fantasia", "documental": "documental",
    "infantil-familia": "infantil-familia", "animacion": "animacion", "anime": "animacion",
    "reality": "reality", "talk show": "talk show", "concursos": "concursos",
    "telenovela": "telenovela", "deportes": "deportes", "noticias": "noticias", "musica": "musica",
}
# IMDb -> concepto (misma tabla que validar_categorias, sin los extras)
IMDB_CONCEPTO = {"Drama": "drama", "Comedy": "comedia", "Romance": "romance", "Horror": "terror",
                 "Thriller": "crimen-misterio", "Mystery": "crimen-misterio", "Crime": "crimen-misterio",
                 "Film-Noir": "crimen-misterio", "Action": "accion-aventura", "Adventure": "accion-aventura",
                 "War": "accion-aventura", "Western": "western", "Sci-Fi": "sci-fi", "Fantasy": "fantasia",
                 "Documentary": "documental", "Biography": "documental", "History": "documental",
                 "News": "noticias", "Sport": "deportes", "Music": "musica", "Musical": "musica",
                 "Family": "infantil-familia", "Animation": "animacion", "Reality-TV": "reality",
                 "Talk-Show": "talk show", "Game-Show": "concursos"}
# vecinos: declarar A cuando la fuente dice B no es un error claro
AFINES = {
    "telenovela": {"drama", "romance"}, "drama": {"telenovela", "romance", "crimen-misterio"},
    "romance": {"telenovela", "drama", "comedia"}, "comedia": {"romance", "infantil-familia"},
    "terror": {"crimen-misterio", "sci-fi", "fantasia"}, "crimen-misterio": {"terror", "drama", "accion-aventura"},
    "accion-aventura": {"crimen-misterio", "sci-fi", "fantasia", "western"},
    "sci-fi": {"fantasia", "terror", "accion-aventura"}, "fantasia": {"sci-fi", "infantil-familia", "animacion"},
    "documental": {"reality", "noticias", "deportes", "musica", "talk show"},
    "infantil-familia": {"animacion", "comedia", "fantasia"}, "animacion": {"infantil-familia", "fantasia"},
    "reality": {"documental", "concursos", "talk show"}, "talk show": {"reality", "noticias", "comedia"},
    "concursos": {"reality"}, "deportes": {"documental"}, "noticias": {"documental", "talk show"},
    "musica": {"documental"}, "western": {"accion-aventura", "drama"},
}
CANON_DESDE_CONCEPTO = {"crimen-misterio": "thriller", "accion-aventura": "accion"}
RE_TEMP = re.compile(r"\b(?:season|temporada|temp|t|s)\s*\.?\s*(\d{1,2})\b", re.I)
RE_EPI = re.compile(r"\b(?:episode|episodio|ep|cap[ií]tulo|cap|e)\s*\.?\s*(\d{1,4})\b", re.I)
RE_SE = re.compile(r"\bs(\d{1,2})\s*(?:ep\.?|e)\s*(\d{1,3})\b", re.I)
RE_TEMP_LETRAS = re.compile(r"\s*[-:|(,]?\s*\b(season|temporada|series)\s+(one|two|three|four|five|six|seven|eight|"
                            r"nine|ten|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|[ivx]{1,4})\b\)?.*$", re.I)


def temporada_episodio(titulo):
    """('2', '5') si el titulo crudo trae temporada/episodio; ('', '') si no."""
    t = titulo or ""
    m = RE_SE.search(t)
    if m:
        return str(int(m.group(1))), str(int(m.group(2)))
    temp = RE_TEMP.search(t)
    epi = RE_EPI.search(t)
    return (str(int(temp.group(1))) if temp else ""), (str(int(epi.group(1))) if epi else "")


def nombre_serie_desde_titulo(titulo):
    """Titulo crudo sin sufijos de temporada/episodio/trailer, conservando mayusculas."""
    s = (titulo or "").strip()
    s = RE_TRAILER.sub("", s)
    s = RE_SXXEXX.sub("", s)
    s = RE_EPREFIX.sub("", s)
    s = RE_EP.sub("", s)
    s = RE_TEMP_LETRAS.sub("", s)
    s = s.strip(" -:|,.(")
    if s.count("(") > s.count(")"):
        s = s[:s.rfind("(")].strip(" -:|,.")
    return s


def generos_esperados(rec, conf_ok):
    """Del cache -> (set de conceptos, lista IMDb original, tipo, confianza) o None."""
    imdb = (rec or {}).get("imdb") or {}
    if not imdb or imdb.get("confianza", "D") not in conf_ok:
        return None
    conceptos = {IMDB_CONCEPTO[g] for g in imdb.get("generos", []) if g in IMDB_CONCEPTO}
    extras = set()
    for g in ((rec or {}).get("wikidata") or {}).get("generos", []) or []:
        low = g.lower()
        for kw, gc in WIKIDATA_GENERO:
            if kw in low:
                if gc in CONCEPTO.values():
                    extras.add(gc)
                break
    return {"conceptos": conceptos | extras, "imdb": imdb.get("generos", []), "wikidata_extra": extras - conceptos,
            "tipo": imdb.get("tipo", ""), "confianza": imdb.get("confianza"), "id": imdb.get("id"),
            "titulo": imdb.get("titulo", "")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("prefijo_salida")
    ap.add_argument("--nombre", default="")
    ap.add_argument("--cache-dir", default="cache-enriquecimiento")
    ap.add_argument("--confianza-min", default="B", choices=list("ABCD"))
    ap.add_argument("--paises", default="Mexico,Colombia,Chile")
    ap.add_argument("--top-publishers", type=int, default=12)
    ap.add_argument("--muestra", type=int, default=400)
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--filas", default="")
    ap.add_argument("--min-filas-serie", type=int, default=30)
    ap.add_argument("--min-rutas-serie", type=int, default=2)
    args = ap.parse_args()
    conf_ok = set(CONFIANZA_ORDEN[:CONFIANZA_ORDEN.index(args.confianza_min) + 1])
    random.seed(args.semilla)
    inicio = datetime.now()
    cache_path = os.path.join(args.cache_dir, "titulos.json")
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}

    filas = []
    with open(args.entrada, encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        columnas = lector.fieldnames
        for d in lector:
            filas.append(d)
    n = len(filas)
    col_gen = "contentGenre_relleno" if "contentGenre_relleno" in columnas else "contentGenre"
    col_ser = "contentSeries_relleno" if "contentSeries_relleno" in columnas else "contentSeries"
    org_gen = "contentGenre_origen" if col_gen.endswith("_relleno") and "contentGenre_origen" in columnas else None
    org_ser = "contentSeries_origen" if col_ser.endswith("_relleno") and "contentSeries_origen" in columnas else None
    print(f"{n} filas; columnas validadas: {col_gen}, {col_ser}", file=sys.stderr)

    # ---- pasada 1: titulo, series conocidas por titulo (para intra) --------------------------
    series_por_titulo = defaultdict(Counter)
    rutas_serie = defaultdict(set)
    for d in filas:
        t = (d.get("contentTitle") or "").strip()
        k = normalizar_titulo(t) if titulo_real(t) else ""
        d["_k"] = k
        d["_req"] = int(float(d.get("Total Requests") or 0))
        s = (d.get(col_ser) or "").strip()
        d["_ser_ok"] = es_util("contentSeries", s) and s.lower() not in SERIES_PLACEHOLDER
        if k and d["_ser_ok"]:
            series_por_titulo[k][s] += 1
            rutas_serie[k].add(d.get("Publisher", ""))
    serie_intra = {}
    for k, c in series_por_titulo.items():
        if sum(c.values()) >= args.min_filas_serie and len(rutas_serie[k]) >= args.min_rutas_serie:
            v, m = c.most_common(1)[0]
            if m / sum(c.values()) >= 0.8:
                serie_intra[k] = v

    tot_req = sum(d["_req"] for d in filas)
    paises = [p.strip() for p in args.paises.split(",") if p.strip()]
    pub_top = [p for p, _ in Counter(d.get("Publisher", "") for d in filas).most_common(args.top_publishers)]
    A = defaultdict(Agg)
    gen_conf = Agg()           # (declarado -> imdb) en contradicciones
    gen_choque_por_genero = Agg()
    gen_titulos = Agg(); gen_ejemplo = {}
    ser_pares = Agg(); ser_titulos = Agg(); ser_ejemplo = {}
    ser_prop_top = Agg()
    gen_prop_top = Agg()
    m_gen, m_ser, m_prop = [], [], []

    salida_cols = [c for c in ("Publisher", "App Name", "Country", "contentTitle", "contentGenre", "contentSeries",
                               "Total Requests", "eCPM") if c in columnas]
    for c in (col_gen, org_gen, col_ser, org_ser):
        if c and c not in salida_cols:
            salida_cols.append(c)
    salida_cols += ["titulo_clave", "ext_imdb_id", "ext_tipo", "ext_generos", "ext_confianza", "ext_wikidata_extra",
                    "gen_declarados", "gen_no_mapeados", "gen_clase_no_mapeado", "gen_nivel_actual", "gen_veredicto",
                    "gen_detalle", "gen_propuesta", "gen_nivel_propuesto", "gen_mejora",
                    "ser_veredicto", "ser_detalle", "ser_es", "ser_evidencia", "serie_propuesta", "ser_mejora",
                    "temporada", "episodio"]
    filas_path = args.filas or (args.prefijo_salida + "-filas.csv")
    os.makedirs(os.path.dirname(os.path.abspath(args.prefijo_salida + ".json")), exist_ok=True)
    w = csv.DictWriter(open(filas_path, "w", encoding="utf-8", newline=""), fieldnames=salida_cols, extrasaction="ignore")
    w.writeheader()

    for d in filas:
        k, req = d["_k"], d["_req"]
        pais, pub = d.get("Country", ""), d.get("Publisher", "")
        rec = cache.get(k) if k else None
        ext = generos_esperados(rec, conf_ok) if rec else None
        imdb = (rec or {}).get("imdb") or {}
        titulo = d.get("contentTitle", "")
        forma_tit = forma_por_titulo(titulo) if k else None
        temp, epi = temporada_episodio(titulo) if k else ("", "")
        d["titulo_clave"] = k
        d["ext_imdb_id"] = imdb.get("id", "")
        d["ext_tipo"] = imdb.get("tipo", "")
        d["ext_generos"] = ",".join(imdb.get("generos", []))
        d["ext_confianza"] = imdb.get("confianza", "")
        d["ext_wikidata_extra"] = ",".join(sorted(ext["wikidata_extra"])) if ext else ""
        d["temporada"], d["episodio"] = temp, epi
        o_gen = d.get(org_gen, "") if org_gen else ""
        o_ser = d.get(org_ser, "") if org_ser else ""

        # ================= contentGenre =================
        raw = d.get(col_gen) or ""
        gen_ok = es_util("contentGenre", raw)
        canon, _, no_map = norm_genre(raw) if gen_ok else ([], False, [])
        conceptos_decl = []
        for g in canon:
            c = CONCEPTO.get(g)
            if c and c not in conceptos_decl:
                conceptos_decl.append(c)
        d["gen_declarados"] = ";".join(canon)
        d["gen_no_mapeados"] = ";".join(no_map)
        d["gen_clase_no_mapeado"] = clasificar_genero_no_mapeado(no_map) if (no_map and not canon) else ""
        nivel = 0 if not gen_ok else (1 if not conceptos_decl else (2 if len(conceptos_decl) == 1 else 3))
        d["gen_nivel_actual"] = nivel
        ver, det = "", ""
        if gen_ok:
            A["gen_formato"].add("mapeado" if canon else ("no_mapeado:" + d["gen_clase_no_mapeado"]), req)
            A["gen_n_declarados"].add(str(min(len(conceptos_decl), 3)), req)
            if ext and ext["conceptos"] and conceptos_decl:
                aciertos = [c for c in conceptos_decl if c in ext["conceptos"]]
                afines = [c for c in conceptos_decl if c not in ext["conceptos"] and AFINES.get(c, set()) & ext["conceptos"]]
                choques = [c for c in conceptos_decl if c not in aciertos and c not in afines]
                if choques and not aciertos:
                    ver = "contradice"
                elif choques:
                    ver = "parcial"
                elif aciertos:
                    ver = "coincide"
                else:
                    ver = "afin"
                det = ";".join(f"{c}!={','.join(sorted(ext['conceptos']))}" for c in choques) if choques else \
                    (";".join(f"{c}~{','.join(sorted(AFINES[c] & ext['conceptos']))}" for c in afines) if afines else "")
                if choques:
                    for c in choques:
                        gen_choque_por_genero.add(c, req)
                        gen_conf.add(f"{c} -> {','.join(sorted(ext['conceptos']))}", req)
                if ver == "contradice":
                    if k:
                        gen_titulos.add(k, req)
                        gen_ejemplo.setdefault(k, {"titulo": titulo, "declarado": raw, "imdb": ext["id"],
                                                   "imdb_titulo": ext["titulo"], "generos_imdb": ",".join(ext["imdb"]),
                                                   "wikidata": ",".join(sorted(ext["wikidata_extra"])), "detalle": det,
                                                   "publisher": pub, "confianza": ext["confianza"]})
                    m_gen.append(d)
            elif ext and ext["conceptos"]:
                ver, det = "no_evaluable", "sin_genero_comparable"
            else:
                ver, det = "no_evaluable", "sin_match"
            A["gen_veredicto"].add(ver, req)
            if pais in paises:
                A[f"gen_pais|{pais}"].add(ver, req)
            if pub in pub_top:
                A[f"gen_pub|{pub}"].add(ver, req)
            if o_gen:
                A[f"gen_origen|{o_gen}"].add(ver, req)
        d["gen_veredicto"], d["gen_detalle"] = ver, det
        # completitud genero
        prop, nivel_p, mejora = [], nivel, ""
        if ext and ext["conceptos"]:
            # se CONSERVA lo declarado que no choca (incluido lo no comparable: "lifestyle")
            # y se AGREGAN los generos IMDb/Wikidata cuyo concepto no este ya representado
            choca = {c for c in conceptos_decl if c not in ext["conceptos"] and
                     not (AFINES.get(c, set()) & ext["conceptos"])}
            keep = [g for g in canon if CONCEPTO.get(g) not in choca]
            externos = [IMDB_GENERO_MAP[g] for g in ext["imdb"] if g in IMDB_GENERO_MAP] + sorted(ext["wikidata_extra"])
            vistos = {CONCEPTO.get(g, g) for g in keep}
            for g in externos:
                c = CONCEPTO.get(g, g)
                if c not in vistos:
                    keep.append(g)
                    vistos.add(c)
            prop = keep[:5]
            conceptos_prop = {CONCEPTO[g] for g in prop if g in CONCEPTO}
            nivel_p = 3 if len(conceptos_prop) >= 2 else (2 if conceptos_prop else 1)
        if not gen_ok:
            mejora = "rellena" if prop else "sin_propuesta"
        elif ver == "contradice":
            mejora = "corrige" if prop else "contradicha_sin_propuesta"
        elif ver == "parcial":
            mejora = "corrige_parcial" if prop else "mantiene"
        elif prop and (nivel_p > nivel or len(prop) > len(canon)):
            mejora = "sube"        # mas generos, o un genero mas preciso (telenovela)
        else:
            mejora, prop, nivel_p = "mantiene", [], nivel
        d["gen_propuesta"] = ",".join(prop)
        d["gen_nivel_propuesto"] = nivel_p
        d["gen_mejora"] = mejora
        A["gen_estado"].add("vacia" if not gen_ok else ("contradicha" if ver == "contradice" else "llena"), req)
        A["gen_nivel_actual"].add(str(nivel), req)
        A["gen_nivel_prop"].add(str(nivel_p), req)
        A["gen_mejora"].add(mejora, req)
        if pais in paises:
            A[f"gen_comp_pais|{pais}"].add(mejora, req)
        if pub in pub_top:
            A[f"gen_comp_pub|{pub}"].add(mejora, req)
        if o_gen:
            A[f"gen_comp_origen|{o_gen}"].add(mejora, req)
        if prop:
            gen_prop_top.add(",".join(prop), req)
        if ext and "telenovela" in ext["wikidata_extra"]:
            A["gen_telenovela"].add("ya_declarada" if "telenovela" in conceptos_decl else "propuesta", req)

        # ================= contentSeries =================
        s = (d.get(col_ser) or "").strip()
        s_ok = d["_ser_ok"]
        placeholder = es_util("contentSeries", s) and s.lower() in SERIES_PLACEHOLDER
        tipo = ext["tipo"] if ext else ""
        es_serie_imdb = tipo in ("tvSeries", "tvMiniSeries")
        es_peli_imdb = tipo == "movie"
        sver, sdet = "", ""
        if s_ok:
            A["ser_formato"].add("serie_real", req)
            if es_serie_imdb:
                same = normalizar_titulo(s) in (normalizar_titulo(ext["titulo"]), k)
                sver, sdet = ("coincide", "") if same else ("otro_nombre", f"{s} != {ext['titulo']}")
            elif es_peli_imdb and not forma_tit:
                sver, sdet = "contradice", f"IMDb movie {ext['titulo']} ({ext['id']})"
                ser_pares.add(f"{s[:40]} -> {ext['titulo'][:40]}", req)
                if k:
                    ser_titulos.add(k, req)
                    ser_ejemplo.setdefault(k, {"titulo": titulo, "serie_declarada": s, "imdb": ext["id"],
                                               "imdb_titulo": ext["titulo"], "tipo": tipo, "publisher": pub,
                                               "confianza": ext["confianza"]})
                m_ser.append(d)
            elif es_peli_imdb and forma_tit:
                sver, sdet = "no_evaluable", "titulo_dice_serie_imdb_dice_pelicula"
            elif ext:
                sver, sdet = "no_evaluable", f"tipo_ambiguo:{tipo}"
            else:
                sver, sdet = "no_evaluable", "sin_match"
            A["ser_veredicto"].add(sver, req)
            if pub in pub_top:
                A[f"ser_pub|{pub}"].add(sver, req)
            if o_ser:
                A[f"ser_origen|{o_ser}"].add(sver, req)
        elif placeholder:
            A["ser_formato"].add("placeholder:" + s.lower(), req)
        d["ser_veredicto"], d["ser_detalle"] = sver, sdet
        # completitud series: que ES la fila
        es, evid, prop_s = "desconocido", "", ""
        if forma_tit:
            es, evid = "serie", "titulo"
        elif es_serie_imdb:
            es, evid = "serie", "imdb"
        elif k in serie_intra:
            es, evid = "serie", "intra_titulo"
        elif es_peli_imdb:
            es, evid = "pelicula", "imdb"
        elif ext:
            es, evid = "ambiguo", f"imdb:{tipo}"
        elif s_ok:
            es, evid = "serie", "declarado"
        elif placeholder and s.lower() == "vod":
            es, evid = "ambiguo", "placeholder_vod"
        if es == "serie" and not s_ok:
            if evid == "titulo":
                prop_s = nombre_serie_desde_titulo(titulo) or (ext["titulo"] if ext else "")
            elif evid == "intra_titulo":
                prop_s = serie_intra[k]
            elif evid == "imdb":
                prop_s = nombre_serie_desde_titulo(titulo) or ext["titulo"]
        if es == "serie" and s_ok:
            smej = "ya_nombrada" if sver != "contradice" else "contradicha"
        elif es == "serie":
            smej = "serie_sin_nombre_recuperable" if prop_s else "serie_sin_nombre"
        elif es == "pelicula":
            smej = "pelicula_vacio_correcto" if not s_ok else "pelicula_con_serie_declarada"
        elif s_ok:
            smej = "nombrada_sin_evidencia"
        else:
            smej = "sin_evidencia"
        d["ser_es"], d["ser_evidencia"], d["serie_propuesta"], d["ser_mejora"] = es, evid, prop_s, smej
        A["ser_es"].add(f"{es}|{evid or '-'}", req)
        A["ser_mejora"].add(smej, req)
        A["ser_temporada"].add("temporada+episodio" if (temp and epi) else ("solo_temporada" if temp else ("solo_episodio" if epi else "nada")), req)
        if pais in paises:
            A[f"ser_comp_pais|{pais}"].add(smej, req)
        if pub in pub_top:
            A[f"ser_comp_pub|{pub}"].add(smej, req)
        if o_ser:
            A[f"ser_comp_origen|{o_ser or 'sin_dato'}"].add(smej, req)
        if prop_s:
            ser_prop_top.add(f"{prop_s[:50]} [{evid}]", req)
            if random.random() < 0.004:
                m_prop.append(d)
        w.writerow(d)

    # ---- agregados ------------------------------------------------------------------------
    gen_llenas = sum(1 for d in filas if es_util("contentGenre", d.get(col_gen) or ""))
    gen_llenas_req = sum(d["_req"] for d in filas if es_util("contentGenre", d.get(col_gen) or ""))
    ser_llenas = sum(1 for d in filas if d["_ser_ok"])
    ser_llenas_req = sum(d["_req"] for d in filas if d["_ser_ok"])

    def grupo(prefijo, keys):
        out = {}
        for kk in keys:
            a = A.get(f"{prefijo}|{kk}")
            if a:
                out[kk] = {"filas": sum(a.f.values()), "requests": sum(a.r.values()),
                           "desglose": a.dump(sum(a.f.values()), sum(a.r.values()))}
        return out

    def origenes(prefijo):
        return sorted(k.split("|", 1)[1] for k in A if k.startswith(prefijo + "|"))

    res = {
        "meta": {"archivo": args.entrada, "nombre": args.nombre or os.path.basename(args.entrada),
                 "columna_genero": col_gen, "columna_series": col_ser, "filas": n, "requests": tot_req,
                 "confianza_min": args.confianza_min, "titulos_en_cache": len(cache),
                 "filas_con_match_externo": sum(1 for d in filas if d["_k"] and generos_esperados(cache.get(d["_k"]), conf_ok)),
                 "fecha": inicio.strftime("%Y-%m-%d %H:%M"), "paises": paises, "publishers_top": pub_top,
                 "min_filas_serie": args.min_filas_serie, "min_rutas_serie": args.min_rutas_serie},
        "genero": {
            "filas_con_genero": gen_llenas, "pct_filas_con_genero": pct(gen_llenas, n),
            "pct_requests_con_genero": pct(gen_llenas_req, tot_req),
            "formato": A["gen_formato"].dump(gen_llenas, gen_llenas_req),
            "n_declarados": A["gen_n_declarados"].dump(gen_llenas, gen_llenas_req),
            "veredicto": A["gen_veredicto"].dump(gen_llenas, gen_llenas_req),
            "choque_por_genero": gen_choque_por_genero.dump(None, None, 25),
            "confusiones_top": gen_conf.dump(None, None, 30),
            "por_pais": grupo("gen_pais", paises), "por_publisher": grupo("gen_pub", pub_top),
            "por_origen": grupo("gen_origen", origenes("gen_origen")),
            "contradicciones_top_titulos": [dict(gen_ejemplo[k], filas=gen_titulos.f[k], requests=gen_titulos.r[k])
                                            for k, _ in gen_titulos.r.most_common(30)],
            "completitud": {
                "estado": A["gen_estado"].dump(n, tot_req),
                "nivel_actual": A["gen_nivel_actual"].dump(n, tot_req),
                "nivel_propuesto": A["gen_nivel_prop"].dump(n, tot_req),
                "mejora": A["gen_mejora"].dump(n, tot_req),
                "telenovela_wikidata": A["gen_telenovela"].dump(n, tot_req),
                "por_pais": {p: A[f"gen_comp_pais|{p}"].dump(sum(A[f"gen_comp_pais|{p}"].f.values()), sum(A[f"gen_comp_pais|{p}"].r.values())) for p in paises if f"gen_comp_pais|{p}" in A},
                "por_publisher": {p: A[f"gen_comp_pub|{p}"].dump(sum(A[f"gen_comp_pub|{p}"].f.values()), sum(A[f"gen_comp_pub|{p}"].r.values())) for p in pub_top if f"gen_comp_pub|{p}" in A},
                "por_origen": {o: A[f"gen_comp_origen|{o}"].dump(sum(A[f"gen_comp_origen|{o}"].f.values()), sum(A[f"gen_comp_origen|{o}"].r.values())) for o in origenes("gen_comp_origen")},
                "propuestas_top": gen_prop_top.dump(n, tot_req, 25)}},
        "series": {
            "filas_con_serie_real": ser_llenas, "pct_filas_con_serie_real": pct(ser_llenas, n),
            "pct_requests_con_serie_real": pct(ser_llenas_req, tot_req),
            "formato": A["ser_formato"].dump(n, tot_req),
            "veredicto": A["ser_veredicto"].dump(ser_llenas, ser_llenas_req),
            "por_publisher": grupo("ser_pub", pub_top), "por_origen": grupo("ser_origen", origenes("ser_origen")),
            "contradicciones_top_titulos": [dict(ser_ejemplo[k], filas=ser_titulos.f[k], requests=ser_titulos.r[k])
                                            for k, _ in ser_titulos.r.most_common(30)],
            "contradicciones_top_pares": ser_pares.dump(None, None, 20),
            "completitud": {
                "que_es": A["ser_es"].dump(n, tot_req),
                "mejora": A["ser_mejora"].dump(n, tot_req),
                "temporada_episodio": A["ser_temporada"].dump(n, tot_req),
                "titulos_con_serie_intra": len(serie_intra),
                "por_pais": {p: A[f"ser_comp_pais|{p}"].dump(sum(A[f"ser_comp_pais|{p}"].f.values()), sum(A[f"ser_comp_pais|{p}"].r.values())) for p in paises if f"ser_comp_pais|{p}" in A},
                "por_publisher": {p: A[f"ser_comp_pub|{p}"].dump(sum(A[f"ser_comp_pub|{p}"].f.values()), sum(A[f"ser_comp_pub|{p}"].r.values())) for p in pub_top if f"ser_comp_pub|{p}" in A},
                "por_origen": {o: A[f"ser_comp_origen|{o}"].dump(sum(A[f"ser_comp_origen|{o}"].f.values()), sum(A[f"ser_comp_origen|{o}"].r.values())) for o in origenes("ser_comp_origen")},
                "propuestas_top": ser_prop_top.dump(n, tot_req, 30)}},
    }
    json.dump(res, open(args.prefijo_salida + ".json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # ---- muestras ---------------------------------------------------------------------------------
    def muestra(nombre, lista, cols, por_titulo=True):
        lista = sorted(lista, key=lambda d: -d["_req"])
        vistos, sel = set(), []
        for d in lista:
            key = d["_k"] or d.get("contentTitle")
            if por_titulo and key in vistos:
                continue
            vistos.add(key)
            sel.append(d)
            if len(sel) >= args.muestra:
                break
        with open(f"{args.prefijo_salida}-muestra-{nombre}.csv", "w", encoding="utf-8", newline="") as f:
            wm = csv.DictWriter(f, fieldnames=[c for c in cols if c in salida_cols], extrasaction="ignore")
            wm.writeheader()
            for d in sel:
                wm.writerow(d)
    base = ["Publisher", "Country", "contentTitle", "Total Requests", "ext_imdb_id", "ext_tipo", "ext_generos", "ext_confianza", "ext_wikidata_extra"]
    muestra("genero-contradicciones", m_gen, base + [col_gen, "gen_declarados", "gen_detalle", "gen_propuesta"])
    muestra("series-contradicciones", m_ser, base + [col_ser, "ser_detalle", "ser_es", "serie_propuesta"])
    muestra("series-propuestas", m_prop, base + [col_ser, "ser_es", "ser_evidencia", "serie_propuesta", "temporada", "episodio"], por_titulo=False)

    g, s_ = res["genero"], res["series"]
    print(f"\n[{res['meta']['nombre']}] genero: {gen_llenas:,} filas con genero; veredicto:")
    for kk, v in g["veredicto"].items():
        print(f"  {kk:18} {v['filas']:8,} {v['pct_filas']:6.2f}%")
    print("  mejora:", {kk: v["pct_filas"] for kk, v in g["completitud"]["mejora"].items()})
    print(f"series: {ser_llenas:,} filas con serie real; veredicto:")
    for kk, v in s_["veredicto"].items():
        print(f"  {kk:18} {v['filas']:8,} {v['pct_filas']:6.2f}%")
    print("  que es:", {kk: v["pct_filas"] for kk, v in s_["completitud"]["mejora"].items()})
    print(f"listo en {(datetime.now() - inicio).seconds}s", file=sys.stderr)


if __name__ == "__main__":
    main()
