# Content Objects por país: México, Colombia y Chile (consolidado v10 a v19)

**Fuente:** `inventory-consolidado-v10-a-v19.csv` — 1,158,509 filas únicas, 482,736,715,920 requests (métricas del corte v19, ventana 31 ago–14 sep 2026; v19 aportó 86,669 combinaciones nuevas). Solo v19: 512,000 filas, 388,392,618,080 requests.
**Data completa:** `recursos/reporte-content-objects-detallado-v19-consolidado.json` (top-15 de valores por columna para cada país). Generado con `scripts/analizar.py`; tablas con `scripts/generar_reporte_detallado.py`.

*Nota: "llenas" excluye centinelas — una fila cuenta como vacía tanto si la celda no trae valor como si trae `Not Available`, `Not Applicable`, `Unknown` o basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).*

*Nota sobre "¿Se puede aumentar el % de filas llenas?" y "% aumento estimado": "Sí" cuando el pipeline de relleno (`scripts/enriquecer_externo.py`) tiene un método para esa columna; el aumento es la ganancia en puntos porcentuales sobre el total del consolidado (columna "Ganancia" del reporte de completitud, `recursos/reporte-completitud-content-objects-v19-completo.md`) y se muestra igual en las tablas por país. contentTitle y contentLanguage no se rellenan; Publisher y contentIsTitlePresent ya vienen al 100 %.*

*Nota sobre `md5-vacío`: en `contentSeries` algunos vendedores mandan un hash MD5 en vez del nombre de la serie. El valor `d41d8cd98f00b204e9800998ecf8427e` es el MD5 de la cadena vacía, es decir, el vendedor hasheó un texto en blanco; se cuenta como vacío.*

## Total consolidado (todos los países) — 1,158,509 filas · 482,736,715,920 requests

eCPM: 82.2% de filas en cero · media no-cero $4.54 · ponderado $4.05

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | OTTera 20.2%, iion 19.3%, TCL Springserve 12.4% | No | — |
| App Name | 93.7% | MovieArk 34.4%, Live TV 22.4%, TCL CHANNEL 11.9% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 93.2%, false 6.8% | No | — |
| contentGenre | 91.7% | Drama 10.0%, *N/A 8.2%*, drama 5.6% | Sí | +5.5 pp |
| contentTitle | 93.2% | *N/A 6.8%*, roku 0.2%, epg 0.1% | No | — |
| contentRating | 74.3% | *N/A 25.7%*, Adults 8.9%, Teen Plus 7.7% | Sí | +8.4 pp |
| contentLanguage | 65.7% | *N/A 34.3%*, en 25.9%, es 14.8% | No | — |
| contentIsLiveStream | 29.2% | *Unknown 37.1%*, *N/A 33.7%*, 1 29.2% | Sí | +19.7 pp |
| contentCategory | 21.7% | *[-7] 78.3%*, [IAB1] 5.3%, [IAB1-22] 2.9% | Sí | +71.5 pp |
| contentLength | 11.9% | *N/A 88.1%*, 5 3.3%, 4 3.1% | Sí | +35.9 pp |
| contentSeries | 6.5% | *N/A 92.8%*, *md5-vacío 0.7%*, VOD 0.6% | Sí | +7.6 pp |

## México — 347,432 filas (30.0%) · 59.2% de los requests

