# -*- coding: utf-8 -*-
"""Arma la base SQLite que usa el armador de deals de la plataforma (plataforma-etiquetado, pestaña Deals).

La web no lee los CSV: lee esta base chica, que se regenera en cada tanda y se copia a la VM.

  base         el corte vigente agregado por pais x publisher x titulo x lo que el publisher declara en
               cada content object (requests, vendidos, gasto): sobre esto se mide el alcance de cada camino
  titulo_attr  que genero, categoria, serie, rating, duracion y en vivo le reconoce nuestra base a cada titulo (todo el consolidado
               relleno, solo origenes confiables, atributo dominante): de aqui salen las listas de titulos
  valores      valores disponibles de cada content object por pais, para los selectores
  meta         de que archivos salio y cuando

Los criterios son los de scripts/compilar_deal.py (mismo dominio minimo y mismos origenes).

Uso:
    python scripts/exportar_deals_db.py [--salida plataforma-etiquetado/data/deals.db]
        [--relleno relleno.csv] [--corte crudo.csv]
    scp plataforma-etiquetado/data/deals.db usuario@vm:.../plataforma-etiquetado/data/deals.db
"""
import argparse
import csv
import glob
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from analizar import es_util  # noqa: E402
from analizar_genero_titulo_paises import clasificar_titulo  # noqa: E402
from compilar_deal import MAX_LARGO, N_DIMS, ORIGEN_IMDB, ORIGEN_OK, TITULO_NO_SIRVE, codigos, generos  # noqa: E402
from correr_tanda import RE_CRUDO, crudos, ventana_texto  # noqa: E402

DOMINIO = 0.6
CONF_IMDB = {"A"}
RE_HASH = re.compile(r"^[0-9a-f]{32}$")


def titulo_util(t):
    return t if es_util("contentTitle", t) and clasificar_titulo(t) not in TITULO_NO_SIRVE and len(t) <= MAX_LARGO else ""


def uno(col):
    """Extractor de una columna de valor unico: {valor} si trae dato util."""
    return lambda v: {v.strip()} if es_util(col, v) else set()


def series(v):
    """Nombre de la serie, sin macros sin reemplazar ni nombres hasheados (no le dicen nada a quien arma el deal)."""
    v = v.strip()
    if not es_util("contentSeries", v) or "{{" in v or "[CONTENT" in v.upper() or RE_HASH.match(v.lower()) or ";" in v:
        return set()
    return {v}


# Content objects del reporte: (tipo, columna del CSV, columna en la tabla base, extractor, se puede enriquecer).
# Los enriquecibles tienen ademas su lista de titulos (titulo_attr); idioma y "trae titulo" solo valen como vienen:
# el idioma nunca se rellena y sin titulo no hay nada que reconocer.
ATRIBUTOS = [
    ("genero", "contentGenre", "gen_decl", generos, True),
    ("categoria", "contentCategory", "cat_decl", codigos, True),
    ("serie", "contentSeries", "ser_decl", series, True),
    ("rating", "contentRating", "rat_decl", uno("contentRating"), True),
    ("duracion", "contentLength", "len_decl", uno("contentLength"), True),
    ("envivo", "contentIsLiveStream", "live_decl", uno("contentIsLiveStream"), True),
    ("idioma", "contentLanguage", "lang_decl", uno("contentLanguage"), False),
    ("con_titulo", "contentIsTitlePresent", "tit_decl", uno("contentIsTitlePresent"), False),
]
# Origenes del relleno que se dan por buenos para armar listas (los que dependen del match IMDb, solo con confianza A)
ORIGEN_FIABLE = ORIGEN_OK | {"app_semantica", "corregido_imdb", "corregido_genero"}


