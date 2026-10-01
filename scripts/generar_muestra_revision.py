# -*- coding: utf-8 -*-
"""Muestra de filas con valores RELLENADOS + pagina HTML para revisarlas a mano (paso 1 de 2).

La unidad de revision es una fila real del consolidado relleno (titulo x app x publisher x pais...):
la pagina muestra todos sus content objects, resalta los que se llenaron de mas (no dice con que
metodo) y explica los codigos (IAB, rating, livestream) para que el revisor no tenga que buscarlos.
El revisor marca cada valor llenado como correcto / incorrecto / no se puede saber.

Seleccion: cada par columna x origen es un estrato con una cuota de valores a revisar; se elige
siempre el estrato mas atrasado respecto de su cuota y, dentro de el, la siguiente fila de un sorteo
proporcional a requests (Efraimidis-Spirakis). Un solo registro por titulo (o por app x genero si la
fila no trae titulo), asi la muestra no se concentra en los titulos grandes. Una fila cuenta para
todos los estratos de los campos que trae llenados.

Escribe, con el prefijo de salida:
    <prefijo>.html   la pagina de revision (autocontenida; guarda el avance en el navegador y
                     exporta la revision a JSON)
    <prefijo>.json   los mismos registros y los totales por estrato (para extrapolar)

Paso 2: scripts/calcular_precision_revision.py <revision exportada>.json

Uso:
    python scripts/generar_muestra_revision.py inventory-consolidado-v10-a-v22-relleno.csv \
        reportes/NN/recursos/revision-manual-v22 --registros 500 --semilla 22
"""
import argparse
import csv
import json
import os
import random
import sys
import urllib.parse
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enriquecer_externo import normalizar_titulo, es_util  # noqa: E402

csv.field_size_limit(10 ** 8)
AQUI = os.path.dirname(os.path.abspath(__file__))
CAMPOS = ["contentGenre", "contentCategory", "contentSeries", "contentRating", "contentIsLiveStream",
          "contentLength", "contentLanguage"]
NOMBRE_CAMPO = {"contentGenre": "Género", "contentCategory": "Categoría (IAB)", "contentSeries": "Serie",
                "contentRating": "Clasificación por edad", "contentIsLiveStream": "En vivo / lineal",
                "contentLength": "Duración (código)", "contentLanguage": "Idioma"}
# cuota de valores llenados a revisar por estrato (columna|origen)
CUOTAS = {"contentCategory|derivado_tipo": 55, "contentCategory|derivado_genero": 55,
          "contentCategory|intra_titulo": 45, "contentSeries|imdb": 55, "contentSeries|intra_titulo": 45,
          "contentGenre|imdb": 55, "contentGenre|intra_titulo": 50, "contentRating|intra_titulo": 50,
          "contentRating|wikidata": 30, "contentLength|intra_titulo": 35,
          "contentIsLiveStream|app_semantica": 30,
          "contentCategory_afinado|genero_declarado": 60, "contentCategory_afinado|imdb": 50,
          "contentCategory_afinado|wikidata": 15}
EXTERNO = {"imdb", "wikidata", "tvmaze", "derivado_tipo"}

