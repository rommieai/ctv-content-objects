# -*- coding: utf-8 -*-
"""Bot de descarga del CSV crudo desde PubMatic Media Console (no hay acceso por API todavia).

Replica lo que se hacia a mano en Analytics > Reports (Inventory Discovery Report):

  1. inicia sesion con PUBMATIC_USUARIO / PUBMATIC_CLAVE del archivo .env de la raiz;
  2. toma el reporte mas reciente cuyo nombre sea exactamente
     "inventory-source-alcance-ctv-vNN-latam-content-objetcs" (los demas reportes de la cuenta se ignoran), le da
     "..." > Copy, deja la configuracion tal cual, "Select Report Configuration", le pone el nombre
     con la version siguiente y "Save & Generate";
  3. espera (20-30 min) a que el reporte nuevo pase de Processing a Available;
  4. lo descarga a la raiz del repo con el nombre de siempre (60333-...-vN-...-<ventana>.csv);
  5. con --tanda, lanza scripts/correr_tanda.py sobre ese CSV (los argumentos que no reconoce se
     le pasan tal cual: --bigquery --commit --push).

La version N es la mayor de los CSV crudos de la raiz + 1 (no depende del nombre que tenga el
ultimo reporte en PubMatic). Si ya existe un reporte vN en PubMatic no crea otro: retoma la espera
y la descarga. Si el CSV vN ya esta en la raiz no hace nada.

Uso:
    python scripts/descargar_pubmatic.py --revisar           # solo entra y muestra que haria
    python scripts/descargar_pubmatic.py [--tanda --bigquery --commit --push]

Requiere `pip install playwright` y `python -m playwright install chromium`. Sale con 0 si todo paso y 1 si no;
el log y, si falla, una captura de pantalla quedan en logs/.
"""
import argparse
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from correr_tanda import RE_CRUDO, crudos  # noqa: E402

URL_LISTA = "https://apps.pubmatic.com/v3/analytics/inventory-discovery"
URL_LOGIN = "https://apps.pubmatic.com/login/demand?ref=https:%2F%2Fapps.pubmatic.com%2Fv3%2Fanalytics%2Finventory-discovery"
NOMBRE = "inventory-source-alcance-ctv-v{}-latam-content-objetcs"
FILTRO = "inventory-source-alcance-ctv-v"
RE_NOMBRE = re.compile(r"^inventory-source-alcance-ctv-v(\d+)-latam-content-objetcs$")
# lo que debe verse en el panel Summary antes de generar: la configuracion copiada ya cargo
RESUMEN_ESPERADO = ["CTV", "Video", "Country"]
EN_PROCESO = ("processing", "in progress", "queued", "pending")
LOGS = os.path.join(REPO, "logs")
LOG = None


class Fallo(Exception):
    pass


def decir(msg):
    linea = f"{datetime.now():%H:%M:%S} {msg}"
    print(linea, flush=True)
    if LOG:
        LOG.write(linea + "\n")
        LOG.flush()


def leer_env():
    ruta = os.path.join(REPO, ".env")
    if not os.path.exists(ruta):
        raise Fallo("falta el archivo .env en la raiz (copiar .env.example y llenarlo)")
    env = {}
    for linea in open(ruta, encoding="utf-8-sig"):
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            k, v = linea.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    if not env.get("PUBMATIC_USUARIO") or not env.get("PUBMATIC_CLAVE"):
        raise Fallo(".env no trae PUBMATIC_USUARIO y PUBMATIC_CLAVE")
    return env


