# -*- coding: utf-8 -*-
"""Validacion de contentCategory (y contentGenre) contra fuentes abiertas — pipeline repetible.

Responde dos preguntas sobre la columna de categoria IAB de un consolidado (el original o
el relleno por enriquecer_externo.py):

  1. CORRECTITUD  — las filas que traen categoria, ¿la traen bien?
  2. COMPLETITUD  — ¿se puede poner una categoria IAB mas fina (mas granular) que la actual?

FUENTES DE VERDAD
-----------------
  * Taxonomias oficiales IAB Tech Lab (Content Taxonomy 1.0, 2.2 y 3.0), descargadas a
    <cache-dir>/iab/ desde github.com/InteractiveAdvertisingBureau/Taxonomies. Sirven para
    (a) saber si un codigo declarado existe y en que taxonomia, y (b) proponer codigos.
  * El cache de titulos de enriquecer_externo.py (<cache-dir>/titulos.json): por cada titulo
    normalizado, el match IMDb (tipo movie/tvSeries, generos, confianza A-D) y los generos
    de Wikidata (P136). NO se consulta nada online aqui: si un titulo no esta en el cache,
    correr antes enriquecer_externo.py (que es quien lo llena).
  * El propio dataset: el contentGenre de la misma fila (evidencia "interna", mas debil) y
    las demas filas del mismo titulo (consistencia intra-titulo).

COMO SE COMPARA (concepto comun a las tres taxonomias)
------------------------------------------------------
Cada codigo declarado y cada evidencia se traducen a un mismo "concepto" de tres atributos:
    vertical  entretenimiento | deportes | noticias | musica | videojuegos | viajes | ...
    forma     pelicula | tv           (solo tiene sentido dentro de entretenimiento)
    genero    drama | comedia | accion-aventura | terror | documental | telenovela | ...
              (o el sub-deporte: soccer, boxeo...)
Asi `[IAB1-5]` (1.0) = (entretenimiento, pelicula, -), `[333]` (2.2 Drama Movies) =
(entretenimiento, pelicula, drama), y un match IMDb tipo=movie generos=Drama,Romance =
(entretenimiento, pelicula, {drama, romance}). El numero de atributos conocidos (0-3) es
el NIVEL de granularidad, comparable entre taxonomias.

VEREDICTOS DE CORRECTITUD (por fila, sobre las filas con categoria)
------------------------------------------------------------------
  coincide      algun codigo declarado acierta en el atributo mas fino que declara
                (forma o genero) y ninguno contradice
  compatible    lo declarado no contradice pero es generico (solo vertical, o las dos
                formas a la vez `[IAB1-5, IAB1-7]`)
  contradice    algun codigo declarado choca con la evidencia. `detalle` dice en que:
                  vertical  (ej. [IAB12] Noticias para una pelicula de drama)
                  forma     (ej. [IAB1-5] Peliculas para una serie de TV)
                  genero    (ej. [336] Horror Movies para una comedia romantica)
  no_evaluable  sin evidencia para esa fila, o lo declarado no es una categoria
                (texto libre `[sports]`/`[Live]`, codigo inexistente `[IAB-7]`,
                metadato `[1070]` = Content Language > Spanish)

La evidencia se usa en este orden y queda anotada en `evidencia`:
  externa   titulo real con match IMDb de confianza >= --confianza-min (default B).
            Es la unica que prueba las tres cosas (vertical, forma, genero).
  interna   sin match, pero el contentGenre de la misma fila implica vertical o forma
            (genero "Sports" con categoria [IAB1-5]? -> no se marca; genero "Drama" con
            categoria [IAB12] Noticias -> contradice vertical). Solo prueba lo que un
            genero puede implicar; nunca prueba el genero mismo.
  ninguna   ni lo uno ni lo otro -> no_evaluable.

Ojo: un match IMDb de confianza B tiene ~75% de precision, asi que parte de las
contradicciones "externas" son matches equivocados. Para separarlas, cada fila trae
`genero_vs_imdb`: si el contentGenre declarado coincide con los generos IMDb, el match es
creible y la contradiccion de categoria es muy probablemente un error del vendedor; si
tambien el genero choca, sospechar del match. El JSON reporta ambas particiones.

COMPLETITUD (por fila, sobre TODAS las filas)
---------------------------------------------
Para cada fila se calcula la categoria mas fina que la evidencia permite, en dos
taxonomias: `prop_iab22` (Content Taxonomy 2.2, la ultima con hijos de genero bajo
Movies/Television y ~70 deportes) y `prop_iab10` (1.0, la que usa el 80% de las filas
llenas). Se compara el nivel actual (atributos conocidos de lo declarado) con el nivel
propuesto. La forma (pelicula/tv) se toma, en orden, de: tipo IMDb > contentSeries real
> lo ya declarado > genero que la implica (telenovela/reality -> tv). Sin forma pero con
genero se propone el par pelicula+tv del genero (`[333, 647]`), como ya hacen algunos
vendedores.

SALIDAS
-------
  <prefijo>-filas.csv     una fila por fila de entrada con todas las columnas de
                          diagnostico (grande; no se versiona)
  <prefijo>.json          agregados de correctitud y completitud (alimenta el reporte)
  <prefijo>-muestra-contradicciones.csv   top filas contradictorias por requests, para
                                          revision manual
  <prefijo>-muestra-propuestas.csv        muestra aleatoria de propuestas de granularidad

Uso:
    python scripts/validar_categorias.py inventory-consolidado-v10-a-v17.csv \
        reportes/15-validacion-categorias-v17/validacion-consolidado \
        --nombre consolidado --cache-dir cache-enriquecimiento
    python scripts/validar_categorias.py inventory-consolidado-v10-a-v17-relleno.csv \
        reportes/15-validacion-categorias-v17/validacion-relleno --nombre relleno
    (con el relleno se valida contentCategory_relleno y se desglosa por _origen)

Solo stdlib. Descarga las taxonomias IAB (~100 KB) la primera vez.
"""
import argparse
import csv
import json
import os
import random
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enriquecer_externo import (es_util, normalizar_titulo, titulo_real, SERIES_PLACEHOLDER,  # noqa: E402
                                RE_EP, RE_SXXEXX, RE_EPREFIX)
from analizar_genero_titulo_paises import norm_genre  # noqa: E402

csv.field_size_limit(10 ** 8)

# ----------------------------------------------------------------------------
# Taxonomias IAB
# ----------------------------------------------------------------------------
IAB_REPO = ("https://raw.githubusercontent.com/InteractiveAdvertisingBureau/Taxonomies/"
            "main/Content%20Taxonomies/Content%20Taxonomy%20{v}.tsv")
IAB_VERSIONES = ["1.0", "2.2", "3.0"]
UA = "ctv-inventory-validate/0.1 (+https://github.com; contacto: analista)"


def iab_descargar(cache_dir):
    d = os.path.join(cache_dir, "iab")
    os.makedirs(d, exist_ok=True)
    out = {}
    for v in IAB_VERSIONES:
        p = os.path.join(d, f"Content_Taxonomy_{v}.tsv")
        ok = os.path.exists(p) and "<html>" not in open(p, encoding="utf-8", errors="ignore").read(2000)
        for intento in range(6):
            if ok:
                break
            print(f"  descargando IAB Content Taxonomy {v} (intento {intento + 1})", file=sys.stderr)
            try:
                req = urllib.request.Request(IAB_REPO.format(v=v), headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = r.read()
                if b"<html>" in data[:2000]:   # el CDN de GitHub a veces responde 503 en HTML
                    raise IOError("respuesta HTML (503?)")
                open(p, "wb").write(data)
                ok = True
            except Exception as e:
                print(f"  aviso: {e}", file=sys.stderr)
                time.sleep(3 * (intento + 1))
        if not ok:
            sys.exit(f"no se pudo descargar la taxonomia IAB {v}; reintentar con red")
        out[v] = p
    return out


def cargar_iab10(path):
    """IAB Code -> (tier, nombre). Formato: 'IAB Code\\tTier\\tIAB Category'."""
    nodos = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        next(r)
        for row in r:
            if len(row) >= 3 and row[0].startswith("IAB"):
                nodos[row[0].strip()] = {"tier": 1 if row[1].strip() == "Tier 1" else 2,
                                        "nombre": row[2].strip()}
    return nodos


def cargar_iab2x(path):
    """Unique ID -> {parent, nombre, ruta (tiers)}. Formato relacional de 2.x/3.x."""
    nodos = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f, delimiter="\t")
        next(r)
        next(r)
        for row in r:
            if not row or not row[0].strip():
                continue
            ruta = [x.strip() for x in row[3:7] if x.strip()]
            nodos[row[0].strip()] = {"parent": row[1].strip(), "nombre": row[2].strip(),
                                     "ruta": ruta, "tier": len(ruta)}
    return nodos


