# -*- coding: utf-8 -*-
"""Genera un SVG con las tablas de los paises lado a lado (estilo hoja de calculo).

Lee el JSON del analisis por pais (salida de analizar.py) y arma, para cada pais,
un panel Columna | Fill | Top valores, con el fill coloreado por semaforo:
verde >= 90%, amarillo >= 60%, naranja >= 20%, rojo < 20%.

Uso:
    python generar_visual_paises.py reporte-paises.json salida.svg [pais1 pais2 ...]

Si no se pasan paises usa todos los del JSON en su orden.
"""
import json
import sys
from xml.sax.saxutils import escape

FILAS = ["Publisher", "App Name", "contentTitle", "contentGenre", "contentSeries",
         "contentLanguage", "contentCategory", "contentRating", "contentLength",
         "contentIsLiveStream", "contentIsTitlePresent"]
ETIQUETA_PAIS = {"Mexico": "MX", "Colombia": "CO", "Chile": "CL", "Peru": "PE",
                 "Argentina": "AR", "Ecuador": "EC"}
ABREVIAR = {"Not Available": "N/A", "Not Applicable": "N/A",
            "d41d8cd98f00b204e9800998ecf8427e": "md5-vacío",
            "MovieArk: Stream Movies & Live": "MovieArk",
            "Browser TV Web - BrowseHere": "BrowseHere",
            "Televisa Univision via SpringServe": "Televisa (SS)",
            "TCL ADS - Springserve": "TCL Springserve", "TCL ADs (APAC)": "TCL APAC",
            "Select Plus PTE LTD (CTV)": "Select Plus",
            "METAX SOFTWARE PTE. LTD. (Exchange)": "METAX",
            "Equativ (Formerly SMART AdServer) - oRTB CTV": "Equativ",
            "iion Pty Ltd": "iion", "OTTera.tv": "OTTera"}
TOP_N = 4
ANCHO_COL, ANCHO_FILL, ANCHO_TOP = 158, 66, 470
ALTO_FILA, ALTO_HEADER = 24, 26
SEP = 16
MAX_CHARS_TOP = 76


def color_fill(pct):
    if pct is None:
        return "#f4cccc"
    if pct >= 90:
        return "#d9ead3"
    if pct >= 60:
        return "#fff2cc"
    if pct >= 20:
        return "#fce5cd"
    return "#f4cccc"


def abreviar(v):
    v = ABREVIAR.get(v, v)
    return v if len(v) <= 26 else v[:25] + "…"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    datos = json.load(open(sys.argv[1], encoding="utf-8"))
    paises = sys.argv[3:] or list(datos["grupos"].keys())

    ancho_panel = ANCHO_COL + ANCHO_FILL + ANCHO_TOP
    ancho = 10 + len(paises) * ancho_panel + (len(paises) - 1) * SEP + 10
    alto = 10 + ALTO_HEADER * 2 + ALTO_FILA * len(FILAS) + 10

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" '
           f'viewBox="0 0 {ancho} {alto}" font-family="Arial, sans-serif">',
           f'<rect width="{ancho}" height="{alto}" fill="white"/>']

    def celda(x, y, w, h, texto, bg=None, negrilla=False, tam=12, dx=6, anchor="start"):
        if bg:
            svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>')
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
                   f'stroke="#b7b7b7" stroke-width="1"/>')
        peso = ' font-weight="bold"' if negrilla else ""
        tx = x + dx if anchor == "start" else x + w - dx
        svg.append(f'<text x="{tx}" y="{y + h / 2 + tam / 3}" font-size="{tam}" '
                   f'text-anchor="{anchor}"{peso}>{escape(texto)}</text>')

    x0 = 10
    for pais in paises:
        g = datos["grupos"][pais]
        y = 10
        celda(x0, y, ancho_panel, ALTO_HEADER, ETIQUETA_PAIS.get(pais, pais),
              bg="#efefef", negrilla=True, tam=13, dx=ancho_panel / 2, anchor="middle")
        y += ALTO_HEADER
        celda(x0, y, ANCHO_COL, ALTO_HEADER, "Columna", bg="#f7f7f7", negrilla=True)
        celda(x0 + ANCHO_COL, y, ANCHO_FILL, ALTO_HEADER, "Fill", bg="#f7f7f7", negrilla=True)
        celda(x0 + ANCHO_COL + ANCHO_FILL, y, ANCHO_TOP, ALTO_HEADER,
              "Top valores (% filas del país)", bg="#f7f7f7", negrilla=True)
        y += ALTO_HEADER
        for col in FILAS:
            cc = g["columnas"][col]
            fill = cc["fill_rate_pct"]
            tops = ", ".join(f"{abreviar(v)} {p:.1f}%" for v, n, p in cc["top"][:TOP_N])
            if len(tops) > MAX_CHARS_TOP:
                tops = tops[:MAX_CHARS_TOP - 1] + "…"
            celda(x0, y, ANCHO_COL, ALTO_FILA, col, tam=11.5)
            celda(x0 + ANCHO_COL, y, ANCHO_FILL, ALTO_FILA, f"{fill:.2f}%",
                  bg=color_fill(fill), tam=11.5, anchor="end")
            celda(x0 + ANCHO_COL + ANCHO_FILL, y, ANCHO_TOP, ALTO_FILA, tops, tam=11)
            y += ALTO_FILA
        x0 += ancho_panel + SEP

    svg.append("</svg>")
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"-> {sys.argv[2]} ({ancho}x{alto})")


if __name__ == "__main__":
    main()
