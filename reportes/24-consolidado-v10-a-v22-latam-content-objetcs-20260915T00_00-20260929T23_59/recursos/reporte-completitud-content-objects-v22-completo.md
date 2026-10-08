# Qué se puede completar de cada content object: métodos y fuentes (consolidado v10 a v22)

**Fuente:** `inventory-consolidado-v10-a-v22.csv` — 1,344,629 filas únicas, 622,384,767,599 requests (métricas del corte v22). **Relleno:** `inventory-consolidado-v10-a-v22-relleno.csv` (no versionado), generado con `scripts/enriquecer_externo.py --wikidata`, corrida del 2026-10-06 16:38 → `recursos/reporte-relleno-v22.json`. Títulos distintos: 18,246; con match en IMDb: 8,753; consultados por primera vez en esta corrida: 0.
**Validaciones:** `scripts/validar_categorias.py` y `scripts/validar_genero_series.py` sobre el consolidado y sobre el relleno (`recursos/validacion-*.json`, con muestras CSV para revisión manual en la misma carpeta). Tablas generadas con `scripts/generar_reporte_completitud.py`.

## Cómo leer este reporte

- Cada fila del consolidado es una **combinación** de 14 dimensiones (país × publisher × app × género × …), no un programa. El mismo contenido llega por varias rutas de venta y cada ruta manda la metadata que quiere: lo que una ruta declara describe a esa ruta, así que el relleno solo usa lo que describe al contenido (el match IMDb del título y el género de la propia fila).
- Una celda cuenta como **llena** solo si trae dato útil: no cuentan los centinelas (`Not Available`, `Unknown`, `[-7]`, el MD5 de cadena vacía, macros sin reemplazar).
- Los % son sobre el total de filas del consolidado (y, cuando se indica, sobre el total de requests). "Hoy" es como llega; "tras el relleno" es después de correr el pipeline con los candados por defecto.
- **Se puede completar** tiene dos lecturas: (1) lo que el pipeline **ya llena** automáticamente (tabla de orígenes por columna) y (2) lo que la validación contra fuentes abiertas dice que **se podría afinar o corregir** además (nivel de detalle alcanzable, géneros adicionales, nombre de serie proponible). Lo segundo no se escribe al CSV: son propuestas fila a fila en los `validacion-*.json` y en los CSV `*-filas.csv` de la raíz.

## Fuentes

| Fuente | Qué aporta | Cómo se usa | Licencia / límite |
|---|---|---|---|
| **Semántica de apps curada a mano** (`cache-enriquecimiento/semantica_apps.csv`) | Modo de entrega (lineal / VOD) por app | Ficha de tienda y evidencia del dataset, revisada a mano; solo las filas con `aplicar=si` rellenan | 16 apps revisadas; solo 2 (Live TV de TCL, Coolita Channel) son lineales puras y se aplican |
| **IMDb Non-Commercial Datasets** (`title.basics`, `title.akas` es/pt/en, `title.ratings`, `title.episode`) | Tipo (película / serie / corto…), géneros, título canónico, año, duración | Match offline por título normalizado y alias en español/portugués/inglés; confianza A–D (A ≈ 90 %+, B ≈ 75 %; se usa hasta B) | Solo uso no comercial; ~750 MB descargados a `cache-enriquecimiento/imdb/` |
| **Wikidata** (SPARQL, vía el id IMDb `P345`) | Duración (`P2047`), géneros (`P136`, p. ej. telenovela), clasificación (`P3834`, rara). Trae también el idioma original (`P364`), que **no se usa** | Solo para títulos con match IMDb; resultado cacheado por título | CC0, sin API key |
| **TVMaze** (opcional, `--tvmaze`) | Géneros y duración de series | Series sin match IMDb | CC BY-SA, ~20 req/10 s. **No se usó en esta corrida** |
| **Taxonomías IAB Tech Lab** (Content Taxonomy 1.0, 2.2, 3.0) | Si un código declarado existe y qué significa; códigos propuestos | Descargadas a `cache-enriquecimiento/iab/`; cada código se traduce a (vertical, forma, género) para comparar entre taxonomías | Abiertas (GitHub de IAB Tech Lab) |

