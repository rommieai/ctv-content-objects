# Reporte — Análisis por publisher, consolidado v10+v11+v12 (CTV LATAM)

**Fuente:** `inventory-consolidado-v10-v11-v12.csv` (539,190 filas, 429,176,186,240 requests).
**Generado con:** `scripts/analizar.py --por Publisher --top-grupos 12` → `reporte-publishers-v12-consolidado.json` (top-15 de valores por columna para cada publisher).
**Alcance:** los 12 publishers con más requests, que concentran el **~91% del tráfico** del dataset. Los porcentajes de "top valores" son sobre las filas de cada publisher.

Este es el desglose que faltaba: los reportes por país mostraron que la calidad de metadata "depende del publisher"; aquí queda con nombre y apellido quién manda qué, quién rompe qué, y cómo monetiza cada uno.

## Tabla comparativa

| Publisher | % filas | % requests | % filas eCPM=0 | eCPM pond. | Fill category | Fill language | Fill title | Fill length |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 24.2% | 24.2% | **99.9%** | 6.33 | 40.0% | 99.9% | 99.8% | 1.0% |
| Roku - oRTB | 1.6% | 14.0% | 94.7% | 5.96 | **98.1%** | 94.8% | **25.1%** | **77.1%** |
| TCL ADS - Springserve | 13.0% | 11.3% | 66.3% | 5.19 | 0.8% | 93.6% | 99.6% | 1.1% |
| TCL ADs (APAC) | 13.2% | 8.8% | **56.9%** | 6.20 | 0.9% | 96.8% | 99.8% | 1.4% |
| iion Pty Ltd | 15.0% | 7.6% | 85.1% | 3.63 | 0.4% | **4.0%** | 99.7% | 2.5% |
| TV Azteca - Springserve | 0.4% | 5.3% | 95.3% | 5.34 | 0.1% | 100% | **0.1%** | 0.1% |
| Televisa Univision via SpringServe | 1.5% | 4.4% | 55.9% | 2.23 | 0.0% | 60.5% | 85.7% | 52.5% |
| Coocaa (SKYWORTH) | 1.2% | 4.2% | **42.7%** | 3.47 | **100%** | **100%** | **100%** | **100%** |
| Select Plus PTE LTD (CTV) | 7.8% | 3.7% | 99.8% | 7.27 | 0.0% | 83.8% | 99.9% | 1.2% |
| Equativ - oRTB CTV | 2.4% | 3.2% | 84.0% | 2.75 | 24.1% | 81.4% | 84.2% | 28.5% |
| Televisa Univision via OB | 0.7% | 2.7% | 48.6% | 1.31 | 0.0% | 100% | **0.0%** | 0.0% |
| Zeasn Europe B.V. | 0.2% | 1.7% | 68.7% | 4.76 | 0.0% | 100% | **0.0%** | 0.0% |

Dos lecturas rápidas: (1) nadie está completo — el que tiene la mejor metadata estructural (Roku, Coocaa) esconde otra cosa o es chico, y los gigantes de catálogo (OTTera, TCL, iion) no mandan categoría ni duración; (2) el sell-through por filas va de 0.1% (OTTera) a 57% (Coocaa) — dos órdenes de magnitud entre vendedores.

---

## 1. OTTera.tv — 130,216 filas (24.2%) · 24.2% de los requests

eCPM: **99.89% de filas en cero** · ponderado 6.33 sobre lo poquísimo que vende

| Columna | Distintos | Fill | Top valores |
|---|---:|---:|---|
| pageURL | 18 | 100% | com.tcl.movieark 34.3%, com.tcl.livetv 24.9%, com.tcl.waterfall 19.1%, com.tcl.browser 14.7%, +com.tcl.livetv 4.7% |
| Country | 18 | 100% | México 17.4%, Argentina 16.3%, Colombia 9.8%, Perú 9.2% |
| contentGenre | 2,347 | 99.8% | other 7.2%, drama 6.6%, documentary 6.3%, horror 3.5% |
| contentCategory | 20 | 40.0% | *[-7] 60.0%*, [IAB1] 22.4%, [IAB1-22] 15.1% |
| contentSeries | 64 | 0.9% | *N/A 99.1%*, VOD 0.5% |
| contentLength | 7 | 1.0% | *N/A 99.0%* |
| contentLanguage | 462 | **99.9%** | en 69.5%, es 25.9%, pt 0.9% |
| contentIsLiveStream | 2 | 18.3% | *Unknown 81.7%*, 1 18.3% |
| contentTitle | 8,345 | 99.8% | catálogo OTT Studios (haus of horror, the baddest bad boy...) |
| contentRating | 92 | **99.9%** | tv-pg 18.2%, r 13.4%, tv-ma 13.2%, nr 9.8% |

