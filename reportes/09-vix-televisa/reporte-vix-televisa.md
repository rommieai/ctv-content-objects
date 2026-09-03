# Reporte — ViX / TelevisaUnivision en México: completitud antes/después del relleno, requests, eCPM y rutas de venta

**Fuente:** `inventory-consolidado-v10-a-v15-relleno.csv` (648,589 filas; métricas del corte v15, ventana 15–29 ago 2026). Los números de este reporte salen del análisis reproducible sobre ese CSV; el mecanismo de relleno está documentado en `reportes/08-enriquecimiento-externo/reporte-relleno-por-columna.md`.

**Cómo se definió el segmento:** una fila es "ViX/Televisa" si la app, el bundle o el publisher lo delatan — `App Name` contiene "ViX", bundle en la familia ViX (`com.univision.prendetv` Android/Fire, `552828` Roku, `g20329015921` Samsung, `1167028` Roku, `tv.vidaa.ui.apps.vix` ViX embebido en Hisense/Vidaa, `com.batanga.vix` legado BR, `b08kj77pqy` Amazon, `com.univision.android`), o `Publisher` contiene "Televisa"/"Univision". Este reporte se restringe a **México**: 29,190 filas (4.5% del consolidado) — el segmento también aparece con volumen menor en Argentina (1,404 filas), Guatemala (1,114), Perú (1,051), Colombia (920) y Chile (809).

## Los números gruesos del segmento (México)

| Métrica | ViX/Televisa MX | Global (todo el consolidado) |
|---|---:|---:|
| Filas | 29,190 | 648,589 |
| Requests | **51,555,372,720** (13.4% del total global) | 385,830,361,280 |
| eCPM ponderado (>0) | **2.09** | 4.16 |
| % de requests monetizados | **88.3%** | 52.9% |
| % de filas con título real | 60.5% | 85.6% |

La foto comercial en una línea: **ViX/Televisa es el inventario más líquido del dataset (88% de los requests monetizan, contra 53% global) pero al precio la mitad del promedio (2.09 vs 4.16)** — volumen enorme, venta casi total, cobro bajo. El 60.5% de título real (vs 85.6% global) se explica por los canales lineales que llegan como nombre de canal (`las estrellas`, `canal 5`, `golden`) y los feeds con códigos (`mxf01`).

## Completitud por columna, antes → después del relleno

"Antes" = la celda traía dato útil de origen (`origen=original`); "después" = tras las corridas de relleno del pipeline. Se muestran % de filas y % de requests para ambas poblaciones.

**Tabla general (648,589 filas · 385.8B requests):**

| Columna | % filas antes | % filas después | % reqs antes | % reqs después |
|---|---:|---:|---:|---:|
| contentGenre | 98.8% | 99.1% | 92.4% | 92.6% |
| contentCategory | 23.0% | **95.2%** | 32.3% | 86.9% |
| contentLanguage | 77.2% | **97.4%** | 82.5% | 96.3% |
| contentRating | 83.9% | 90.5% | 87.9% | 92.1% |
| contentLength | 11.7% | 50.1% | 24.8% | 59.5% |
| contentIsLiveStream | 28.7% | 48.9% | 38.9% | 53.1% |
| contentSeries | 6.1% | 14.6% | 6.9% | 16.4% |

**Solo ViX/Televisa en México (29,190 filas · 51.6B requests):**

| Columna | % filas antes | % filas después | % reqs antes | % reqs después |
|---|---:|---:|---:|---:|
| contentGenre | 99.4% | 99.4% | 94.7% | 94.7% |
| contentCategory | 39.2% | **88.4%** | 15.5% | **81.6%** |
| contentLanguage | 75.6% | **96.8%** | 65.9% | **97.6%** |
| contentRating | 80.8% | 86.1% | 79.6% | 83.6% |
| contentLength | 18.4% | 61.1% | 20.8% | 73.2% |
| contentIsLiveStream | 42.3% | 42.3% | 40.6% | 40.6% |
| contentSeries | 0.4% | **31.6%** | 0.0% | **38.5%** |

**Lecturas del contraste segmento vs global:**