# ---------------------------------------------------------------------------------------------
# Significados
# ---------------------------------------------------------------------------------------------
# Traduccion al espanol de los nombres IAB mas frecuentes (el nombre oficial en ingles se muestra igual)
IAB_ES = {
    "Arts & Entertainment": "Arte y entretenimiento", "Movies": "Películas", "Television": "Televisión",
    "Music": "Música", "Sports": "Deportes", "News": "Noticias", "Food & Drink": "Comida y bebida",
    "Travel": "Viajes", "Religion & Spirituality": "Religión y espiritualidad", "Education": "Educación",
    "Video & Computer Games": "Videojuegos", "Family & Parenting": "Familia y crianza", "Humor": "Humor",
    "Hobbies & Interests": "Pasatiempos", "Science": "Ciencia", "Technology & Computing": "Tecnología",
    "Business": "Negocios", "Health & Fitness": "Salud y ejercicio", "Home & Garden": "Hogar y jardín",
    "Style & Fashion": "Moda y estilo", "Automotive": "Automotriz", "Pets": "Mascotas",
    "Society": "Sociedad", "Law, Gov't & Politics": "Leyes, gobierno y política", "Real Estate": "Bienes raíces",
    "Personal Finance": "Finanzas personales", "Careers": "Empleo", "Shopping": "Compras",
    "Uncategorized": "Sin categoría", "Fine Art": "Bellas artes", "Celebrity Fan/Gossip": "Celebridades",
    "Books & Literature": "Libros y literatura", "Humor ": "Humor", "Documentary": "Documental",
    "Action and Adventure Movies": "Películas de acción y aventura", "Comedy Movies": "Películas de comedia",
    "Drama Movies": "Películas de drama", "Horror Movies": "Películas de terror",
    "Romance Movies": "Películas románticas", "Science Fiction Movies": "Películas de ciencia ficción",
    "Family and Children Movies": "Películas familiares e infantiles", "Documentary Movies": "Películas documentales",
    "Crime and Mystery Movies": "Películas de crimen y misterio", "Animation Movies": "Películas animadas",
    "Fantasy Movies": "Películas de fantasía", "Western Movies": "Películas del oeste", "World Movies": "Cine del mundo",
    "Action TV": "Series de acción", "Comedy TV": "Series de comedia", "Drama TV": "Series de drama",
    "Reality TV": "Reality", "Children's TV": "TV infantil", "Animation TV": "Series animadas",
    "Crime TV": "Series policiales", "Documentary TV": "TV documental", "Science Fiction TV": "Series de ciencia ficción",
    "Soap Opera TV": "Telenovelas", "Special Interest TV": "TV de interés especial", "Sports TV": "TV deportiva",
    "Family/Children TV": "TV familiar / infantil", "Mystery TV": "Series de misterio", "Fantasy TV": "Series de fantasía",
    "Horror TV": "Series de terror", "Music TV": "TV musical", "Talk Show": "Programa de entrevistas",
    "Game Show": "Concursos", "Holiday TV": "TV de temporada / fiestas", "Romance TV": "Series románticas",
    "Science Fiction": "Ciencia ficción", "Soccer": "Fútbol", "Boxing": "Boxeo", "Wrestling": "Lucha libre",
    "Auto Racing": "Automovilismo", "Basketball": "Baloncesto", "Baseball": "Béisbol",
    "American Football": "Fútbol americano", "Tennis": "Tenis", "Mixed Martial Arts": "Artes marciales mixtas",
    "Golf": "Golf", "Cooking": "Cocina", "Video Gaming": "Videojuegos", "Entertainment": "Entretenimiento",
    "Pop Culture": "Cultura pop", "Comics and Animation": "Cómics y animación", "Anime": "Anime",
    "International News": "Noticias internacionales", "Local News": "Noticias locales",
    "National News": "Noticias nacionales", "Weather": "Clima", "Politics": "Política",
}
RATING_SIGNIFICADO = {
    "g": "Apto para todo público (escala de EE. UU.)", "pg": "Se sugiere supervisión de los padres (EE. UU.)",
    "pg-13": "Mayores de 13 años (EE. UU.)", "r": "Mayores de 17, o menores acompañados (EE. UU.)",
    "nc-17": "Solo adultos, 18+ (EE. UU.)", "tv-y": "Infantil, todas las edades (TV EE. UU.)",
    "tv-y7": "Niños de 7 años o más (TV EE. UU.)", "tv-g": "Todo público (TV EE. UU.)",
    "tv-pg": "Supervisión de los padres, aprox. 10+ (TV EE. UU.)", "tv-14": "Mayores de 14 años (TV EE. UU.)",
    "tv-ma": "Solo adultos, 17+ (TV EE. UU.)", "nr": "Sin clasificar", "unrated": "Sin clasificar",
    "not rated": "Sin clasificar", "all ages": "Todas las edades (escala nueva del reporte, equivale a G)",
    "teen": "Adolescentes, aprox. 10+ (escala nueva del reporte, equivale a TV-PG)",
    "teen plus": "Mayores de 13–15 (escala nueva del reporte, equivale a TV-14)",
    "adults": "Solo adultos, 18+ (escala nueva del reporte, equivale a R / TV-MA)",
    "aa": "Infantil (clasificación RTC de México)", "a": "Todo público (clasificación RTC de México)",
    "b": "Adolescentes de 12 años o más (clasificación RTC de México)",
    "b15": "Mayores de 15 años (clasificación RTC de México)", "c": "Mayores de 18 años (clasificación RTC de México)",
    "d": "Solo adultos, contenido explícito (clasificación RTC de México)",
    "tp": "Todos los públicos (escala de España)", "bbfc-pg": "Supervisión de los padres (escala británica BBFC)",
    "bbfc-u": "Todo público (escala británica BBFC)", "bbfc-12": "Mayores de 12 (escala británica BBFC)",
    "bbfc-15": "Mayores de 15 (escala británica BBFC)", "bbfc-18": "Solo adultos (escala británica BBFC)",
    "l": "Libre, todas las edades (escala de Brasil)", "atp": "Apta para todo público (escala de Argentina)",
}
# codigos de categoria que no estan en ninguna taxonomia IAB pero aparecen en el inventario
IAB_NO_ESTANDAR = {
    "IAB1-22": "Código no estándar (no existe en IAB 1.0); varios vendedores lo usan para «Entretenimiento» en general",
}
LIVESTREAM = {"1": "Sí: en vivo o canal lineal (programado en horario)", "0": "No: bajo demanda (el usuario elige qué ver)"}


