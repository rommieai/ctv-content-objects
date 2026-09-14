# Reporte — Relleno de content objects: qué se hizo columna por columna (consolidado v10 a v16)

**Fuente:** `inventory-consolidado-v10-a-v16-enriquecido.csv` — 810,933 filas (métricas del corte v16).
**Generado con:** `scripts/enriquecer_externo.py` → `inventory-consolidado-v10-a-v16-relleno.csv` + `reporte-relleno-v16.json` (los porcentajes exactos de este reporte salen de ese JSON; el desglose por país, de `reporte-relleno-v16-por-pais.json`). Corrida del 9 sep 2026.

**Convención de porcentajes: todos los % de este reporte son % de filas** (nunca de requests). Cuando el % es sobre las 810,933 filas del consolidado se dice "**del total**"; cuando es sobre las filas que venían vacías en esa columna se dice "**de las vacías**". Una celda cuenta como vacía si no trae nada o trae un centinela/basura (`Not Available`, `Unknown`, `[-7]`, hash MD5 de cadena vacía, macros `{{...}}`).

**Qué cambió respecto a la corrida anterior (v10 a v15):** el corte v16 llegó con un formato nuevo en el 28% de sus filas — rating en escala nueva (`All Ages`, `Teen`, `Teen Plus`, `Adults`), idioma como nombre (`English`) y, sobre todo, **rating e idioma vacíos** en dos de cada tres de esas filas. Por eso el punto de partida de contentLanguage (66.9% del total, venía de 77.2%) y contentRating (72.9%, venía de 83.9%) es peor, y por eso el relleno de esas dos columnas es el protagonista de esta tanda.

---

## Cómo funciona el relleno (lo común a todas las columnas)

Cada fila del consolidado no es un programa: es una **combinación** de 14 dimensiones (país × publisher × app × género × …). El mismo contenido llega por muchas rutas de venta a la vez y **cada ruta manda la metadata como quiere**: el título "golden edge" trae `contentCategory=[IAB12]` cuando viaja por Vidaa o Equativ y `[-7]` cuando viaja por OTTera/TCL. Y desde v16 hay una segunda fuente de redundancia: **el mismo contenido en los dos formatos del reporte** — `hatchback` trae `tv-14` y `en` en las filas del formato viejo y `Not Applicable` en las del nuevo. El "vacío" casi nunca significa que nadie sepa el dato — significa que *esa ruta* (o *ese formato*) lo descarta. Sobre esa redundancia se montan las corridas.

El script hace dos pasadas. La **pasada 1** aprende del propio dataset: normaliza el título de cada fila a una clave (`hatchback: trailer` → `hatchback`; 14,343 claves distintas), y arma dos memorias: qué valores trae cada título cuando sí vienen (`conocido`) y qué manda cada app cuando manda (`por_app`). Novedad de esta tanda: al aprender el idioma, `English`/`Spanish` se cuentan como `en`/`es`, para que las dos escrituras del reporte no compitan entre sí. Las fuentes externas se consultan **una vez por título**, no por fila, y quedan en caché. La **pasada 2** rellena fila por fila probando fuentes en un orden fijo — la primera que da valor gana — y anota de dónde salió cada valor en `<col>_origen`:

| Corrida | Qué hace | Candado |
|---|---|---|
| `original` | La fila ya traía el dato. Nunca se toca. | — |
| `intra_titulo` | Copia el dato de otra fila **del mismo título** (misma película, distinta ruta o distinto formato). | El valor debe dominar ≥ 80% de las filas con dato de ese título; si no, no se rellena. |
| `app_default` | Copia el valor constante **de la misma app** (mismo vendedor, distinto título). | La app debe mandar ese valor ≥ 95% de las veces, con ≥ 200 filas de evidencia. |
| `imdb` / `wikidata` / `tvmaze` | Fuentes externas, vía el título normalizado. | Solo matches IMDb de confianza A (candidato único + género compatible, ~90% precisión) o B (desempatado por género, ~75%). |
| `derivado_*` | Traduce **otra columna de la misma fila** (género → categoría IAB; tipo IMDb → categoría/serie). | Según columna, ver abajo. |
| `app_semantica` | Solo livestream: veredicto por app validado a mano (`semantica_apps.csv`). | Solo filas con `aplicar=si` en el CSV. |

