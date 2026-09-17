# -*- coding: utf-8 -*-
"""Por titulo: en cuantos pageURL (apps), rutas de venta (publishers), emisores y paises aparece.

El publisher es la ruta de venta (SSP); el pageURL es la app que emite. Un mismo emisor tiene
varios pageURL (uno por tienda o plataforma), asi que se agrupan en "emisor" por el App Name
con una tabla de patrones (EMISOR_PATRONES) ampliable a mano.

Escribe en la carpeta de salida:
    pageurl-emisores.csv       top pageURL por requests: pageURL, App Name, emisor, publishers, requests
    titulos-pageurl.json       distribucion de titulos por numero de pageURL/emisores y top titulos

Uso:
    python scripts/generar_tabla_pageurl_titulos.py inventory-consolidado-relleno.csv reportes/NN/recursos [--top 200]
(usa el CSV de relleno porque trae titulo_clave; el consolidado crudo no)
"""
import argparse
import csv
import json
import os
from collections import Counter, defaultdict

EMISOR_PATRONES = [("vix", "ViX"), ("univision", "ViX"), ("prendetv", "ViX"), ("azteca", "TV Azteca"),
                   ("roku", "Roku"), ("pluto", "Pluto TV"), ("tubi", "Tubi"), ("plex", "Plex"), ("xumo", "Xumo"),
                   ("lg channels", "LG Channels"), ("samsung", "Samsung TV Plus"), ("vidaa", "Vidaa"),
                   ("whalelive", "Zeasn (WhaleLive)"), ("zeasn", "Zeasn (WhaleLive)"), ("caracol", "Caracol"),
                   ("movieark", "OTTera (pool FAST)"), ("ottera", "OTTera (pool FAST)"), ("freetube", "OTTera (pool FAST)"),
                   ("browsefree", "OTTera (pool FAST)"), ("browsehere", "OTTera (pool FAST)"), ("coolita", "OTTera (pool FAST)"),
                   ("live tv", "OTTera (pool FAST)"), ("tcl", "TCL"), ("google tv", "Google TV"), ("filmrise", "FilmRise")]


def emisor(app, url):
    s = (app or "").lower() + " " + (url or "").lower()
    for pat, nombre in EMISOR_PATRONES:
        if pat in s:
            return nombre
    return app if app and app.lower() != "not available" else "(App Name vacío)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida_dir")
    ap.add_argument("--top", type=int, default=200)
    a = ap.parse_args()
    csv.field_size_limit(10 ** 9)
    url_req, url_app, url_pubs = Counter(), {}, defaultdict(set)
    t_urls, t_pubs, t_paises, t_em, t_req = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(set), Counter()
    t_em_req = defaultdict(Counter)
    with open(a.entrada, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            q = int(r["Total Requests"])
            url = (r["pageURL"] or "").strip().lower() or "(vacío)"
            app = (r["App Name"] or "").strip()
            url_req[url] += q
            url_app.setdefault(url, app)
            url_pubs[url].add(r["Publisher"])
            k = r.get("titulo_clave")
            if not k:
                continue
            em = emisor(app, url)
            t_urls[k].add(url)
            t_pubs[k].add(r["Publisher"])
            t_paises[k].add(r["Country"])
            t_em[k].add(em)
            t_req[k] += q
            t_em_req[k][em] += q
    # tabla pageURL -> emisor
    with open(os.path.join(a.salida_dir, "pageurl-emisores.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pageURL", "App Name", "emisor", "publishers", "n_publishers", "requests"])
        for url, q in url_req.most_common(a.top):
            w.writerow([url, url_app[url], emisor(url_app[url], url), " | ".join(sorted(url_pubs[url])), len(url_pubs[url]), q])
    n = len(t_urls)
    tot_req = sum(t_req.values())

    def dist(d):
        c = Counter(min(len(v), 5) for v in d.values())
        rq = defaultdict(int)
        for k, v in d.items():
            rq[min(len(v), 5)] += t_req[k]
        return [{"n": ("5+" if i == 5 else str(i)), "titulos": c[i], "pct_titulos": round(100 * c[i] / n, 1),
                 "pct_requests": round(100 * rq[i] / tot_req, 1)} for i in range(1, 6)]
    top = sorted((k for k in t_urls if len(t_em[k]) >= 2), key=lambda k: -t_req[k])[:15]
    out = {"fuente": a.entrada, "titulos_reales": n, "requests_con_titulo": tot_req,
           "por_pageurl": dist(t_urls), "por_emisor": dist(t_em),
           "top_titulos_multi_emisor": [{"titulo": k, "pageurls": len(t_urls[k]), "publishers": len(t_pubs[k]), "emisores": len(t_em[k]),
                                         "paises": len(t_paises[k]), "requests": t_req[k],
                                         "emisores_principales": [f"{e} {100 * q / t_req[k]:.0f}%" for e, q in t_em_req[k].most_common(4)]}
                                        for k in top]}
    json.dump(out, open(os.path.join(a.salida_dir, "titulos-pageurl.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"-> {a.salida_dir}: {n:,} titulos; {sum(1 for k in t_em if len(t_em[k]) >= 2):,} en >=2 emisores")


if __name__ == "__main__":
    main()
