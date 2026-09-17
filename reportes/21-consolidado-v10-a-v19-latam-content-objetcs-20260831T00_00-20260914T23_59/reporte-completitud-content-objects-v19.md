# Qué se puede completar de cada content object: métodos y fuentes (consolidado v10 a v19)

**Fuente:** `inventory-consolidado-v10-a-v19.csv` — 1,158,509 filas únicas, 482,736,715,920 requests (métricas del corte v19). **Relleno:** `inventory-consolidado-v10-a-v19-relleno.csv` (no versionado), generado con `scripts/enriquecer_externo.py --wikidata`, corrida del 2026-09-16 15:30 → `recursos/reporte-relleno-v19.json`. Títulos distintos: 15,799; con match en IMDb: 7,879; consultados por primera vez en esta corrida: 532.
**Validaciones:** `scripts/validar_categorias.py` y `scripts/validar_genero_series.py` sobre el consolidado y sobre el relleno (`recursos/validacion-*.json`, con muestras CSV para revisión manual en la misma carpeta). Tablas generadas con `scripts/generar_reporte_completitud.py`.

## Cómo leer este reporte

- Cada fila del consolidado es una **combinación** de 14 dimensiones (país × publisher × app × género × …), no un programa. El mismo contenido llega por varias rutas de venta y cada ruta manda la metadata que quiere: por eso la respuesta a un vacío muchas veces ya está escrita en otra fila del mismo título.
- Una celda cuenta como **llena** solo si trae dato útil: no cuentan los centinelas (`Not Available`, `Unknown`, `[-7]`, el MD5 de cadena vacía, macros sin reemplazar).
- Los % son sobre el total de filas del consolidado (y, cuando se indica, sobre el total de requests). "Hoy" es como llega; "tras el relleno" es después de correr el pipeline con los candados por defecto.
- **Se puede completar** tiene dos lecturas: (1) lo que el pipeline **ya llena** automáticamente (tabla de orígenes por columna) y (2) lo que la validación contra fuentes abiertas dice que **se podría afinar o corregir** además (nivel de detalle alcanzable, géneros adicionales, nombre de serie proponible). Lo segundo no se escribe al CSV: son propuestas fila a fila en los `validacion-*.json` y en los CSV `*-filas.csv` de la raíz.

## Fuentes

| Fuente | Qué aporta | Cómo se usa | Licencia / límite |
|---|---|---|---|
| **El propio consolidado** (otras filas del mismo título; el comportamiento de cada app) | Categoría, serie, duración, idioma, rating, género | Se normaliza el título a `titulo_clave` (url-decode, mojibake, sin ": trailer", "season N", SxxEyy) y se agrupan las filas; por app se mide qué valor manda cuando manda | Sin costo. Es la fuente más precisa (mismo contenido, otra ruta) y la que más aporta |
| **Semántica de apps curada a mano** (`cache-enriquecimiento/semantica_apps.csv`) | Modo de entrega (lineal / VOD) por app | Ficha de tienda y evidencia del dataset, revisada a mano; solo las filas con `aplicar=si` rellenan | 16 apps revisadas; solo 2 (Live TV de TCL, Coolita Channel) son lineales puras y se aplican |
| **IMDb Non-Commercial Datasets** (`title.basics`, `title.akas` es/pt/en, `title.ratings`, `title.episode`) | Tipo (película / serie / corto…), géneros, título canónico, año, duración | Match offline por título normalizado y alias en español/portugués/inglés; confianza A–D (A ≈ 90 %+, B ≈ 75 %; se usa hasta B) | Solo uso no comercial; ~750 MB descargados a `cache-enriquecimiento/imdb/` |
| **Wikidata** (SPARQL, vía el id IMDb `P345`) | Idioma original (`P364`), duración (`P2047`), géneros (`P136`, p. ej. telenovela), clasificación (`P3834`, rara) | Solo para títulos con match IMDb; resultado cacheado por título | CC0, sin API key; el idioma es el **original**, no el de emisión |
| **TVMaze** (opcional, `--tvmaze`) | Idioma, géneros, duración de series | Series sin match IMDb | CC BY-SA, ~20 req/10 s. **No se usó en esta corrida** |
| **Taxonomías IAB Tech Lab** (Content Taxonomy 1.0, 2.2, 3.0) | Si un código declarado existe y qué significa; códigos propuestos | Descargadas a `cache-enriquecimiento/iab/`; cada código se traduce a (vertical, forma, género) para comparar entre taxonomías | Abiertas (GitHub de IAB Tech Lab) |

