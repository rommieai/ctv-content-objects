# Análisis por publisher, consolidado v10 a v18 (CTV LATAM)

**Fuente:** `inventory-consolidado-v10-a-v18.csv` (1,071,840 filas, 426,223,575,360 requests; métricas de v18).
**Generado con:** `scripts/analizar.py --por Publisher --top-grupos 12` → `reporte-publishers-v18-consolidado.json`.
**Alcance:** los 12 publishers con más requests (~88% del tráfico). Porcentajes sobre las filas de cada publisher.

## Tabla comparativa

| Publisher | % filas | % requests | % filas eCPM=0 | eCPM pond. | % llenas: category | % llenas: language | % llenas: title | % llenas: length |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| iion Pty Ltd | 19.4% | 15.9% | 88.9% | $4.72 | 0.6% | 3.3% | 99.8% | 2.9% |
| Roku - oRTB | 1.4% | 14.8% | 98.2% | $5.67 | 98.1% | 85.7% | 27.5% | 80.8% |
| OTTera.tv | 20.6% | 13.7% | 100.0% | $6.17 | 37.8% | 91.2% | 99.7% | 1.1% |
| TCL ADS - Springserve | 12.4% | 9.4% | 61.4% | $4.95 | 0.7% | 76.7% | 99.6% | 1.3% |
| TCL ADs (APAC) | 11.8% | 5.6% | 51.2% | $5.64 | 0.9% | 82.0% | 99.8% | 2.4% |
| Televisa Univision via SpringServe | 1.5% | 5.2% | 62.2% | $2.26 | 0.0% | 52.8% | 85.3% | 53.4% |
| Equativ - oRTB CTV | 2.4% | 5.1% | 80.3% | $2.61 | 24.9% | 77.5% | 86.5% | 24.0% |
| Select Plus PTE LTD (CTV) | 9.1% | 4.6% | 99.9% | $13.42 | 0.0% | 71.3% | 100% | 1.4% |
| TV Azteca - Springserve | 0.2% | 3.8% | 97.7% | $7.31 | 0.4% | 98.7% | 0.6% | 0.3% |
| Coocaa (SKYWORTH) | 1.5% | 3.7% | 62.1% | $3.26 | 100% | 78.2% | 100% | 100% |
| Televisa Univision via OB | 0.5% | 3.1% | 48.0% | $0.97 | 0.0% | 94.0% | 0.0% | 0.0% |
| Vidaa | 1.8% | 3.0% | 70.5% | $1.48 | 86.3% | 91.3% | 79.1% | 2.3% |

*"% filas" y "% requests" son la participación del publisher sobre el total del dataset (Publisher viene en el 100% de las filas). Las columnas "% llenas" son sobre las filas del propio publisher. El orden sigue el peso en requests. Data completa en el JSON.*

*Nota sobre `contentSeries` de Roku: viene como hash MD5 en vez del nombre de la serie; el 53.5% de sus filas trae `d41d8cd98f00b204e9800998ecf8427e`, el MD5 de la cadena vacía, que se cuenta como vacío.*
