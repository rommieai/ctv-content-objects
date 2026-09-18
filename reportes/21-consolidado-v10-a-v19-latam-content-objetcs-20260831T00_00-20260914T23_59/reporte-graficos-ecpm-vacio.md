# Gráficos: eCPM de las filas llenas vs vacías (consolidado v10 a v19)

**Fuente:** `recursos/reporte-requests-ecpm-por-vacio-v19.json` (mismos datos de las tablas por país del detallado). Generado con `scripts/generar_graficos_ecpm_vacio.py` → `recursos/graficos-ecpm-vacio-r2.json`; tablas con `scripts/generar_reporte_graficos.py`.

*eCPM ponderado = Σ(eCPM × requests) / Σ requests, sin las filas con requests = 0 o eCPM = 0. Columnas: App Name y los 8 content objects con filas vacías; contentIsTitlePresent y Publisher vienen al 100% y no entran.*

## 1. Reparto del gasto (eCPM × requests / 1000) entre filas llenas y vacías

![reparto del gasto](recursos/graficos-ecpm-vacio-pies.svg)

*% del gasto del grupo que cae en filas donde la columna trae dato útil. El gasto se calcula solo sobre filas con eCPM > 0.*

| Columna | Total consolidado | México | Colombia | Chile |
|---|---:|---:|---:|---:|
| App Name | 93.8% | 92.2% | 89.1% | 96.0% |
| contentGenre | 81.9% | 84.8% | 90.1% | 84.9% |
| contentTitle | 63.7% | 50.9% | 89.9% | 87.2% |
| contentRating | 79.6% | 83.7% | 79.8% | 82.2% |
| contentLanguage | 68.0% | 74.3% | 46.8% | 84.2% |
| contentIsLiveStream | 47.7% | 54.1% | 40.1% | 23.2% |
| contentCategory | 33.0% | 46.3% | 31.4% | 15.2% |
| contentLength | 31.5% | 46.7% | 18.4% | 15.0% |
| contentSeries | 6.8% | 5.2% | 11.9% | 11.2% |

## 2. % de columnas llenas de la fila vs eCPM (fila a fila)

Cada registro del consolidado se clasifica por el % de los 8 content objects que trae con dato útil (contentGenre, contentCategory, contentSeries, contentLength, contentLanguage, contentIsLiveStream, contentTitle, contentRating; contentIsTitlePresent no cuenta porque siempre viene). Cada punto es un registro con eCPM > 0, con el eCPM en escala logarítmica y el tamaño según sus requests (por nivel y panel se dibujan los 40 registros de más requests y 300 al azar). El punto naranja es el eCPM ponderado por requests de todos los registros del nivel. Generado con `scripts/generar_scatter_completitud_ecpm.py` → `recursos/graficos-ecpm-completitud-scatter.json`.

![completitud vs eCPM, registro a registro](recursos/graficos-ecpm-completitud-scatter.svg)

**Total consolidado** — 1,158,509 filas · 482,736,715,920 requests

| % de columnas llenas (de 8) | % filas | % requests | % requests vendidos (eCPM > 0) | eCPM pond. (>0) |
|---:|---:|---:|---:|---:|
| 0% (0) | 0.1% | 2.4% | 85.9% | $6.46 |
| 12.5% (1) | 2.1% | 2.4% | 53.7% | $4.32 |
| 25% (2) | 11.2% | 11.9% | 61.5% | $3.33 |
| 37.5% (3) | 23.6% | 22.4% | 52.8% | $3.87 |
| 50% (4) | 32.4% | 27.8% | 51.2% | $3.32 |
| 62.5% (5) | 21.4% | 15.0% | 39.8% | $4.67 |
| 75% (6) | 4.8% | 8.4% | 63.0% | $4.79 |
| 87.5% (7) | 1.9% | 6.9% | 79.1% | $5.20 |
| 100% (8) | 2.5% | 3.0% | 67.9% | $3.34 |

**México** — 347,432 filas · 285,694,946,000 requests