- **contentSeries es la gran victoria del segmento: 0.4% → 31.6% de filas (0.0% → 38.5% de requests).** ViX prácticamente no manda el campo, pero su catálogo son telenovelas y series que IMDb sí conoce: el pipeline puso el nombre canónico (`Porque el amor manda`, `¡Vivan los niños!`, `40 and 20`) vía el tipo `tvSeries` del match. El segmento pasó de "sin serie" a duplicar el promedio global (14.6%).
- **contentCategory tenía una trampa de tráfico: 39.2% de filas llenas pero solo 15.5% de los requests** — las combinaciones pesadas de ViX (deportes/noticias vía SpringServe) llegaban con `[-7]`. El relleno lo lleva a 81.6% de los requests, principalmente derivándolo del género (que ViX sí manda al 99.4%).
- **contentLanguage subió más en requests que en filas (65.9% → 97.6%)**: el vacío estaba en las rutas de mayor tráfico y el default por app (`ViX → es`, 97–100% de consistencia) más el intra lo cerraron casi por completo.
- **contentIsLiveStream no se movió (42.3%), a propósito**: ViX es una app mixta (VOD + canales en vivo) en la tabla de semántica validada — ni el título ni la app determinan el modo de entrega, así que el pipeline no inventa. Es el pendiente que solo resuelve metadata del propio TelevisaUnivision.
- contentRating subió poco (80.8 → 86.1): las vacías del segmento son las rutas Vidaa/Equativ donde el título tampoco aparece con rating en otras filas, y el candado de ambigüedad (tv-14 vs movie-pg-13 conviven en ViX) bloqueó parte.

## Publishers / ad servers que ofrecen ViX-Televisa en México

28 publishers distintos venden este inventario. Concentración: **los 4 primeros mueven el 95.2% de los requests del segmento.**

| Ruta de venta (Publisher) | Filas | % reqs del segmento | eCPM pond (>0) | % reqs monetizados | Bundles principales |
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
| Cola (19 publishers: Seedtag, EXTE ×2, LG Ads, TCL ×4, Adsmovil, NGL, NubaTV, InMobi, LoopMe, Glewed, Vizio ×2, Sparteo, TripleB, Indicue) | ~1,050 | 0.3% | 0–5.75 | mayormente 0% | variados |

**Estructura de las rutas (quién es quién):**

1. **Rutas directas de TelevisaUnivision (50.9% de los requests):** el publisher se llama a sí mismo y el sufijo dice el ad server — **via SpringServe** (su ad server de video principal, 31.7%), **via OB** (18.8%) y **via TAM** (Amazon Transparent Ad Marketplace, residual). Son las rutas más líquidas del segmento (91–98% monetizado) y las más baratas (1.40–2.25): inventario propio vendido a piso.
2. **SSP/exchange third-party (≈35%):** **Equativ es la ruta individual más grande (33.0%)** — y su bundle dominante es `tv.vidaa.ui.apps.vix`, o sea que gran parte de lo que Equativ ofrece es el ViX embebido en televisores Hisense. Le siguen METAX (1.6%) y una cola de exchanges (Seedtag, EXTE, InMobi, LoopMe…) casi sin monetizar.
3. **OEM (13%):** **Vidaa/Hisense vende directamente** el ViX de sus televisores (11.7% + 1.3% de la ruta APAC) al eCPM más bajo del segmento (1.26). TCL aparece testimonialmente.
4. **Resellers LATAM/APAC (≈1.5%):** VGI, AWG, Adsmovil, NubaTV, NGL — poco volumen, monetización floja (0–35%), aunque con eCPM nominal más alto cuando venden (2.1–3.2): la ruta larga cobra más caro pero casi no vende.

**El patrón de precio del segmento:** a más directa la ruta, más barato y más líquido (OB: 1.40 y 97.7% vendido; resellers: 3+ de eCPM y <35% vendido). Consistente con un inventario que TelevisaUnivision mueve a volumen por sus propios pipes, y que los intermediarios remarcan sin lograr venderlo.

**Nota de cobertura:** fuera del segmento definido por app/bundle/publisher casi no hay contenido Televisa — los títulos de canales Televisa (`las estrellas`, `canal 5`, `golden`…) en México aparecen solo residualmente por otras rutas (2 filas vía izzi TV en Vidaa y 2 vía Seedtag). Es decir, la definición del segmento captura la operación completa de ViX/Televisa en el dataset.
