# Reporte — ViX / TelevisaUnivision en México: completitud de content objects, requests, eCPM y rutas de venta

**Fuente:** `inventory-consolidado-v10-a-v15.csv` — 648,589 filas (métricas del corte v15, ventana 15–29 ago 2026). Todos los porcentajes de completitud describen el consolidado **tal como viene del reporte de inventario**: una celda cuenta como con dato si trae algo útil (se excluyen centinelas y basura: `Not Available`, `Unknown`, `[-7]`, hash MD5 de cadena vacía, macros `{{...}}`).

**Definición del segmento (filtro acordado):** `Country = Mexico` **y** (`Publisher` contiene la palabra "televisa" **o** `App Name` contiene la palabra "vix"), ambos sin distinguir mayúsculas. Resultado: **18,723 filas**. Queda documentado que este filtro **excluye a propósito** el ViX embebido en televisores Hisense/Vidaa, que solo es identificable por el id técnico de la app (`tv.vidaa.ui.apps.vix`, `com.vix`) porque llega con `App Name` = "Vidaa" o vacío: son 10,467 filas y 7.4B de requests adicionales (~14% del tráfico del segmento ampliado) que este reporte NO incluye. Con el filtro acordado, el segmento también existe fuera de México (Argentina 746 filas, Perú 741, Colombia 629, Chile 568, Ecuador 514, Costa Rica 477, Guatemala 446), no cubierto aquí.

**Nota sobre el eCPM:** todos los eCPM de este reporte son **promedios ponderados por requests** — Σ(requests × eCPM) / Σ(requests) — calculados solo sobre los requests con eCPM > 0. No son promedios simples de filas: una combinación con mil millones de requests pesa mil millones de veces más que una de un request.

## Los números gruesos del segmento (México)

| Métrica | ViX/Televisa MX | Global (todo el consolidado) |
|---|---:|---:|
| Filas | 18,723 | 648,589 |
| Requests | **44,167,178,640** (11.4% del total global) | 385,830,361,280 |
| eCPM ponderado (>0) | **2.19** | 4.16 |
| % de requests monetizados | **89.8%** | 52.9% |
| % de filas con título real | 62.6% | 86.7% |

La foto comercial en una línea: **ViX/Televisa es el inventario más líquido del dataset (89.8% de los requests monetizan, contra 52.9% global) pero a la mitad del precio promedio (eCPM ponderado 2.19 vs 4.16)** — volumen enorme, venta casi total, cobro bajo. El 62.6% de título real (vs 86.7% global) se explica por los canales lineales que llegan como nombre de canal (`las estrellas`, `golden`, `canal 5`) y los feeds con códigos internos (`mxf01`) en lugar del programa.

## Completitud por columna (el consolidado como viene)

% de filas y % de requests con dato útil, para el total y para el segmento:

| Columna | Global: % filas | Global: % reqs | ViX/Televisa MX: % filas | ViX/Televisa MX: % reqs |
|---|---:|---:|---:|---:|
| contentGenre | 98.8% | 92.4% | **99.0%** | **93.9%** |
| contentRating | 83.9% | 87.9% | **89.6%** | 86.4% |
| contentLanguage | 77.2% | 82.5% | 64.6% | **60.5%** |
| contentIsLiveStream | 28.7% | 38.9% | 42.9% | 40.4% |
| contentCategory | 23.0% | 32.3% | **9.5%** | **1.9%** |
| contentLength | 11.7% | 24.8% | 28.3% | 24.3% |
| contentSeries | 6.1% | 6.9% | **0.3%** | **0.0%** |

**Lecturas:**

- **contentSeries prácticamente no existe en ViX: 0.3% de filas y 0.0% de los requests** (global: 6.1% / 6.9%). Para un catálogo cuyo corazón son telenovelas y series, el campo que las nombra viene vacío — es el hueco más grande del segmento frente a lo que OpenRTB espera.
- **contentCategory es casi inexistente: 9.5% de filas y solo 1.9% de los requests con dato** (global: 32.3% de requests). Las rutas de ViX mandan `[-7]` de forma casi universal; lo poco que llega con IAB viene de combinaciones marginales.
- **contentLanguage está por debajo del global (64.6% de filas, 60.5% de requests, vs 82.5% global en requests)** — el idioma falta justo en un inventario cuyo argumento de venta es el español; cuando viene, es `es` de forma abrumadora.
- **contentGenre es la fortaleza del segmento** (99.0% de filas, 93.9% de requests) y **contentRating viene mejor que el global** (89.6% de filas vs 83.9%), dominado por `tv-14`.
- **contentIsLiveStream viene mejor que el global en apariencia (42.9% vs 28.7% de filas), pero con la advertencia de siempre:** el 100% de lo declarado es `1`, también en el VOD — el campo no distingue los canales en vivo de ViX de su catálogo on-demand.

## Detalle por valor: qué trae cada columna

Mismo formato del reporte 07 (% de filas no vacías + top 3 valores más frecuentes). Primero **México completo** como referencia (las 193,264 filas del país, tabla del reporte 07 sobre este mismo consolidado):

**Content objects — México completo:**

| Columna | % de filas no vacías | Top 3 referencias (% filas del país) |
|---|---:|---|
| contentIsTitlePresent | 100% | true 83.7%, false 16.3% |
| contentGenre | 99.1% | drama 11.1%, documentary 4.0%, other 3.9% |
| contentTitle | 83.7% | *N/A 16.3%*, las estrellas 0.5%, canal 5 0.4% |
| contentRating | 82.8% | *N/A 17.1%*, tv-14 13.7%, r 9.7% |
| contentLanguage | 75.9% | **es 36.5%, en 34.1%**, *N/A 23.8%* |
| contentIsLiveStream | 26.3% | *Unknown 37.1%*, *N/A 36.5%*, 1 26.3% |
| contentCategory | 25.3% | *[-7] 74.7%*, [IAB12] 5.2%, [IAB1-5] 4.2% |
| contentLength | 17.0% | *N/A 83.0%*, 6 6.4%, 5 3.9% |
| contentSeries | 7.2% | *N/A 91.5%*, md5-vacío 1.3%, VOD 0.5% |

