# -*- coding: utf-8 -*-
"""Consolida N exportaciones del reporte de inventory source en un solo CSV sin duplicados.

Cada fila se identifica por la llave de 14 dimensiones (todas las columnas menos
`Total Requests` y `eCPM`). Cuando una llave aparece en varios archivos se conservan
las metricas del archivo de mayor prioridad (el primero en la linea de comandos);
las llaves que solo existen en archivos viejos se agregan con sus metricas originales.
Esto evita el doble conteo: las exportaciones son cortes casi identicos de la misma
ventana, no periodos disjuntos que se puedan sumar.

Uso:
    python consolidar.py salida.csv mas_reciente.csv ... mas_viejo.csv

Imprime estadisticas de solapamiento entre cada archivo y el acumulado.
"""
import csv
import sys

N_DIMS = 14  # las primeras 14 columnas son dimensiones; las ultimas 2, metricas


def cargar(path):
    """Lee un CSV y devuelve (encabezado, dict llave -> [metricas])."""
    data = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        cols = next(reader)
        for row in reader:
            if len(row) != len(cols):
                continue
            data[tuple(row[:N_DIMS])] = row[N_DIMS:]
    return cols, data


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out_path = sys.argv[1]
    fuentes = sys.argv[2:]

    consolidado = {}
    cols = None
    for i, path in enumerate(fuentes):
        cols_f, data = cargar(path)
        cols = cols or cols_f
        nuevas = sum(1 for k in data if k not in consolidado)
        compartidas = len(data) - nuevas
        print(f"[{i}] {path.split(chr(92))[-1]}: {len(data):,} filas | "
              f"{compartidas:,} ya vistas | {nuevas:,} nuevas")
        for k, met in data.items():
            consolidado.setdefault(k, met)  # el primero (mas reciente) gana

    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        for k, met in consolidado.items():
            writer.writerow(list(k) + met)
    print(f"-> {out_path}: {len(consolidado):,} filas consolidadas")


if __name__ == "__main__":
    main()
