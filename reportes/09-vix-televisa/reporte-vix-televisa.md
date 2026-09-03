# Reporte — ViX / TelevisaUnivision en México: completitud de content objects, requests, eCPM y rutas de venta

**Fuente:** `inventory-consolidado-v10-a-v15.csv` — 648,589 filas (métricas del corte v15, ventana 15–29 ago 2026). Todos los porcentajes de completitud describen el consolidado **tal como viene del reporte de inventario**: una celda cuenta como con dato si trae algo útil (se excluyen centinelas y basura: `Not Available`, `Unknown`, `[-7]`, hash MD5 de cadena vacía, macros `{{...}}`).

**Nota sobre el eCPM:** todos los eCPM de este reporte son **promedios ponderados por requests** — Σ(requests × eCPM) / Σ(requests) — calculados solo sobre los requests con eCPM > 0. No son promedios simples de filas: una combinación con mil millones de requests pesa mil millones de veces más que una de un request.

**Cómo se definió el segmento:** una fila es "ViX/Televisa" si la app, la plataforma o el publisher lo delatan — `App Name` contiene "ViX", el identificador de la app pertenece a la familia ViX (Android/Fire `com.univision.prendetv`, Roku `552828` y `1167028`, Samsung `g20329015921`, ViX embebido en Hisense/Vidaa `tv.vidaa.ui.apps.vix`, legado BR `com.batanga.vix`, Amazon `b08kj77pqy`, `com.univision.android`), o `Publisher` contiene "Televisa"/"Univision". Este reporte se restringe a **México**: 29,190 filas (4.5% del consolidado) — el segmento también aparece con volumen menor en Argentina (1,404 filas), Guatemala (1,114), Perú (1,051), Colombia (920) y Chile (809).

## Los números gruesos del segmento (México)

| Métrica | ViX/Televisa MX | Global (todo el consolidado) |
|---|---:|---:|
| Filas | 29,190 | 648,589 |
| Requests | **51,555,372,720** (13.4% del total global) | 385,830,361,280 |
| eCPM ponderado (>0) | **2.09** | 4.16 |
| % de requests monetizados | **88.3%** | 52.9% |
| % de filas con título real | 60.5% | 85.6% |

La foto comercial en una línea: **ViX/Televisa es el inventario más líquido del dataset (88% de los requests monetizan, contra 53% global) pero al precio la mitad del promedio (eCPM ponderado 2.09 vs 4.16)** — volumen enorme, venta casi total, cobro bajo. El 60.5% de título real (vs 85.6% global) se explica por los canales lineales que llegan como nombre de canal (`las estrellas`, `canal 5`, `golden`) y los feeds con códigos internos (`mxf01`) en lugar del programa.

## Completitud por columna (el consolidado como viene)

% de filas y % de requests con dato útil, para el total y para el segmento:

| Columna | Global: % filas | Global: % reqs | ViX/Televisa MX: % filas | ViX/Televisa MX: % reqs |
|---|---:|---:|---:|---:|
| contentGenre | 98.8% | 92.4% | **99.4%** | **94.7%** |
| contentRating | 83.9% | 87.9% | 80.8% | 79.6% |
| contentLanguage | 77.2% | 82.5% | 75.6% | **65.9%** |
| contentIsLiveStream | 28.7% | 38.9% | 42.3% | 40.6% |
| contentCategory | 23.0% | 32.3% | 39.2% | **15.5%** |
| contentLength | 11.7% | 24.8% | 18.4% | 20.8% |
| contentSeries | 6.1% | 6.9% | **0.4%** | **0.0%** |

**Lecturas:**

- **contentSeries prácticamente no existe en ViX: 0.4% de filas y 0.0% de los requests** (global: 6.1% / 6.9%). Para un catálogo cuyo corazón son telenovelas y series, el campo que las nombra viene vacío — es el hueco más grande del segmento frente a lo que OpenRTB espera.
- **contentCategory trae una trampa de tráfico:** en filas el segmento se ve mejor que el global (39.2% vs 23.0%), pero en requests se invierte (15.5% vs 32.3%) — las combinaciones pesadas del segmento (deportes/noticias por las rutas de mayor volumen) van con `[-7]`. La variedad de catálogo está mejor etiquetada que el tráfico real.
- **contentLanguage repite el patrón en menor grado:** 75.6% de filas pero solo 65.9% de los requests con dato (global: 82.5% de requests) — el vacío del idioma está concentrado en las rutas que más tráfico mueven, justo en un inventario cuyo argumento de venta es el español.
- **contentGenre es la fortaleza del segmento** (99.4% de filas, 94.7% de requests, por encima del global) y contentRating está en línea (80.8%).
- **contentIsLiveStream viene mejor que el global en apariencia (42.3% vs 28.7% de filas), pero con la advertencia de siempre:** el 100% de lo declarado es `1`, también en el VOD — el campo no distingue los canales en vivo de ViX de su catálogo on-demand.

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

Y la misma tabla calculada **solo para el segmento ViX/Televisa en México** (29,190 filas):

**Content objects — ViX/Televisa MX:**

