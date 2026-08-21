# Análisis exploratorio — Inventario CTV LATAM (content objects + eCPM)

Análisis de las exportaciones del reporte de *inventory source* (v10, v11 y v12) sobre
inventario CTV en LATAM: cobertura y calidad de los content objects de OpenRTB
(género, categoría, serie, título, rating, idioma, duración, livestream) y
comportamiento del eCPM, global y por país.

Los CSV de origen **no se versionan** (100+ MB cada uno, ver `.gitignore`); los reportes
y la data agregada en JSON sí.

## Estructura

```
scripts/                 codigo que genera los consolidados y los JSON
  consolidar.py          une N exportaciones en un CSV sin duplicados
  analizar.py            analisis por columna y por pais -> JSON (+ digests de texto)
  normalizar_monetizar.py  normaliza genero/rating y analiza el inventario con eCPM > 0

reporte-*.md             reportes redactados (el analisis narrado)
reporte-*.json           la data que respalda cada reporte
```

## Pipeline

```bash
# 1. Consolidar las exportaciones (la mas reciente primero: sus metricas ganan)
python scripts/consolidar.py inventory-consolidado.csv v12.csv v11.csv v10.csv

# 2. Analisis por columna + por pais (JSON + digests de texto para redactar)
python scripts/analizar.py inventory-consolidado.csv reporte-detallado.json \
    --paises "Mexico,Colombia,Chile" --digest ./digests

# 3. Normalizacion de genero/rating + analisis del inventario monetizado
python scripts/normalizar_monetizar.py inventory-consolidado.csv \
    inventory-enriquecido.csv reporte-normalizacion.json
```

Solo requiere Python 3.9+ (stdlib, sin dependencias).

## Notas metodológicas clave

- Cada fila de los CSV es una **combinación agregada** de 14 dimensiones + 2 métricas
  (`Total Requests`, `eCPM`), no un evento. Los análisis siempre separan **% de filas**
  (variedad de catálogo) y **% de requests** (tráfico real): el 1% de las filas
  concentra ~50% de los requests.
- Las exportaciones vienen **truncadas a 512,000 filas** y son cortes casi idénticos de
  la misma ventana (~97% de llaves compartidas entre versiones). Por eso se consolidan
  por unión de llaves (sin sumar métricas, que sería doble conteo) conservando las
  métricas del corte más reciente.
- Un valor se considera vacío si es centinela (`Not Available`, `Not Applicable`,
  `Unknown`...) o basura equivalente: `[-7]` en contentCategory, el hash MD5 de la
  cadena vacía en contentSeries, macros sin reemplazar (`{{CONTENT_SERIES}}`).
- Los content objects son estables entre versiones del reporte; **los eCPM se
  recalculan** (entre v11 y v12 desapareció un outlier de 200.0 y el ponderado global
  bajó de ~4.98 a 4.55). Fijar la versión antes de comparar precios.

## Reportes

| Reporte | Contenido |
|---|---|
| `reporte-content-objects-detallado-v12-consolidado.md` | El más reciente: consolidado v10+v11+v12, columna por columna + México/Colombia/Chile |
| `reporte-content-objects-detallado.md` / `-v11.md` | Detallados de cada exportación individual (18 países) |
| `reporte-content-objects-detallado-unificado.md` | Consolidado v10+v11 |
| `reporte-comparativo-v10-v11.md` | Cruce entre exportaciones y justificación del consolidado |
| `reporte-normalizacion-y-ecpm.md` | Género/rating normalizados + análisis del inventario monetizado |
| `resumen-ejecutivo.pdf` | Resumen para stakeholders (compilado con LaTeX) |
