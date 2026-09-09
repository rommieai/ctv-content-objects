# Reporte — Relleno de content objects: qué se hizo columna por columna (consolidado v10 a v17)

**Fuente:** `inventory-consolidado-v10-a-v17-enriquecido.csv` — 959,442 filas (métricas del corte v17).
**Generado con:** `scripts/enriquecer_externo.py` → `inventory-consolidado-v10-a-v17-relleno.csv` + `reporte-relleno-v17.json` (los porcentajes exactos de este reporte salen de ese JSON; el desglose por país, de `reporte-relleno-v17-por-pais.json`). Corrida del 9 sep 2026.

**Convención de porcentajes: todos los % de este reporte son % de filas** (nunca de requests). Cuando el % es sobre las 959,442 filas del consolidado se dice "**del total**"; cuando es sobre las filas que venían vacías en esa columna se dice "**de las vacías**". Una celda cuenta como vacía si no trae nada o trae un centinela/basura (`Not Available`, `Unknown`, `[-7]`, hash MD5 de cadena vacía, macros `{{...}}`).

**Qué cambió respecto a la corrida anterior (v10 a v16):** la escritura nueva del reporte ya es el 54% del corte v17 (30% del consolidado). Eso obligó a dos ajustes del script: el rating se canoniza al aprender (`Teen Plus` cuenta como `tv-14`), y la propagación de series por título exige evidencia mínima (30 filas, 2 publishers). Ambos se explican en su columna.

---

## Cómo funciona el relleno (lo común a todas las columnas)

Cada fila del consolidado no es un programa: es una **combinación** de 14 dimensiones (país × publisher × app × género × …). El mismo contenido llega por muchas rutas de venta a la vez y **cada ruta manda la metadata como quiere**, y desde v16 también llega en **dos escrituras del reporte** (`tv-14`/`en` en la vieja, `Teen Plus`/`English` o `Not Applicable` en la nueva). El "vacío" casi nunca significa que nadie sepa el dato — significa que *esa ruta* (o *ese formato*) lo descarta. Sobre esa redundancia se montan las corridas.

El script hace dos pasadas. La **pasada 1** aprende del propio dataset: normaliza el título de cada fila a una clave (`hatchback: trailer` → `hatchback`; 14,686 claves distintas), y arma dos memorias: qué valores trae cada título cuando sí vienen (`conocido`) y qué manda cada app cuando manda (`por_app`). Al aprender, idioma y rating se traducen a una sola escritura (`English`→`en`; `All Ages`→`g`, `Teen`→`tv-pg`, `Teen Plus`→`tv-14`, `Adults`→`tv-ma`, `Unrated`→`nr`). Las fuentes externas se consultan **una vez por título** y quedan en caché. La **pasada 2** rellena fila por fila probando fuentes en un orden fijo — la primera que da valor gana — y anota de dónde salió cada valor en `<col>_origen`:

| Corrida | Qué hace | Candado |
|---|---|---|
| `original` | La fila ya traía el dato. Nunca se toca. | — |
| `intra_titulo` | Copia el dato de otra fila **del mismo título** (misma película, distinta ruta o distinto formato). | El valor debe dominar ≥ 80% de las filas con dato de ese título. En `contentSeries`, además ≥ 30 filas y ≥ 2 publishers con dato. |
| `app_default` | Copia el valor constante **de la misma app** (mismo vendedor, distinto título). | La app debe mandar ese valor ≥ 95% de las veces, con ≥ 200 filas de evidencia. |
| `imdb` / `wikidata` / `tvmaze` | Fuentes externas, vía el título normalizado. | Solo matches IMDb de confianza A (~90% precisión) o B (~75%). |
| `derivado_*` | Traduce **otra columna de la misma fila** (género → categoría IAB; tipo IMDb → categoría/serie). | Según columna, ver abajo. |
| `app_semantica` | Solo livestream: veredicto por app validado a mano (`semantica_apps.csv`). | Solo filas con `aplicar=si` en el CSV. |

---

## contentLanguage — 66.3% → 96.1% del total

Vacías al inicio: 33.7% del total. Se rescató el 88.4% de las vacías. Sigue siendo el caso más puro de "el dataset se rellena a sí mismo": el vacío es un artefacto de un SSP (iion, 97% sin idioma) y del formato nuevo del reporte, y en los dos casos el dato está en las filas hermanas.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 66.3% | Lo declarado (incluye `English`/`Spanish` tal cual llegaron). |
| intra_titulo | +29.0% | "chicken stew" trae `en` por 2,009 filas de 6+ rutas y `es` por 318 → las vacías (iion y las del formato nuevo) reciben `en`. De las 155k filas del formato nuevo que llegaron sin idioma, 133k se rellenaron así. |
| app_default | +0.5% | Solo apps monolingües: ViX (`es`), iion\|LG y Free Games by PlayWorks (`en`). |
| wikidata | +0.3% | Idioma original de la obra (P364), último recurso. |
| sin_dato | 3.9% | Títulos multilingües bloqueados por el candado ("space dogs 3": `ru`×416, `es`×61, `en`×44) — información, no ruido — y un residuo de la escritura nueva que aún no se canoniza: "ivan's game" trae `hr`×399 y `Croatian`×124 como valores distintos (399 de 580 = 69% < 80% → bloqueado). Ampliar `IDIOMA_CANON` con `Croatian`, `Bengali` lo resuelve. |