| Columna | % de filas no vacías | Top 3 referencias (% filas del segmento) |
|---|---:|---|
| contentIsTitlePresent | 100% | true 74.4%, false 25.6% |
| contentGenre | 99.4% | drama 35.8%, comedy 11.0%, reality 2.5% |
| contentTitle | 74.4% | *N/A 25.6%*, las estrellas 3.3%, canal 5 2.8% |
| contentRating | 80.8% | **tv-14 37.6%**, *N/A 19.2%*, tv-pg 6.8% |
| contentLanguage | 75.6% | **es 73.0%**, *N/A 24.4%*, spa 2.0% |
| contentIsLiveStream | 42.3% | 1 42.3%, *N/A 32.7%*, *Unknown 24.9%* |
| contentCategory | 39.2% | *[-7] 60.8%*, [IAB12] 33.3%, [IAB1, IAB1-5] 4.6% |
| contentLength | 18.4% | *N/A 81.6%*, 8 18.1%, 5 0.2% |
| contentSeries | 0.4% | *N/A 99.6%*, FIFA Club World Cup 0.2%, Ownage Pranks 0.0% |

El contraste retrata al segmento: es **hispanohablante casi puro** (es 73.0% vs 36.5% del país), con **perfil de telenovela** (drama 35.8% y tv-14 37.6%, el triple de concentración que el país), sus títulos más vistos son **canales lineales y no programas** (las estrellas 3.3%, canal 5 2.8%), su categoría dominante cuando viene es el default **[IAB12] Noticias (33.3%)** aunque el catálogo sea entretenimiento, y la serie no se nombra nunca (99.6% N/A).

## Publishers / ad servers que ofrecen ViX-Televisa en México

28 publishers distintos venden este inventario. Concentración: **los 4 primeros mueven el 95.2% de los requests del segmento.** (eCPM: promedio ponderado por requests, sobre requests con eCPM > 0.)

| Ruta de venta (Publisher) | Filas | % reqs del segmento | eCPM pond (>0) | % reqs monetizados | Plataformas donde corre la app |
|---|---:|---:|---:|---:|---|
| **Equativ (ex SMART AdServer) — oRTB CTV** | 8,361 | **33.0%** | 2.60 | 87.9% | ViX en Vidaa/Hisense, Roku, Samsung |
| **TelevisaUnivision via SpringServe** | 5,552 | **31.7%** | 2.25 | 90.9% | prendetv (Android), Roku, Amazon |
| **TelevisaUnivision via OB** | 3,380 | **18.8%** | 1.40 | **97.7%** | Roku, prendetv, batanga (BR) |
| **Vidaa** (Hisense OEM) | 5,495 | **11.7%** | 1.26 | 84.5% | ViX embebido en Vidaa |
| METAX Software (Exchange) | 1,760 | 1.6% | 2.47 | 65.4% | prendetv, Roku, Samsung |
| Vidaa APAC (Hisense HQ) | 1,844 | 1.3% | 3.20 | 54.3% | ViX en Vidaa |
| VGI CTV Inc APAC | 1,712 | 1.0% | 2.13 | 34.9% | prendetv, Roku |
| AWG Media | 19 | 0.3% | 3.13 | 28.7% | Roku, prendetv |
| TelevisaUnivision via TAM / TAM Prime | 21 | 0.3% | 0.00 | 0.0% | prendetv, Univision App |
| Cola (19 publishers: Seedtag, EXTE ×2, LG Ads, TCL ×4, Adsmovil, NGL, NubaTV, InMobi, LoopMe, Glewed, Vizio ×2, Sparteo, TripleB, Indicue) | ~1,050 | 0.3% | 0–5.75 | mayormente 0% | variadas |

**Estructura de las rutas (quién es quién):**

1. **Rutas directas de TelevisaUnivision (50.9% de los requests):** el publisher se llama a sí mismo y el sufijo dice el ad server — **via SpringServe** (su ad server de video principal, 31.7%), **via OB** (18.8%) y **via TAM** (Amazon Transparent Ad Marketplace, residual). Son las rutas más líquidas del segmento (91–98% monetizado) y las más baratas (1.40–2.25): inventario propio vendido a piso.
2. **SSP/exchange third-party (≈35%):** **Equativ es la ruta individual más grande (33.0%)** — y su plataforma dominante es el ViX embebido en televisores Hisense/Vidaa, o sea que gran parte de lo que Equativ ofrece es la pantalla del OEM. Le siguen METAX (1.6%) y una cola de exchanges (Seedtag, EXTE, InMobi, LoopMe…) casi sin monetizar.
3. **OEM (13%):** **Vidaa/Hisense vende directamente** el ViX de sus televisores (11.7% + 1.3% de la ruta APAC) al eCPM más bajo del segmento (1.26). TCL aparece testimonialmente.
4. **Resellers LATAM/APAC (≈1.5%):** VGI, AWG, Adsmovil, NubaTV, NGL — poco volumen, monetización floja (0–35%), aunque con eCPM nominal más alto cuando venden (2.1–3.2): la ruta larga cobra más caro pero casi no vende.

**El patrón de precio del segmento:** a más directa la ruta, más barato y más líquido (OB: 1.40 y 97.7% vendido; resellers: 3+ de eCPM y <35% vendido). Consistente con un inventario que TelevisaUnivision mueve a volumen por sus propios pipes, y que los intermediarios remarcan sin lograr venderlo.

**Nota de cobertura:** fuera del segmento definido por app/plataforma/publisher casi no hay contenido Televisa — los títulos de canales Televisa (`las estrellas`, `canal 5`, `golden`…) en México aparecen solo residualmente por otras rutas (2 filas vía izzi TV en Vidaa y 2 vía Seedtag). Es decir, la definición del segmento captura la operación completa de ViX/Televisa en el dataset.
