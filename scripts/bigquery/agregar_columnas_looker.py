# -*- coding: utf-8 -*-
"""Agrega al CSV enriquecido las dos columnas que usa Looker Studio:
  cal_total_cost = Total Requests * eCPM / 1000
  fecha_reporte  = fecha (YYYY-MM-DD) en que se genero el reporte en PubMatic

Uso:
    python agregar_columnas_looker.py entrada-enriquecida.csv salida.csv 2026-09-14
"""
import csv, sys
if len(sys.argv) != 4:
    print(__doc__); sys.exit(1)
SRC, OUT, FECHA = sys.argv[1:4]
csv.field_size_limit(10**9)
r = csv.reader(open(SRC, encoding='utf-8-sig', newline=''))
w = csv.writer(open(OUT, 'w', encoding='utf-8', newline=''))
hdr = next(r); ir = hdr.index('Total Requests'); ie = hdr.index('eCPM')
w.writerow(hdr + ['cal_total_cost', 'fecha_reporte'])
n = req = 0; cost = 0.0
for row in r:
    tr = int(row[ir]); c = tr * float(row[ie]) / 1000
    w.writerow(row + [repr(round(c, 6)), FECHA]); n += 1; req += tr; cost += c
print(f'filas={n:,} requests={req:,} cal_total_cost={cost:,.2f}')
