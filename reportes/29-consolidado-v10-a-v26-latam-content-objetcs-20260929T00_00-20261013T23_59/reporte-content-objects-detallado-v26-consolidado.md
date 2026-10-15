# Content Objects por país: México, Colombia y Chile (consolidado v10 a v26)

**Fuente:** `inventory-consolidado-v10-a-v26.csv` — 1,473,643 filas únicas, 527,882,754,682 requests (métricas del corte v26, ventana 29 sep–13 oct 2026; v26 aportó 30,253 combinaciones nuevas). Solo v26: 512,000 filas, 361,404,328,162 requests.
**Data completa:** `recursos/reporte-content-objects-detallado-v26-consolidado.json` (top-15 de valores por columna para cada país). Generado con `scripts/analizar.py`; tablas con `scripts/generar_reporte_detallado.py`.

*Nota: "llenas" excluye centinelas — una fila cuenta como vacía tanto si la celda no trae valor como si trae `Not Available`, `Not Applicable`, `Unknown` o basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).*

*Nota sobre "¿Se puede aumentar el % de filas llenas?" y "% aumento estimado": "Sí" cuando el pipeline de relleno (`scripts/enriquecer_externo.py`) tiene un método para esa columna; el aumento es la ganancia en puntos porcentuales sobre el total del consolidado (columna "Ganancia" del reporte de completitud, `recursos/reporte-completitud-content-objects-v26-completo.md`) y se muestra igual en las tablas por país. contentTitle y contentLanguage no se rellenan; Publisher y contentIsTitlePresent ya vienen al 100 %.*

*Nota sobre `md5-vacío`: en `contentSeries` algunos vendedores mandan un hash MD5 en vez del nombre de la serie. El valor `d41d8cd98f00b204e9800998ecf8427e` es el MD5 de la cadena vacía, es decir, el vendedor hasheó un texto en blanco; se cuenta como vacío.*

## Total consolidado (todos los países) — 1,473,643 filas · 527,882,754,682 requests

eCPM: 82.6% de filas en cero · media no-cero $4.52 · ponderado $4.13

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 19.8%, OTTera 18.1%, TCL APAC 12.2% | No | — |
| App Name | 92.8% | MovieArk 31.0%, Live TV 21.7%, TCL CHANNEL 12.8% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 92.4%, false 7.6% | No | — |
| contentGenre | 90.2% | Drama 11.7%, *N/A 9.7%*, Horror 4.7% | Sí | +2.8 pp |
| contentTitle | 92.4% | *N/A 7.6%*, {{content_title}} 0.2%, roku 0.2% | No | — |
| contentRating | 75.5% | *N/A 24.5%*, Adults 11.5%, Teen Plus 11.1% | Sí | +0.1 pp |
| contentLanguage | 67.9% | *N/A 32.1%*, en 20.3%, English 20.3% | No | — |
| contentIsLiveStream | 29.9% | *Unknown 35.4%*, *N/A 34.7%*, 1 29.9% | Sí | +18.7 pp |
| contentCategory | 22.5% | *[-7] 77.5%*, [IAB1] 5.2%, [IAB1-22] 2.8% | Sí | +69.2 pp |
| contentLength | 13.5% | *N/A 86.5%*, 5 3.9%, 6 3.7% | No | — |
| contentSeries | 7.6% | *N/A 91.7%*, *md5-vacío 0.7%*, VOD 0.6% | Sí | +7.1 pp |

## México — 443,729 filas (30.1%) · 62.2% de los requests

