# Reporte — Relleno de content objects: qué se hizo columna por columna

**Fuente:** `inventory-consolidado-v10-a-v15-enriquecido.csv` — 648,589 filas (métricas del corte v15).
**Generado con:** `scripts/enriquecer_externo.py` → `inventory-consolidado-v10-a-v15-relleno.csv` + `reporte-relleno-v15.json` (los porcentajes exactos de este reporte salen de ese JSON).

**Convención de porcentajes: todos los % de este reporte son % de filas** (nunca de requests). Cuando el % es sobre las 648,589 filas del consolidado se dice "**del total**"; cuando es sobre las filas que venían vacías en esa columna se dice "**de las vacías**". Una celda cuenta como vacía si no trae nada o trae un centinela/basura (`Not Available`, `Unknown`, `[-7]`, hash MD5 de cadena vacía, macros `{{...}}`).

---

## Cómo funciona el relleno (lo común a todas las columnas)

Cada fila del consolidado no es un programa: es una **combinación** de 14 dimensiones (país × publisher × app × género × …). El mismo contenido llega por muchas rutas de venta a la vez y **cada ruta manda la metadata como quiere**: el título "ideas en 5 minutos" trae `contentCategory=[IAB1-6]` cuando viaja por Vidaa y `[-7]` cuando viaja por OTTera/TCL. El "vacío" casi nunca significa que nadie sepa el dato — significa que *esa ruta* lo descarta. Sobre esa redundancia se montan las corridas.

El script hace dos pasadas. La **pasada 1** aprende del propio dataset: normaliza el título de cada fila a una clave (`hatchback: trailer` → `hatchback`; ~14,100 claves distintas), y arma dos memorias: qué valores trae cada título cuando sí vienen (`conocido`) y qué manda cada app cuando manda (`por_app`). Las fuentes externas se consultan **una vez por título**, no por fila, y quedan en caché. La **pasada 2** rellena fila por fila probando fuentes en un orden fijo — la primera que da valor gana — y anota de dónde salió cada valor en `<col>_origen`:

| Corrida | Qué hace | Candado |
|---|---|---|
| `original` | La fila ya traía el dato. Nunca se toca. | — |
| `intra_titulo` | Copia el dato de otra fila **del mismo título** (misma película, distinta ruta). | El valor debe dominar ≥ 80% de las filas con dato de ese título; si no, no se rellena. |
| `app_default` | Copia el valor constante **de la misma app** (mismo vendedor, distinto título). | La app debe mandar ese valor ≥ 95% de las veces, con ≥ 200 filas de evidencia. |
| `imdb` / `wikidata` / `tvmaze` | Fuentes externas, vía el título normalizado. | Solo matches IMDb de confianza A (candidato único + género compatible, ~90% precisión) o B (desempatado por género, ~75%). |
| `derivado_*` | Traduce **otra columna de la misma fila** (género → categoría IAB; tipo IMDb → categoría/serie). | Según columna, ver abajo. |
| `app_semantica` | Solo livestream: veredicto por app validado a mano (`semantica_apps.csv`). | Solo filas con `aplicar=si` en el CSV. |

La diferencia entre las dos primeras, en una frase: `intra_titulo` responde "¿qué es *este contenido*?" y `app_default` responde "¿qué manda *este vendedor*?". La primera es más precisa y por eso corre antes.

---

## contentCategory — 23.0% → 95.2% del total

Vacías al inicio: 77.0% del total. Se rescató el 93.8% de las vacías.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 23.0% | Lo que ya venía ([IAB…] de Roku, Vidaa, LG…). |
| intra_titulo | +12.0% | El mismo título trae categoría en otra ruta: "ideas en 5 minutos" = `[IAB1-6]` por Vidaa/Equativ/Stingray → se copia a las filas de OTTera/TCL que traían `[-7]`. |
| app_default | +8.1% | Apps monotemáticas: OTTera→MovieArk manda `[IAB1]` el 99.2% de las veces que manda; Vidaa `[IAB12]` el 100%; PML `[sports]` el 97%. Sus vacías reciben ese valor. |
| derivado_genero | +25.7% | La fila vacía en categoría casi siempre está **llena en contentGenre** (99%). Mapa género→IAB aprendido de las ~149k filas que traen ambas columnas: deportes→`[IAB17]`, noticias→`[IAB12]`, música→`[IAB1-6]`, infantil/animación/telenovela/reality→`[IAB1-7]`. |
| derivado_tipo | +26.4% | Para géneros que no definen categoría (un *drama* puede ser película o serie), desempata el tipo del match IMDb: `movie`→`[IAB1-5]`, `tvSeries`→`[IAB1-7]`. |
| sin_dato | 4.8% | Sin título buscable, sin género y de apps inconsistentes. |

