# -*- coding: utf-8 -*-
"""Corre una tanda completa a partir del CSV crudo descargado de PubMatic.

Encadena lo que antes se corria a mano (ver "Pipeline" en el README):

  verificar    chequeos del CSV crudo (encabezado, filas, metricas, ventana, cambio de formato)
  consolidar   consolidado v10-a-vN = corte nuevo + consolidado anterior (consolidar.py)
  analizar     JSON del detallado por pais y de requests/eCPM lleno-vacio
  relleno      normalizar_monetizar.py + enriquecer_externo.py --wikidata
  graficas     los siete scripts de SVG/JSON de la tanda
  validar      validar_categorias.py y validar_genero_series.py (consolidado y relleno)
  reportes     los tres md (detallado, graficas, completitud)
  archivar     deja en reportes/ la tanda vigente y la anterior; el resto va a old_reports/
  readme       arbol de carpetas y tabla de reportes del README
  deals        (--deals) genera deals.db para la pestaña Deals de la plataforma y la sube a la VM
  bigquery     (--bigquery) recarga ctv_inventory.consolidado_v10_a_v14 con el corte crudo
  commit       (--commit / --push) commit de reportes/ y README.md

La version, la ventana y el nombre de la carpeta salen del nombre del archivo
(60333-inventory-source-alcance-ctv-v22-latam-content-objetcs-20260915T00_00-20260929T23_59.csv).
Cada paso se salta si sus salidas ya existen y son mas nuevas que sus entradas, asi que se puede
volver a lanzar despues de un fallo; --forzar los repite todos.

Uso:
    python scripts/correr_tanda.py [crudo.csv] [--bigquery] [--commit] [--push]
    python scripts/correr_tanda.py crudo.csv --prueba carpeta   # todo a una carpeta aparte, sin
                                                                 # archivar, README, BigQuery ni git

Sin crudo.csv toma el de mayor version de la raiz. Sale con codigo 0 si todo paso, 1 si fallo un
paso y 2 si el CSV no paso los chequeos. El log queda en logs/tanda-vN-<fecha>.log.
"""
import argparse
import csv
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from analizar import es_util  # noqa: E402

RE_CRUDO = re.compile(r"^\d+-inventory-source-alcance-ctv-v(\d+)-latam-content-objetcs-"
                      r"((\d{8})T\d\d_\d\d-(\d{8})T\d\d_\d\d)\.csv$")
RE_CARPETA = re.compile(r"^(\d+)-consolidado-v10-a-v(\d+)-")
ENCABEZADO = ["Publisher ID", "Publisher", "pageURL", "App Name", "Country", "contentGenre", "contentCategory",
              "contentSeries", "contentIsTitlePresent", "contentLength", "contentLanguage", "contentIsLiveStream",
              "contentTitle", "contentRating", "Total Requests", "eCPM"]
CONTENT = ["contentGenre", "contentCategory", "contentSeries", "contentLength", "contentLanguage",
           "contentIsLiveStream", "contentTitle", "contentRating"]
FILAS_TOPE = 512000      # las exportaciones vienen truncadas a este numero de filas
MAX_MALFORMADAS = 0.001  # fraccion de filas con otro numero de columnas que se tolera
SALTO_FORMATO_PP = 10.0  # cambio en % de filas llenas de una columna que se avisa (v16 fue de 10-13)
PAISES = "Mexico,Colombia,Chile"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
BQ_PROYECTO = "tudia-tagscreen"
BQ_TABLA = "ctv_inventory.consolidado_v10_a_v14"
BQ_GCLOUD_CONFIG = "ctv-bot"  # configuracion de gcloud con la cuenta de servicio ctv-bot@tudia-tagscreen

LOG = None


def decir(msg=""):
    print(msg, flush=True)
    if LOG:
        LOG.write(msg + "\n")
        LOG.flush()


class Fallo(Exception):
    def __init__(self, msg, codigo=1):
        super().__init__(msg)
        self.codigo = codigo


