# -*- coding: utf-8 -*-
"""Normaliza contentGenre (a ~34 generos canonicos) y contentRating (a 7 franjas de edad)
y analiza el inventario monetizado (filas con eCPM > 0).

Escribe un CSV enriquecido con dos columnas nuevas (genero_normalizado, rating_franja)
y un JSON con: distribucion por genero y franja (con eCPM ponderado y tasa de
monetizacion), y el desglose del trafico monetizado por pais, publisher, bundle,
idioma, livestream, presencia de titulo y riqueza de metadata.

Uso:
    python normalizar_monetizar.py entrada.csv salida_enriquecida.csv salida.json
"""
import csv
import json
import sys
from collections import Counter, defaultdict

if len(sys.argv) != 4:
    print(__doc__)
    sys.exit(1)
SRC, OUT_CSV, OUT_JSON = sys.argv[1], sys.argv[2], sys.argv[3]

SENT = {"not available", "not applicable", "unknown", "n/a", "null", "undefined",
        "none", "-", ""}
EMPTY_MD5 = "d41d8cd98f00b204e9800998ecf8427e"

# ---------- normalizacion de genero ----------
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
 "entertainment": "entretenimiento", "variety": "entretenimiento",
 "general entertainment": "entretenimiento",
 "variety show": "entretenimiento",
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
    """Devuelve (lista de generos canonicos, lista de tokens no mapeados)."""
    s = raw.strip().lower()
    if s in SENT:
        return [], []
    toks = [t.strip() for t in s.replace("/", ",").replace("&", ",").replace(";", ",").split(",")]
    out, unmapped = [], []
    for t in toks:
        if not t or t in SENT:
            continue
        g = GENRE_MAP.get(t)
        if g is None:
            unmapped.append(t)
        elif g not in out:
            out.append(g)
    return out, unmapped


# ---------- normalizacion de rating ----------
TIER_ORDER = ["todos", "7+", "10+", "13-15", "16-17", "18+ / adulto",
              "sin clasificar", "sin dato", "no mapeado"]
RATING_MAP = {}
for v in ["g", "tv-g", "tvg", "tv-y", "tvy", "a", "aa", "l", "0", "all", "todos",
          "libre", "atp", "e", "tv-g7"]:
    RATING_MAP[v] = "todos"
for v in ["tv-y7", "tv-y7-fv", "tvy7", "6", "7", "7+", "6+"]:
    RATING_MAP[v] = "7+"
for v in ["pg", "tv-pg", "tvpg", "10", "10+", "tvpg_tv_pg", "tv-pg-d", "tv-pg-l",
          "tv-pg-v", "tv-pg-s"]:
    RATING_MAP[v] = "10+"
for v in ["pg-13", "pg13", "12", "12+", "13", "13+", "14", "14+", "tv-14", "tv14",
          "tvpg_tv_14", "b", "15", "15+", "b-15", "b15", "sm14"]:
    RATING_MAP[v] = "13-15"
for v in ["16", "16+", "r", "m", "ma-15", "tvpg_tv_r"]:
    RATING_MAP[v] = "16-17"
for v in ["tv-ma", "tvma", "tvpg_tv_ma", "nc-17", "nc17", "18", "18+", "x", "adult",
          "adults only", "c", "d", "ao"]:
    RATING_MAP[v] = "18+ / adulto"
for v in ["nr", "not rated", "not-rated", "unrated", "banned", "no rating",
          "sin clasificar"]:
    RATING_MAP[v] = "sin clasificar"


def norm_rating(raw):
    s = raw.strip().lower()
    if s in SENT:
        return "sin dato"
    return RATING_MAP.get(s, "no mapeado")


# ---------- recorrido ----------
CONTENT = ["contentGenre", "contentCategory", "contentSeries", "contentLength",
           "contentLanguage", "contentIsLiveStream", "contentTitle", "contentRating"]


def field_filled(c, v):
    v = v.strip()
    if v.lower() in SENT:
        return False
    if c == "contentSeries" and v == EMPTY_MD5:
        return False
    if c == "contentCategory" and v in ("[-7]", "[]", "[-1]"):
        return False
    return True