**Conclusiones.** OTTera no tiene apps propias: **revende el inventario de las 4 apps TCL** (100% de sus bundles son com.tcl.\* — incluido el malformado `+com.tcl.livetv`, que es 100% suyo). Su metadata descriptiva es casi perfecta (idioma, rating, título al 99.9%: la mejor ruta TCL en señales) pero **es el catálogo muerto del dataset: monetiza el 0.11% de sus filas**. Un cuarto del archivo entero es catálogo de OTTera que nadie compra. También es el origen del código inválido `[IAB1-22]` (15.1% de sus filas).

## 2. Roku - oRTB — 8,641 filas (1.6%) · 14.0% de los requests

eCPM: 94.7% de filas en cero · ponderado 5.96

| Columna | Distintos | Fill | Top valores |
|---|---:|---:|---|
| pageURL | 6 | 100% | 151908 (Roku Channel) 71.2%, `roku` 16.7%, 41468 (Tubi) 9.9%, 584171 (Canela.TV) 1.6% |
| Country | 12 | 100% | **México 66.0%, Puerto Rico 32.8%** |
| contentGenre | 2,525 | 99.9% | entertainment 5.3%, drama 3.0%, movies & tv 2.9%, news 2.1% |
| contentCategory | 303 | **98.1%** | [IAB1-5, IAB1-7] 32.1%, [IAB1-7] 20.6%, [IAB1-5] 6.8% |
| contentSeries | 640 | 26.4% | **md5-de-vacío 50.8%**, *N/A 22.9%*, y hashes MD5 de series reales (8d2ec0..., ee2338...) |
| contentLength | 9 | **77.1%** | 5 → 27.4%, 6 → 26.5%, 4 → 11.1%, 8 → 5.3% |
| contentLanguage | 10 | 94.8% | en 58.7%, es 35.6% |
| contentIsLiveStream | 2 | 27.2% | *Unknown 72.8%*, 1 27.2% |
| contentTitle | **5** | **25.1%** | *N/A 74.8%*, `roku` 11.3%, `epg` 9.0%, `vod` 4.3% |
| contentRating | 39 | 98.4% | tv14 17.1%, tvpg 16.5%, **b (RTC México) 8.3%**, r 6.1% |

**Conclusiones.** El espejo de OTTera: **la mejor metadata estructural del dataset (categoría 98%, duración 77%, rating 98%) y la peor identidad de contenido (solo 5 valores de título en 8,641 filas)**. Roku ofusca sistemáticamente: títulos tras `roku`/`epg`/`vod` y series tras hashes MD5 — la mitad son el hash del vacío, pero también hay hashes de series reales, o sea que la serie viaja pero irreconocible. Es el origen de los ratings sin guión (`tv14`, `tvpg`) y el mayor emisor del rating mexicano `b`. Su negocio está en México (66%) y Puerto Rico (33%), con solo 6 bundles.

## 3. TCL ADS - Springserve — 70,065 filas (13.0%) · 11.3% de los requests

eCPM: 66.3% en cero · ponderado 5.19

Vende las 4 apps TCL repartido parejo (movieark 28.4%, waterfall 24.6%, browser 23.2%, livetv 22.7%), centrado en Argentina (30.3%) + México (25.4%) + Chile (16.5%). Metadata descriptiva buena (título 99.6%, idioma 93.6%, rating 90.9%) y estructural nula: **`[-7]` en el 99.2% de sus filas**, series/duración ~1%. Es, junto con TCL APAC e iion, la fuente masiva del placeholder de categoría. Monetiza bien: un tercio de sus filas genera revenue a 5.19 ponderado.

## 4. TCL ADs (APAC) — 71,100 filas (13.2%) · 8.8% de los requests

eCPM: **56.9% en cero (el segundo mejor sell-through del top)** · ponderado 6.20

Gemela de la anterior (mismas apps, mismo perfil de metadata: `[-7]` 99.1%, idioma 96.8%, título 99.8%) pero con mejor conversión a revenue: **43% de sus filas monetizan a 6.20** — la ruta TCL que mejor vende. Fuerte en Argentina (24.9%), México (23.8%), Chile (14.5%) y Ecuador (12.4%).

## 5. iion Pty Ltd — 80,897 filas (15.0%) · 7.6% de los requests