| % de columnas llenas (de 8) | % filas | % requests | % requests vendidos (eCPM > 0) | eCPM pond. (>0) |
|---:|---:|---:|---:|---:|
| 0% (0) | 0.1% | 0.8% | 84.9% | $4.11 |
| 12.5% (1) | 3.0% | 2.5% | 59.8% | $4.34 |
| 25% (2) | 14.0% | 13.0% | 71.8% | $2.85 |
| 37.5% (3) | 23.0% | 22.2% | 63.6% | $3.00 |
| 50% (4) | 31.3% | 29.2% | 58.3% | $2.35 |
| 62.5% (5) | 17.8% | 10.2% | 48.0% | $2.46 |
| 75% (6) | 6.7% | 11.6% | 66.6% | $4.76 |
| 87.5% (7) | 2.6% | 9.7% | 83.9% | $5.40 |
| 100% (8) | 1.3% | 0.8% | 73.7% | $2.79 |

**Colombia** — 122,400 filas · 34,995,318,240 requests

| % de columnas llenas (de 8) | % filas | % requests | % requests vendidos (eCPM > 0) | eCPM pond. (>0) |
|---:|---:|---:|---:|---:|
| 0% (0) | 0.1% | 1.3% | 35.7% | $2.63 |
| 12.5% (1) | 2.5% | 2.7% | 21.5% | $3.74 |
| 25% (2) | 13.8% | 11.6% | 36.6% | $4.55 |
| 37.5% (3) | 32.3% | 31.6% | 26.9% | $5.79 |
| 50% (4) | 24.2% | 22.8% | 26.4% | $2.58 |
| 62.5% (5) | 18.3% | 15.9% | 22.7% | $5.69 |
| 75% (6) | 4.5% | 4.2% | 44.1% | $7.98 |
| 87.5% (7) | 1.6% | 2.7% | 59.7% | $3.12 |
| 100% (8) | 2.7% | 7.2% | 59.6% | $2.69 |

**Chile** — 133,317 filas · 27,900,831,680 requests

| % de columnas llenas (de 8) | % filas | % requests | % requests vendidos (eCPM > 0) | eCPM pond. (>0) |
|---:|---:|---:|---:|---:|
| 0% (0) | 0.1% | 2.6% | 42.3% | $12.28 |
| 12.5% (1) | 1.8% | 1.3% | 18.3% | $4.98 |
| 25% (2) | 14.7% | 9.3% | 23.6% | $6.24 |
| 37.5% (3) | 28.1% | 23.5% | 17.7% | $5.05 |
| 50% (4) | 35.4% | 37.1% | 55.9% | $5.72 |
| 62.5% (5) | 13.2% | 15.1% | 21.7% | $7.42 |
| 75% (6) | 3.2% | 3.8% | 41.1% | $5.40 |
| 87.5% (7) | 1.2% | 2.0% | 50.7% | $4.68 |
| 100% (8) | 2.3% | 5.3% | 58.4% | $4.52 |

## 3. Qué mueve el eCPM ponderado: la ruta de venta (publisher y país)

Sobre las filas con eCPM > 0 y requests > 0, la combinación publisher × país explica cerca de dos tercios de la variación del eCPM ponderado; los content objects, controlando por la ruta, aportan pocos puntos (género y rating los que más). Generado con `scripts/generar_graficos_drivers_ecpm.py` → `recursos/graficos-drivers-ecpm.json`.

### 3.1 eCPM ponderado por publisher y país

![eCPM por publisher y país](recursos/graficos-drivers-ecpm-heatmap-publisher-pais.svg)

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

### 3.2 Publishers: % de requests vendidos vs eCPM ponderado

![publishers: % vendido vs eCPM](recursos/graficos-drivers-ecpm-scatter-publisher.svg)

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

## 4. Por app: eCPM ponderado según cuántos content objects trae el registro

Top 12 apps por requests vendidos. Para cada app, barra = eCPM ponderado (eCPM > 0) de los registros con ese número de content objects con dato útil (de 8); debajo de cada barra, el % de los requests vendidos de la app en ese nivel. Los niveles con menos del 2 % de los requests vendidos de la app no se dibujan ni se tabulan. Generado con `scripts/generar_barras_app_completitud.py` → `recursos/graficos-app-completitud-barras.json`.

![eCPM por app y campos llenos](recursos/graficos-app-completitud-barras.svg)