rows = 0
total_req = 0
genre_rows = Counter(); genre_req = Counter()
genre_e_wsum = defaultdict(float); genre_e_wreq = defaultdict(int)
unmapped_tok = Counter(); rows_multi = 0; rows_all_unmapped = 0; rows_genre_sin_dato = 0
tier_rows = Counter(); tier_req = Counter()
tier_e_wsum = defaultdict(float); tier_e_wreq = defaultdict(int)
nomap_rating = Counter()

nz_rows = 0; nz_req = 0
pub_nz = defaultdict(lambda: [0, 0, 0.0, 0, 0])   # [filas_nz, req_nz, e*req, filas, req]
cty_nz = defaultdict(lambda: [0, 0, 0.0, 0, 0])
app_nz = defaultdict(lambda: [0, 0, 0.0])
lang_nz = defaultdict(lambda: [0, 0, 0.0])
live_nz = defaultdict(lambda: [0, 0, 0.0])
title_nz = defaultdict(lambda: [0, 0, 0.0])
rich_nz = defaultdict(lambda: [0, 0, 0.0])
top_rows = []

out = open(OUT_CSV, "w", newline="", encoding="utf-8-sig")
w = csv.writer(out)

with open(SRC, newline="", encoding="utf-8-sig") as f:
    r = csv.reader(f)
    cols = next(r)
    idx = {c: i for i, c in enumerate(cols)}
    w.writerow(cols + ["genero_normalizado", "rating_franja"])
    for row in r:
        if len(row) != len(cols):
            continue
        rows += 1
        try:
            req = int(row[idx["Total Requests"]])
        except ValueError:
            req = 0
        try:
            e = float(row[idx["eCPM"]])
        except ValueError:
            e = None
        total_req += req

        gl, unm = norm_genre(row[idx["contentGenre"]])
        for t in unm:
            unmapped_tok[t] += 1
        raw_g = row[idx["contentGenre"]].strip().lower()
        if raw_g in SENT:
            rows_genre_sin_dato += 1
        elif not gl:
            rows_all_unmapped += 1
        if len(gl) > 1:
            rows_multi += 1
        tier = norm_rating(row[idx["contentRating"]])
        if tier == "no mapeado":
            nomap_rating[row[idx["contentRating"]].strip().lower()] += 1
        w.writerow(row + [";".join(gl), tier])

        for g in gl:
            genre_rows[g] += 1; genre_req[g] += req
            if e is not None and e > 0:
                genre_e_wsum[g] += e * req; genre_e_wreq[g] += req
        tier_rows[tier] += 1; tier_req[tier] += req
        if e is not None and e > 0:
            tier_e_wsum[tier] += e * req; tier_e_wreq[tier] += req

        pub = row[idx["Publisher"]]; cty = row[idx["Country"]]
        pub_nz[pub][3] += 1; pub_nz[pub][4] += req
        cty_nz[cty][3] += 1; cty_nz[cty][4] += req
        if e is not None and e > 0:
            nz_rows += 1; nz_req += req
            pub_nz[pub][0] += 1; pub_nz[pub][1] += req; pub_nz[pub][2] += e * req
            cty_nz[cty][0] += 1; cty_nz[cty][1] += req; cty_nz[cty][2] += e * req
            b = row[idx["pageURL"]]
            app_nz[b][0] += 1; app_nz[b][1] += req; app_nz[b][2] += e * req
            lg = row[idx["contentLanguage"]].strip().lower()
            lg = lg if lg not in SENT else "(sin dato)"
            lang_nz[lg][0] += 1; lang_nz[lg][1] += req; lang_nz[lg][2] += e * req
            lv = "1 (live)" if row[idx["contentIsLiveStream"]].strip() == "1" else "(sin dato)"
            live_nz[lv][0] += 1; live_nz[lv][1] += req; live_nz[lv][2] += e * req
            tp = row[idx["contentIsTitlePresent"]].strip().lower()
            title_nz[tp][0] += 1; title_nz[tp][1] += req; title_nz[tp][2] += e * req
            n = sum(1 for c in CONTENT if field_filled(c, row[idx[c]]))
            rich_nz[n][0] += 1; rich_nz[n][1] += req; rich_nz[n][2] += e * req
            top_rows.append((e, req, pub, row[idx["App Name"]], cty,
                             row[idx["contentTitle"]][:60]))
out.close()
top_rows.sort(reverse=True)


def wavg(s, q):
    return round(s / q, 3) if q else None