eCPM: 80.7% de filas en cero · media no-cero $2.52 · ponderado $3.71

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 18.0%, OTTera 11.1%, TCL Springserve 10.5% | No | — |
| App Name | 84.4% | MovieArk 28.2%, Live TV 19.2%, *N/A 15.6%* | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 87.9%, false 12.1% | No | — |
| contentGenre | 89.4% | *N/A 10.6%*, Drama 10.5%, drama 4.8% | Sí | +2.8 pp |
| contentTitle | 87.9% | *N/A 12.1%*, las estrellas 0.5%, {{content_title}} 0.3% | No | — |
| contentRating | 72.3% | *N/A 27.6%*, Teen Plus 12.1%, Adults 9.0% | Sí | +0.1 pp |
| contentLanguage | 64.5% | *N/A 35.4%*, es 16.0%, Spanish 15.9% | No | — |
| contentIsLiveStream | 27.9% | *N/A 38.4%*, *Unknown 33.8%*, 1 27.9% | Sí | +18.7 pp |
| contentCategory | 26.2% | *[-7] 73.8%*, [IAB1] 5.3%, [IAB12] 3.9% | Sí | +69.2 pp |
| contentLength | 17.4% | *N/A 82.6%*, 6 5.6%, 5 4.7% | No | — |
| contentSeries | 9.6% | *N/A 89.2%*, *md5-vacío 1.2%*, VOD 0.5% | Sí | +7.1 pp |

## Colombia — 154,752 filas (10.5%) · 7.3% de los requests

eCPM: 82.0% de filas en cero · media no-cero $3.88 · ponderado $4.39

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 33.1%, OTTera 15.6%, TCL APAC 11.9% | No | — |
| App Name | 97.1% | MovieArk 31.8%, Live TV 28.1%, TCL CHANNEL 14.1% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 94.2%, false 5.8% | No | — |
| contentGenre | 89.7% | Drama 13.3%, *N/A 10.2%*, Horror 5.4% | Sí | +2.8 pp |
| contentTitle | 94.2% | *N/A 5.8%*, {{content_title}} 0.5%, life & me 0.2% | No | — |
| contentRating | 71.7% | *N/A 28.3%*, Adults 11.6%, Teen Plus 10.6% | Sí | +0.1 pp |
| contentLanguage | 56.3% | *N/A 43.7%*, English 19.7%, en 17.1% | No | — |
| contentIsLiveStream | 26.3% | *Unknown 37.6%*, *N/A 36.1%*, 1 26.3% | Sí | +18.7 pp |
| contentCategory | 21.7% | *[-7] 78.3%*, [IAB1] 5.1%, [IAB1-22] 2.4% | Sí | +69.2 pp |
| contentLength | 12.1% | *N/A 87.9%*, 4 3.5%, 5 3.5% | No | — |
| contentSeries | 7.2% | *N/A 92.7%*, VOD 0.8%, {{CONTENT_SERIES}} 0.4% | Sí | +7.1 pp |

## Chile — 160,464 filas (10.9%) · 5.6% de los requests

eCPM: 82.3% de filas en cero · media no-cero $6.31 · ponderado $6.06

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 24.4%, TCL Springserve 17.6%, TCL APAC 14.0% | No | — |
| App Name | 95.6% | MovieArk 45.6%, Live TV 29.9%, TCL CHANNEL 6.5% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 96.4%, false 3.6% | No | — |
| contentGenre | 90.8% | Drama 11.8%, *N/A 9.2%*, Horror 5.1% | Sí | +2.8 pp |
| contentTitle | 96.3% | *N/A 3.6%*, {{content_title}} 0.3%, catalunya �ber alles! 0.2% | No | — |
| contentRating | 71.7% | *N/A 28.3%*, Adults 12.2%, Teen Plus 8.7% | Sí | +0.1 pp |
| contentLanguage | 62.5% | *N/A 37.5%*, en 22.3%, English 21.0% | No | — |
| contentIsLiveStream | 20.5% | *N/A 43.0%*, *Unknown 36.5%*, 1 20.5% | Sí | +18.7 pp |
| contentCategory | 15.3% | *[-7] 84.7%*, [IAB1] 5.4%, [IAB17] 1.0% | Sí | +69.2 pp |
| contentLength | 9.0% | *N/A 91.0%*, 4 3.2%, 5 2.4% | No | — |
| contentSeries | 5.9% | *N/A 94.1%*, VOD 0.8%, {{CONTENT_SERIES}} 0.3% | Sí | +7.1 pp |
