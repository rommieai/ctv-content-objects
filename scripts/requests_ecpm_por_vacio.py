# -*- coding: utf-8 -*-
"""Por pais y por columna: requests y eCPM ponderado de las filas donde la columna viene
llena (dato util) y de las filas donde viene vacia (centinela, [-7], hash MD5 vacio).
Mismo criterio de "util" que analizar.py.

"requests" suma todas las filas del grupo. eCPM ponderado = sum(eCPM * requests) /
sum(requests) excluyendo las filas con requests = 0 o eCPM = 0 (misma convencion que el
resto de los reportes). pct_req_monetizado = requests de esas filas / requests del grupo.

Ademas de los paises pedidos emite el grupo "(todos)" con el total del dataset.

Uso:
    python requests_ecpm_por_vacio.py entrada.csv salida.json [--paises "Mexico,Colombia,Chile"]
"""
import argparse, csv, json, sys
from collections import defaultdict

SENTINELAS = {"not available", "not applicable", "unknown", "n/a", "null",
              "undefined", "none", "-", ""}
MD5_VACIO = "d41d8cd98f00b204e9800998ecf8427e"
COLUMNAS = ["App Name", "contentIsTitlePresent", "contentGenre", "contentTitle",
            "contentRating", "contentLanguage", "contentIsLiveStream", "contentCategory",
            "contentLength", "contentSeries"]

def util(col, v):
    s = v.strip()
    if s.lower() in SENTINELAS:
        return False
    if col == "contentCategory" and s == "[-7]":
        return False
    if col == "contentSeries" and s.lower() == MD5_VACIO:
        return False
    if col == "contentIsLiveStream" and s not in ("0", "1"):
        return False
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada"); ap.add_argument("salida_json")
    ap.add_argument("--paises", default="Mexico,Colombia,Chile")
    a = ap.parse_args()
    paises = ["(todos)"] + [p.strip() for p in a.paises.split(",")]
    csv.field_size_limit(10**9)
    # acc[pais][col][lleno/vacio] = [filas, req, sum_ecpm_req, req_no_cero]
    acc = {p: {c: {"lleno": [0, 0, 0.0, 0], "vacio": [0, 0, 0.0, 0]} for c in COLUMNAS} for p in paises}
    tot = {p: [0, 0] for p in paises}
    with open(a.entrada, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        for row in r:
            req = int(row["Total Requests"]); e = float(row["eCPM"])
            grupos = ["(todos)"] + ([row["Country"]] if row["Country"] in acc else [])
            for p in grupos:
                tot[p][0] += 1; tot[p][1] += req
                for c in COLUMNAS:
                    k = "lleno" if util(c, row[c]) else "vacio"
                    b = acc[p][c][k]
                    b[0] += 1; b[1] += req
                    if e > 0 and req > 0:
                        b[2] += e * req; b[3] += req
    out = {"fuente": a.entrada, "paises": {}}
    for p in paises:
        filas, reqs = tot[p]
        cols = {}
        for c in COLUMNAS:
            d = {}
            for k in ("lleno", "vacio"):
                n, rq, s, rnz = acc[p][c][k]
                d[k] = {"filas": n, "pct_filas": round(100 * n / filas, 2) if filas else 0,
                        "requests": rq, "pct_requests": round(100 * rq / reqs, 2) if reqs else 0,
                        "ecpm_ponderado": round(s / rnz, 3) if rnz else None,
                        "pct_req_monetizado": round(100 * rnz / rq, 2) if rq else None}
            cols[c] = d
        out["paises"][p] = {"filas": filas, "requests": reqs, "columnas": cols}
    json.dump(out, open(a.salida_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"-> {a.salida_json}")

if __name__ == "__main__":
    main()
