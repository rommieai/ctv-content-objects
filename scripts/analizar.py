# -*- coding: utf-8 -*-
"""Analisis exploratorio del reporte de inventory source CTV (content objects + eCPM).

Para cada columna calcula: valores distintos (totales y utiles), fill rate por filas
y por requests, y la distribucion de valores (completa si hay <= 40 distintos, top-30
si hay mas). Para las columnas numericas (Total Requests, eCPM) calcula estadisticos.
Luego repite el desglose agrupando por una dimension (pais, publisher, etc.).

Un valor se considera "util" cuando no es centinela (Not Available, Not Applicable,
Unknown, N/A, null, none, undefined, vacio) ni basura equivalente a vacio:
`[-7]` en contentCategory, el hash MD5 de cadena vacia en contentSeries.

Uso:
    python analizar.py entrada.csv salida.json [--por Country] \
        [--grupos "Mexico,Colombia,Chile"] [--top-grupos 12] [--digest carpeta]

--por         dimension de desglose (default: Country; ej. Publisher, pageURL)
--grupos      lista explicita de valores a incluir (separados por coma)
--top-grupos  limitar a los N grupos con mas requests (0 = todos)
--digest      carpeta para resumenes en texto plano (digest_global.txt, digest_grupos.txt)
"""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict

SENTINELAS = {"not available", "not applicable", "unknown", "n/a", "null",
              "undefined", "none", "-", ""}
MD5_VACIO = "d41d8cd98f00b204e9800998ecf8427e"
CATEGORICAS = ["Publisher ID", "Publisher", "pageURL", "App Name", "Country",
               "contentGenre", "contentCategory", "contentSeries",
               "contentIsTitlePresent", "contentLength", "contentLanguage",
               "contentIsLiveStream", "contentTitle", "contentRating"]
DIST_COMPLETA_HASTA = 40   # si hay mas valores distintos que esto, se emite top-30
TOP_N = 30
TOP_GRUPO = 15
BUCKETS_ECPM = [("0", lambda e: e == 0), ("0-1", lambda e: 0 < e < 1),
                ("1-3", lambda e: 1 <= e < 3), ("3-5", lambda e: 3 <= e < 5),
                ("5-10", lambda e: 5 <= e < 10), ("10-20", lambda e: 10 <= e < 20),
                (">=20", lambda e: e >= 20)]


def es_util(col, valor):
    v = valor.strip()
    if v.lower() in SENTINELAS:
        return False
    if col == "contentSeries" and v == MD5_VACIO:
        return False
    if col == "contentCategory" and v in ("[-7]", "[]", "[-1]"):
        return False
    return True


def pct(n, d):
    return round(100.0 * n / d, 2) if d else 0.0


