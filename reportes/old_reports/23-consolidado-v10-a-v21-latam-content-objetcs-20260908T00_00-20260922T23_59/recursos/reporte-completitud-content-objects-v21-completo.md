# Qué se puede completar de cada content object: métodos y fuentes (consolidado v10 a v21)

**Fuente:** `inventory-consolidado-v10-a-v21.csv` — 1,298,145 filas únicas, 593,279,479,040 requests (métricas del corte v21). **Relleno:** `inventory-consolidado-v10-a-v21-relleno.csv` (no versionado), generado con `scripts/enriquecer_externo.py --wikidata`, corrida del 2026-09-24 15:00 → `recursos/reporte-relleno-v21.json`. Títulos distintos: 17,345; con match en IMDb: 8,439; consultados por primera vez en esta corrida: 360.
**Validaciones:** `scripts/validar_categorias.py` y `scripts/validar_genero_series.py` sobre el consolidado y sobre el relleno (`recursos/validacion-*.json`, con muestras CSV para revisión manual en la misma carpeta). Tablas generadas con `scripts/generar_reporte_completitud.py`.

## Cómo leer este reporte

- Cada fila del consolidado es una **combinación** de 14 dimensiones (país × publisher × app × género × …), no un programa. El mismo contenido llega por varias rutas de venta y cada ruta manda la metadata que quiere: por eso la respuesta a un vacío muchas veces ya está escrita en otra fila del mismo título.
- Una celda cuenta como **llena** solo si trae dato útil: no cuentan los centinelas (`Not Available`, `Unknown`, `[-7]`, el MD5 de cadena vacía, macros sin reemplazar).
- Los % son sobre el total de filas del consolidado (y, cuando se indica, sobre el total de requests). "Hoy" es como llega; "tras el relleno" es después de correr el pipeline con los candados por defecto.
- **Se puede completar** tiene dos lecturas: (1) lo que el pipeline **ya llena** automáticamente (tabla de orígenes por columna) y (2) lo que la validación contra fuentes abiertas dice que **se podría afinar o corregir** además (nivel de detalle alcanzable, géneros adicionales, nombre de serie proponible). Lo segundo no se escribe al CSV: son propuestas fila a fila en los `validacion-*.json` y en los CSV `*-filas.csv` de la raíz.

## Fuentes

| Fuente | Qué aporta | Cómo se usa | Licencia / límite |
|---|---|---|---|
| **El propio consolidado** (otras filas del mismo título) | Categoría, serie, duración, rating, género | Se normaliza el título a `titulo_clave` (url-decode, mojibake, sin ": trailer", "season N", SxxEyy) y se agrupan las filas por título | Sin costo. Es la fuente más precisa (mismo contenido, otra ruta) y la que más aporta |
| **Semántica de apps curada a mano** (`cache-enriquecimiento/semantica_apps.csv`) | Modo de entrega (lineal / VOD) por app | Ficha de tienda y evidencia del dataset, revisada a mano; solo las filas con `aplicar=si` rellenan | 16 apps revisadas; solo 2 (Live TV de TCL, Coolita Channel) son lineales puras y se aplican |
| **IMDb Non-Commercial Datasets** (`title.basics`, `title.akas` es/pt/en, `title.ratings`, `title.episode`) | Tipo (película / serie / corto…), géneros, título canónico, año, duración | Match offline por título normalizado y alias en español/portugués/inglés; confianza A–D (A ≈ 90 %+, B ≈ 75 %; se usa hasta B) | Solo uso no comercial; ~750 MB descargados a `cache-enriquecimiento/imdb/` |
| **Wikidata** (SPARQL, vía el id IMDb `P345`) | Duración (`P2047`), géneros (`P136`, p. ej. telenovela), clasificación (`P3834`, rara). Trae también el idioma original (`P364`), que **no se usa** | Solo para títulos con match IMDb; resultado cacheado por título | CC0, sin API key |
| **TVMaze** (opcional, `--tvmaze`) | Géneros y duración de series | Series sin match IMDb | CC BY-SA, ~20 req/10 s. **No se usó en esta corrida** |
| **Taxonomías IAB Tech Lab** (Content Taxonomy 1.0, 2.2, 3.0) | Si un código declarado existe y qué significa; códigos propuestos | Descargadas a `cache-enriquecimiento/iab/`; cada código se traduce a (vertical, forma, género) para comparar entre taxonomías | Abiertas (GitHub de IAB Tech Lab) |

