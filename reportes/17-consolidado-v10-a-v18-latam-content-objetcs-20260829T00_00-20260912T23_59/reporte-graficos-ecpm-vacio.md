# Gráficos: eCPM de las filas no vacías vs vacías (consolidado v10 a v18)

**Fuente:** `reporte-requests-ecpm-por-vacio-v18.json` (mismos datos de las tablas por país del detallado). Generado con `scripts/generar_graficos_ecpm_vacio.py` → `graficos-ecpm-vacio-r2.json`.

*eCPM ponderado = Σ(eCPM × requests) / Σ requests, sin las filas con requests = 0 o eCPM = 0. Un punto por content object (9 columnas: App Name y los 8 content objects con filas vacías; contentIsTitlePresent y Publisher vienen al 100% y no entran). R² es el de la recta de mínimos cuadrados (OLS) sobre esos 9 puntos.*

## 1. eCPM no vacías (x) vs eCPM vacías (y)

![eCPM no vacías vs vacías](graficos-ecpm-vacio-scatter.svg)

| Grupo | R² | Pendiente | Intercepto | Columnas que pagan más vacías |
|---|---:|---:|---:|---:|
| Total consolidado | 0.128 | -0.697 | 6.69 | 3 de 9 |
| México | 0.270 | -0.446 | 4.42 | 2 de 9 |
| Colombia | 0.422 | -1.005 | 9.63 | 6 de 9 |
| Chile | 0.114 | 0.708 | 3.03 | 8 de 9 |

## 2. % de filas no vacías (x) vs eCPM (y), por serie

![completitud vs eCPM](graficos-ecpm-vacio-scatter-fill.svg)

| Grupo | Serie | R² | Pendiente ($ por punto de %) | Intercepto |
|---|---|---:|---:|---:|
| Total consolidado | eCPM filas no vacías | 0.000 | 0.0001 | 4.10 |
| Total consolidado | eCPM filas vacías | 0.091 | -0.0040 | 4.05 |
| México | eCPM filas no vacías | 0.585 | -0.0124 | 4.28 |
| México | eCPM filas vacías | 0.033 | 0.0025 | 2.67 |
| Colombia | eCPM filas no vacías | 0.627 | 0.0190 | 3.45 |
| Colombia | eCPM filas vacías | 0.151 | -0.0144 | 5.91 |
| Chile | eCPM filas no vacías | 0.653 | 0.0101 | 5.05 |
| Chile | eCPM filas vacías | 0.400 | 0.0165 | 6.12 |

## 3. Reparto del gasto (eCPM × requests / 1000) entre filas no vacías y vacías

![reparto del gasto](graficos-ecpm-vacio-pies.svg)

*% del gasto del grupo que cae en filas donde la columna trae dato útil. El gasto se calcula solo sobre filas con eCPM > 0.*

| Columna | Total consolidado | México | Colombia | Chile |
|---|---:|---:|---:|---:|
| App Name | 93.6% | 91.5% | 89.4% | 96.1% |
| contentGenre | 80.3% | 83.7% | 89.9% | 83.7% |
| contentTitle | 65.2% | 54.0% | 89.8% | 85.8% |
| contentRating | 76.8% | 81.0% | 78.4% | 80.3% |
| contentLanguage | 65.6% | 71.9% | 45.7% | 82.2% |
| contentIsLiveStream | 49.1% | 57.7% | 39.1% | 22.4% |
| contentCategory | 33.6% | 49.4% | 29.8% | 14.7% |
| contentLength | 32.0% | 49.4% | 16.9% | 14.8% |
| contentSeries | 6.9% | 5.6% | 10.7% | 10.9% |
