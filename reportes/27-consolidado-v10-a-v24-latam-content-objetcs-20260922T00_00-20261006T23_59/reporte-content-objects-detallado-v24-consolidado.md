# Content Objects por país: México, Colombia y Chile (consolidado v10 a v24)

**Fuente:** `inventory-consolidado-v10-a-v24.csv` — 1,396,663 filas únicas, 583,047,756,539 requests (métricas del corte v24, ventana 22 sep–6 oct 2026; v24 aportó 19,657 combinaciones nuevas). Solo v24: 512,000 filas, 425,921,024,811 requests.
**Data completa:** `recursos/reporte-content-objects-detallado-v24-consolidado.json` (top-15 de valores por columna para cada país). Generado con `scripts/analizar.py`; tablas con `scripts/generar_reporte_detallado.py`.

*Nota: "llenas" excluye centinelas — una fila cuenta como vacía tanto si la celda no trae valor como si trae `Not Available`, `Not Applicable`, `Unknown` o basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).*

*Nota sobre "¿Se puede aumentar el % de filas llenas?" y "% aumento estimado": "Sí" cuando el pipeline de relleno (`scripts/enriquecer_externo.py`) tiene un método para esa columna; el aumento es la ganancia en puntos porcentuales sobre el total del consolidado (columna "Ganancia" del reporte de completitud, `recursos/reporte-completitud-content-objects-v24-completo.md`) y se muestra igual en las tablas por país. contentTitle y contentLanguage no se rellenan; Publisher y contentIsTitlePresent ya vienen al 100 %.*

*Nota sobre `md5-vacío`: en `contentSeries` algunos vendedores mandan un hash MD5 en vez del nombre de la serie. El valor `d41d8cd98f00b204e9800998ecf8427e` es el MD5 de la cadena vacía, es decir, el vendedor hasheó un texto en blanco; se cuenta como vacío.*

## Total consolidado (todos los países) — 1,396,663 filas · 583,047,756,539 requests

eCPM: 81.5% de filas en cero · media no-cero $4.23 · ponderado $3.81

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 19.9%, OTTera 19.0%, TCL APAC 12.0% | No | — |
| App Name | 93.2% | MovieArk 31.8%, Live TV 22.2%, TCL CHANNEL 12.5% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 92.7%, false 7.3% | No | — |
| contentGenre | 90.6% | Drama 11.3%, *N/A 9.4%*, drama 4.6% | Sí | +2.7 pp |
| contentTitle | 92.7% | *N/A 7.3%*, {{content_title}} 0.2%, roku 0.2% | No | — |
| contentRating | 75.5% | *N/A 24.5%*, Adults 11.1%, Teen Plus 10.4% | Sí | +0.1 pp |
| contentLanguage | 67.5% | *N/A 32.5%*, en 21.4%, English 19.4% | No | — |
| contentIsLiveStream | 29.8% | *Unknown 36.3%*, *N/A 33.9%*, 1 29.8% | Sí | +19.1 pp |
| contentCategory | 22.1% | *[-7] 77.9%*, [IAB1] 5.2%, [IAB1-22] 3.0% | Sí | +69.7 pp |
| contentLength | 13.1% | *N/A 86.9%*, 5 3.7%, 6 3.6% | No | — |
| contentSeries | 7.0% | *N/A 92.3%*, *md5-vacío 0.7%*, VOD 0.6% | Sí | +7.2 pp |

## México — 413,895 filas (29.6%) · 59.2% de los requests

