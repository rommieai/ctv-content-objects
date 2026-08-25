# -*- coding: utf-8 -*-
"""Normalizacion de contentGenre y auditoria de calidad de contentTitle, por pais.

Parte 1 (genero): aplica la misma normalizacion de normalizar_monetizar.py
(split por comas + diccionario de sinonimos -> generos canonicos) pero desglosada
por pais: % de filas y de requests de cada genero, eCPM ponderado (>0) y tasa de
monetizacion.

Parte 2 (titulo): dentro del fill "util" de contentTitle (que ya excluye centinelas),
clasifica los valores que NO corresponden a un titulo de contenido segun la practica
esperada por OpenRTB 2.6 (content.title = titulo del contenido, ej. "A New Hope"):

  - macro_sin_reemplazar : contiene {{ o }}          (ej. {{content_title}})
  - hash                 : 32 hex                     (titulo ofuscado)
  - placeholder          : valores de plataforma      (roku, epg, vod, live...)
  - canal_no_programa    : nombre de canal/feed lineal, no del programa
                           (las estrellas, canal 5, golden, red bull tv...)
  - slug_tecnico         : identificador con guion bajo (sponge_bob_bounce)
  - encoding_roto        : contiene el caracter U+FFFD (mojibake)
  - sin_letras           : solo digitos/simbolos
  - muy_corto            : 1-2 caracteres

Lo que no cae en ninguna categoria se considera "titulo aparentemente valido" y
define el fill efectivo.

Uso:
    python analizar_genero_titulo_paises.py entrada.csv salida.json [--paises "Mexico,Colombia,Chile"]
"""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict

SENT = {"not available", "not applicable", "unknown", "n/a", "null", "undefined",
        "none", "-", ""}

# --- normalizacion de genero (mismo diccionario de normalizar_monetizar.py) ---
GENRE_MAP = {
 "drama": "drama", "dramas": "drama", "melodrama": "drama",
 "comedy": "comedia", "comedia": "comedia", "sitcom": "comedia",
 "stand-up": "comedia", "standup": "comedia", "stand up": "comedia", "humor": "comedia",
 "romance": "romance", "romantic": "romance", "romantico": "romance",
 "romantic comedy": "romance",
 "horror": "terror", "terror": "terror",
 "thriller": "thriller", "suspense": "thriller", "suspenso": "thriller",
 "mystery": "misterio", "misterio": "misterio",
 "action": "accion", "accion": "accion", "acción": "accion", "martial arts": "accion",
 "adventure": "aventura", "aventura": "aventura",
 "crime": "crimen", "crimen": "crimen", "true crime": "crimen", "police": "crimen",
 "western": "western", "westerns": "western",
 "sci-fi": "sci-fi", "scifi": "sci-fi", "sci fi": "sci-fi",
 "science fiction": "sci-fi", "science-fiction": "sci-fi", "ciencia ficcion": "sci-fi",
 "fantasy": "fantasia", "fantasia": "fantasia", "fantasía": "fantasia",
 "documentary": "documental", "documentaries": "documental", "documental": "documental",
 "docu": "documental", "docuseries": "documental", "biography": "documental",
 "biografia": "documental", "history": "documental", "historia": "documental",
 "nature": "documental", "wildlife": "documental", "science": "documental",
 "ciencia": "documental",
 "news": "noticias", "noticias": "noticias", "local news": "noticias",
 "world news": "noticias",
 "sports": "deportes", "sport": "deportes", "deportes": "deportes",
 "futbol": "deportes", "soccer": "deportes", "football": "deportes",
 "wrestling": "deportes", "boxing": "deportes", "motorsport": "deportes",
 "esports": "deportes",
 "music": "musica", "musica": "musica", "música": "musica", "musical": "musica",
 "concert": "musica",
 "kids": "infantil-familia", "children": "infantil-familia", "child": "infantil-familia",
 "family": "infantil-familia", "familia": "infantil-familia",
 "infantil": "infantil-familia", "preschool": "infantil-familia",
 "animation": "animacion", "animacion": "animacion", "animación": "animacion",
 "cartoon": "animacion", "cartoons": "animacion",
 "anime": "anime",
 "reality": "reality", "reality tv": "reality", "reality-tv": "reality",
 "telenovela": "telenovela", "novela": "telenovela", "novelas": "telenovela",
 "soap": "telenovela", "soap opera": "telenovela", "soaps": "telenovela",
 "faith": "religion", "religion": "religion", "religious": "religion",
 "espiritual": "religion", "spiritual": "religion",
 "lifestyle": "lifestyle", "estilo de vida": "lifestyle", "fashion": "lifestyle",
 "home & garden": "lifestyle", "health": "lifestyle", "fitness": "lifestyle",
 "wellness": "lifestyle",
 "food": "gastronomia", "cooking": "gastronomia", "cocina": "gastronomia",
 "culinary": "gastronomia",
 "travel": "viajes", "viajes": "viajes",
 "game show": "concursos", "gameshow": "concursos", "game-show": "concursos",
 "concurso": "concursos", "quiz": "concursos",
 "talk": "talk show", "talk show": "talk show", "talk-show": "talk show",
 "talkshow": "talk show",
 "education": "educacion", "educational": "educacion", "educacion": "educacion",
 "educación": "educacion", "learning": "educacion",
 "entertainment": "entretenimiento (generico)", "variety": "entretenimiento (generico)",
 "general entertainment": "entretenimiento (generico)",
 "variety show": "entretenimiento (generico)",
 "movies": "pelicula (generico)", "movie": "pelicula (generico)",
 "film": "pelicula (generico)", "films": "pelicula (generico)",
 "cine": "pelicula (generico)", "cinema": "pelicula (generico)",
 "series": "tv/series (generico)", "tv": "tv/series (generico)",
 "television": "tv/series (generico)", "tv shows": "tv/series (generico)",
 "shows": "tv/series (generico)", "special": "tv/series (generico)",
 "specials": "tv/series (generico)",
 "other": "otros/desconocido", "otros": "otros/desconocido",
 "others": "otros/desconocido", "general": "otros/desconocido",
 "misc": "otros/desconocido", "miscellaneous": "otros/desconocido",
 "unknown": "otros/desconocido",
 "war": "belico", "guerra": "belico", "military": "belico",
 "gaming": "videojuegos", "games": "videojuegos", "video games": "videojuegos",
 "gameplay": "videojuegos",
}