| App | eCPM pond. app | % tráfico vendido | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| The Roku Channel | $5.65 | 15.8% | — | — | — | — | $5.71 (3%) | $5.54 (6%) | $5.77 (39%) | $5.57 (52%) | — |
| Live TV | $3.16 | 13.4% | — | — | $3.05 (12%) | $3.21 (40%) | $3.09 (44%) | $3.39 (2%) | — | — | — |
| ViX: TV, Deportes y Noticias | $2.36 | 11.5% | — | — | $2.37 (7%) | $2.14 (19%) | $2.38 (67%) | — | $2.44 (3%) | — | — |
| TCL CHANNEL | $6.29 | 9.7% | $7.25 (20%) | — | $6.56 (5%) | $5.80 (26%) | $5.14 (10%) | $6.43 (37%) | — | — | — |
| Not Available | $2.67 | 9.4% | — | — | $2.19 (8%) | $3.98 (6%) | $2.96 (40%) | $2.30 (24%) | $2.16 (15%) | $3.08 (4%) | — |
| MovieArk: Stream Movies & Live | $4.13 | 7.8% | — | $3.81 (2%) | $3.63 (15%) | $4.31 (39%) | $3.96 (40%) | $5.03 (2%) | — | — | — |
| ViX: TV, Sports and News | $1.87 | 7.1% | — | — | $1.50 (32%) | $1.93 (46%) | $2.36 (10%) | $2.41 (8%) | — | — | — |
| Coolita Channel | $3.26 | 5.2% | — | — | — | — | — | — | $2.84 (10%) | $3.39 (22%) | $3.31 (66%) |
| Browser TV Web - BrowseHere | $7.30 | 4.6% | $5.79 (23%) | — | $7.71 (3%) | $6.65 (15%) | $7.41 (37%) | $9.23 (21%) | — | — | — |
| Tubi: Free Movies & Live TV | $7.95 | 4.5% | $5.31 (6%) | $7.95 (14%) | $7.97 (36%) | $8.32 (44%) | — | — | — | — | — |
| WhaleLive | $2.53 | 4.3% | — | $2.82 (10%) | $2.48 (88%) | — | — | — | — | — | — |
| Vidaa | $1.53 | 2.3% | — | — | — | $1.37 (11%) | $1.46 (18%) | $1.55 (58%) | $1.33 (12%) | — | — |

*Entre paréntesis, el % de los requests vendidos de la app que cae en ese nivel de campos llenos.*

## 5. Títulos emitidos por más de un App Name

15,799 títulos reales, agrupados solo por App Name (sin pageURL). Generado con `scripts/generar_tabla_pageurl_titulos.py` → `recursos/titulos-appname.json`.

| App Name distintos por título | % de títulos | % de requests |
|---:|---:|---:|
| 1 | 47.7% | 7.8% |
| 2 | 27.3% | 8.3% |
| 3 | 7.0% | 2.1% |
| 4 | 3.3% | 2.1% |
| 5+ | 14.7% | 79.7% |

**Top 10 títulos (por requests) en dos o más App Name:** una barra por App Name dentro de cada título, con altura = eCPM ponderado de ese título en esa app (eCPM > 0; las 5 apps con más requests vendidos del título). Línea punteada = eCPM ponderado del título en todas sus apps.

![títulos en varios App Name: eCPM y reparto por app](recursos/graficos-titulos-appname-barras.svg)

