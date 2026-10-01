# -*- coding: utf-8 -*-
"""Auditoria del relleno de content objects (enriquecer_externo.py): que tan confiable es lo llenado.

No usa nada online. Lee el CSV de relleno y el cache de titulos (match IMDb + Wikidata) y mide:

  origen          por columna y origen del valor: filas, requests y requests vendidos (eCPM > 0)
  enmascaramiento prueba "leave-one-publisher-out" de intra_titulo: para cada fila que YA traia el
                  dato, se esconde el publisher completo y se predice con las demas rutas del mismo
                  titulo (mismos candados que el pipeline). Mide cuanto acierta el metodo cuando se
                  sabe la respuesta. Igual para derivado_genero en contentCategory (el mapa
                  genero -> IAB contra la categoria que el vendedor si mando).
  imdb_tipo       chequeo independiente del match IMDb: titulos con marca de serie en el propio
                  titulo (S01E03, temporada 2, episodio 4) o con contentSeries declarado por otras
                  rutas; si IMDb dice pelicula, el match es sospechoso (homonimo). Por confianza.
                  (El genero NO sirve para auditar el match: la confianza A/B ya se asigna por
                  coincidencia de genero, seria circular.)
  riesgo_externo  filas llenadas con un dato externo, por confianza, numero de candidatos IMDb
                  homonimos, votos del candidato elegido y palabras del titulo.
  homonimos_intra titulos donde dos publishers (>= 5 filas cada uno) mandan generos disjuntos:
                  probablemente dos contenidos distintos con el mismo titulo; cuanto relleno
                  intra_titulo cae en ellos.
  rating_pais     contentRating llenado desde Wikidata (clasificacion RTC de Mexico) por pais.

Uso:
    python scripts/auditar_relleno.py inventory-consolidado-v10-a-v22-relleno.csv reportes/NN/recursos/auditoria-relleno.json
"""
import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from enriquecer_externo import es_util, es_propagable, canon_valor, RE_SXXEXX, GENERO_IAB  # noqa: E402
from analizar_genero_titulo_paises import norm_genre  # noqa: E402

csv.field_size_limit(10 ** 8)
COLS = ["contentCategory", "contentSeries", "contentLength", "contentIsLiveStream", "contentRating", "contentGenre"]
INTRA_COLS = ["contentCategory", "contentSeries", "contentLength", "contentRating", "contentGenre"]
RE_SERIE = re.compile(r"\b(season|temporada|episode|episodio|cap[ií]tulo)\s*\d+|\bs\d{1,2}\s*e\d{1,3}\b|\bep\.?\s*\d+", re.I)
GENERICOS = {"tv/series (generico)", "pelicula (generico)", "entretenimiento (generico)", "otros", ""}


def bucket(x, cortes, etiquetas):
    for c, e in zip(cortes, etiquetas):
        if x <= c:
            return e
    return etiquetas[-1]


def codigos(cat):
    return [c.strip() for c in cat.strip().strip("[]").split(",") if c.strip()]


def vertical(code):
    return code.split("-")[0]


