# Content Objects por país: México, Colombia y Chile (consolidado v10 a v25)

**Fuente:** `inventory-consolidado-v10-a-v25.csv` — 1,443,390 filas únicas, 541,945,571,178 requests (métricas del corte v25, ventana 26 sep–10 oct 2026; v25 aportó 46,727 combinaciones nuevas). Solo v25: 512,000 filas, 376,752,281,894 requests.
**Data completa:** `recursos/reporte-content-objects-detallado-v25-consolidado.json` (top-15 de valores por columna para cada país). Generado con `scripts/analizar.py`; tablas con `scripts/generar_reporte_detallado.py`.

*Nota: "llenas" excluye centinelas — una fila cuenta como vacía tanto si la celda no trae valor como si trae `Not Available`, `Not Applicable`, `Unknown` o basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).*

*Nota sobre "¿Se puede aumentar el % de filas llenas?" y "% aumento estimado": "Sí" cuando el pipeline de relleno (`scripts/enriquecer_externo.py`) tiene un método para esa columna; el aumento es la ganancia en puntos porcentuales sobre el total del consolidado (columna "Ganancia" del reporte de completitud, `recursos/reporte-completitud-content-objects-v25-completo.md`) y se muestra igual en las tablas por país. contentTitle y contentLanguage no se rellenan; Publisher y contentIsTitlePresent ya vienen al 100 %.*

*Nota sobre `md5-vacío`: en `contentSeries` algunos vendedores mandan un hash MD5 en vez del nombre de la serie. El valor `d41d8cd98f00b204e9800998ecf8427e` es el MD5 de la cadena vacía, es decir, el vendedor hasheó un texto en blanco; se cuenta como vacío.*

## Total consolidado (todos los países) — 1,443,390 filas · 541,945,571,178 requests

eCPM: 81.9% de filas en cero · media no-cero $4.34 · ponderado $3.97

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 19.9%, OTTera 18.4%, TCL APAC 12.2% | No | — |
| App Name | 93.0% | MovieArk 31.3%, Live TV 22.0%, TCL CHANNEL 12.5% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 92.5%, false 7.5% | No | — |
| contentGenre | 90.4% | Drama 11.6%, *N/A 9.6%*, Horror 4.6% | Sí | +2.7 pp |
| contentTitle | 92.5% | *N/A 7.5%*, {{content_title}} 0.2%, roku 0.2% | No | — |
| contentRating | 75.7% | *N/A 24.3%*, Adults 11.4%, Teen Plus 10.9% | Sí | +0.1 pp |
| contentLanguage | 67.9% | *N/A 32.1%*, en 20.7%, English 20.1% | No | — |
| contentIsLiveStream | 30.0% | *Unknown 35.8%*, *N/A 34.3%*, 1 30.0% | Sí | +18.8 pp |
| contentCategory | 22.4% | *[-7] 77.6%*, [IAB1] 5.2%, [IAB1-22] 2.9% | Sí | +69.4 pp |
| contentLength | 13.4% | *N/A 86.6%*, 5 3.8%, 6 3.7% | No | — |
| contentSeries | 7.4% | *N/A 91.9%*, *md5-vacío 0.7%*, VOD 0.6% | Sí | +7.1 pp |

## México — 430,242 filas (29.8%) · 60.9% de los requests