La diferencia entre las dos primeras, en una frase: `intra_titulo` responde "¿qué es *este contenido*?" y `app_default` responde "¿qué manda *este vendedor*?". La primera es más precisa y por eso corre antes.

---

## contentLanguage — 66.9% → 95.9% del total

Vacías al inicio: 33.1% del total (venía de 22.8%). Se rescató el 87.6% de las vacías. Es el caso más puro de "el dataset se rellena a sí mismo" y el que más creció en esta tanda: el vacío era un artefacto de un SSP (iion, que despoja el campo) **y ahora también del formato nuevo del reporte**, que trae `Not Applicable` en el 72% de sus filas; en los dos casos el dato está en las filas hermanas.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 66.9% | Lo declarado (incluye `English`/`Spanish` tal cual llegaron: el original nunca se toca). |
| intra_titulo | +28.2% | "chicken stew" trae `en` por 1,705 filas de 6+ rutas (Aluna, Equativ, Kivi, NubaTV…) y `es` por 249 → las vacías (iion y las del formato nuevo) reciben `en`. De las 102k filas del formato nuevo que llegaron sin idioma, 86k se rellenaron así. |
| app_default | +0.5% | Solo apps monolingües calificaron: ViX (`es`), iion\|LG y Free Games by PlayWorks (`en`). |
| wikidata | +0.3% | Idioma original de la obra (P364), último recurso. |
| sin_dato | 4.1% | Títulos bilingües o multilingües bloqueados por el candado: "om nom" trae `en`×221, `es`×157, `de`×88, `fr`×88 → ningún idioma pasa del 80% → no se adivina. La mezcla es información (pistas de audio), no ruido. |

## contentRating — 72.9% → 85.4% del total

Vacías al inicio: 27.1% del total (venía de 16.1%). Se rescató el 46.1% de las vacías. Contexto: cada vendedor manda su propio sistema de clasificación (`tv-14` US TV, `r` MPAA, `b`/`b15` RTC mexicana, `16`/`16+` numéricos) y desde v16 se suma la escala del formato nuevo (`All Ages`, `Teen`, `Teen Plus`, `Adults`, `Unrated`), que por cruce de títulos equivale a `g` / `tv-pg` / `tv-14` / `r`–`tv-ma` / `nr`.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 72.9% | Lo declarado, en cualquiera de las escalas. |
| intra_titulo | +12.4% | "hatchback" trae `tv-14`×1,367 y `Teen Plus`×282 → dominante 83% → las vacías reciben `tv-14`. De las 97k filas del formato nuevo que llegaron sin rating, 50k se rellenaron así. Lo más escrito: `tv-14`, `tv-ma`, `tv-pg`, `r`. |
| wikidata | +0.1% | P3834 existe pero solo ~3% de los títulos la tienen (y en escala RTC). |
| app_default | +0.0% | Casi nada califica: solo apps rígidas (WhaleLive `dv-g`). |
| sin_dato | 14.6% | El candado bloqueó mucho: 93% de ambigüedad entre títulos rellenables, casi toda por *sistemas distintos* ("chicken stew": `tv-pg`×907, `g`×686, `Teen`×45, `All Ages`×12 → dominante 55% < 80% → no se rellena; "corona": `tv-14`×639, `tv-ma`×551, `Teen Plus`×143, `Adults`×132). Mejora pendiente (ahora más urgente): hacer el intra sobre `rating_franja` en vez del código crudo — `tv-14` y `Teen Plus` son la misma franja. |

## contentCategory — 22.8% → 94.9% del total

Vacías al inicio: 77.2% del total. Se rescató el 93.4% de las vacías. Sin cambios de fondo respecto a la corrida anterior (95.2%).

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 22.8% | Lo que ya venía ([IAB…] de Roku, Vidaa, LG…). |
| intra_titulo | +10.3% | El mismo título trae categoría en otra ruta: "golden edge" = `[IAB12]` por Vidaa/Equativ/METAX (419 filas) → se copia a las filas de OTTera/TCL que traían `[-7]`. "naruto shippuden" = `[IAB1]` por OTTera → a las rutas TCL. |
| app_default | +8.9% | Apps monotemáticas: OTTera→MovieArk manda `[IAB1]` (51,724 filas rellenadas), OTTera→Live TV `[IAB1]` (10,713), PML→Live TV `[sports]` (9,266). Vidaa **perdió** este corte su default `[IAB12]` (con más `[-7]` en el formato nuevo ya no llega al 95%); sus vacías se llenan por intra o género. |
| derivado_genero | +24.1% | La fila vacía en categoría casi siempre está **llena en contentGenre** (96%). Mapa género→IAB aprendido de las filas que traen ambas columnas: deportes→`[IAB17]`, noticias→`[IAB12]`, música→`[IAB1-6]`, infantil/animación/telenovela/reality→`[IAB1-7]`. |
| derivado_tipo | +28.7% | Para géneros que no definen categoría (un *drama* puede ser película o serie), desempata el tipo del match IMDb: `movie`→`[IAB1-5]`, `tvSeries`→`[IAB1-7]`. |
| sin_dato | 5.1% | Sin título buscable, sin género, y títulos bloqueados por ambigüedad real ("entrepreneur tv": `[IAB1]`×27, `[IAB1-22]`×17, `[sports]`×13 → nadie domina). |