# ----------------------------------------------------------------------------
# Concepto comun: (vertical, forma, genero)
# ----------------------------------------------------------------------------
# Verticales "de contenido de video": lo que un content object de CTV puede ser. El resto
# de verticales IAB (automotor, inmobiliaria...) existen pero no se esperan en este
# inventario; si aparecen se evaluan igual (contradicen si hay evidencia).
VERT_10 = {1: "entretenimiento", 2: "automotor", 3: "negocios", 4: "carreras", 5: "educacion",
           6: "familia", 7: "salud", 8: "gastronomia", 9: "hobbies", 10: "hogar",
           11: "politica", 12: "noticias", 13: "finanzas", 14: "sociedad", 15: "ciencia",
           16: "mascotas", 17: "deportes", 18: "estilo", 19: "tecnologia", 20: "viajes",
           21: "inmobiliaria", 22: "compras", 23: "religion", 24: "sin_categoria",
           25: "no_estandar", 26: "ilegal"}
VERT_2X = {"Movies": "entretenimiento", "Television": "entretenimiento",
           "Entertainment": "entretenimiento", "Pop Culture": "entretenimiento",
           "Music and Audio": "musica", "Music": "musica", "Sports": "deportes",
           "News and Politics": "noticias", "Politics": "politica", "Crime": "noticias",
           "Video Gaming": "videojuegos", "Travel": "viajes", "Food & Drink": "gastronomia",
           "Religion & Spirituality": "religion", "Education": "educacion",
           "Business and Finance": "negocios", "Healthy Living": "salud",
           "Medical Health": "salud", "Style & Fashion": "estilo",
           "Technology & Computing": "tecnologia", "Science": "ciencia",
           "Family and Relationships": "familia", "Pets": "mascotas",
           "Home & Garden": "hogar", "Automotive": "automotor",
           "Hobbies & Interests": "hobbies", "Fine Art": "arte",
           "Books and Literature": "libros", "Careers": "carreras",
           "Events and Attractions": "eventos", "Attractions": "eventos", "Events": "eventos",
           "Personal Finance": "finanzas", "Real Estate": "inmobiliaria",
           "Shopping": "compras", "Sensitive Topics": "sensible",
           "Brand Suitability and Risk": "sensible", "Genres": "entretenimiento",
           "Holidays": "entretenimiento", "War and Conflicts": "noticias",
           "Disasters": "noticias", "Law": "politica",
           "Personal Celebrations & Life Events": "sociedad",
           # Ramas 1000+ de 2.2: no son categorias de contenido, son metadatos
           "Content Channel": "metadato", "Content Type": "metadato",
           "Content Source": "metadato", "Content Media Format": "metadato",
           "Content Language": "metadato", "Content Source Geo": "metadato"}

# Nombre del nodo de genero (2.2 Movies/Television, 3.0 Genres) -> genero canonico.
GENERO_POR_NOMBRE = [
    ("action", "accion-aventura"), ("adventure", "accion-aventura"), ("romance", "romance"),
    ("science fiction", "sci-fi"), ("indie", "indie"), ("arthouse", "indie"),
    ("special interest", "indie"), ("animation", "animacion"), ("anime", "animacion"),
    ("comedy", "comedia"), ("crime", "crimen-misterio"), ("mystery", "crimen-misterio"),
    ("documentary", "documental"), ("factual", "documental"), ("biograph", "documental"),
    ("history", "documental"), ("nature", "documental"), ("drama", "drama"),
    ("family", "infantil-familia"), ("children", "infantil-familia"),
    ("young adult", "infantil-familia"), ("fantasy", "fantasia"), ("horror", "terror"),
    ("world", "world"), ("soap", "telenovela"), ("sports", "deportes"),
    ("holiday", "holiday"), ("music", "musica"), ("musical", "musica"),
    ("reality", "reality"), ("talk show", "talk show"), ("western", "western"),
    ("lifestyle", "lifestyle"),
]

# Genero canonico del dataset (salida de norm_genre) -> concepto que implica.
# vertical: el genero nombra una vertical distinta de entretenimiento.
# forma:    el genero implica pelicula o tv.
# genero:   el genero de ficcion/no ficcion comparable con IMDb/IAB 2.2.
GENERO_DATASET = {
    "drama": {"genero": "drama"}, "comedia": {"genero": "comedia"},
    "romance": {"genero": "romance"}, "terror": {"genero": "terror"},
    "thriller": {"genero": "crimen-misterio"}, "misterio": {"genero": "crimen-misterio"},
    "crimen": {"genero": "crimen-misterio"}, "accion": {"genero": "accion-aventura"},
    "aventura": {"genero": "accion-aventura"}, "western": {"genero": "western"},
    "sci-fi": {"genero": "sci-fi"}, "fantasia": {"genero": "fantasia"},
    "documental": {"genero": "documental"}, "belico": {"genero": "accion-aventura"},
    "infantil-familia": {"genero": "infantil-familia"}, "animacion": {"genero": "animacion"},
    "anime": {"genero": "animacion"}, "reality": {"genero": "reality", "forma": "tv"},
    "telenovela": {"genero": "telenovela", "forma": "tv"},
    "talk show": {"genero": "talk show", "forma": "tv"},
    "concursos": {"genero": "concursos", "forma": "tv"},
    "noticias": {"vertical": "noticias"}, "deportes": {"vertical": "deportes"},
    "musica": {"vertical": "musica"}, "videojuegos": {"vertical": "videojuegos"},
    "viajes": {"vertical": "viajes"}, "gastronomia": {"vertical": "gastronomia"},
    "religion": {"vertical": "religion"}, "educacion": {"vertical": "educacion"},
    "lifestyle": {"vertical": "lifestyle"},
    "pelicula (generico)": {"forma": "pelicula"}, "tv/series (generico)": {"forma": "tv"},
    "entretenimiento": {}, "otros/desconocido": {},
}
# Generos de ficcion: si el contentGenre dice esto y la categoria dice Noticias/Deportes/
# Musica..., la categoria contradice al genero (evidencia interna).
GENEROS_FICCION = {"drama", "comedia", "romance", "terror", "crimen-misterio",
                   "accion-aventura", "western", "sci-fi", "fantasia", "telenovela"}
# Generos de NO ficcion: con ellos el tema del programa puede ser cualquiera (un
# documental de viajes, un reality de cocina) y IMDb no lo dice -> las verticales
# tematicas no se pueden contradecir.
GENEROS_NO_FICCION = {"documental", "reality", "talk show", "concursos", "noticias",
                      "deportes", "musica"}
# Verticales "fuertes": nombran un tipo de contenido reconocible por el genero.
VERT_FUERTES = {"deportes", "noticias", "musica", "videojuegos"}
# Verticales tematicas: el tema de un programa de no ficcion; nunca se contradicen
# entre si ni con una vertical fuerte (hay noticias de negocios, deportes extremos...).
VERT_TEMA = {"viajes", "gastronomia", "salud", "tecnologia", "negocios", "finanzas",
             "hobbies", "estilo", "educacion", "ciencia", "religion", "familia", "hogar",
             "automotor", "mascotas", "sociedad", "arte", "libros", "carreras", "compras",
             "eventos", "inmobiliaria", "politica", "lifestyle", "otros"}
