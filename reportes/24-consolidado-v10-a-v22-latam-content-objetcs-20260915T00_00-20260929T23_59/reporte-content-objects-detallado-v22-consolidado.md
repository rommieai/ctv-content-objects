# Content Objects por país: México, Colombia y Chile (consolidado v10 a v22)

**Fuente:** `inventory-consolidado-v10-a-v22.csv` — 1,344,629 filas únicas, 622,384,767,599 requests (métricas del corte v22, ventana 15–29 sep 2026; v22 aportó 46,484 combinaciones nuevas). Solo v22: 512,000 filas, 472,750,396,159 requests.
**Data completa:** `recursos/reporte-content-objects-detallado-v22-consolidado.json` (top-15 de valores por columna para cada país). Generado con `scripts/analizar.py`; tablas con `scripts/generar_reporte_detallado.py`.

*Nota: "llenas" excluye centinelas — una fila cuenta como vacía tanto si la celda no trae valor como si trae `Not Available`, `Not Applicable`, `Unknown` o basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).*

*Nota sobre "¿Se puede aumentar el % de filas llenas?" y "% aumento estimado": "Sí" cuando el pipeline de relleno (`scripts/enriquecer_externo.py`) tiene un método para esa columna; el aumento es la ganancia en puntos porcentuales sobre el total del consolidado (columna "Ganancia" del reporte de completitud, `recursos/reporte-completitud-content-objects-v22-completo.md`) y se muestra igual en las tablas por país. contentTitle y contentLanguage no se rellenan; Publisher y contentIsTitlePresent ya vienen al 100 %.*

*Nota sobre `md5-vacío`: en `contentSeries` algunos vendedores mandan un hash MD5 en vez del nombre de la serie. El valor `d41d8cd98f00b204e9800998ecf8427e` es el MD5 de la cadena vacía, es decir, el vendedor hasheó un texto en blanco; se cuenta como vacío.*

## Total consolidado (todos los países) — 1,344,629 filas · 622,384,767,599 requests

eCPM: 81.0% de filas en cero · media no-cero $4.13 · ponderado $3.67

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 20.0%, OTTera 19.6%, TCL Springserve 12.1% | No | — |
| App Name | 93.3% | MovieArk 32.5%, Live TV 22.2%, TCL CHANNEL 12.5% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 93.0%, false 7.0% | No | — |
| contentGenre | 90.8% | Drama 11.0%, *N/A 9.2%*, drama 4.8% | Sí | +6.0 pp |
| contentTitle | 93.0% | *N/A 7.0%*, roku 0.2%, {{content_title}} 0.2% | No | — |
| contentRating | 75.2% | *N/A 24.8%*, Adults 10.7%, Teen Plus 9.8% | Sí | +7.1 pp |
| contentLanguage | 67.0% | *N/A 32.9%*, en 22.3%, English 18.6% | No | — |
| contentIsLiveStream | 29.5% | *Unknown 36.8%*, *N/A 33.7%*, 1 29.5% | Sí | +19.2 pp |
| contentCategory | 21.9% | *[-7] 78.1%*, [IAB1] 5.2%, [IAB1-22] 3.0% | Sí | +71.1 pp |
| contentLength | 12.6% | *N/A 87.4%*, 5 3.5%, 6 3.4% | Sí | +36.8 pp |
| contentSeries | 6.8% | *N/A 92.5%*, *md5-vacío 0.7%*, VOD 0.6% | Sí | +7.6 pp |

## México — 397,781 filas (29.6%) · 58.6% de los requests

