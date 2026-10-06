# Content Objects por país: México, Colombia y Chile (consolidado v10 a v23)

**Fuente:** `inventory-consolidado-v10-a-v23.csv` — 1,377,006 filas únicas, 604,322,292,147 requests (métricas del corte v23, ventana 20 sep–4 oct 2026; v23 aportó 32,377 combinaciones nuevas). Solo v23: 512,000 filas, 451,484,559,785 requests.
**Data completa:** `recursos/reporte-content-objects-detallado-v23-consolidado.json` (top-15 de valores por columna para cada país). Generado con `scripts/analizar.py`; tablas con `scripts/generar_reporte_detallado.py`.

*Nota: "llenas" excluye centinelas — una fila cuenta como vacía tanto si la celda no trae valor como si trae `Not Available`, `Not Applicable`, `Unknown` o basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).*

*Nota sobre "¿Se puede aumentar el % de filas llenas?" y "% aumento estimado": "Sí" cuando el pipeline de relleno (`scripts/enriquecer_externo.py`) tiene un método para esa columna; el aumento es la ganancia en puntos porcentuales sobre el total del consolidado (columna "Ganancia" del reporte de completitud, `recursos/reporte-completitud-content-objects-v23-completo.md`) y se muestra igual en las tablas por país. contentTitle y contentLanguage no se rellenan; Publisher y contentIsTitlePresent ya vienen al 100 %.*

*Nota sobre `md5-vacío`: en `contentSeries` algunos vendedores mandan un hash MD5 en vez del nombre de la serie. El valor `d41d8cd98f00b204e9800998ecf8427e` es el MD5 de la cadena vacía, es decir, el vendedor hasheó un texto en blanco; se cuenta como vacío.*

## Total consolidado (todos los países) — 1,377,006 filas · 604,322,292,147 requests

eCPM: 81.4% de filas en cero · media no-cero $4.16 · ponderado $3.76

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 19.9%, OTTera 19.3%, TCL Springserve 12.0% | No | — |
| App Name | 93.2% | MovieArk 32.0%, Live TV 22.2%, TCL CHANNEL 12.5% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 92.9%, false 7.1% | No | — |
| contentGenre | 90.7% | Drama 11.2%, *N/A 9.3%*, drama 4.7% | Sí | +6.0 pp |
| contentTitle | 92.9% | *N/A 7.1%*, {{content_title}} 0.2%, roku 0.2% | No | — |
| contentRating | 75.4% | *N/A 24.6%*, Adults 10.9%, Teen Plus 10.2% | Sí | +7.0 pp |
| contentLanguage | 67.3% | *N/A 32.6%*, en 21.7%, English 19.2% | No | — |
| contentIsLiveStream | 29.6% | *Unknown 36.5%*, *N/A 33.9%*, 1 29.6% | Sí | +19.2 pp |
| contentCategory | 21.9% | *[-7] 78.1%*, [IAB1] 5.2%, [IAB1-22] 3.0% | Sí | +71.0 pp |
| contentLength | 12.9% | *N/A 87.1%*, 5 3.6%, 6 3.5% | Sí | +36.7 pp |
| contentSeries | 6.9% | *N/A 92.4%*, *md5-vacío 0.7%*, VOD 0.6% | Sí | +7.6 pp |

## México — 408,487 filas (29.7%) · 59.0% de los requests