## contentIsLiveStream — 28.1% → 49.3% del total

Vacías al inicio: 71.9% del total. Se rescató solo el 29.5% de las vacías — **a propósito**. Esta columna mide el **modo de entrega** (lineal/programado vs on-demand), no el tipo de contenido, y el valor declarado es `1` en el 100% de las filas que lo traen (incluidas 66,882 filas de películas según IMDb): propagarlo no agrega información, e inferir `0` porque IMDb dice "movie" confunde contenido con entrega. Por eso aquí `intra_titulo` está **apagado** y solo corren fuentes defendibles:

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 28.1% | El `1` declarado. Intacto. |
| derivado_tipo (señales del vendedor) | +0.5% | Lo único que el vendedor declara sobre la *entrega*: `contentSeries = "VOD"` → `0`; `contentSeries = "... Livestream"` → `1`. |
| app_semantica | +20.6% | Veredicto por app validado a mano en `cache-enriquecimiento/semantica_apps.csv` (2 bundles activos). Solo las inequívocamente lineales rellenan `1`: "Live TV" de TCL y Coolita Channel — las dos crecieron en v16 (Coolita casi duplicó filas), de ahí el punto extra vs la corrida anterior (19.7%). Las mixtas (MovieArk, TCL Channel, ViX, Tubi, Roku…) no rellenan nada. |
| sin_dato | 50.7% | Honestamente vacío: en una app mixta, ni el título ni la app determinan la entrega. Distinguirlo requiere el EPG/feed del vendedor (OTTera/TCL). |

## contentLength — 12.5% → 49.7% del total

Vacías al inicio: 87.5% del total. Se rescató el 42.5% de las vacías. Contexto clave: los valores son **códigos 1–8** (pendiente confirmar con PubMatic qué rango es cada uno) que **no correlacionan de forma monótona con la duración real** (código 1 → 60 min de mediana IMDb, 3 → 12, 7 → 150, pero 4/5/6/8 → 60–94) — por eso esta columna no usa ninguna fuente externa: solo se copian códigos que el propio sistema ya emitió.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 12.5% | Los códigos declarados (Roku 4–6, ViX siempre 8…). El formato nuevo los trae un poco mejor poblados (16% vs 12%). |
| intra_titulo | +34.8% | "brooklyn love stories" = código `4` por 291 filas de 6 rutas (Equativ, METAX, OTTera, Select Plus…), `6`×10, `2`×6 → 95% → las vacías reciben `4`. La lógica: *sea lo que sea el código 4, este contenido ES un código 4* — lo dijeron seis vendedores independientes. |
| app_default | +2.4% | Vidaa manda `5` en sus filas con dato → sus vacías son `5` (6,770); iion→BrowseHere `4` (6,025); ViX `8` (2,790). Menos que en la corrida anterior (6.0%) porque MovieArk vía Select Plus ya no pasa el 95%. |
| sin_dato | 50.3% | Títulos que nunca traen código en ninguna ruta (catálogo OTTera/MovieArk). El candado también bloqueó ambigüedades reales ("the baddest bad boy": `1`×4, `5`×5 → 56% < 80% → no se rellena). |

Donde no se pudo hablar el idioma de los códigos, se habla el de los minutos: **`ext_runtime_min`** (duración real vía IMDb/Wikidata) viaja en columna aparte en el 42.7% del total de filas. El día que PubMatic confirme la tabla de códigos, `--length-desde-runtime --buckets "..."` convierte esos minutos a códigos.

## contentSeries — 6.8% → 15.2% del total

