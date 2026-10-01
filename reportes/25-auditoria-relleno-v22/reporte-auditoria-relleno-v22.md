# Auditoría del relleno de content objects (consolidado v10 a v22)

**Pregunta:** lo que "llenamos" de más en los ejercicios de completitud y correctitud, ¿está bien y es útil? ¿Cómo se comprueba, contra qué otras bases, cómo se evitan los homónimos y qué más se puede llenar?

**Fuente:** `inventory-consolidado-v10-a-v22-relleno.csv`: 1,344,629 filas y 622,384,767,599 requests, más el caché de títulos `cache-enriquecimiento/titulos.json` (18,246 títulos normalizados). Las cifras salen de `scripts/auditar_relleno.py` → `recursos/auditoria-relleno-v22.json` y de una consulta a Wikidata → `recursos/cobertura-wikidata-propiedades.json`.

---

## 0. Respuesta corta

| Pregunta | Respuesta |
|---|---|
| ¿Se puede tener certeza completa? | **No con lo que hay hoy.** Las precisiones que citamos (A ≈ 90 %, B ≈ 75 %) salen de una revisión manual de v15 que no quedó guardada, y las validaciones (`validar_*`) miden el relleno contra la **misma** evidencia que lo produjo (IMDb/Wikidata), así que no pueden detectar un match equivocado. La certeza se consigue con tres cosas: (1) una prueba de enmascaramiento, ya medida aquí; (2) una muestra revisada a mano con intervalo de confianza, para la que ya quedó la página de revisión; (3) una segunda base cruzada por ID y no por título. |
| ¿Qué está bien? | Lo que se copia **entre rutas del mismo título** (`intra_titulo`): al esconder el dato que sí se conoce y predecirlo, acierta el 97–99 % en series y length, y el 92–98 % en rating y género. La semántica de app para livestream, revisada a mano. |
| ¿Qué es dudoso? | Todo lo que depende del **match por título con IMDb**: tipo película/serie → categoría `[IAB1-5]`/`[IAB1-7]`, nombre de serie y géneros IMDb. Es el 33 % de los requests del consolidado (206 mil millones) y el **62 % de esos requests tiene al menos una señal de homónimo**. Además, `intra_titulo` en contentCategory solo coincide con la categoría del vendedor en el 50 % de los casos (70 % en la vertical). |
| ¿Qué es poco útil? | El 32 % del tráfico con categoría rellenada recibe `[IAB1]` genérico ("Arts & Entertainment"), que casi no informa. contentLength se rellena con un código 1–8 cuyo significado no conocemos: coincide entre rutas, pero no sabemos qué dice. |
| ¿Contra qué contrastar? | **TMDB por ID** (el 51 % de los matches A/B ya trae el ID de TMDB en Wikidata, así que el cruce no depende del título) y **Wikidata** para tipo, país, año y cadena. Para el rating por país: TMDB (certificaciones MX/CO/CL/AR/BR) y los organismos oficiales. Lo definitivo: el ID de contenido del propio vendedor (EIDR / Gracenote). |
| ¿Homónimos? | Hay casos medidos: "faded" → *Milk Money*, "hunter" → *Predator*, "ono" → *It* (2017), "adam jones" → *Burnt* (confianza A), y remakes de telenovela ("hasta que el dinero nos separe" de ViX → la colombiana de 2006, aunque IMDb tiene la de Televisa 2009 con el título exacto). Los candados recomendados están en la §5. |

---

## 1. Qué se llena hoy y cuánto pesa

% sobre el total del consolidado (1,344,629 filas; 622,384,767,599 requests).

| Columna | Origen del valor | % filas | % requests |
|---|---|---:|---:|
| contentCategory | original (vendedor) | 21.9% | 28.6% |
| contentCategory | derivado_tipo (tipo IMDb → [IAB1-5]/[IAB1-7]) | 33.6% | 28.1% |
| contentCategory | derivado_genero (mapa género → IAB) | 26.0% | 25.2% |
| contentCategory | intra_titulo | 11.6% | 6.3% |
| contentCategory | sigue vacía | 7.0% | 11.7% |
| contentSeries | original | 6.6% | 5.4% |
| contentSeries | imdb (título canónico si IMDb dice serie) | 6.9% | 8.2% |
| contentSeries | intra_titulo | 0.7% | 0.6% |
| contentLength | original | 12.6% | 21.0% |
| contentLength | intra_titulo | 36.8% | 30.7% |
| contentIsLiveStream | original | 29.5% | 38.6% |
| contentIsLiveStream | app_semantica (curada a mano) | 19.2% | 16.6% |
| contentRating | original | 75.1% | 78.3% |
| contentRating | intra_titulo | 7.0% | 3.9% |
| contentRating | wikidata | 0.1% | 0.0% |
| contentGenre | original | 90.8% | 85.6% |
| contentGenre | intra_titulo | 3.6% | 2.6% |
| contentGenre | imdb | 2.3% | 1.4% |