## contentLanguage — 77.2% → 97.4% del total

Vacías al inicio: 22.8% del total. Se rescató el 88.4% de las vacías. Es el caso más puro de "el dataset se rellena a sí mismo": el vacío era un artefacto de un solo SSP (iion), que despoja el campo que las demás rutas sí mandan.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 77.2% | Lo declarado. |
| intra_titulo | +19.6% | "cbn rj" trae `es` por 8 rutas (OTTera, TCL, Equativ, NubaTV…) y `Not Applicable` por iion → las de iion reciben `es`. Repetido ~131k veces. |
| app_default | +0.3% | Solo apps monolingües calificaron: ViX (`es` ≥ 97%), iion\|LG (`en` 100%). Las rutas grandes de iion mandan mezcla `en`/`es` → no pasan el 95%. |
| sin_dato | 2.6% | Sobre todo títulos bilingües bloqueados por el candado: "memorias adolescentes" trae `es` 3 veces y `en` 1 (75% < 80%) → no se adivina. La mezcla es información (pistas de audio), no ruido. |

## contentIsLiveStream — 28.7% → 48.9% del total

Vacías al inicio: 71.3% del total. Se rescató solo el 28.3% de las vacías — **a propósito**. Esta columna mide el **modo de entrega** (lineal/programado vs on-demand), no el tipo de contenido, y el valor declarado es `1` en el 100% de las filas que lo traen (incluido VOD evidente): propagarlo no agrega información, e inferir `0` porque IMDb dice "movie" confunde contenido con entrega (una película vieja en un canal lineal FAST va en horario → `livestream=1`). Por eso aquí `intra_titulo` está **apagado** y solo corren fuentes defendibles:

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 28.7% | El `1` declarado. Intacto. |
| derivado_tipo (señales del vendedor) | +0.5% | Lo único que el vendedor declara sobre la *entrega*: `contentSeries = "VOD"` → `0` (3,171 filas); `contentSeries = "... Livestream"` → `1` (62 filas). |
| app_semantica | +19.7% | Veredicto por app validado a mano en `cache-enriquecimiento/semantica_apps.csv` (evidencia: la ficha pública de cada app, legible desde cualquier país). Solo las inequívocamente lineales rellenan `1`: "Live TV" de TCL ("300+ FAST channels", sin VOD) y Coolita ("auto-play like traditional TV"). Las mixtas (MovieArk, TCL Channel, ViX, Tubi, Roku…) no rellenan nada. |
| sin_dato | 51.1% | Honestamente vacío: en una app mixta, ni el título ni la app determinan la entrega. Distinguirlo requiere el EPG/feed del vendedor (OTTera/TCL), no metadata de contenido. |

## contentRating — 83.9% → 90.5% del total

Vacías al inicio: 16.1% del total. Se rescató el 41.0% de las vacías. Contexto: cada vendedor manda su propio sistema de clasificación (`tv-14` US TV, `r` MPAA, `b`/`b15` RTC mexicana, `16`/`16+` numéricos).

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 83.9% | La columna mejor poblada del grupo. |
| intra_titulo | +6.4% | "los hermanos fierro" trae `tv-14` por 6 rutas y `Not Applicable` por EXTE → EXTE recibe `tv-14`. Lo más escrito: `tv-ma`, `tv-14`, `tv-pg`, `r`. |
| app_default | +0.2% | Casi nada califica: solo apps rígidas (iion\|LG `tv-g` 100%, WhaleLive `dv-g`). |
| wikidata | +0.04% | P3834 existe pero solo ~2% de los títulos la tienen (y en escala RTC). Confirmó que no hay fuente abierta buena para rating; el camino real es TMDB (clasificación **por país**, requiere key). |
| sin_dato | 9.5% | El candado bloqueó mucho: rating tiene 61% de ambigüedad entre títulos rellenables, casi toda por *sistemas distintos* ("so i married the anti fan": `16`×4, `b`×2, `16+`×1 → dominante 57% < 80% → no se rellena). Mejora pendiente: hacer el intra sobre `rating_franja` (la banda normalizada) en vez del código crudo. |


## contentLength — 11.7% → 50.1% del total