def cargar_iab(cache_dir):
    """codigo -> (taxonomia, ruta en ingles). 1.0 por codigo IABx-y; 2.2/3.0 por id numerico."""
    d = os.path.join(cache_dir, "iab")
    iab10, iab2 = {}, {}
    with open(os.path.join(d, "Content_Taxonomy_1.0.tsv"), encoding="utf-8") as f:
        r = csv.reader(f, delimiter="\t")
        next(r)
        padres = {}
        for row in r:
            if len(row) < 3:
                continue
            cod, nombre = row[0].strip(), row[2].strip()
            padres[cod] = nombre
            base = cod.split("-")[0]
            iab10[cod] = [padres.get(base, ""), nombre] if "-" in cod else [nombre]
    for v in ("2.2", "3.0"):
        with open(os.path.join(d, f"Content_Taxonomy_{v}.tsv"), encoding="utf-8") as f:
            r = csv.reader(f, delimiter="\t")
            next(r)
            next(r)
            for row in r:
                if len(row) < 4 or not row[0].strip():
                    continue
                ruta = [x.strip() for x in row[3:7] if x.strip()]
                iab2.setdefault(row[0].strip(), {})[v] = ruta
    return iab10, iab2


def es_ruta(ruta):
    return " › ".join(IAB_ES.get(x, x) for x in ruta)


def significado_categoria(valor, iab10, iab2):
    out = []
    for c in [x.strip() for x in valor.strip().strip("[]").split(",") if x.strip()]:
        if c.upper().startswith("IAB") and c.upper() in iab10:
            ruta = iab10[c.upper()]
            out.append({"codigo": c, "es": es_ruta(ruta), "en": " › ".join(ruta), "tax": "IAB 1.0"})
        elif c in iab2:
            t = iab2[c]
            ruta = t.get("2.2") or t.get("3.0")
            nota = "IAB 2.2" if "2.2" in t else "IAB 3.0"
            if "2.2" in t and "3.0" in t and t["2.2"] != t["3.0"]:
                nota = f"IAB 2.2 (en 3.0: {' › '.join(t['3.0'])})"
            out.append({"codigo": c, "es": es_ruta(ruta), "en": " › ".join(ruta), "tax": nota})
        elif c.upper() in IAB_NO_ESTANDAR:
            out.append({"codigo": c, "es": IAB_NO_ESTANDAR[c.upper()], "en": "", "tax": ""})
        elif not any(ch.isdigit() for ch in c):
            out.append({"codigo": c, "es": "texto libre del vendedor, no es un código IAB", "en": "", "tax": ""})
        else:
            out.append({"codigo": c, "es": "código que no existe en las taxonomías IAB (1.0, 2.2, 3.0)", "en": "", "tax": ""})
    return out