*Cache incremental: `cache-enriquecimiento/titulos.json` guarda el resultado de cada título; en cada tanda solo se consultan los títulos nuevos.*

## Métodos (en orden: el primero que llena gana, y queda anotado en `<columna>_origen`)

| Método (`origen`) | Qué hace | Candado | Columnas donde aplica |
|---|---|---|---|
| `intra_titulo` | Copia el valor que otra fila del **mismo título** ya trae (misma película, otra ruta de venta) | El valor debe dominar ≥ 80 % de las filas con dato de ese título; en contentSeries además ≥ 30 filas y ≥ 2 publishers | category, series, length, language, rating, genre |
| `app_default` | Para títulos donde ninguna ruta manda el dato, usa el valor **constante** que esa app manda cuando sí lo manda | La app debe mandar el mismo valor ≥ 95 % de las veces y tener ≥ 200 filas con dato | category, length, language, rating, genre (no livestream) |
| `imdb` | Match del título contra IMDb: tipo, géneros, título canónico | Confianza A o B | series (tvSeries → título canónico), genre |
| `wikidata` | Idioma original, duración, géneros y clasificación del ítem ligado al id IMDb | Solo títulos con match IMDb | language, rating (y genre vía telenovela) |
| `derivado_genero` | Traduce el género de la misma fila a categoría IAB (mapa aprendido de las filas que traen ambas columnas: deportes → `[IAB17]`, noticias → `[IAB12]`…) | Solo géneros que definen vertical | category |
| `derivado_tipo` | Desempata con el tipo IMDb cuando el género no define categoría: movie → `[IAB1-5]`, tvSeries → `[IAB1-7]` | Match IMDb A/B | category (y livestream = 0 solo con flag explícito) |
| `app_semantica` + señales del vendedor | Modo de entrega: `contentSeries = "VOD"` → 0, `"… Livestream"` → 1; app lineal pura → 1, VOD pura → 0 | Solo apps con `aplicar=si` en la tabla curada | livestream |

## Resumen: cuánto viene lleno hoy y cuánto queda tras el relleno

| Columna | Hoy (% filas) | Hoy (% requests) | Tras el relleno (% filas) | Ganancia | Sigue vacío | Método que más aporta |
|---|---:|---:|---:|---:|---:|---|
| contentGenre | 91.7% | 84.7% | 97.2% | +5.5 pp | 2.8% | Copiado de otra ruta del mismo título (`intra_titulo`) |
| contentTitle | 93.2% | 71.3% | 93.2% | — | 6.8% | No se rellena (ver abajo) |
| contentRating | 74.3% | 75.5% | 82.7% | +8.4 pp | 17.3% | Copiado de otra ruta del mismo título (`intra_titulo`) |
| contentLanguage | 65.7% | 66.7% | 96.1% | +30.4 pp | 3.9% | Copiado de otra ruta del mismo título (`intra_titulo`) |
| contentIsLiveStream | 29.2% | 42.7% | 49.2% | +20.0 pp | 50.8% | Semántica de la app (curada a mano) (`app_semantica`) |
| contentCategory | 21.7% | 30.7% | 93.9% | +72.2 pp | 6.1% | Derivado del tipo IMDb (película / serie) (`derivado_tipo`) |
| contentLength | 11.9% | 23.4% | 50.2% | +38.3 pp | 49.8% | Copiado de otra ruta del mismo título (`intra_titulo`) |
| contentSeries | 6.5% | 6.9% | 14.0% | +7.6 pp | 86.0% | IMDb (`imdb`) |

