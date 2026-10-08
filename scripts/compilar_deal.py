# -*- coding: utf-8 -*-
"""Compila un segmento de la base enriquecida a algo que PubMatic puede filtrar en un deal.

Un filtro de deal compara contra lo que el publisher manda en el bid request, asi que los valores
rellenados por nosotros no se pueden usar directo. Lo que si viaja es el titulo: este script toma un
segmento definido con NUESTROS atributos (genero normalizado o categoria IAB, ya rellenados) y saca
la lista de contentTitle crudos que lo componen, en el formato que acepta la regla
Content Object > Title > Upload del armado de deals (CSV de una columna "Title_is", max 500 KB por
archivo y 10,000 valores por deal).

Ademas mide, sobre el corte vigente, cuanto alcanza cada camino:
  filtro nativo   filas donde el publisher ya declara el atributo (lo que alcanza "Genre is X")
  lista de titulos filas cuyo titulo esta en la lista (lo que alcanza "Title is [lista]")
  union            las dos reglas juntas

Un titulo entra a la lista si es un titulo de verdad y el atributo domina sus requests con dato
(--dominio, default 0.6). Solo cuentan los valores cuyo origen es confiable: original, intra_titulo,
derivado_genero, y los que dependen del match IMDb solo con confianza A (--confianza-imdb).

Uso:
    python scripts/compilar_deal.py --listar genero [--paises Mexico]
    python scripts/compilar_deal.py --genero terror --paises Mexico [--nombre terror-mx]
    python scripts/compilar_deal.py --categoria IAB17 --paises "Mexico,Colombia"

Salida en deals/<nombre>/: Title_is-NN.csv, ficha.md (tablas) y ficha.json.
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
from analizar_genero_titulo_paises import clasificar_titulo, norm_genre  # noqa: E402
from correr_tanda import crudos  # noqa: E402

MAX_VALORES = 10000      # valores por deal en la carga por CSV
MAX_BYTES = 500 * 1000   # tamano maximo de cada CSV
MAX_LARGO = 245          # largo maximo de un Title en PubMatic
TITULO_NO_SIRVE = {"macro_sin_reemplazar", "hash", "placeholder", "encoding_roto", "sin_letras", "muy_corto"}
ORIGEN_OK = {"original", "intra_titulo", "derivado_genero"}
ORIGEN_IMDB = {"imdb", "derivado_tipo", "wikidata", "tvmaze"}
N_DIMS = 14


def n(x):
    return f"{x:,}"


def pct(a, b):
    return f"{100.0 * a / b:.1f}%" if b else "—"


def codigos(v):
    """'[IAB1-5, 333]' -> {'IAB1-5', '333'}"""
    return {t.strip() for t in v.strip().strip("[]").split(",") if t.strip()} if es_util("contentCategory", v) else set()


def generos(v):
    return set(norm_genre(v)[0]) if es_util("contentGenre", v) else set()


ATRIBUTOS = {"genero": ("contentGenre", generos), "categoria": ("contentCategory", codigos)}


class Acum:
    """Filas, requests, requests vendidos y gasto de un conjunto de filas del corte."""
    def __init__(self):
        self.filas = self.req = self.vend = 0
        self.gasto = 0.0

    def suma(self, q, e):
        self.filas += 1
        self.req += q
        if e > 0 and q > 0:
            self.vend += q
            self.gasto += q * e

    def ecpm(self):
        return self.gasto / self.vend if self.vend else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--relleno", default="", help="CSV relleno (default: el de mayor version de la raiz)")
    ap.add_argument("--corte", default="", help="CSV crudo del corte vigente (default: el de mayor version de la raiz)")
    ap.add_argument("--paises", default="", help='ej. "Mexico,Colombia" (default: todos)')
    ap.add_argument("--genero", default="", help="genero normalizado (ver --listar genero)")
    ap.add_argument("--categoria", default="", help="codigo IAB, ej. IAB17 o IAB1-5")
    ap.add_argument("--listar", default="", choices=["", "genero", "categoria"], help="lista los valores disponibles y sale")
    ap.add_argument("--dominio", type=float, default=0.6, help="parte minima de los requests con dato del titulo que debe tener el atributo")
    ap.add_argument("--confianza-imdb", default="A", choices=["A", "B", "ninguna"], help="peor confianza del match IMDb que se acepta")
    ap.add_argument("--nombre", default="", help="carpeta de salida dentro de deals/")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")

    def ultimo(patron, regex):
        c = {int(m.group(1)): p for p in glob.glob(os.path.join(REPO, patron)) for m in [re.search(regex, os.path.basename(p))] if m}
        return c[max(c)] if c else None
    relleno = a.relleno or ultimo("inventory-consolidado-v10-a-v*-relleno.csv", r"-v(\d+)-relleno\.csv$")
    cr = crudos(REPO)
    corte = a.corte or (cr[max(cr)] if cr else None)
    if not relleno or not corte:
        sys.exit("faltan el CSV relleno o el CSV crudo del corte en la raiz")
    tipo = a.listar or ("genero" if a.genero else "categoria" if a.categoria else "")
    if not tipo:
        sys.exit("indicar --genero, --categoria o --listar")
    col, extraer = ATRIBUTOS[tipo]
    objetivo = (a.genero or a.categoria).strip()
    if tipo == "genero":
        objetivo = objetivo.lower()
    paises = {p.strip() for p in a.paises.split(",") if p.strip()}
    conf_ok = {"A": {"A"}, "B": {"A", "B"}, "ninguna": set()}[a.confianza_imdb]

    # llaves del corte vigente: el alcance se mide solo sobre ellas (el consolidado arrastra llaves viejas)
    vigentes = set()
    with open(corte, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) == N_DIMS + 2:
                vigentes.add(tuple(row[:N_DIMS]))

    csv.field_size_limit(10**9)
    filas = []                                   # (titulo o None, declarados, enriquecidos, requests, ecpm, vigente)
    por_titulo = defaultdict(Counter)            # titulo -> requests por valor enriquecido (evidencia: todo el consolidado)
    con_dato = Counter()                         # titulo -> requests con algun valor
    disponibles = Counter()
    with open(relleno, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        hdr = next(r)
        ix = {h: i for i, h in enumerate(hdr)}
        i_rel, i_org, i_conf = ix[col + "_relleno"], ix[col + "_origen"], ix["ext_confianza"]
        for row in r:
            if paises and row[ix["Country"]] not in paises:
                continue
            q, e = int(row[ix["Total Requests"]]), float(row[ix["eCPM"]])
            t = row[ix["contentTitle"]]
            titulo = t if es_util("contentTitle", t) and clasificar_titulo(t) not in TITULO_NO_SIRVE and len(t) <= MAX_LARGO else None
            declarados = extraer(row[ix[col]])
            org = row[i_org]
            fiable = org in ORIGEN_OK or (org in ORIGEN_IMDB and row[i_conf] in conf_ok)
            enriq = extraer(row[i_rel]) if fiable else set()
            vig = tuple(row[:N_DIMS]) in vigentes
            if titulo and enriq:
                con_dato[titulo] += q
                for v in enriq:
                    por_titulo[titulo][v] += q
            if vig:
                for v in enriq | declarados:
                    disponibles[v] += q
                filas.append((titulo, declarados, q, e))

    if a.listar:
        print(f"{tipo}: valores con requests en el corte ({', '.join(sorted(paises)) or 'todos los paises'})")
        for v, q in disponibles.most_common(60):
            print(f"  {v:<28} {n(q):>18}")
        return 0

    lista = {t for t, c in por_titulo.items() if c[objetivo] >= a.dominio * con_dato[t] and c[objetivo] > 0}
    U, nativo, por_lista, union, solo_lista, contradice = Acum(), Acum(), Acum(), Acum(), Acum(), Acum()
    req_titulo = Counter()
    for titulo, declarados, q, e in filas:
        U.suma(q, e)
        es_nat = objetivo in declarados
        en_lista = titulo in lista
        if es_nat:
            nativo.suma(q, e)
        if en_lista:
            por_lista.suma(q, e)
            req_titulo[titulo] += q
            if declarados and not es_nat:
                contradice.suma(q, e)
        if es_nat or en_lista:
            union.suma(q, e)
        if en_lista and not es_nat:
            solo_lista.suma(q, e)
    if not req_titulo:
        sys.exit(f"ningun titulo del corte cumple para {tipo}={objetivo}")

    # CSV en el formato de la plantilla de PubMatic (COT_INCLUSION_Title_is.csv)
    orden = [t for t, _ in req_titulo.most_common()]
    recortados = orden[MAX_VALORES:]
    orden = orden[:MAX_VALORES]
    nombre = a.nombre or re.sub(r"[^a-z0-9]+", "-", f"{tipo}-{objetivo}-{'-'.join(sorted(paises)) or 'todos'}".lower()).strip("-")
    out = os.path.join(REPO, "deals", nombre)
    os.makedirs(out, exist_ok=True)
    for viejo in glob.glob(os.path.join(out, "Title_is-*.csv")):
        os.remove(viejo)
    archivos, bloque, peso = [], [], 12
    for t in orden + [None]:
        linea = None if t is None else ('"' + t.replace('"', '""') + '"\r\n').encode("utf-8")
        if t is None or peso + len(linea) > MAX_BYTES:
            if bloque:
                p = os.path.join(out, f"Title_is-{len(archivos) + 1:02d}.csv")
                with open(p, "wb") as f:
                    f.write(b'"Title_is"\r\n' + b"".join(bloque))
                archivos.append((os.path.basename(p), len(bloque), os.path.getsize(p)))
            bloque, peso = [], 12
        if t is not None:
            bloque.append(linea)
            peso += len(linea)

    def fila(etq, x):
        return f"| {etq} | {n(x.filas)} | {n(x.req)} | {pct(x.req, U.req)} | {pct(x.vend, x.req)} | " + (f"${x.ecpm():.2f}" if x.ecpm() else "—") + " |"
    L = [f"# Segmento {tipo} = {objetivo} ({', '.join(sorted(paises)) or 'todos los paises'})\n",
         "| Fuente | Valor |\n|---|---|",
         f"| Relleno | `{os.path.basename(relleno)}` |", f"| Corte vigente | `{os.path.basename(corte)}` |",
         f"| Dominio minimo por titulo | {a.dominio} |", f"| Confianza IMDb aceptada | {a.confianza_imdb} |\n",
         "## Alcance sobre el corte vigente\n",
         "| Camino | Filas | Requests | % del universo | % vendido | eCPM pond. |\n|---|---:|---:|---:|---:|---:|",
         fila("Universo (paises elegidos)", U), fila(f"Filtro nativo ({col} declarado)", nativo),
         fila("Lista de titulos (Title is)", por_lista), fila("Union de las dos reglas", union),
         fila("Solo por la lista (no lo alcanza el filtro nativo)", solo_lista),
         fila("En la lista pero el publisher declara otro valor", contradice), "",
         "## Archivos para subir a PubMatic (Content Object > Title > Upload)\n",
         "| Archivo | Titulos | KB |\n|---|---:|---:|"]
    L += [f"| `{f}` | {n(c)} | {b / 1000:.0f} |" for f, c, b in archivos]
    if recortados:
        L.append(f"\n*Quedaron fuera {n(len(recortados))} titulos por el tope de {n(MAX_VALORES)} por deal "
                 f"({pct(sum(req_titulo[t] for t in recortados), por_lista.req)} de los requests de la lista).*")
    L += ["\n## Top 25 titulos de la lista\n", "| Titulo | Requests | % de la lista |\n|---|---:|---:|"]
    L += [f"| {t} | {n(q)} | {pct(q, por_lista.req)} |" for t, q in req_titulo.most_common(25)]
    with open(os.path.join(out, "ficha.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    datos = {"tipo": tipo, "valor": objetivo, "paises": sorted(paises), "relleno": os.path.basename(relleno),
             "corte": os.path.basename(corte), "dominio": a.dominio, "confianza_imdb": a.confianza_imdb,
             "titulos": len(orden), "titulos_recortados": len(recortados), "archivos": [f for f, _, _ in archivos],
             "alcance": {k: {"filas": x.filas, "requests": x.req, "vendidos": x.vend, "ecpm_ponderado": x.ecpm()}
                         for k, x in (("universo", U), ("nativo", nativo), ("lista", por_lista), ("union", union),
                                      ("solo_lista", solo_lista), ("contradice_declarado", contradice))}}
    with open(os.path.join(out, "ficha.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    print(f"{tipo}={objetivo} | universo {n(U.req)} requests")
    print(f"  filtro nativo:    {n(nativo.req):>18} ({pct(nativo.req, U.req)})")
    print(f"  lista de titulos: {n(por_lista.req):>18} ({pct(por_lista.req, U.req)}) con {n(len(orden))} titulos")
    print(f"  union:            {n(union.req):>18} ({pct(union.req, U.req)})  -> +{pct(solo_lista.req, nativo.req)} sobre el filtro nativo")
    print(f"  la lista incluye {pct(contradice.req, por_lista.req)} de requests donde el publisher declara otro valor")
    print(f"-> {os.path.relpath(out, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