eCPM: 79.7% de filas en cero · media no-cero $2.12 · ponderado $3.35

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 17.6%, OTTera 11.9%, TCL Springserve 11.0% | No | — |
| App Name | 84.9% | MovieArk 28.5%, Live TV 20.2%, *N/A 15.1%* | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 87.7%, false 12.3% | No | — |
| contentGenre | 89.8% | *N/A 10.2%*, Drama 10.1%, drama 5.2% | Sí | +2.7 pp |
| contentTitle | 87.7% | *N/A 12.3%*, las estrellas 0.5%, canal 5 0.3% | No | — |
| contentRating | 72.7% | *N/A 27.3%*, Teen Plus 11.3%, Adults 8.7% | Sí | +0.1 pp |
| contentLanguage | 64.0% | *N/A 35.8%*, es 17.1%, en 15.9% | No | — |
| contentIsLiveStream | 27.6% | *N/A 37.7%*, *Unknown 34.7%*, 1 27.6% | Sí | +19.1 pp |
| contentCategory | 25.7% | *[-7] 74.3%*, [IAB1] 5.0%, [IAB12] 3.9% | Sí | +69.7 pp |
| contentLength | 17.2% | *N/A 82.8%*, 6 5.6%, 5 4.5% | No | — |
| contentSeries | 8.6% | *N/A 90.2%*, *md5-vacío 1.2%*, VOD 0.5% | Sí | +7.2 pp |

## Colombia — 146,020 filas (10.4%) · 7.7% de los requests

eCPM: 81.6% de filas en cero · media no-cero $3.04 · ponderado $3.00

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 34.2%, OTTera 16.5%, TCL APAC 11.9% | No | — |
| App Name | 97.2% | MovieArk 32.9%, Live TV 29.3%, TCL CHANNEL 13.1% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 94.5%, false 5.5% | No | — |
| contentGenre | 90.3% | Drama 13.0%, *N/A 9.7%*, Horror 5.3% | Sí | +2.7 pp |
| contentTitle | 94.5% | *N/A 5.5%*, {{content_title}} 0.4%, life & me 0.2% | No | — |
| contentRating | 72.1% | *N/A 27.9%*, Adults 11.5%, Teen Plus 10.0% | Sí | +0.1 pp |
| contentLanguage | 56.0% | *N/A 44.0%*, English 19.2%, en 18.1% | No | — |
| contentIsLiveStream | 26.4% | *Unknown 38.8%*, *N/A 34.9%*, 1 26.4% | Sí | +19.1 pp |
| contentCategory | 21.9% | *[-7] 78.1%*, [IAB1] 5.3%, [IAB1-22] 2.5% | Sí | +69.7 pp |
| contentLength | 11.7% | *N/A 88.3%*, 4 3.5%, 5 3.4% | No | — |
| contentSeries | 6.8% | *N/A 93.2%*, VOD 0.8%, {{CONTENT_SERIES}} 0.4% | Sí | +7.2 pp |

## Chile — 155,307 filas (11.1%) · 6.2% de los requests

eCPM: 80.1% de filas en cero · media no-cero $6.47 · ponderado $5.79

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 24.8%, TCL Springserve 17.6%, OTTera 14.0% | No | — |
| App Name | 95.7% | MovieArk 46.1%, Live TV 30.2%, TCL CHANNEL 6.2% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 96.6%, false 3.4% | No | — |
| contentGenre | 90.9% | Drama 11.5%, *N/A 9.1%*, Horror 5.0% | Sí | +2.7 pp |
| contentTitle | 96.6% | *N/A 3.4%*, {{content_title}} 0.2%, catalunya �ber alles! 0.2% | No | — |
| contentRating | 71.4% | *N/A 28.6%*, Adults 11.8%, Teen Plus 8.3% | Sí | +0.1 pp |
| contentLanguage | 61.9% | *N/A 38.1%*, en 23.1%, English 20.4% | No | — |
| contentIsLiveStream | 20.1% | *N/A 42.8%*, *Unknown 37.1%*, 1 20.1% | Sí | +19.1 pp |
| contentCategory | 15.2% | *[-7] 84.8%*, [IAB1] 5.5%, [IAB17] 1.0% | Sí | +69.7 pp |
| contentLength | 8.8% | *N/A 91.2%*, 4 3.2%, 5 2.3% | No | — |
| contentSeries | 5.7% | *N/A 94.2%*, VOD 0.8%, {{CONTENT_SERIES}} 0.2% | Sí | +7.2 pp |
