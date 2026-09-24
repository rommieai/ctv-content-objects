# Content Objects por país: México, Colombia y Chile (consolidado v10 a v21)

**Fuente:** `inventory-consolidado-v10-a-v21.csv` — 1,298,145 filas únicas, 593,279,479,040 requests (métricas del corte v21, ventana 8–22 sep 2026; v21 aportó 25,267 combinaciones nuevas). Solo v21: 512,000 filas, 450,500,254,240 requests.
**Data completa:** `recursos/reporte-content-objects-detallado-v21-consolidado.json` (top-15 de valores por columna para cada país). Generado con `scripts/analizar.py`; tablas con `scripts/generar_reporte_detallado.py`.

*Nota: "llenas" excluye centinelas — una fila cuenta como vacía tanto si la celda no trae valor como si trae `Not Available`, `Not Applicable`, `Unknown` o basura equivalente a vacío (`[-7]`, hash MD5 de cadena vacía, macros sin reemplazar).*

*Nota sobre "¿Se puede aumentar el % de filas llenas?" y "% aumento estimado": "Sí" cuando el pipeline de relleno (`scripts/enriquecer_externo.py`) tiene un método para esa columna; el aumento es la ganancia en puntos porcentuales sobre el total del consolidado (columna "Ganancia" del reporte de completitud, `recursos/reporte-completitud-content-objects-v21-completo.md`) y se muestra igual en las tablas por país. contentTitle y contentLanguage no se rellenan; Publisher y contentIsTitlePresent ya vienen al 100 %.*

*Nota sobre `md5-vacío`: en `contentSeries` algunos vendedores mandan un hash MD5 en vez del nombre de la serie. El valor `d41d8cd98f00b204e9800998ecf8427e` es el MD5 de la cadena vacía, es decir, el vendedor hasheó un texto en blanco; se cuenta como vacío.*

## Total consolidado (todos los países) — 1,298,145 filas · 593,279,479,040 requests

eCPM: 81.5% de filas en cero · media no-cero $4.21 · ponderado $3.69

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 20.1%, OTTera 19.6%, TCL Springserve 12.3% | No | — |
| App Name | 93.5% | MovieArk 33.2%, Live TV 22.3%, TCL CHANNEL 12.4% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del total) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 93.2%, false 6.8% | No | — |
| contentGenre | 91.0% | Drama 10.8%, *N/A 9.0%*, drama 5.0% | Sí | +5.9 pp |
| contentTitle | 93.2% | *N/A 6.8%*, roku 0.2%, epg 0.2% | No | — |
| contentRating | 74.9% | *N/A 25.1%*, Adults 10.3%, Teen Plus 9.3% | Sí | +7.2 pp |
| contentLanguage | 66.3% | *N/A 33.6%*, en 23.1%, English 17.5% | No | — |
| contentIsLiveStream | 29.3% | *Unknown 36.7%*, *N/A 34.0%*, 1 29.3% | Sí | +19.4 pp |
| contentCategory | 21.5% | *[-7] 78.5%*, [IAB1] 5.1%, [IAB1-22] 2.9% | Sí | +71.5 pp |
| contentLength | 12.2% | *N/A 87.8%*, 5 3.4%, 6 3.2% | Sí | +36.8 pp |
| contentSeries | 6.5% | *N/A 92.7%*, *md5-vacío 0.7%*, VOD 0.6% | Sí | +7.6 pp |

## México — 383,163 filas (29.5%) · 59.6% de los requests