*Cache incremental: `cache-enriquecimiento/titulos.json` guarda el resultado de cada título; en cada tanda solo se consultan los títulos nuevos.*

## Métodos (en orden: el primero que llena gana, y queda anotado en `<columna>_origen`)

| Método (`origen`) | Qué hace | Candado | Columnas donde aplica |
|---|---|---|---|
| `intra_titulo` | Copia el valor que otra fila del **mismo título** ya trae (misma película, otra ruta de venta) | El valor debe dominar ≥ 80 % de las filas con dato de ese título; en contentSeries además ≥ 30 filas y ≥ 2 publishers | category, series, length, rating, genre |
| `imdb` | Match del título contra IMDb: tipo, géneros, título canónico | Confianza A o B | series (tvSeries → título canónico), genre |
| `wikidata` | Duración, géneros y clasificación del ítem ligado al id IMDb | Solo títulos con match IMDb | rating (y genre vía telenovela) |
| `derivado_genero` | Traduce el género de la misma fila a categoría IAB (mapa aprendido de las filas que traen ambas columnas: deportes → `[IAB17]`, noticias → `[IAB12]`…) | Solo géneros que definen vertical | category |
| `derivado_tipo` | Desempata con el tipo IMDb cuando el género no define categoría: movie → `[IAB1-5]`, tvSeries → `[IAB1-7]` | Match IMDb A/B | category |
| `app_semantica` | Modo de entrega según la app: lineal pura → 1, VOD pura → 0 | Solo apps con `aplicar=si` en la tabla curada | livestream |
| *(retirados el 2026-09-17)* | `app_default` (copiar el valor constante de la app) en todas las columnas: describe al vendedor, no al contenido. Todo relleno de contentLanguage. El tipo IMDb como señal de livestream | | |

## Resumen: cuánto viene lleno hoy y cuánto queda tras el relleno

| Columna | Hoy (% filas) | Hoy (% requests) | Tras el relleno (% filas) | Ganancia | Sigue vacío | Método que más aporta |
|---|---:|---:|---:|---:|---:|---|
| contentGenre | 91.0% | 85.8% | 96.9% | +5.9 pp | 3.1% | Copiado de otra ruta del mismo título (`intra_titulo`) |
| contentTitle | 93.2% | 71.6% | 93.2% | — | 6.8% | No se rellena (ver abajo) |
| contentRating | 74.9% | 78.1% | 82.1% | +7.2 pp | 17.9% | Copiado de otra ruta del mismo título (`intra_titulo`) |
| contentLanguage | 66.3% | 66.2% | 66.3% | — | 33.7% | No se rellena (ver abajo) |
| contentIsLiveStream | 29.3% | 39.9% | 48.7% | +19.4 pp | 51.3% | Semántica de la app (curada a mano) (`app_semantica`) |
| contentCategory | 21.5% | 28.7% | 93.0% | +71.5 pp | 7.0% | Derivado del tipo IMDb (película / serie) (`derivado_tipo`) |
| contentLength | 12.2% | 21.4% | 49.0% | +36.8 pp | 51.0% | Copiado de otra ruta del mismo título (`intra_titulo`) |
| contentSeries | 6.5% | 6.0% | 14.0% | +7.6 pp | 86.0% | IMDb (`imdb`) |

*contentIsTitlePresent y Publisher vienen al 100 % y no entran. "Ganancia" son puntos porcentuales de filas del consolidado.*

