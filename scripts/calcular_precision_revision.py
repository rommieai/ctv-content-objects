# -*- coding: utf-8 -*-
"""Precision del relleno a partir de la revision manual (paso 2 de 2).

Lee uno o mas JSON exportados desde la pagina de revision (generar_muestra_revision.py, boton
"Exportar revision"). Cada item es un valor llenado (un codigo de categoria o un genero de una lista
cuentan por separado) con su veredicto: correcto | incorrecto |
no_se_sabe. Por estrato (columna x metodo de relleno, que el revisor no ve):
    precision = correctos / (correctos + incorrectos), con intervalo de Wilson al 95%
    no_se_sabe se reporta aparte (si son muchos, el estrato no se puede auditar a mano)
    requests probablemente mal = (1 - precision) x requests del estrato en el consolidado
Si hay varios revisores, la precision usa el primer veredicto de cada valor y aparte se reporta el
acuerdo entre revisores en los valores que revisaron dos o mas.

Escribe junto al primer archivo: revision-precision.json, revision-precision.md y
revision-incorrectos.csv (para la lista de titulos revisados del pipeline).

Uso:
    python scripts/calcular_precision_revision.py revision-manual-v22-ana-2026-10-02.json [otro-revisor.json ...]
"""
import csv
import json
import math
import os
import sys
from collections import Counter, defaultdict

NOMBRE = {"contentGenre": "Género", "contentCategory": "Categoría", "contentSeries": "Serie",
          "contentRating": "Clasificación por edad", "contentIsLiveStream": "En vivo / lineal",
          "contentLength": "Duración (código)", "contentCategory_afinado": "Categoría (código más específico agregado)",
          "_ficha_externa": "La ficha IMDb es la misma obra (pregunta opcional)"}
METODO = {"intra_titulo": "copiado de otra ruta del mismo título", "derivado_genero": "derivado del género",
          "derivado_tipo": "tipo película/serie de IMDb", "imdb": "IMDb", "wikidata": "Wikidata",
          "app_semantica": "semántica de la app", "genero_declarado": "género declarado por el vendedor"}


def wilson(ok, n, z=1.96):
    if n == 0:
        return None, None, None
    p = ok / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, centro - margen), min(1.0, centro + margen)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    archivos = sys.argv[1:]
    primero, por_valor, totales, version = {}, defaultdict(list), {}, None
    for ruta in archivos:
        d = json.load(open(ruta, encoding="utf-8"))
        if version and d["version"] != version:
            sys.exit(f"{ruta} es de otra muestra ({d['version']} != {version})")
        version, totales = d["version"], d["totales_estrato"]
        for it in d["items"]:
            if not it["veredicto"]:
                continue
            k = (it["id"], it["campo"], it["valor"])
            por_valor[k].append(it["veredicto"])
            primero.setdefault(k, {**it, "revisor": d.get("revisor", "")})
    cnt = defaultdict(Counter)
    pendientes = Counter()
    for ruta in archivos[:1]:
        for it in json.load(open(ruta, encoding="utf-8"))["items"]:
            if (it["id"], it["campo"], it["valor"]) not in primero:
                pendientes[it["estrato"]] += 1
    for it in primero.values():
        cnt[it["estrato"]][it["veredicto"]] += 1

    out, md = {}, ["| Campo | Método | Revisados | No se sabe | Pendientes | Precisión | IC 95% | Requests del estrato | Requests probablemente mal |",
                   "|---|---|---:|---:|---:|---:|---|---:|---:|"]
    pct = (lambda x: "—" if x is None else f"{100 * x:.0f}%")
    for e in sorted(set(cnt) | set(pendientes)):
        c = cnt[e]
        n = c["correcto"] + c["incorrecto"]
        p, lo, hi = wilson(c["correcto"], n)
        req = totales.get(e, {}).get("requests", 0)
        mal = round((1 - p) * req) if p is not None else None
        out[e] = {"revisados": n, "correctos": c["correcto"], "incorrectos": c["incorrecto"], "no_se_sabe": c["no_se_sabe"],
                  "pendientes": pendientes[e], "precision": p, "ic95": [lo, hi], "requests_estrato": req,
                  "requests_probablemente_mal": mal}
        campo, metodo = e.split("|") if "|" in e else (e, "")
        md.append(f"| {NOMBRE.get(campo, campo)} | {METODO.get(metodo, metodo)} | {n} | {c['no_se_sabe']} | {pendientes[e]} | "
                  f"{pct(p)} | {pct(lo)}–{pct(hi)} | {req:,} | {'—' if mal is None else f'{mal:,}'} |")
    dobles = [v for v in por_valor.values() if len(v) >= 2]
    acuerdo = sum(1 for v in dobles if v[0] == v[1]) / len(dobles) if dobles else None
    out["_acuerdo_entre_revisores"] = {"valores_con_2_revisiones": len(dobles), "acuerdo": acuerdo}
    md.append("")
    md.append(f"Acuerdo entre revisores: {pct(acuerdo)} en {len(dobles)} valores revisados por dos personas."
              if dobles else "Acuerdo entre revisores: no hay valores revisados por dos personas.")

    base = os.path.join(os.path.dirname(os.path.abspath(archivos[0])), "revision-")
    json.dump(out, open(base + "precision.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(base + "precision.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    malos = [it for it in primero.values() if it["veredicto"] == "incorrecto"]
    if malos:
        cols = ["id", "titulo", "app", "pais", "campo", "valor", "valor_correcto", "estrato", "nota", "revisor"]
        with open(base + "incorrectos.csv", "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(malos)
    print("\n".join(md))


if __name__ == "__main__":
    main()