# Verticales que un titulo de entretenimiento tambien puede llevar segun su genero IMDb.
VERT_POR_GENERO_IMDB = {"Sport": "deportes", "News": "noticias", "Music": "musica",
                        "Musical": "musica"}
IMDB_GENERO = {"Drama": "drama", "Comedy": "comedia", "Romance": "romance",
               "Horror": "terror", "Thriller": "crimen-misterio", "Mystery": "crimen-misterio",
               "Crime": "crimen-misterio", "Film-Noir": "crimen-misterio",
               "Action": "accion-aventura", "Adventure": "accion-aventura",
               "War": "accion-aventura", "Western": "western", "Sci-Fi": "sci-fi",
               "Fantasy": "fantasia", "Documentary": "documental", "Biography": "documental",
               "History": "documental", "News": "noticias", "Sport": "deportes",
               "Music": "musica", "Musical": "musica", "Family": "infantil-familia",
               "Animation": "animacion", "Reality-TV": "reality", "Talk-Show": "talk show",
               "Game-Show": "concursos"}
# Una biografia o pelicula historica casi siempre es drama tambien: no castigar [333].
IMDB_GENERO_EXTRA = {"Biography": "drama", "History": "drama", "War": "drama"}
WIKIDATA_GENERO = [
    ("telenovela", "telenovela"), ("soap opera", "telenovela"), ("christmas", "holiday"),
    ("children", "infantil-familia"), ("family", "infantil-familia"),
    ("teen", "infantil-familia"), ("martial arts", "accion-aventura"),
    ("superhero", "accion-aventura"), ("disaster", "accion-aventura"),
    ("action", "accion-aventura"), ("adventure", "accion-aventura"), ("war film", "accion-aventura"),
    ("documentary", "documental"), ("biographical", "drama"), ("historical", "drama"),
    ("animated", "animacion"), ("anime", "animacion"), ("western", "western"),
    ("comedy", "comedia"), ("drama", "drama"), ("horror", "terror"), ("slasher", "terror"),
    ("monster", "terror"), ("zombie", "terror"), ("romance", "romance"), ("romantic", "romance"),
    ("science fiction", "sci-fi"), ("fantasy", "fantasia"), ("thriller", "crimen-misterio"),
    ("crime", "crimen-misterio"), ("mystery", "crimen-misterio"), ("heist", "crimen-misterio"),
    ("noir", "crimen-misterio"), ("musical", "musica"), ("concert", "musica"),
    ("sports", "deportes"), ("reality", "reality"), ("talk show", "talk show"),
    ("game show", "concursos"), ("independent", "indie"), ("art film", "indie"),
]
FORMA_IMDB = {"movie": "pelicula", "tvSeries": "tv", "tvMiniSeries": "tv"}
# tvMovie/short/video/tvSpecial: sin forma (una TV movie cabe en Movies y en Television)
CONFIANZA_ORDEN = "ABCD"

# Sub-deportes: palabra en el contentGenre o nombre del nodo -> nombre del nodo 2.2 y codigo 1.0
SUBDEPORTES = [
    (("soccer", "futbol", "fútbol", "world soccer", "liga mx", "la liga", "champions"), "Soccer", "IAB17-44"),
    (("boxing", "boxeo"), "Boxing", "IAB17-5"),
    (("wrestling", "lucha libre", "lucha"), "Wrestling", None),
    (("basketball", "baloncesto", "basquet", "nba", "pro basketball"), "Basketball", "IAB17-26"),
    (("baseball", "beisbol", "béisbol", "mlb"), "Baseball", "IAB17-2"),
    (("tennis", "tenis"), "Tennis", "IAB17-40"),
    (("golf",), "Golf", "IAB17-15"),
    (("motorsport", "motorsports", "auto racing", "racing", "formula 1", "f1", "nascar", "motor",
      "motocross", "fmx", "rally"), "Auto Racing", "IAB17-1"),
    (("mma", "martial arts", "artes marciales", "ufc"), "Martial Arts", "IAB17-20"),
    (("cycling", "ciclismo", "bicycling"), "Cycling", "IAB17-3"),
    (("volleyball", "voleibol", "voley"), "Volleyball", "IAB17-41"),
    (("american football", "nfl"), "American Football", "IAB17-12"),
    (("fishing", "pesca", "fly fishing", "freshwater fishing", "saltwater fishing"), "Fishing Sports", "IAB17-13"),
    (("hunting", "caza", "hunting/shooting"), "Hunting and Shooting", "IAB17-18"),
    (("cricket",), "Cricket", "IAB17-9"),
    (("rugby",), "Rugby", "IAB17-29"),
    (("hockey", "ice hockey", "pro ice hockey"), "Ice Hockey", "IAB17-27"),
    (("olympics", "olimpicos", "olímpicos"), "Olympic Sports", "IAB17-23"),
    (("poker",), "Poker and Professional Gambling", None),
    (("surf", "surfing", "surfing/bodyboarding"), "Surfing and Bodyboarding", "IAB17-37"),
    (("skate", "skateboarding"), "Skateboarding", "IAB17-34"),
    (("swimming", "natacion", "natación"), "Swimming", "IAB17-38"),
    (("athletics", "atletismo", "track and field", "running", "running/jogging"), "Track and Field", "IAB17-30"),
    (("gymnastics", "gimnasia"), "Gymnastics", None),
    (("horse racing", "hipica", "hípica", "horses"), "Horse Racing", "IAB17-16"),
    (("extreme", "extremos"), "Extreme Sports", None),
    (("esports", "e-sports"), "eSports", None),
    (("football",), "American Football", "IAB17-12"),  # en 1.0 "Football" es americano; va al final a proposito
]

SUB_POR_CODIGO10 = {c: nombre for _kws, nombre, c in SUBDEPORTES if c}

RE_CODE = re.compile(r"^(IAB-?(\d+)((?:-\d+)*)|\d+)$", re.I)