eCPM: 85.1% en cero · ponderado 3.63

| Columna | Distintos | Fill | Top valores |
|---|---:|---:|---|
| Publisher ID | 2 | — | 166799 51.3%, 163091 48.7% (las dos cuentas) |
| pageURL | 66 | 100% | com.tcl.livetv 36.2%, com.tcl.movieark 34.9%, com.tcl.waterfall 16.5% |
| contentCategory | 8 | 0.4% | *[-7] 99.6%* |
| contentLanguage | 17 | **4.0%** | ***N/A 96.0%***, es 1.6%, en 1.5% |
| contentIsLiveStream | 3 | 4.0% | *N/A + Unknown 96%* |
| contentTitle | 4,419 | 99.7% | catálogo OTT Studios |
| contentRating | 85 | 84.7% | r 13.8%, tv-ma 13.3%, nr 10.3% |

**Conclusiones.** Tercera ruta de reventa del inventario TCL (con dos seats), y **el culpable número uno del idioma faltante del dataset: manda `contentLanguage` en solo el 4% de sus filas** (el 96% de `Not Applicable` global de idioma sale mayormente de aquí). Como además el tráfico sin idioma paga ~40% menos, iion tiene el argumento de yield más directo de todos: activar un campo que sus rutas hermanas (TCL SS 93.6%, OTTera 99.9%) sí mandan. Monetiza poco y barato (3.63) para su tamaño.

## 6. TV Azteca - Springserve — 2,035 filas (0.4%) · 5.3% de los requests

eCPM: 95.3% en cero · ponderado 5.34

**Conclusiones.** Sorpresa del desglose: TV Azteca no vende un canal propio sino **el inventario de Tubi en México (com.tubitv = 98.7% de sus filas; México 98%)** — más una migaja de "Azteca TV". Y es el publisher más sucio del dataset por metro cuadrado: es el origen de **los géneros con prefijo `genre_*`** (`genre_drama`, `genre_action`...), de **los ratings concatenados `tvpg_tv_14`/`mpaa_r`** (25.3% y 12% de sus filas), y hasta de una macro nueva: **`[{{CONTENT_CATEGORIES}}]`** en contentCategory. Título: 0.1% (99.9% sin título). Idioma: 100% `es` (único con idioma perfecto). Un solo fix de este publisher limpiaría el grueso de las "variantes sucias" de rating del dataset, que pesan ~8% del tráfico.

## 7. Televisa Univision via SpringServe — 8,153 filas (1.5%) · 4.4% de los requests

eCPM: **55.9% en cero** · ponderado 2.23

ViX en 5 plataformas (Android 43.7%, Samsung 18.6%, Roku 17.4%, Fire TV 15.4%). Metadata razonable: género real (drama 49%, comedy 13.6%), rating 99.2% (tv-14 65.5%), duración 52.5% (todo en bucket 8 — coherente con TV lineal/novelas largas), títulos de canales lineales (las estrellas, canal 5, golden). **Vende casi la mitad de sus filas... a 2.23**: el modelo broadcaster de alto fill y precio bajo confirmado a nivel de ruta. Curiosidad: la única serie declarada con volumen es "FIFA Club World Cup".

## 8. Coocaa, a SKYWORTH company — 6,520 filas (1.2%) · 4.2% de los requests

eCPM: **42.7% en cero — el mejor sell-through del dataset** · ponderado 3.47

**El content object perfecto: 100% de fill en categoría, duración, idioma, título y livestream, y 91% en series.** Un solo bundle (Coolita Channel), todo declarado live, catálogo deportes/animación/música con series reales (The Cube USA, J1 League, Podpah, Rango Brabo). Dos rarezas: su vocabulario de género es propio ("sports & games", "animation,family,sport") y **la distribución por país es sospechosamente uniforme (~9.9% de filas en cada uno de 16 países)** — es el mismo catálogo replicado idéntico en todos lados, no demanda orgánica por mercado. Vende más de la mitad de sus filas, pero barato (3.47): metadata perfecta ≠ precio premium.

## 9. Select Plus PTE LTD (CTV) — 42,137 filas (7.8%) · 3.7% de los requests

eCPM: **99.8% en cero** · ponderado 7.27 sobre casi nada