def norm_genre(raw):
    """Devuelve (generos canonicos, hubo_algun_token, tokens_no_mapeados)."""
    s = raw.strip().lower()
    if s in SENT:
        return [], False, []
    toks = [t.strip() for t in s.replace("/", ",").replace("&", ",").replace(";", ",").split(",")]
    out = []
    no_map = []
    algun_token = False
    for t in toks:
        if not t or t in SENT:
            continue
        algun_token = True
        g = GENRE_MAP.get(t)
        if g is None:
            no_map.append(t)
        elif g not in out:
            out.append(g)
    return out, algun_token, no_map


# --- auditoria de contentGenre: valores que no son un genero ---
TIPO_CONTENIDO = {"short", "shorts", "feature film", "tv series", "tvshows", "tv shows",
                  "videos", "video", "classic tv", "movies & tv", "movies and tv",
                  "live", "live tv", "episode", "episodes", "clip", "clips",
                  "trailer", "trailers", "web series", "full episodes"}
IDIOMA_REGION = {"en español", "en espanol", "spanish", "english", "international",
                 "world", "foreign", "latino", "latin", "hindi", "korean", "japanese",
                 "global news"}
TEMA_NO_GENERO = {"culture", "relaxing", "opinion", "technology", "business", "finance",
                  "arts", "outdoors", "review", "technology & computing",
                  "home entertaining", "consumer electronics", "shopping", "weather"}
GENERO_BASE = ["drama", "comed", "roman", "crime", "horror", "terror", "thriller",
               "action", "accion", "western", "myster", "adventur", "fantas", "sci",
               "documenta", "noir", "suspense", "animat", "anime", "sport", "music",
               "news", "kids", "family", "novela"]
CATEGORIAS_GENERO = ["prefijo_tecnico", "genero_en_formato_sucio", "tipo_de_contenido",
                     "idioma_o_region", "tema_no_genero", "otros_no_reconocidos"]


def clasificar_genero_no_mapeado(tokens):
    """Clasifica una fila cuyo genero no mapeo a nada canonico."""
    for t in tokens:
        if t.startswith("genre_"):
            return "prefijo_tecnico"
    for t in tokens:
        if any(b in t for b in GENERO_BASE):
            return "genero_en_formato_sucio"
    for t in tokens:
        if t in TIPO_CONTENIDO:
            return "tipo_de_contenido"
    for t in tokens:
        if t in IDIOMA_REGION:
            return "idioma_o_region"
    for t in tokens:
        if t in TEMA_NO_GENERO:
            return "tema_no_genero"
    return "otros_no_reconocidos"


# --- auditoria de contentTitle ---
RE_HEX32 = re.compile(r"^[0-9a-f]{32}$")
PLACEHOLDERS = {"roku", "epg", "vod", "live", "livestream", "test", "demo", "video",
                "movie", "movies", "pelicula", "series", "tv", "stream", "content",
                "untitled", "no title", "sin titulo", "run of video network", "default"}