eCPM: 80.1% de filas en cero · media no-cero $2.34 · ponderado $3.57

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 17.9%, OTTera 11.5%, TCL Springserve 10.8% | No | — |
| App Name | 84.5% | MovieArk 28.4%, Live TV 19.7%, *N/A 15.5%* | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 87.8%, false 12.2% | No | — |
| contentGenre | 89.5% | *N/A 10.4%*, Drama 10.3%, drama 5.0% | Sí | +2.7 pp |
| contentTitle | 87.8% | *N/A 12.2%*, las estrellas 0.5%, {{content_title}} 0.3% | No | — |
| contentRating | 72.8% | *N/A 27.1%*, Teen Plus 11.8%, Adults 9.0% | Sí | +0.1 pp |
| contentLanguage | 64.5% | *N/A 35.4%*, es 16.5%, en 15.3% | No | — |
| contentIsLiveStream | 27.9% | *N/A 37.9%*, *Unknown 34.2%*, 1 27.9% | Sí | +18.8 pp |
| contentCategory | 26.1% | *[-7] 73.9%*, [IAB1] 5.2%, [IAB12] 3.9% | Sí | +69.4 pp |
| contentLength | 17.4% | *N/A 82.6%*, 6 5.7%, 5 4.6% | No | — |
| contentSeries | 9.3% | *N/A 89.5%*, *md5-vacío 1.2%*, VOD 0.5% | Sí | +7.1 pp |

## Colombia — 150,486 filas (10.4%) · 7.4% de los requests

eCPM: 81.6% de filas en cero · media no-cero $3.38 · ponderado $3.56

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 33.8%, OTTera 16.0%, TCL APAC 12.0% | No | — |
| App Name | 97.1% | MovieArk 32.2%, Live TV 28.7%, TCL CHANNEL 13.4% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 94.3%, false 5.7% | No | — |
| contentGenre | 89.9% | Drama 13.0%, *N/A 10.1%*, Horror 5.3% | Sí | +2.7 pp |
| contentTitle | 94.3% | *N/A 5.7%*, {{content_title}} 0.5%, life & me 0.2% | No | — |
| contentRating | 72.1% | *N/A 27.9%*, Adults 11.6%, Teen Plus 10.3% | Sí | +0.1 pp |
| contentLanguage | 56.4% | *N/A 43.6%*, English 19.5%, en 17.6% | No | — |
| contentIsLiveStream | 26.5% | *Unknown 38.2%*, *N/A 35.3%*, 1 26.5% | Sí | +18.8 pp |
| contentCategory | 21.9% | *[-7] 78.1%*, [IAB1] 5.2%, [IAB1-22] 2.5% | Sí | +69.4 pp |
| contentLength | 12.0% | *N/A 88.0%*, 4 3.5%, 5 3.5% | No | — |
| contentSeries | 7.1% | *N/A 92.8%*, VOD 0.8%, {{CONTENT_SERIES}} 0.4% | Sí | +7.1 pp |

## Chile — 158,556 filas (11.0%) · 5.8% de los requests

eCPM: 81.1% de filas en cero · media no-cero $6.49 · ponderado $6.09

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 24.4%, TCL Springserve 17.6%, TCL APAC 14.0% | No | — |
| App Name | 95.6% | MovieArk 45.8%, Live TV 30.0%, TCL CHANNEL 6.3% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 96.4%, false 3.6% | No | — |
| contentGenre | 90.8% | Drama 11.7%, *N/A 9.1%*, Horror 5.0% | Sí | +2.7 pp |
| contentTitle | 96.4% | *N/A 3.6%*, {{content_title}} 0.3%, catalunya �ber alles! 0.2% | No | — |
| contentRating | 71.7% | *N/A 28.4%*, Adults 12.1%, Teen Plus 8.6% | Sí | +0.1 pp |
| contentLanguage | 62.4% | *N/A 37.6%*, en 22.6%, English 20.8% | No | — |
| contentIsLiveStream | 20.5% | *N/A 42.8%*, *Unknown 36.7%*, 1 20.5% | Sí | +18.8 pp |
| contentCategory | 15.3% | *[-7] 84.7%*, [IAB1] 5.5%, [IAB17] 1.0% | Sí | +69.4 pp |
| contentLength | 9.0% | *N/A 91.0%*, 4 3.2%, 5 2.4% | No | — |
| contentSeries | 5.8% | *N/A 94.2%*, VOD 0.8%, {{CONTENT_SERIES}} 0.3% | Sí | +7.1 pp |