def lista(vals):
    """{'drama', 'accion'} -> ';accion;drama;' (para buscar con LIKE '%;drama;%')"""
    return ";" + ";".join(sorted(vals)) + ";" if vals else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salida", default=os.path.join(REPO, "plataforma-etiquetado", "data", "deals.db"))
    ap.add_argument("--relleno", default="")
    ap.add_argument("--corte", default="")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")
    cr = crudos(REPO)
    corte = a.corte or cr[max(cr)]
    m = RE_CRUDO.match(os.path.basename(corte))
    version = int(m.group(1))
    relleno = a.relleno or os.path.join(REPO, f"inventory-consolidado-v10-a-v{version}-relleno.csv")
    if not os.path.exists(relleno):
        sys.exit(f"no existe {relleno}")

    vigentes = set()
    with open(corte, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) == N_DIMS + 2:
                vigentes.add(tuple(row[:N_DIMS]))

    csv.field_size_limit(10**9)
    base = defaultdict(lambda: [0, 0, 0.0, 0])                  # llave -> [req, vendidos, gasto, filas]
    enriquecibles = [t for t, _, _, _, enr in ATRIBUTOS if enr]
    evid = {t: defaultdict(Counter) for t in enriquecibles}     # tipo -> titulo -> requests por valor reconocido
    con_dato = {t: Counter() for t in enriquecibles}
    valores = Counter()
    with open(relleno, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        ix = {h: i for i, h in enumerate(next(r))}

        def enriq(row, col, extraer):
            org = row[ix[col + "_origen"]]
            fiable = org in ORIGEN_FIABLE or (org in ORIGEN_IMDB and row[ix["ext_confianza"]] in CONF_IMDB)
            return extraer(row[ix[col + "_relleno"]]) if fiable else set()
        for row in r:
            q, e = int(row[ix["Total Requests"]]), float(row[ix["eCPM"]])
            t = titulo_util(row[ix["contentTitle"]])
            reconocidos = {tipo: enriq(row, col, extraer) for tipo, col, _, extraer, enr in ATRIBUTOS if enr}
            if t:
                for tipo, vals in reconocidos.items():
                    if vals:
                        con_dato[tipo][t] += q
                        for v in vals:
                            evid[tipo][t][v] += q
            if tuple(row[:N_DIMS]) not in vigentes:
                continue
            pais = row[ix["Country"]]
            declarados = [extraer(row[ix[col]]) for _, col, _, extraer, _ in ATRIBUTOS]
            x = base[(pais, row[ix["Publisher"]], t, *(lista(d) for d in declarados))]
            x[0] += q
            x[3] += 1
            if e > 0 and q > 0:
                x[1] += q
                x[2] += q * e
            for (tipo, *_), d in zip(ATRIBUTOS, declarados):
                for v in d | reconocidos.get(tipo, set()):
                    valores[(tipo, v, pais)] += q

    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    tmp = a.salida + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    db = sqlite3.connect(tmp)
    db.executescript("""
        CREATE TABLE meta (clave TEXT PRIMARY KEY, valor TEXT NOT NULL);
        CREATE TABLE base (pais TEXT NOT NULL, publisher TEXT NOT NULL, titulo TEXT NOT NULL,
            {cols}, req INTEGER NOT NULL, vend INTEGER NOT NULL, gasto REAL NOT NULL, filas INTEGER NOT NULL);
        CREATE TABLE titulo_attr (tipo TEXT NOT NULL, valor TEXT NOT NULL, titulo TEXT NOT NULL,
            PRIMARY KEY (tipo, valor, titulo)) WITHOUT ROWID;
        CREATE TABLE valores (tipo TEXT NOT NULL, valor TEXT NOT NULL, pais TEXT NOT NULL, req INTEGER NOT NULL,
            PRIMARY KEY (tipo, valor, pais)) WITHOUT ROWID;
    """.replace("{cols}", ", ".join(f"{c} TEXT NOT NULL" for _, _, c, _, _ in ATRIBUTOS)))
    db.executemany(f"INSERT INTO base VALUES ({','.join('?' * (3 + len(ATRIBUTOS) + 4))})", ((*k, *v) for k, v in base.items()))
    attr = [(tipo, v, t) for tipo in evid for t, c in evid[tipo].items() for v, q in c.items()
            if q > 0 and q >= DOMINIO * con_dato[tipo][t]]
    db.executemany("INSERT INTO titulo_attr VALUES (?,?,?)", attr)
    db.executemany("INSERT INTO valores VALUES (?,?,?,?)", ((*k, q) for k, q in valores.items()))
    db.executescript("CREATE INDEX idx_base_pais ON base(pais); CREATE INDEX idx_base_titulo ON base(titulo);")
    meta = {"version": str(version), "ventana": ventana_texto(m.group(3), m.group(4)), "corte": os.path.basename(corte),
            "relleno": os.path.basename(relleno), "generado": datetime.now().isoformat(timespec="seconds"),
            "dominio": str(DOMINIO), "esquema": "2",
            "atributos": ",".join(t for t, *_ in ATRIBUTOS), "enriquecibles": ",".join(enriquecibles), "confianza_imdb": ",".join(sorted(CONF_IMDB)),
            "requests": str(sum(v[0] for v in base.values())), "filas_corte": str(sum(v[3] for v in base.values()))}
    db.executemany("INSERT INTO meta VALUES (?,?)", meta.items())
    db.commit()
    db.execute("VACUUM")
    db.close()
    os.replace(tmp, a.salida)
    print(f"-> {a.salida} ({os.path.getsize(a.salida) / 1e6:.1f} MB): v{version}, {len(base):,} grupos de {int(meta['filas_corte']):,} filas, "
          f"{len(attr):,} pares titulo-atributo, {int(meta['requests']):,} requests")


if __name__ == "__main__":
    main()