*Cache incremental: `cache-enriquecimiento/titulos.json` guarda el resultado de cada título; en cada tanda solo se consultan los títulos nuevos.*

## Métodos (en orden: el primero que llena gana, y queda anotado en `<columna>_origen`)

| Método (`origen`) | Qué hace | Candado | Columnas donde aplica |
|---|---|---|---|
| `imdb` | Match del título contra IMDb: tipo, géneros, título canónico | Confianza A o B | series (tvSeries → título canónico), genre |
| `wikidata` | Duración, géneros y clasificación del ítem ligado al id IMDb | Solo títulos con match IMDb | rating (y genre vía telenovela) |
| `derivado_tipo` | El tipo IMDb decide la categoría y tiene prioridad sobre el género: movie → `[IAB1-5]`, tvSeries → `[IAB1-7]` | Match IMDb A/B | category |
| `derivado_genero` | Traduce el género de la misma fila a categoría IAB (deportes → `[IAB17]`, noticias → `[IAB12]`…) | Solo si no hay match IMDb A/B, o si los géneros IMDb confirman la vertical (Sport / News / Music) | category |
| `app_semantica` | Modo de entrega según la app: lineal pura → 1, VOD pura → 0 | Solo apps con `aplicar=si` en la tabla curada | livestream |
| `corregido_imdb` | **Corrige** un valor que el vendedor sí mandó cuando contradice a IMDb/Wikidata (vertical, película/serie o género). La columna original no se toca; el motivo queda en `<columna>_correccion` | Match IMDb de confianza A; el reemplazo no puede contradecir la evidencia | category, genre |
| `corregido_genero` | **Corrige** una categoría declarada como noticias o deportes cuando el género de la misma fila es ficción (el `[IAB12]` de Vidaa en una telenovela) | Solo sin match A y solo esas dos verticales | category |
| *(retirados el 2026-09-17)* | `app_default` (copiar el valor constante de la app) en todas las columnas: describe al vendedor, no al contenido. Todo relleno de contentLanguage. El tipo IMDb como señal de livestream | | |
| *(retirado el 2026-10-06)* | `intra_titulo` (copiar el valor que otra fila del mismo título ya trae) en todas las columnas: propagaba los valores por defecto de los vendedores (el `[IAB12]` que Vidaa manda en casi todas sus filas llegaba a las telenovelas de ViX) | | |

## Resumen: cuánto viene lleno hoy y cuánto queda tras el relleno

| Columna | Hoy (% filas) | Hoy (% requests) | Tras el relleno (% filas) | Ganancia | Sigue vacío | Método que más aporta |
|---|---:|---:|---:|---:|---:|---|
| contentGenre | 90.8% | 85.6% | 93.4% | +2.6 pp | 6.6% | IMDb (`imdb`) |
| contentTitle | 93.0% | 72.7% | 93.0% | — | 7.0% | No se rellena (ver abajo) |
| contentRating | 75.2% | 78.3% | 75.3% | +0.2 pp | 24.7% | Wikidata (`wikidata`) |
| contentLanguage | 67.0% | 67.8% | 67.0% | — | 33.0% | No se rellena (ver abajo) |
| contentIsLiveStream | 29.5% | 38.6% | 48.7% | +19.2 pp | 51.3% | Semántica de la app (curada a mano) (`app_semantica`) |
| contentCategory | 21.9% | 28.6% | 91.8% | +69.9 pp | 8.2% | Derivado del tipo IMDb (película / serie) (`derivado_tipo`) |
| contentLength | 12.6% | 21.0% | 12.6% | +0.0 pp | 87.4% | — (`—`) |
| contentSeries | 6.8% | 6.2% | 13.8% | +7.2 pp | 86.2% | IMDb (`imdb`) |