eCPM: 79.2% de filas en cero · media no-cero $2.09 · ponderado $3.28

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 17.7%, OTTera 12.0%, TCL Springserve 11.1% | No | — |
| App Name | 85.0% | MovieArk 28.8%, Live TV 20.4%, *N/A 15.0%* | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 87.8%, false 12.2% | No | — |
| contentGenre | 89.9% | *N/A 10.1%*, Drama 10.0%, drama 5.2% | Sí | +6.0 pp |
| contentTitle | 87.8% | *N/A 12.2%*, las estrellas 0.5%, canal 5 0.3% | No | — |
| contentRating | 72.6% | *N/A 27.4%*, Teen Plus 11.0%, Adults 8.7% | Sí | +7.0 pp |
| contentLanguage | 63.8% | *N/A 36.0%*, es 17.3%, en 16.1% | No | — |
| contentIsLiveStream | 27.2% | *N/A 37.9%*, *Unknown 34.9%*, 1 27.2% | Sí | +19.2 pp |
| contentCategory | 25.4% | *[-7] 74.6%*, [IAB1] 4.9%, [IAB12] 3.9% | Sí | +71.0 pp |
| contentLength | 17.1% | *N/A 82.9%*, 6 5.6%, 5 4.4% | Sí | +36.7 pp |
| contentSeries | 8.3% | *N/A 90.4%*, *md5-vacío 1.2%*, VOD 0.5% | Sí | +7.6 pp |

## Colombia — 143,820 filas (10.4%) · 7.8% de los requests

eCPM: 81.7% de filas en cero · media no-cero $3.02 · ponderado $2.94

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 34.1%, OTTera 16.8%, TCL APAC 11.9% | No | — |
| App Name | 97.3% | MovieArk 33.2%, Live TV 29.5%, TCL CHANNEL 12.8% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 94.8%, false 5.2% | No | — |
| contentGenre | 90.3% | Drama 12.9%, *N/A 9.6%*, Horror 5.3% | Sí | +6.0 pp |
| contentTitle | 94.8% | *N/A 5.2%*, {{content_title}} 0.4%, life & me 0.2% | No | — |
| contentRating | 71.9% | *N/A 28.1%*, Adults 11.4%, Teen Plus 9.8% | Sí | +7.0 pp |
| contentLanguage | 55.9% | *N/A 44.1%*, English 19.1%, en 18.4% | No | — |
| contentIsLiveStream | 26.4% | *Unknown 39.1%*, *N/A 34.5%*, 1 26.4% | Sí | +19.2 pp |
| contentCategory | 21.8% | *[-7] 78.2%*, [IAB1] 5.4%, [IAB1-22] 2.5% | Sí | +71.0 pp |
| contentLength | 11.5% | *N/A 88.5%*, 4 3.5%, 5 3.3% | Sí | +36.7 pp |
| contentSeries | 6.7% | *N/A 93.3%*, VOD 0.8%, {{CONTENT_SERIES}} 0.3% | Sí | +7.6 pp |

## Chile — 153,686 filas (11.2%) · 6.1% de los requests

eCPM: 80.0% de filas en cero · media no-cero $6.41 · ponderado $5.72

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 25.0%, TCL Springserve 17.6%, OTTera 14.1% | No | — |
| App Name | 95.7% | MovieArk 46.4%, Live TV 30.2%, TCL CHANNEL 6.1% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 96.9%, false 3.1% | No | — |
| contentGenre | 90.9% | Drama 11.5%, *N/A 9.1%*, Horror 4.9% | Sí | +6.0 pp |
| contentTitle | 96.9% | *N/A 3.1%*, {{content_title}} 0.2%, catalunya �ber alles! 0.2% | No | — |
| contentRating | 71.3% | *N/A 28.7%*, Adults 11.8%, Teen Plus 8.2% | Sí | +7.0 pp |
| contentLanguage | 61.6% | *N/A 38.4%*, en 23.3%, English 20.1% | No | — |
| contentIsLiveStream | 19.9% | *N/A 42.9%*, *Unknown 37.3%*, 1 19.9% | Sí | +19.2 pp |
| contentCategory | 15.0% | *[-7] 85.0%*, [IAB1] 5.6%, [IAB17] 1.0% | Sí | +71.0 pp |
| contentLength | 8.6% | *N/A 91.4%*, 4 3.1%, 5 2.3% | Sí | +36.7 pp |
| contentSeries | 5.6% | *N/A 94.3%*, VOD 0.8%, {{CONTENT_SERIES}} 0.2% | Sí | +7.6 pp |