Y la misma tabla calculada **solo para el segmento ViX/Televisa en México** (18,723 filas, filtro acordado):

**Content objects — ViX/Televisa MX:**

| Columna | % de filas no vacías | Top 3 referencias (% filas del segmento) |
|---|---:|---|
| contentIsTitlePresent | 100% | true 75.2%, false 24.8% |
| contentGenre | 99.0% | drama 38.5%, comedy 11.6%, news 3.1% |
| contentTitle | 75.2% | *N/A 24.8%*, las estrellas 2.6%, golden 2.5% |
| contentRating | 89.6% | **tv-14 43.3%**, *N/A 10.4%*, dv-t 8.6% |
| contentLanguage | 64.6% | **es 60.5%**, *N/A 35.4%*, spa 3.1% |
| contentIsLiveStream | 42.9% | 1 42.9%, *N/A 39.8%*, *Unknown 17.4%* |
| contentCategory | 9.5% | *[-7] 90.5%*, [IAB1, IAB1-5] 7.2%, [IAB1, IAB1-5, IAB1-7] 1.6% |
| contentLength | 28.3% | *N/A 71.7%*, 8 28.3% |
| contentSeries | 0.3% | *N/A 99.7%*, FIFA Club World Cup 0.2%, WDBJ News 0.0% |

El contraste retrata al segmento: es **hispanohablante puro** (es 60.5% + spa 3.1%; el inglés no aparece en el top), con **perfil de telenovela** (drama 38.5% y tv-14 43.3%, el triple de concentración que el país), sus títulos más vistos son **canales lineales y no programas** (las estrellas 2.6%, golden 2.5%), la categoría IAB casi no viene (90.5% en `[-7]`), `contentLength` solo conoce un valor (el código `8`) y la serie no se nombra nunca (99.7% N/A).

## Publishers / ad servers que ofrecen ViX-Televisa en México

24 publishers distintos venden este inventario. Concentración: **los 3 primeros mueven el 96.1% de los requests del segmento.** (eCPM: promedio ponderado por requests, sobre requests con eCPM > 0.)

| Ruta de venta (Publisher) | Filas | % reqs del segmento | eCPM pond (>0) | % reqs monetizados | Plataformas donde corre la app |
|---|---:|---:|---:|---:|---|
| **Equativ (ex SMART AdServer) — oRTB CTV** | 5,343 | **37.1%** | 2.61 | 88.8% | Roku, Samsung, Amazon |
| **TelevisaUnivision via SpringServe** | 5,552 | **37.1%** | 2.25 | 90.9% | prendetv (Android), Roku, Amazon |
| **TelevisaUnivision via OB** | 3,380 | **21.9%** | 1.40 | **97.7%** | Roku, prendetv, batanga (BR) |
| METAX Software (Exchange) | 1,760 | 1.9% | 2.47 | 65.4% | prendetv, Roku, Samsung |
| VGI CTV Inc APAC | 1,712 | 1.1% | 2.13 | 34.9% | prendetv, Roku |
| TelevisaUnivision via TAM / TAM Prime | 21 | 0.4% | 0.00 | 0.0% | prendetv, Univision App |
| AWG Media | 19 | 0.3% | 3.13 | 28.7% | Roku, prendetv |
| Seedtag Advertising (oRTB) | 339 | 0.1% | 1.72 | 1.4% | prendetv, Roku, Samsung |
| Cola (16 publishers: EXTE ×2, LG Ads, Adsmovil, NGL, NubaTV, InMobi, LoopMe, Glewed, Vizio ×2, TCL, Indicue, Sparteo, TripleB…) | ~800 | 0.1% | 0–4.49 | mayormente 0% | variadas |

**Estructura de las rutas (quién es quién):**

1. **Rutas directas de TelevisaUnivision (59.4% de los requests):** el publisher se llama a sí mismo y el sufijo dice el ad server — **via SpringServe** (su ad server de video principal, 37.1%), **via OB** (21.9%) y **via TAM** (Amazon Transparent Ad Marketplace, residual). Son las rutas más líquidas del segmento (91–98% monetizado) y las más baratas (1.40–2.25): inventario propio vendido a piso.
2. **SSP/exchange third-party (≈39%):** **Equativ es la ruta individual más grande (37.1%, empatada con SpringServe)** vendiendo las apps ViX de Roku/Samsung/Amazon. Le siguen METAX (1.9%) y una cola de exchanges (Seedtag, EXTE, InMobi, LoopMe…) casi sin monetizar.
3. **Resellers LATAM/APAC (≈1.5%):** VGI, AWG, Adsmovil, NubaTV, NGL — poco volumen, monetización floja (0–35%), aunque con eCPM nominal más alto cuando venden (2.1–3.1): la ruta larga cobra más caro pero casi no vende.

**El patrón de precio del segmento:** a más directa la ruta, más barato y más líquido (OB: 1.40 y 97.7% vendido; resellers: 3+ de eCPM y <35% vendido). Consistente con un inventario que TelevisaUnivision mueve a volumen por sus propios pipes, y que los intermediarios remarcan sin lograr venderlo.

**Nota:** con el filtro acordado, la ruta OEM (Vidaa/Hisense vendiendo el ViX embebido en sus televisores) queda fuera del segmento — esa ruta movía ~11.7% de los requests en la definición ampliada y era la más barata (eCPM 1.26).