Vacías al inicio: 93.2% del total. Se rescató el 9.0% de las vacías — el techo es estructural: el catálogo es ~76% película según IMDb, y una película **no pertenece a ninguna serie**, así que la mayor parte del vacío es *correcta* y se deja en paz.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 6.8% | Con asterisco: parte es placeholder (`VOD`, `No Series`, `OTT Studios …`) que se respeta como llegó pero **no se propaga**. |
| intra_titulo | +1.9% | "breathe" trae `contentSeries = Breathe` en 44 filas de OTTera/TCL → se copia a las 839 que lo traían vacío. **Ojo — falso positivo detectado en esta corrida**: "abandoned" (película) recibió `FBI` porque 3 filas de Scripps/Seedtag corresponden al *episodio* "Abandoned" de la serie *FBI*; "continuum" recibió `WDBJ News` (18 filas de un noticiero). ~1,500 filas afectadas. Falta un candado de mínimo de filas y rutas para esta columna (ver reporte principal, §5); mientras tanto, filtrar por `contentSeries_origen = imdb` para análisis de series. |
| imdb | +6.6% | Si el match (confianza A/B) dice que el título ES `tvSeries`/`tvMiniSeries`, el nombre de la serie es el título canónico: "porque el amor manda" → `Porque el amor manda`. Ojo: IMDb a veces devuelve el canónico en inglés ("40 y 20" → `40 and 20`). |
| sin_dato | 84.8% | Mayormente películas (vacío correcto) + títulos sin match. TVMaze como fallback existe pero no se corrió en esta pasada (aportaría ~1–2 puntos en series). |

## contentGenre — 95.9% → 98.5% del total

Vacías al inicio: 4.1% del total (venía de 1.2%: el formato nuevo trae `Not Applicable` en una de cada cuatro de sus filas). Se rescató el 63% de las vacías. La columna es el **insumo** de los demás rellenos (el mapa género→IAB de category y el desempate de confianza B del match IMDb usan `genero_normalizado`), y la normalización ya absorbe la mayúscula del formato nuevo (`Drama` = `drama`).

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 95.9% | Lo declarado (ya normalizado aparte en `genero_normalizado`). |
| intra_titulo | +1.4% | Ahora sí aplica (antes +0.1%): las filas del formato nuevo sin género tienen hermanas del formato viejo con género. "the cube usa" recibe la etiqueta larga de Coocaa/AWG (`game show, reality competition, …`). |
| imdb | +1.1% | Géneros IMDb traducidos al vocabulario canónico (`Horror`→terror, `Biography`→documental). Va al final porque en títulos de una palabra el match puede ser dudoso. |
| app_default | +0.2% | Apps de juegos casuales (iion\|LG, Free Games by PlayWorks) mandan `game` el 100% de las veces. |
| sin_dato | 1.5% | Residuo, más los títulos bloqueados por ambigüedad de escritura ("blink and friends": `adventure,kids`×309, `adventure,kids,anime`×166, `Adventure`×87… → ningún literal domina, aunque todos digan lo mismo normalizados). Mejora pendiente: intra sobre `genero_normalizado`. |

---

## Resumen

| Columna | Antes (del total) | Después (del total) | % de las vacías rescatado | Corrida dominante |
|---|---:|---:|---:|---|
| contentLanguage | 66.9% | **95.9%** | 87.6% | intra_titulo (28.2) |
| contentCategory | 22.8% | **94.9%** | 93.4% | derivados de género/tipo (52.8) |
| contentRating | 72.9% | **85.4%** | 46.1% | intra_titulo (12.4) |
| contentLength | 12.5% | **49.7%** | 42.5% | intra_titulo (34.8) |
| contentIsLiveStream | 28.1% | **49.3%** | 29.5% | app_semantica validada (20.6) |
| contentSeries | 6.8% | **15.2%** | 9.0% | imdb tipo serie (6.6) |
| contentGenre | 95.9% | **98.5%** | ~63% | intra_titulo (1.4) |

Frente a la corrida sobre v10–v15, el "después" es prácticamente el mismo en todas las columnas (±1pp, salvo rating: 90.5% → 85.4%) aunque idioma y rating arrancaron 10 puntos más abajo: el relleno intra-dataset compensó casi por completo lo que el formato nuevo del reporte dejó vacío. Cada valor rellenado lleva su `<col>_origen` en el CSV de salida, así que cualquier análisis puede quedarse solo con los orígenes que le den confianza.