Cuarta ruta de reventa TCL (movieark 78.8% + livetv 20.6%). Réplica del patrón OTTera: catálogo enorme que no se vende (0.2% de filas monetizan). Dos señales rotas particulares: **declara livestream=1 en el 100% de sus filas** — incluyendo el catálogo de películas de MovieArk, lo que es directamente falso y contamina la señal de live del dataset — y el rating casi no viaja (fill 22%, el peor del top). Cuando vende, vende caro (7.27), pero es anecdótico.

## 10. Equativ (SMART AdServer) - oRTB CTV — 12,897 filas (2.4%) · 3.2% de los requests

eCPM: 84.0% en cero · ponderado 2.75

El único exchange clásico del top: mezcla bundles de ViX (Roku/Samsung/Vidaa), TCL y Roku, con México al 87.8%. Metadata intermedia (categoría 24.1%, duración 28.5%, idioma 81.4% con mayoría `es`) y App Name perdido en el 35.7% (la reventa borra el nombre). Trae género real (drama 27.9%) y ratings decentes (tv-14 41.7%). Precio bajo (2.75) — consistente con inventario ViX/broadcaster revendido.

## 11. Televisa Univision via OB — 3,981 filas (0.7%) · 2.7% de los requests

eCPM: 48.6% en cero · ponderado **1.31**

El contraste perfecto con su ruta hermana: **mismo dueño, misma app (ViX en 5 bundles), y la metadata desaparece** — título 0%, series 0%, duración 0%, categoría `[-7]` 100%. Solo sobreviven idioma (es 96.9%) y un rating en formato propio: **`dv-t`/`dv-ma` — la familia `dv-*` del dataset nace aquí** (y en Zeasn). El género usa otro vocabulario no estándar ("drama tv", "romance movies" — los tokens que la normalización no mapeaba). Vende la mitad de sus filas al peor precio del top (1.31). **Comparar las dos rutas de Televisa es el caso de estudio de supply path del dataset**: por SpringServe llega metadata y 2.23; por OB llega nada y 1.31.

## 12. Zeasn Europe B.V. — 886 filas (0.2%) · 1.7% de los requests

eCPM: 68.7% en cero · ponderado 4.76

El dueño de la fila más grande del dataset (WhaleLive, 84.2% de sus filas; el resto Whale TV+/rlaxx). Perfil "canal lineal opaco": livestream=1 al 99.2%, idioma 100% (es 68%), **título/series/categoría/duración en cero absoluto**, y ratings en formato `dv-g`/`dv-t` (la otra fuente de la familia `dv-*`). Tras el recálculo de v12 quedó en 4.76 ponderado (era >10): sigue siendo caro para lo poco que declara, pero ya no es el outlier premium que parecía.

---

## Síntesis — el mapa de responsables

1. **El inventario TCL se vende por cinco rutas distintas** (TCL SS, TCL APAC, iion, Select Plus, OTTera) **con calidades y resultados opuestos**: TCL APAC monetiza el 43% de sus filas a 6.20; OTTera y Select Plus, con el mismo inventario, el 0.1–0.2%. La elección de ruta importa más que el inventario.
2. **Cada problema de metadata del dataset tiene ya un responsable identificado**: el `[-7]` masivo sale de las rutas TCL/iion/Select Plus (99–100% de sus filas); el idioma faltante es de iion (4% de fill); los ratings `tvpg_tv_*`/`mpaa_*` y los géneros `genre_*` son de TV Azteca (que además aportó la macro `{{CONTENT_CATEGORIES}}`); la familia `dv-*` es de Televisa-OB y Zeasn; los títulos/series ocultos y los hashes MD5 son de Roku; el `[IAB1-22]` inválido y el bundle `+com.tcl.livetv` son de OTTera; el livestream=1 falso sobre catálogo VOD es de Select Plus. **La lista de fixes por partner queda lista para negociar.**
3. **Metadata y monetización son ejes independientes también a nivel de publisher**: Coocaa (fill perfecto) vende mucho a 3.47; Roku (estructura perfecta, identidad oculta) vende poco de su catálogo pero mueve 14% del tráfico; OTTera (descriptiva perfecta) no vende nada. Lo que sí se repite: **los que menos declaran, menos cobran** (Televisa-OB 1.31, Equativ 2.75) y las rutas limpias de un mismo inventario cobran más que las sucias.
4. Datos operativos sueltos: la distribución uniforme por país de Coocaa delata catálogo replicado (su "alcance de 16 países" es una sola parrilla); las dos cuentas de iion (166799/163091) parten su volumen a la mitad y conviene sumarlas en cualquier ranking; y Roku vende también Tubi y Canela.TV dentro de su seat — otro caso de dueño ≠ vendedor.