Lo rellenado se reparte en tres familias con riesgos distintos:

| Familia | Orígenes | De qué depende | Riesgo principal |
|---|---|---|---|
| Interna | `intra_titulo` | que dos rutas con el mismo título normalizado sean el mismo contenido | homónimo **entre apps** (dos contenidos distintos con el mismo nombre) |
| Derivada | `derivado_genero` | el contentGenre de la misma fila | género mal puesto por el vendedor; mapa genérico ([IAB1]) |
| Externa | `derivado_tipo`, `imdb`, `wikidata` | el **match por título** con IMDb | homónimo **contra IMDb** (otra obra con el mismo título o un título alterno) |
| Curada | `app_semantica` | la tabla `semantica_apps.csv`, revisada a mano | bajo (ya pasó por revisión humana) |

---

## 2. Qué tan bien está: evidencia medida

### 2.1 Prueba de enmascaramiento de `intra_titulo` (leave-one-publisher-out)

Para cada fila que **sí** trae el dato, se esconde el publisher completo y se predice el valor solo con las demás rutas del mismo título, con los mismos candados del pipeline (≥ 80 % de dominancia; en series, ≥ 30 filas y ≥ 2 publishers). Así se simula exactamente el caso real (un vendedor que no manda el dato) en filas donde sí se conoce la respuesta.

| Columna | Filas evaluables | Cobertura (se pudo predecir) | Acierto exacto (filas) | Acierto exacto (requests) | Acierto parcial |
|---|---:|---:|---:|---:|---|
| contentSeries | 51,170 | 62.6% | 99.4% | 99.8% | — |
| contentLength | 97,072 | 84.0% | 97.2% | 98.1% | — |
| contentRating | 867,838 | 43.3% | 91.7% | 97.8% | — |
| contentGenre | 1,057,126 | 9.1% | 91.7% | 95.4% | comparte ≥ 1 género: 88.7% filas / 92.0% req |
| contentCategory | 215,368 | 46.4% | **50.3%** | **67.2%** | misma vertical (IAB1, IAB17…): 70.5% filas / 79.3% req |

Lectura:
- Series, length, rating y género: el método **reproduce lo que el vendedor manda** en más del 90 % de los casos. Es la parte más sólida del relleno.
- Categoría: cada vendedor usa su propio criterio (taxonomía 1.0 frente a 2.x, `[IAB1-5]` frente a `[IAB1-7]` para lo mismo), así que copiar la de otra ruta solo coincide en la mitad de los casos. **Coincidir con otro vendedor no es lo mismo que acertar**, pero tampoco hay base para afirmar que el valor copiado es correcto.
- contentLength: el 97 % de coincidencia mide consistencia, no verdad. El código 1–8 no es duración (ver `old_reports/08-…`), así que copiarlo es coherente pero no sabemos qué le dice al comprador.

### 2.2 `derivado_genero` en contentCategory, contra la categoría IAB 1.0 que el vendedor sí mandó

| Métrica | Filas | Requests |
|---|---:|---:|
| Filas evaluables (traen género y categoría IAB 1.0) | 223,908 | 151,421,049,296 |
| El mapa solo puede proponer `[IAB1]` genérico (el género no define categoría) | 69.5% | 70.6% |
| Código exacto igual al del vendedor | 44.3% | 27.1% |
| Misma vertical (IAB1 / IAB17 / IAB12…) | 85.2% | 85.8% |

Del tráfico de contentCategory rellenado (371 mil millones de requests), **119 mil millones (32 %) recibían `[IAB1]` genérico**. Es correcto casi siempre, pero dice muy poco. *(Medición antes del afinado de la §3.1, que ahora agrega códigos de género a esas filas cuando tienen título.)*

### 2.3 El match con IMDb: chequeo independiente

El género **no sirve** para auditar el match: la confianza A/B se asigna justamente porque el género de la fila coincide con el de IMDb, así que la comparación es circular. Las validaciones `validar_categorias` y `validar_genero_series` usan esa misma evidencia, por eso no pueden detectar un homónimo. Hay que usar señales que el match no usó.

**Señal 1: el título trae marca de serie** (`S01E03`, "temporada 2", "episodio 4"). Si IMDb dice película, el match es sospechoso.