def n(x):
    return f"{x:,}"


def ventana_texto(d1, d2):
    """'20260915', '20260929' -> '15–29 sep 2026'; entre meses, '31 ago–14 sep 2026'."""
    a, b = datetime.strptime(d1, "%Y%m%d"), datetime.strptime(d2, "%Y%m%d")
    fin = f"{b.day} {MESES[b.month - 1]} {b.year}"
    if (a.year, a.month) == (b.year, b.month):
        return f"{a.day}–{fin}"
    if a.year == b.year:
        return f"{a.day} {MESES[a.month - 1]}–{fin}"
    return f"{a.day} {MESES[a.month - 1]} {a.year}–{fin}"


def crudos(carpeta):
    """{version: ruta} de los CSV crudos de una carpeta."""
    out = {}
    for p in glob.glob(os.path.join(carpeta, "*-inventory-source-alcance-ctv-v*-latam-content-objetcs-*.csv")):
        m = RE_CRUDO.match(os.path.basename(p))
        if m:
            out[int(m.group(1))] = p
    return out


def stats_crudo(path):
    """Una pasada por el CSV crudo: encabezado, filas, filas malformadas, requests y % de filas llenas."""
    llenas = dict.fromkeys(CONTENT, 0)
    idx = [(c, ENCABEZADO.index(c)) for c in CONTENT]
    filas = malas = req = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        hdr = next(r)
        for row in r:
            if len(row) != len(ENCABEZADO):
                malas += 1
                continue
            try:
                req += int(row[14])
                float(row[15])
            except ValueError:
                malas += 1
                continue
            filas += 1
            for c, i in idx:
                if es_util(c, row[i]):
                    llenas[c] += 1
    return {"encabezado": hdr, "filas": filas, "malformadas": malas, "requests": req,
            "pct_llenas": {c: (100.0 * v / filas if filas else 0.0) for c, v in llenas.items()}}


