# Reporte detallado — Content Objects, universo unificado v10+v11 (CTV LATAM)

**Archivo analizado:** `inventory-consolidado-v10-v11.csv` — **525,178 filas únicas**, 16 columnas, 428,140,540,640 requests.
**Construcción:** unión de las llaves de 14 dimensiones de ambos CSVs, sin duplicados. Métricas: las de v11 cuando la llave existe en ambos (el corte más fresco), las de v10 para las 13,178 llaves que solo están allí. Ver `reporte-comparativo-v10-v11.md` para la justificación.
**Data completa:** `reporte-content-objects-detallado-unificado.json` (distribuciones completas por columna y por país, mismo formato que las tandas anteriores).

**Nota de lectura:** como v10 y v11 comparten el 97.4% de las llaves y el 99.8% del volumen, este universo es un ~2.5% más ancho que cada archivo individual pero cuenta la misma historia. Los **glosarios de cada columna y las conclusiones cualitativas de los reportes v10 y v11 aplican íntegros aquí** (mismos placeholders, mismos sistemas de rating, mismos buckets); este reporte se concentra en las cifras del universo completo y en lo que aporta la unión.

---

## PARTE 1 — Las 16 columnas sobre el universo unificado

### Resumen de dimensiones

| Columna | Distintos (útiles) | Fill filas | Fill requests | Ganancia de la unión vs un archivo suelto |
|---|---:|---:|---:|---|
| Publisher ID | 238 | 100% | 100% | +10 cuentas vs v11 (recupera la cola de v10) |
| Publisher | 232 | 100% | 100% | +10 sellers vs v11 (AETN, Hearst, VIZIO, Xumo...) |
| pageURL | 668 | 100% | 100% | +30 bundles vs v11 |
| App Name | 389 (388) | 91.84% | 93.42% | +12 nombres |
| Country | 18 | 100% | 100% | sin cambio |
| contentGenre | 7,742 (7,739) | 98.72% | 94.26% | +175 variantes de cola |
| contentCategory | 479 (478) | 21.95% | 29.95% | sin cambio material |
| contentSeries | 1,867 (1,864) | 5.48% | 6.72% | +53 series de cola |
| contentIsTitlePresent | 2 | 100% | 100% | sin cambio |
| contentLength | 9 (8) | 11.22% | 23.64% | sin cambio |
| contentLanguage | 484 (482) | 79.88% | 86.74% | sin cambio material |
| contentIsLiveStream | 3 (1) | 29.15% | 38.02% | sin cambio |
| contentTitle | 14,071 (14,070) | 91.64% | 76.21% | +423 títulos de cola |
| contentRating | 182 (177) | 84.71% | 88.17% | sin cambio |

La jerarquía de fills es exactamente la misma de siempre: genre > title > rating > language ≫ livestream > category > length > series (que sigue siendo **la columna con menos datos: 5.48%**).

### Publisher / Publisher ID

232 publishers, 238 cuentas, ninguna cuenta con dos nombres. Concentración idéntica a los archivos individuales: OTTera 23.8% de filas (23.5% de requests), luego iion 15.0%, TCL ADs (APAC) 13.4%, TCL Springserve 12.8%, Select Plus 7.9%. Los desproporcionados en volumen siguen siendo **Roku (1.63% de filas → 14.13% de requests)** y **TV Azteca (0.39% → 5.49%)**. La unión suma 10 sellers de cola que solo estaban en v10 y 3 que solo estaban en v11 — juntos no llegan al 0.2% del volumen.

### pageURL / App Name

668 bundles. Las 4 apps de TCL = **78.1% de las filas y 56.2% de los requests**. Top por volumen: com.tcl.movieark 28.6% de requests, com.tcl.livetv 13.6%, The Roku Channel (151908) 11.7%, TCL Channel 9.1%, Tubi 5.7%, Coolita 4.8%, ViX (sumando sus 3+ bundles) ~9%. Persisten los malformados (`+com.tcl.livetv` 6,133 filas, `roku` 1,441) y la fragmentación de nombres (ViX con 6 variantes, Tubi con 5).

### Country

Misma foto: México 28.45% de filas / **61.23% de requests**, Argentina 18.9%/17.3%, Chile 11.3%/5.9%, Colombia 9.8%/6.3%, Perú 8.4%/2.5%; los 13 restantes suman <7% del volumen.

### contentGenre

7,739 valores útiles (variantes/combos de ~30-40 géneros base). Top: drama 9.9% de filas, other 5.8%, documentary 5.2%, horror 3.7%, comedy 3.5%; siguen los combos (`drama,romance` 2.2%) y el duplicado `music,music` (2,358 filas). El 49.2% de las filas está fuera del top 30 — cola larguísima de texto libre.