eCPM: 78.5% de filas en cero · media no-cero $2.10 · ponderado $3.13

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 17.7%, OTTera 12.2%, TCL Springserve 11.2% | No | — |
| App Name | 85.3% | MovieArk 29.2%, Live TV 20.4%, *N/A 14.7%* | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 87.7%, false 12.3% | No | — |
| contentGenre | 90.0% | *N/A 10.0%*, Drama 9.8%, drama 5.4% | Sí | +6.0 pp |
| contentTitle | 87.7% | *N/A 12.3%*, las estrellas 0.5%, canal 5 0.3% | No | — |
| contentRating | 72.3% | *N/A 27.7%*, Teen Plus 10.6%, Adults 8.4% | Sí | +7.1 pp |
| contentLanguage | 63.5% | *N/A 36.4%*, es 17.8%, en 16.6% | No | — |
| contentIsLiveStream | 26.9% | *N/A 37.9%*, *Unknown 35.2%*, 1 26.9% | Sí | +19.2 pp |
| contentCategory | 25.3% | *[-7] 74.7%*, [IAB1] 4.8%, [IAB12] 4.0% | Sí | +71.1 pp |
| contentLength | 16.8% | *N/A 83.2%*, 6 5.5%, 5 4.3% | Sí | +36.8 pp |
| contentSeries | 8.0% | *N/A 90.7%*, *md5-vacío 1.2%*, VOD 0.5% | Sí | +7.6 pp |

## Colombia — 139,362 filas (10.4%) · 7.8% de los requests

eCPM: 81.7% de filas en cero · media no-cero $2.89 · ponderado $2.65

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 34.2%, OTTera 17.0%, TCL APAC 11.7% | No | — |
| App Name | 97.4% | MovieArk 34.1%, Live TV 29.4%, TCL CHANNEL 12.8% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 95.1%, false 4.9% | No | — |
| contentGenre | 90.5% | Drama 12.5%, *N/A 9.4%*, Horror 5.2% | Sí | +6.0 pp |
| contentTitle | 95.1% | *N/A 4.9%*, {{content_title}} 0.3%, life & me 0.2% | No | — |
| contentRating | 71.5% | *N/A 28.5%*, Adults 11.1%, Teen Plus 9.4% | Sí | +7.1 pp |
| contentLanguage | 55.0% | *N/A 45.0%*, en 19.0%, English 18.2% | No | — |
| contentIsLiveStream | 26.5% | *Unknown 39.6%*, *N/A 33.9%*, 1 26.5% | Sí | +19.2 pp |
| contentCategory | 21.7% | *[-7] 78.3%*, [IAB1] 5.5%, [IAB1-22] 2.3% | Sí | +71.1 pp |
| contentLength | 11.2% | *N/A 88.8%*, 4 3.5%, 5 3.2% | Sí | +36.8 pp |
| contentSeries | 6.5% | *N/A 93.4%*, VOD 0.8%, {{CONTENT_SERIES}} 0.3% | Sí | +7.6 pp |

## Chile — 150,984 filas (11.2%) · 6.2% de los requests

eCPM: 79.4% de filas en cero · media no-cero $6.47 · ponderado $5.59

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 25.4%, TCL Springserve 17.6%, OTTera 14.2% | No | — |
| App Name | 95.8% | MovieArk 46.8%, Live TV 30.2%, TCL CHANNEL 6.0% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 96.9%, false 3.1% | No | — |
| contentGenre | 91.0% | Drama 11.4%, *N/A 9.0%*, Horror 4.8% | Sí | +6.0 pp |
| contentTitle | 96.9% | *N/A 3.1%*, {{content_title}} 0.2%, catalunya �ber alles! 0.2% | No | — |
| contentRating | 71.3% | *N/A 28.7%*, Adults 11.7%, Teen Plus 8.0% | Sí | +7.1 pp |
| contentLanguage | 61.3% | *N/A 38.7%*, en 23.7%, English 19.6% | No | — |
| contentIsLiveStream | 19.6% | *N/A 43.0%*, *Unknown 37.4%*, 1 19.6% | Sí | +19.2 pp |
| contentCategory | 14.8% | *[-7] 85.2%*, [IAB1] 5.6%, [IAB17] 1.0% | Sí | +71.1 pp |
| contentLength | 8.4% | *N/A 91.6%*, 4 3.1%, 5 2.2% | Sí | +36.8 pp |
| contentSeries | 5.5% | *N/A 94.4%*, VOD 0.8%, {{CONTENT_SERIES}} 0.2% | Sí | +7.6 pp |
