# Reporte — Content Objects por país: México, Colombia y Chile (consolidado v10+v11+v12)

**Fuente:** `inventory-consolidado-v10-v11-v12.csv` — 539,190 filas únicas, 429,176,186,240 requests (métricas del corte v12 cuando la llave existe en varios archivos).
**Data completa:** `reporte-content-objects-detallado-v12-consolidado.json` (top-15 de valores por columna para cada país). Generado con `scripts/analizar.py`.

## Comparativo de fill por columna

Porcentaje de filas de cada país con dato útil (excluye centinelas y basura equivalente a vacío):

| Columna | México | Colombia | Chile |
|---|---:|---:|---:|
| Publisher | 100% | 100% | 100% |
| contentIsTitlePresent | 100% | 100% | 100% |
| contentGenre | 99.0% | 98.5% | 99.5% |
| contentTitle | 82.5% | 94.9% | 96.6% |
| App Name | 82.8% | 96.7% | 92.3% |
| contentRating | 84.7% | 80.2% | 83.2% |
| contentLanguage | 77.7% | **62.2%** | 75.3% |
| contentIsLiveStream | 25.5% | 28.0% | **17.8%** |
| contentCategory | 22.9% | 24.3% | **14.4%** |
| contentLength | 17.5% | 9.6% | 6.9% |
| contentSeries | 6.9% | 5.7% | 4.5% |

## México — 154,529 filas (28.7%) · 60.8% de los requests

eCPM: 82.2% de filas en cero · media no-cero 2.61 · **ponderado 3.78**

| Columna | Fill | # filas con dato | # requests con dato (M) | Top 3 referencias (% filas del país) |
|---|---:|---:|---:|---|
| Publisher | 100% | 154,529 | 260,777 | OTTera 14.7%, iion 12.8%, TCL Springserve 11.5% |
| contentIsTitlePresent | 100% | 154,529 | 260,777 | true 82.5%, false 17.5% |
| contentGenre | 99.0% | 152,991 | 243,564 | drama 10.8%, documentary 4.2%, other 4.1% |
| contentRating | 84.7% | 130,922 | 230,376 | *N/A 15.2%*, tv-14 13.7%, r 10.1% |
| App Name | 82.8% | 127,877 | 235,945 | MovieArk 22.9%, Live TV 21.4%, *N/A 17.2%* |
| contentTitle | 82.5% | 127,538 | 169,679 | *N/A 17.5%*, las estrellas 0.4%, canal 5 0.3% |
| contentLanguage | 77.7% | 120,103 | 223,889 | en 36.6%, es 36.3%, *N/A 22.1%* |
| contentIsLiveStream | 25.5% | 39,463 | 92,132 | *Unknown 38.7%*, *N/A 35.8%*, 1 25.5% |
| contentCategory | 22.9% | 35,388 | 89,519 | *[-7] 77.1%*, [IAB1] 4.5%, [IAB1-5] 3.7% |
| contentLength | 17.5% | 27,017 | 77,764 | *N/A 82.5%*, 6 6.4%, 5 3.9% |
| contentSeries | 6.9% | 10,673 | 11,044 | *N/A 91.6%*, md5-vacío 1.5%, VOD 0.5% |

**Conclusiones — México:**
- Único mercado con paridad inglés/español (36.6% vs 36.3%), gracias a los broadcasters locales (Televisa: "Las Estrellas" y "Canal 5" en el top de títulos).
- La peor tasa de títulos de los mercados grandes (17.5% sin título): la ruta Roku/EPG y los agregadores pierden el título justo en el mercado más grande. También es el más fragmentado: 174 publishers, 513 bundles, 6,167 variantes de género.
- **El eCPM ponderado bajó de 4.44 a 3.78 con las métricas de v12** — es donde golpea el recálculo de WhaleLive, que es tráfico mexicano. El eCPM medio no-cero (2.61) sigue siendo el más bajo de los grandes: mucha cola barata con un núcleo premium (Roku, TV Azteca).

## Colombia — 52,176 filas (9.7%) · 6.1% de los requests

eCPM: 87.8% de filas en cero · media no-cero 2.63 · **ponderado 3.01**

