# Content Objects por país: México, Colombia y Chile (consolidado v10 a v17)

**Fuente:** `inventory-consolidado-v10-a-v17.csv` — 959,442 filas únicas, 380,355,807,040 requests (métricas del corte v17, ventana 24 ago–7 sep 2026). Solo v17: 512,000 filas, 340,106,429,600 requests.
**Data completa:** `reporte-content-objects-detallado-v17-consolidado.json` (top-15 de valores por columna para cada país). Generado con `scripts/analizar.py`.

*Nota: "no vacías" excluye centinelas — una fila cuenta como vacía tanto si la celda no trae valor como si trae `Not Available`, `Not Applicable`, `Unknown` o basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).*

*Nota sobre `md5-vacío`: en `contentSeries` algunos vendedores mandan un hash MD5 en vez del nombre de la serie. El valor `d41d8cd98f00b204e9800998ecf8427e` es el MD5 de la cadena vacía, es decir, el vendedor hasheó un texto en blanco; se cuenta como vacío.*

## Comparativo de % de filas no vacías por columna

Entre paréntesis, el valor del consolidado anterior (v10 a v16) cuando el cambio supera un punto.

**Campos de app / vendedor:**

| Columna | México | Colombia | Chile |
|---|---:|---:|---:|
| Publisher | 100% | 100% | 100% |
| App Name | 87.5% | 97.3% | 94.8% |

**Content objects:**

| Columna | México | Colombia | Chile |
|---|---:|---:|---:|
| contentIsTitlePresent | 100% | 100% | 100% |
| contentGenre | 92.1% (93.9) | 93.0% (95.7) | 94.6% (96.9) |
| contentTitle | 87.0% | 95.6% | 97.1% |
| contentRating | 70.5% (69.4) | 69.8% (66.6) | 72.1% (71.1) |
| contentLanguage | 62.1% | 53.3% | 62.6% |
| contentIsLiveStream | 25.0% | 26.7% | 18.9% (17.2) |
| contentCategory | 23.1% | 21.8% (23.3) | 16.1% (17.5) |
| contentLength | 15.2% | 10.9% | 9.1% |
| contentSeries | 6.4% | 6.8% | 6.3% |

![Tablas de los tres países lado a lado](visual-tablas-paises.svg)

*(Generada con `scripts/generar_visual_paises.py` a partir del JSON de este reporte. En contentGenre aparecen `Drama` y `drama` como valores separados: así vienen en la fuente.)*

## México — 304,329 filas (31.7%) · 60.2% de los requests

eCPM: 79.5% de filas en cero · media no-cero 2.05 · ponderado 3.11

**Campos de app / vendedor:**

| Columna | % de filas no vacías | Top 3 referencias (% filas del país) |
|---|---:|---|
| Publisher | 100% | iion 17.8%, OTTera 12.9%, TCL Springserve 12.2% |
| App Name | 87.5% | MovieArk 31.8%, Live TV 22.4%, *N/A 12.6%* |

**Content objects:**

| Columna | % de filas no vacías | Top 3 referencias (% filas del país) |
|---|---:|---|
| contentIsTitlePresent | 100% | true 87.0%, false 13.0% |
| contentGenre | 92.1% | Drama 8.1%, *N/A 7.9%*, drama 7.0% |
| contentTitle | 87.0% | *N/A 13.0%*, las estrellas 0.4%, canal 5 0.3% |
| contentRating | 70.5% | *N/A 29.5%*, tv-14 8.7%, r 6.2% |
| contentLanguage | 62.1% | *N/A 37.7%*, es 23.3%, en 21.7% |
| contentIsLiveStream | 25.0% | *N/A 38.9%*, *Unknown 36.2%*, 1 25.0% |
| contentCategory | 23.1% | *[-7] 76.9%*, [IAB12] 4.4%, [IAB1] 4.0% |
| contentLength | 15.2% | *N/A 84.8%*, 6 5.0%, 5 3.5% |
| contentSeries | 6.4% | *N/A 92.3%*, md5-vacío 1.2%, VOD 0.5% |

## Colombia — 101,514 filas (10.6%) · 6.6% de los requests

eCPM: 85.7% de filas en cero · media no-cero 4.65 · ponderado 5.85

**Campos de app / vendedor:**

| Columna | % de filas no vacías | Top 3 referencias (% filas del país) |
|---|---:|---|
| Publisher | 100% | iion 33.3%, OTTera 18.5%, Select Plus 11.7% |
| App Name | 97.3% | MovieArk 38.7%, Live TV 30.9%, TCL CHANNEL 9.6% |

**Content objects:**

| Columna | % de filas no vacías | Top 3 referencias (% filas del país) |
|---|---:|---|
| contentIsTitlePresent | 100% | true 95.6%, false 4.4% |
| contentGenre | 93.0% | Drama 9.9%, *N/A 6.9%*, drama 6.0% |
| contentTitle | 95.6% | *N/A 4.4%*, haus of horror 0.2%, the baddest bad boy 0.2% |
| contentRating | 69.8% | *N/A 30.2%*, r 7.2%, Adults 7.0% |
| contentLanguage | 53.3% | *N/A 46.7%*, en 26.1%, English 10.9% |
| contentIsLiveStream | 26.7% | *Unknown 41.2%*, *N/A 32.1%*, 1 26.7% |
| contentCategory | 21.8% | *[-7] 78.2%*, [IAB1] 6.4%, [IAB1-22] 2.0% |
| contentLength | 10.9% | *N/A 89.1%*, 4 4.0%, 5 3.1% |
| contentSeries | 6.8% | *N/A 93.2%*, VOD 0.8%, OTT Studios Ent. 0.2% |

## Chile — 107,269 filas (11.2%) · 5.3% de los requests

eCPM: 77.1% de filas en cero · media no-cero 6.43 · ponderado 6.10

**Campos de app / vendedor:**

| Columna | % de filas no vacías | Top 3 referencias (% filas del país) |
|---|---:|---|
| Publisher | 100% | iion 24.1%, TCL Springserve 17.2%, OTTera 15.9% |
| App Name | 94.8% | MovieArk 46.2%, Live TV 30.8%, *N/A 5.2%* |

**Content objects:**

| Columna | % de filas no vacías | Top 3 referencias (% filas del país) |
|---|---:|---|
| contentIsTitlePresent | 100% | true 97.1%, false 2.9% |
| contentGenre | 94.6% | Drama 9.1%, drama 5.6%, *N/A 5.4%* |
| contentTitle | 97.1% | *N/A 2.9%*, catalunya über alles! 0.2%, hatchback 0.2% |
| contentRating | 72.1% | *N/A 27.9%*, tv-ma 8.6%, r 7.5% |
| contentLanguage | 62.6% | *N/A 37.4%*, en 33.4%, es 11.9% |
| contentIsLiveStream | 18.9% | *N/A 40.9%*, *Unknown 40.2%*, 1 18.9% |
| contentCategory | 16.1% | *[-7] 83.9%*, [IAB1] 6.7%, [IAB17] 1.1% |
| contentLength | 9.1% | *N/A 90.9%*, 4 3.7%, 5 2.4% |
| contentSeries | 6.3% | *N/A 93.7%*, VOD 0.9%, OTT Studios Ent. 0.1% |
