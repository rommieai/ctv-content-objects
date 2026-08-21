# Reporte detallado — Content Objects, consolidado v10+v11+v12 (CTV LATAM)

**Archivo analizado:** `inventory-consolidado-v10-v11-v12.csv` — **539,190 filas únicas**, 16 columnas, 429,176,186,240 requests.
**Construcción:** unión de las llaves de 14 dimensiones de los tres CSV (v10, v11 y v12, ventana 5–19 ago 2026 en el más reciente), sin duplicados. Cuando una llave está en varios archivos se conservan las métricas de v12 (el corte más fresco); v11 aportó 14,808 llaves que v12 ya no trae y v10 otras 12,382. Generado con `scripts/consolidar.py`.
**Data completa:** `reporte-content-objects-detallado-v12-consolidado.json` (generado con `scripts/analizar.py`).
**Referencia de campos content\*:** [OpenRTB 2.6 — Object: Content](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent)

**Cómo leer:** cada fila es una combinación agregada (publisher + app + país + señales de contenido), no un evento. Todo se reporta en dos vistas: **% de filas** (variedad de catálogo) y **% de requests** (tráfico real) — el 1% de las filas concentra el 50.3% de los requests, así que las dos vistas cuentan historias distintas. Un valor cuenta como "vacío" si es centinela (`Not Available`, `Not Applicable`, `Unknown`, etc.) o basura equivalente (`[-7]`, hash MD5 de cadena vacía).

---

# PARTE 1 — Análisis por columna (las 16)

## 1. Publisher ID

**Glosario.** Identificador numérico de la cuenta del publisher/seller en la plataforma que genera el reporte (el "seat" del vendedor). No es un campo OpenRTB del bid request. Un ID = una cuenta comercial; un mismo publisher puede tener varias.

**Datos.** 240 valores distintos, 100% fill. Relación limpia con Publisher (ningún ID apunta a dos nombres; 240 IDs para 234 nombres → ~6 publishers con más de una cuenta, p. ej. iion con 164918 + 166799). Top: 161101/OTTera 24.2% de filas, 161489/TCL APAC 13.2%, 164918/iion 13.0%, 161517/Select Plus 7.8%, 163091/TCL Springserve 7.3%. Las cuentas desproporcionadas en volumen: **165045/Roku con 1.6% de filas mueve 14.0% de requests** y 166869/TV Azteca con 0.38% mueve 5.3%.

## 2. Publisher

**Glosario.** Nombre comercial del vendedor. En CTV describe el **camino de suministro**, no necesariamente al dueño del contenido: "Roku - oRTB" o "Televisa Univision via OB" indican quién vende y por qué protocolo/ad server (oRTB = integración directa; SpringServe/FreeWheel/OB = intermediario).

**Datos.** 234 valores distintos, 100% fill. Top:

| Publisher | % filas | % requests |
|---|---:|---:|
| OTTera.tv | 24.2% | 24.2% |
| iion Pty Ltd | 15.0% | 7.6% |
| TCL ADs (APAC) | 13.2% | 8.8% |
| TCL ADS - Springserve | 13.0% | 11.3% |
| Select Plus PTE LTD (CTV) | 7.8% | 3.7% |
| PML Digital | 2.8% | 0.9% |
| METAX (Exchange) | 2.4% | 0.5% |
| Equativ - oRTB CTV | 2.4% | 3.2% |
| Roku - oRTB | 1.6% | **14.0%** |
| Televisa Univision via SpringServe | 1.5% | 4.4% |
| Coocaa (SKYWORTH) | 1.2% | 4.2% |
| Televisa Univision via OB | 0.7% | 2.7% |
| TV Azteca - Springserve | 0.4% | **5.3%** |

**Conclusiones.** El suministro sigue concentrado en OEMs de TV (OTTera + TCL×2 + iion + Select Plus ≈ 72% de filas, ~55% de requests). Los broadcasters (TelevisaUnivision por dos rutas, TV Azteca) pesan poco en catálogo y mucho en volumen. Para supply path conviene normalizar por dueño real: el mismo dueño aparece por varias rutas.

## 3. pageURL

**Glosario.** En CTV este campo transporta el **bundle de la app** (`app.bundle` en OpenRTB). El formato delata la tienda: `com.x.y` = Android/Google TV; numérico = Roku Channel Store (151908 = The Roku Channel, 552828 = ViX en Roku); `b0...` = ASIN de Amazon Fire TV; `g...` = Samsung Tizen (g15147002586 = Samsung TV Plus). `roku` y `+com.tcl.livetv` son valores malformados.