def significado(campo, valor, iab10, iab2, runtime):
    v = (valor or "").strip()
    if not v:
        return None
    if campo == "contentCategory":
        return {"iab": significado_categoria(v, iab10, iab2)}
    if campo == "contentRating":
        t = RATING_SIGNIFICADO.get(v.lower(), "")
        num = v.strip("+- ").rstrip("+")
        if not t and num.isdigit():
            t = f"Mayores de {int(num)} años" if int(num) > 0 else "Todas las edades"
        return {"texto": t}
    if campo == "contentIsLiveStream":
        return {"texto": LIVESTREAM.get(v, "")}
    if campo == "contentLength":
        t = "Código del reporte (1 a 8); PubMatic no ha confirmado a qué duración corresponde cada código."
        if runtime:
            t += f" Según IMDb/Wikidata la obra dura {runtime} min."
        return {"texto": t}
    return None


# ---------------------------------------------------------------------------------------------
# Informacion extra de IMDb (datasets locales) y Wikidata (por IMDb id) que no llena ninguna columna
# ---------------------------------------------------------------------------------------------
TIPO_ES = {"movie": "película", "tvSeries": "serie", "tvMiniSeries": "miniserie", "tvMovie": "película para TV",
           "short": "cortometraje", "video": "video", "tvSpecial": "especial de TV", "tvShort": "corto de TV"}
WD_PROPS = {"P495": "pais", "P57": "director", "P161": "reparto", "P272": "productora", "P449": "cadena",
            "P364": "idioma_original", "P2437": "temporadas", "P1113": "episodios", "P577": "estreno",
            "P4947": "tmdb_pelicula", "P4983": "tmdb_serie"}


