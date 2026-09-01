# -*- coding: utf-8 -*-
"""Relleno de content objects vacios con fuentes internas y abiertas (pipeline periodico).

Toma el consolidado (idealmente el *enriquecido*, que ya trae genero_normalizado y
rating_franja) y produce un CSV con, para cada columna objetivo, dos columnas nuevas:

    <col>_relleno   valor final (el original si venia, o el inferido)
    <col>_origen    de donde salio: original | intra_titulo | app_default | imdb |
                    tvmaze | wikidata | derivado_genero | derivado_tipo | (vacio)

Columnas objetivo: contentCategory, contentSeries, contentLength, contentLanguage,
contentIsLiveStream, contentRating, contentGenre.

Etapas (en orden; la primera que llena gana):
  0. Normalizacion del titulo -> `titulo_clave` (url-decode, mojibake cp1252->utf8,
     quitar ": trailer", "season N", "episodio N", SxxEyy, puntuacion). Solo se
     buscan los titulos que pasan el filtro de "titulo de verdad" de
     analizar_genero_titulo_paises.clasificar_titulo.
  1. intra_titulo: el mismo titulo_clave trae el dato en otra fila del consolidado
     (se exige que el valor dominante cubra >= --umbral-intra de las filas con dato).
  2. app_default: la app manda un valor constante (>= --umbral-app) cuando lo manda.
     contentIsLiveStream queda EXCLUIDO por defecto (MovieArk marca 1 todo su VOD).
  3. imdb: match offline contra los IMDb Non-Commercial Datasets (title.basics +
     title.akas es/pt/en + title.ratings + title.episode). Aporta tipo (movie /
     tvSeries...), runtime, generos y titulo canonico. Se descargan a --cache-dir si
     tienen mas de --imdb-max-dias dias. Solo para uso no comercial (ver README).
  4. tvmaze (--tvmaze): series no resueltas por IMDb; aporta idioma, generos, runtime.
     Sin API key, CC BY-SA, ~20 req/10 s.
  5. wikidata (--wikidata): via IMDb id (P345) -> idioma original (P364), duracion
     (P2047), generos (P136), clasificacion (P3834, rara). CC0, sin API key.
  6. derivados: contentCategory desde el genero (mapa IAB 1.0) y el tipo IMDb,
     contentSeries desde el tipo (tvSeries -> titulo canonico), contentLength desde
     el runtime (requiere --length-desde-runtime, ver docstring de BUCKETS).
     contentIsLiveStream es caso aparte (mide modo de entrega, no contenido):
     señales del vendedor en contentSeries ("VOD" -> 0, "... Livestream" -> 1) +
     semantica de la app validada a mano (cache-dir/semantica_apps.csv, columna
     "aplicar"); ni intra_titulo (propagaria el "1" default) ni el tipo IMDb (una
     pelicula en canal lineal es livestream=1) se usan salvo flag explicito.

COMO FUNCIONA, CON UN EJEMPLO REAL (contentCategory: 23% -> 95%)
----------------------------------------------------------------
La idea central: cada fila del consolidado NO es un programa, es una COMBINACION de
14 dimensiones (pais x publisher x app x genero x ...). El mismo contenido llega por
muchas rutas de venta a la vez, y cada ruta manda la metadata como quiere. El titulo
"ideas en 5 minutos" aparece en 10+ filas:

    Mexico/Panama via Vidaa, Equativ, Stingray  -> contentCategory = [IAB1-6] (Musica)
    Argentina    via OTTera/TCL                 -> contentCategory = [-7]     (basura)

El "vacio" no es que nadie sepa la categoria: es que ESA ruta la descarta. La
respuesta correcta ya esta escrita en otra fila del mismo titulo. De ahi los
escalones (el primero que aplica gana, y queda anotado en <col>_origen):

  original       (23.0%) la fila ya lo traia; nunca se toca.
  intra_titulo  (+12.0%) otra fila del MISMO TITULO lo trae -> se copia el [IAB1-6]
                         de Vidaa a las filas de OTTera. Candado: el valor debe
                         dominar >= 80% de las filas con dato de ese titulo.
  app_default    (+8.1%) para titulos donde NINGUNA ruta manda el dato, la pregunta
                         cambia de "que es este contenido?" a "que manda este
                         vendedor cuando si manda?": OTTera->MovieArk manda [IAB1]
                         el 99.2% de las veces, Vidaa [IAB12] el 100%. Si una app es
                         asi de constante (>= 95%), sus vacias reciben ese valor.
  derivado_*    (+52.1%) la fila vacia en category casi siempre esta LLENA en
                         contentGenre (99% de fill): deportes -> [IAB17], noticias ->
                         [IAB12]... (mapa aprendido de las ~149k filas que traen
                         ambas columnas). Y para generos que no definen categoria
                         (un drama puede ser pelicula o serie), desempata el tipo
                         del match IMDb: movie -> [IAB1-5], tvSeries -> [IAB1-7].

  intra vs app en una frase: intra_titulo copia ENTRE FILAS DEL MISMO TITULO (misma
  pelicula, distinta ruta); app_default copia ENTRE FILAS DE LA MISMA APP (mismo
  vendedor, distinto titulo). El primero es mas preciso y por eso va antes.

De todo lo rellenado en las 7 columnas, ~2/3 sale del propio dataset (intra + app +
derivado del genero) y ~1/3 depende del match externo (el tipo IMDb para separar
pelicula/serie y corregir livestream, el titulo canonico para series).

Cache incremental: --cache-dir/titulos.json guarda el resultado de cada titulo_clave;
en corridas siguientes solo se consultan los titulos nuevos. Asi el mismo comando
sirve para cada tanda nueva.

Uso:
    python scripts/enriquecer_externo.py inventory-consolidado-enriquecido.csv \
        inventory-consolidado-relleno.csv reporte-relleno.json \
        --cache-dir cache-enriquecimiento [--tvmaze] [--wikidata] [--sin-imdb]

Solo stdlib salvo `requests` (opcional, para --tvmaze/--wikidata; si no esta, se usa urllib).
"""
import argparse
import csv
import gzip
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analizar_genero_titulo_paises import clasificar_titulo, norm_genre  # noqa: E402