| Confianza IMDb | Títulos con marca de serie | IMDb dice película / corto | % sospechoso |
|---|---:|---:|---:|
| A (se usa) | 77 | 1 | 1% |
| B (se usa) | 46 | 17 | **37%** |
| C (no se usa) | 40 | 4 | 10% |
| D (no se usa) | 17 | 7 | 41% |

**Señal 2: señales de homónimo** en las filas que hoy usan un valor externo (506,893 filas; 206,307,993,022 requests = 33 % del consolidado):

| Señal | Filas | Requests | % de los requests con valor externo |
|---|---:|---:|---:|
| El match entró por un título alterno o el título original (aka), no por el título principal | 90,557 | 37,427,468,194 | 18% |
| El candidato elegido tiene < 100 votos en IMDb | 199,511 | 70,001,394,080 | 34% |
| Título de una sola palabra | 113,767 | 46,146,489,507 | 22% |
| **Al menos una de las anteriores** | **329,216** | **128,027,354,112** | **62%** |

Por columna (% de los requests rellenados con fuente externa):

| Columna | Requests con valor externo | Confianza A | Confianza B | 2+ candidatos homónimos en IMDb | 10+ candidatos | Candidato con 0 votos |
|---|---:|---:|---:|---:|---:|---:|
| contentCategory (derivado_tipo) | 174,806,606,700 | 55.0% | 45.0% | 45.0% | 19.3% | 12.0% |
| contentSeries (imdb) | 51,213,891,732 | 73.0% | 27.0% | 27.0% | 6.5% | 6.3% |
| contentGenre (imdb) | 8,743,431,816 | 56.4% | 43.6% | 43.6% | 15.6% | 20.7% |
| contentRating (wikidata) | 182,610,441 | 40.0% | 60.0% | 60.0% | 44.7% | 0.0% |

**Homónimos encontrados al revisar** (todos con valores en uso o en el caché):

| Título en el inventario | Match IMDb elegido | Confianza | Problema |
|---|---|:---:|---|
| faded | *Milk Money* (2011, 23 votos) | D | título alterno de otra obra |
| hunter | *Predator* (1987), elegido entre **84 candidatos** | B | título alterno de otra obra, ganó por votos; llena el género accion/aventura/terror |
| ono | *It* (2017) | D | aka en otro idioma |
| adam jones | *Burnt* (2015) | **A** | título de rodaje de otra película; el vendedor lo manda como serie "FMX Stars" |
| rider | *River* (2015) | D | aka |
| travel | *Yatra* (2018) | D | aka en hindi |
| wrath | *Delirium* (2023) | B | aka |
| diary of a lunatic | *Trew Calling* (2017) | B | aka |
| the next dance | *Nearly Forgotten* (2013, corto, 0 votos) | B | aka |
| hasta que el dinero nos separe (ViX) | *Until Money Do Us Part* (Colombia, 2006; título original "Hasta que la plata nos separe") | B | **remake de telenovela**: IMDb tiene también la versión de Televisa (2009) cuyo título es **exactamente** "Hasta que el dinero nos separe", pero perdió contra la colombiana, que coincide solo por un aka y tiene más votos |
| cain (part 3) | *Caïn* (2012, serie francesa), elegido entre 34 candidatos | B | probable homónimo |
| news | *News* (2009, película) | B | el vendedor la manda como serie "Euronews News" |

### 2.4 Otros problemas encontrados

| # | Problema | Efecto | Evidencia |
|---:|---|---|---|
| 1 | El rating de Wikidata es la **clasificación RTC de México** (`B15`, `AA`, `B`, `C`) y se aplica a filas de **todos los países** | 535 de las 1,001 filas rellenadas por Wikidata no son de México (Argentina 180, Chile 111, Colombia 72, Perú 69…) | `rating_wikidata_por_pais` |
| 2 | contentSeries se llena con el **título principal de IMDb, que suele estar en inglés** | "Amores verdaderos" → `True Love`, "Hasta que el dinero nos separe" → `Until Money Do Us Part` | muestra de revisión |
| 3 | El caché **nunca reevalúa** un match: el título que se emparejó en v15 conserva ese match en v22 aunque IMDb haya agregado candidatos o se corrija la regla | errores fijos que se arrastran de tanda en tanda | `actualizado` en `titulos.json` |
| 4 | La precisión por nivel (A ≈ 90 %, B ≈ 75 %) **no es reproducible**: la muestra auditada a mano en v15 no se guardó | no hay cómo defender la cifra ante un tercero | `old_reports/08-…` |
| 5 | Confianza B se gana con coincidir en **un** género amplio (drama, comedia), que comparten miles de obras | B es un desempate débil; las marcas de serie dan 37 % de sospechosos en B | §2.3 |
| 6 | Homónimos **entre publishers** en `intra_titulo`: 70 títulos tienen dos publishers con géneros sin ningún punto en común (p. ej. "eve": terror en Select Plus, drama en Televisa) | 11,180 filas de contentLength, 3,071 de series y 1,636 de categoría se llenaron copiando desde esos títulos | `homonimos_intra` |
| 7 | **Licencias:** los IMDb Non-Commercial Datasets son solo para uso personal y no comercial; TMDB exige un contrato para uso comercial | si el relleno alimenta un producto de Tagscreen, el uso de IMDb hay que revisarlo con legal **antes** de escalar | términos de IMDb / TMDB |