eCPM: 78.9% de filas en cero · media no-cero $2.09 · ponderado $3.15

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 18.0%, OTTera 12.5%, TCL Springserve 11.4% | No | — |
| App Name | 85.9% | MovieArk 30.0%, Live TV 20.8%, *N/A 14.1%* | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 87.7%, false 12.3% | No | — |
| contentGenre | 90.2% | *N/A 9.8%*, Drama 9.7%, drama 5.6% | Sí | +5.9 pp |
| contentTitle | 87.7% | *N/A 12.3%*, las estrellas 0.5%, canal 5 0.3% | No | — |
| contentRating | 71.8% | *N/A 28.2%*, Teen Plus 9.8%, Adults 8.0% | Sí | +7.2 pp |
| contentLanguage | 62.9% | *N/A 36.9%*, es 18.5%, en 17.2% | No | — |
| contentIsLiveStream | 26.3% | *N/A 38.4%*, *Unknown 35.3%*, 1 26.3% | Sí | +19.4 pp |
| contentCategory | 24.9% | *[-7] 75.1%*, [IAB1] 4.6%, [IAB12] 4.0% | Sí | +71.5 pp |
| contentLength | 16.3% | *N/A 83.7%*, 6 5.3%, 5 4.0% | Sí | +36.8 pp |
| contentSeries | 7.4% | *N/A 91.3%*, *md5-vacío 1.3%*, VOD 0.5% | Sí | +7.6 pp |

## Colombia — 134,258 filas (10.3%) · 7.3% de los requests

eCPM: 83.1% de filas en cero · media no-cero $2.99 · ponderado $2.86

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 34.3%, OTTera 16.8%, TCL APAC 11.5% | No | — |
| App Name | 97.4% | MovieArk 35.2%, Live TV 30.0%, TCL CHANNEL 12.3% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 95.2%, false 4.8% | No | — |
| contentGenre | 90.8% | Drama 12.2%, *N/A 9.2%*, Horror 5.1% | Sí | +5.9 pp |
| contentTitle | 95.2% | *N/A 4.8%*, {{content_title}} 0.3%, life & me 0.2% | No | — |
| contentRating | 71.1% | *N/A 28.9%*, Adults 10.6%, Teen Plus 8.9% | Sí | +7.2 pp |
| contentLanguage | 53.7% | *N/A 46.3%*, en 19.7%, English 16.8% | No | — |
| contentIsLiveStream | 26.2% | *Unknown 39.6%*, *N/A 34.2%*, 1 26.2% | Sí | +19.4 pp |
| contentCategory | 21.3% | *[-7] 78.7%*, [IAB1] 5.7%, [IAB1, IAB1-5] 2.0% | Sí | +71.5 pp |
| contentLength | 11.0% | *N/A 89.0%*, 4 3.5%, 5 3.1% | Sí | +36.8 pp |
| contentSeries | 6.5% | *N/A 93.5%*, VOD 0.8%, {{CONTENT_SERIES}} 0.3% | Sí | +7.6 pp |

## Chile — 148,353 filas (11.4%) · 6.1% de los requests

eCPM: 79.4% de filas en cero · media no-cero $6.16 · ponderado $5.02

**Campos de app / vendedor:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| Publisher | 100% | iion 25.8%, TCL Springserve 17.5%, OTTera 14.3% | No | — |
| App Name | 95.8% | MovieArk 47.1%, Live TV 30.4%, TCL CHANNEL 5.7% | No | — |

**Content objects:**

| Columna | % de filas llenas | Top 3 referencias (% filas del país) | ¿Se puede aumentar el % de filas llenas? | % aumento estimado |
|---|---:|---|:---:|---:|
| contentIsTitlePresent | 100% | true 97.0%, false 3.0% | No | — |
| contentGenre | 91.0% | Drama 11.3%, *N/A 9.0%*, Horror 4.8% | Sí | +5.9 pp |
| contentTitle | 97.0% | *N/A 3.0%*, {{content_title}} 0.2%, catalunya �ber alles! 0.2% | No | — |
| contentRating | 71.3% | *N/A 28.7%*, Adults 11.6%, Teen Plus 7.9% | Sí | +7.2 pp |
| contentLanguage | 60.9% | *N/A 39.1%*, en 24.1%, English 19.0% | No | — |
| contentIsLiveStream | 19.3% | *N/A 43.1%*, *Unknown 37.6%*, 1 19.3% | Sí | +19.4 pp |
| contentCategory | 14.7% | *[-7] 85.3%*, [IAB1] 5.7%, [IAB17] 1.0% | Sí | +71.5 pp |
| contentLength | 8.2% | *N/A 91.8%*, 4 3.1%, 5 2.2% | Sí | +36.8 pp |
| contentSeries | 5.5% | *N/A 94.5%*, VOD 0.8%, {{CONTENT_SERIES}} 0.2% | Sí | +7.6 pp |
