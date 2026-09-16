# Análisis por publisher, consolidado v10 a v17 (CTV LATAM)

**Fuente:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas, 380,355,807,040 requests; métricas de v17).
**Generado con:** `scripts/analizar.py --por Publisher --top-grupos 12` → `reporte-publishers-v17-consolidado.json`.
**Alcance:** los 12 publishers con más requests (~88% del tráfico). Porcentajes sobre las filas de cada publisher.

## Tabla comparativa

| Publisher | % filas | % requests | % filas eCPM=0 | eCPM pond. | % no vacías: category | % no vacías: language | % no vacías: title | % no vacías: length |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Roku - oRTB | 1.4% | 16.3% | 98.0% | 5.32 | 98.1% | 85.2% | 27.4% | 80.0% |
| OTTera.tv | 20.9% | 15.4% | 99.9% | 6.25 | 37.1% | 90.4% | 99.7% | 1.1% |
| iion Pty Ltd | 19.1% | 13.8% | 89.0% | 5.66 | 0.6% | 3.4% | 99.8% | 3.0% |
| TCL ADS - Springserve | 12.5% | 9.3% | 61.3% | 5.04 | 0.7% | 76.8% | 99.6% | 1.3% |
| TCL ADs (APAC) | 11.8% | 5.4% | 52.5% | 5.62 | 0.9% | 82.3% | 99.8% | 2.4% |
| Equativ - oRTB CTV | 2.5% | 5.1% | 80.0% | 2.57 | 24.0% | 77.3% | 86.1% | 23.2% |
| Televisa Univision via SpringServe | 1.5% | 5.1% | 61.4% | 2.24 | 0.0% | 52.1% | 85.4% | 53.0% |
| TV Azteca - Springserve | 0.2% | 4.3% | 93.2% | 5.92 | 0.3% | 98.7% | 0.2% | 0.2% |
| Coocaa (SKYWORTH) | 1.6% | 4.3% | 56.3% | 2.89 | 100% | 77.3% | 100% | 100% |
| Televisa Univision via OB | 0.6% | 3.3% | 46.9% | 1.10 | 0.0% | 93.9% | 0.0% | 0.0% |
| Select Plus PTE LTD (CTV) | 8.7% | 3.2% | 99.9% | 12.61 | 0.0% | 71.4% | 99.9% | 1.4% |
| Vidaa | 1.8% | 2.6% | 70.7% | 1.42 | 86.1% | 90.3% | 79.7% | 2.4% |

*"% filas" y "% requests" son la participación del publisher sobre el total del dataset (Publisher viene en el 100% de las filas). Las columnas "% no vacías" son sobre las filas del propio publisher. El orden sigue el peso en requests. Data completa en el JSON.*

*Nota sobre `contentSeries` de Roku: viene como hash MD5 en vez del nombre de la serie; el 53.2% de sus filas trae `d41d8cd98f00b204e9800998ecf8427e`, el MD5 de la cadena vacía, que se cuenta como vacío.*