class Taxonomias:
    def __init__(self, cache_dir):
        paths = iab_descargar(cache_dir)
        self.t10 = cargar_iab10(paths["1.0"])
        self.t22 = cargar_iab2x(paths["2.2"])
        self.t30 = cargar_iab2x(paths["3.0"])
        # indices para proponer: nombre de nodo -> id en 2.2, por padre
        self.hijos22 = defaultdict(dict)
        for i, n in self.t22.items():
            if n["parent"]:
                self.hijos22[n["parent"]][n["nombre"].lower()] = i
        self.id22 = {n["nombre"]: i for i, n in self.t22.items() if not n["parent"]}
        # Movies/Television: genero canonico -> id del hijo
        self.gen_movie = self._generos_hijos(self.id22["Movies"])
        self.gen_tv = self._generos_hijos(self.id22["Television"])
        self.sub_sport = {}
        for nombre, i in self.hijos22[self.id22["Sports"]].items():
            self.sub_sport[nombre] = i
            for sub, j in self.hijos22.get(i, {}).items():
                self.sub_sport[sub] = j
        self.sub_news = self.hijos22[self.id22["News and Politics"]]
        self.nombre10 = {k: v["nombre"] for k, v in self.t10.items()}

    def _generos_hijos(self, padre):
        out = {}
        for nombre, i in self.hijos22[padre].items():
            for kw, g in GENERO_POR_NOMBRE:
                if kw in nombre:
                    out.setdefault(g, i)
                    break
        return out

    # ---- codigo declarado -> nodo con concepto --------------------------------------
    def nodo(self, tok):
        """Devuelve dict {codigo, taxonomia, formato, tier, nombre, vertical, forma, genero, sub}."""
        t = tok.strip()
        m = RE_CODE.match(t)
        base = {"codigo": t, "taxonomia": "", "formato": "", "tier": 0, "nombre": "",
                "vertical": None, "forma": None, "genero": None, "sub": None}
        if not m:
            base["formato"] = "texto_libre"
            low = t.lower()
            if low in ("sports", "sport", "deportes"):
                base.update(vertical="deportes", nombre=t)
            elif low in ("entertainment", "entretenimiento"):
                base.update(vertical="entretenimiento", nombre=t)
            elif low in ("news", "noticias"):
                base.update(vertical="noticias", nombre=t)
            elif low in ("music", "musica"):
                base.update(vertical="musica", nombre=t)
            return base
        if t.upper().startswith("IAB"):
            code = t.upper()
            t1 = int(m.group(2))
            base["taxonomia"] = "1.0"
            if code.startswith("IAB-") or code.count("-") > 1:
                # [IAB-7] o [IAB1-6-3]: no existe en 1.0; se lee el tier 1 si lo hay
                base["formato"] = "no_estandar"
                if code.startswith("IAB-") or f"IAB{t1}" not in self.t10:
                    return base
                base.update(tier=1, nombre=self.t10[f"IAB{t1}"]["nombre"] + " (codigo inexistente)")
                base["vertical"] = VERT_10.get(t1)
                return base
            if code in self.t10:
                base.update(formato="estandar", tier=self.t10[code]["tier"], nombre=self.t10[code]["nombre"])
            elif f"IAB{t1}" in self.t10:
                base.update(formato="no_estandar", tier=1, nombre=self.t10[f"IAB{t1}"]["nombre"] + " (tier 2 inexistente)")
            else:
                base.update(formato="no_estandar")
                return base
            base["vertical"] = VERT_10.get(t1)
            if code == "IAB1-5":
                base["forma"] = "pelicula"
            elif code == "IAB1-7":
                base["forma"] = "tv"
            elif code == "IAB1-6":
                base["vertical"] = "musica"
            elif code == "IAB1-4":
                base["genero"] = "comedia"
            elif code == "IAB1-1":
                base["vertical"] = "libros"
            elif code == "IAB1-3":
                base["vertical"] = "arte"
            elif code == "IAB9-30":
                base["vertical"] = "videojuegos"
            elif t1 == 17 and base["tier"] == 2:
                # nombre canonico (el de 2.2): IAB17-44 "World Soccer" = Soccer
                base["sub"] = SUB_POR_CODIGO10.get(code, base["nombre"])
            return base
        # numerico: 2.2 (superset de los ids de 3.0 para lo que usa este dataset)
        base["taxonomia"] = "2.2"
        n = self.t22.get(t) or self.t30.get(t)
        if not n:
            base["formato"] = "no_estandar"
            return base
        base.update(formato="estandar", tier=n["tier"], nombre=" > ".join(n["ruta"]))
        raiz = n["ruta"][0]
        base["vertical"] = VERT_2X.get(raiz, "otros")
        if n["nombre"] == "Crime":          # 380: News and Politics > Crime (true crime / policial)
            base["genero"] = "crimen-misterio"
        if raiz in ("Movies", "Television"):
            base["forma"] = "pelicula" if raiz == "Movies" else "tv"
            if n["tier"] >= 2:
                base["genero"] = self._genero_de_nombre(n["nombre"])
                if base["genero"] == "deportes":
                    base["vertical"] = "deportes"   # 644 Sports TV
                    base["genero"] = None
        elif raiz == "Genres":           # 3.0
            base["genero"] = self._genero_de_nombre(n["nombre"])
        elif raiz == "Sports" and n["tier"] >= 2:
            base["sub"] = n["nombre"]
        elif raiz == "Entertainment" and n["tier"] >= 2:   # 3.0 Entertainment > Movies
            if n["ruta"][1] == "Movies":
                base["forma"] = "pelicula"
            elif n["ruta"][1] == "Television":
                base["forma"] = "tv"
            elif n["ruta"][1] == "Music":
                base["vertical"] = "musica"
        return base

    @staticmethod
    def _genero_de_nombre(nombre):
        low = nombre.lower()
        for kw, g in GENERO_POR_NOMBRE:
            if kw in low:
                return g
        return None

    # ---- propuesta 2.2 / 1.0 --------------------------------------------------------
    def proponer(self, vertical, forma, generos, sub):
        """Devuelve (codigos 2.2, codigos 1.0, nivel) para un concepto."""
        c22, c10 = [], []
        if vertical == "deportes":
            if sub and sub.lower() in self.sub_sport:
                c22.append(self.sub_sport[sub.lower()])
            else:
                c22.append(self.id22["Sports"])
            c10.append(next((c for kws, nom, c in SUBDEPORTES if nom == sub and c), None) or "IAB17")
            nivel = 2 if sub else 1
            return c22, [c for c in c10 if c], nivel
        simples = {"noticias": ("News and Politics", "IAB12"), "musica": ("Music and Audio", "IAB1-6"),
                   "videojuegos": ("Video Gaming", "IAB9-30"), "viajes": ("Travel", "IAB20"),
                   "gastronomia": ("Food & Drink", "IAB8"), "religion": ("Religion & Spirituality", "IAB23"),
                   "educacion": ("Education", "IAB5")}
        if vertical in simples:
            n22, n10 = simples[vertical]
            return [self.id22[n22]], [n10], 1
        if vertical != "entretenimiento":
            return [], [], 0
        gens = [g for g in generos if g]
        if forma == "pelicula":
            ids = [self.gen_movie[g] for g in gens if g in self.gen_movie]
            c22 = ids or [self.id22["Movies"]]
            c10 = ["IAB1-5"]
            return c22, c10, 3 if ids else 2
        if forma == "tv":
            ids = [self.gen_tv[g] for g in gens if g in self.gen_tv]
            c22 = ids or [self.id22["Television"]]
            c10 = ["IAB1-7"]
            return c22, c10, 3 if ids else 2
        # sin forma: par pelicula+tv por genero (como [333, 647])
        pares = []
        for g in gens:
            if g in self.gen_movie:
                pares.append(self.gen_movie[g])
            if g in self.gen_tv:
                pares.append(self.gen_tv[g])
        if pares:
            return pares, ["IAB1"], 2   # nivel 2: vertical + genero, forma ambigua
        return [], ["IAB1"], 1


RE_TEMPORADA = re.compile(r"\b(season|temporada|episodio|episode|cap[ií]tulo|s\d{1,2}\s*e\d{1,3}|"
                          r"t\d{1,2}\s*e\d{1,3}|ep\.?\s*\d+)\b", re.I)


def forma_por_titulo(titulo_crudo):
    """Si el titulo crudo dice "season 4", "episodio 12", "S02E05"... el contenido es una
    serie, diga lo que diga el match IMDb (que se hizo con el titulo sin ese sufijo y
    puede haber caido en una pelicula homonima: "yoyo season 1" -> Yoyo (1965))."""
    t = (titulo_crudo or "").strip()
    if RE_TEMPORADA.search(t) or RE_SXXEXX.search(t) or RE_EPREFIX.match(t):
        return "tv"
    return None


def sub_deporte_de_texto(texto):
    low = (texto or "").lower()
    for kws, nombre, _ in SUBDEPORTES:
        if any(re.search(r"\b" + re.escape(k) + r"\b", low) for k in kws):
            return nombre
    return None


def parse_categoria(v):
    s = (v or "").strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    return [t.strip() for t in s.split(",") if t.strip()]