*contentIsTitlePresent y Publisher vienen al 100 % y no entran. "Ganancia" son puntos porcentuales de filas del consolidado.*

## contentCategory

**Hoy:** 21.7% de las filas y 30.7% de los requests traen dato útil. Top 3 referencias: *[-7] 78.3%*, [IAB1] 5.3%, [IAB1-22] 2.9%.

**Tras el relleno:** 93.9% de las filas (de 21.7%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 21.7% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 11.1% |
| Valor habitual de la app (`app_default`) | 8.1% |
| Derivado del género (`derivado_genero`) | 22.8% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 30.2% |
| Sigue vacío (`sin_dato`) | 6.1% |

**Método y fuentes:** cuatro escalones. `intra_titulo` copia la categoría que otra ruta del mismo título ya manda (Vidaa o Equativ suelen mandarla; OTTera y TCL mandan `[-7]`). `app_default` aplica el valor constante de la app (OTTera → MovieArk manda `[IAB1]` el 99 % de las veces). `derivado_genero` traduce el contentGenre de la misma fila con el mapa IAB 1.0 aprendido del propio dataset (~150k filas traen ambas columnas). `derivado_tipo` usa el tipo IMDb para separar película (`[IAB1-5]`) de serie (`[IAB1-7]`). La validación va un paso más allá y propone, con la taxonomía 2.2, la categoría más fina que la evidencia permite (forma + género).

**Qué más se puede afinar (validación del consolidado contra IMDb / Wikidata / taxonomías IAB):**

| Mejora posible | % filas | % requests |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 70.9% | 56.9% |
| Se puede afinar (estaba llena, pero genérica) (`sube`) | 11.3% | 10.4% |
| Se puede corregir (estaba incorrecta) (`corrige`) | 2.7% | 3.5% |
| Se queda igual (ya está bien) (`mantiene`) | 7.7% | 16.7% |
| Sin propuesta (vacía y sin evidencia) (`sin_propuesta`) | 7.4% | 12.4% |

| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |
|---|---:|---:|
| Nivel 0 · nada | 78.6% | 7.5% |
| Nivel 1 · solo la vertical | 13.6% | 13.8% |
| Nivel 2 · vertical + película/TV (o deporte) | 6.8% | 33.5% |
| Nivel 3 · vertical + película/TV + género | 1.1% | 45.3% |

*El nivel mide cuántos atributos conoce la categoría: vertical (entretenimiento, deportes…), forma (película / TV) y género. La propuesta usa Content Taxonomy 2.2 (p. ej. `Movies > Drama Movies`) porque es la que permite los tres.*

Evidencia disponible por fila: externa 49.3%, interna 33.8%, ninguna 15.7%, serie 1.2% (*externa* = match IMDb; *interna* = el género de la misma fila; *serie* = trae nombre de serie; *ninguna* = sin nada que cruzar).

Categorías más propuestas: `Movies > Drama Movies | Television > Drama TV` 5.2%; `Movies > Drama Movies` 5.0%; `Movies > Horror Movies` 3.8%; `Movies > Documentary Movies | Television > Factual TV` 3.7%; `Movies > Crime and Mystery Movies` 3.4%.

**Confiabilidad de lo que trae y de lo que se llena (filas con categoría, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide con la evidencia (`coincide`) | 20.2% | 37.4% |
| Compatible (genérica, no contradice) (`compatible`) | 49.8% | 47.5% |
| Contradice la evidencia (`contradice`) | 12.4% | 5.2% |
| No se pudo evaluar (`no_evaluable`) | 17.5% | 9.8% |

**Límites:** el consolidado mezcla tres taxonomías (1.0, 2.2, 3.0) y texto libre (`[sports]`, `[Live]`); lo declarado es en su mayoría genérico (nivel 1, solo la vertical). Los defaults por app (`[IAB12]` de Vidaa, `[IAB1]` de OTTera) son correctos como vertical pero no como género, y `intra_titulo` los propaga. Un match IMDb de confianza B acierta ~75 %, así que parte de las "contradicciones" son matches equivocados; se separan con `genero_vs_imdb` en el CSV fila a fila.

## contentGenre

**Hoy:** 91.7% de las filas y 84.7% de los requests traen dato útil. Top 3 referencias: Drama 10.0%, *N/A 8.2%*, drama 5.6%.

**Tras el relleno:** 97.2% de las filas (de 91.7%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 91.7% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 3.2% |
| IMDb (`imdb`) | 2.2% |
| Sigue vacío (`sin_dato`) | 2.8% |

**Método y fuentes:** `intra_titulo` y `app_default` como en las demás columnas; para lo que sigue vacío, los géneros del match IMDb (`title.basics`, hasta tres) traducidos al vocabulario canónico del proyecto (`norm_genre`), y los géneros de Wikidata (`P136`) para lo que IMDb no expresa (telenovela, holiday). La validación compara cada género declarado con IMDb/Wikidata por *conceptos* (thriller/misterio/crimen → crimen-misterio, anime → animación) y propone géneros adicionales o más precisos.

**Qué más se puede afinar (validación del consolidado):**

| Mejora posible | % filas | % requests |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 2.5% | 1.9% |
| Se pueden agregar géneros o uno más preciso (`sube`) | 23.1% | 22.2% |
| Se puede corregir (contradecía) (`corrige`) | 1.4% | 1.7% |
| Se corrige en parte (acertaba en parte) (`corrige_parcial`) | 3.0% | 0.9% |
| Se queda igual (ya está bien) (`mantiene`) | 64.2% | 59.9% |
| Sin propuesta (sin evidencia) (`sin_propuesta`) | 5.8% | 13.4% |

| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |
|---|---:|---:|
| Nivel 0 · vacío | 8.3% | 5.8% |
| Nivel 1 · sin género comparable (solo "entertainment", "other"…) | 15.0% | 13.1% |
| Nivel 2 · un género | 57.4% | 40.7% |
| Nivel 3 · dos o más géneros | 19.3% | 40.4% |

*Wikidata (`P136`) permite etiquetar como telenovela 1.6% de las filas (4.6% de los requests) que hoy solo dicen drama/romance.*

Combinaciones más propuestas: `drama,romance` 0.9%; `drama` 0.9%; `drama,comedia` 0.8%; `terror,thriller` 0.8%; `comedia` 0.7%.

**Confiabilidad (filas con género comparable, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 41.6% | 41.7% |
| Parecido (género vecino) (`afin`) | 2.5% | 2.4% |
| Acierta en parte (`parcial`) | 3.3% | 3.1% |
| Contradice (`contradice`) | 1.6% | 1.5% |
| No se pudo evaluar (`no_evaluable`) | 51.1% | 51.4% |

**Límites:** es la columna que mejor viene (>90 %), así que el margen es afinar, no llenar. El vocabulario del vendedor es libre (`Drama` y `drama` son valores distintos en la fuente; `entertainment`, `other`, `movies` no son géneros comparables) y géneros que IMDb no maneja (lifestyle, viajes, religión, videojuegos) no se pueden juzgar. Solo la mitad de las filas tiene match externo; el resto queda como "no evaluable".

## contentSeries

**Hoy:** 6.5% de las filas y 6.9% de los requests traen dato útil. Top 3 referencias: *N/A 92.8%*, *md5-vacío 0.7%*, VOD 0.6%.

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
| Serie | 15.3% |
| Película | 33.9% |
| Ambiguo (corto, tv movie, video, especial) | 7.6% |
| Desconocido (sin evidencia) | 43.2% |

**Qué se puede hacer con cada fila:**

| Situación | % filas | % requests |
|---|---:|---:|
| Serie con nombre (`ya_nombrada`) | 5.0% | 5.5% |
| Serie sin nombre, con nombre proponible (`serie_sin_nombre_recuperable`) | 10.2% | 10.9% |
| Película: el vacío es correcto (`pelicula_vacio_correcto`) | 33.8% | 22.3% |
| Película con serie declarada (contradicción) (`pelicula_con_serie_declarada`) | 0.1% | 0.0% |
| Contradicha (`contradicha`) | 0.0% | 0.0% |
| Con nombre, sin evidencia para juzgar (`nombrada_sin_evidencia`) | 0.0% | 0.0% |
| Sin evidencia (`sin_evidencia`) | 50.8% | 61.3% |

**Temporada / episodio que trae el título** (candidatos a `content.season` / `content.episode`):

| El título trae | % filas |
|---|---:|
| Temporada y episodio (`temporada+episodio`) | 0.2% |
| Solo temporada (`solo_temporada`) | 3.7% |
| Solo episodio (`solo_episodio`) | 0.8% |
| Nada (`nada`) | 95.4% |

Nombres de serie más propuestos (`[titulo]` = del propio título sin sufijos, `[imdb]` = título canónico): `chicken stew [titulo]` 0.4%; `forest frenzy of boonie bears [titulo]` 0.2%; `something scary [titulo]` 0.2%; `cain [imdb]` 0.1%; `the baddest bad boy [imdb]` 0.1%.

**Confiabilidad de las series declaradas (filas con nombre de serie real, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 2.5% | 57.1% |
| Es serie, pero con otro nombre (compatible) (`otro_nombre`) | 5.2% | 2.2% |
| IMDb dice que es película (`contradice`) | 2.5% | 1.2% |
| No se pudo evaluar (`no_evaluable`) | 89.8% | 39.5% |

**Límites:** la mayor parte del vacío es correcta: las películas no pertenecen a ninguna serie. Casi la mitad de las filas no tiene evidencia (títulos sin match, placeholders como `roku` / `epg`). Roku manda un hash MD5 en vez del nombre y algunos vendedores mandan `VOD` o macros sin reemplazar; todo eso cuenta como vacío.

## contentLength

**Hoy:** 11.9% de las filas y 23.4% de los requests traen dato útil. Top 3 referencias: *N/A 88.1%*, 5 3.3%, 4 3.1%.

**Tras el relleno:** 50.2% de las filas (de 11.9%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 11.9% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 35.9% |
| Valor habitual de la app (`app_default`) | 2.3% |
| Sigue vacío (`sin_dato`) | 49.8% |

**Método y fuentes:** `intra_titulo` (otra ruta del mismo título trae el código) y `app_default`. IMDb (`runtimeMinutes`) y Wikidata (`P2047`) traen la duración en minutos de la mayoría de los títulos con match, pero esa duración solo se escribe con `--length-desde-runtime`, apagado por defecto.

**Límites:** contentLength no es una duración: es un **código 1–8** (rangos de duración; el mapa por defecto del pipeline es 1: ≤ 1 min, 2: ≤ 5, 3: ≤ 15, 4: ≤ 30, 5: ≤ 60, 6: ≤ 120, 7: ≤ 180, 8: más). Mientras PubMatic no confirme los cortes de cada código, convertir minutos a código es una suposición y por eso no se aplica. Con esa confirmación, el runtime externo cubriría buena parte de lo que sigue vacío (títulos con match IMDb).

## contentLanguage

**Hoy:** 65.7% de las filas y 66.7% de los requests traen dato útil. Top 3 referencias: *N/A 34.3%*, en 25.9%, es 14.8%.

**Tras el relleno:** 96.1% de las filas (de 65.7%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 65.7% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 29.6% |
| Valor habitual de la app (`app_default`) | 0.5% |
| Wikidata (`wikidata`) | 0.3% |
| Sigue vacío (`sin_dato`) | 3.9% |

**Método y fuentes:** `intra_titulo` (canonizando `English` → `en`, `Spanish` → `es`, porque desde v16 conviven el código ISO y el nombre), `app_default` y, para lo que sigue vacío, el idioma **original** del título según Wikidata (`P364`).

**Límites:** el idioma original no siempre es el de emisión (una película en inglés doblada al español en un canal FAST). Por eso Wikidata se usa al final y aporta poco; casi todo el relleno viene de otras rutas del mismo título.

## contentIsLiveStream

**Hoy:** 29.2% de las filas y 42.7% de los requests traen dato útil. Top 3 referencias: *Unknown 37.1%*, *N/A 33.7%*, 1 29.2%.

**Tras el relleno:** 49.2% de las filas (de 29.2%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 29.2% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 0.5% |
| Semántica de la app (curada a mano) (`app_semantica`) | 19.5% |
| Sigue vacío (`sin_dato`) | 50.8% |

**Método y fuentes:** mide el **modo de entrega** (canal lineal vs on demand), no el contenido, así que no se propaga por título (la misma película puede ir en un canal lineal y en VOD) ni por app (MovieArk marca 1 todo su catálogo). Solo se usan dos señales: lo que el vendedor deja en contentSeries (`VOD` → 0, `… Livestream` → 1) y la semántica de la app validada a mano (`semantica_apps.csv`: ficha de tienda + evidencia del dataset). El tipo IMDb (película → 0) existe como opción pero está apagado: una película en un canal lineal es livestream = 1.

**Límites:** todo lo declarado por los vendedores es `1`; el `0` nunca llega. De 16 apps revisadas solo dos son lineales puras; las 13 mixtas (MovieArk, TCL CHANNEL…) no se pueden resolver sin saber por qué ruta se sirvió cada request. La mitad del consolidado seguirá vacía hasta que el vendedor lo mande.

## contentRating

**Hoy:** 74.3% de las filas y 75.5% de los requests traen dato útil. Top 3 referencias: *N/A 25.7%*, Adults 8.9%, Teen Plus 7.7%.

**Tras el relleno:** 82.7% de las filas (de 74.3%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 74.3% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 8.4% |
| Wikidata (`wikidata`) | 0.1% |
| Sigue vacío (`sin_dato`) | 17.3% |

**Método y fuentes:** `intra_titulo` (canonizando la escala nueva: `All Ages` = g, `Teen` = tv-pg, `Teen Plus` = tv-14, `Adults` = tv-ma, `Unrated` = nr), `app_default` y, marginalmente, la clasificación de Wikidata (`P3834`).

**Límites:** no hay fuente abierta de clasificaciones por edad con cobertura: los datasets públicos de IMDb no traen la Parental Guide y en Wikidata `P3834` es rara. Lo que queda vacío son títulos que ninguna ruta clasifica; solo el vendedor puede completarlo. El consolidado mezcla dos escalas (`tv-14` y `Teen Plus` para el mismo título); `rating_franja` de `normalizar_monetizar.py` las unifica en franjas de edad.

## contentTitle

**Hoy:** 93.2% de las filas y 71.3% de los requests traen algo. Top 3 referencias: *N/A 6.8%*, roku 0.2%, epg 0.1%.

**Método y fuentes:** no se rellena. El título es la **llave** de todo lo demás: es lo que se normaliza (`titulo_clave`) y se busca en IMDb/Wikidata, y es lo que agrupa las rutas de venta para `intra_titulo`. Lo que sí se hace es medir cuánto de lo "lleno" es un título de verdad: se descuentan placeholders (`roku`, `epg`, `vod`), nombres de canal (`las estrellas`, `canal 5`), slugs técnicos (`*_trailer`), macros sin reemplazar (`{{content_title}}`), texto sin letras o de una o dos letras y encoding roto (en esta tanda, 1,003,379 filas, 86.6% del consolidado, pasan el filtro).

**Límites:** sin título no hay nada que cruzar afuera: una fila vacía en contentTitle solo la puede completar el vendedor. Y el vacío pesa más en tráfico que en catálogo (28.7% de los requests vs 6.8% de las filas): son pocas combinaciones con muchos requests.