---

## 3. Confiabilidad × utilidad por columna (recomendación)

| Columna · origen | Confiabilidad medida | Utilidad para el comprador | Recomendación |
|---|---|---|---|
| contentSeries · intra_titulo | 99% (enmascaramiento) | alta | **Mantener** |
| contentRating · intra_titulo | 92% filas / 98% req | alta | **Mantener**; agregar el país al candado (el rating es por país) |
| contentGenre · intra_titulo | 92% exacto | media-alta | **Mantener** |
| contentLength · intra_titulo | 97% de consistencia, significado desconocido | baja mientras no se sepa qué es el código | **Condicionar**: confirmar la definición con PubMatic; mientras tanto entregar `ext_runtime_min` (minutos reales) |
| contentIsLiveStream · app_semantica | revisada a mano por app | alta | **Mantener** |
| contentCategory · intra_titulo | 50% exacto / 70% vertical frente a otro vendedor | media | **Condicionar**: copiar solo la vertical o solo entre rutas con la misma taxonomía |
| contentCategory · derivado_genero (específico) | 85% vertical | media | **Mantener** |
| contentCategory · derivado_genero (`[IAB1]` genérico) | correcto pero vacío de información | baja | **Afinado** con códigos de género cuando hay título (§3.1); sin título, marcarlo como genérico en los % de completitud |
| contentCategory · derivado_tipo | depende del match; 62% del tráfico con alertas | alta si es correcto (película frente a serie) | **Condicionar** a la revisión manual y a la segunda fuente (§4–§6) |
| contentSeries · imdb | depende del match; nombre en inglés | alta si es correcto | **Corregir**: usar el título original o el aka es-MX, y exigir marca de serie o un segundo ID |
| contentGenre · imdb | depende del match (circular) | media | **Condicionar** a la segunda fuente |
| contentRating · wikidata | RTC México aplicado a otros países | baja | **Retirar fuera de México** (o mapear por país con TMDB) |

### 3.1 Categoría genérica afinada con códigos de género (aplicado el 2026-10-01)

El 93 % de las filas con categoría rellenada había quedado con un código genérico: `[IAB1]` Arte y entretenimiento, `[IAB1-5]` Películas o `[IAB1-7]` Televisión. IAB 1.0 no tiene nada más fino para cine y TV; los códigos por género están en IAB 2.2 (Películas › Drama = `333`, Televisión › Comedia = `646`, Telenovelas = `642`…). Ahora `enriquecer_externo.py` **conserva el código genérico y le agrega hasta 3 códigos de género de IAB 2.2**, por ejemplo `[IAB1-5]` → `[IAB1-5, 333, 331]`. Solo se aplica a filas con título cuya categoría fue rellenada; lo que mandó el vendedor no se toca. El género sale primero del contentGenre de la propia fila (lo declara el vendedor para esa ruta, sin riesgo de homónimo) y, si no trae uno comparable, de IMDb/Wikidata. El origen queda en `contentCategory_afinado_origen`.

| Fuente del género agregado | % de filas del consolidado | Requests | Coincide con IMDb/Wikidata (validación del relleno) | Contradice |
|---|---:|---:|---:|---:|
| Género declarado por el vendedor | 47.9% | 221,250,857,629 | 81.6% | 18.4% |
| Géneros IMDb (match A/B) | 3.6% | 11,302,712,662 | 99.9% (circular: se valida contra la misma fuente) | 0.1% |
| Géneros Wikidata | 0.0% | 7,580,705 | 100% | 0% |

Efecto sobre contentCategory rellenada (validación `validacion-categorias-relleno.json`, % de requests): coincide con la evidencia **41.3 % → 58.0 %**, genérica sin contradecir 44.6 % → 20.4 %, contradice **4.7 % → 12.2 %**.