CANALES = {"las estrellas", "canal 5", "golden", "golden multiplex", "azteca uno",
           "azteca 7", "adn 40", "foro tv", "distrito comedia", "tlnovelas",
           "de pelicula", "de película", "bandamax", "red bull tv", "local news",
           "asian drama", "canal once", "canal de las estrellas"}
CATEGORIAS_TITULO = ["macro_sin_reemplazar", "hash", "placeholder", "canal_no_programa",
                     "slug_tecnico", "encoding_roto", "sin_letras", "muy_corto"]


def clasificar_titulo(v):
    """Devuelve la categoria de sospecha, o None si parece un titulo valido."""
    s = v.strip()
    low = s.lower()
    if "{{" in s or "}}" in s:
        return "macro_sin_reemplazar"
    if RE_HEX32.match(low):
        return "hash"
    if low in PLACEHOLDERS:
        return "placeholder"
    if low in CANALES:
        return "canal_no_programa"
    if "_" in s:
        return "slug_tecnico"
    if "�" in s:
        return "encoding_roto"
    if not any(ch.isalpha() for ch in s):
        return "sin_letras"
    if len(s) <= 2:
        return "muy_corto"
    return None


def pct(n, d):
    return round(100.0 * n / d, 2) if d else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida_json")
    ap.add_argument("--paises", default="Mexico,Colombia,Chile")
    args = ap.parse_args()
    paises = [p.strip() for p in args.paises.split(",") if p.strip()]

    G = {p: {"filas": 0, "req": 0,
             "gen_filas": Counter(), "gen_req": Counter(),
             "gen_ewsum": defaultdict(float), "gen_ewreq": defaultdict(int),
             "gen_sin_dato": 0, "gen_no_mapeado": 0, "gen_multi": 0,
             "gen_util_filas": 0, "gen_util_req": 0,
             "gen_parcial_filas": 0, "gen_parcial_req": 0,
             "gen_cat_filas": Counter(), "gen_cat_req": Counter(),
             "gen_cat_ejemplos": defaultdict(Counter),
             "tit_filas_util": 0, "tit_req_util": 0,
             "tit_cat_filas": Counter(), "tit_cat_req": Counter(),
             "tit_ejemplos": defaultdict(Counter)}
         for p in paises}

    with open(args.entrada, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        cols = next(r)
        idx = {c: i for i, c in enumerate(cols)}
        for row in r:
            if len(row) != len(cols):
                continue
            pais = row[idx["Country"]].strip()
            if pais not in G:
                continue
            g = G[pais]
            try:
                req = int(row[idx["Total Requests"]])
            except ValueError:
                req = 0
            try:
                e = float(row[idx["eCPM"]])
            except ValueError:
                e = None
            g["filas"] += 1
            g["req"] += req

            generos, tenia_algo, no_map = norm_genre(row[idx["contentGenre"]])
            if not tenia_algo:
                g["gen_sin_dato"] += 1
            else:
                g["gen_util_filas"] += 1
                g["gen_util_req"] += req
                if not generos:
                    g["gen_no_mapeado"] += 1
                    cat = clasificar_genero_no_mapeado(no_map)
                    g["gen_cat_filas"][cat] += 1
                    g["gen_cat_req"][cat] += req
                    g["gen_cat_ejemplos"][cat][row[idx["contentGenre"]].strip()[:40]] += 1
                elif no_map:
                    g["gen_parcial_filas"] += 1
                    g["gen_parcial_req"] += req
            if len(generos) > 1:
                g["gen_multi"] += 1
            for gen in generos:
                g["gen_filas"][gen] += 1
                g["gen_req"][gen] += req
                if e is not None and e > 0:
                    g["gen_ewsum"][gen] += e * req
                    g["gen_ewreq"][gen] += req

            titulo = row[idx["contentTitle"]].strip()
            if titulo.lower() not in SENT:
                g["tit_filas_util"] += 1
                g["tit_req_util"] += req
                cat = clasificar_titulo(titulo)
                if cat:
                    g["tit_cat_filas"][cat] += 1
                    g["tit_cat_req"][cat] += req
                    g["tit_ejemplos"][cat][titulo[:40]] += 1

    res = {"archivo": args.entrada.split("\\")[-1], "paises": {}}
    for p in paises:
        g = G[p]
        generos = [{"genero": k, "filas": g["gen_filas"][k],
                    "pct_filas": pct(g["gen_filas"][k], g["filas"]),
                    "requests": g["gen_req"][k],
                    "pct_requests": pct(g["gen_req"][k], g["req"]),
                    "ecpm_ponderado_no_cero": round(g["gen_ewsum"][k] / g["gen_ewreq"][k], 3)
                        if g["gen_ewreq"][k] else None,
                    "pct_req_monetizado": pct(g["gen_ewreq"][k], g["gen_req"][k])}
                   for k in sorted(g["gen_filas"], key=lambda x: -g["gen_req"][x])]
        sosp_filas = sum(g["tit_cat_filas"].values())
        sosp_req = sum(g["tit_cat_req"].values())
        res["paises"][p] = {
            "filas": g["filas"], "requests": g["req"],
            "genero": {
                "filas_sin_dato": g["gen_sin_dato"],
                "filas_con_genero_no_mapeado": g["gen_no_mapeado"],
                "filas_multigenero": g["gen_multi"],
                "pct_filas_con_genero_canonico": pct(
                    g["filas"] - g["gen_sin_dato"] - g["gen_no_mapeado"], g["filas"]),
                "distribucion": generos,
                "auditoria": {
                    "fill_util_pct_filas": pct(g["gen_util_filas"], g["filas"]),
                    "fill_util_pct_requests": pct(g["gen_util_req"], g["req"]),
                    "mapeado_parcial_filas": g["gen_parcial_filas"],
                    "mapeado_parcial_pct_filas": pct(g["gen_parcial_filas"], g["filas"]),
                    "sin_sentido": {
                        cat: {"filas": g["gen_cat_filas"][cat],
                              "pct_filas_pais": pct(g["gen_cat_filas"][cat], g["filas"]),
                              "pct_requests_pais": pct(g["gen_cat_req"][cat], g["req"]),
                              "ejemplos_top": g["gen_cat_ejemplos"][cat].most_common(5)}
                        for cat in CATEGORIAS_GENERO if g["gen_cat_filas"][cat]},
                    "total_sin_sentido_filas": g["gen_no_mapeado"],
                    "total_sin_sentido_pct_filas": pct(g["gen_no_mapeado"], g["filas"]),
                    "total_sin_sentido_pct_requests": pct(
                        sum(g["gen_cat_req"].values()), g["req"]),
                    "fill_efectivo_pct_filas": pct(
                        g["gen_util_filas"] - g["gen_no_mapeado"], g["filas"]),
                    "fill_efectivo_pct_requests": pct(
                        g["gen_util_req"] - sum(g["gen_cat_req"].values()), g["req"]),
                },
            },
            "titulo": {
                "fill_util_filas": g["tit_filas_util"],
                "fill_util_pct_filas": pct(g["tit_filas_util"], g["filas"]),
                "fill_util_pct_requests": pct(g["tit_req_util"], g["req"]),
                "sospechosos": {
                    cat: {"filas": g["tit_cat_filas"][cat],
                          "pct_filas_pais": pct(g["tit_cat_filas"][cat], g["filas"]),
                          "pct_del_fill_filas": pct(g["tit_cat_filas"][cat], g["tit_filas_util"]),
                          "requests": g["tit_cat_req"][cat],
                          "pct_requests_pais": pct(g["tit_cat_req"][cat], g["req"]),
                          "ejemplos_top": g["tit_ejemplos"][cat].most_common(5)}
                    for cat in CATEGORIAS_TITULO if g["tit_cat_filas"][cat]},
                "total_sospechosos_filas": sosp_filas,
                "total_sospechosos_requests": sosp_req,
                "fill_efectivo_filas": g["tit_filas_util"] - sosp_filas,
                "fill_efectivo_pct_filas": pct(g["tit_filas_util"] - sosp_filas, g["filas"]),
                "fill_efectivo_pct_requests": pct(g["tit_req_util"] - sosp_req, g["req"]),
            },
        }

    with open(args.salida_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)

    for p in paises:
        t = res["paises"][p]["titulo"]
        print(f"== {p}: titulo fill util {t['fill_util_pct_filas']}% filas / "
              f"{t['fill_util_pct_requests']}% reqs -> efectivo "
              f"{t['fill_efectivo_pct_filas']}% filas / {t['fill_efectivo_pct_requests']}% reqs")
        for cat, d in t["sospechosos"].items():
            print(f"   {cat:22s} filas={d['filas']:6d} ({d['pct_filas_pais']}% pais) "
                  f"reqs={d['pct_requests_pais']}% pais | ej: "
                  + "; ".join(v for v, _ in d["ejemplos_top"][:3]))
    print(f"-> {args.salida_json}")


if __name__ == "__main__":
    main()