### contentCategory

`[-7]` en **409,876 filas (78.05% / 70.05% de requests)** — el placeholder crece en términos absolutos con la unión pero no en proporción. Válidas dominantes: [IAB1] 6.3%, [IAB1-5] 1.5%, [IAB12] 1.2%, [IAB1-7] 0.9% (pero 5.9% de requests). El código inexistente [IAB1-22] queda en 19,603 filas (3.7%). Categoría IAB limpia y válida: ~17% de filas.

### contentSeries

93.68% `Not Available`. El hash MD5 de cadena vacía suma 4,349 filas (0.83%) pero **10.94% de los requests** (Roku). Macro `{{CONTENT_SERIES}}` en 624 filas. Series reales ~3.5% de filas: Doña Bárbara (339), Chicago Fire (165), MasterChef México (140), J1 League (170), Podpah (136). La unión aporta 53 series de cola nuevas (p. ej. más contenido brasileño: Ciência Sem Fim, Goats).

### contentIsTitlePresent / contentTitle

true 91.65% de filas pero solo 76.26% de requests — **23.7% del tráfico viaja sin título**. contentTitle llega a 14,070 títulos únicos (la unión suma 423 de cola); persisten `roku`+`epg` (5.8% de requests), `{{content_title}}` (599 filas) y el mojibake (`catalunya �ber alles!`).

### contentLength

Buckets 1–8, no segundos. Fill 11.22% de filas / 23.64% de requests, concentrado en 4-5-6. Sin cambio; sigue pendiente confirmar el mapeo de buckets con la fuente.

### contentLanguage

en 48.35% de filas / 40.19% de requests; es 26.82% / **42.09%** — se mantiene la paradoja (inglés gana en catálogo, español gana en tráfico). Basura persistente: `c` (1,674), `spa`/`eng`/`por` (formato ISO-639-2), `sp`, `504`.

### contentIsLiveStream

1 (live) en 29.15% de filas / 38.02% de requests; el resto Unknown + Not Available. **Sigue sin llegar un solo 0**: la ausencia no es interpretable como VOD.

### contentRating

Mismos cinco sistemas conviviendo. Top: tv-14 11.5% de filas (15.8% de requests), tv-ma 11.1%, r 11.0%, tv-pg 8.2%, nr 7.3%, g 5.8%; edades numéricas ~11.3% de filas; variantes sucias (`tv14`, `tvpg`, `tvpg_tv_14`, `tvpg_tv_ma`) ~1.9% de filas pero **8.5% de requests**; `b` (RTC México) 2,396 filas; `banned` 1,951.

### Total Requests

| Métrica | Valor |
|---|---:|
| Mínimo / Mediana / Media | 28,560 / 104,000 / 815,229 |
| p90 / p99 | 1,029,384 / 9,684,552 |
| Máximo | 4,547,172,800 (WhaleLive/México) |
| Share del top 1% de filas | **50.31%** |

La unión baja ligeramente la mediana (agrega cola pequeña), y el top 1% sigue concentrando la mitad del tráfico. Recordatorio: el universo sigue truncado por el umbral de ~29K del reporte original — esta unión recupera la cola perdida entre cortes, no la cola por debajo del umbral.

### eCPM

| Métrica | Valor |
|---|---:|
| Filas con eCPM = 0 | 435,032 (**82.84%**) — 48.9% de los requests |
| Filas con eCPM > 0 | 90,146 |
| Media / Mediana / p90 (solo >0) | 4.851 / 3.115 / 10.50 |
| Ponderado por requests (solo >0) | **4.98** |
| Máximo | 200.0 (outlier heredado de v11, auditar) |

Distribución del tráfico monetizado: 1-3 USD → 17.5% de requests totales, 5-10 USD → 17.7%, 3-5 → 8.5%, 10-20 → 5.1%, >20 → 0.18%.

---

## PARTE 2 — Los 18 países sobre el universo unificado

Detalle completo por país (top-15 de cada columna) en el JSON, clave `countries`. Tabla comparativa:

| País | Filas | % requests | % filas eCPM=0 | eCPM medio (>0) | eCPM pond. | Fill category | Fill livestream | Fill length | Fill series |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| México | 149,399 | 61.23% | 81.6% | 2.66 | 4.44 | 23.3% | 25.9% | 17.9% | 7.0% |
| Argentina | 99,052 | 17.26% | 80.4% | 6.24 | 6.25 | 11.3% | 31.8% | 4.5% | 2.6% |
| Colombia | 51,301 | 6.27% | 87.7% | 2.69 | 3.00 | 24.4% | 28.0% | 9.7% | 5.7% |
| Chile | 59,210 | 5.91% | 80.5% | 7.36 | **8.33** | 14.5% | 17.9% | 6.9% | 4.6% |
| Perú | 44,250 | 2.50% | 81.6% | 6.44 | 6.09 | 23.7% | 27.6% | 7.5% | 4.3% |
| Ecuador | 22,294 | 1.39% | 94.0% | 6.25 | 7.54 | 20.4% | 31.0% | 6.8% | 3.2% |
| Costa Rica | 17,151 | 1.31% | **62.5%** | 4.58 | 5.94 | 25.4% | 42.1% | 11.3% | 7.4% |
| Rep. Dominicana | 19,544 | 1.23% | 91.8% | 5.70 | 5.45 | 15.7% | 48.4% | 5.5% | 3.5% |
| Venezuela | 9,029 | 0.63% | **100%** | — | — | 42.1% | 45.8% | 21.7% | 12.0% |
| Panamá | 10,553 | 0.58% | 89.2% | 4.33 | 4.26 | 26.5% | 30.6% | 4.3% | 2.1% |
| Puerto Rico | 7,523 | 0.44% | 88.8% | **8.61** | 8.14 | **63.6%** | 39.1% | **64.7%** | 24.6% |
| Uruguay | 5,108 | 0.40% | 97.4% | 6.99 | 5.45 | 46.2% | 25.6% | 18.8% | 11.3% |
| Honduras | 10,834 | 0.23% | 78.8% | 3.98 | 4.00 | 26.1% | 33.0% | 3.5% | 3.0% |
| Guatemala | 7,350 | 0.23% | 77.2% | 4.88 | 4.62 | 48.1% | 23.1% | 9.2% | 4.5% |
| El Salvador | 7,896 | 0.23% | 85.7% | 6.21 | 6.43 | 41.4% | 31.2% | 4.0% | 2.4% |
| Paraguay | 1,910 | 0.09% | 87.8% | 5.96 | 5.94 | 23.0% | **69.6%** | 5.3% | 2.2% |
| Bolivia | 1,234 | 0.04% | 99.8% | 2.97 | 1.99 | **76.7%** | 59.7% | 47.7% | 36.5% |
| Nicaragua | 1,540 | 0.03% | 69.2% | 6.09 | 7.79 | 56.7% | 42.9% | 37.1% | 31.4% |

**Lo que se mantiene del análisis por país** (idéntico a las tandas anteriores, ahora con el universo completo):

- **México**: 61% del tráfico, paridad en/es (36.9/36.8), el peor fill de título de los mercados grandes (82.3%), eCPM medio bajo (2.66) con núcleo premium (ponderado 4.44). Con la unión llega a 174 publishers y 10,599 títulos distintos — el mercado más fragmentado.
- **Argentina**: 93%+ apps TCL; mejor título (97.4%), peor categoría (11.3%); precio parejo ~6.25.
- **Colombia**: el peor precio de los grandes (3.00 ponderado, 87.7% ceros) y el peor idioma (62.0% fill, en 41.7% vs es 15.4%); lidera iion.
- **Chile**: el mejor precio de los grandes (8.33), perfil VOD/película (MovieArk 41.8%, livestream 17.9% — mínimo del dataset).
- **Puerto Rico**: mercado US de facto — Roku 37.3%, category 63.6%, length 64.7%, series US (Chicago Fire, NCIS, FBI), mejor eCPM medio (8.61), pero título en 55.2% por los placeholders `roku`/`epg`. Con la unión: 110 publishers en 7,523 filas.
- **Venezuela**: 100% de sus 9,029 filas sin revenue; metadata mejor que la media. **Bolivia**: 99.8% ceros con la mejor metadata del dataset (category 76.7%) — efecto Coocaa/Coolita, igual que **Nicaragua** (que en cambio sí monetiza: 69.2% ceros, 7.79 ponderado).
- **Costa Rica**: la mejor tasa de monetización (62.5% ceros). **Paraguay**: récords de live confirmado (69.6%) y de peor rating (39.5% fill). **Guatemala**: el mejor rating (95.1%). **Uruguay**: máxima dependencia de un seller (OTTera 68.0%).

**Síntesis transversal (sin cambios, reforzada por la unión):** la calidad de la metadata la determina el mix de publishers, no el país (TCL sin category/length; Roku con category/length pero títulos ocultos; Coocaa/Coolita con el content object completo); la monetización por país depende de la demanda, no de la metadata; el catálogo de relleno de OTT Studios se repite en 15+ países; y las prioridades de limpieza siguen siendo ratings → `[-7]` → mapa bundle→servicio → buckets de length → auditar el eCPM 200.0.
