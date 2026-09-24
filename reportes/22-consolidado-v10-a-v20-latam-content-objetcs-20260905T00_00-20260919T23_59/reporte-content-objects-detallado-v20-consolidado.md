# Content Objects por país: México, Colombia y Chile (consolidado v10 a v20)

**Fuente:** `inventory-consolidado-v10-a-v20.csv` — 1,272,878 filas únicas, 561,740,400,400 requests (métricas del corte v20, ventana 5–19 sep 2026; v20 aportó 114,369 combinaciones nuevas). Solo v20: 512,000 filas, 420,586,831,200 requests.
**Data completa:** `recursos/reporte-content-objects-detallado-v20-consolidado.json` (top-15 de valores por columna para cada país). Generado con `scripts/analizar.py`; tablas con `scripts/generar_reporte_detallado.py`.

*Nota: "llenas" excluye centinelas — una fila cuenta como vacía tanto si la celda no trae valor como si trae `Not Available`, `Not Applicable`, `Unknown` o basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).*

*Nota sobre "¿Se puede aumentar el % de filas llenas?" y "% aumento estimado": "Sí" cuando el pipeline de relleno (`scripts/enriquecer_externo.py`) tiene un método para esa columna; el aumento es la ganancia en puntos porcentuales sobre el total del consolidado (columna "Ganancia" del reporte de completitud, `recursos/reporte-completitud-content-objects-v20-completo.md`) y se muestra igual en las tablas por país. contentTitle y contentLanguage no se rellenan; Publisher y contentIsTitlePresent ya vienen al 100 %.*

*Nota sobre `md5-vacío`: en `contentSeries` algunos vendedores mandan un hash MD5 en vez del nombre de la serie. El valor `d41d8cd98f00b204e9800998ecf8427e` es el MD5 de la cadena vacía, es decir, el vendedor hasheó un texto en blanco; se cuenta como vacío.*

## Total consolidado (todos los países) — 1,272,878 filas · 561,740,400,400 requests

eCPM: 81.6% de filas en cero · media no-cero $4.34 · ponderado $3.85

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 20.1%, OTTera 19.8%, TCL Springserve 12.3% | No | — |
| App Name | 93.6% | MovieArk 33.6%, Live TV 22.3%, TCL CHANNEL 12.4% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 93.2%, false 6.8% | No | — |
| contentGenre | 91.2% | Drama 10.7%, *N/A 8.8%*, drama 5.1% | Sí | +5.8 pp |
| contentTitle | 93.2% | *N/A 6.8%*, roku 0.2%, epg 0.2% | No | — |
| contentRating | 74.8% | *N/A 25.2%*, Adults 10.1%, Teen Plus 9.0% | Sí | +7.3 pp |
| contentLanguage | 66.2% | *N/A 33.8%*, en 23.5%, English 17.0% | No | — |
| contentIsLiveStream | 29.2% | *Unknown 36.7%*, *N/A 34.0%*, 1 29.2% | Sí | +19.3 pp |
| contentCategory | 21.4% | *[-7] 78.6%*, [IAB1] 5.1%, [IAB1-22] 2.9% | Sí | +71.6 pp |
| contentLength | 12.0% | *N/A 88.0%*, 5 3.3%, 6 3.1% | Sí | +36.2 pp |
| contentSeries | 6.5% | *N/A 92.8%*, *md5-vacío 0.7%*, VOD 0.6% | Sí | +7.7 pp |

## México — 376,062 filas (29.5%) · 59.2% de los requests