# ----------------------------------------------------------------------------
def evidencia_externa(rec, conf_ok, forma_titulo=None):
    """Del cache de titulos -> forma, generos, verticales aceptadas, es_ficcion.
    forma_titulo ("tv" si el titulo crudo trae season/episodio) manda sobre el tipo IMDb."""
    imdb = (rec or {}).get("imdb") or {}
    if not imdb or imdb.get("confianza", "D") not in conf_ok:
        return None
    forma = forma_titulo or FORMA_IMDB.get(imdb.get("tipo", ""))
    gens, verts = set(), {"entretenimiento"}
    for g in imdb.get("generos", []):
        if g in IMDB_GENERO:
            gens.add(IMDB_GENERO[g])
        if g in IMDB_GENERO_EXTRA:
            gens.add(IMDB_GENERO_EXTRA[g])
        if g in VERT_POR_GENERO_IMDB:
            verts.add(VERT_POR_GENERO_IMDB[g])
    wd = (rec or {}).get("wikidata") or {}
    for g in wd.get("generos", []):
        low = g.lower()
        for kw, gc in WIKIDATA_GENERO:
            if kw in low:
                gens.add(gc)
                break
    if gens & {"telenovela", "reality", "talk show", "concursos"}:
        forma = forma or "tv"
    for g in ("deportes", "musica", "noticias"):
        if g in gens:
            verts.add(g)
    if "noticias" in verts:
        verts.add("politica")          # IAB11 Law, Gov't & Politics en un noticiero: aceptable
    if "infantil-familia" in gens:
        verts.add("familia")           # IAB6 Family & Parenting en contenido infantil: aceptable
    # Ficcion pura: el tema es el genero. No ficcion (documental, reality, talk...): el
    # tema puede ser cualquier vertical y IMDb no lo registra -> no se contradice.
    es_ficcion = bool(gens & GENEROS_FICCION) and not (gens & GENEROS_NO_FICCION)
    return {"forma": forma, "generos": gens, "verticales": verts, "es_ficcion": es_ficcion,
            "confianza": imdb.get("confianza"), "tipo": imdb.get("tipo"), "id": imdb.get("id"),
            "titulo": imdb.get("titulo")}


def evidencia_interna(generos_norm, genero_crudo=""):
    """Del contentGenre de la fila -> (vertical implicada, forma implicada, generos, sub-deporte).
    Si el texto del genero nombra un deporte ("Soccer", "Auto Racing", "baseball") la
    vertical es deportes aunque el diccionario de generos no lo mapee."""
    vert, forma, gens = None, None, set()
    sub = sub_deporte_de_texto(genero_crudo)
    if sub:
        vert = "deportes"
    for g in generos_norm:
        c = GENERO_DATASET.get(g, {})
        if c.get("vertical") and not vert:
            vert = c["vertical"]
        if c.get("forma") and not forma:
            forma = c["forma"]
        if c.get("genero"):
            gens.add(c["genero"])
    return {"vertical": vert, "forma": forma, "generos": gens, "sub": sub}


def veredicto_fila(nodos, ext, inte):
    """Devuelve (evidencia, veredicto, detalle, nivel_actual).

    Reglas (la primera que aplica a cada codigo declarado):
      - el codigo nombra un genero y ese genero esta en la evidencia -> acierta
        (vale para [333] Drama Movies y para [380] News > Crime en un policial)
      - vertical: choca si la evidencia dice FICCION y el codigo dice una vertical que
        no es entretenimiento (ni familia/politica cuando aplican). Con no ficcion, una
        vertical tematica (viajes, gastronomia, tecnologia...) no se puede juzgar.
        Entre verticales fuertes (deportes/noticias/musica/videojuegos) choca si la
        evidencia nombra una y el codigo otra (salvo deportes<->noticias).
      - forma: choca si el codigo declara UNA sola forma y la evidencia dice la otra.
      - genero: choca si el codigo nombra un genero que la evidencia no trae.
    """
    evaluables = [n for n in nodos if n["vertical"] not in (None, "metadato", "sensible",
                                                             "sin_categoria", "no_estandar")]
    nivel = 0
    for n in evaluables:
        nivel = max(nivel, 1 + (1 if n["forma"] else 0) + (1 if (n["genero"] or n["sub"]) else 0))
    if not evaluables:
        return "ninguna", "no_evaluable", "sin_codigo_evaluable", nivel
    formas = {n["forma"] for n in evaluables if n["forma"]}
    ambigua = len(formas) > 1

    def evaluar(evid, verticales, forma_esp, generos_esp, es_ficcion, vert_fuerte_esp, sub_esp=None):
        problemas, aciertos = [], []
        for n in evaluables:
            v = n["vertical"]
            if n["genero"] and generos_esp and n["genero"] in generos_esp:
                aciertos.append(n["codigo"])
                continue
            if n["sub"] and sub_esp:
                # el codigo nombra un deporte concreto y el genero declarado nombra otro:
                # [IAB17-1] Auto Racing con genero "Soccer"
                if n["sub"].lower() != sub_esp.lower() and not (
                        {n["sub"].lower(), sub_esp.lower()} <= {"auto racing", "motorcycle sports"}):
                    problemas.append(f"sub:{n['sub']}!={sub_esp}")
                    continue
                aciertos.append(n["codigo"])
                continue
            if v not in verticales:
                if es_ficcion and v not in ("religion", "familia"):
                    # religion y familia son temas que la ficcion tambien lleva
                    # (cine cristiano, cine familiar); el resto no
                    problemas.append(f"vertical:{v}")
                    continue
                if v in VERT_FUERTES and vert_fuerte_esp and v != vert_fuerte_esp and \
                        {v, vert_fuerte_esp} != {"deportes", "noticias"}:
                    problemas.append(f"vertical:{v}")
                    continue
                continue              # tema de no ficcion: no verificable con esta evidencia
            elif v in VERT_FUERTES:
                aciertos.append(n["codigo"])   # vertical especifica acertada
            if n["forma"] and forma_esp and not ambigua:
                if n["forma"] != forma_esp:
                    problemas.append(f"forma:{n['forma']}!={forma_esp}")
                    continue
                aciertos.append(n["codigo"])
            if n["genero"] and generos_esp and n["genero"] not in generos_esp:
                problemas.append(f"genero:{n['genero']}")
        if problemas:
            return evid, "contradice", ";".join(sorted(set(problemas))), nivel
        if aciertos:
            return evid, "coincide", "", nivel
        return evid, "compatible", ("forma_ambigua" if ambigua else "generico"), nivel

    if ext:
        verticales = set(ext["verticales"])
        if inte["vertical"]:
            verticales.add(inte["vertical"])   # el vendedor dice "Auto Racing": IAB17 es coherente
        fuerte = next((x for x in ("deportes", "noticias", "musica") if x in ext["verticales"]), None)
        return evaluar("externa", verticales, ext["forma"], ext["generos"], ext["es_ficcion"], fuerte, inte.get("sub"))
    if inte and (inte["vertical"] or inte["forma"] or inte["generos"]):
        es_ficcion = bool(inte["generos"] & GENEROS_FICCION) and not inte["vertical"] and \
            not (inte["generos"] & GENEROS_NO_FICCION)
        verticales = {"entretenimiento", "familia"} | ({inte["vertical"]} if inte["vertical"] else set())
        fuerte = inte["vertical"] if inte["vertical"] in VERT_FUERTES else None
        return evaluar("interna", verticales, inte["forma"], inte["generos"], es_ficcion, fuerte, inte.get("sub"))
    return "ninguna", "no_evaluable", "sin_evidencia", nivel


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
def pct(n, d):
    return round(100.0 * n / d, 2) if d else 0.0