eCPM: 79.8% de filas en cero · media no-cero $2.08 · ponderado $3.32

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 17.2%, OTTera 13.2%, TCL Springserve 11.9% | No | — |
| App Name | 87.0% | MovieArk 31.8%, Live TV 21.1%, *N/A 13.0%* | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 87.3%, false 12.7% | No | — |
| contentGenre | 90.8% | *N/A 9.2%*, Drama 9.2%, drama 6.2% | Sí | +5.5 pp |
| contentTitle | 87.3% | *N/A 12.7%*, las estrellas 0.4%, canal 5 0.3% | No | — |
| contentRating | 71.0% | *N/A 28.9%*, Teen Plus 8.2%, tv-14 7.6% | Sí | +8.4 pp |
| contentLanguage | 62.3% | *N/A 37.5%*, es 20.4%, en 19.0% | No | — |
| contentIsLiveStream | 25.4% | *N/A 38.9%*, *Unknown 35.6%*, 1 25.4% | Sí | +19.7 pp |
| contentCategory | 24.3% | *[-7] 75.7%*, [IAB1] 4.4%, [IAB12] 4.2% | Sí | +71.5 pp |
| contentLength | 15.7% | *N/A 84.3%*, 6 5.0%, 5 3.7% | Sí | +35.9 pp |
| contentSeries | 6.9% | *N/A 91.9%*, *md5-vacío 1.2%*, VOD 0.5% | Sí | +7.6 pp |

## Colombia — 122,400 filas (10.6%) · 7.2% de los requests

eCPM: 85.4% de filas en cero · media no-cero $3.98 · ponderado $4.47

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 32.6%, OTTera 17.4%, TCL APAC 11.6% | No | — |
| App Name | 97.4% | MovieArk 37.3%, Live TV 30.2%, TCL CHANNEL 11.4% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 95.4%, false 4.6% | No | — |
| contentGenre | 91.5% | Drama 11.5%, *N/A 8.5%*, drama 5.0% | Sí | +5.5 pp |
| contentTitle | 95.4% | *N/A 4.6%*, {{content_title}} 0.3%, life & me 0.2% | No | — |
| contentRating | 70.5% | *N/A 29.5%*, Adults 9.7%, Teen Plus 7.8% | Sí | +8.4 pp |
| contentLanguage | 52.5% | *N/A 47.5%*, en 21.6%, English 14.5% | No | — |
| contentIsLiveStream | 26.6% | *Unknown 40.0%*, *N/A 33.4%*, 1 26.6% | Sí | +19.7 pp |
| contentCategory | 21.8% | *[-7] 78.2%*, [IAB1] 6.0%, [IAB1, IAB1-5] 2.2% | Sí | +71.5 pp |
| contentLength | 10.5% | *N/A 89.5%*, 4 3.6%, 5 3.0% | Sí | +35.9 pp |
| contentSeries | 6.3% | *N/A 93.6%*, VOD 0.8%, {{CONTENT_SERIES}} 0.2% | Sí | +7.6 pp |

## Chile — 133,317 filas (11.5%) · 5.8% de los requests

eCPM: 78.5% de filas en cero · media no-cero $6.45 · ponderado $5.87

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 25.0%, TCL Springserve 17.7%, OTTera 15.0% | No | — |
| App Name | 95.5% | MovieArk 47.6%, Live TV 31.0%, *N/A 4.5%* | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 97.1%, false 2.9% | No | — |
| contentGenre | 91.6% | Drama 10.7%, *N/A 8.4%*, Horror 4.6% | Sí | +5.5 pp |
| contentTitle | 97.1% | *N/A 2.9%*, catalunya �ber alles! 0.2%, {{content_title}} 0.2% | No | — |
| contentRating | 71.1% | *N/A 28.9%*, Adults 10.4%, tv-ma 6.9% | Sí | +8.4 pp |
| contentLanguage | 61.2% | *N/A 38.8%*, en 26.9%, English 16.7% | No | — |
| contentIsLiveStream | 19.0% | *N/A 42.2%*, *Unknown 38.8%*, 1 19.0% | Sí | +19.7 pp |
| contentCategory | 15.3% | *[-7] 84.7%*, [IAB1] 6.2%, [IAB17] 1.0% | Sí | +71.5 pp |
| contentLength | 8.3% | *N/A 91.7%*, 4 3.3%, 5 2.3% | Sí | +35.9 pp |
| contentSeries | 5.8% | *N/A 94.2%*, VOD 0.9%, {{CONTENT_SERIES}} 0.2% | Sí | +7.6 pp |