| Columna | Fill | # filas con dato | # requests con dato (M) | Top 3 referencias (% filas del país) |
|---|---:|---:|---:|---|
| Publisher | 100% | 52,176 | 26,320 | iion 30.0%, OTTera 24.5%, Select Plus 11.4% |
| contentIsTitlePresent | 100% | 52,176 | 26,320 | true 94.9%, false 5.1% |
| contentGenre | 98.5% | 51,382 | 25,267 | drama 10.1%, other 7.6%, documentary 4.8% |
| App Name | 96.7% | 50,446 | 25,790 | MovieArk 34.6%, Live TV 28.3%, TCL CHANNEL 13.3% |
| contentTitle | 94.9% | 49,526 | 25,303 | *N/A 5.1%*, {{content_title}} 0.2%, haus of horror 0.2% |
| contentRating | 80.2% | 41,855 | 21,154 | *N/A 19.8%*, r 11.8%, tv-14 9.8% |
| contentLanguage | **62.2%** | 32,449 | 19,399 | en 41.8%, *N/A 37.8%*, es 15.6% |
| contentIsLiveStream | 28.0% | 14,626 | 9,148 | *Unknown 44.9%*, 1 28.0%, *N/A 27.0%* |
| contentCategory | 24.3% | 12,668 | 6,032 | *[-7] 75.7%*, [IAB1] 7.1%, [IAB1-22] 3.5% |
| contentLength | 9.6% | 5,015 | 3,070 | *N/A 90.4%*, 4 3.2%, 5 2.8% |
| contentSeries | 5.7% | 2,981 | 2,239 | *N/A 94.3%*, VOD 0.9%, No Series 0.1% |

**Conclusiones — Colombia:**
- Sigue siendo **el mercado enfermo de los grandes**: 87.8% de filas sin revenue y ponderado de 3.01, con volumen de sobra (3° por filas). No es problema de catálogo sino de demanda.
- El peor idioma de los grandes (62.2% fill; en 41.8% vs es 15.6%): inventario mayormente importado sin señal local. La macro `{{content_title}}` sigue activa en su supply.
- iion lidera aquí (30.0%) — el único mercado grande donde no manda OTTera ni TCL.

## Chile — 60,427 filas (11.2%) · 5.9% de los requests

eCPM: 80.6% de filas en cero · media no-cero 7.30 · **ponderado 8.17**

| Columna | Fill | # filas con dato | # requests con dato (M) | Top 3 referencias (% filas del país) |
|---|---:|---:|---:|---|
| Publisher | 100% | 60,427 | 25,450 | iion 21.2%, TCL Springserve 19.1%, OTTera 17.1% |
| contentIsTitlePresent | 100% | 60,427 | 25,450 | true 96.6%, false 3.4% |
| contentGenre | 99.5% | 60,118 | 25,105 | drama 8.5%, other 6.7%, documentary 6.2% |
| contentTitle | 96.6% | 58,396 | 24,839 | *N/A 3.4%*, catalunya über alles! 0.2%, the baddest bad boy 0.2% |
| App Name | 92.3% | 55,756 | 24,759 | MovieArk 41.6%, Live TV 30.2%, *N/A 7.7%* |
| contentRating | 83.2% | 50,290 | 23,927 | *N/A 16.8%*, tv-ma 13.5%, r 11.8% |
| contentLanguage | 75.3% | 45,517 | 22,340 | en 52.6%, *N/A 24.7%*, es 18.6% |
| contentIsLiveStream | **17.8%** | 10,735 | 4,495 | *N/A 42.5%*, *Unknown 39.7%*, 1 17.8% |
| contentCategory | **14.4%** | 8,734 | 6,310 | *[-7] 85.5%*, [IAB1] 6.4%, [IAB1-22] 0.8% |
| contentLength | 6.9% | 4,165 | 3,188 | *N/A 93.1%*, 4 2.6%, 5 1.8% |
| contentSeries | 4.5% | 2,735 | 2,471 | *N/A 95.5%*, VOD 0.9%, {{CONTENT_SERIES}} 0.1% |

**Conclusiones — Chile:**
- **El mejor precio de los mercados grandes se sostiene en v12** (ponderado 8.17, medio 7.30) con tasa de monetización normal (80.6% en cero).
- Perfil muy VOD/película: MovieArk sola es el 41.6% de las filas y el fill de livestream es el mínimo del dataset (17.8%).
- Metadata estructural pobre (categoría 14.4%, duración 6.9%) y catálogo muy anglófono (en 52.6% vs es 18.6%): el precio alto viene de la demanda del mercado, no de la calidad de señal.