## contentRating — 74.3% → 82.2% del total

Vacías al inicio: 25.7% del total. Se rescató el 30.7% de las vacías. Esta es la columna donde el formato nuevo más pesó y donde el ajuste del script fue necesario: **sin canonizar la escala nueva, la primera pasada de esta corrida dejó el rating en 76.2%** (+1.8pp), porque `tv-14`×1367 y `Teen Plus`×616 del mismo título competían como valores distintos y ninguno llegaba al 80%.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 74.3% | Lo declarado, en cualquiera de las escalas. |
| intra_titulo | +7.9% | Con la escala nueva traducida al aprender, "hatchback" = `tv-14`×1,983 → sus vacías reciben `tv-14`; "crazy on the outside" = `r`×424 + `Adults`×103 (→`tv-ma`) → 80% → `r`. De las 122k filas del formato nuevo que llegaron sin rating, 37k se rellenaron así. |
| wikidata | +0.1% | P3834 solo en ~3% de los títulos, y en escala RTC. |
| app_default | +0.0% | Solo apps rígidas (WhaleLive `dv-g`, Roku vía Seedtag `tv-14`). |
| sin_dato | 17.8% | Ahora la ambigüedad que queda es **real, entre franjas**: "chicken stew" `tv-pg`×1,130 vs `g`×859 (55%); "corona" `tv-14`×940 vs `tv-ma`×805 (54%). No se adivina. Lo que sí queda pendiente: el intra sobre `rating_franja` daría el mismo resultado aquí (son franjas distintas), así que el siguiente escalón real es TMDB (clasificación por país). |

## contentCategory — 21.9% → 94.3% del total

Vacías al inicio: 78.1% del total. Se rescató el 92.7% de las vacías. Sin cambios de fondo respecto a las corridas anteriores.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 21.9% | Lo que ya venía ([IAB…] de Roku, Vidaa, LG…). |
| intra_titulo | +9.7% | "golden edge" = `[IAB12]` por Vidaa/Equativ/METAX (437 filas) → a las filas de OTTera/TCL con `[-7]`; "naruto shippuden" = `[IAB1]` por OTTera → a las rutas TCL. |
| app_default | +8.7% | OTTera→MovieArk `[IAB1]` (62,408 filas rellenadas), OTTera→Live TV `[IAB1]` (10,631), PML→Live TV `[sports]` (10,271). |
| derivado_genero | +23.6% | La fila vacía en categoría casi siempre está llena en contentGenre (94%). Mapa género→IAB aprendido de las filas que traen ambas: deportes→`[IAB17]`, noticias→`[IAB12]`, música→`[IAB1-6]`, infantil/animación/telenovela/reality→`[IAB1-7]`. |
| derivado_tipo | +30.3% | Para géneros que no definen categoría, desempata el tipo del match IMDb: `movie`→`[IAB1-5]`, `tvSeries`→`[IAB1-7]`. |
| sin_dato | 5.7% | Sin título buscable, sin género, o ambigüedad real ("entrepreneur tv": `[IAB1]`×27, `[IAB1-22]`×17, `[sports]`×13). |

## contentIsLiveStream — 28.8% → 49.7% del total

Vacías al inicio: 71.2% del total. Se rescató el 29.4% de las vacías — **a propósito**. La columna mide el **modo de entrega**, el valor declarado es `1` en el 100% de las filas que lo traen (incluidas 83,298 filas de películas según IMDb) y propagarlo no agrega información. `intra_titulo` está **apagado** aquí y solo corren fuentes defendibles:

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 28.8% | El `1` declarado. Intacto. |
| derivado_tipo (señales del vendedor) | +0.5% | `contentSeries = "VOD"` → `0`; `contentSeries = "... Livestream"` → `1`. |
| app_semantica | +20.4% | Veredicto por app validado a mano (`semantica_apps.csv`, 2 bundles activos): "Live TV" de TCL y Coolita Channel → `1`. Las mixtas (MovieArk, TCL Channel, ViX, Tubi, Roku…) no rellenan nada. |
| sin_dato | 50.3% | Honestamente vacío: distinguirlo requiere el EPG/feed del vendedor. |

## contentLength — 12.2% → 50.1% del total