def pct(n, d):
    return round(100.0 * n / d, 2) if d else 0.0


res = {
 "fuente": SRC.split("\\")[-1], "filas": rows, "requests": total_req,
 "genero": {
   "filas_multigenero": rows_multi,
   "filas_sin_dato": rows_genre_sin_dato,
   "filas_con_genero_pero_nada_mapeado": rows_all_unmapped,
   "tokens_no_mapeados_top": unmapped_tok.most_common(40),
   "tokens_no_mapeados_filas_total": sum(unmapped_tok.values()),
   "distribucion": [
     {"genero": g, "filas": genre_rows[g], "pct_filas": pct(genre_rows[g], rows),
      "requests": genre_req[g], "pct_requests": pct(genre_req[g], total_req),
      "ecpm_ponderado_no_cero": wavg(genre_e_wsum[g], genre_e_wreq[g]),
      "pct_req_monetizado": pct(genre_e_wreq[g], genre_req[g])}
     for g in sorted(genre_rows, key=lambda x: -genre_req[x])],
 },
 "rating": {
   "no_mapeados_top": nomap_rating.most_common(30),
   "distribucion": [
     {"franja": t, "filas": tier_rows[t], "pct_filas": pct(tier_rows[t], rows),
      "requests": tier_req[t], "pct_requests": pct(tier_req[t], total_req),
      "ecpm_ponderado_no_cero": wavg(tier_e_wsum[t], tier_e_wreq[t]),
      "pct_req_monetizado": pct(tier_e_wreq[t], tier_req[t])}
     for t in TIER_ORDER if tier_rows[t]],
 },
 "monetizado": {
   "filas_no_cero": nz_rows, "pct_filas": pct(nz_rows, rows),
   "requests_no_cero": nz_req, "pct_requests": pct(nz_req, total_req),
   "por_pais": [
     {"pais": c, "filas_nz": v[0], "req_nz": v[1],
      "pct_req_pais_monetizado": pct(v[1], v[4]),
      "pct_filas_pais_monetizadas": pct(v[0], v[3]),
      "ecpm_ponderado": wavg(v[2], v[1])}
     for c, v in sorted(cty_nz.items(), key=lambda kv: -kv[1][1])],
   "por_publisher_top": [
     {"publisher": p, "filas_nz": v[0], "req_nz": v[1],
      "share_del_trafico_monetizado": pct(v[1], nz_req),
      "pct_req_propio_monetizado": pct(v[1], v[4]),
      "ecpm_ponderado": wavg(v[2], v[1])}
     for p, v in sorted(pub_nz.items(), key=lambda kv: -kv[1][1])[:25]],
   "por_bundle_top": [
     {"bundle": b, "filas_nz": v[0], "req_nz": v[1],
      "share_del_trafico_monetizado": pct(v[1], nz_req),
      "ecpm_ponderado": wavg(v[2], v[1])}
     for b, v in sorted(app_nz.items(), key=lambda kv: -kv[1][1])[:20]],
   "por_idioma_top": [
     {"idioma": l, "req_nz": v[1], "share": pct(v[1], nz_req),
      "ecpm_ponderado": wavg(v[2], v[1])}
     for l, v in sorted(lang_nz.items(), key=lambda kv: -kv[1][1])[:12]],
   "por_livestream": {k: {"req_nz": v[1], "share": pct(v[1], nz_req),
                          "ecpm_ponderado": wavg(v[2], v[1])}
                      for k, v in live_nz.items()},
   "por_titulo_presente": {k: {"req_nz": v[1], "share": pct(v[1], nz_req),
                               "ecpm_ponderado": wavg(v[2], v[1])}
                           for k, v in title_nz.items()},
   "por_riqueza_metadata": {str(k): {"filas_nz": v[0], "req_nz": v[1],
                                     "ecpm_ponderado": wavg(v[2], v[1])}
                            for k, v in sorted(rich_nz.items())},
   "top_20_ecpm": [{"ecpm": t[0], "requests": t[1], "publisher": t[2], "app": t[3],
                    "pais": t[4], "titulo": t[5]} for t in top_rows[:20]],
 },
}
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(f"filas={rows:,} | monetizadas={nz_rows:,} ({pct(nz_req, total_req)}% de requests)")
print(f"-> {OUT_CSV}")
print(f"-> {OUT_JSON}")