Las contradicciones nuevas son casi todas parciales: el vendedor declara "drama; romance" e IMDb solo "Drama", así que `333` Películas de drama coincide y `326` Películas románticas no. También aparecen cuando el género declarado choca con IMDb ("terror" contra "Thriller"), y ahí puede estar mal cualquiera de los dos, o ser un homónimo. Por eso la revisión manual juzga **cada código por separado**. Si la revisión muestra que los códigos sacados del género declarado bajan la precisión, la alternativa es agregar solo los géneros en los que coinciden el vendedor e IMDb.

Advertencia técnica: la lista mezcla taxonomías (1.0 y 2.2). Varios vendedores ya lo hacen, pero OpenRTB declara una sola taxonomía por objeto (`cattax`). Si este dato se fuera a enviar en un bid request, habría que separar los códigos 2.2 y declarar `cattax = 2`.

---

## 4. Otras bases para contrastar

Cobertura medida en Wikidata sobre los 6,458 IDs IMDb de confianza A/B (4,059 tienen ficha en Wikidata):

| Propiedad Wikidata | IDs A/B con dato | Para qué sirve |
|---|---:|---|
| País de origen (P495) | 62.0% | candado de homónimos: una telenovela mexicana frente a la versión colombiana |
| Género (P136) | 53.3% | segunda opinión del género (independiente del match si se cruza por ID) |
| Idioma original (P364) | 52.7% | candado de homónimos (no sirve para rellenar el idioma de emisión) |
| **ID TMDB película (P4947)** | **51.1%** | **cruce con TMDB por ID, sin buscar por título** |
| Fecha de estreno (P577) | 47.1% | candado: año |
| Director (P57) / reparto (P161) | 46.6% / 44.4% | revisión manual; desambiguación |
| Duración (P2047) | 43.0% | runtime, segunda opinión |
| Productora (P272) | 20.8% | `content.producer` |
| ID TMDB serie (P4983) | 11.3% | cruce por ID |
| Cadena original (P449) | 11.2% | `content.network` |
| ID TheTVDB (P4835) | 10.4% | cruce por ID para series |
| Núm. de episodios / temporadas | 10.3% / 7.3% | validar que es serie |
| Clasificación MPA (EE. UU.) / ClassInd (Brasil) / RTC (México) | 4.5% / 4.5% / 3.1% | rating: cobertura muy baja |

| Base | Qué aporta | Cómo cruzar sin homónimos | Licencia / costo | Recomendación |
|---|---|---|---|---|
| **TMDB** | géneros, tipo, año, idioma original, **certificaciones por país** (MX, CO, CL, AR, BR), títulos alternos por país, temporadas y episodios, palabras clave, productoras y cadenas | `/find/{imdb_id}?external_source=imdb_id`: va por ID, no por título | API key gratis solo para uso no comercial; uso comercial con contrato | **Primera opción** como segunda fuente y para el rating por país |
| **Wikidata** | lo de la tabla de arriba | SPARQL por P345 (IMDb ID), como ya hace el pipeline | CC0, sin restricciones | **Ampliar** la consulta actual (hoy solo pide idioma, duración, género y rating) |
| **TVMaze** | series: cadena, país, idioma, episodios con temporada/número | `/lookup/shows?imdb={id}` (por ID) | CC BY-SA, comercial permitido con atribución | **Activar `--tvmaze`** para series; hoy está apagado (0 títulos en el caché) |
| **OMDb** | `Rated` (escala de EE. UU.), runtime, premios | por IMDb ID | API key; revisar los términos de su licencia antes de usarla comercialmente | Opcional, solo como tercera opinión |
| **Organismos de clasificación** (RTC México, ClassInd Brasil, CCC Chile, Argentina) | rating oficial por país | por título + año (sin ID): solo como verificación manual | públicos; sin API estable | Para la revisión manual del rating |
| **EIDR / Gracenote (Nielsen)** | ID estándar de la obra y del episodio, metadata de la industria | por ID que mande el vendedor | membresía / comercial | Solución de fondo si esto pasa a producto |
| **Los propios vendedores** (OTTera, TCL, Vidaa, ViX) | el dato de origen: `content.id`, serie, temporada, episodio | su feed de catálogo (MRSS/JSON) | acuerdo comercial | **La única certeza real**; OTTera/TCL concentran la mayoría de las filas vacías |