## contentCategory

**Hoy:** 21.5% de las filas y 28.7% de los requests traen dato útil. Top 3 referencias: *[-7] 78.5%*, [IAB1] 5.1%, [IAB1-22] 2.9%.

**Tras el relleno:** 93.0% de las filas (de 21.5%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 21.5% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 11.6% |
| Derivado del género (`derivado_genero`) | 26.0% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 33.9% |
| Sigue vacío (`sin_dato`) | 7.0% |

**Método y fuentes:** tres escalones. `intra_titulo` copia la categoría que otra ruta del mismo título ya manda (Vidaa o Equativ suelen mandarla; OTTera y TCL mandan `[-7]`). `derivado_genero` traduce el contentGenre de la misma fila con el mapa IAB 1.0 aprendido del propio dataset (~150k filas traen ambas columnas). `derivado_tipo` usa el tipo IMDb para separar película (`[IAB1-5]`) de serie (`[IAB1-7]`). La validación va un paso más allá y propone, con la taxonomía 2.2, la categoría más fina que la evidencia permite (forma + género).

**Qué más se puede afinar (validación del consolidado contra IMDb / Wikidata / taxonomías IAB):**

| Mejora posible | % filas | % requests |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 70.9% | 59.3% |
| Se puede afinar (estaba llena, pero genérica) (`sube`) | 11.1% | 9.6% |
| Se puede corregir (estaba incorrecta) (`corrige`) | 2.7% | 3.3% |
| Se queda igual (ya está bien) (`mantiene`) | 7.7% | 15.8% |
| Sin propuesta (vacía y sin evidencia) (`sin_propuesta`) | 7.6% | 12.0% |

| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |
|---|---:|---:|
| Nivel 0 · nada | 78.8% | 7.7% |
| Nivel 1 · solo la vertical | 13.3% | 13.6% |
| Nivel 2 · vertical + película/TV (o deporte) | 6.8% | 33.7% |
| Nivel 3 · vertical + película/TV + género | 1.1% | 45.0% |

*El nivel mide cuántos atributos conoce la categoría: vertical (entretenimiento, deportes…), forma (película / TV) y género. La propuesta usa Content Taxonomy 2.2 (p. ej. `Movies > Drama Movies`) porque es la que permite los tres.*

Evidencia disponible por fila: externa 48.8%, interna 34.0%, ninguna 16.0%, serie 1.2% (*externa* = match IMDb; *interna* = el género de la misma fila; *serie* = trae nombre de serie; *ninguna* = sin nada que cruzar).

Categorías más propuestas: `Movies > Drama Movies | Television > Drama TV` 5.2%; `Movies > Drama Movies` 5.0%; `Movies > Documentary Movies | Television > Factual TV` 3.9%; `Movies > Horror Movies` 3.8%; `Movies > Crime and Mystery Movies` 3.4%.

**Confiabilidad de lo que trae y de lo que se llena (filas con categoría, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide con la evidencia (`coincide`) | 19.8% | 41.5% |
| Compatible (genérica, no contradice) (`compatible`) | 49.7% | 44.4% |
| Contradice la evidencia (`contradice`) | 12.7% | 4.7% |
| No se pudo evaluar (`no_evaluable`) | 17.9% | 9.3% |

**Límites:** el consolidado mezcla tres taxonomías (1.0, 2.2, 3.0) y texto libre (`[sports]`, `[Live]`); lo declarado es en su mayoría genérico (nivel 1, solo la vertical). Los valores por defecto que declaran algunas apps (`[IAB12]` de Vidaa, `[IAB1]` de OTTera) son correctos como vertical pero no como género, y `intra_titulo` los propaga. Un match IMDb de confianza B acierta ~75 %, así que parte de las "contradicciones" son matches equivocados; se separan con `genero_vs_imdb` en el CSV fila a fila.

## contentGenre

**Hoy:** 91.0% de las filas y 85.8% de los requests traen dato útil. Top 3 referencias: Drama 10.8%, *N/A 9.0%*, drama 5.0%.

**Tras el relleno:** 96.9% de las filas (de 91.0%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 91.0% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 3.6% |
| IMDb (`imdb`) | 2.3% |
| Sigue vacío (`sin_dato`) | 3.1% |

**Método y fuentes:** `intra_titulo` como en las demás columnas; para lo que sigue vacío, los géneros del match IMDb (`title.basics`, hasta tres) traducidos al vocabulario canónico del proyecto (`norm_genre`), y los géneros de Wikidata (`P136`) para lo que IMDb no expresa (telenovela, holiday). La validación compara cada género declarado con IMDb/Wikidata por *conceptos* (thriller/misterio/crimen → crimen-misterio, anime → animación) y propone géneros adicionales o más precisos.

**Qué más se puede afinar (validación del consolidado):**

| Mejora posible | % filas | % requests |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 2.6% | 1.3% |
| Se pueden agregar géneros o uno más preciso (`sube`) | 23.6% | 23.5% |
| Se puede corregir (contradecía) (`corrige`) | 1.5% | 2.0% |
| Se corrige en parte (acertaba en parte) (`corrige_parcial`) | 2.7% | 0.8% |
| Se queda igual (ya está bien) (`mantiene`) | 63.2% | 59.6% |
| Sin propuesta (sin evidencia) (`sin_propuesta`) | 6.4% | 12.9% |

| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |
|---|---:|---:|
| Nivel 0 · vacío | 9.0% | 6.4% |
| Nivel 1 · sin género comparable (solo "entertainment", "other"…) | 14.8% | 12.9% |
| Nivel 2 · un género | 59.0% | 41.5% |
| Nivel 3 · dos o más géneros | 17.3% | 39.3% |

*Wikidata (`P136`) permite etiquetar como telenovela 1.6% de las filas (4.3% de los requests) que hoy solo dicen drama/romance.*

Combinaciones más propuestas: `drama,romance` 1.0%; `drama` 0.9%; `drama,comedia` 0.8%; `terror,thriller` 0.8%; `drama,thriller` 0.7%.

**Confiabilidad (filas con género comparable, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 41.4% | 41.5% |
| Parecido (género vecino) (`afin`) | 2.6% | 2.5% |
| Acierta en parte (`parcial`) | 2.9% | 2.8% |
| Contradice (`contradice`) | 1.7% | 1.6% |
| No se pudo evaluar (`no_evaluable`) | 51.3% | 51.7% |

**Límites:** es la columna que mejor viene (>90 %), así que el margen es afinar, no llenar. El vocabulario del vendedor es libre (`Drama` y `drama` son valores distintos en la fuente; `entertainment`, `other`, `movies` no son géneros comparables) y géneros que IMDb no maneja (lifestyle, viajes, religión, videojuegos) no se pueden juzgar. Solo la mitad de las filas tiene match externo; el resto queda como "no evaluable".

## contentSeries

**Hoy:** 6.5% de las filas y 6.0% de los requests traen dato útil. Top 3 referencias: *N/A 92.7%*, *md5-vacío 0.7%*, VOD 0.6%.

**Tras el relleno:** 14.0% de las filas (de 6.4%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 6.4% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 0.7% |
| IMDb (`imdb`) | 7.0% |
| Sigue vacío (`sin_dato`) | 86.0% |

**Método y fuentes:** el pipeline llena solo lo seguro: `imdb` cuando el match (A/B) dice tvSeries o tvMiniSeries, con el título canónico de IMDb; `intra_titulo` cuando otras rutas del mismo título nombran la serie (≥ 30 filas y ≥ 2 publishers, porque un episodio puede llamarse igual que una película). La validación identifica además qué filas **son** serie sin decirlo (IMDb, el título con "season N" / S01E03 / "ep N", o las otras rutas) y propone un nombre: el título sin sufijos de temporada/episodio, el que traen las otras rutas, o el canónico IMDb.

**Qué es cada fila según la evidencia (consolidado):**

| Qué es | % filas |
|---|---:|
| Serie | 15.4% |
| Película | 33.5% |
| Ambiguo (corto, tv movie, video, especial) | 7.5% |
| Desconocido (sin evidencia) | 43.6% |

**Qué se puede hacer con cada fila:**

| Situación | % filas | % requests |
|---|---:|---:|
| Serie con nombre (`ya_nombrada`) | 5.0% | 4.5% |
| Serie sin nombre, con nombre proponible (`serie_sin_nombre_recuperable`) | 10.3% | 11.0% |
| Película: el vacío es correcto (`pelicula_vacio_correcto`) | 33.4% | 23.1% |
| Película con serie declarada (contradicción) (`pelicula_con_serie_declarada`) | 0.1% | 0.0% |
| Contradicha (`contradicha`) | 0.0% | 0.0% |
| Con nombre, sin evidencia para juzgar (`nombrada_sin_evidencia`) | 0.0% | 0.0% |
| Sin evidencia (`sin_evidencia`) | 51.1% | 61.3% |

**Temporada / episodio que trae el título** (candidatos a `content.season` / `content.episode`):

| El título trae | % filas |
|---|---:|
| Temporada y episodio (`temporada+episodio`) | 0.1% |
| Solo temporada (`solo_temporada`) | 3.8% |
| Solo episodio (`solo_episodio`) | 0.8% |
| Nada (`nada`) | 95.3% |

Nombres de serie más propuestos (`[titulo]` = del propio título sin sufijos, `[imdb]` = título canónico): `chicken stew [titulo]` 0.4%; `forest frenzy of boonie bears [titulo]` 0.2%; `something scary [titulo]` 0.2%; `cain [imdb]` 0.1%; `haus of horror [imdb]` 0.1%.

**Confiabilidad de las series declaradas (filas con nombre de serie real, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 2.5% | 57.3% |
| Es serie, pero con otro nombre (compatible) (`otro_nombre`) | 4.9% | 2.1% |
| IMDb dice que es película (`contradice`) | 2.6% | 1.2% |
| No se pudo evaluar (`no_evaluable`) | 90.1% | 39.4% |

**Límites:** la mayor parte del vacío es correcta: las películas no pertenecen a ninguna serie. Casi la mitad de las filas no tiene evidencia (títulos sin match, placeholders como `roku` / `epg`). Roku manda un hash MD5 en vez del nombre y algunos vendedores mandan `VOD` o macros sin reemplazar; todo eso cuenta como vacío.

## contentLength

**Hoy:** 12.2% de las filas y 21.4% de los requests traen dato útil. Top 3 referencias: *N/A 87.8%*, 5 3.4%, 6 3.2%.

**Tras el relleno:** 49.0% de las filas (de 12.2%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 12.2% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 36.8% |
| Sigue vacío (`sin_dato`) | 51.0% |

**Método y fuentes:** solo `intra_titulo` (otra ruta del mismo título trae el código). IMDb (`runtimeMinutes`) y Wikidata (`P2047`) traen la duración en minutos de la mayoría de los títulos con match, pero esa duración solo se escribe con `--length-desde-runtime`, apagado por defecto.

**Límites:** contentLength no es una duración: es un **código 1–8** (rangos de duración; el mapa por defecto del pipeline es 1: ≤ 1 min, 2: ≤ 5, 3: ≤ 15, 4: ≤ 30, 5: ≤ 60, 6: ≤ 120, 7: ≤ 180, 8: más). Mientras PubMatic no confirme los cortes de cada código, convertir minutos a código es una suposición y por eso no se aplica. Con esa confirmación, el runtime externo cubriría buena parte de lo que sigue vacío (títulos con match IMDb).

## contentLanguage

**Hoy:** 66.3% de las filas y 66.2% de los requests traen dato útil. Top 3 referencias: *N/A 33.6%*, en 23.1%, English 17.5%.

**No se rellena.** No hay forma de asumir el idioma en el que se emite un programa en ninguna circunstancia: el mismo título puede ir con pistas de audio distintas por ruta, y el idioma original de la obra (IMDb / Wikidata) no dice en cuál se sirvió. Solo vale lo que declara el vendedor.

## contentIsLiveStream

**Hoy:** 29.3% de las filas y 39.9% de los requests traen dato útil. Top 3 referencias: *Unknown 36.7%*, *N/A 34.0%*, 1 29.3%.

**Tras el relleno:** 48.7% de las filas (de 29.3%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 29.3% |
| Semántica de la app (curada a mano) (`app_semantica`) | 19.4% |
| Sigue vacío (`sin_dato`) | 51.3% |

**Método y fuentes:** mide el **modo de entrega** (canal lineal vs on demand), no el contenido, así que no se propaga por título (la misma película puede ir en un canal lineal y en VOD) ni por app (MovieArk marca 1 todo su catálogo). La única señal que se usa es la semántica de la app validada a mano (`semantica_apps.csv`: ficha de tienda + evidencia del dataset). El tipo IMDb (película → 0) se retiró: una película en un canal lineal es livestream = 1.

**Límites:** todo lo declarado por los vendedores es `1`; el `0` nunca llega. De 16 apps revisadas solo dos son lineales puras; las 13 mixtas (MovieArk, TCL CHANNEL…) no se pueden resolver sin saber por qué ruta se sirvió cada request. La mitad del consolidado seguirá vacía hasta que el vendedor lo mande.

## contentRating

**Hoy:** 74.9% de las filas y 78.1% de los requests traen dato útil. Top 3 referencias: *N/A 25.1%*, Adults 10.3%, Teen Plus 9.3%.

**Tras el relleno:** 82.1% de las filas (de 74.9%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 74.9% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 7.2% |
| Wikidata (`wikidata`) | 0.1% |
| Sigue vacío (`sin_dato`) | 17.9% |

**Método y fuentes:** `intra_titulo` (canonizando la escala nueva: `All Ages` = g, `Teen` = tv-pg, `Teen Plus` = tv-14, `Adults` = tv-ma, `Unrated` = nr) y, marginalmente, la clasificación de Wikidata (`P3834`).

**Límites:** no hay fuente abierta de clasificaciones por edad con cobertura: los datasets públicos de IMDb no traen la Parental Guide y en Wikidata `P3834` es rara. Lo que queda vacío son títulos que ninguna ruta clasifica; solo el vendedor puede completarlo. El consolidado mezcla dos escalas (`tv-14` y `Teen Plus` para el mismo título); `rating_franja` de `normalizar_monetizar.py` las unifica en franjas de edad.

## contentTitle

**Hoy:** 93.2% de las filas y 71.6% de los requests traen algo. Top 3 referencias: *N/A 6.8%*, roku 0.2%, epg 0.2%.

**Método y fuentes:** no se rellena. El título es la **llave** de todo lo demás: es lo que se normaliza (`titulo_clave`) y se busca en IMDb/Wikidata, y es lo que agrupa las rutas de venta para `intra_titulo`. Lo que sí se hace es medir cuánto de lo "lleno" es un título de verdad: se descuentan placeholders (`roku`, `epg`, `vod`), nombres de canal (`las estrellas`, `canal 5`), slugs técnicos (`*_trailer`), macros sin reemplazar (`{{content_title}}`), texto sin letras o de una o dos letras y encoding roto (en esta tanda, 1,124,340 filas, 86.6% del consolidado, pasan el filtro).

**Límites:** sin título no hay nada que cruzar afuera: una fila vacía en contentTitle solo la puede completar el vendedor. Y el vacío pesa más en tráfico que en catálogo (28.4% de los requests vs 6.8% de las filas): son pocas combinaciones con muchos requests.
