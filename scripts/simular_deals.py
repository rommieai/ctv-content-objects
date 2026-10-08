# -*- coding: utf-8 -*-
"""Simulacion hacia atras: para unos filtros, que habria comprado un deal armado con los filtros
nativos de PubMatic vs. uno armado con la base enriquecida, usando solo datos viejos.

Para que no haga trampa, lo que "sabemos" sale de una tanda vieja y el resultado se mide en un corte
posterior que no se solapa:

  conocimiento  relleno de una tanda anterior (--viejo): de ahi salen las listas de titulos
  evaluacion    corte crudo posterior (--corte) y su relleno (--nuevo, solo como techo de referencia)

Por cada escenario (pais + genero y/o categoria):

  A  nativo      filas del corte donde el publisher DECLARA todos los atributos del filtro
                 (lo que alcanza "Genre is X" + "Category is Y" en el armado de deals)
  B  enriquecido A + filas cuyo titulo esta en la lista compilada con los datos viejos
                 (lo que alcanza agregar la regla "Title is [lista]")
  techo          filas que el relleno nuevo clasifica en el segmento, tengan o no titulo
                 (lo que se alcanzaria si el dato enriquecido viajara en el bid request)

Uso:
    python scripts/simular_deals.py [--viejo relleno-v20.csv] [--corte crudo-v23.csv] [--nuevo relleno-v23.csv]

Escribe deals/simulacion-v<viejo>-v<corte>.md (tablas) y .json.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from analizar import es_util  # noqa: E402
from analizar_genero_titulo_paises import clasificar_titulo  # noqa: E402
from compilar_deal import (Acum, MAX_LARGO, N_DIMS, ORIGEN_IMDB, ORIGEN_OK, TITULO_NO_SIRVE, codigos,  # noqa: E402
                           generos, n, pct)
from correr_tanda import crudos  # noqa: E402

PAISES = ["Mexico", "Colombia", "Chile"]
ESCENARIOS = [("drama", ""), ("comedia", ""), ("terror", ""), ("accion", ""), ("deportes", ""), ("noticias", ""),
              ("documental", ""), ("", "IAB1-5"), ("", "IAB1-7"), ("", "IAB17"), ("", "IAB12"),
              ("drama", "IAB1-7"), ("comedia", "IAB1-7"), ("accion", "IAB1-5"), ("terror", "IAB1-5"),
              ("deportes", "IAB17"), ("noticias", "IAB12")]
DOMINIO = 0.6
CONF_IMDB = {"A"}


def titulo_util(t):
    return t if es_util("contentTitle", t) and clasificar_titulo(t) not in TITULO_NO_SIRVE and len(t) <= MAX_LARGO else None


def enriquecidos(row, ix, col, extraer):
    org = row[ix[col + "_origen"]]
    fiable = org in ORIGEN_OK or (org in ORIGEN_IMDB and row[ix["ext_confianza"]] in CONF_IMDB)
    return extraer(row[ix[col + "_relleno"]]) if fiable else set()


def leer(path):
    csv.field_size_limit(10**9)
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        hdr = next(r)
        ix = {h: i for i, h in enumerate(hdr)}
        for row in r:
            yield row, ix


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--viejo", default=os.path.join(REPO, "inventory-consolidado-v10-a-v20-relleno.csv"))
    ap.add_argument("--corte", default="")
    ap.add_argument("--nuevo", default="")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")
    cr = crudos(REPO)
    corte = a.corte or cr[max(cr)]
    vc = int(re.search(r"-ctv-v(\d+)-", os.path.basename(corte)).group(1))
    vv = int(re.search(r"-v(\d+)-relleno", os.path.basename(a.viejo)).group(1))
    nuevo = a.nuevo or os.path.join(REPO, f"inventory-consolidado-v10-a-v{vc}-relleno.csv")
    if vv >= vc:
        sys.exit("el relleno viejo debe ser de una tanda anterior al corte")

    # 1. conocimiento viejo: por titulo, requests por genero y por categoria enriquecidos (todos los paises)
    gen_t, cat_t, gen_n, cat_n = defaultdict(Counter), defaultdict(Counter), Counter(), Counter()
    for row, ix in leer(a.viejo):
        t = titulo_util(row[ix["contentTitle"]])
        if not t:
            continue
        q = int(row[ix["Total Requests"]])
        g, c = enriquecidos(row, ix, "contentGenre", generos), enriquecidos(row, ix, "contentCategory", codigos)
        if g:
            gen_n[t] += q
            for v in g:
                gen_t[t][v] += q
        if c:
            cat_n[t] += q
            for v in c:
                cat_t[t][v] += q
    conocidos = set(gen_n) | set(cat_n)

    def en_lista(t, g, c):
        return ((not g or (gen_n[t] and gen_t[t][g] >= DOMINIO * gen_n[t])) and
                (not c or (cat_n[t] and cat_t[t][c] >= DOMINIO * cat_n[t])))

    # 2. filas del corte de evaluacion (via el relleno nuevo, que trae lo crudo y lo enriquecido)
    vigentes = set()
    for row, _ in leer(corte):
        if len(row) == N_DIMS + 2:
            vigentes.add(tuple(row[:N_DIMS]))
    filas = defaultdict(list)   # pais -> (titulo, generos declarados, categorias declaradas, generos enriq., categorias enriq., q, e)
    for row, ix in leer(nuevo):
        p = row[ix["Country"]]
        if p not in PAISES or tuple(row[:N_DIMS]) not in vigentes:
            continue
        filas[p].append((titulo_util(row[ix["contentTitle"]]), generos(row[ix["contentGenre"]]), codigos(row[ix["contentCategory"]]),
                         enriquecidos(row, ix, "contentGenre", generos), enriquecidos(row, ix, "contentCategory", codigos),
                         int(row[ix["Total Requests"]]), float(row[ix["eCPM"]])))

    res = []
    for p in PAISES:
        U = Acum()
        for f in filas[p]:
            U.suma(f[5], f[6])
        for g, c in ESCENARIOS:
            A, B, extra, techo, otro = Acum(), Acum(), Acum(), Acum(), Acum()
            cache, titulos, nuevos = {}, set(), 0
            for t, gd, cd, ge, ce, q, e in filas[p]:
                nat = (not g or g in gd) and (not c or c in cd)
                lst = False
                if t:
                    if t not in cache:
                        cache[t] = en_lista(t, g, c)
                    lst = cache[t]
                if nat:
                    A.suma(q, e)
                if nat or lst:
                    B.suma(q, e)
                if lst and not nat:
                    extra.suma(q, e)
                    titulos.add(t)
                    # el publisher declara todos los atributos del filtro y alguno no coincide
                    if (not g or gd) and (not c or cd):
                        otro.suma(q, e)
                if (not g or g in ge) and (not c or c in ce):
                    techo.suma(q, e)
                    if t and t not in conocidos and not nat:
                        nuevos += q
            res.append({"pais": p, "genero": g, "categoria": c, "universo": U.req,
                        "A": vars(A) | {"ecpm": A.ecpm()}, "B": vars(B) | {"ecpm": B.ecpm()},
                        "extra": vars(extra) | {"ecpm": extra.ecpm()}, "techo": vars(techo) | {"ecpm": techo.ecpm()},
                        "extra_declara_otro": otro.req, "titulos_extra": len(titulos), "techo_titulos_nuevos": nuevos})

    def d(x):
        return f"${x:.2f}" if x else "—"
    L = [f"# Simulación: deal con filtros nativos vs. con la base enriquecida (conocimiento hasta v{vv}, medido en el corte v{vc})\n",
         "| Fuente | Archivo |\n|---|---|", f"| Conocimiento (listas de títulos) | `{os.path.basename(a.viejo)}` |",
         f"| Corte evaluado | `{os.path.basename(corte)}` |", f"| Techo de referencia | `{os.path.basename(nuevo)}` |\n",
         "*A = filas donde el publisher declara todos los atributos del filtro. B = A + filas cuyo título está en la lista "
         f"compilada con los datos viejos (dominio ≥ {DOMINIO}, orígenes confiables). Techo = lo que el relleno nuevo clasifica en "
         "el segmento, con o sin título. Porcentajes de requests sobre el país.*\n"]
    for p in PAISES:
        rs = [r for r in res if r["pais"] == p]
        L += [f"## {p} — {n(rs[0]['universo'])} requests en el corte\n",
              "| Género | Categoría | A nativo | B enriquecido | Ganancia de B | Techo | B / techo | eCPM A | eCPM de lo que agrega B | % vendido de lo que agrega B | Títulos que agrega B | Lo agregado donde el publisher declara otra cosa |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in rs:
            L.append(f"| {r['genero'] or '—'} | {r['categoria'] or '—'} | {pct(r['A']['req'], r['universo'])} | {pct(r['B']['req'], r['universo'])} | "
                     f"{'+' + pct(r['extra']['req'], r['A']['req']) if r['A']['req'] else '—'} | {pct(r['techo']['req'], r['universo'])} | "
                     f"{pct(r['B']['req'], r['techo']['req'])} | {d(r['A']['ecpm'])} | {d(r['extra']['ecpm'])} | "
                     f"{pct(r['extra']['vend'], r['extra']['req'])} | {n(r['titulos_extra'])} | {pct(r['extra_declara_otro'], r['extra']['req'])} |")
        L.append("")
    out = os.path.join(REPO, "deals", f"simulacion-v{vv}-v{vc}")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out + ".md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