Vacías al inicio: 88.3% del total. Se rescató el 43.5% de las vacías. Contexto clave: los valores son **códigos 1–8** (pendiente confirmar con PubMatic qué rango es cada uno) que **no correlacionan con la duración real** — por eso esta columna no usa ninguna fuente externa: solo se copian códigos que el propio sistema ya emitió.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 11.7% | Los códigos declarados (Roku 4–6, ViX siempre 8…). |
| intra_titulo | +32.4% | "me apodan calibre 45" = código `6` por 6 rutas, `Not Applicable` por 4 → las 4 reciben `6`. La lógica: *sea lo que sea el código 6, este contenido ES un código 6* — lo dijeron seis vendedores independientes. |
| app_default | +6.0% | ViX manda `8` el 100% de sus filas con dato → sus vacías son `8`; Select Plus→MovieArk `4` (98.4%). |
| sin_dato | 49.9% | Títulos que nunca traen código en ninguna ruta (catálogo OTTera/MovieArk). El candado también bloqueó ambigüedades reales (el pseudo-título "entertainment": `{4:7, 5:2, 6:1}` → 70% < 80% → no se rellena). |

Donde no se pudo hablar el idioma de los códigos, se habla el de los minutos: **`ext_runtime_min`** (duración real vía IMDb/TVMaze/Wikidata) viaja en columna aparte en el 41.5% del total de filas. El día que PubMatic confirme la tabla de códigos, `--length-desde-runtime --buckets "..."` convierte esos minutos a códigos y la columna saltaría a ~75% en una corrida.

## contentSeries — 6.1% → 14.6% del total

Vacías al inicio: 93.9% del total. Se rescató el 9.1% de las vacías — el techo es estructural: el catálogo es ~67% película, y una película **no pertenece a ninguna serie**, así que la mayor parte del vacío es *correcta* y se deja en paz.

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 6.1% | Con asterisco: parte es placeholder (`VOD`, `No Series`, `OTT Studios …`) que se respeta como llegó pero **no se propaga**. |
| intra_titulo | +1.9% | El título "mxf01" (código de feed de ViX) trae `contentSeries = FIFA Club World Cup` en una sola ruta → se copia a las otras 8. |
| imdb | +6.6% | Si el match (confianza A/B) dice que el título ES `tvSeries`/`tvMiniSeries`, el nombre de la serie es el título canónico: "halo 4 forward unto dawn" → `Halo 4: Forward Unto Dawn`; "porque el amor manda" → `Porque el amor manda`. Ojo: IMDb a veces devuelve el canónico en inglés ("40 y 20" → `40 and 20`). |
| sin_dato | 85.4% | Mayormente películas (vacío correcto) + títulos sin match. TVMaze como fallback existe pero no se corrió en esta pasada (aportaría ~1–2 puntos en series). |

## contentGenre — 98.8% → 99.1% del total

Vacías al inicio: 1.2% del total. Se rescató ~1/3 de las vacías. Aquí el trabajo fue de bordes: la columna ya estaba llena y es el **insumo** de los demás rellenos (el mapa género→IAB de category y el desempate de confianza B del match IMDb usan `genero_normalizado`).

| Corrida | % del total | Qué se hizo |
|---|---:|---|
| original | 98.8% | Lo declarado (ya normalizado aparte en `genero_normalizado`). |
| app_default | +0.2% | El rincón principal: apps de juegos casuales (iion\|LG, Free Games by PlayWorks) mandan `game` el 100% de las veces → sus vacías reciben `game`. |
| intra_titulo | +0.1% | Casi no aplica: un título sin género en una fila suele estar sin género en todas (el género viaja pegado a la app, no al título). |
| imdb | +0.1% | Géneros IMDb traducidos al vocabulario canónico (`Horror`→terror, `Biography`→documental). Va al final porque en títulos de una palabra el match puede ser dudoso. |
| sin_dato | 0.9% | Residuo. |

---

## Resumen

| Columna | Antes (del total) | Después (del total) | % de las vacías rescatado | Corrida dominante |
|---|---:|---:|---:|---|
| contentCategory | 23.0% | **95.2%** | 93.8% | derivados de género/tipo (52.1) |
| contentLanguage | 77.2% | **97.4%** | 88.4% | intra_titulo (19.6) |
| contentRating | 83.9% | **90.5%** | 41.0% | intra_titulo (6.4) |
| contentLength | 11.7% | **50.1%** | 43.5% | intra_titulo (32.4) |
| contentIsLiveStream | 28.7% | **48.9%** | 28.3% | app_semantica validada (19.7) |
| contentSeries | 6.1% | **14.6%** | 9.1% | imdb tipo serie (6.6) |
| contentGenre | 98.8% | **99.1%** | ~33% | app_default (0.2) |

Cada valor rellenado lleva su `<col>_origen` en el CSV de salida, así que cualquier análisis puede quedarse solo con los orígenes que le den confianza.