Vacías al inicio: 87.8% del total. Se rescató el 43.2% de las vacías. Los valores son **códigos 1–8** que no correlacionan de forma monótona con la duración real (código 3 → 12 min, 7 → 150, pero 1/5/8 → 60 y 4/6 → 84–93) — por eso no se usa ninguna fuente externa: solo se copian códigos que el propio sistema ya emitió.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 12.2% | Los códigos declarados (Roku 4–6, ViX siempre 8…). |
| intra_titulo | +35.4% | "brooklyn love stories" = `4`×322 por 6 rutas, `6`×14, `2`×9 → 93% → las vacías reciben `4`. |
| app_default | +2.6% | Vidaa `5` (7,367), iion→BrowseHere `4` (6,787), ViX `8` (3,254), Aluna→TCL Channel `4` (2,466). |
| sin_dato | 49.9% | Títulos que nunca traen código en ninguna ruta, más ambigüedades reales ("cain": `3`×2, `4`×2). |

Lo útil para análisis sigue siendo **`ext_runtime_min`** (duración real vía IMDb/Wikidata) en el 43.0% del total de filas.

## contentSeries — 6.5% → 14.1% del total

Vacías al inicio: 93.5% del total. Se rescató el 8.1% de las vacías — el techo es estructural (el catálogo es ~76% película) y **esta corrida añade un candado que baja la cobertura a cambio de precisión**.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 6.5% | Con asterisco: parte es placeholder (`VOD`, `No Series`, `OTT Studios …`) que se respeta pero **no se propaga**. |
| imdb | +6.9% | Si el match (A/B) dice que el título ES `tvSeries`/`tvMiniSeries`, el nombre de la serie es el título canónico. Es el origen más confiable para series. |
| intra_titulo | +0.7% (era +1.9%) | Ahora solo cuando el título tiene ≥ 30 filas con serie y ≥ 2 publishers: "breathe" → *Breathe* (45 filas, 3 rutas, 1,065 rellenadas), "plant center" (55, 5), "el peso del amor" → *Oh My Venus* (45, 4; correcto: es su título en español). **Bloqueados los falsos positivos de la corrida anterior**: "abandoned" → *FBI* (3 filas: era el episodio "Abandoned" de esa serie), "continuum" → *WDBJ News* (20), "insert coin" → *Pocoyo* (4), "la rosa de guadalupe" → *Mother Stabbed Trial* (2 filas de Vidaa). Se pierde algún verdadero positivo chico ("mxf01" → *FIFA Club World Cup*, 4 filas) y queda un residuo dudoso que pasa el candado ("grandes parejas" → *Curro Jiménez*, 302 filas). |
| sin_dato | 85.9% | Mayormente películas (vacío correcto) + títulos sin match. |

## contentGenre — 93.6% → 98.0% del total

Vacías al inicio: 6.4% del total (1.2% antes del cambio de formato; la escritura nueva trae `Not Applicable` en una de cada nueve filas). Se rescató el 69% de las vacías. La columna es el **insumo** de los demás rellenos.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 93.6% | Lo declarado (normalizado aparte en `genero_normalizado`; `Drama` = `drama`). |
| intra_titulo | +2.4% | Las filas del formato nuevo sin género tienen hermanas con género: "the cube usa" recibe la etiqueta larga de Coocaa/AWG; "unboxathon" recibe `other`. |
| imdb | +1.8% | Géneros IMDb traducidos al vocabulario canónico. Va al final porque en títulos de una palabra el match puede ser dudoso. |
| app_default | +0.2% | Apps de juegos casuales (iion\|LG, Free Games by PlayWorks) → `game`. |
| sin_dato | 2.0% | Residuo, más títulos bloqueados por ambigüedad de escritura ("forest frenzy of boonie bears": `kids`×919, `kids,anime,action,comedy`×305, `Children`×172…). Mejora pendiente: intra sobre `genero_normalizado`. |

---

## Resumen

| Columna | Antes (del total) | Después (del total) | % de las vacías rescatado | Corrida dominante |
|---|---:|---:|---:|---|
| contentLanguage | 66.3% | **96.1%** | 88.4% | intra_titulo (29.0) |
| contentCategory | 21.9% | **94.3%** | 92.7% | derivados de género/tipo (53.9) |
| contentRating | 74.3% | **82.2%** | 30.7% | intra_titulo (7.9), con la escala nueva canonizada |
| contentLength | 12.2% | **50.1%** | 43.2% | intra_titulo (35.4) |
| contentIsLiveStream | 28.8% | **49.7%** | 29.4% | app_semantica validada (20.4) |
| contentSeries | 6.5% | **14.1%** | 8.1% | imdb tipo serie (6.9) |
| contentGenre | 93.6% | **98.0%** | ~69% | intra_titulo (2.4) |

Frente a la corrida sobre v10–v16, el "después" es el mismo en idioma, categoría, livestream y length; rating queda 3 puntos más abajo (ambigüedad real entre franjas, ya no de escritura) y series 1 punto más abajo (candado nuevo). Cada valor rellenado lleva su `<col>_origen` en el CSV de salida, así que cualquier análisis puede quedarse solo con los orígenes que le den confianza.