def percentil(orden, p):
    if not orden:
        return None
    k = (len(orden) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return orden[int(k)]
    return orden[f] + (orden[c] - orden[f]) * (k - f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida_json")
    ap.add_argument("--por", default="Country",
                    help="dimension de desglose (default: Country)")
    ap.add_argument("--grupos", default="",
                    help="lista de valores a incluir, separados por coma; vacio = todos")
    ap.add_argument("--top-grupos", type=int, default=0,
                    help="limitar a los N grupos con mas requests (0 = todos)")
    ap.add_argument("--digest", default="", help="carpeta para los digests de texto")
    args = ap.parse_args()
    filtro = {g.strip() for g in args.grupos.split(",") if g.strip()}

    filas = 0
    total_req = 0
    val_filas = {c: Counter() for c in CATEGORICAS}
    val_reqs = {c: Counter() for c in CATEGORICAS}
    grupos = defaultdict(lambda: {"filas": 0, "req": 0,
                                  "cols": {c: Counter() for c in CATEGORICAS},
                                  "util": {c: [0, 0] for c in CATEGORICAS},
                                  "e0": 0, "e_nz_sum": 0.0, "e_nz_n": 0,
                                  "e_w": 0.0, "req_w": 0})
    lista_reqs = []
    lista_ecpm = []
    e0 = 0; e_nz_sum = 0.0; e_nz_n = 0; e_w = 0.0; req_w = 0
    b_filas = Counter(); b_reqs = Counter()

    with open(args.entrada, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        cols = next(reader)
        idx = {c: i for i, c in enumerate(cols)}
        if args.por not in idx:
            raise SystemExit(f"La columna '{args.por}' no existe en el CSV")
        for row in reader:
            if len(row) != len(cols):
                continue
            filas += 1
            try:
                req = int(row[idx["Total Requests"]])
            except ValueError:
                req = 0
            try:
                e = float(row[idx["eCPM"]])
            except ValueError:
                e = None
            total_req += req
            lista_reqs.append(req)
            grupo = row[idx[args.por]].strip()
            G = grupos[grupo]
            G["filas"] += 1; G["req"] += req
            if e is not None:
                lista_ecpm.append(e)
                if e == 0:
                    e0 += 1; G["e0"] += 1
                else:
                    e_nz_sum += e; e_nz_n += 1
                    G["e_nz_sum"] += e; G["e_nz_n"] += 1
                    if req > 0:
                        e_w += e * req; req_w += req
                        G["e_w"] += e * req; G["req_w"] += req
                for nombre, cond in BUCKETS_ECPM:
                    if cond(e):
                        b_filas[nombre] += 1; b_reqs[nombre] += req
                        break
            for c in CATEGORICAS:
                v_raw = row[idx[c]].strip()
                v = v_raw or "(vacio)"
                val_filas[c][v] += 1
                val_reqs[c][v] += req
                G["cols"][c][v] += 1
                if es_util(c, v_raw):
                    u = G["util"][c]
                    u[0] += 1
                    u[1] += req

    res = {"archivo": args.entrada.split("\\")[-1], "filas": filas,
           "total_requests": total_req, "columnas": {},
           "dimension_grupos": args.por, "grupos": {}}

    for c in CATEGORICAS:
        vc, vq = val_filas[c], val_reqs[c]
        utiles = [v for v in vc if es_util(c, v if v != "(vacio)" else "")]
        filas_utiles = sum(vc[v] for v in utiles)
        req_utiles = sum(vq[v] for v in utiles)
        items = vc.most_common() if len(vc) <= DIST_COMPLETA_HASTA else vc.most_common(TOP_N)
        res["columnas"][c] = {
            "valores_distintos_totales": len(vc),
            "valores_distintos_utiles": len(utiles),
            "fill_rate_filas_pct": pct(filas_utiles, filas),
            "fill_rate_requests_pct": pct(req_utiles, total_req),
            "distribucion": [[v, n, pct(n, filas), vq[v], pct(vq[v], total_req)]
                             for v, n in items],
            "distribucion_es_completa": len(vc) <= DIST_COMPLETA_HASTA,
            "otras_filas": filas - sum(n for _, n in items),
        }

    lista_reqs.sort(); lista_ecpm.sort()
    nz = [e for e in lista_ecpm if e > 0]
    top1 = sum(sorted(lista_reqs, reverse=True)[:max(1, filas // 100)])
    res["columnas"]["Total Requests"] = {
        "tipo": "numerica", "min": lista_reqs[0], "max": lista_reqs[-1],
        "media": round(sum(lista_reqs) / filas, 1), "mediana": percentil(lista_reqs, .5),
        "p75": percentil(lista_reqs, .75), "p90": percentil(lista_reqs, .90),
        "p99": percentil(lista_reqs, .99),
        "share_requests_top1pct_filas": pct(top1, total_req)}
    res["columnas"]["eCPM"] = {
        "tipo": "numerica", "filas_cero": e0, "pct_filas_cero": pct(e0, filas),
        "filas_no_cero": e_nz_n,
        "media_no_cero": round(e_nz_sum / e_nz_n, 3) if e_nz_n else None,
        "mediana_no_cero": round(percentil(nz, .5), 3) if nz else None,
        "p90_no_cero": round(percentil(nz, .9), 3) if nz else None,
        "max": lista_ecpm[-1] if lista_ecpm else None,
        "ecpm_ponderado_por_requests": round(e_w / req_w, 3) if req_w else None,
        "buckets_filas": dict(b_filas), "buckets_requests": dict(b_reqs)}

    orden = sorted(grupos.items(), key=lambda kv: -kv[1]["req"])
    incluidos = 0
    for grupo, G in orden:
        if filtro and grupo not in filtro:
            continue
        if args.top_grupos and incluidos >= args.top_grupos:
            break
        incluidos += 1
        entrada = {"filas": G["filas"], "pct_filas": pct(G["filas"], filas),
                   "requests": G["req"], "pct_requests": pct(G["req"], total_req),
                   "ecpm": {"pct_filas_cero": pct(G["e0"], G["filas"]),
                            "media_no_cero": round(G["e_nz_sum"] / G["e_nz_n"], 3) if G["e_nz_n"] else None,
                            "ponderado_requests": round(G["e_w"] / G["req_w"], 3) if G["req_w"] else None},
                   "columnas": {}}
        for c in CATEGORICAS:
            if c == args.por:
                continue
            vc = G["cols"][c]
            u_filas, u_req = G["util"][c]
            entrada["columnas"][c] = {
                "valores_distintos": len(vc),
                "filas_utiles": u_filas,
                "requests_utiles": u_req,
                "fill_rate_pct": pct(u_filas, G["filas"]),
                "fill_rate_requests_pct": pct(u_req, G["req"]),
                "top": [[v, n, pct(n, G["filas"])] for v, n in vc.most_common(TOP_GRUPO)]}
        res["grupos"][grupo] = entrada

    with open(args.salida_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"filas={filas:,} requests={total_req:,} grupos={len(res['grupos'])} "
          f"(por {args.por}) -> {args.salida_json}")

    if args.digest:
        with open(args.digest + r"\digest_global.txt", "w", encoding="utf-8") as g:
            g.write(f"FILAS {filas} REQUESTS {total_req}\n\n")
            for c in CATEGORICAS:
                col = res["columnas"][c]
                g.write(f"### {c} | distintos={col['valores_distintos_totales']} "
                        f"utiles={col['valores_distintos_utiles']} "
                        f"fill_filas={col['fill_rate_filas_pct']}% "
                        f"fill_reqs={col['fill_rate_requests_pct']}%\n")
                for v, n, p, q, pq in col["distribucion"]:
                    g.write(f"  {v[:55]:55s} {n:8d} filas {p:6.2f}% | {pq:5.2f}% reqs\n")
                if not col["distribucion_es_completa"]:
                    g.write(f"  ...otras: {col['otras_filas']} filas\n")
                g.write("\n")
            g.write("### Total Requests %s\n" % json.dumps(res["columnas"]["Total Requests"]))
            g.write("### eCPM %s\n" % json.dumps(res["columnas"]["eCPM"]))
        with open(args.digest + r"\digest_grupos.txt", "w", encoding="utf-8") as g:
            for grupo, ge in res["grupos"].items():
                g.write(f"== {grupo} | filas={ge['filas']} ({ge['pct_filas']}%) "
                        f"reqs={ge['requests']} ({ge['pct_requests']}%) "
                        f"ecpm0={ge['ecpm']['pct_filas_cero']}% "
                        f"avg_nz={ge['ecpm']['media_no_cero']} wtd={ge['ecpm']['ponderado_requests']}\n")
                for c in CATEGORICAS:
                    if c == args.por:
                        continue
                    cc = ge["columnas"][c]
                    tops = ", ".join(f"{v[:28]} {p:.1f}%" for v, n, p in cc["top"][:5])
                    g.write(f"   {c:20s} d={cc['valores_distintos']:<5d} "
                            f"fill={cc['fill_rate_pct']:5.1f}% "
                            f"futil={cc['filas_utiles']} rutil={cc['requests_utiles']} | {tops}\n")
                g.write("\n")
        print("digests escritos en", args.digest)


if __name__ == "__main__":
    main()