**Datos.** 675 valores distintos, 100% fill. Top: com.tcl.movieark 29.4% de filas / 27.6% de requests, com.tcl.livetv 24.4%/14.6%, com.tcl.waterfall.overseas 14.4%/9.6%, com.tcl.browser 10.2%/5.2%, com.coolita.channel 1.8%/4.7%, 151908 (Roku Channel) 1.3%/**11.7%**, 552828 (ViX-Roku) 1.1%/4.7%, com.tubitv 0.6%/**5.5%**.

**Conclusiones.** Las 4 apps nativas de TCL son el **78.4% de las filas pero solo el 57.0% de los requests**. Persisten ~7,600 filas con bundle malformado (`+com.tcl.livetv`, `roku`). El mismo servicio usa bundles distintos por plataforma (ViX aparece con 4), así que medir alcance por servicio requiere un mapa bundle→servicio.

## 4. App Name

**Glosario.** Nombre comercial de la app (`app.name`), texto libre y localizado por tienda/idioma — por eso la misma app aparece con múltiples variantes.

**Datos.** 394 distintos (393 útiles), fill 91.8% filas / 93.5% requests. Top: MovieArk 29.4%, Live TV 22.5%, TCL CHANNEL 14.4%, BrowseHere 10.2%, *Not Available* 8.2%, Coolita 1.8%, ViX (6+ variantes que suman ~4.5% de filas y ~10% de requests), The Roku Channel 1.3%/11.7%, Tubi (5 variantes), Plex (2).

**Conclusiones.** Nunca agrupar por App Name (ViX en 6 nombres, Tubi en 5); usar el bundle. Nombres genéricos ("Live TV", "Runtime", "LG") vienen del sistema operativo del TV, no de una app editorial. El 8.2% sin nombre es sobre todo inventario agregado de exchanges.

## 5. Country

**Glosario.** País del dispositivo (`device.geo.country`), normalizado a nombre en inglés.

**Datos.** 18 valores, 100% fill:

| País | % filas | % requests |
|---|---:|---:|
| Mexico | 28.7% | **60.8%** |
| Argentina | 18.8% | 17.7% |
| Chile | 11.2% | 5.9% |
| Colombia | 9.7% | 6.1% |
| Peru | 8.4% | 2.5% |
| Ecuador | 4.3% | 1.5% |
| Dominican Republic | 3.7% | 1.3% |
| Costa Rica | 3.3% | 1.3% |
| (los otros 10) | 12.1% | 3.0% |

**Conclusiones.** México mueve 4x más requests por fila que el resto (ahí viven Roku, TV Azteca y TelevisaUnivision). Los 10 países chicos suman 3% del tráfico: sus análisis van con cautela por muestra.

## 6. contentGenre

**Glosario.** `content.genre`: género del contenido. La spec lo define como **string libre**, sin taxonomía — cada publisher manda su vocabulario, a veces listas separadas por coma.

**Datos.** 8,149 distintos (8,146 útiles) — el consolidado de 3 archivos suma variantes de cola. Fill: **98.7% filas / 94.2% requests, el content object mejor poblado**. Top: drama 9.8%/10.7%, other 5.7%/3.1%, documentary 5.2%/3.0%, horror 3.8%/3.3%, comedy 3.4%/3.3%, combos (`drama,romance` 2.2%), entertainment 0.9%/**4.8%**, news 1.0%/2.6%, sports 1.3%/1.8%. El 49% de filas está fuera del top 30.

**Conclusiones.** Las 8,149 variantes son combos de ~30-40 géneros base (hay duplicados como `music,music` y prefijos `genre_*`). Con la normalización que ya está construida (split + sinónimos) queda una taxonomía de ~15 géneros útiles con >90% de cobertura — es la mejor señal contextual del dataset.

## 7. contentCategory

**Glosario.** `content.cat`: array de categorías IAB. La taxonomía la declara `cattax` (no incluido en el reporte); por defecto aplica la Content Category Taxonomy 1.0 (códigos IABx-y, deprecada). Códigos frecuentes: IAB1 Arts & Entertainment, IAB1-5 Movies, IAB1-6 Music, IAB1-7 Television, IAB12 News, IAB17 Sports. **`IAB1-22` no existe** en la taxonomía (IAB1 llega hasta IAB1-7). Los valores numéricos (`[640]`, `[325]`...) parecen taxonomía 2.x sin declarar. **`[-7]` no es ninguna categoría: es un placeholder/bug.**

**Datos.** 479 distintos (478 útiles). Fill real: **21.7% filas / 29.9% requests**. `[-7]` en 422,171 filas (78.3% / 70.1% de requests); [IAB1] 6.2%/6.2%; [IAB1-22] 3.7%/1.8%; [IAB1-7] 0.9%/**5.8%**; [IAB1-5, IAB1-7] 0.7%/4.0%; texto libre ([sports], [Live]) ~1%.

**Conclusiones.** La columna más rota: categoría IAB limpia y válida en apenas ~17% de filas. Los que sí categorizan (Roku, TelevisaUnivision — la rama IAB1-7) concentran ~10% del tráfico; el placeholder viene masivamente del ecosistema TCL/OEM. Sin el fix del `[-7]` no hay contextual ni brand safety por categoría.

## 8. contentSeries

**Glosario.** `content.series`: serie a la que pertenece el contenido. Valores especiales: `d41d8cd98f00b204e9800998ecf8427e` = **MD5 de la cadena vacía** (Roku ofusca la serie con hash; este valor es un vacío disfrazado), `{{CONTENT_SERIES}}` = macro de ad server sin reemplazar, `VOD`/`No Series`/`OTT Studios ...` = placeholders operativos.

**Datos.** 1,888 distintos (1,885 útiles). Fill real: **5.4% filas / 6.6% requests — la columna con menos datos**. `Not Available` 93.7%; el hash MD5 vacío en 4,388 filas pero **10.9% de los requests** (Roku); macro en 633 filas. Series reales ~3.5% de filas: Doña Bárbara, MasterChef México, Chicago Fire, The Good Doctor, J1 League, Podpah.

**Conclusiones.** Si se cuenta el hash como "poblado", el fill por requests se infla de 6.6% a ~17.5% — trampa clásica de QA. Tal como llega, solo sirve para targeting puntual en los pocos publishers que la mandan bien.

## 9. contentIsTitlePresent

**Glosario.** Bandera derivada por la plataforma del reporte (no es campo OpenRTB): indica si el bid request traía `content.title`.

**Datos.** 2 valores, 100% fill: `true` 91.7% de filas / 76.6% de requests; `false` 8.3% / **23.4%**.

**Conclusiones.** Consistente al decimal con contentTitle (8.29% de `Not Applicable`) — bandera fiable. La lectura importante es por requests: casi una cuarta parte del tráfico viaja sin título, concentrada en las rutas de mayor volumen.

## 10. contentLength

**Glosario.** `content.len`: duración del contenido **en segundos** según la spec. Aquí llega como enteros 1–8: son **buckets de duración sin documentar** (contenido de 1-8 segundos no existe). No usar como duración sin confirmar el mapeo con la fuente.

**Datos.** 9 distintos (8 útiles). Fill: 11.1% filas / **23.5% requests** (quien lo manda es gente de alto volumen — Roku). Distribución completa: N/A 88.9%; 6 → 3.2%/5.0%; 5 → 3.0%/7.6%; 4 → 2.6%/5.5%; 8 → 1.5%/3.7%; 7 → 0.5%/1.4%; 3/2/1 residuales.

## 11. contentLanguage

**Glosario.** `content.language`: idioma en ISO-639-1 (dos letras). Fuera de norma: `spa`/`eng`/`por` (ISO-639-2, que corresponde al campo `langb`), `sp` (no existe), `c` y `504` (basura). `ca` es catalán, real.

**Datos.** 485 distintos (483 útiles). Fill: 79.5% filas / 86.5% requests. `en` 48.3% filas / 40.2% requests; **`es` 26.6% filas / 41.9% requests**; N/A 20.4%/13.5%; `pt` 1.2%/1.9%; cola de ru/hi/de/fr/ja/etc. <0.5% cada uno.

**Conclusiones.** Se mantiene la paradoja del dataset: el inglés gana en catálogo, el español gana en tráfico. La cola de idiomas delata catálogo global de relleno en apps OEM. Normalizar los códigos de 3 letras antes de segmentar.

## 12. contentIsLiveStream

**Glosario.** `content.livestream`: 1 = transmisión en vivo/lineal (FAST, eventos), 0 = VOD. 

**Datos.** 3 valores (1 útil): `Unknown` 40.2%, `Not Available` 30.9%, `1` 28.8% de filas / **37.6% de requests**.

**Conclusiones.** **Nunca llega un 0**: la ausencia no es interpretable como VOD, así que no se puede medir la proporción real live/VOD. Sirve solo como señal positiva de live (37.6% del tráfico confirmado).

## 13. contentTitle

**Glosario.** `content.title`: título del contenido. Valores no literales: `roku`/`epg` (placeholders del EPG de Roku — título oculto), `{{content_title}}` (macro sin reemplazar), sufijos ": trailer" (pre-roll sobre trailers de OTT Studios).

**Datos.** **15,260 distintos — la mayor cardinalidad del dataset**. Fill: 91.7% filas / 76.5% requests. El 88.3% de filas está fuera del top 30 (títulos únicos de catálogo). `roku`+`epg` son 0.33% de filas pero **5.8% de requests**. Persiste el mojibake (`catalunya �ber alles!`).

**Conclusiones.** Sumando el 23.5% de requests sin título más los placeholders de Roku, **~30% del tráfico no es targeteable por título**. El top repite las películas B de OTT Studios en todos los países — parte de la "variedad" es un mismo catálogo replicado.

## 14. contentRating

**Glosario.** `content.contentrating`: clasificación de edad, texto libre en la práctica. Conviven 5 sistemas: **TV Parental Guidelines** (tv-g/tv-pg/tv-14/tv-ma y variantes sucias tv14, tvpg, `tvpg_tv_14` = sistema+rating concatenados), **MPAA** (g/pg/pg-13/r/nc-17), **edades numéricas** (10–18, estilo ClassInd), **RTC México** (`b`), y **sin clasificar** (nr, not rated, `banned`). `dv-t`/`dv-g` y `mpaa_r` son prefijos de sistema sin normalizar.

**Datos.** 187 distintos (182 útiles). Fill: 84.8% filas / 88.6% requests. Top: N/A 15.2%, tv-14 11.5%/**15.7%**, tv-ma 11.1%/9.8%, r 11.0%/7.9%, tv-pg 8.1%/5.2%, nr 7.3%/4.4%, g 5.8%/4.3%, edades numéricas ~11% de filas, variantes concatenadas ~1.5% de filas pero **~8.4% de requests**.

**Conclusiones.** Buena cobertura pero inutilizable sin normalizar (ya existe el mapa a 7 franjas: cubre 97%). El contenido maduro (tv-ma/r/nc-17/18) ronda 27% de filas. El ~10% declarado "sin clasificar" conviene tratarlo como categoría propia — paga ~24% menos según el análisis de monetización.

## 15. Total Requests

**Glosario.** Bid requests registrados para la combinación en la ventana. Mide volumen/alcance potencial, no impresiones vendidas.

**Datos.** min 28,560 · mediana 101,520 · media 795,965 · p90 1,032,640 · p99 9,363,048 · **max 4,580,856,640** (WhaleLive/México). **El top 1% de filas concentra el 50.3% de los requests.** El mínimo constante ~28K confirma el umbral de corte del reporte; el consolidado recupera la cola perdida entre cortes, no la que queda bajo el umbral.

## 16. eCPM

**Glosario.** Ingresos efectivos por mil impresiones de esa combinación en la ventana. eCPM = 0 significa que no generó revenue en el periodo, no que sea invendible.

**Datos.** Filas en cero: 447,102 (**82.9%**, que son el 49.3% de los requests). Sobre las 92,088 filas con eCPM > 0: media 4.84 · mediana 3.10 · p90 10.5 · **ponderado por requests 4.55** · máximo 76.67. Por rangos (en % de requests totales): 1–3 → 17.5%, 3–5 → 9.4%, 5–10 → 18.0%, 10–20 → 3.4%, ≥20 → 0.06%.

**Conclusiones.**
- La mitad del tráfico corre por combinaciones con revenue; el grueso se transa entre 1 y 10 USD.
- **Cambio relevante en v12: el outlier de 200.0 desapareció** (la fila de ViX/Perú se recalculó; el máximo bajó a 76.7) **y el eCPM de WhaleLive — la fila más grande del dataset — cayó de 13.6 a 4.9**. Eso arrastra el ponderado global de ~4.98 a 4.55 y el bucket 10–20 se encogió de ~5% a 3.4% del tráfico. Los precios altos del corte anterior se revisaron a la baja: otra razón para no leer estos reportes como serie temporal sin verificar qué recalcula la plataforma entre versiones.

---

# PARTE 2 — Análisis por país (México, Colombia y Chile)

Solo estos tres mercados por pedido expreso; el JSON trae el mismo detalle (top-15 por columna) solo para ellos. Los porcentajes de "top valores" son sobre las filas del país.

## México — 154,529 filas (28.7%) · 60.8% de los requests

eCPM: 82.2% de filas en cero · media no-cero 2.61 · **ponderado 3.78**

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 174 | 100% | OTTera 14.7%, iion 12.8%, TCL Springserve 11.5%, TCL APAC 10.9%, Equativ 7.3% |
| pageURL | 513 | 100% | com.tcl.livetv 24.1%, com.tcl.movieark 22.9%, com.tcl.browser 5.8%, 974696 (Roku) 5.2% |
| App Name | 308 | 82.8% | MovieArk 22.9%, Live TV 21.4%, *N/A 17.2%*, BrowseHere 5.8% |
| contentGenre | 6,167 | 99.0% | drama 10.8%, documentary 4.2%, other 4.1%, comedy 3.7%, horror 3.4% |
| contentCategory | 312 | 22.9% | *[-7] 77.1%*, [IAB1] 4.5%, [IAB1-5] 3.7%, [IAB12] 2.7% |
| contentSeries | 1,517 | 6.9% | *N/A 91.6%*, md5-vacío 1.5%, VOD 0.5%, Doña Bárbara 0.2% |
| contentLength | 9 | 17.5% | *N/A 82.5%*, 6 6.4%, 5 3.9%, 8 3.5% |
| contentLanguage | 477 | 77.7% | en 36.6%, es 36.3%, *N/A 22.1%*, spa 0.8% |
| contentIsLiveStream | 3 | 25.5% | *Unknown 38.7%*, *N/A 35.8%*, 1 25.5% |
| contentTitle | 11,685 | 82.5% | *N/A 17.5%*, las estrellas 0.4%, canal 5 0.3%, golden 0.3% |
| contentRating | 154 | 84.7% | *N/A 15.2%*, tv-14 13.7%, r 10.1%, tv-ma 8.2% |
| contentIsTitlePresent | 2 | — | true 82.5%, false 17.5% |

**Conclusiones — México:**
- Único mercado con paridad inglés/español (36.6% vs 36.3%), gracias a los broadcasters locales (Televisa: "Las Estrellas" y "Canal 5" en el top de títulos).
- La peor tasa de títulos de los mercados grandes (17.5% sin título): la ruta Roku/EPG y los agregadores pierden el título justo en el mercado más grande. También es el más fragmentado: 174 publishers, 513 bundles, 6,167 variantes de género.
- **El eCPM ponderado bajó de 4.44 a 3.78 con las métricas de v12** — es donde golpea el recálculo de WhaleLive, que es tráfico mexicano. El eCPM medio no-cero (2.61) sigue siendo el más bajo de los grandes: mucha cola barata con un núcleo premium (Roku, TV Azteca).

## Colombia — 52,176 filas (9.7%) · 6.1% de los requests

eCPM: 87.8% de filas en cero · media no-cero 2.63 · **ponderado 3.01**

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 93 | 100% | iion 30.0%, OTTera 24.5%, Select Plus 11.4%, TCL APAC 11.0%, METAX 7.6% |
| pageURL | 176 | 100% | com.tcl.movieark 34.6%, com.tcl.livetv 28.4%, com.tcl.waterfall 13.3%, com.tcl.browser 8.1% |
| App Name | 134 | 96.7% | MovieArk 34.6%, Live TV 28.3%, TCL CHANNEL 13.3%, BrowseHere 8.1% |
| contentGenre | 1,337 | 98.5% | drama 10.1%, other 7.6%, documentary 4.8%, horror 4.3% |
| contentCategory | 128 | 24.3% | *[-7] 75.7%*, [IAB1] 7.1%, [IAB1-22] 3.5%, [sports] 1.9% |
| contentSeries | 580 | 5.7% | *N/A 94.3%*, VOD 0.9%, No Series 0.1% |
| contentLength | 9 | 9.6% | *N/A 90.4%*, 4 3.2%, 5 2.8%, 6 2.5% |
| contentLanguage | 30 | **62.2%** | en 41.8%, *N/A 37.8%*, es 15.6%, c (basura) 1.9% |
| contentIsLiveStream | 3 | 28.0% | *Unknown 44.9%*, 1 28.0%, *N/A 27.0%* |
| contentTitle | 4,371 | 94.9% | *N/A 5.1%*, {{content_title}} 0.2%, haus of horror 0.2% |
| contentRating | 97 | 80.2% | *N/A 19.8%*, r 11.8%, tv-14 9.8%, tv-pg 9.4%, nr 8.8% |
| contentIsTitlePresent | 2 | — | true 94.9%, false 5.1% |

**Conclusiones — Colombia:**
- Sigue siendo **el mercado enfermo de los grandes**: 87.8% de filas sin revenue y ponderado de 3.01, con volumen de sobra (3° por filas). No es problema de catálogo sino de demanda.
- El peor idioma de los grandes (62.2% fill; en 41.8% vs es 15.6%): inventario mayormente importado sin señal local. La macro `{{content_title}}` sigue activa en su supply.
- iion lidera aquí (30.0%) — el único mercado grande donde no manda OTTera ni TCL.

## Chile — 60,427 filas (11.2%) · 5.9% de los requests

eCPM: 80.6% de filas en cero · media no-cero 7.30 · **ponderado 8.17**

| Columna | Distintos | Fill | Top valores (% filas del país) |
|---|---:|---:|---|
| Publisher | 93 | 100% | iion 21.2%, TCL Springserve 19.1%, OTTera 17.1%, TCL APAC 17.1%, PML Digital 6.6% |
| pageURL | 145 | 100% | com.tcl.movieark 41.6%, com.tcl.livetv 34.7%, com.tcl.waterfall 7.4%, com.tcl.browser 5.5% |
| App Name | 106 | 92.3% | MovieArk 41.6%, Live TV 30.2%, *N/A 7.7%*, TCL CHANNEL 7.4% |
| contentGenre | 1,441 | 99.5% | drama 8.5%, other 6.7%, documentary 6.2%, horror 3.6% |
| contentCategory | 110 | **14.4%** | *[-7] 85.5%*, [IAB1] 6.4%, [IAB1-22] 0.8% |
| contentSeries | 500 | 4.5% | *N/A 95.5%*, VOD 0.9%, {{CONTENT_SERIES}} 0.1% |
| contentLength | 9 | 6.9% | *N/A 93.1%*, 4 2.6%, 5 1.8%, 6 1.6% |
| contentLanguage | 44 | 75.3% | en 52.6%, *N/A 24.7%*, es 18.6%, pt 1.4% |
| contentIsLiveStream | 3 | **17.8%** | *N/A 42.5%*, *Unknown 39.7%*, 1 17.8% |
| contentTitle | 4,089 | 96.6% | *N/A 3.4%*, catalunya über alles! 0.2%, the baddest bad boy 0.2% |
| contentRating | 95 | 83.2% | *N/A 16.8%*, tv-ma 13.5%, r 11.8%, tv-14 10.6%, nr 9.2% |
| contentIsTitlePresent | 2 | — | true 96.6%, false 3.4% |

**Conclusiones — Chile:**
- **El mejor precio de los mercados grandes se sostiene en v12** (ponderado 8.17, medio 7.30) con tasa de monetización normal (80.6% en cero).
- Perfil muy VOD/película: MovieArk sola es el 41.6% de las filas y el fill de livestream es el mínimo del dataset (17.8%).
- Metadata estructural pobre (categoría 14.4%, duración 6.9%) y catálogo muy anglófono (en 52.6% vs es 18.6%): el precio alto viene de la demanda del mercado, no de la calidad de señal.

---

**Síntesis.** El tercer corte confirma todo lo estructural (fills, problemas de calidad, jerarquías por país) y aporta dos novedades: los agregados crecen ~2.6% de llaves por el churn del límite de exportación de 512K filas, y **las métricas de precio se recalculan entre cortes** (desapareció el outlier 200.0, WhaleLive bajó de 13.6 a 4.9, el ponderado global pasó de ~4.98 a 4.55). Moraleja operativa: los content objects son estables entre versiones; los eCPM no — cualquier análisis de precio debería fijar la versión del reporte que usa.