def abrir_lista(page, env):
    """Va a la lista de reportes; si PubMatic manda al login, inicia sesion."""
    page.goto(URL_LISTA, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    if "/login" in page.url:
        decir("iniciando sesion")
        # sin sesion PubMatic manda al login de publisher; la cuenta es de Media Console (demand)
        page.goto(URL_LOGIN, wait_until="domcontentloaded")
        clave = page.locator("#okta-signin-password")
        clave.wait_for(state="visible", timeout=30000)
        page.locator("#okta-signin-username").fill(env["PUBMATIC_USUARIO"])
        clave.fill(env["PUBMATIC_CLAVE"])
        page.locator("#okta-signin-submit").click()
        try:
            page.wait_for_url(lambda u: "/login" not in u, timeout=60000)
        except Exception:
            aviso = page.locator(".okta-form-infobox-error, .o-form-error-container").first
            detalle = aviso.inner_text().strip() if aviso.count() else "¿clave vencida, captcha o codigo de verificacion?"
            raise Fallo(f"el login no paso: {detalle}")
        page.goto(URL_LISTA, wait_until="domcontentloaded")
    page.locator("tbody tr td.report-name a").first.wait_for(state="visible", timeout=60000)
    # la cuenta tiene otros reportes y la lista pagina de a 10: dejar a la vista solo los de la serie
    page.locator('input[placeholder="Search reports"]:visible').first.fill(FILTRO)
    page.wait_for_timeout(3000)
    page.locator("tbody tr td.report-name a").first.wait_for(state="visible", timeout=60000)


def filas(page):
    """[(nombre, estado, ultima actualizacion, locator de la fila)] en el orden de la lista (mas reciente primero)."""
    out = []
    trs = page.locator("tbody tr")
    for i in range(trs.count()):
        tr = trs.nth(i)
        if not tr.locator("td.report-name").count():
            continue
        out.append((tr.locator("td.report-name").inner_text().strip(), tr.locator("td.report-status").inner_text().strip(),
                    tr.locator("td.report-modification-time").inner_text().strip(), tr))
    return out


def buscar(page, nombre):
    return next((f for f in filas(page) if f[0] == nombre), None)


def horas_desde(texto):
    try:
        return (datetime.now() - datetime.strptime(texto, "%m/%d/%Y %I:%M %p")).total_seconds() / 3600
    except ValueError:
        return None


def generar(page, origen, nombre_nuevo):
    """Copy del reporte `origen` (fila), sin tocar la configuracion, con el nombre nuevo."""
    nombre_origen, _, _, tr = origen
    decir(f"copiando {nombre_origen} -> {nombre_nuevo}")
    tr.locator('[data-pm-id="report-actions-dropdown"]').click()
    page.get_by_text("Copy", exact=True).click()
    page.wait_for_url("**/inventory-discovery/create/**", timeout=60000)
    # la configuracion copiada tarda en cargar: no avanzar hasta verla completa en el panel Summary
    for texto in RESUMEN_ESPERADO:
        page.get_by_text(texto, exact=True).first.wait_for(state="visible", timeout=120000)
    page.wait_for_timeout(5000)  # (no sirve esperar "networkidle": la pagina nunca deja de hacer peticiones)
    page.get_by_role("button", name="Select Report Configuration").click()
    campo = page.locator('input[maxlength="120"]')
    campo.wait_for(state="visible", timeout=30000)
    if campo.input_value().strip() != f"Copy of {nombre_origen}":
        raise Fallo(f"el nombre propuesto no es el esperado: {campo.input_value()!r}")
    campo.fill(nombre_nuevo)
    page.get_by_role("button", name="Save & Generate").click()
    page.wait_for_url(re.compile(r"/inventory-discovery/?(\?.*)?$"), timeout=120000)
    page.get_by_text("Report saved successfully").wait_for(state="visible", timeout=60000)


def esperar_disponible(page, env, nombre, minutos):
    limite = datetime.now().timestamp() + minutos * 60
    while True:
        f = buscar(page, nombre)
        estado = f[1] if f else "(no aparece)"
        if estado.lower() == "available":
            return f
        if not f or estado.lower() not in EN_PROCESO:
            raise Fallo(f"{nombre} quedo en estado {estado!r}")
        if datetime.now().timestamp() > limite:
            raise Fallo(f"{nombre} sigue en {estado} despues de {minutos} min")
        decir(f"{estado}; reviso de nuevo en 1 min")
        page.wait_for_timeout(60000)
        abrir_lista(page, env)


def descargar(page, fila, version):
    # El boton abre una pestana emergente hacia /artifact/download/<id>?pte=<token>. No se usa la descarga
    # del navegador (la emergente se cierra antes de poder guardarla): se toma esa URL y se baja con la
    # misma sesion.
    urls = []
    page.context.on("request", lambda r: urls.append(r.url) if "/artifact/download/" in r.url else None)
    fila[3].locator('button[data-pm-id^="report-Download"]').click()
    for _ in range(120):
        if urls:
            break
        page.wait_for_timeout(500)
    if not urls:
        raise Fallo("el boton de descarga no pidio el archivo")
    resp = page.context.request.get(urls[0], timeout=900000)
    m = re.search(r'filename="?([^";]+)', resp.headers.get("content-disposition", ""))
    if not resp.ok or not m:
        raise Fallo(f"la descarga respondio {resp.status} sin archivo adjunto")
    sugerido = os.path.basename(m.group(1)).replace(":", "_")  # T00:00 -> T00_00, como lo guarda el navegador
    temporal = os.path.join(LOGS, sugerido)
    with open(temporal, "wb") as f:
        f.write(resp.body())
    if sugerido.lower().endswith(".zip"):
        with zipfile.ZipFile(temporal) as z:
            dentro = [x for x in z.namelist() if x.lower().endswith(".csv")]
            if len(dentro) != 1:
                raise Fallo(f"el zip {sugerido} no trae un unico CSV: {z.namelist()}")
            z.extract(dentro[0], LOGS)
        os.remove(temporal)
        sugerido, temporal = os.path.basename(dentro[0]), os.path.join(LOGS, dentro[0])
    m = RE_CRUDO.match(sugerido)
    if not m:
        raise Fallo(f"el archivo descargado no tiene el nombre esperado; quedo en logs/{sugerido}")
    # la version del nombre es la del repo, aunque el reporte se llame distinto en PubMatic
    final = os.path.join(REPO, re.sub(r"-ctv-v\d+-", f"-ctv-v{version}-", sugerido, count=1))
    os.replace(temporal, final)
    decir(f"descargado: {os.path.basename(final)} ({os.path.getsize(final) / 1e6:.1f} MB)")
    return final


def main():
    global LOG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--revisar", action="store_true", help="solo entra, lista los reportes y dice que haria")
    ap.add_argument("--version", type=int, default=0, help="version a generar (default: la mayor de la raiz + 1)")
    ap.add_argument("--espera-min", type=int, default=90, help="minutos maximos esperando a que quede Available")
    ap.add_argument("--min-horas", type=float, default=24, help="no copiar si el ultimo reporte de la serie tiene menos de "
                    "estas horas y no es la version buscada (evita generar dos veces el mismo corte)")
    ap.add_argument("--headless", action="store_true", help="sin ventana (por defecto se ve el navegador)")
    ap.add_argument("--tanda", action="store_true", help="al terminar, correr_tanda.py sobre el CSV (con los argumentos de sobra)")
    a, extra = ap.parse_known_args()
    sys.stdout.reconfigure(errors="replace")
    os.makedirs(LOGS, exist_ok=True)

    en_raiz = crudos(REPO)
    V = a.version or (max(en_raiz) + 1 if en_raiz else 0)
    if not V:
        sys.exit("no hay CSV crudos en la raiz para calcular la version; usar --version")
    LOG = open(os.path.join(LOGS, f"descarga-v{V}-{datetime.now():%Y%m%d-%H%M}.log"), "w", encoding="utf-8")
    nombre = NOMBRE.format(V)
    final = en_raiz.get(V)
    page = ctx = None
    try:
        if final:
            decir(f"el CSV v{V} ya esta en la raiz: {os.path.basename(final)}")
        else:
            env = leer_env()
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                # Chromium de Playwright (con el Chrome instalado el navegador se cerraba al descargar)
                ctx = pw.chromium.launch(headless=a.headless).new_context(viewport={"width": 1600, "height": 900})
                page = ctx.new_page()
                try:
                    abrir_lista(page, env)
                    lista = filas(page)
                    # solo cuentan los reportes de la serie (nombre exacto); el mas reciente es el que se copia
                    serie = [f for f in lista if RE_NOMBRE.match(f[0])]
                    serie.sort(key=lambda f: horas_desde(f[2]) if horas_desde(f[2]) is not None else 1e9)
                    for f in lista:
                        decir(f"  {f[2]:<20} {f[1]:<12} {f[0]}")
                    if not serie:
                        raise Fallo("no encuentro reportes inventory-source-alcance-ctv-vNN-latam-content-objetcs en la lista")
                    existente = buscar(page, nombre)
                    if existente:
                        decir(f"{nombre} ya existe en PubMatic ({existente[1]}); no se copia")
                    else:
                        h = horas_desde(serie[0][2])
                        if h is not None and h < a.min_horas and serie[0][0] == NOMBRE.format(V - 1) and V - 1 in en_raiz:
                            # el corte de hoy ya se genero y se descargo: no toca generar otro (relanzar tras un fallo)
                            decir(f"{serie[0][0]} tiene {h:.0f} h y su CSV ya esta en la raiz: no se genera v{V}")
                            final = en_raiz[V - 1]
                        elif h is not None and h < a.min_horas:
                            raise Fallo(f"el ultimo reporte de la serie ({serie[0][0]}, {serie[0][2]}) tiene {h:.0f} h y no se llama "
                                        f"{nombre}: parece el mismo corte con otro nombre. Renombrar, o usar --min-horas 0 para copiar igual")
                        else:
                            decir(f"se copia {serie[0][0]} ({serie[0][2]}) como {nombre}")
                    if a.revisar:
                        decir("solo revision: no se genero ni descargo nada")
                        return 0
                    if final:
                        pass
                    elif not existente:
                        origen = serie[0]
                        if origen[1].lower() != "available":
                            decir(f"{origen[0]} todavia esta en {origen[1]}; espero a que termine antes de copiarlo")
                            origen = esperar_disponible(page, env, origen[0], a.espera_min)
                        generar(page, origen, nombre)
                        abrir_lista(page, env)
                        if not buscar(page, nombre):
                            raise Fallo(f"despues de Save & Generate no aparece {nombre} en la lista")
                    if not final:
                        fila = esperar_disponible(page, env, nombre, a.espera_min)
                        final = descargar(page, fila, V)
                except Exception:
                    try:
                        page.screenshot(path=os.path.join(LOGS, f"descarga-v{V}-fallo.png"))
                    except Exception:
                        pass
                    raise
                finally:
                    ctx.browser.close()
        if a.tanda:
            decir("lanzando correr_tanda.py " + " ".join(extra))
            return subprocess.run([sys.executable, os.path.join(AQUI, "correr_tanda.py"), final] + extra, cwd=REPO).returncode
        return 0
    except Fallo as e:
        decir(f"ERROR: {e}")
        return 1
    except Exception as e:  # fallos de Playwright (timeouts, selectores): que queden en el log
        decir(f"ERROR inesperado: {type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