class Acc:
    """Acumulador de aciertos en filas y requests."""
    def __init__(self):
        self.c = Counter()

    def add(self, clave, req):
        self.c[clave + "_filas"] += 1
        self.c[clave + "_req"] += req

    def out(self, total="evaluadas"):
        d = dict(self.c)
        for k in list(d):
            if k.endswith("_filas") and not k.startswith(total):
                base = k[:-6]
                if d.get(total + "_filas"):
                    d[base + "_pct_filas"] = round(100 * d[k] / d[total + "_filas"], 1)
                    d[base + "_pct_req"] = round(100 * d[base + "_req"] / max(d[total + "_req"], 1), 1)
        return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("relleno")
    ap.add_argument("salida_json")
    ap.add_argument("--cache-dir", default="cache-enriquecimiento")
    ap.add_argument("--umbral-intra", type=float, default=0.8)
    ap.add_argument("--min-filas-serie", type=int, default=30)
    ap.add_argument("--min-rutas-serie", type=int, default=2)
    a = ap.parse_args()
    cache = json.load(open(os.path.join(a.cache_dir, "titulos.json"), encoding="utf-8"))

    # ---- lectura (solo los campos necesarios) ----
    filas = []
    with open(a.relleno, encoding="utf-8-sig", newline="") as f:
        for d in csv.DictReader(f):
            req = int(d["Total Requests"] or 0)
            vend = req if float(d["eCPM"] or 0) > 0 else 0
            filas.append({"k": d["titulo_clave"], "pub": d["Publisher"], "pais": d["Country"], "req": req, "vend": vend,
                          "titulo": d["contentTitle"], "gn": d["genero_normalizado"], "conf": d["ext_confianza"],
                          "tipo": d["ext_tipo"],
                          **{c: d[c] for c in COLS},
                          **{c + "_r": d[c + "_relleno"] for c in COLS}, **{c + "_o": d[c + "_origen"] for c in COLS}})
    n = len(filas)
    print(f"{n:,} filas", file=sys.stderr)
    R = {"entrada": a.relleno, "filas": n, "requests": sum(x["req"] for x in filas)}

    # ---- 1. origen ----
    org = {c: defaultdict(Counter) for c in COLS}
    for x in filas:
        for c in COLS:
            o = x[c + "_o"] or "sin_dato"
            org[c][o]["filas"] += 1
            org[c][o]["req"] += x["req"]
            org[c][o]["vend"] += x["vend"]
    R["origen"] = {c: {o: dict(v) for o, v in d.items()} for c, d in org.items()}

    # ---- 2. enmascaramiento de intra_titulo (leave-one-publisher-out) ----
    cnt = {c: defaultdict(lambda: defaultdict(Counter)) for c in INTRA_COLS}   # col -> k -> pub -> Counter(valor)
    for x in filas:
        if not x["k"]:
            continue
        for c in INTRA_COLS:
            if es_propagable(c, x[c]):
                cnt[c][x["k"]][x["pub"]][canon_valor(c, x[c])] += 1
    enm = {}
    for c in INTRA_COLS:
        acc = Acc()
        pred_cache = {}
        for x in filas:
            if not x["k"] or not es_propagable(c, x[c]):
                continue
            acc.add("evaluadas", x["req"])
            key = (x["k"], x["pub"])
            if key not in pred_cache:
                otras = Counter()
                pubs = 0
                for p, cc in cnt[c][x["k"]].items():
                    if p != x["pub"]:
                        otras.update(cc)
                        pubs += 1
                pred = None
                tot = sum(otras.values())
                if tot and not (c == "contentSeries" and (tot < a.min_filas_serie or pubs < a.min_rutas_serie)):
                    v, m = otras.most_common(1)[0]
                    if m / tot >= a.umbral_intra:
                        pred = v
                pred_cache[key] = pred
            pred = pred_cache[key]
            if pred is None:
                continue
            acc.add("predichas", x["req"])
            real = canon_valor(c, x[c])
            if c == "contentGenre":
                gp, gr = set(norm_genre(pred)[0]), set(norm_genre(real)[0])
                if pred.strip().lower() == real.strip().lower():
                    acc.add("exacto", x["req"])
                if gp & gr:
                    acc.add("comparte_genero", x["req"])
            elif c == "contentCategory":
                if set(codigos(pred)) == set(codigos(real)):
                    acc.add("exacto", x["req"])
                if {vertical(z) for z in codigos(pred)} & {vertical(z) for z in codigos(real)}:
                    acc.add("misma_vertical", x["req"])
            else:
                if pred.strip().lower() == real.strip().lower():
                    acc.add("exacto", x["req"])
        d = acc.c
        out = dict(d)
        for base in ("exacto", "comparte_genero", "misma_vertical"):
            if d.get(base + "_filas"):
                out[base + "_pct_filas"] = round(100 * d[base + "_filas"] / d["predichas_filas"], 1)
                out[base + "_pct_req"] = round(100 * d[base + "_req"] / max(d["predichas_req"], 1), 1)
        if d.get("evaluadas_filas"):
            out["cobertura_pct_filas"] = round(100 * d.get("predichas_filas", 0) / d["evaluadas_filas"], 1)
        enm[c] = out
    R["enmascaramiento_intra"] = enm

    # derivado_genero de contentCategory contra la categoria IAB 1.0 declarada por el vendedor
    acc = Acc()
    genericos = Counter()
    for x in filas:
        cod = [z for z in codigos(x["contentCategory"]) if z.upper().startswith("IAB")] \
            if es_util("contentCategory", x["contentCategory"]) else []
        gs = [g for g in x["gn"].split(";") if g]
        if not cod or not gs:
            continue
        pc = [GENERO_IAB[g] for g in gs if g in GENERO_IAB]
        pred = pc[0] if pc else "[IAB1]"
        p = codigos(pred)[0]
        acc.add("evaluadas", x["req"])
        acc.add("mapa_especifico" if pc else "mapa_generico_IAB1", x["req"])
        if p in cod:
            acc.add("exacto", x["req"])
        if vertical(p) in {vertical(z) for z in cod}:
            acc.add("misma_vertical", x["req"])
    R["enmascaramiento_derivado_genero"] = acc.out()
    for x in filas:
        if x["contentCategory_o"] in ("derivado_genero", "derivado_tipo", "intra_titulo"):
            v = x["contentCategory_r"].strip()
            genericos[("IAB1 generico" if v == "[IAB1]" else "especifico") + "|" + x["contentCategory_o"]] += x["req"]
    R["categoria_generica_req"] = dict(genericos)

    # ---- 3. chequeo independiente del tipo IMDb (marcas de serie) ----
    serie_decl = defaultdict(set)
    for x in filas:
        if x["k"] and es_propagable("contentSeries", x["contentSeries"]):
            serie_decl[x["k"]].add(x["pub"])
    marca = defaultdict(bool)
    for x in filas:
        if x["k"] and (RE_SERIE.search(x["titulo"]) or RE_SXXEXX.search(x["titulo"])):
            marca[x["k"]] = True
    tipo_chk = defaultdict(Counter)
    for k, v in cache.items():
        i = v.get("imdb")
        if not i:
            continue
        ev = "marca_en_titulo" if marca.get(k) else ("serie_declarada_2+_rutas" if len(serie_decl.get(k, ())) >= 2 else None)
        if not ev:
            continue
        pel = i["tipo"] in ("movie", "tvMovie", "video", "short")
        tipo_chk[i["confianza"]]["titulos_" + ev] += 1
        tipo_chk[i["confianza"]]["imdb_pelicula_" + ev] += pel
    R["imdb_tipo_vs_marca_serie"] = {k: dict(v) for k, v in sorted(tipo_chk.items())}

    # ---- 4. riesgo de lo llenado con fuente externa ----
    ext_origen = {"imdb", "wikidata", "tvmaze", "derivado_tipo"}
    riesgo = defaultdict(lambda: defaultdict(Counter))
    for x in filas:
        i = (cache.get(x["k"]) or {}).get("imdb") if x["k"] else None
        for c in COLS:
            if x[c + "_o"] not in ext_origen or not i:
                continue
            req = x["req"]
            for dim, val in (("confianza", i["confianza"]),
                             ("candidatos", bucket(i["candidatos"], [1, 4, 9], ["1", "2-4", "5-9", "10+"])),
                             ("votos", bucket(i["votos"], [0, 99, 999], ["0", "1-99", "100-999", "1000+"])),
                             ("palabras_titulo", bucket(len(x["k"].split()), [1, 2], ["1", "2", "3+"]))):
                riesgo[c][dim + ":" + val]["filas"] += 1
                riesgo[c][dim + ":" + val]["req"] += req
            if i["candidatos"] > 1 and i["votos"] < 100:
                riesgo[c]["alto_riesgo(2+ candidatos y <100 votos)"]["filas"] += 1
                riesgo[c]["alto_riesgo(2+ candidatos y <100 votos)"]["req"] += req
    R["riesgo_externo"] = {c: {k: dict(v) for k, v in sorted(d.items())} for c, d in riesgo.items()}

    # ---- 5. homonimos entre publishers (intra_titulo) ----
    gen_pub = defaultdict(lambda: defaultdict(Counter))
    for x in filas:
        if x["k"]:
            for g in x["gn"].split(";"):
                if g and g not in GENERICOS and "generico" not in g:
                    gen_pub[x["k"]][x["pub"]][g] += 1
    sospechosos = {}
    for k, pubs in gen_pub.items():
        grandes = {p: set(c) for p, c in pubs.items() if sum(c.values()) >= 5}
        ps = list(grandes)
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                if not grandes[ps[i]] & grandes[ps[j]]:
                    sospechosos[k] = (ps[i], sorted(grandes[ps[i]])[:3], ps[j], sorted(grandes[ps[j]])[:3])
                    break
            if k in sospechosos:
                break
    hom = Counter()
    for x in filas:
        if x["k"] in sospechosos:
            hom["filas_titulo_sospechoso"] += 1
            for c in COLS:
                if x[c + "_o"] == "intra_titulo":
                    hom[c + "_intra_filas"] += 1
                    hom[c + "_intra_req"] += x["req"]
    tot_intra = Counter()
    for x in filas:
        for c in COLS:
            if x[c + "_o"] == "intra_titulo":
                tot_intra[c + "_intra_filas"] += 1
    R["homonimos_intra"] = {"titulos_sospechosos": len(sospechosos), "titulos_con_2+_publishers": sum(
        1 for p in gen_pub.values() if sum(1 for c in p.values() if sum(c.values()) >= 5) >= 2),
        **dict(hom), "total_intra": dict(tot_intra),
        "ejemplos": [{"titulo": k, "pub_a": v[0], "generos_a": v[1], "pub_b": v[2], "generos_b": v[3]}
                     for k, v in sorted(sospechosos.items(), key=lambda kv: -sum(sum(c.values()) for c in gen_pub[kv[0]].values()))[:25]]}

    # ---- 6. rating de Wikidata por pais ----
    rp = defaultdict(Counter)
    for x in filas:
        if x["contentRating_o"] == "wikidata":
            rp[x["pais"]]["filas"] += 1
            rp[x["pais"]]["req"] += x["req"]
    R["rating_wikidata_por_pais"] = {p: dict(v) for p, v in rp.items()}

    json.dump(R, open(a.salida_json, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("->", a.salida_json)


if __name__ == "__main__":
    main()