| Título | App Name | Requests | eCPM pond. | Reparto por app (% de requests vendidos, eCPM pond. de la app) |
|---|---:|---:|---:|---|
| lo que la vida me robo | 7 | 3,106,572,320 | $2.21 | ViX: TV, Deportes y Noticias 70% ($2.35), Vidaa 11% ($1.57), Not Available 8% ($1.43), ViX: Cine y TV Gratis en Español 6% ($2.28), ViX: TV, Sports and News 4% ($2.90) |
| eve | 12 | 2,169,736,560 | $4.13 | Live TV 55% ($3.74), MovieArk: Stream Movies & Live 36% ($4.57), TCL CHANNEL 4% ($6.50), ViX: TV, Deportes y Noticias 2% ($2.22), Browser TV Web - BrowseHere 2% ($5.89) |
| brooklyn love stories | 8 | 2,111,762,640 | $3.72 | Live TV 54% ($3.10), MovieArk: Stream Movies & Live 39% ($4.16), TCL CHANNEL 4% ($6.56), Browser TV Web - BrowseHere 2% ($6.57), Not Available 1% ($3.85) |
| hatchback | 7 | 2,070,447,840 | $3.47 | Live TV 56% ($2.85), MovieArk: Stream Movies & Live 37% ($4.05), TCL CHANNEL 4% ($4.45), Browser TV Web - BrowseHere 2% ($7.30), Not Available 1% ($4.14) |
| corona | 7 | 2,055,902,000 | $3.99 | Live TV 54% ($3.40), MovieArk: Stream Movies & Live 40% ($4.38), TCL CHANNEL 4% ($6.53), Browser TV Web - BrowseHere 2% ($7.44), Not Available 0% ($3.91) |
| penance lane | 8 | 2,047,331,120 | $4.01 | Live TV 56% ($3.40), MovieArk: Stream Movies & Live 38% ($4.55), TCL CHANNEL 4% ($6.11), Browser TV Web - BrowseHere 2% ($7.06), Not Available 0% ($3.85) |
| american apocalypse | 8 | 2,046,553,920 | $3.77 | Live TV 56% ($3.30), MovieArk: Stream Movies & Live 37% ($3.96), TCL CHANNEL 4% ($6.64), Browser TV Web - BrowseHere 2% ($7.78), Not Available 1% ($5.06) |
| chicken stew | 7 | 1,882,113,200 | $6.19 | TCL CHANNEL 61% ($5.38), Browser TV Web - BrowseHere 27% ($9.37), Live TV 8% ($2.94), MovieArk: Stream Movies & Live 4% ($3.82), Not Available 0% ($4.54) |
| chicken coop | 7 | 1,858,788,400 | $6.01 | TCL CHANNEL 62% ($5.13), Browser TV Web - BrowseHere 25% ($9.44), Live TV 7% ($3.14), MovieArk: Stream Movies & Live 5% ($3.91), Not Available 0% ($2.72) |
| humble pie | 7 | 1,786,588,400 | $6.77 | Live TV 32% ($5.10), TCL CHANNEL 31% ($7.50), MovieArk: Stream Movies & Live 23% ($6.93), Browser TV Web - BrowseHere 13% ($8.82), Not Available 0% ($7.03) |

## 6. Completitud de los content objects por canal

Canal = filas cuyo Publisher o App Name lo nombra (Caracol via OB / ditu por Caracol, RCN via OB / Canal RCN, Canal 13 OB, Televisa Univision via … / ViX, TV Azteca - Springserve / Azteca TV). Cada segmento de la barra es una columna, con altura = % de filas del canal con dato útil en esa columna dividido entre 8; la barra completa es la completitud promedio de las 8 columnas. Generado con `scripts/generar_barras_canales_completitud.py` → `recursos/graficos-canales-completitud-barras.json`.

![completitud por canal](recursos/graficos-canales-completitud-barras.svg)

| Canal | Filas | Requests | Promedio | Title | Genre | Rating | Language | IsLiveStream | Category | Length | Series |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Televisa | 40,779 | 66,601,273,920 | 49.4% | 75.2% | 96.3% | 82.0% | 57.3% | 34.8% | 10.7% | 38.3% | 0.2% |
| TV Azteca | 2,251 | 18,906,692,640 | 36.9% | 0.7% | 97.9% | 96.8% | 98.5% | 0.2% | 0.4% | 0.4% | 0.2% |
| RCN | 42 | 105,527,120 | 21.1% | 0.0% | 0.0% | 0.0% | 83.3% | 28.6% | 0.0% | 57.1% | 0.0% |
| Canal 13 | 8 | 9,988,800 | 18.8% | 0.0% | 0.0% | 0.0% | 75.0% | 75.0% | 0.0% | 0.0% | 0.0% |
| Caracol | 12 | 34,383,840 | 14.6% | 0.0% | 0.0% | 0.0% | 66.7% | 50.0% | 0.0% | 0.0% | 0.0% |
| Win | 0 | 0 | — | — | — | — | — | — | — | — | — |
| Telefe | 0 | 0 | — | — | — | — | — | — | — | — | — |

*Win y Telefe no aparecen en el consolidado: ningún Publisher ni App Name los nombra.*

## 7. Canales: requests totales vs eCPM ponderado

Un punto por canal (mismos canales y misma definición de la sección 6). x = requests totales del canal en escala logarítmica; y = eCPM ponderado de sus filas con eCPM > 0. Junto al punto, requests totales y % de requests vendidos.