class Agg:
    """Contador doble (filas, requests) por clave."""
    def __init__(self):
        self.f = Counter()
        self.r = Counter()

    def add(self, k, req):
        self.f[k] += 1
        self.r[k] += req

    def dump(self, tot_f=None, tot_r=None, top=None):
        items = self.f.most_common(top)
        return {k: {"filas": v, "requests": self.r[k],
                    "pct_filas": pct(v, tot_f) if tot_f else None,
                    "pct_requests": pct(self.r[k], tot_r) if tot_r else None}
                for k, v in items}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("prefijo_salida", help="prefijo de los archivos de salida (sin extension)")
    ap.add_argument("--nombre", default="", help="etiqueta del dataset (consolidado / relleno)")
    ap.add_argument("--cache-dir", default="cache-enriquecimiento")
    ap.add_argument("--confianza-min", default="B", choices=list("ABCD"),
                    help="peor confianza IMDb aceptada como evidencia externa (default B)")
    ap.add_argument("--columna", default="", help="columna de categoria a validar "
                    "(default: contentCategory_relleno si existe, si no contentCategory)")
    ap.add_argument("--paises", default="Mexico,Colombia,Chile")
    ap.add_argument("--top-publishers", type=int, default=12)
    ap.add_argument("--muestra", type=int, default=400)
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--filas", default="", help="ruta del CSV fila a fila (default <prefijo>-filas.csv; "
                    "es grande, conviene dejarlo fuera de reportes/)")
    args = ap.parse_args()
    conf_ok = set(CONFIANZA_ORDEN[:CONFIANZA_ORDEN.index(args.confianza_min) + 1])
    random.seed(args.semilla)
    inicio = datetime.now()

    tax = Taxonomias(args.cache_dir)
    cache_path = os.path.join(args.cache_dir, "titulos.json")
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
    print(f"taxonomias: 1.0={len(tax.t10)} nodos, 2.2={len(tax.t22)}, 3.0={len(tax.t30)}; "
          f"cache de titulos: {len(cache)}", file=sys.stderr)

    # ---- pasada 1: leer, normalizar titulo, aprender consistencia intra-titulo ----------
    filas = []
    with open(args.entrada, encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        columnas = lector.fieldnames
        for d in lector:
            filas.append(d)
    n = len(filas)
    col_cat = args.columna or ("contentCategory_relleno" if "contentCategory_relleno" in columnas
                               else "contentCategory")
    col_origen = "contentCategory_origen" if col_cat == "contentCategory_relleno" and \
        "contentCategory_origen" in columnas else None
    tiene_gn = "genero_normalizado" in columnas
    print(f"{n} filas; columna validada: {col_cat}", file=sys.stderr)

    nodos_cache = {}
    inte_forma_cache = {}

    def nodos_de(v):
        if v not in nodos_cache:
            nodos_cache[v] = [tax.nodo(t) for t in parse_categoria(v)]
        return nodos_cache[v]

    # consistencia intra-titulo: por titulo, que (vertical) y (forma) declaran sus filas
    tit_vert = defaultdict(Counter)
    tit_forma = defaultdict(Counter)
    for d in filas:
        t = (d.get("contentTitle") or "").strip()
        k = normalizar_titulo(t) if titulo_real(t) else ""
        d["_k"] = k
        d["_req"] = int(float(d.get("Total Requests") or 0))
        v = d.get(col_cat) or ""
        d["_cat_ok"] = es_util("contentCategory", v)
        if k and d["_cat_ok"]:
            ns = [x for x in nodos_de(v) if x["vertical"] and x["vertical"] not in ("metadato", "sensible", "no_estandar", "sin_categoria")]
            verts = {x["vertical"] for x in ns}
            formas = {x["forma"] for x in ns if x["forma"]}
            for x in verts:
                tit_vert[k][x] += 1
            if len(formas) == 1:
                tit_forma[k][next(iter(formas))] += 1
    tit_conf_vert = {k for k, c in tit_vert.items() if len(c) > 1}
    tit_conf_forma = {k for k, c in tit_forma.items() if len(c) > 1}
    # la mayoria del titulo: una fila esta "en minoria" si su vertical (o su forma) no es
    # la que declara la mayoria de las filas del mismo titulo
    tit_mayoria_vert = {k: c.most_common(1)[0][0] for k, c in tit_vert.items()}
    tit_mayoria_forma = {k: c.most_common(1)[0][0] for k, c in tit_forma.items()}

    # ---- pasada 2: validar y proponer fila por fila -----------------------------------
    tot_req = sum(d["_req"] for d in filas)
    paises = [p.strip() for p in args.paises.split(",") if p.strip()]
    pub_top = [p for p, _ in Counter(d.get("Publisher", "") for d in filas).most_common(args.top_publishers)]

    A = defaultdict(Agg)          # agregados nombrados
    contra_titulos = Agg()        # titulo -> filas contradictorias
    contra_pares = Agg()          # (declarado -> esperado)
    contra_ejemplo = {}
    prop_top = Agg()
    muestra_contra, muestra_prop = [], []
    reglas = Agg()
    genero_vs = Agg()
    genero_vs_pub = defaultdict(Agg)

    salida_cols = [c for c in ("Publisher", "App Name", "Country", "contentGenre", "contentTitle",
                               "contentSeries", "Total Requests", "eCPM") if c in columnas]
    salida_cols += [col_cat] + ([col_origen] if col_origen else [])
    salida_cols += ["titulo_clave", "ext_imdb_id", "ext_tipo", "ext_generos", "ext_confianza",
                    "cat_formato", "cat_taxonomia", "cat_nombres", "nivel_actual",
                    "evidencia", "veredicto", "detalle", "genero_vs_imdb",
                    "conflicto_intra_titulo", "prop_iab22", "prop_iab22_nombres", "prop_iab10",
                    "nivel_propuesto", "ganancia", "prop_forma_origen", "prop_evidencia"]
    filas_path = args.filas or (args.prefijo_salida + "-filas.csv")
    os.makedirs(os.path.dirname(os.path.abspath(filas_path)), exist_ok=True)
    w = csv.DictWriter(open(filas_path, "w", encoding="utf-8", newline=""),
                       fieldnames=salida_cols, extrasaction="ignore")
    w.writeheader()

    for d in filas:
        k, req = d["_k"], d["_req"]
        pais, pub = d.get("Country", ""), d.get("Publisher", "")
        origen = d.get(col_origen, "") if col_origen else ""
        rec = cache.get(k) if k else None
        forma_tit = forma_por_titulo(d.get("contentTitle", "")) if k else None
        ext = evidencia_externa(rec, conf_ok, forma_tit) if rec else None
        if forma_tit and not inte_forma_cache.get(k):
            inte_forma_cache[k] = forma_tit
        if tiene_gn:
            gnorm = [g for g in (d.get("genero_normalizado") or "").split(";") if g]
        else:
            gnorm = norm_genre(d.get("contentGenre") or "")[0]
        inte = evidencia_interna(gnorm, d.get("contentGenre", ""))
        if forma_tit and not inte["forma"]:
            inte["forma"] = forma_tit       # "x season 2" es serie aunque el genero no lo diga
        imdb = (rec or {}).get("imdb") or {}
        d["titulo_clave"] = k
        d["ext_imdb_id"] = imdb.get("id", "")
        d["ext_tipo"] = imdb.get("tipo", "")
        d["ext_generos"] = ",".join(imdb.get("generos", []))
        d["ext_confianza"] = imdb.get("confianza", "")

        # genero declarado vs IMDb (proxy de calidad del match y validacion de contentGenre)
        if ext and ext["generos"] and inte["generos"]:
            gv = "coincide" if inte["generos"] & ext["generos"] else "no_coincide"
        elif ext and ext["generos"]:
            gv = "sin_genero_declarado"
        else:
            gv = "no_comparable"
        d["genero_vs_imdb"] = gv
        if ext:
            genero_vs.add(gv, req)
            if pub in pub_top:
                genero_vs_pub[pub].add(gv, req)

        # ---- correctitud --------------------------------------------------------------
        v = d.get(col_cat) or ""
        nodos = nodos_de(v) if d["_cat_ok"] else []
        d["cat_formato"] = ";".join(sorted({x["formato"] for x in nodos}))
        d["cat_taxonomia"] = ";".join(sorted({x["taxonomia"] or "ninguna" for x in nodos}))
        d["cat_nombres"] = " | ".join(x["nombre"] or x["codigo"] for x in nodos)
        conflicto = ""
        if k and d["_cat_ok"] and (k in tit_conf_vert or k in tit_conf_forma):
            ns = [x for x in nodos if x["vertical"] and x["vertical"] not in ("metadato", "sensible", "no_estandar", "sin_categoria")]
            verts = {x["vertical"] for x in ns}
            formas_d = {x["forma"] for x in ns if x["forma"]}
            if k in tit_conf_vert and verts and tit_mayoria_vert[k] not in verts:
                conflicto = "vertical"
            if k in tit_conf_forma and len(formas_d) == 1 and tit_mayoria_forma[k] not in formas_d:
                conflicto = (conflicto + ";forma").strip(";")
        d["conflicto_intra_titulo"] = conflicto
        if d["_cat_ok"]:
            evid, ver, det, nivel = veredicto_fila(nodos, ext, inte)
            A["formato"].add(d["cat_formato"] or "vacio", req)
            A["taxonomia"].add(d["cat_taxonomia"], req)
            A["valor"].add(v, req)
            A["evidencia"].add(evid, req)
            A["veredicto"].add(f"{evid}|{ver}", req)
            A["veredicto_total"].add(ver, req)
            if origen:
                A[f"origen|{origen}"].add(f"{evid}|{ver}", req)
            if pais in paises:
                A[f"pais|{pais}"].add(f"{evid}|{ver}", req)
            if pub in pub_top:
                A[f"pub|{pub}"].add(f"{evid}|{ver}", req)
            if ver == "contradice":
                tipo_c = det.split(":")[0]
                A["contradice_tipo"].add(f"{evid}|{tipo_c}", req)
                if evid == "externa":
                    A["contradice_genero_vs"].add(gv, req)
                esperado = ""
                if ext:
                    esperado = (ext["forma"] or "?") + "/" + ",".join(sorted(ext["generos"])[:3])
                elif inte:
                    esperado = "genero:" + ",".join(sorted(inte["generos"] | ({inte["vertical"]} if inte["vertical"] else set())))
                contra_pares.add(f"{v} -> {esperado}", req)
                if k:
                    contra_titulos.add(k, req)
                    contra_ejemplo.setdefault(k, {"titulo": d.get("contentTitle"), "declarado": v,
                                                  "esperado": esperado, "imdb": imdb.get("id", ""),
                                                  "imdb_titulo": imdb.get("titulo", ""),
                                                  "genero_declarado": d.get("contentGenre", ""),
                                                  "genero_vs_imdb": gv, "evidencia": evid,
                                                  "detalle": det, "publisher": pub})
                muestra_contra.append(d)
            if conflicto:
                A["conflicto_intra"].add(conflicto, req)
            if evid == "externa":
                A["ext_confianza"].add(ext["confianza"], req)
        else:
            evid, ver, det, nivel = "", "", "", 0
        d["evidencia"], d["veredicto"], d["detalle"], d["nivel_actual"] = evid, ver, det, nivel

        # ---- completitud --------------------------------------------------------------
        # vertical: entretenimiento salvo que una vertical fuerte este respaldada (por la
        # evidencia externa Y el genero declarado, o por el unico que hable)
        vertical, forma, gens, sub, forma_org, pev = "entretenimiento", None, [], None, "", "ninguna"
        fuerte_ext = next((x for x in ("deportes", "noticias", "musica") if ext and x in ext["verticales"]), None)
        fuerte_int = inte["vertical"] if inte["vertical"] in VERT_FUERTES | {"viajes", "gastronomia", "religion", "educacion"} else None
        if ext:
            pev = "externa"
            gens = [g for g in (IMDB_GENERO.get(x) for x in imdb.get("generos", [])) if g] + \
                   [g for g in sorted(ext["generos"]) if g]
            gens = list(dict.fromkeys(g for g in gens if g not in ("deportes", "noticias", "musica")))
            if fuerte_ext and (fuerte_ext == fuerte_int or not gnorm or not ext["es_ficcion"] and not fuerte_int and not gens):
                vertical = fuerte_ext
            elif fuerte_int and not ext["es_ficcion"]:
                vertical = fuerte_int
        elif inte["vertical"] or inte["generos"]:
            pev = "interna"
            gens = sorted(inte["generos"])
            if fuerte_int:
                vertical = fuerte_int
        if vertical == "deportes":
            sub = inte.get("sub") or sub_deporte_de_texto(d.get("contentTitle", "") if k else "")
            for x in nodos:
                if x["sub"] and not sub:
                    sub = x["sub"]
        # forma: IMDb > contentSeries real > declarado > genero
        if forma_tit:
            forma, forma_org = forma_tit, "titulo"
        elif ext and ext["forma"]:
            forma, forma_org = ext["forma"], "imdb"
        elif es_util("contentSeries", d.get("contentSeries", "")) and \
                (d.get("contentSeries") or "").strip().lower() not in SERIES_PLACEHOLDER:
            forma, forma_org = "tv", "contentSeries"
            if pev == "ninguna":
                pev = "serie"
        else:
            formas_decl = {x["forma"] for x in nodos if x["forma"]}
            if len(formas_decl) == 1 and d["_cat_ok"] and ver != "contradice":
                forma, forma_org = next(iter(formas_decl)), "declarado"
            elif inte["forma"]:
                forma, forma_org = inte["forma"], "genero"
        c22, c10, nivel_p = tax.proponer(vertical, forma, gens, sub)
        if vertical == "entretenimiento" and forma is None and not gens:
            nivel_p = 1 if (ext or gnorm) else 0
        # si lo declarado ya es igual o mas fino y no esta contradicho, se mantiene
        mantiene = d["_cat_ok"] and ver != "contradice" and nivel_p <= nivel
        if mantiene:
            c22, c10, nivel_p = [], [], nivel
        gan = nivel_p - nivel if d["_cat_ok"] else nivel_p
        d["prop_iab22"] = "[" + ", ".join(c22) + "]" if c22 else ""
        d["prop_iab22_nombres"] = " | ".join(" > ".join((tax.t22.get(c) or tax.t30.get(c))["ruta"]) for c in c22)
        d["prop_iab10"] = "[" + ", ".join(c10) + "]" if c10 else ""
        d["nivel_propuesto"] = nivel_p
        d["ganancia"] = gan
        d["prop_forma_origen"] = forma_org
        d["prop_evidencia"] = pev

        estado = "vacia" if not d["_cat_ok"] else ("contradicha" if ver == "contradice" else "llena")
        A["comp_estado"].add(estado, req)
        A["comp_matriz"].add(f"{estado}|{nivel}->{nivel_p}", req)
        A["comp_nivel_actual"].add(f"{estado}|{nivel}", req)
        A["comp_nivel_prop"].add(str(nivel_p), req)
        A["comp_evidencia"].add(pev, req)
        A["comp_forma_origen"].add(forma_org or "sin_forma", req)
        if not d["_cat_ok"]:
            mejora = "rellena" if nivel_p > 0 else "sin_propuesta"
        elif estado == "contradicha":
            mejora = "corrige" if nivel_p > 0 else "contradicha_sin_propuesta"
        elif mantiene:
            mejora = "mantiene"
        else:
            mejora = "sube"
        A["comp_mejora"].add(mejora, req)
        if pais in paises:
            A[f"comp_pais|{pais}"].add(mejora, req)
        if pub in pub_top:
            A[f"comp_pub|{pub}"].add(mejora, req)
        if origen:
            A[f"comp_origen|{origen}"].add(mejora, req)
        if c22:
            prop_top.add(d["prop_iab22_nombres"], req)
            reglas.add(f"{pev}|{vertical}|{forma or '-'}|{forma_org or '-'}", req)
        if random.random() < 0.002:
            muestra_prop.append(d)
        w.writerow(d)

    # ---- agregados ------------------------------------------------------------------------
    llenas = sum(1 for d in filas if d["_cat_ok"])
    llenas_req = sum(d["_req"] for d in filas if d["_cat_ok"])
    con_titulo = sum(1 for d in filas if d["_k"])
    con_ext = sum(1 for d in filas if d["_k"] and cache.get(d["_k"], {}).get("imdb")
                  and cache[d["_k"]]["imdb"].get("confianza") in conf_ok)

    def bloque(prefijo, keys, tot_f, tot_r):
        out = {}
        for kk in keys:
            a = A.get(f"{prefijo}|{kk}")
            if a:
                tf = sum(a.f.values()); tr = sum(a.r.values())
                out[kk] = {"filas": tf, "requests": tr, "desglose": a.dump(tf, tr)}
        return out

    res = {
        "meta": {"archivo": args.entrada, "nombre": args.nombre or os.path.basename(args.entrada),
                 "columna": col_cat, "filas": n, "requests": tot_req,
                 "filas_con_categoria": llenas, "pct_filas_con_categoria": pct(llenas, n),
                 "requests_con_categoria": llenas_req, "pct_requests_con_categoria": pct(llenas_req, tot_req),
                 "filas_con_titulo_real": con_titulo, "filas_con_match_externo": con_ext,
                 "pct_filas_con_match_externo": pct(con_ext, n),
                 "titulos_distintos": len({d["_k"] for d in filas if d["_k"]}),
                 "titulos_en_cache": len(cache), "confianza_min": args.confianza_min,
                 "taxonomias": {v: {"1.0": len(tax.t10), "2.2": len(tax.t22), "3.0": len(tax.t30)}[v]
                                for v in ("1.0", "2.2", "3.0")},
                 "fecha": inicio.strftime("%Y-%m-%d %H:%M"),
                 "paises": paises, "publishers_top": pub_top},
        "correctitud": {
            "formato": A["formato"].dump(llenas, llenas_req),
            "taxonomia": A["taxonomia"].dump(llenas, llenas_req),
            "valores_top": A["valor"].dump(llenas, llenas_req, 40),
            "evidencia": A["evidencia"].dump(llenas, llenas_req),
            "veredicto_total": A["veredicto_total"].dump(llenas, llenas_req),
            "veredicto": A["veredicto"].dump(llenas, llenas_req),
            "contradice_tipo": A["contradice_tipo"].dump(llenas, llenas_req),
            "contradice_externa_por_genero_vs_imdb": A["contradice_genero_vs"].dump(),
            "ext_confianza": A["ext_confianza"].dump(),
            "conflicto_intra_titulo": {
                "titulos_con_categoria": len(tit_vert),
                "titulos_conflicto_vertical": len(tit_conf_vert),
                "titulos_conflicto_forma": len(tit_conf_forma),
                "filas_en_titulos_con_conflicto": {
                    "vertical": sum(tit_vert[k][v] for k in tit_conf_vert for v in tit_vert[k]),
                    "forma": sum(tit_forma[k][v] for k in tit_conf_forma for v in tit_forma[k])},
                "filas_minoritarias": A["conflicto_intra"].dump(llenas, llenas_req),
                "ejemplos_vertical": {k: dict(tit_vert[k]) for k in
                                      sorted(tit_conf_vert, key=lambda x: -sum(tit_vert[x].values()))[:15]},
                "ejemplos_forma": {k: dict(tit_forma[k]) for k in
                                   sorted(tit_conf_forma, key=lambda x: -sum(tit_forma[x].values()))[:15]}},
            "por_pais": bloque("pais", paises, llenas, llenas_req),
            "por_publisher": bloque("pub", pub_top, llenas, llenas_req),
            "por_origen": bloque("origen", sorted({d.get(col_origen, "") for d in filas} - {""}) if col_origen else [], llenas, llenas_req),
            "contradicciones_top_titulos": [dict(contra_ejemplo[k], filas=contra_titulos.f[k], requests=contra_titulos.r[k])
                                            for k, _ in contra_titulos.r.most_common(40)],
            "contradicciones_top_pares": contra_pares.dump(None, None, 40),
            "genero_vs_imdb": {"total": genero_vs.dump(sum(genero_vs.f.values()), sum(genero_vs.r.values())),
                               "por_publisher": {p: genero_vs_pub[p].dump(sum(genero_vs_pub[p].f.values()), sum(genero_vs_pub[p].r.values()))
                                                 for p in pub_top if p in genero_vs_pub}},
        },
        "completitud": {
            "estado": A["comp_estado"].dump(n, tot_req),
            "nivel_actual": A["comp_nivel_actual"].dump(n, tot_req),
            "nivel_propuesto": A["comp_nivel_prop"].dump(n, tot_req),
            "matriz": A["comp_matriz"].dump(n, tot_req),
            "mejora": A["comp_mejora"].dump(n, tot_req),
            "evidencia": A["comp_evidencia"].dump(n, tot_req),
            "forma_origen": A["comp_forma_origen"].dump(n, tot_req),
            "por_pais": {p: A[f"comp_pais|{p}"].dump(sum(A[f"comp_pais|{p}"].f.values()), sum(A[f"comp_pais|{p}"].r.values()))
                         for p in paises if f"comp_pais|{p}" in A},
            "por_publisher": {p: A[f"comp_pub|{p}"].dump(sum(A[f"comp_pub|{p}"].f.values()), sum(A[f"comp_pub|{p}"].r.values()))
                              for p in pub_top if f"comp_pub|{p}" in A},
            "por_origen": {o: A[f"comp_origen|{o}"].dump(sum(A[f"comp_origen|{o}"].f.values()), sum(A[f"comp_origen|{o}"].r.values()))
                           for o in sorted(k.split("|", 1)[1] for k in A if k.startswith("comp_origen|"))},
            "propuestas_top": prop_top.dump(n, tot_req, 40),
            "reglas": reglas.dump(n, tot_req, 40),
        },
    }
    json.dump(res, open(args.prefijo_salida + ".json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # ---- muestras para revision manual ----------------------------------------------------
    cols_m = [c for c in ("Publisher", "Country", "contentTitle", "contentGenre", col_cat, "cat_nombres",
                          "evidencia", "veredicto", "detalle", "ext_imdb_id", "ext_tipo", "ext_generos",
                          "ext_confianza", "genero_vs_imdb", "conflicto_intra_titulo", "Total Requests",
                          "prop_iab22", "prop_iab22_nombres", "prop_iab10", "nivel_actual",
                          "nivel_propuesto", "prop_evidencia", "prop_forma_origen") if c in salida_cols]
    muestra_contra.sort(key=lambda d: -d["_req"])
    vistos, sel = set(), []
    for d in muestra_contra:              # un ejemplo por titulo, los de mas trafico primero
        key = d["_k"] or d.get("contentTitle")
        if key in vistos:
            continue
        vistos.add(key)
        sel.append(d)
        if len(sel) >= args.muestra:
            break
    for nombre, lista in (("contradicciones", sel), ("propuestas", muestra_prop[:args.muestra])):
        with open(f"{args.prefijo_salida}-muestra-{nombre}.csv", "w", encoding="utf-8", newline="") as f:
            wm = csv.DictWriter(f, fieldnames=cols_m, extrasaction="ignore")
            wm.writeheader()
            for d in lista:
                wm.writerow(d)

    # ---- resumen en consola -----------------------------------------------------------------
    c = res["correctitud"]
    print(f"\n[{res['meta']['nombre']}] {n:,} filas; con categoria {llenas:,} ({pct(llenas, n)}%); "
          f"con match externo {con_ext:,} ({pct(con_ext, n)}%)")
    print("veredicto (filas con categoria):")
    for k_, v_ in c["veredicto"].items():
        print(f"  {k_:26} {v_['filas']:8,} {v_['pct_filas']:6.2f}%  req {v_['pct_requests']:6.2f}%")
    print("completitud (mejora, todas las filas):")
    for k_, v_ in res["completitud"]["mejora"].items():
        print(f"  {k_:26} {v_['filas']:8,} {v_['pct_filas']:6.2f}%  req {v_['pct_requests']:6.2f}%")
    print(f"listo en {(datetime.now() - inicio).seconds}s", file=sys.stderr)


if __name__ == "__main__":
    main()