Regla para que el contraste sea válido: **la segunda fuente se consulta por el ID** (IMDb → TMDB/Wikidata/TVMaze), nunca volviendo a buscar el título. Si se busca de nuevo por título, la segunda fuente repite el mismo homónimo y "confirma" el error.

---

## 5. Cómo cuidarse de series y películas homónimas

Candados propuestos, del más rendidor al menos. Todos son cambios a `enriquecer_externo.py` (no aplicados todavía).

| # | Candado | Qué evita | Costo |
|---:|---|---|---|
| 0 | **Preferir el match por título principal u original sobre el match por aka**: hoy se elige por género y votos sin mirar por dónde entró el candidato | "hasta que el dinero nos separe": la versión de Televisa 2009 coincide exacto y perdió contra un aka | bajo |
| 1 | **Matches por aka**: aceptarlos solo si el aka es de una región LATAM/ES (MX, AR, CO, CL, ES…) o en español/portugués, y no si es un aka en inglés o en otra lengua | "hunter" → *Predator*, "ono" → *It*, "travel" → *Yatra* | bajo (el dato ya está en `title.akas`) |
| 2 | **Margen frente al segundo candidato**: con 2+ candidatos, exigir que el elegido tenga ≥ 10× los votos del siguiente o que coincida en tipo con las marcas del título; si no, no usar | títulos de una palabra (`broken`, `eve`, `rain`) | bajo |
| 3 | **Coherencia de tipo**: si el título trae marca de serie o 2+ rutas declaran serie, descartar un match a película/corto | el 37 % de sospechosos en B | bajo |
| 4 | **Piso de popularidad**: con 0 votos, no rellenar (salvo candidato único directo) | cortos y videos oscuros que comparten nombre | bajo |
| 5 | **País y año** (Wikidata P495/P577 o TMDB): para títulos de ViX/Televisa/Canela preferir país de origen MX/ES-LATAM; ante remakes, elegir la versión más reciente cuyo país coincida con el emisor | remakes de telenovela (versión colombiana frente a la mexicana) | medio (requiere la consulta ampliada de Wikidata o TMDB) |
| 6 | **Segunda fuente por ID**: rellenar tipo, género o serie solo si IMDb y (TMDB o Wikidata o TVMaze) coinciden | cualquier error del match IMDb | medio |
| 7 | **Ámbito de `intra_titulo`**: no copiar entre publishers cuyos géneros declarados para ese título son disjuntos (la señal de la §2.4 #6) | "eve" de Select Plus frente a la telenovela de Televisa | bajo |
| 8 | **Lista curada** `cache-enriquecimiento/titulos_revisados.csv` (titulo_clave, imdb_id correcto o "ninguno", veredicto, revisor, fecha), con la misma lógica de `aplicar` que `semantica_apps.csv`: lo revisado a mano manda sobre cualquier regla | errores conocidos que no vuelven | bajo; se alimenta de la revisión manual (§6) |
| 9 | **Reevaluar el caché** en cada tanda con las reglas vigentes (guardar candidatos, no solo el elegido) | errores antiguos que se arrastran | bajo |
| 10 | Pedir a los vendedores `content.id` (EIDR/Gracenote) | el problema completo | negociación |

---

## 6. Pipeline de revisión manual

La revisión se hace en una página web local, sin instalar nada: `recursos/revision-manual-v22.html` (doble clic para abrirla).

```
# 1. sortear la muestra y generar la pagina (500 filas reales del inventario)
python scripts/generar_muestra_revision.py inventory-consolidado-v10-a-v22-relleno.csv \
    reportes/25-auditoria-relleno-v22/recursos/revision-manual-v22 --registros 500 --semilla 22
# 2. revisar en recursos/revision-manual-v22.html y pulsar "Exportar revision" (descarga un JSON)
# 3. precision por campo y metodo con IC 95% (acepta los JSON de varios revisores)
python scripts/calcular_precision_revision.py revision-manual-v22-<revisor>-<fecha>.json [otro.json ...]
```

**Qué muestra la página:** cada tarjeta es una fila real del inventario (título, app, publisher, país, requests) con **todos** sus content objects. Los valores que llenamos de más van en naranja con la etiqueta LLENADO. Los que mandó el vendedor van en neutro, como contexto. Debajo de cada código va su significado: categorías IAB 1.0, 2.2 y 3.0 traducidas al español con el nombre oficial; clasificaciones por edad de EE. UU., la escala nueva del reporte, la RTC de México y otras; livestream 1/0; y el código de duración con los minutos reales si se conocen. El revisor **no ve el método** con que se llenó cada valor: el script lo guarda aparte para calcular la precisión por método. Hay botones para buscar el título con la app en Google y la ficha IMDb de referencia, filtros (pendientes, por campo, búsqueda) y "ir al siguiente pendiente". El avance se guarda en el navegador; **el registro oficial es el JSON exportado**, que también se puede importar para seguir otro día o en otra computadora.

**Veredicto por valor:** cuando un campo llenado trae varios valores (varios códigos de categoría o una lista de géneros), cada uno se juzga por separado. Los códigos de género que se agregaron a una categoría genérica (§3.1) llevan la marca MÁS ESPECÍFICO.

**Información extra:** las tarjetas en las que algún valor salió de IMDb o Wikidata traen un apartado plegable, solo de referencia (no llena ninguna columna): título en IMDb y original, tipo, años, duración, géneros, calificación IMDb con votos, y desde Wikidata país de origen, idioma original, estreno, dirección, reparto, productora, cadena, temporadas, episodios e IDs de TMDB. Incluye una pregunta opcional, "¿esta ficha es la misma obra que emite la app?", que mide directamente los homónimos.

**Muestra:** 500 filas, **todas con título** (sin título un humano no puede verificar nada), una por título, elegidas con probabilidad proporcional a requests y con cuotas para que cada campo y método quede representado. En total hay 1,770 valores a revisar (426 de ellos son códigos más específicos agregados) y 264 tarjetas con información extra. Por campo y método (una fila puede contar en varios):

| Campo | Método (no visible para el revisor) | Filas de la muestra con ese valor llenado | Filas del consolidado | Requests del consolidado |
|---|---|---:|---:|---:|
| Duración (código) | copiado de otra ruta del mismo título | 224 | 495,062 | 190,820,974,605 |
| Categoría | tipo película/serie de IMDb | 172 | 451,312 | 174,806,606,700 |
| Categoría (código más específico) | género declarado por el vendedor | 170 | 644,442 | 221,250,857,629 |
| Categoría | copiado de otra ruta del mismo título | 103 | 155,345 | 39,516,678,850 |
| Categoría (código más específico) | IMDb | 100 | 49,063 | 11,302,712,662 |
| Categoría | derivado del género | 96 | 349,587 | 157,021,985,057 |
| Serie | IMDb | 96 | 93,342 | 51,213,891,732 |
| Género | IMDb | 95 | 31,144 | 8,743,431,816 |
| Género | copiado de otra ruta del mismo título | 87 | 48,792 | 16,068,252,622 |
| Clasificación por edad | copiado de otra ruta del mismo título | 87 | 94,263 | 24,215,380,363 |
| En vivo / lineal | semántica de la app | 80 | 257,756 | 103,129,609,151 |
| Serie | copiado de otra ruta del mismo título | 78 | 9,481 | 3,436,052,935 |
| Clasificación por edad | Wikidata | 52 | 987 | 182,610,441 |
| Categoría (código más específico) | Wikidata | 1 | 72 | 7,580,705 |

**Protocolo de revisión:**

| Paso | Regla |
|---|---|
| Qué se juzga | Si el **valor llenado** es correcto para **lo que esa app emite con ese título**. Ejemplo: `[IAB1-5]` Películas para un título que en MovieArk es una película → correcto. |
| Veredicto | `Correcto` · `Incorrecto` (anotar el valor correcto si se sabe) · `No se sabe` (no hay forma de verificar; **no** cuenta como correcto). |
| Duración (código) | El código 1–8 no tiene una equivalencia confirmada. Si no hay forma de juzgarlo, marcar `No se sabe`. Una tasa alta de "no se sabe" en este campo es en sí misma el hallazgo. |
| Doble revisión | Un 10 % de las tarjetas revisado por una segunda persona, sin ver el primer veredicto (cada uno exporta su JSON). El script reporta el acuerdo; si es < 85 %, ajustar las reglas antes de seguir. |
| Tamaño | Con unos 50–100 valores por método, el margen es de ±7–12 puntos (IC 95 %). Para afirmar "≥ 90 %" con ±5 puntos hacen falta ~140 por método: regenerar con más `--registros` solo si un método queda cerca del umbral. Con 1–2 minutos por tarjeta, la ronda completa son ~8–16 horas-persona. |
| Umbral de uso (propuesta) | Un método se usa en producción si el **límite inferior** del IC 95 % de su precisión es ≥ 85 %; si no, se apaga o se le agrega un candado de la §5 y se vuelve a medir. |
| Cierre del ciclo | `calcular_precision_revision.py` escribe `revision-incorrectos.csv`; esos valores pasan a `titulos_revisados.csv` (candado 8) y la tanda siguiente ya no repite el error. Se versionan los JSON exportados: son la evidencia de la cifra de precisión. |

---

## 7. Qué más se puede llenar con bases externas

Campos del objeto `content` de OpenRTB 2.6 que hoy no trae el reporte (o trae vacíos) y su techo de cobertura. Techo: % de filas / requests del consolidado que tienen el insumo (match IMDb A/B: 48.5 % de las filas, 38.1 % de los requests; título real: 86.4 % / 60.9 %).

| Campo OpenRTB 2.6 | Fuente | Techo (filas / requests) | Comentario |
|---|---|---|---|
| `season` / `episode` | el propio título (`S01E03`, "temporada 2"); TVMaze/TMDB por ID | 5.3% / 3.4% desde el título | sin riesgo de homónimo cuando sale del título; `validar_genero_series` ya lo detecta |
| `len` (segundos) | runtime IMDb/Wikidata/TMDB | 41.8% / 32.7% (`ext_runtime_min` ya existe) | más útil que el código 1–8 de contentLength |
| `contentrating` por país | TMDB certificaciones (MX, CO, CL, AR, BR) | ≤ 38.1% de requests (match A/B) × cobertura TMDB | la única forma seria de dar rating por país; requiere licencia |
| `userrating` | IMDb averageRating | 42.4% / 33.8% (votos > 0) | IMDb no comercial: revisar la licencia |
| `producer.name` | Wikidata P272 / TMDB | ~20.8% de los IDs A/B | |
| `network.name` (2.6) | Wikidata P449 / TVMaze / TMDB | ~11.2% de los IDs A/B (series) | útil para separar Televisa, Caracol, RCN… |
| `genres` + `gtax` (2.6) | IMDb/Wikidata/TMDB mapeados a IAB 3.0 o Gracenote | ≤ 38.1% de requests | permite declarar la taxonomía en vez de texto libre |
| `cat` + `cattax` en IAB 3.0 | taxonomía oficial (ya descargada) | el mismo que contentCategory | declara la versión: hoy conviven 1.0 y 2.x sin `cattax` |
| `ext.anio_estreno`, `ext.pais_origen` | IMDb startYear / Wikidata P495 | 47.9% / 37.6% (año) | no están en OpenRTB; útiles para Looker y para el candado de homónimos |
| `ext.idioma_original` | Wikidata P364 / TMDB | ~52.7% de los IDs A/B | **no** reemplaza contentLanguage (idioma de emisión) |
| `id` (EIDR/Gracenote) | vendedores / Gracenote | — | resolvería los homónimos de raíz |

---

## 8. Plan recomendado

| Paso | Qué | Quién | Esfuerzo |
|---:|---|---|---|
| 1 | Revisar con legal el uso de IMDb (no comercial) y decidir la licencia TMDB | negocio / legal | — |
| 2 | Revisión manual de la muestra v22 (500 tarjetas en `revision-manual-v22.html`) con doble revisión del 10 % | analista | 8–16 h |
| 3 | Aplicar los candados baratos de la §5 (1, 2, 3, 4, 7, 8, 9) y retirar el rating Wikidata fuera de México; nombre de serie en título original o aka es-MX | pipeline | 1 día |
| 4 | Segunda fuente por ID (Wikidata ampliado + TVMaze, y TMDB si hay licencia) y regla de "dos fuentes coinciden" | pipeline | 2–3 días |
| 5 | Volver a medir: enmascaramiento + nueva muestra con los candados → precisión por estrato con IC | pipeline + analista | 1 día + revisión |
| 6 | Dejar de contar `[IAB1]` genérico y el código de contentLength como "lleno" en los % de completitud hasta definir su utilidad | reporte | bajo |
| 7 | Pedir `content.id`, serie, temporada y episodio a OTTera/TCL/Vidaa/ViX | comercial | — |

---

**Archivos de esta carpeta**

| Archivo | Contenido |
|---|---|
| `recursos/auditoria-relleno-v22.json` | origen, enmascaramiento, chequeo de tipo IMDb, riesgo externo, homónimos entre publishers, rating por país (`scripts/auditar_relleno.py`) |
| `recursos/cobertura-wikidata-propiedades.json` | cobertura de cada propiedad Wikidata sobre los IDs IMDb A/B |
| `recursos/revision-manual-v22.html` | página de revisión manual (500 filas, abrir con doble clic) |
| `recursos/revision-manual-v22.json` | los mismos registros con el método de cada valor y los totales por estrato, para extrapolar la precisión |