eCPM: 79.0% de filas en cero · media no-cero $2.11 · ponderado $3.25

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 18.0%, OTTera 12.6%, TCL Springserve 11.5% | No | — |
| App Name | 86.2% | MovieArk 30.4%, Live TV 20.9%, *N/A 13.8%* | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 87.6%, false 12.4% | No | — |
| contentGenre | 90.3% | *N/A 9.7%*, Drama 9.6%, drama 5.7% | Sí | +5.8 pp |
| contentTitle | 87.6% | *N/A 12.4%*, las estrellas 0.5%, canal 5 0.3% | No | — |
| contentRating | 71.5% | *N/A 28.4%*, Teen Plus 9.5%, Adults 7.8% | Sí | +7.3 pp |
| contentLanguage | 62.7% | *N/A 37.1%*, es 18.8%, en 17.5% | No | — |
| contentIsLiveStream | 26.0% | *N/A 38.6%*, *Unknown 35.3%*, 1 26.0% | Sí | +19.3 pp |
| contentCategory | 24.6% | *[-7] 75.3%*, [IAB1] 4.5%, [IAB1-5] 4.1% | Sí | +71.6 pp |
| contentLength | 16.1% | *N/A 83.9%*, 6 5.2%, 5 3.9% | Sí | +36.2 pp |
| contentSeries | 7.2% | *N/A 91.5%*, *md5-vacío 1.3%*, VOD 0.5% | Sí | +7.7 pp |

## Colombia — 131,911 filas (10.4%) · 7.3% de los requests

eCPM: 84.4% de filas en cero · media no-cero $3.16 · ponderado $3.22

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 34.0%, OTTera 16.9%, TCL APAC 11.6% | No | — |
| App Name | 97.5% | MovieArk 35.7%, Live TV 29.9%, TCL CHANNEL 12.3% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 95.2%, false 4.8% | No | — |
| contentGenre | 90.9% | Drama 12.1%, *N/A 9.1%*, Horror 5.1% | Sí | +5.8 pp |
| contentTitle | 95.2% | *N/A 4.8%*, {{content_title}} 0.3%, life & me 0.2% | No | — |
| contentRating | 71.1% | *N/A 28.9%*, Adults 10.5%, Teen Plus 8.7% | Sí | +7.3 pp |
| contentLanguage | 53.2% | *N/A 46.8%*, en 20.1%, English 16.3% | No | — |
| contentIsLiveStream | 26.2% | *Unknown 39.8%*, *N/A 34.0%*, 1 26.2% | Sí | +19.3 pp |
| contentCategory | 21.2% | *[-7] 78.8%*, [IAB1] 5.7%, [IAB1, IAB1-5] 2.1% | Sí | +71.6 pp |
| contentLength | 10.8% | *N/A 89.2%*, 4 3.5%, 5 3.0% | Sí | +36.2 pp |
| contentSeries | 6.4% | *N/A 93.6%*, VOD 0.8%, {{CONTENT_SERIES}} 0.3% | Sí | +7.7 pp |

## Chile — 145,451 filas (11.4%) · 6.0% de los requests

eCPM: 78.8% de filas en cero · media no-cero $6.28 · ponderado $5.34

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 25.6%, TCL Springserve 17.3%, OTTera 14.5% | No | — |
| App Name | 95.7% | MovieArk 47.6%, Live TV 30.6%, TCL CHANNEL 5.0% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 97.1%, false 2.9% | No | — |
| contentGenre | 91.1% | Drama 11.1%, *N/A 8.9%*, Horror 4.8% | Sí | +5.8 pp |
| contentTitle | 97.1% | *N/A 2.9%*, {{content_title}} 0.2%, catalunya �ber alles! 0.2% | No | — |
| contentRating | 71.1% | *N/A 28.9%*, Adults 11.3%, Teen Plus 7.7% | Sí | +7.3 pp |
| contentLanguage | 60.9% | *N/A 39.1%*, en 24.6%, English 18.6% | No | — |
| contentIsLiveStream | 19.0% | *N/A 43.4%*, *Unknown 37.6%*, 1 19.0% | Sí | +19.3 pp |
| contentCategory | 14.7% | *[-7] 85.3%*, [IAB1] 5.8%, [IAB17] 1.0% | Sí | +71.6 pp |
| contentLength | 8.2% | *N/A 91.8%*, 4 3.1%, 5 2.2% | Sí | +36.2 pp |
| contentSeries | 5.5% | *N/A 94.4%*, VOD 0.8%, {{CONTENT_SERIES}} 0.2% | Sí | +7.7 pp |