*contentIsTitlePresent y Publisher vienen al 100 % y no entran. "Ganancia" son puntos porcentuales de filas del consolidado.*

## contentCategory

**Hoy:** 21.9% de las filas y 28.6% de los requests traen dato útil. Top 3 referencias: *[-7] 78.1%*, [IAB1] 5.2%, [IAB1-22] 3.0%.

**Tras el relleno:** 91.8% de las filas (de 21.9%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 20.0% |
| Derivado del género (`derivado_genero`) | 29.9% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 40.1% |
| Venía del vendedor y se corrigió con IMDb (match A) (`corregido_imdb`) | 0.7% |
| Venía del vendedor y se corrigió con el género de la fila (`corregido_genero`) | 1.1% |
| Sigue vacío (`sin_dato`) | 8.2% |

**Método y fuentes:** dos escalones. `derivado_tipo`: si el título tiene match IMDb (A/B), el tipo IMDb decide entre película (`[IAB1-5]`) y serie (`[IAB1-7]`), y tiene prioridad sobre el género (la vertical del género solo se conserva si los géneros IMDb la confirman: Sport, News, Music). `derivado_genero`: sin match, se traduce el contentGenre de la misma fila con el mapa IAB 1.0. La validación va un paso más allá y propone, con la taxonomía 2.2, la categoría más fina que la evidencia permite (forma + género).

**Qué más se puede afinar (validación del consolidado contra IMDb / Wikidata / taxonomías IAB):**

| Mejora posible | % filas | % requests |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 70.5% | 59.5% |
| Se puede afinar (estaba llena, pero genérica) (`sube`) | 11.2% | 9.7% |
| Se puede corregir (estaba incorrecta) (`corrige`) | 2.7% | 3.3% |
| Se queda igual (ya está bien) (`mantiene`) | 7.9% | 15.6% |
| Sin propuesta (vacía y sin evidencia) (`sin_propuesta`) | 7.7% | 11.9% |

| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |
|---|---:|---:|
| Nivel 0 · nada | 78.5% | 7.7% |
| Nivel 1 · solo la vertical | 13.5% | 13.7% |
| Nivel 2 · vertical + película/TV (o deporte) | 6.9% | 33.9% |
| Nivel 3 · vertical + película/TV + género | 1.2% | 44.8% |

*El nivel mide cuántos atributos conoce la categoría: vertical (entretenimiento, deportes…), forma (película / TV) y género. La propuesta usa Content Taxonomy 2.2 (p. ej. `Movies > Drama Movies`) porque es la que permite los tres.*

Evidencia disponible por fila: externa 48.5%, interna 34.1%, ninguna 16.1%, serie 1.3% (*externa* = match IMDb; *interna* = el género de la misma fila; *serie* = trae nombre de serie; *ninguna* = sin nada que cruzar).

Categorías más propuestas: `Movies > Drama Movies | Television > Drama TV` 5.2%; `Movies > Drama Movies` 5.0%; `Movies > Documentary Movies | Television > Factual TV` 3.9%; `Movies > Horror Movies` 3.8%; `Movies > Crime and Mystery Movies` 3.3%.

**Confiabilidad de lo que trae y de lo que se llena (filas con categoría, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide con la evidencia (`coincide`) | 19.5% | 62.6% |
| Compatible (genérica, no contradice) (`compatible`) | 50.1% | 19.4% |
| Contradice la evidencia (`contradice`) | 12.5% | 9.5% |
| No se pudo evaluar (`no_evaluable`) | 18.0% | 8.4% |

**Límites:** el consolidado mezcla tres taxonomías (1.0, 2.2, 3.0) y texto libre (`[sports]`, `[Live]`); lo declarado es en su mayoría genérico (nivel 1, solo la vertical). Los valores por defecto que declaran algunas apps (`[IAB12]` de Vidaa, `[IAB1]` de OTTera) no describen al contenido (Vidaa manda `[IAB12]` en telenovelas y películas); por eso ya no se copian entre rutas (`intra_titulo`, retirado el 2026-10-06). Un match IMDb de confianza B acierta ~75 %, así que parte de las "contradicciones" son matches equivocados; se separan con `genero_vs_imdb` en el CSV fila a fila.

## contentGenre

**Hoy:** 90.8% de las filas y 85.6% de los requests traen dato útil. Top 3 referencias: Drama 11.0%, *N/A 9.2%*, drama 4.8%.

**Tras el relleno:** 93.4% de las filas (de 90.8%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 89.8% |
| IMDb (`imdb`) | 2.6% |
| Venía del vendedor y se corrigió con IMDb (match A) (`corregido_imdb`) | 1.0% |
| Sigue vacío (`sin_dato`) | 6.6% |

**Método y fuentes:** los géneros del match IMDb (`title.basics`, hasta tres) traducidos al vocabulario canónico del proyecto (`norm_genre`), y los géneros de Wikidata (`P136`) para lo que IMDb no expresa (telenovela, holiday). La validación compara cada género declarado con IMDb/Wikidata por *conceptos* (thriller/misterio/crimen → crimen-misterio, anime → animación) y propone géneros adicionales o más precisos.

**Qué más se puede afinar (validación del consolidado):**

| Mejora posible | % filas | % requests |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 2.7% | 1.6% |
| Se pueden agregar géneros o uno más preciso (`sube`) | 23.6% | 23.7% |
| Se puede corregir (contradecía) (`corrige`) | 1.6% | 2.1% |
| Se corrige en parte (acertaba en parte) (`corrige_parcial`) | 2.6% | 0.7% |
| Se queda igual (ya está bien) (`mantiene`) | 63.1% | 59.1% |
| Sin propuesta (sin evidencia) (`sin_propuesta`) | 6.5% | 12.8% |

| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |
|---|---:|---:|
| Nivel 0 · vacío | 9.2% | 6.5% |
| Nivel 1 · sin género comparable (solo "entertainment", "other"…) | 14.8% | 12.9% |
| Nivel 2 · un género | 59.4% | 41.7% |
| Nivel 3 · dos o más géneros | 16.7% | 38.9% |

*Wikidata (`P136`) permite etiquetar como telenovela 1.6% de las filas (3.9% de los requests) que hoy solo dicen drama/romance.*

Combinaciones más propuestas: `drama,romance` 1.0%; `drama` 0.9%; `drama,comedia` 0.8%; `terror,thriller` 0.7%; `drama,thriller` 0.7%.

**Confiabilidad (filas con género comparable, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 41.2% | 43.9% |
| Parecido (género vecino) (`afin`) | 2.6% | 2.6% |
| Acierta en parte (`parcial`) | 2.8% | 2.7% |
| Contradice (`contradice`) | 1.7% | 0.7% |
| No se pudo evaluar (`no_evaluable`) | 51.6% | 50.1% |

**Límites:** es la columna que mejor viene (>90 %), así que el margen es afinar, no llenar. El vocabulario del vendedor es libre (`Drama` y `drama` son valores distintos en la fuente; `entertainment`, `other`, `movies` no son géneros comparables) y géneros que IMDb no maneja (lifestyle, viajes, religión, videojuegos) no se pueden juzgar. Solo la mitad de las filas tiene match externo; el resto queda como "no evaluable".

## contentSeries

**Hoy:** 6.8% de las filas y 6.2% de los requests traen dato útil. Top 3 referencias: *N/A 92.5%*, *md5-vacío 0.7%*, VOD 0.6%.

**Tras el relleno:** 13.8% de las filas (de 6.6%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 6.6% |
| IMDb (`imdb`) | 7.2% |
| Sigue vacío (`sin_dato`) | 86.2% |

**Método y fuentes:** el pipeline llena solo lo seguro: `imdb` cuando el match (A/B) dice tvSeries o tvMiniSeries, con el título canónico de IMDb. La validación identifica además qué filas **son** serie sin decirlo (IMDb, el título con "season N" / S01E03 / "ep N", o las otras rutas) y propone un nombre: el título sin sufijos de temporada/episodio, el que traen las otras rutas, o el canónico IMDb.

**Qué es cada fila según la evidencia (consolidado):**

| Qué es | % filas |
|---|---:|
| Serie | 15.5% |
| Película | 33.3% |
| Ambiguo (corto, tv movie, video, especial) | 7.5% |
| Desconocido (sin evidencia) | 43.7% |

**Qué se puede hacer con cada fila:**

| Situación | % filas | % requests |
|---|---:|---:|
| Serie con nombre (`ya_nombrada`) | 5.2% | 4.7% |
| Serie sin nombre, con nombre proponible (`serie_sin_nombre_recuperable`) | 10.4% | 10.4% |
| Película: el vacío es correcto (`pelicula_vacio_correcto`) | 33.2% | 24.2% |
| Película con serie declarada (contradicción) (`pelicula_con_serie_declarada`) | 0.1% | 0.0% |
| Contradicha (`contradicha`) | 0.0% | 0.0% |
| Con nombre, sin evidencia para juzgar (`nombrada_sin_evidencia`) | 0.0% | 0.0% |
| Sin evidencia (`sin_evidencia`) | 51.1% | 60.7% |

**Temporada / episodio que trae el título** (candidatos a `content.season` / `content.episode`):

| El título trae | % filas |
|---|---:|
| Temporada y episodio (`temporada+episodio`) | 0.1% |
| Solo temporada (`solo_temporada`) | 3.8% |
| Solo episodio (`solo_episodio`) | 0.8% |
| Nada (`nada`) | 95.2% |

Nombres de serie más propuestos (`[titulo]` = del propio título sin sufijos, `[imdb]` = título canónico): `chicken stew [titulo]` 0.4%; `forest frenzy of boonie bears [titulo]` 0.2%; `something scary [titulo]` 0.2%; `cain [imdb]` 0.1%; `haus of horror [imdb]` 0.1%.

**Confiabilidad de las series declaradas (filas con nombre de serie real, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 2.4% | 58.4% |
| Es serie, pero con otro nombre (compatible) (`otro_nombre`) | 4.7% | 2.3% |
| IMDb dice que es película (`contradice`) | 2.7% | 1.3% |
| No se pudo evaluar (`no_evaluable`) | 90.2% | 38.0% |

**Límites:** la mayor parte del vacío es correcta: las películas no pertenecen a ninguna serie. Casi la mitad de las filas no tiene evidencia (títulos sin match, placeholders como `roku` / `epg`). Roku manda un hash MD5 en vez del nombre y algunos vendedores mandan `VOD` o macros sin reemplazar; todo eso cuenta como vacío.

## contentLength

**Hoy:** 12.6% de las filas y 21.0% de los requests traen dato útil. Top 3 referencias: *N/A 87.4%*, 5 3.5%, 6 3.4%.

**Tras el relleno:** 12.6% de las filas (de 12.6%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 12.6% |
| Sigue vacío (`sin_dato`) | 87.4% |

**Método y fuentes:** no se rellena. IMDb (`runtimeMinutes`) y Wikidata (`P2047`) traen la duración en minutos de la mayoría de los títulos con match, pero esa duración solo se escribe con `--length-desde-runtime`, apagado por defecto.

**Límites:** contentLength no es una duración: es un **código 1–8** (rangos de duración; el mapa por defecto del pipeline es 1: ≤ 1 min, 2: ≤ 5, 3: ≤ 15, 4: ≤ 30, 5: ≤ 60, 6: ≤ 120, 7: ≤ 180, 8: más). Mientras PubMatic no confirme los cortes de cada código, convertir minutos a código es una suposición y por eso no se aplica. Con esa confirmación, el runtime externo cubriría buena parte de lo que sigue vacío (títulos con match IMDb).

## contentLanguage

**Hoy:** 67.0% de las filas y 67.8% de los requests traen dato útil. Top 3 referencias: *N/A 32.9%*, en 22.3%, English 18.6%.

**No se rellena.** No hay forma de asumir el idioma en el que se emite un programa en ninguna circunstancia: el mismo título puede ir con pistas de audio distintas por ruta, y el idioma original de la obra (IMDb / Wikidata) no dice en cuál se sirvió. Solo vale lo que declara el vendedor.

## contentIsLiveStream

**Hoy:** 29.5% de las filas y 38.6% de los requests traen dato útil. Top 3 referencias: *Unknown 36.8%*, *N/A 33.7%*, 1 29.5%.

**Tras el relleno:** 48.7% de las filas (de 29.5%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 29.5% |
| Semántica de la app (curada a mano) (`app_semantica`) | 19.2% |
| Sigue vacío (`sin_dato`) | 51.3% |

**Método y fuentes:** mide el **modo de entrega** (canal lineal vs on demand), no el contenido, así que no se propaga por título (la misma película puede ir en un canal lineal y en VOD) ni por app (MovieArk marca 1 todo su catálogo). La única señal que se usa es la semántica de la app validada a mano (`semantica_apps.csv`: ficha de tienda + evidencia del dataset). El tipo IMDb (película → 0) se retiró: una película en un canal lineal es livestream = 1.

**Límites:** todo lo declarado por los vendedores es `1`; el `0` nunca llega. De 16 apps revisadas solo dos son lineales puras; las 13 mixtas (MovieArk, TCL CHANNEL…) no se pueden resolver sin saber por qué ruta se sirvió cada request. La mitad del consolidado seguirá vacía hasta que el vendedor lo mande.

## contentRating

**Hoy:** 75.2% de las filas y 78.3% de los requests traen dato útil. Top 3 referencias: *N/A 24.8%*, Adults 10.7%, Teen Plus 9.8%.

**Tras el relleno:** 75.3% de las filas (de 75.1%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 75.1% |
| Wikidata (`wikidata`) | 0.1% |
| Sigue vacío (`sin_dato`) | 24.7% |

**Método y fuentes:** solo la clasificación de Wikidata (`P3834`), que casi nunca viene.

**Límites:** no hay fuente abierta de clasificaciones por edad con cobertura: los datasets públicos de IMDb no traen la Parental Guide y en Wikidata `P3834` es rara. Lo que queda vacío son títulos que ninguna ruta clasifica; solo el vendedor puede completarlo. El consolidado mezcla dos escalas (`tv-14` y `Teen Plus` para el mismo título); `rating_franja` de `normalizar_monetizar.py` las unifica en franjas de edad.

## contentTitle

**Hoy:** 93.0% de las filas y 72.7% de los requests traen algo. Top 3 referencias: *N/A 7.0%*, roku 0.2%, {{content_title}} 0.2%.

**Método y fuentes:** no se rellena. El título es la **llave** de todo lo demás: es lo que se normaliza (`titulo_clave`) y se busca en IMDb/Wikidata. Lo que sí se hace es medir cuánto de lo "lleno" es un título de verdad: se descuentan placeholders (`roku`, `epg`, `vod`), nombres de canal (`las estrellas`, `canal 5`), slugs técnicos (`*_trailer`), macros sin reemplazar (`{{content_title}}`), texto sin letras o de una o dos letras y encoding roto (en esta tanda, 1,161,941 filas, 86.4% del consolidado, pasan el filtro).

**Límites:** sin título no hay nada que cruzar afuera: una fila vacía en contentTitle solo la puede completar el vendedor. Y el vacío pesa más en tráfico que en catálogo (27.3% de los requests vs 7.0% de las filas): son pocas combinaciones con muchos requests.