csv.field_size_limit(10 ** 8)

SENT = {"not available", "not applicable", "unknown", "n/a", "null", "undefined",
        "none", "-", ""}
MD5_VACIO = "d41d8cd98f00b204e9800998ecf8427e"
OBJETIVO = ["contentCategory", "contentSeries", "contentLength", "contentLanguage",
            "contentIsLiveStream", "contentRating", "contentGenre"]
UA = "ctv-inventory-enrich/0.1 (+https://github.com; contacto: analista)"


# contentSeries "lleno" que no nombra una serie: "VOD" o "No Series" es tecnicamente
# un valor, pero copiarlo a otras filas seria propagar un placeholder, no un dato.
SERIES_PLACEHOLDER = {"vod", "no series", "ott studios entertainment on demand",
                      "ott studios sports livestream", "ott studios entertainment livestream",
                      "research unit", "video chart"}


def es_propagable(col, v):
    if not es_util(col, v):
        return False
    return not (col == "contentSeries" and v.strip().lower() in SERIES_PLACEHOLDER)


def es_util(col, v):
    """Una celda cuenta como VACIA aunque traiga texto, si ese texto es un centinela
    ("Not Available", "Unknown"...) o basura equivalente: [-7] en contentCategory,
    el hash MD5 de la cadena vacia en contentSeries, o una macro sin reemplazar
    ({{content_title}}). Es la misma definicion de "vacio" de los reportes."""
    v = (v or "").strip()
    if v.lower() in SENT:
        return False
    if col == "contentSeries" and v == MD5_VACIO:
        return False
    if col == "contentCategory" and v in ("[-7]", "[]", "[-1]"):
        return False
    if "{{" in v or "}}" in v:
        return False
    return True


# ----------------------------------------------------------------------------
# 0. Normalizacion del titulo
# ----------------------------------------------------------------------------
RE_TRAILER = re.compile(r"\s*[:\-–|]?\s*\b(trailer|tráiler|teaser|promo)\b\s*$", re.I)
RE_SXXEXX = re.compile(r"\s*[-:|]?\s*\bs\d{1,2}\s*e\d{1,3}\b.*$", re.I)
RE_EPREFIX = re.compile(r"^\s*(e|ep|cap|episodio|episode)\.?\s*\d+\s*[.:\-]\s*", re.I)
RE_EP = re.compile(r"\s*[-:|,]?\s*\b(season|temporada|series|episode|episodio|ep|"
                   r"cap[ií]tulo|cap|programa|parte|part|s|t)\.?\s*\d+\b.*$", re.I)
RE_SPACE = re.compile(r"\s+")


def _fix_mojibake(s):
    try:
        return s.encode("cp1252").decode("utf-8")
    except Exception:
        return s


