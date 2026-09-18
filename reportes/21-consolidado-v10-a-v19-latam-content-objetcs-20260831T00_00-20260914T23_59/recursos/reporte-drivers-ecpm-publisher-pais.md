# Qué mueve el eCPM ponderado: la ruta de venta (publisher y país) (consolidado v10 a v19)

Sobre las filas con eCPM > 0 y requests > 0, la combinación publisher × país explica cerca de dos tercios de la variación del eCPM ponderado; los content objects, controlando por la ruta, aportan pocos puntos (género y rating los que más). Generado con `scripts/generar_graficos_drivers_ecpm.py` → `graficos-drivers-ecpm.json`.

## 1. eCPM ponderado por publisher y país

![eCPM por publisher y país](graficos-drivers-ecpm-heatmap-publisher-pais.svg)

*Publishers ordenados por requests vendidos (top 12). En cada celda, eCPM ponderado y, debajo, % del tráfico vendido del consolidado que cae en esa combinación. Vacío = menos del 0.05 % del tráfico vendido.*

| Publisher | Mexico | Argentina | Colombia | Chile | Peru | Costa Rica |
|---|---:|---:|---:|---:|---:|---:|
| Roku - oRTB | $5.65 (16.0%) | — | — | — | — | — |
| TCL ADS - Springserve | $2.09 (6.5%) | $7.45 (5.1%) | — | $7.76 (1.2%) | — | $4.75 (0.4%) |
| iion Pty Ltd | $2.73 (6.0%) | $5.73 (4.3%) | $6.76 (1.5%) | — | $5.40 (1.3%) | — |
| Televisa Univision via SpringServe | $2.04 (7.5%) | $2.52 (0.1%) | — | — | — | — |
| Equativ (Formerly SMART AdServer) - oRTB CTV | $2.62 (7.9%) | — | — | — | — | — |
| TCL ADs (APAC) | $2.08 (2.5%) | $9.47 (2.4%) | $1.55 (0.9%) | $8.61 (0.8%) | $5.16 (0.5%) | — |
| Televisa Univision via OB | $1.00 (5.4%) | $1.01 (0.1%) | — | — | — | — |
| Coocaa, a SKYWORTH company | $2.54 (0.5%) | $3.15 (2.8%) | $2.67 (0.8%) | $4.38 (0.5%) | $2.52 (0.4%) | $8.80 (0.2%) |
| TV Azteca - Springserve | $7.92 (4.6%) | — | — | — | — | — |
| Vidaa | $1.11 (3.9%) | $2.63 (0.2%) | $6.32 (0.1%) | $3.87 (0.1%) | $2.62 (0.1%) | — |
| Zeasn Europe B.V. | $2.02 (2.5%) | $2.92 (0.9%) | $1.72 (0.3%) | — | $5.30 (0.1%) | $5.97 (0.3%) |
| Vidaa  APAC Hisense Headquarter | $1.43 (1.6%) | $2.63 (0.1%) | $3.94 (0.1%) | — | — | — |

## 2. Publishers: % de requests vendidos vs eCPM ponderado

![publishers: % vendido vs eCPM](graficos-drivers-ecpm-scatter-publisher.svg)

*Un punto por publisher (top 20 por requests); el tamaño es el total de requests. Líneas punteadas: promedio ponderado del consolidado (55 % vendido, $4.05).*

| Publisher | Requests | % vendido (eCPM > 0) | eCPM pond. | % del tráfico vendido |
|---|---:|---:|---:|---:|
| iion Pty Ltd | 74,914,338,080 | 47.0% | $4.48 | 13.2% |
| Roku - oRTB | 71,242,132,400 | 60.2% | $5.65 | 16.1% |
| OTTera.tv | 66,580,855,520 | 0.3% | $6.38 | 0.1% |
| TCL ADS - Springserve | 45,260,186,640 | 80.4% | $4.79 | 13.6% |
| TCL ADs (APAC) | 27,098,439,200 | 75.6% | $5.48 | 7.7% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 25,464,790,800 | 83.3% | $2.61 | 7.9% |
| Televisa Univision via SpringServe | 25,078,019,680 | 85.2% | $2.25 | 8.0% |
| Select Plus PTE LTD (CTV) | 22,836,943,680 | 0.1% | $13.68 | 0.0% |
| TV Azteca - Springserve | 18,892,164,560 | 64.5% | $7.92 | 4.6% |
| Coocaa, a SKYWORTH company | 17,434,893,120 | 79.8% | $3.26 | 5.2% |
| Televisa Univision via OB | 15,145,327,600 | 97.8% | $1.03 | 5.5% |
| Vidaa | 14,056,808,560 | 84.5% | $1.50 | 4.4% |
| Zeasn Europe B.V. | 11,740,200,320 | 98.7% | $2.54 | 4.3% |
| AWG Media | 7,687,746,400 | 52.8% | $3.19 | 1.5% |
| PML Digital | 7,007,781,760 | 73.7% | $2.33 | 1.9% |
| Vidaa  APAC Hisense Headquarter | 6,535,494,320 | 81.1% | $1.88 | 2.0% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 5,692,454,640 | 49.2% | $3.56 | 1.1% |
| Aluna Limited | 2,491,119,840 | 77.4% | $5.30 | 0.7% |
| METAX SOFTWARE PTE. LTD. | 1,850,575,760 | 80.5% | $6.11 | 0.6% |
| Kivi via Springserve | 1,236,449,920 | 22.7% | $5.11 | 0.1% |
