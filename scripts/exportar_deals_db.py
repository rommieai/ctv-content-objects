# -*- coding: utf-8 -*-
"""Arma la base SQLite que usa el armador de deals de la plataforma (plataforma-etiquetado, pestaña Deals).

La web no lee los CSV: lee esta base chica, que se regenera en cada tanda y se copia a la VM.

  base         el corte vigente agregado por pais x publisher x titulo x atributos (requests, vendidos,
               gasto): sobre esto se mide el alcance de cada camino
  titulo_attr  que generos y categorias le reconoce nuestra base a cada titulo (todo el consolidado
               relleno, solo origenes confiables, atributo dominante): de aqui salen las listas de titulos
  valores      generos y categorias disponibles por pais, para los selectores
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


def titulo_util(t):
    return t if es_util("contentTitle", t) and clasificar_titulo(t) not in TITULO_NO_SIRVE and len(t) <= MAX_LARGO else ""


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
    evid = {"genero": defaultdict(Counter), "categoria": defaultdict(Counter)}
    con_dato = {"genero": Counter(), "categoria": Counter()}
    valores = Counter()
    with open(relleno, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        ix = {h: i for i, h in enumerate(next(r))}

        def enriq(row, col, extraer):
            org = row[ix[col + "_origen"]]
            fiable = org in ORIGEN_OK or (org in ORIGEN_IMDB and row[ix["ext_confianza"]] in CONF_IMDB)
            return extraer(row[ix[col + "_relleno"]]) if fiable else set()
        for row in r:
            q, e = int(row[ix["Total Requests"]]), float(row[ix["eCPM"]])
            t = titulo_util(row[ix["contentTitle"]])
            ge, ce = enriq(row, "contentGenre", generos), enriq(row, "contentCategory", codigos)
            if t:
                for tipo, vals in (("genero", ge), ("categoria", ce)):
                    if vals:
                        con_dato[tipo][t] += q
                        for v in vals:
                            evid[tipo][t][v] += q
            if tuple(row[:N_DIMS]) not in vigentes:
                continue
            gd, cd = generos(row[ix["contentGenre"]]), codigos(row[ix["contentCategory"]])
            pais = row[ix["Country"]]
            x = base[(pais, row[ix["Publisher"]], t, lista(gd), lista(cd), lista(ge), lista(ce))]
            x[0] += q
            x[3] += 1
            if e > 0 and q > 0:
                x[1] += q
                x[2] += q * e
            for v in gd | ge:
                valores[("genero", v, pais)] += q
            for v in cd | ce:
                valores[("categoria", v, pais)] += q

    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    tmp = a.salida + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    db = sqlite3.connect(tmp)
    db.executescript("""
        CREATE TABLE meta (clave TEXT PRIMARY KEY, valor TEXT NOT NULL);
        CREATE TABLE base (pais TEXT NOT NULL, publisher TEXT NOT NULL, titulo TEXT NOT NULL, gen_decl TEXT NOT NULL,
            cat_decl TEXT NOT NULL, gen_enr TEXT NOT NULL, cat_enr TEXT NOT NULL, req INTEGER NOT NULL,
            vend INTEGER NOT NULL, gasto REAL NOT NULL, filas INTEGER NOT NULL);
        CREATE TABLE titulo_attr (tipo TEXT NOT NULL, valor TEXT NOT NULL, titulo TEXT NOT NULL,
            PRIMARY KEY (tipo, valor, titulo)) WITHOUT ROWID;
        CREATE TABLE valores (tipo TEXT NOT NULL, valor TEXT NOT NULL, pais TEXT NOT NULL, req INTEGER NOT NULL,
            PRIMARY KEY (tipo, valor, pais)) WITHOUT ROWID;
    """)
    db.executemany("INSERT INTO base VALUES (?,?,?,?,?,?,?,?,?,?,?)", ((*k, *v) for k, v in base.items()))
    attr = [(tipo, v, t) for tipo in evid for t, c in evid[tipo].items() for v, q in c.items()
            if q > 0 and q >= DOMINIO * con_dato[tipo][t]]
    db.executemany("INSERT INTO titulo_attr VALUES (?,?,?)", attr)
    db.executemany("INSERT INTO valores VALUES (?,?,?,?)", ((*k, q) for k, q in valores.items()))
    db.executescript("CREATE INDEX idx_base_pais ON base(pais); CREATE INDEX idx_base_titulo ON base(titulo);")
    meta = {"version": str(version), "ventana": ventana_texto(m.group(3), m.group(4)), "corte": os.path.basename(corte),
            "relleno": os.path.basename(relleno), "generado": datetime.now().isoformat(timespec="seconds"),
            "dominio": str(DOMINIO), "confianza_imdb": ",".join(sorted(CONF_IMDB)),
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