![canales: requests vs eCPM](recursos/graficos-canales-requests-ecpm.svg)

| Canal | Requests | Requests vendidos | % vendido | eCPM pond. |
|---|---:|---:|---:|---:|
| Televisa | 66,601,273,920 | 57,893,466,880 | 86.9% | $2.08 |
| TV Azteca | 18,906,692,640 | 12,184,514,160 | 64.4% | $7.92 |
| RCN | 105,527,120 | 105,382,000 | 99.9% | $1.65 |
| Caracol | 34,383,840 | 33,774,800 | 98.2% | $3.17 |
| Canal 13 | 9,988,800 | 0 | 0.0% | — (sin filas vendidas) |
| Win | 0 | 0 | — | — |
| Telefe | 0 | 0 | — | — |

## 8. Registros sin contentTitle: qué content objects se relacionan con el eCPM

80,799 filas sin título (138,465,959,120 requests; 68.8% vendidos; eCPM ponderado $4.12). Generado con `scripts/generar_graficos_sin_titulo.py` → `recursos/graficos-sin-titulo.json`.

### 8.1 eCPM ponderado con y sin dato en cada columna

Filas sin título del consolidado tal como llega, antes del relleno. Por columna se parten en dos grupos: las que traen dato útil (círculo lleno) y las que la traen vacía (círculo hueco); de cada grupo, su % de las filas sin título, su % de requests vendidos y su eCPM ponderado. Diferencia = eCPM con dato − eCPM sin dato.

![sin título: eCPM con y sin dato por columna](recursos/graficos-sin-titulo-con-sin-dato.svg)

| Columna | % filas con dato | % vendido con dato | eCPM pond. con dato | % filas sin dato | % vendido sin dato | eCPM pond. sin dato | Diferencia |
|---|---:|---:|---:|---:|---:|---:|---:|
| contentLength | 54.3% | 57.0% | $5.62 | 45.7% | 73.0% | $3.70 | +$1.92 |
| contentSeries | 6.5% | 46.0% | $5.71 | 93.5% | 69.6% | $4.08 | +$1.62 |
| contentRating | 80.9% | 61.5% | $4.71 | 19.1% | 80.8% | $3.38 | +$1.33 |
| contentCategory | 50.7% | 50.1% | $4.98 | 49.3% | 80.0% | $3.80 | +$1.18 |
| contentLanguage | 82.4% | 65.2% | $4.09 | 17.6% | 77.9% | $4.18 | −$0.09 |
| contentGenre | 87.9% | 65.0% | $3.93 | 12.1% | 76.4% | $4.44 | −$0.51 |
| contentIsLiveStream | 24.2% | 82.8% | $3.17 | 75.8% | 52.9% | $5.80 | −$2.63 |

### 8.2 eCPM ponderado por género en las filas sin título

Género normalizado tal como llega. Es el content object que más separa el precio cuando no hay título: explica el 20.6 % de la variación del eCPM ponderado solo y aporta 6.9 puntos más controlando por publisher × país (rating: 17.1 % y 4.7 puntos; livestream, length, categoría y series: menos de 1.5 puntos).

![sin título: eCPM por género](recursos/graficos-sin-titulo-genero.svg)

| Género | Filas | % del tráfico vendido sin título | eCPM pond. |
|---|---:|---:|---:|
| drama | 7,548 | 10.5% | $6.09 |
| documental | 2,132 | 0.6% | $5.92 |
| concursos | 389 | 0.6% | $5.85 |
| noticias | 2,149 | 5.5% | $5.40 |
| aventura | 1,134 | 0.9% | $5.36 |
| gastronomia | 484 | 1.1% | $5.23 |
| terror | 1,910 | 1.1% | $4.96 |
| accion | 4,281 | 3.0% | $4.75 |
| pelicula (generico) | 1,774 | 0.8% | $4.52 |
| entretenimiento | 3,340 | 10.8% | $4.46 |
| (sin género) | 30,263 | 39.0% | $4.39 |
| thriller | 1,678 | 0.5% | $4.18 |
| comedia | 4,961 | 3.6% | $3.26 |
| romance | 2,048 | 2.4% | $2.12 |
| deportes | 3,247 | 17.9% | $1.90 |