def _sin_acentos(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def normalizar_titulo(t):
    """Convierte las variantes de un mismo contenido en UNA sola clave de busqueda.

    Sin esto, "Hatchback: Trailer", "hatchback" y "HATCHBACK temporada 2" serian tres
    titulos distintos y las filas no se encontrarian entre si (ni en IMDb). Pasos:
      - url-decode:  "barking%20dogs" -> "barking dogs"
      - mojibake:    "Do�a B�rbara" (cp1252 mal decodificado) -> "Doña Bárbara"
      - sufijos:     ": trailer", "temporada 8", "episodio 79", "S01E03" fuera
      - minusculas, sin acentos, sin puntuacion, espacios colapsados
    El resultado es la llave del cache y de los indices intra-dataset e IMDb
    (18,374 titulos crudos -> ~14,100 claves)."""
    s = t.strip()
    if "%" in s:
        try:
            s = urllib.parse.unquote(s)
        except Exception:
            pass
    if "+" in s and " " not in s:
        s = s.replace("+", " ")
    s = _fix_mojibake(s).replace("�", "")
    low = s.lower()
    low = RE_TRAILER.sub("", low)
    low = RE_SXXEXX.sub("", low)
    low = RE_EPREFIX.sub("", low)
    low = RE_EP.sub("", low)
    low = _sin_acentos(low).replace("&", "and")
    low = re.sub(r"[^\w\s']", " ", low)
    return RE_SPACE.sub(" ", low).strip()


def titulo_real(t):
    return es_util("contentTitle", t) and clasificar_titulo(t) is None


# ----------------------------------------------------------------------------
# 3. IMDb offline
# ----------------------------------------------------------------------------
IMDB_FILES = ["title.basics.tsv.gz", "title.akas.tsv.gz", "title.ratings.tsv.gz"]
IMDB_URL = "https://datasets.imdbws.com/"
IMDB_TIPOS = {"movie", "tvSeries", "tvMiniSeries", "tvMovie", "video", "short",
              "tvSpecial", "tvShort"}
IMDB_REGIONES = {"MX", "ES", "AR", "CO", "CL", "PE", "BR", "US", "GB", r"\N"}
IMDB_IDIOMAS = {"es", "pt", "en", r"\N"}


def imdb_descargar(cache_dir, max_dias):
    d = os.path.join(cache_dir, "imdb")
    os.makedirs(d, exist_ok=True)
    for f in IMDB_FILES:
        p = os.path.join(d, f)
        viejo = (not os.path.exists(p)) or \
            (time.time() - os.path.getmtime(p)) > max_dias * 86400
        if viejo:
            print(f"  descargando {f} ...", file=sys.stderr)
            req = urllib.request.Request(IMDB_URL + f, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r, open(p, "wb") as out:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
    return d


def imdb_indexar(imdb_dir, claves_necesarias):
    """Indice titulo normalizado -> candidatos, solo para las claves que nos interesan."""
    basics = {}
    idx = defaultdict(set)
    with gzip.open(os.path.join(imdb_dir, "title.basics.tsv.gz"), "rt",
                   encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            if row[1] not in IMDB_TIPOS:
                continue
            k1 = normalizar_titulo(row[2])
            k2 = normalizar_titulo(row[3]) if row[3] != row[2] else k1
            if k1 in claves_necesarias or k2 in claves_necesarias:
                basics[row[0]] = {"tipo": row[1], "titulo": row[2], "anio": row[5],
                                  "runtime": row[7], "generos": row[8]}
                idx[k1].add(row[0])
                idx[k2].add(row[0])
    # akas: titulos locales (es/pt/en) de cualquier titulo -> necesitamos basics completo
    # para resolver el tipo; segunda pasada sobre basics solo para los tconst nuevos.
    nuevos = defaultdict(set)
    with gzip.open(os.path.join(imdb_dir, "title.akas.tsv.gz"), "rt",
                   encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            if row[3] not in IMDB_REGIONES and row[4] not in IMDB_IDIOMAS:
                continue
            k = normalizar_titulo(row[2])
            if k in claves_necesarias:
                nuevos[row[0]].add(k)
    faltan = {tc for tc in nuevos if tc not in basics}
    if faltan:
        with gzip.open(os.path.join(imdb_dir, "title.basics.tsv.gz"), "rt",
                       encoding="utf-8", newline="") as f:
            r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
            next(r)
            for row in r:
                if row[0] in faltan and row[1] in IMDB_TIPOS:
                    basics[row[0]] = {"tipo": row[1], "titulo": row[2], "anio": row[5],
                                      "runtime": row[7], "generos": row[8]}
    for tc, ks in nuevos.items():
        if tc in basics:
            for k in ks:
                idx[k].add(tc)
    votos = {}
    with gzip.open(os.path.join(imdb_dir, "title.ratings.tsv.gz"), "rt",
                   encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            if row[0] in basics:
                votos[row[0]] = int(row[2])
    return basics, idx, votos


IMDB_GENERO_MAP = {"Drama": "drama", "Comedy": "comedia", "Romance": "romance",
                   "Horror": "terror", "Thriller": "thriller", "Mystery": "misterio",
                   "Action": "accion", "Adventure": "aventura", "Crime": "crimen",
                   "Western": "western", "Sci-Fi": "sci-fi", "Fantasy": "fantasia",
                   "Documentary": "documental", "Biography": "documental",
                   "History": "documental", "News": "noticias", "Sport": "deportes",
                   "Music": "musica", "Musical": "musica", "Family": "infantil-familia",
                   "Animation": "animacion", "Reality-TV": "reality",
                   "Talk-Show": "talk show", "Game-Show": "concursos", "War": "belico"}


def imdb_elegir(cands, basics, votos, generos_fila):
    """Desambigua: si hay varios candidatos con votos, prefiere el que comparte genero
    con la fila; empate -> mas votos; prefiere movie/tvSeries sobre short/video."""
    def score(tc):
        b = basics[tc]
        g_imdb = {IMDB_GENERO_MAP.get(x) for x in b["generos"].split(",")} - {None}
        coincide = len(g_imdb & set(generos_fila)) if generos_fila else 0
        return (coincide, votos.get(tc, 0),
                b["tipo"] in ("movie", "tvSeries", "tvMiniSeries", "tvMovie"))
    mejor = max(cands, key=score)
    coincide = score(mejor)[0] > 0
    if len(cands) == 1:
        confianza = "A" if (coincide or not generos_fila) else "C"
    else:
        confianza = "B" if coincide else "D"
    return mejor, confianza


# ----------------------------------------------------------------------------
# 4/5. Fuentes online (opcionales)
# ----------------------------------------------------------------------------
try:
    import requests as _requests  # usa certifi; el urllib de Python 3.9 en Windows falla el SSL de wikidata
except ImportError:  # pragma: no cover
    _requests = None


def _get_json(url, params, pausa):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    for intento in range(3):
        try:
            if _requests is not None:
                r = _requests.get(url, params=params, headers=headers, timeout=30)
                r.raise_for_status()
                data = r.json()
            else:
                full = url + "?" + urllib.parse.urlencode(params)
                req = urllib.request.Request(full, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            time.sleep(pausa)
            return data
        except Exception as e:  # 429 / red
            print(f"  aviso: {url} intento {intento + 1}: {e}", file=sys.stderr)
            time.sleep(pausa * (3 ** intento))
    return None


def tvmaze_buscar(clave):
    data = _get_json("https://api.tvmaze.com/search/shows", {"q": clave}, 0.5)
    if not data:
        return None
    mejor = data[0]
    show = mejor["show"]
    if normalizar_titulo(show["name"]) != clave and mejor["score"] < 1.0:
        return None
    return {"nombre": show["name"], "idioma": (show.get("language") or ""),
            "generos": show.get("genres") or [],
            "runtime": show.get("runtime") or show.get("averageRuntime"),
            "tipo": show.get("type"), "score": round(mejor["score"], 2)}


WD_SPARQL = "https://query.wikidata.org/sparql"


def wikidata_por_imdb(tconsts):
    """Lote de hasta ~150 IMDb ids -> idioma original, duracion, generos, clasificacion."""
    if not tconsts:
        return {}
    values = " ".join(f'"{t}"' for t in tconsts)
    q = f"""
    SELECT ?imdb ?langCode ?dur ?genreLabel ?ratingLabel WHERE {{
      VALUES ?imdb {{ {values} }}
      ?item wdt:P345 ?imdb .
      OPTIONAL {{ ?item wdt:P364 ?lang . ?lang wdt:P218 ?langCode . }}
      OPTIONAL {{ ?item wdt:P2047 ?dur . }}
      OPTIONAL {{ ?item wdt:P136 ?genre . ?genre rdfs:label ?genreLabel FILTER(LANG(?genreLabel)="en") }}
      OPTIONAL {{ ?item wdt:P3834 ?rating . ?rating rdfs:label ?ratingLabel FILTER(LANG(?ratingLabel)="en") }}
    }}"""
    data = _get_json(WD_SPARQL, {"query": q, "format": "json"}, 1.0)
    out = defaultdict(lambda: {"idioma": set(), "duracion": set(), "generos": set(), "rating": set()})
    if not data:
        return {}
    for b in data["results"]["bindings"]:
        t = b["imdb"]["value"]
        if "langCode" in b:
            out[t]["idioma"].add(b["langCode"]["value"])
        if "dur" in b:
            out[t]["duracion"].add(b["dur"]["value"])
        if "genreLabel" in b:
            out[t]["generos"].add(b["genreLabel"]["value"])
        if "ratingLabel" in b:
            out[t]["rating"].add(b["ratingLabel"]["value"])
    return {t: {k: sorted(v) for k, v in d.items()} for t, d in out.items()}


# ----------------------------------------------------------------------------
# 6. Derivados
# ----------------------------------------------------------------------------
# Genero canonico -> categoria IAB Content Taxonomy 1.0 (lo que los vendedores ya usan:
# IAB1 Arts & Entertainment, IAB1-5 Movies, IAB1-6 Music, IAB1-7 Television,
# IAB1-22 (no estandar, "Entertainment" en varios SSP), IAB12 News, IAB17 Sports,
# IAB8 Food & Drink, IAB20 Travel, IAB9-30 Video & Computer Games, IAB23 Religion).
GENERO_IAB = {
    "deportes": "[IAB17]", "noticias": "[IAB12]", "musica": "[IAB1-6]",
    "gastronomia": "[IAB8]", "viajes": "[IAB20]", "videojuegos": "[IAB9-30]",
    "religion": "[IAB23]", "infantil-familia": "[IAB1-7]", "animacion": "[IAB1-7]",
    "telenovela": "[IAB1-7]", "reality": "[IAB1-7]", "talk show": "[IAB1-7]",
    "concursos": "[IAB1-7]", "tv/series (generico)": "[IAB1-7]",
    "pelicula (generico)": "[IAB1-5]", "educacion": "[IAB5]", "lifestyle": "[IAB1]",
}
IAB_POR_TIPO = {"movie": "[IAB1-5]", "tvMovie": "[IAB1-5]", "video": "[IAB1-5]",
                "short": "[IAB1-5]", "tvSeries": "[IAB1-7]", "tvMiniSeries": "[IAB1-7]",
                "tvSpecial": "[IAB1-7]", "tvShort": "[IAB1-7]"}
IAB_DEFAULT_ENTRETENIMIENTO = "[IAB1]"

# contentLength en estas exportaciones NO viene en segundos: es un codigo 1..8 del
# reporte cuya semantica no es la duracion (calibrado contra el runtime de IMDb, todos
# los codigos tienen mediana 60-95 min; ver reporte 08). Por eso NO se rellena por
# defecto: la duracion real queda en `ext_runtime_min`. Si algun dia se conoce la
# definicion de los codigos, activar --length-desde-runtime con --buckets
# "1:1,2:5,3:15,4:30,5:60,6:120,7:180" (codigo:limite superior en minutos).
BUCKETS_DEFAULT = [(1, 1), (2, 5), (3, 15), (4, 30), (5, 60), (6, 120), (7, 180)]

# Confianza del match IMDb (ver reporte 08; precision estimada en muestra manual):
#   A  candidato unico y genero compatible (o sin genero en la fila)   ~90%+
#   B  varios candidatos, elegido por coincidencia de genero            ~75%
#   C  candidato unico pero genero distinto                             ~60%
#   D  varios candidatos sin apoyo de genero (se elige por votos)       ~50%
CONFIANZA_ORDEN = "ABCD"


def runtime_a_bucket(minutos, buckets):
    try:
        m = float(minutos)
    except (TypeError, ValueError):
        return None
    for b, lim in buckets:
        if m <= lim:
            return str(b)
    return str(buckets[-1][0] + 1)


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("salida_csv")
    ap.add_argument("salida_json")
    ap.add_argument("--cache-dir", default="cache-enriquecimiento")
    ap.add_argument("--umbral-intra", type=float, default=0.8)
    ap.add_argument("--umbral-app", type=float, default=0.95)
    ap.add_argument("--min-filas-app", type=int, default=200)
    ap.add_argument("--app-default-livestream", action="store_true",
                    help="permitir default por app en contentIsLiveStream (desaconsejado)")
    ap.add_argument("--livestream-desde-tipo", action="store_true",
                    help="inferir contentIsLiveStream=0 cuando IMDb dice movie/serie "
                         "(desaconsejado: confunde tipo de contenido con modo de entrega; "
                         "una pelicula en canal lineal es livestream=1)")
    ap.add_argument("--intra-livestream", action="store_true",
                    help="permitir intra_titulo en contentIsLiveStream (desaconsejado: como "
                         "todo lo declarado es '1', solo propaga el default del vendedor)")
    ap.add_argument("--semantica-apps", default="",
                    help="CSV con el veredicto de entrega por app (bundle,app_name,veredicto,"
                         "aplicar,...); default: <cache-dir>/semantica_apps.csv si existe. "
                         "Solo filas con aplicar=si rellenan: lineal->1, vod->0")
    ap.add_argument("--sin-imdb", action="store_true")
    ap.add_argument("--imdb-max-dias", type=int, default=7)
    ap.add_argument("--tvmaze", action="store_true")
    ap.add_argument("--wikidata", action="store_true")
    ap.add_argument("--max-online", type=int, default=0, help="tope de consultas online nuevas (0 = sin tope)")
    ap.add_argument("--buckets", default="", help='ej. "1:1,2:5,3:15,4:30,5:60,6:120,7:180"')
    ap.add_argument("--length-desde-runtime", action="store_true",
                    help="rellenar contentLength con el bucket del runtime (ver BUCKETS_DEFAULT)")
    ap.add_argument("--confianza-min", default="B", choices=list("ABCD"),
                    help="peor nivel de confianza IMDb que se usa para rellenar (default B)")
    args = ap.parse_args()
    conf_ok = set(CONFIANZA_ORDEN[:CONFIANZA_ORDEN.index(args.confianza_min) + 1])

    buckets = BUCKETS_DEFAULT
    if args.buckets:
        buckets = [(int(a), float(b)) for a, b in (x.split(":") for x in args.buckets.split(","))]
    os.makedirs(args.cache_dir, exist_ok=True)
    cache_path = os.path.join(args.cache_dir, "titulos.json")
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
    inicio = datetime.now()

    # Tabla de semantica de entrega por app, VALIDADA A MANO (ver reporte 08 §4):
    # el modo de entrega (lineal vs on-demand) es una propiedad de la app/canal, no
    # del titulo. La tabla se llena con evidencia publica (ficha de la tienda, web
    # del vendedor) y cada fila trae "aplicar" (si/no) para que la revision humana
    # decida que veredictos se usan. lineal -> 1, vod -> 0; mixto/desconocido no
    # rellenan nunca. Se busca por bundle (pageURL) y si no, por App Name.
    sem_path = args.semantica_apps or os.path.join(args.cache_dir, "semantica_apps.csv")
    sem_bundle, sem_app = {}, {}
    if os.path.exists(sem_path):
        with open(sem_path, encoding="utf-8-sig", newline="") as f:
            for fila in csv.DictReader(f):
                if (fila.get("aplicar") or "").strip().lower() != "si":
                    continue
                v = {"lineal": "1", "vod": "0"}.get((fila.get("veredicto") or "").strip().lower())
                if not v:
                    continue
                if fila.get("bundle"):
                    sem_bundle[fila["bundle"].strip().lower()] = v
                if fila.get("app_name"):
                    sem_app[fila["app_name"].strip().lower()] = v
        print(f"semantica_apps: {len(sem_bundle)} bundles / {len(sem_app)} apps activos",
              file=sys.stderr)

    # =========================================================================
    # PASADA 1 — aprender del propio dataset (aqui no se rellena nada todavia).
    # Se leen las 648k filas y se construyen dos "memorias":
    #   conocido[col][titulo] = Counter de valores que ese titulo trae en las filas
    #                           donde SI viene el dato  -> alimenta intra_titulo
    #   por_app[col][app]     = Counter de valores que esa app manda cuando manda
    #                           el campo                 -> alimenta app_default
    # =========================================================================
    filas = []
    with open(args.entrada, encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        columnas = lector.fieldnames
        for d in lector:
            filas.append(d)
    tiene_genero_norm = "genero_normalizado" in columnas
    n = len(filas)
    print(f"{n} filas leidas", file=sys.stderr)

    conocido = {c: defaultdict(Counter) for c in OBJETIVO}
    por_app = {c: defaultdict(Counter) for c in OBJETIVO}
    claves = {}
    for d in filas:
        t = (d.get("contentTitle") or "").strip()
        k = normalizar_titulo(t) if titulo_real(t) else ""
        d["titulo_clave"] = k
        app = f'{d.get("Publisher", "")}|{d.get("App Name", "")}'
        for c in OBJETIVO:
            if es_propagable(c, d.get(c)):
                v = d[c].strip()
                if k:
                    conocido[c][k][v] += 1
                por_app[c][app][v] += 1
        if k:
            claves[k] = claves.get(k, 0) + 1

    # Defaults por app: una app "gana" un default solo si es casi monotematica en esa
    # columna — su valor mas comun cubre >= 95% (umbral-app) de las filas donde manda
    # el dato, con >= 200 filas de evidencia. Ej.: Vidaa manda [IAB12] el 100% de las
    # veces que manda categoria; ViX manda "es" el ~97%. contentIsLiveStream queda
    # excluido: MovieArk marca "1" hasta en peliculas, propagarlo seria amplificar
    # un valor por defecto que no describe nada (se corrige en la pasada 2).
    app_default = {c: {} for c in OBJETIVO}
    for c in OBJETIVO:
        if c == "contentIsLiveStream" and not args.app_default_livestream:
            continue
        for app, cnt in por_app[c].items():
            tot = sum(cnt.values())
            v, k_ = cnt.most_common(1)[0]
            if tot >= args.min_filas_app and k_ / tot >= args.umbral_app:
                app_default[c][app] = v

    # =========================================================================
    # FUENTES EXTERNAS — se consultan POR TITULO DISTINTO (14 mil claves), nunca
    # por fila (648 mil): el resultado de cada titulo queda en el cache
    # (titulos.json), asi la proxima tanda solo consulta los titulos nuevos.
    # =========================================================================
    nuevas = [k for k in claves if k not in cache]
    print(f"{len(claves)} titulos distintos, {len(nuevas)} sin cache", file=sys.stderr)
    generos_por_clave = defaultdict(Counter)
    if tiene_genero_norm:
        for d in filas:
            if d["titulo_clave"]:
                for g in (d.get("genero_normalizado") or "").split(";"):
                    if g:
                        generos_por_clave[d["titulo_clave"]][g] += 1
    else:
        for d in filas:
            if d["titulo_clave"]:
                for g in norm_genre(d.get("contentGenre") or "")[0]:
                    generos_por_clave[d["titulo_clave"]][g] += 1

    if nuevas and not args.sin_imdb:
        print("IMDb: preparando datasets ...", file=sys.stderr)
        imdb_dir = imdb_descargar(args.cache_dir, args.imdb_max_dias)
        basics, idx, votos = imdb_indexar(imdb_dir, set(nuevas))
        print(f"IMDb: {len(basics)} titulos candidatos indexados", file=sys.stderr)
        for k in nuevas:
            cands = idx.get(k)
            rec = {"imdb": None, "actualizado": inicio.strftime("%Y-%m-%d")}
            if cands:
                tc, confianza = imdb_elegir(cands, basics, votos,
                                            [g for g, _ in generos_por_clave[k].most_common(3)])
                b = basics[tc]
                rec["imdb"] = {"id": tc, "tipo": b["tipo"], "titulo": b["titulo"],
                               "anio": b["anio"], "runtime": None if b["runtime"] == r"\N" else b["runtime"],
                               "generos": [] if b["generos"] == r"\N" else b["generos"].split(","),
                               "votos": votos.get(tc, 0), "candidatos": len(cands),
                               "confianza": confianza}
            cache[k] = rec
        json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
    elif nuevas:
        for k in nuevas:
            cache[k] = {"imdb": None, "actualizado": inicio.strftime("%Y-%m-%d")}

    # --- TVMaze (solo lo que IMDb no resolvio o resolvio como serie sin runtime) ----
    if args.tvmaze:
        pend = [k for k in claves if "tvmaze" not in cache[k] and
                (not cache[k]["imdb"] or cache[k]["imdb"]["tipo"].startswith("tv"))]
        if args.max_online:
            pend = pend[:args.max_online]
        print(f"TVMaze: {len(pend)} consultas", file=sys.stderr)
        for i, k in enumerate(pend):
            cache[k]["tvmaze"] = tvmaze_buscar(k)
            if i % 100 == 99:
                json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
        json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)

    # --- Wikidata por IMDb id ----------------------------------------------------------
    if args.wikidata:
        pend = [k for k in claves if cache[k].get("imdb") and "wikidata" not in cache[k]]
        if args.max_online:
            pend = pend[:args.max_online]
        print(f"Wikidata: {len(pend)} titulos en lotes de 150", file=sys.stderr)
        for i in range(0, len(pend), 150):
            lote = pend[i:i + 150]
            res = wikidata_por_imdb([cache[k]["imdb"]["id"] for k in lote])
            for k in lote:
                cache[k]["wikidata"] = res.get(cache[k]["imdb"]["id"])
            json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)

    # --- pasada 2: rellenar --------------------------------------------------------------
    stats = {c: Counter() for c in OBJETIVO}
    salida_cols = list(columnas) + ["titulo_clave", "ext_imdb_id", "ext_tipo", "ext_anio",
                                    "ext_runtime_min", "ext_confianza"]
    for c in OBJETIVO:
        salida_cols += [c + "_relleno", c + "_origen"]

    def intra(c, k):
        """Escalon intra_titulo: ¿alguna fila hermana (mismo titulo) trae el dato?

        Devuelve el valor dominante SOLO si cubre >= 80% (umbral-intra) de las filas
        con dato de ese titulo. El candado importa: si "memorias adolescentes" trae
        es en 3 filas y en en 1 (75%), no se rellena — la mezcla es informacion
        (pistas de audio distintas), no ruido, y copiar seria adivinar."""
        cnt = conocido[c].get(k)
        if not cnt:
            return None
        v, m = cnt.most_common(1)[0]
        return v if m / sum(cnt.values()) >= args.umbral_intra else None

    # =========================================================================
    # PASADA 2 — rellenar fila por fila. Para cada columna vacia se prueban las
    # fuentes EN ORDEN (la primera que da valor gana) y el origen queda anotado
    # en <col>_origen para poder filtrar por confianza despues:
    #   original -> intra_titulo -> app_default -> fuente externa / derivado
    # =========================================================================
    with open(args.salida_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=salida_cols, extrasaction="ignore")
        w.writeheader()
        for d in filas:
            k = d["titulo_clave"]
            app = f'{d.get("Publisher", "")}|{d.get("App Name", "")}'
            ext = cache.get(k, {}) if k else {}
            imdb = ext.get("imdb") or {}
            tvm = ext.get("tvmaze") or {}
            wd = ext.get("wikidata") or {}
            d["ext_imdb_id"] = imdb.get("id", "")
            d["ext_confianza"] = imdb.get("confianza", "")
            # Filtro de confianza: por defecto solo se usan matches A (candidato
            # unico + genero compatible, ~90% de precision) y B (varios candidatos,
            # desempatado por genero, ~75%). C y D se reportan pero no rellenan.
            if imdb and imdb.get("confianza", "D") not in conf_ok:
                imdb, wd = {}, {}   # match dudoso: se reporta el id pero no se usa
            d["ext_tipo"] = imdb.get("tipo", "") or (tvm.get("tipo", "") and "tvSeries")
            d["ext_anio"] = imdb.get("anio", "") if imdb.get("anio") not in (None, r"\N") else ""
            d["ext_runtime_min"] = imdb.get("runtime") or tvm.get("runtime") or \
                (wd.get("duracion") or [""])[0]
            tipo = imdb.get("tipo", "")
            generos_fila = [g for g in (d.get("genero_normalizado") or "").split(";") if g] \
                if tiene_genero_norm else norm_genre(d.get("contentGenre") or "")[0]

            for c in OBJETIVO:
                if es_util(c, d.get(c)):
                    val, org = d[c].strip(), "original"
                else:
                    val, org = None, ""
                    v = intra(c, k) if k else None
                    if c == "contentIsLiveStream":
                        # contentIsLiveStream mide el MODO DE ENTREGA (lineal vs
                        # on-demand), no que es el contenido: una pelicula vieja en un
                        # canal lineal FAST va programada en horario -> livestream=1.
                        # Fuentes, en orden:
                        #  1) señales de entrega del propio vendedor en contentSeries
                        #     ("... Livestream" -> 1, "VOD" -> 0)
                        #  2) semantica de la app validada a mano (semantica_apps.csv:
                        #     una app 100% lineal como "Live TV" -> 1)
                        #  3) intra_titulo/tipo IMDb SOLO con sus flags: propagar el
                        #     "1" declarado no agrega informacion (todo lo declarado
                        #     es 1) e inferir 0 de "movie" confunde contenido con
                        #     entrega.
                        if es_util("contentSeries", d.get("contentSeries")) and \
                                "livestream" in d["contentSeries"].lower():
                            val, org = "1", "derivado_tipo"
                        elif es_util("contentSeries", d.get("contentSeries")) and \
                                d["contentSeries"].strip().lower() == "vod":
                            val, org = "0", "derivado_tipo"
                        elif (d.get("pageURL") or "").strip().lower() in sem_bundle:
                            val, org = sem_bundle[d["pageURL"].strip().lower()], "app_semantica"
                        elif (d.get("App Name") or "").strip().lower() in sem_app:
                            val, org = sem_app[d["App Name"].strip().lower()], "app_semantica"
                        elif args.livestream_desde_tipo and tipo in (
                                "movie", "tvMovie", "video", "short", "tvSeries",
                                "tvMiniSeries", "tvSpecial", "tvShort"):
                            val, org = "0", "derivado_tipo"
                        if not val and not args.intra_livestream:
                            v = None   # intra apagado para esta columna por defecto
                    if val:
                        pass
                    elif v:
                        val, org = v, "intra_titulo"
                    elif app in app_default[c]:
                        val, org = app_default[c][app], "app_default"
                    elif c == "contentLength" and args.length_desde_runtime and d["ext_runtime_min"]:
                        b = runtime_a_bucket(d["ext_runtime_min"], buckets)
                        if b:
                            val, org = b, "imdb" if imdb.get("runtime") else ("tvmaze" if tvm.get("runtime") else "wikidata")
                    elif c == "contentLanguage":
                        # Ultimo recurso tras intra/app: el idioma ORIGINAL de la obra
                        # segun Wikidata (P364) o TVMaze. Ojo: es el idioma original,
                        # no la pista de audio servida — por eso va al final.
                        if wd.get("idioma"):
                            val, org = wd["idioma"][0], "wikidata"
                        elif tvm.get("idioma"):
                            val, org = tvm["idioma"][:2].lower(), "tvmaze"
                    elif c == "contentGenre":
                        gs = [IMDB_GENERO_MAP.get(x) for x in imdb.get("generos", [])]
                        gs = [g for g in gs if g]
                        if gs:
                            val, org = ",".join(gs), "imdb"
                        elif tvm.get("generos"):
                            val, org = ",".join(x.lower() for x in tvm["generos"]), "tvmaze"
                    elif c == "contentRating" and wd.get("rating"):
                        val, org = wd["rating"][0], "wikidata"
                    elif c == "contentCategory":
                        # La columna vacia se deriva de OTRA columna de la MISMA fila:
                        # contentGenre esta lleno en el 99% de las filas y el mapa
                        # genero->IAB se aprendio de las filas que traen ambas.
                        # 1) generos inequivocos (deportes->[IAB17], noticias->[IAB12])
                        # 2) genero ambiguo (drama = pelicula o serie?) -> desempata
                        #    el tipo IMDb: movie->[IAB1-5], tvSeries->[IAB1-7]
                        # 3) queda genero pero sin tipo -> [IAB1] generico
                        codes = [GENERO_IAB[g] for g in generos_fila if g in GENERO_IAB]
                        if codes:
                            val, org = codes[0], "derivado_genero"
                        elif tipo in IAB_POR_TIPO:
                            val, org = IAB_POR_TIPO[tipo], "derivado_tipo"
                        elif generos_fila:
                            val, org = IAB_DEFAULT_ENTRETENIMIENTO, "derivado_genero"
                    elif c == "contentSeries":
                        # Si IMDb dice que el titulo ES una serie, el nombre de la
                        # serie es el propio titulo canonico ("40 y 20" -> "40 and
                        # 20"). Para peliculas queda vacio a proposito: una pelicula
                        # no pertenece a ninguna serie (el 85% vacio es correcto).
                        if tipo in ("tvSeries", "tvMiniSeries"):
                            val, org = imdb.get("titulo", ""), "imdb"
                        elif tvm.get("nombre"):
                            val, org = tvm["nombre"], "tvmaze"
                d[c + "_relleno"] = val or ""
                d[c + "_origen"] = org
                stats[c][org or "sin_dato"] += 1
            w.writerow(d)

    resumen = {"entrada": args.entrada, "filas": n, "titulos_distintos": len(claves),
               "titulos_nuevos_consultados": len(nuevas),
               "titulos_con_imdb": sum(1 for k in claves if cache.get(k, {}).get("imdb")),
               "fecha": inicio.strftime("%Y-%m-%d %H:%M"),
               "columnas": {}}
    for c in OBJETIVO:
        s = stats[c]
        lleno = n - s["sin_dato"]
        resumen["columnas"][c] = {
            "pct_original": round(100 * s["original"] / n, 1),
            "pct_final": round(100 * lleno / n, 1),
            "origen": {k: round(100 * v / n, 1) for k, v in s.most_common()}}
    json.dump(resumen, open(args.salida_json, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    for c in OBJETIVO:
        r = resumen["columnas"][c]
        print(f"{c:22} {r['pct_original']:5.1f}% -> {r['pct_final']:5.1f}%  {r['origen']}")


if __name__ == "__main__":
    main()