def info_extra(ids, cache_dir):
    """imdb id -> dict con titulo original, anios, duracion, calificacion IMDb y lo de Wikidata."""
    import gzip
    out = {t: {} for t in ids}
    if not ids:
        return out
    d = os.path.join(cache_dir, "imdb")
    nn = (lambda x: "" if x == "\\N" else x)
    with gzip.open(os.path.join(d, "title.basics.tsv.gz"), "rt", encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            if row[0] in out:
                out[row[0]].update({"titulo_imdb": row[2], "titulo_original": row[3] if row[3] != row[2] else "",
                                    "tipo": TIPO_ES.get(row[1], row[1]), "anio_inicio": nn(row[5]),
                                    "anio_fin": nn(row[6]), "duracion_min": nn(row[7]),
                                    "generos_imdb": nn(row[8]).replace(",", ", ")})
    with gzip.open(os.path.join(d, "title.ratings.tsv.gz"), "rt", encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        for row in r:
            if row[0] in out:
                out[row[0]].update({"calificacion": row[1], "votos": row[2]})
    # Wikidata: cache propio para no repetir consultas entre corridas
    cpath = os.path.join(cache_dir, "wikidata_extra.json")
    wd = json.load(open(cpath, encoding="utf-8")) if os.path.exists(cpath) else {}
    faltan = sorted(t for t in ids if t not in wd)
    try:
        import requests
    except ImportError:
        requests = None
    for i in range(0, len(faltan), 40):
        lote = faltan[i:i + 40]
        sel = " ".join(f'(GROUP_CONCAT(DISTINCT ?{v}L; separator=", ") AS ?{v})' for v in WD_PROPS.values())
        opt = " ".join(f'OPTIONAL {{ ?item wdt:{p} ?{v}x . OPTIONAL {{ ?{v}x rdfs:label ?{v}es FILTER(LANG(?{v}es)="es") }} '
                       f'OPTIONAL {{ ?{v}x rdfs:label ?{v}en FILTER(LANG(?{v}en)="en") }} '
                       f'BIND(COALESCE(?{v}es, ?{v}en, STR(?{v}x)) AS ?{v}L) }}' for p, v in WD_PROPS.items())
        valores = " ".join('"' + t + '"' for t in lote)
        q = f"SELECT ?imdb {sel} WHERE {{ VALUES ?imdb {{ {valores} }} ?item wdt:P345 ?imdb . {opt} }} GROUP BY ?imdb"
        res = None
        for _ in range(3):
            if requests is None:
                break
            try:
                rr = requests.get("https://query.wikidata.org/sparql", params={"query": q, "format": "json"},
                                  headers={"User-Agent": "ctv-revision/0.1 (analista)"}, timeout=120)
                rr.raise_for_status()
                res = rr.json()
                break
            except Exception as e:  # noqa: BLE001
                print(f"  aviso wikidata: {e}", file=sys.stderr)
        if res is None:
            continue
        for t in lote:
            wd[t] = {}
        for b in res["results"]["bindings"]:
            fila = {}
            for v in WD_PROPS.values():
                val = b.get(v, {}).get("value", "")
                if v == "reparto":
                    val = ", ".join(val.split(", ")[:4])
                if v == "estreno":
                    val = min((x[:4] for x in val.split(", ") if x[:4].isdigit()), default="")
                fila[v] = val
            wd[b["imdb"]["value"]] = fila
        json.dump(wd, open(cpath, "w", encoding="utf-8"), ensure_ascii=False)
    for t in ids:
        out[t]["wikidata"] = {k: v for k, v in (wd.get(t) or {}).items() if v}
        out[t]["imdb_id"] = t
    return out


# ---------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("relleno")
    ap.add_argument("salida", help="prefijo de salida (sin extension)")
    ap.add_argument("--cache-dir", default="cache-enriquecimiento")
    ap.add_argument("--registros", type=int, default=500)
    ap.add_argument("--semilla", type=int, default=22)
    ap.add_argument("--plantilla", default=os.path.join(AQUI, "plantillas", "revision-manual.html"))
    a = ap.parse_args()
    cache = json.load(open(os.path.join(a.cache_dir, "titulos.json"), encoding="utf-8"))
    iab10, iab2 = cargar_iab(a.cache_dir)
    rnd = random.Random(a.semilla)

    def riesgo(o, k):
        i = (cache.get(k) or {}).get("imdb") if k else None
        if o not in EXTERNO or not i:
            return "-"
        if normalizar_titulo(i["titulo"]) != k or i["votos"] < 100 or (len(k.split()) == 1 and i["candidatos"] > 1):
            return "alerta"
        return "normal"

    def estratos(d):
        out = []
        for c in CAMPOS:
            o = d.get(c + "_origen", "")
            if o and o != "original":
                out.append(f"{c}|{o}")
        if d.get("contentCategory_afinado_origen"):
            out.append(f"contentCategory_afinado|{d['contentCategory_afinado_origen']}")
        return out

    def titulo_legible(d):
        t = d["contentTitle"].strip() if es_util("contentTitle", d["contentTitle"]) else ""
        t = urllib.parse.unquote(t) if "%" in t else t
        return t.replace("+", " ") if "+" in t and " " not in t else t

    filas, totales = [], defaultdict(Counter)
    por_estrato = defaultdict(list)
    with open(a.relleno, encoding="utf-8-sig", newline="") as f:
        for d in csv.DictReader(f):
            req = int(d["Total Requests"] or 0)
            es = estratos(d)
            for e in es:
                totales[e]["filas"] += 1
                totales[e]["requests"] += req
            # solo filas con un titulo real: sin titulo un humano no puede verificar nada
            if not es or not d["titulo_clave"] or not titulo_legible(d):
                continue
            idx = len(filas)
            filas.append(d)
            clave = rnd.random() ** (1.0 / max(req, 1))      # sorteo proporcional a requests
            for e in es:
                if e in CUOTAS:
                    por_estrato[e].append((clave, idx))
    for e in por_estrato:
        por_estrato[e].sort(reverse=True)
    print(f"{len(filas):,} filas con titulo y algun valor llenado", file=sys.stderr)

    usados, elegidos, cubre = set(), [], Counter()
    punteros = Counter()
    while len(elegidos) < a.registros:
        vivos = [e for e in CUOTAS if punteros[e] < len(por_estrato[e])]
        if not vivos:
            break
        e = min(vivos, key=lambda x: cubre[x] / CUOTAS[x])
        while punteros[e] < len(por_estrato[e]):
            _, idx = por_estrato[e][punteros[e]]
            punteros[e] += 1
            d = filas[idx]
            if d["titulo_clave"] in usados:
                continue
            usados.add(d["titulo_clave"])
            elegidos.append(idx)
            for x in estratos(d):
                cubre[x] += 1
            break

    # informacion extra de IMDb / Wikidata para las filas que usaron una fuente externa
    externas = {}
    for idx in elegidos:
        d = filas[idx]
        usa = any(d.get(c + "_origen") in EXTERNO for c in CAMPOS) or \
            d.get("contentCategory_afinado_origen") in ("imdb", "wikidata")
        if usa and d.get("ext_imdb_id"):
            externas[idx] = d["ext_imdb_id"]
    extra = info_extra(set(externas.values()), a.cache_dir)

    registros = []
    for n, idx in enumerate(elegidos, 1):
        d = filas[idx]
        k = d["titulo_clave"]
        i = (cache.get(k) or {}).get("imdb") or {}
        tl = titulo_legible(d)
        campos = []
        for c in CAMPOS:
            o = d.get(c + "_origen", "")
            lleno = bool(o and o != "original")
            valor = d.get(c + "_relleno", "") if lleno else (d[c].strip() if es_util(c, d[c]) else "")
            sig = significado(c, valor, iab10, iab2, d.get("ext_runtime_min", ""))
            unidades = []
            if lleno:
                est = f"{c}|{o}"
                if c == "contentCategory":
                    af = d.get("contentCategory_afinado_origen", "")
                    for x in sig["iab"]:
                        agregado = bool(af) and x["codigo"] not in ("IAB1", "IAB1-5", "IAB1-7", "IAB1-22")
                        unidades.append({"valor": x["codigo"], "agregado": agregado,
                                         "estrato": f"contentCategory_afinado|{af}" if agregado else est})
                elif c == "contentGenre":
                    for g in [x.strip() for x in valor.split(",") if x.strip()]:
                        unidades.append({"valor": g, "agregado": False, "estrato": est})
                else:
                    unidades.append({"valor": valor, "agregado": False, "estrato": est})
            campos.append({"campo": c, "nombre": NOMBRE_CAMPO[c], "valor": valor, "llenado": lleno,
                           "original": d[c].strip(), "riesgo": riesgo(o, k) if lleno else "",
                           "unidades": unidades, "significado": sig})
        q = urllib.parse.quote_plus(f'"{tl}" {d["App Name"]}')
        registros.append({
            "id": n, "titulo": tl, "app": d["App Name"], "bundle": d["pageURL"],
            "publisher": d["Publisher"], "pais": d["Country"], "requests": int(d["Total Requests"] or 0),
            "campos": campos,
            "extra": extra.get(externas.get(idx)) if idx in externas else None,
            "ayuda": {"busqueda": f"https://www.google.com/search?q={q}",
                      "imdb": f"https://www.imdb.com/title/{i['id']}/" if i.get("id") and d.get("ext_imdb_id") else "",
                      "imdb_texto": f'{i.get("titulo", "")} ({i.get("anio", "")}, {i.get("tipo", "")})' if i.get("id") and d.get("ext_imdb_id") else ""}})

    meta = {"fuente": os.path.basename(a.relleno), "semilla": a.semilla, "cuotas": CUOTAS,
            "cubre": dict(cubre), "totales_estrato": {e: dict(v) for e, v in totales.items()},
            "version": os.path.basename(a.salida)}
    datos = {"meta": meta, "registros": registros}
    json.dump(datos, open(a.salida + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    html = open(a.plantilla, encoding="utf-8").read()
    html = html.replace("/*__DATOS__*/null", json.dumps(datos, ensure_ascii=False).replace("</", "<\\/"))
    open(a.salida + ".html", "w", encoding="utf-8").write(html)
    print(f"{len(registros)} registros -> {a.salida}.html")
    for e in CUOTAS:
        print(f"  {e:38} {cubre[e]:4} valores (cuota {CUOTAS[e]})")


if __name__ == "__main__":
    main()