def contar_filas(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        return sum(1 for _ in r)


def verificar(crudo, version, d1, anteriores):
    """Chequeos del crudo. Devuelve (stats, avisos); lanza Fallo(codigo=2) si no se debe seguir."""
    st = stats_crudo(crudo)
    avisos = []
    if st["encabezado"] != ENCABEZADO:
        raise Fallo(f"el encabezado del CSV cambio: {st['encabezado']}", 2)
    if not st["filas"] or not st["requests"]:
        raise Fallo("el CSV no trae filas o trae 0 requests", 2)
    if st["malformadas"] > MAX_MALFORMADAS * st["filas"]:
        raise Fallo(f"{n(st['malformadas'])} filas malformadas de {n(st['filas'])}", 2)
    if st["malformadas"]:
        avisos.append(f"{n(st['malformadas'])} filas malformadas (se descartan)")
    if st["filas"] != FILAS_TOPE:
        avisos.append(f"el corte trae {n(st['filas'])} filas, no las {n(FILAS_TOPE)} de siempre")
    previas = {v: p for v, p in anteriores.items() if v < version}
    if previas:
        pv = max(previas)
        m = RE_CRUDO.match(os.path.basename(previas[pv]))
        if d1 <= m.group(3):
            avisos.append(f"la ventana empieza el {d1}, no despues que la de v{pv} ({m.group(3)})")
        ant = stats_crudo(previas[pv])
        for c in CONTENT:
            dif = st["pct_llenas"][c] - ant["pct_llenas"][c]
            if abs(dif) >= SALTO_FORMATO_PP:
                avisos.append(f"{c}: {ant['pct_llenas'][c]:.1f}% -> {st['pct_llenas'][c]:.1f}% de filas llenas "
                              f"entre v{pv} y v{version} ({dif:+.1f} pp): posible cambio de formato en la fuente")
    return st, avisos


# ---------------------------------------------------------------------------- pasos
def al_dia(salidas, entradas):
    if not all(os.path.exists(p) for p in salidas):
        return False
    return min(os.path.getmtime(p) for p in salidas) >= max(os.path.getmtime(p) for p in entradas)


def paso(nombre, cmd, salidas, entradas, forzar=False):
    """Corre un script del pipeline salvo que sus salidas ya esten al dia."""
    if not forzar and al_dia(salidas, entradas):
        decir(f"[=] {nombre}: al dia")
        return
    decir(f"[>] {nombre}")
    t0 = datetime.now()
    # rutas relativas a la raiz, como al correrlos a mano: varios scripts guardan la ruta de entrada en su JSON
    cmd = [os.path.relpath(x, REPO).replace(os.sep, "/") if os.path.isabs(x) and x.startswith(REPO + os.sep) else x for x in cmd]
    correr([sys.executable] + cmd)
    faltan = [p for p in salidas if not os.path.exists(p)]
    if faltan:
        raise Fallo(f"{nombre}: no se genero {faltan[0]}")
    decir(f"    listo en {(datetime.now() - t0).seconds} s")


def correr(cmd, capturar=False, **entorno):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", **entorno)
    p = subprocess.run(cmd, cwd=REPO, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       encoding="utf-8", errors="replace")
    if LOG:
        LOG.write(p.stdout)
        LOG.flush()
    if p.returncode != 0:
        cola = "\n".join(p.stdout.strip().splitlines()[-15:])
        raise Fallo(f"fallo ({p.returncode}): {' '.join(map(str, cmd[:3]))} ...\n{cola}")
    return p.stdout if capturar else None


# ---------------------------------------------------------------------------- README
def actualizar_readme(txt, nn, v, datos, archivadas):
    """Arbol de carpetas y tabla de reportes del README para la tanda vN en la carpeta NN.

    datos: filas, requests, nuevas (del consolidado), corte_filas, corte_requests, r2 (publisher x pais).
    archivadas: [(numero de carpeta, version)] que pasan de reportes/ a reportes/old_reports/.
    La tanda que estaba como vigente queda resumida en una fila, con las cifras que ya traia.
    """
    if f"reporte-content-objects-detallado-v{v}-consolidado.md` | **Vigente:**" in txt:
        return txt
    if "\r\n" in txt:
        return actualizar_readme(txt.replace("\r\n", "\n"), nn, v, datos, archivadas).replace("\n", "\r\n")
    L = txt.split("\n")

    # --- tabla de reportes ---
    vig = [i for i, l in enumerate(L) if "| **Vigente:**" in l]
    if not vig:
        raise Fallo("README: no encuentro las filas **Vigente:** de la tabla de reportes")
    viejo = "\n".join(L[i] for i in vig)
    m = re.search(r"`reportes/(\d+)-\.\.\./.*?v10 a v(\d+) \(([\d,]+) filas, ([\d,]+) requests; "
                  r"v\d+ aporto ([\d,]+) combinaciones nuevas", viejo)
    r2 = re.search(r"explica el ([\d.]+) %", viejo)
    if not m or not r2:
        raise Fallo("README: no pude leer las cifras de la tanda vigente anterior")
    pn, pv, pf, pr, pnv = m.groups()
    nuevas = [
        f"| `reportes/{nn}-.../reporte-content-objects-detallado-v{v}-consolidado.md` | **Vigente:** content objects por pais "
        f"(MX/CO/CL) sobre el consolidado v10 a v{v} ({n(datos['filas'])} filas, {n(datos['requests'])} requests; v{v} aporto "
        f"{n(datos['nuevas'])} combinaciones nuevas; solo v{v}: {n(datos['corte_filas'])} filas, {n(datos['corte_requests'])} "
        "requests). Misma estructura que v19 |",
        f"| `reportes/{nn}-.../reporte-graficos-ecpm-vacio.md` | **Vigente:** las mismas graficas que v19 sobre v10-a-v{v} "
        f"(publisher x pais explica el {datos['r2']:.1f} % de la variacion del eCPM ponderado, en "
        "`recursos/reporte-drivers-ecpm-publisher-pais.md`) |",
        f"| `reportes/{nn}-.../reporte-completitud-content-objects-v{v}.md` | **Vigente:** que se puede completar de cada "
        f"content object sobre v10-a-v{v} (version completa en `recursos/reporte-completitud-content-objects-v{v}-completo.md`) |",
        f"| `reportes/{pn}-.../` | (v10-a-v{pv}) los mismos tres md sobre el consolidado v10 a v{pv} ({pf} filas, {pr} requests; "
        f"v{pv} aporto {pnv} combinaciones nuevas; publisher x pais explica el {r2.group(1)} %) |"]
    L = L[:vig[0]] + nuevas + [l for i, l in enumerate(L[vig[0]:], vig[0]) if i not in vig]

    # --- arbol de carpetas ---
    iv = next((i for i, l in enumerate(L) if re.match(r"^  \d+-consolidado-v10-a-v\d+/\s+la version vigente, ", l)), None)
    if iv is None:
        raise Fallo("README: no encuentro la linea 'la version vigente' del arbol de carpetas")
    resto = L[iv].split("la version vigente, ", 1)[1]
    L[iv:iv + 1] = [f"  {pn}-consolidado-v10-a-v{pv}/         tanda v10 a v{pv}, tres reportes md (misma estructura que {nn})",
                    f"  {nn}-consolidado-v10-a-v{v}/         la version vigente, {resto}"]
    for num, ver in archivadas:
        i = next((i for i, l in enumerate(L) if re.match(rf"^  {num}-consolidado-v10-a-v{ver}/", l)), None)
        if i is not None:
            texto = L.pop(i).split("/", 1)[1].strip()
            ult = max(j for j, l in enumerate(L) if re.match(r"^    \d\d-", l))
            L.insert(ult + 1, f"    {num}-consolidado-v10-a-v{ver}/       {texto}")
    txt = "\n".join(L)
    txt = re.sub(r"\(misma estructura que \d+\)", f"(misma estructura que {nn})", txt)
    for num, _ in archivadas:
        txt = txt.replace(f"`reportes/{num}-.../", f"`reportes/old_reports/{num}-.../")
    if archivadas:
        tope = max(ver for _, ver in archivadas)
        txt = re.sub(r"(old_reports/\s+tandas hasta )v\d+( \(v10 a )v\d+\)", rf"\g<1>v{tope}\g<2>v{tope})", txt)
    return txt


def readme_bigquery(txt, v, fecha, filas, requests):
    nuevo, k = re.subn(r"\(desde \d{4}-\d\d-\d\d, v\d+: [\d,]+ filas, [\d,]+ requests\)",
                       f"(desde {fecha}, v{v}: {n(filas)} filas, {n(requests)} requests)", txt)
    if not k:
        raise Fallo("README: no encuentro la linea del corte vigente en BigQuery")
    return nuevo


# ---------------------------------------------------------------------------- BigQuery
def bq(*args, capturar=False):
    exe = shutil.which("bq")
    if not exe:
        raise Fallo("no encuentro `bq` (Google Cloud SDK) en el PATH")
    # si existe la configuracion de gcloud de la cuenta de servicio se usa esa: el login personal caduca
    cfg = os.path.join(os.environ.get("CLOUDSDK_CONFIG") or os.path.join(os.environ.get("APPDATA", ""), "gcloud"),
                       "configurations", f"config_{BQ_GCLOUD_CONFIG}")
    entorno = {"CLOUDSDK_ACTIVE_CONFIG_NAME": BQ_GCLOUD_CONFIG} if os.path.exists(cfg) else {}
    return correr([exe, f"--project_id={BQ_PROYECTO}"] + list(args), capturar=capturar, **entorno)


def bq_cuenta(tabla):
    out = bq("--format=json", "query", "--use_legacy_sql=false",
             f"SELECT COUNT(*) AS filas, SUM(total_requests) AS requests FROM {tabla}", capturar=True)
    d = json.loads(out[out.index("["):])[0]
    return int(d["filas"]), int(d["requests"])


def cargar_bigquery(crudo, fecha, st, trabajo):
    """Carga el corte a una tabla temporal, la valida contra el CSV y solo entonces reemplaza la tabla de Looker."""
    looker = os.path.join(trabajo, "corte-looker.csv")
    temporal = BQ_TABLA + "_carga"
    correr([sys.executable, os.path.join(AQUI, "bigquery", "agregar_columnas_looker.py"), crudo, looker, fecha])
    try:
        bq("load", "--source_format=CSV", "--skip_leading_rows=1", "--allow_quoted_newlines", "--replace",
           temporal, looker, os.path.join(AQUI, "bigquery", "schema-crudo.json"))
        filas, req = bq_cuenta(temporal)
        if (filas, req) != (st["filas"], st["requests"]):
            raise Fallo(f"BigQuery: la carga trae {n(filas)} filas y {n(req)} requests; el CSV, {n(st['filas'])} y "
                        f"{n(st['requests'])}. La tabla de Looker no se toco.")
        bq("cp", "-f", temporal, BQ_TABLA)
    finally:
        try:
            bq("rm", "-f", "-t", temporal)
        except Fallo:
            pass
        if os.path.exists(looker):
            os.remove(looker)
    return filas, req


# ---------------------------------------------------------------------------- deals.db
def subir_deals(ruta):
    """Copia deals.db a la VM de la plataforma. Destino y llave salen del .env de la raiz:
    DEALS_DESTINO=usuario@host:/ruta/plataforma-etiquetado/data/deals.db y DEALS_LLAVE_SSH=ruta de la llave.
    Se sube con otro nombre y se renombra, para que el servidor nunca lea un archivo a medias."""
    cfg = {}
    env = os.path.join(REPO, ".env")
    if os.path.exists(env):
        for linea in open(env, encoding="utf-8-sig"):
            if "=" in linea and not linea.lstrip().startswith("#"):
                k, v = linea.strip().split("=", 1)
                cfg[k.strip()] = v.strip().strip('"')
    destino, llave = cfg.get("DEALS_DESTINO", ""), os.path.expanduser(cfg.get("DEALS_LLAVE_SSH", ""))
    if ":" not in destino or not llave:
        raise Fallo("faltan DEALS_DESTINO y DEALS_LLAVE_SSH en .env")
    host, remoto = destino.split(":", 1)
    ssh = ["-i", llave, "-o", "BatchMode=yes", "-o", "ConnectTimeout=20"]
    correr(["scp"] + ssh + [ruta, f"{host}:{remoto}.nuevo"])
    correr(["ssh"] + ssh + [host, f"mv -f '{remoto}.nuevo' '{remoto}'"])
    return destino


# ---------------------------------------------------------------------------- main
def main():
    global LOG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("crudo", nargs="?", help="CSV crudo de PubMatic (default: el de mayor version de la raiz)")
    ap.add_argument("--prueba", default="", help="carpeta aparte para todas las salidas; no archiva, ni toca README, BigQuery o git")
    ap.add_argument("--forzar", action="store_true", help="repetir los pasos aunque sus salidas esten al dia")
    ap.add_argument("--bigquery", action="store_true", help=f"recargar {BQ_TABLA} con el corte")
    ap.add_argument("--fecha-reporte", default="", help="fecha_reporte de BigQuery (default: fecha de descarga del CSV)")
    ap.add_argument("--deals", action="store_true", help="generar deals.db para la pestaña Deals de la plataforma y subirla a la VM")
    ap.add_argument("--commit", action="store_true", help="commit de reportes/ y README.md")
    ap.add_argument("--push", action="store_true", help="commit y push")
    ap.add_argument("--imdb-max-dias", type=int, default=7, help="se pasa a enriquecer_externo.py")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")  # la consola cp1252 no siempre puede con los titulos

    en_raiz = crudos(REPO)
    crudo = os.path.abspath(a.crudo) if a.crudo else (en_raiz[max(en_raiz)] if en_raiz else None)
    if not crudo or not os.path.exists(crudo):
        sys.exit("no hay CSV crudo que procesar")
    m = RE_CRUDO.match(os.path.basename(crudo))
    if not m:
        sys.exit(f"el nombre no tiene la forma esperada: {os.path.basename(crudo)}")
    V, sufijo, d1, d2 = int(m.group(1)), m.group(2), m.group(3), m.group(4)

    base = os.path.abspath(a.prueba) if a.prueba else REPO
    rep_dir = os.path.join(base, "reportes")
    logs = os.path.join(base, "logs")
    os.makedirs(logs, exist_ok=True)
    os.makedirs(rep_dir, exist_ok=True)
    LOG = open(os.path.join(logs, f"tanda-v{V}-{datetime.now():%Y%m%d-%H%M}.log"), "w", encoding="utf-8")
    decir(f"Tanda v{V} · ventana {ventana_texto(d1, d2)} · {os.path.basename(crudo)}")

    try:
        # carpeta de la tanda: la que ya exista para esta version o la siguiente numeracion
        reales = os.path.join(REPO, "reportes")
        numeradas = [x for d in (reales, os.path.join(reales, "old_reports")) if os.path.isdir(d) for x in os.listdir(d)]
        existente = next((x for x in os.listdir(reales) if RE_CARPETA.match(x) and int(RE_CARPETA.match(x).group(2)) == V), None)
        NN = (RE_CARPETA.match(existente).group(1) if existente else
              f"{max(int(x[:2]) for x in numeradas if x[:2].isdigit()) + 1:02d}")
        D = os.path.join(rep_dir, f"{NN}-consolidado-v10-a-v{V}-latam-content-objetcs-{sufijo}")
        R = os.path.join(D, "recursos")
        os.makedirs(R, exist_ok=True)

        # consolidado anterior: el de mayor version menor que V
        prev = {}
        for p in glob.glob(os.path.join(REPO, "inventory-consolidado-v10-a-v*.csv")):
            mm = re.match(r"^inventory-consolidado-v10-a-v(\d+)\.csv$", os.path.basename(p))
            if mm and int(mm.group(1)) < V:
                prev[int(mm.group(1))] = p
        if not prev:
            raise Fallo(f"no hay consolidado anterior a v{V} en la raiz", 2)
        PV = max(prev)

        decir("[>] verificar")
        st, avisos = verificar(crudo, V, d1, en_raiz)
        decir(f"    {n(st['filas'])} filas, {n(st['requests'])} requests")
        for x in avisos:
            decir(f"    AVISO: {x}")

        S = lambda s: os.path.join(AQUI, s)  # noqa: E731
        C = os.path.join(base, f"inventory-consolidado-v10-a-v{V}.csv")
        E = C[:-4] + "-enriquecido.csv"
        Lr = C[:-4] + "-relleno.csv"
        j_det = os.path.join(R, f"reporte-content-objects-detallado-v{V}-consolidado.json")
        j_vac = os.path.join(R, f"reporte-requests-ecpm-por-vacio-v{V}.json")
        j_rel = os.path.join(R, f"reporte-relleno-v{V}.json")
        cache = os.path.join(REPO, "cache-enriquecimiento")
        F = a.forzar

        paso("consolidar", [S("consolidar.py"), C, crudo, prev[PV]], [C], [crudo, prev[PV]], F)
        paso("detallado por pais (JSON)", [S("analizar.py"), C, j_det, "--grupos", PAISES], [j_det], [C], F)
        paso("requests y eCPM lleno/vacio (JSON)", [S("requests_ecpm_por_vacio.py"), C, j_vac, "--paises", PAISES], [j_vac], [C], F)
        paso("normalizar", [S("normalizar_monetizar.py"), C, E, os.path.join(logs, f"normalizacion-v{V}.json")], [E], [C], F)
        paso("relleno", [S("enriquecer_externo.py"), E, Lr, j_rel, "--cache-dir", cache, "--wikidata",
                         "--imdb-max-dias", str(a.imdb_max_dias)], [Lr, j_rel], [E], F)
        for nombre, script, entrada, extra, salida in [
                ("graficas: eCPM lleno/vacio", "generar_graficos_ecpm_vacio.py", j_vac, [], "graficos-ecpm-vacio-r2.json"),
                ("graficas: scatter completitud", "generar_scatter_completitud_ecpm.py", C, [], "graficos-ecpm-completitud-scatter.json"),
                ("graficas: drivers del eCPM", "generar_graficos_drivers_ecpm.py", C, [], "graficos-drivers-ecpm.json"),
                ("graficas: barras por app", "generar_barras_app_completitud.py", C, [], "graficos-app-completitud-barras.json"),
                ("graficas: titulos por App Name", "generar_tabla_pageurl_titulos.py", Lr, [], "titulos-appname.json"),
                ("graficas: canales", "generar_barras_canales_completitud.py", C, [], "graficos-canales-completitud-barras.json"),
                ("graficas: filas sin titulo", "generar_graficos_sin_titulo.py", E, [], "graficos-sin-titulo.json")]:
            paso(nombre, [S(script), entrada, R] + extra, [os.path.join(R, salida)], [entrada], F)
        val = {}
        for script, pref in (("validar_categorias.py", "validacion-categorias"), ("validar_genero_series.py", "validacion-genero-series")):
            for etiqueta, entrada in (("consolidado", C), ("relleno", Lr)):
                salida = os.path.join(R, f"{pref}-{etiqueta}")
                val[pref, etiqueta] = salida + ".json"
                paso(f"{pref} ({etiqueta})", [S(script), entrada, salida, "--nombre", etiqueta, "--cache-dir", cache, "--filas",
                                             os.path.join(base, f"{pref}-v{V}-{etiqueta}-filas.csv")], [salida + ".json"], [entrada], F)

        prev_filas = contar_filas(prev[PV])
        md_det = os.path.join(D, f"reporte-content-objects-detallado-v{V}-consolidado.md")
        md_gra = os.path.join(D, "reporte-graficos-ecpm-vacio.md")
        md_com = os.path.join(D, f"reporte-completitud-content-objects-v{V}.md")
        jsons = sorted(glob.glob(os.path.join(R, "*.json")))
        paso("md: detallado", [S("generar_reporte_detallado.py"), D, str(V), ventana_texto(d1, d2), "--corte", crudo,
                               "--prev-filas", str(prev_filas)], [md_det], [j_det, j_rel], F)
        paso("md: graficas", [S("generar_reporte_graficos.py"), D, str(V)], [md_gra], jsons, F)
        paso("md: completitud", [S("generar_reporte_completitud.py"), D, str(V), "--detallado", j_det, "--vacio", j_vac,
                                 "--relleno", j_rel, "--cat-consolidado", val["validacion-categorias", "consolidado"],
                                 "--cat-relleno", val["validacion-categorias", "relleno"],
                                 "--gs-consolidado", val["validacion-genero-series", "consolidado"],
                                 "--gs-relleno", val["validacion-genero-series", "relleno"]], [md_com],
             [j_det, j_vac, j_rel] + list(val.values()), F)

        det = json.load(open(j_det, encoding="utf-8"))
        datos = {"filas": det["filas"], "requests": det["total_requests"], "nuevas": det["filas"] - prev_filas,
                 "corte_filas": st["filas"], "corte_requests": st["requests"],
                 "r2": json.load(open(os.path.join(R, "graficos-drivers-ecpm.json"), encoding="utf-8"))["r2_publisher_pais_pct"]}
        decir(f"    consolidado v10-a-v{V}: {n(datos['filas'])} filas, {n(datos['requests'])} requests; "
              f"{n(datos['nuevas'])} combinaciones nuevas")

        if a.prueba:
            decir(f"PRUEBA terminada: {D}")
            return 0

        if a.deals:
            deals_db = os.path.join(REPO, "plataforma-etiquetado", "data", "deals.db")
            paso("base de deals (deals.db)", [S("exportar_deals_db.py"), "--salida", deals_db, "--relleno", Lr, "--corte", crudo],
                 [deals_db], [Lr, crudo], F)
            try:
                decir("[>] deals.db -> " + subir_deals(deals_db))
            except Fallo as e:   # la web sigue con la base anterior; no es motivo para tumbar la tanda
                avisos.append(f"deals.db no se subio: {e}")
                decir(f"    AVISO: {avisos[-1]}")

        # archivar: en reportes/ quedan la vigente y la anterior
        tandas = sorted((int(RE_CARPETA.match(x).group(2)), x) for x in os.listdir(reales) if RE_CARPETA.match(x))
        archivadas = []
        for ver, carpeta in tandas[:-2]:
            decir(f"[>] archivar {carpeta}")
            correr(["git", "mv", os.path.join("reportes", carpeta), os.path.join("reportes", "old_reports", carpeta)])
            archivadas.append((carpeta[:2], ver))
        # para el README cuentan todas las tandas ya archivadas (por si una corrida anterior se corto despues del git mv)
        en_old = [(x[:2], int(RE_CARPETA.match(x).group(2))) for x in os.listdir(os.path.join(reales, "old_reports")) if RE_CARPETA.match(x)]

        readme = os.path.join(REPO, "README.md")
        txt = open(readme, encoding="utf-8", newline="").read()
        nuevo = actualizar_readme(txt, NN, V, datos, en_old)
        mensaje = [f"Tanda v{V}: consolidado v10-a-v{V} ({n(datos['filas'])} filas), carpeta {NN} con los 3 md y recursos"]
        if archivadas:
            mensaje.append("carpeta " + ", ".join(f"{c} (v{v})" for c, v in archivadas) + " a reportes/old_reports")
        if a.bigquery:
            fecha = a.fecha_reporte or date.fromtimestamp(os.path.getmtime(crudo)).isoformat()
            if f"(desde {fecha}, v{V}: " in nuevo:
                decir("[=] BigQuery: al dia")
            else:
                decir(f"[>] BigQuery: {BQ_TABLA} con el corte v{V} (fecha_reporte {fecha})")
                filas, req = cargar_bigquery(crudo, fecha, st, logs)
                nuevo = readme_bigquery(nuevo, V, fecha, filas, req)
                mensaje.append(f"BigQuery recargada con el corte v{V} ({n(filas)} filas, {n(req)} requests, fecha_reporte {fecha})")
        if nuevo != txt:
            with open(readme, "w", encoding="utf-8", newline="") as f:
                f.write(nuevo)
            decir("[>] README actualizado")

        if a.commit or a.push:
            correr(["git", "add", "-A", "reportes", "README.md"])
            if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO).returncode:
                correr(["git", "commit", "-m", "; ".join(mensaje)])
                decir("[>] commit: " + "; ".join(mensaje))
            if a.push:
                # otra persona pudo haber subido cambios (la plataforma vive en el mismo repo)
                correr(["git", "pull", "--rebase", "--autostash"])
                correr(["git", "push"])
                decir("[>] push")
        decir(f"TANDA v{V} LISTA: {os.path.relpath(D, REPO)}" + (f" · {len(avisos)} aviso(s)" if avisos else ""))
        return 0
    except Fallo as e:
        decir(f"ERROR: {e}")
        return e.codigo


if __name__ == "__main__":
    sys.exit(main())
