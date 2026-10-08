# -*- coding: utf-8 -*-
"""Bot que arma un Auction Package Deal en PubMatic Media Console (no hay acceso por API todavia).

Recorre el asistente Deals > Create Auction Package Deal con la cuenta del .env:

  Configuration  nombre, DSP y buyer (sin transaction fee, First Price, piso por defecto)
  Inventory      publishers en Maximum Reach, Media Type Video, plataforma CTV
  Targeting      pais en Geography y reglas de Content Object (valores escritos o CSV de titulos)
  Summary        captura de pantalla; sin --crear se detiene aqui y NO guarda nada

Con --crear da el clic en "Create Auction Package", guarda en logs/ lo que PubMatic respondio y,
salvo --dejar-activo, pone el deal en pausa.

Las reglas se pasan con --regla, una por regla; dentro de una regla las senales van separadas por
" & " (PubMatic las junta con AND):

    --regla "Title=@deals/genero-terror-mexico/Title_is-01.csv"      CSV (formato de compilar_deal.py)
    --regla "Genre=Horror,Terror"                                    valores escritos
    --regla "Series=friends & Episode=10"                            dos senales en la misma regla

Uso:
    python scripts/crear_deal_pubmatic.py --nombre test-bot-01 --pais Mexico --regla "Genre=Horror"
    python scripts/crear_deal_pubmatic.py ... --crear
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
from descargar_pubmatic import Fallo, abrir_lista, leer_env  # noqa: E402

BASE = "https://apps.pubmatic.com/v3/common/pmc"
LOGS = os.path.join(REPO, "logs")
LOG = None


def decir(msg):
    linea = f"{datetime.now():%H:%M:%S} {msg}"
    print(linea, flush=True)
    if LOG:
        LOG.write(linea + "\n")
        LOG.flush()


def pm(page, pm_id):
    return page.locator(f'[data-pm-id="{pm_id}"]')


def elegir(page, select_pm, buscar, opcion):
    """Abre un hls-select, busca y marca la opcion cuyo texto es `opcion`."""
    pm(page, select_pm).locator("hls-select-trigger").click()
    page.wait_for_timeout(1500)
    page.locator('input[placeholder="Search"]:visible').last.fill(buscar)
    page.wait_for_timeout(2500)
    op = page.locator("hls-select-list").get_by_text(opcion, exact=True)
    if not op.count():
        raise Fallo(f"no encuentro la opcion {opcion!r} en {select_pm}")
    op.first.click()
    page.wait_for_timeout(800)
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)


def siguiente(page, trozo_url):
    page.get_by_role("button", name="Next").click()
    for _ in range(120):   # la consola cambia de paso sin recargar: se espera a que cambie la direccion
        if trozo_url in page.url:
            break
        page.wait_for_timeout(500)
    else:
        raise Fallo(f"el asistente no avanzo a {trozo_url} (sigue en {page.url})")
    page.wait_for_timeout(5000)


def configuracion(page, nombre, dsp, buyer):
    page.goto(f"{BASE}/deal/create/general", wait_until="domcontentloaded")
    pm(page, "input-deal-name").locator("input").wait_for(state="visible", timeout=60000)
    page.wait_for_timeout(4000)
    pm(page, "input-deal-name").locator("input").fill(nombre)
    elegir(page, "dsp-select", dsp, dsp)
    elegir(page, "buyer-select", buyer, buyer)
    if "hls-radio-box-selected" not in (pm(page, "radio-transaction-fee-no").locator("label").get_attribute("class") or ""):
        pm(page, "radio-transaction-fee-no").locator("label").click()
    decir(f"configuracion: {nombre} · {dsp} · {buyer} · sin fee · First Price")


def inventario(page):
    siguiente(page, "/deal/create/inventory")
    # Banner y Desktop vienen marcados y los tiles son de seleccion multiple: se marca Video y CTV
    # (el tile de CTV se llama tile-native en la pagina) y se desmarcan los dos de fabrica.
    # Que quedo solo Video + CTV se comprueba despues, en el Summary.
    for tile in ("tile-video", "tile-native", "tile-banner", "tile-desktop"):
        pm(page, tile).click()
        page.wait_for_timeout(1500)
    decir("inventario: Maximum Reach · Video · CTV")


def geografia(page, pais):
    page.get_by_text("Geography", exact=True).first.click()
    page.wait_for_timeout(3000)
    page.locator('input[placeholder*="earch"]:visible').first.fill(pais)
    page.wait_for_timeout(3000)
    page.get_by_text(pais, exact=True).first.click()
    page.wait_for_timeout(2000)
    if pais not in texto(page).split("Selected")[-1]:
        raise Fallo(f"{pais} no quedo en la lista Selected de Geography")
    decir(f"geografia: {pais}")


def senal(page, nombre, valor, primera):
    """Llena el dialogo Add Rule / Add Content Signal con una senal y la guarda (en el formulario, no en PubMatic)."""
    if primera:
        page.get_by_text("Add Rule").last.click()
    else:
        page.get_by_text("Add Content Signal").last.click()
    page.wait_for_timeout(1500)
    page.get_by_text("Select...", exact=True).first.click()
    page.wait_for_timeout(1000)
    page.locator('input[placeholder="Search"]:visible').last.fill(nombre)
    page.wait_for_timeout(1500)
    page.get_by_text(nombre, exact=True).last.click()
    page.wait_for_timeout(1500)
    # Genre, Content Rating y Language abren un submenu: "Standardized Categories" (lista cerrada de
    # PubMatic) o "Manual Entry" (texto libre, lo que el publisher manda). El bot usa el texto libre.
    manual = page.get_by_text("Manual Entry", exact=True)
    if manual.count() and manual.first.is_visible():
        manual.first.click()
        page.wait_for_timeout(1500)
    if valor.startswith("@"):
        ruta = os.path.abspath(os.path.join(REPO, valor[1:]))
        page.get_by_text("Upload", exact=True).first.click()
        page.wait_for_timeout(1000)
        page.locator('input[type="file"]').set_input_files(ruta)
        page.wait_for_timeout(4000)
        detalle = f"CSV {os.path.basename(ruta)}"
    else:
        page.locator("textarea:visible").last.fill(valor)
        page.wait_for_timeout(800)
        detalle = valor[:60]
    guardar = page.get_by_role("button", name="Save").last
    if guardar.is_disabled():
        raise Fallo(f"PubMatic no acepta la senal {nombre} ({detalle}): el boton Save quedo deshabilitado")
    guardar.click()
    page.wait_for_timeout(2500)
    decir(f"  senal {nombre} is {detalle}")


def contenido(page, reglas):
    page.get_by_text("Content Object", exact=True).first.click()
    page.wait_for_timeout(3000)
    for i, regla in enumerate(reglas, 1):
        decir(f"regla {i}:")
        for k, parte in enumerate(regla.split(" & ")):
            nombre, valor = parte.split("=", 1)
            senal(page, nombre.strip(), valor.strip(), primera=(k == 0))


def fila_deal(page, nombre):
    """(fila, estado) del deal con ese nombre en la lista de deals."""
    page.goto(f"{BASE}/deals", wait_until="domcontentloaded")
    try:
        page.get_by_text(nombre, exact=True).first.wait_for(state="visible", timeout=60000)
    except Exception:
        raise Fallo(f"no encuentro el deal {nombre} en la lista")
    page.wait_for_timeout(3000)
    fila = page.locator("tbody tr").filter(has=page.get_by_text(nombre, exact=True))
    celdas = [c.strip() for c in fila.first.inner_text().split("\n") if c.strip()]
    estado = next((c for c in celdas if c in ("Live", "Active", "Paused", "Pending", "Draft", "Inactive", "Expired", "Completed")), "?")
    return fila.first, estado, celdas


def pausar(page, nombre):
    """Pausa el deal desde la lista: marca la fila, boton Pause y confirma en la ventana."""
    fila, estado, celdas = fila_deal(page, nombre)
    decir(f"estado al crear: {estado} · {' · '.join(celdas[:4])}")
    if estado == "Paused":
        return estado
    fila.locator('[data-pm-id="hls-tra-ckbx"] label').click()
    page.wait_for_timeout(1500)
    boton = pm(page, "hls-tba-action-button-Pause")
    if not boton.count():
        acciones = [b.inner_text().strip() for b in page.locator("hls-button-actions button").all()]
        raise Fallo(f"no aparece el boton Pause para {nombre} (acciones: {acciones}). PAUSARLO A MANO en Deals")
    boton.click()
    page.wait_for_timeout(1500)
    modal = pm(page, "pause-deal-modal")
    confirmar = modal.get_by_role("button").filter(has_text=re.compile(r"pause|confirm|yes|ok", re.I))
    if confirmar.count():
        confirmar.last.click()
    page.wait_for_timeout(5000)
    _, estado, _ = fila_deal(page, nombre)
    if estado != "Paused":
        raise Fallo(f"el deal {nombre} quedo en estado {estado} despues de pausar. PAUSARLO A MANO en Deals")
    decir(f"deal {nombre} en pausa")
    return estado


def texto(page):
    return " | ".join(l.strip() for l in page.inner_text("body").split("\n") if l.strip())


def main():
    global LOG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--dsp", default="DV360")
    ap.add_argument("--buyer", default="Ariadna Co DBM")
    ap.add_argument("--pais", default="Mexico")
    ap.add_argument("--regla", action="append", default=[], help='ej. "Genre=Horror" o "Title=@deals/x/Title_is-01.csv"')
    ap.add_argument("--crear", action="store_true", help="dar el clic en Create Auction Package (crea el deal real)")
    ap.add_argument("--pausar", action="store_true", help="no crea nada: solo pausa el deal --nombre que ya existe")
    ap.add_argument("--dejar-activo", action="store_true", help="con --crear, no pausar el deal recien creado")
    ap.add_argument("--con-ventana", action="store_true", help="mostrar el navegador")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")
    os.makedirs(LOGS, exist_ok=True)
    sello = f"{datetime.now():%Y%m%d-%H%M%S}"
    LOG = open(os.path.join(LOGS, f"deal-{a.nombre}-{sello}.log"), "w", encoding="utf-8")
    cap = lambda s: os.path.join(LOGS, f"deal-{a.nombre}-{s}.png")  # noqa: E731
    try:
        env = leer_env()
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            nav = pw.chromium.launch(headless=not a.con_ventana)
            page = nav.new_context(viewport={"width": 1600, "height": 1100}).new_page()
            llamadas = []
            page.context.on("response", lambda r: llamadas.append(r) if "/api/" in r.url and r.request.method in ("POST", "PUT", "PATCH", "DELETE") else None)
            try:
                abrir_lista(page, env)
                if a.pausar:
                    try:
                        pausar(page, a.nombre)
                    finally:
                        page.screenshot(path=cap("pausa"), full_page=True)
                    return 0
                configuracion(page, a.nombre, a.dsp, a.buyer)
                inventario(page)
                siguiente(page, "/deal/create/targeting")
                geografia(page, a.pais)
                contenido(page, a.regla)
                page.screenshot(path=cap("targeting"), full_page=True)
                decir("reglas como quedaron en pantalla: " + texto(page).split("define their values.")[-1].split("30 Day Projection")[0].strip(" |")[:900])
                siguiente(page, "/deal/create/summary")
                page.screenshot(path=cap("summary"), full_page=True)
                resumen = texto(page).split("One final review")[-1]
                decir("summary: " + resumen[:1500])
                if "Media Type | Video | Platform | CTV | Ad Sizes" not in resumen:
                    raise Fallo("el Summary no dice Media Type Video + Platform CTV solamente; no se crea")
                if not a.crear:
                    decir("recorrido completo SIN crear nada (falta --crear)")
                    return 0
                del llamadas[:]
                page.get_by_role("button", name="Create Auction Package").click()
                page.wait_for_url(re.compile(r"/pmc/deals/?(\?.*)?$"), timeout=120000)
                page.wait_for_timeout(8000)
                page.screenshot(path=cap("creado"), full_page=True)
                registro = []
                for r in llamadas:
                    try:
                        cuerpo = r.text()
                    except Exception:
                        cuerpo = ""
                    registro.append({"metodo": r.request.method, "url": r.url, "status": r.status,
                                     "envio": r.request.post_data, "respuesta": cuerpo[:200000]})
                with open(os.path.join(LOGS, f"deal-{a.nombre}-{sello}-api.json"), "w", encoding="utf-8") as f:
                    json.dump(registro, f, ensure_ascii=False, indent=1)
                for x in registro:
                    decir(f"  {x['metodo']} {x['status']} {x['url'].replace('https://apps.pubmatic.com', '')[:110]}")
                ids = [m.group(1) for x in registro for m in [re.search(r'"id"\s*:\s*(\d+)', x["respuesta"] or "")] if m and "curateddeals" in x["url"]]
                if ids:
                    decir(f"deal creado: {BASE}/deal/edit/{ids[0]}/summary")
                if a.dejar_activo:
                    _, estado, celdas = fila_deal(page, a.nombre)
                    decir(f"estado: {estado} · {' · '.join(celdas[:4])} (no se pauso: --dejar-activo)")
                else:
                    try:
                        pausar(page, a.nombre)
                    finally:
                        page.screenshot(path=cap("pausa"), full_page=True)
                return 0
            except Exception:
                try:
                    page.screenshot(path=cap("fallo"), full_page=True)
                except Exception:
                    pass
                raise
            finally:
                nav.close()
    except Fallo as e:
        decir(f"ERROR: {e}")
        return 1
    except Exception as e:
        decir(f"ERROR inesperado: {type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
