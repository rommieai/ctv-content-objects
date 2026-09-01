# Reporte — ¿Qué columnas vacías se pueden rellenar con fuentes abiertas, y en qué porcentaje?

**Fuente:** `inventory-consolidado-v10-a-v15-enriquecido.csv` — 648,589 filas, 385,830,361,280 requests (métricas del corte v15).
**Generado con:** `scripts/enriquecer_externo.py` → `inventory-consolidado-v10-a-v15-relleno.csv` + `reporte-relleno-v15.json`. Las pruebas empíricas de este reporte (IMDb, TVMaze, Wikidata) se corrieron el 1 sep 2026.

La pregunta era doble: (1) de las columnas con alto % de N/A, ¿cuántas filas podríamos llenar sacando la info de fuentes abiertas (IMDb, TMDB, Wikidata, TVMaze…) o de los catálogos de las propias apps?, y (2) ¿se puede dejar eso como un pipeline que corra solo con cada tanda nueva? Respuesta corta: **sí a las dos, pero con dos sorpresas que cambian el planteamiento** — la mitad del relleno no necesita ninguna fuente externa (el mismo consolidado ya trae el dato en otra fila del mismo título), y dos de las columnas "vacías" (`contentLength`, `contentIsLiveStream`) no significan lo que parecen, así que llenarlas desde afuera es llenar un campo que ya está roto.

---

## 1. Punto de partida: qué está vacío y qué llave tenemos para buscarlo

Todo relleno externo depende de una sola cosa: **tener un título real con el cual buscar**. Por eso lo primero fue medir cuántas filas vacías traen un título usable (según la auditoría del reporte de género/título: sin placeholders, slugs, canales ni macros).

| Columna | % filas vacías | % requests vacíos | De las vacías, % con título real (buscable) |
|---|---:|---:|---:|
| contentSeries | **93.9%** | 93.1% | 86.6% |
| contentLength | **88.3%** | 75.2% | 90.6% |
| contentCategory | **77.0%** | 67.7% | 89.4% |
| contentIsLiveStream | **71.3%** | 61.1% | 86.3% |
| contentLanguage | 22.8% | 17.5% | 90.3% |
| contentRating | 16.1% | 12.1% | 87.4% |
| contentTitle | 8.2% | 25.3% | — (no hay llave) |
| contentGenre | 1.2% | 7.6% | 35.5% |

Dos lecturas:

- **La llave existe casi siempre.** 562,443 filas (86.7%) traen un título de verdad; son **18,374 títulos distintos**, que tras normalizar (url-decode, quitar `: trailer`, `temporada N`, `episodio N`, `SxxEyy`, acentos, mojibake) bajan a **14,122 claves**. Y están muy concentrados: los 1,000 títulos más frecuentes cubren 53% de las filas con título; los 5,000 primeros, 90%. Buscar 14 mil títulos una sola vez es barato — el costo no está en el volumen sino en la precisión.
- **Lo que no tiene título no se puede rellenar desde afuera**: el 8.2% de filas sin título (25% de los requests: los `epg`/`roku` de Roku, Pluto, Tubi, Vidaa) queda fuera de cualquier lookup. Eso solo lo arregla el vendedor.

## 2. Primera sorpresa: el consolidado se rellena a sí mismo

Antes de ir a fuentes externas probamos lo obvio: si el título `hatchback` trae `contentLanguage=en` y `contentRating=tv-14` en unas filas y `Not Available` en otras, la fila vacía se puede rellenar con lo que dicen sus hermanas. Resultado (filas vacías que tienen el mismo título con dato en otra fila):

| Columna | % de las vacías rellenables intra-dataset | % de requests vacíos | Ambigüedad (título con >1 valor) |
|---|---:|---:|---:|
| contentCategory | 85.8% | 69.1% | alta (89%): distintos SSP mandan distinto IAB para el mismo título |
| contentLanguage | 89.1% | 69.9% | alta (87%): `en` y `es` para el mismo título (pista de audio doblada) |
| contentIsLiveStream | 83.6% | 70.3% | ninguna — pero ver §4 |
| contentRating | 84.3% | 37.6% | media (61%): `tv-14` vs `movie-pg-13` (sistemas distintos, misma franja) |
| contentLength | 45.3% | 46.6% | media (24%) |
| contentSeries | 5.0% | 5.2% | baja |
| contentGenre | 29.9% | 2.2% | alta |

La ambigüedad no es ruido: en `contentLanguage` es información (MovieArk sirve el mismo catálogo con audio `en` y `es`), y en `contentRating` desaparece si se compara por franja (`rating_franja`) en vez de por código. El pipeline aplica esta propagación **solo cuando el valor dominante cubre ≥ 80% de las filas con dato de ese título** (configurable), y marca el origen como `intra_titulo`.

Complemento: **defaults por app** — cuando una app manda un valor constante (≥ 95%) siempre que lo manda: ViX siempre `es` y length `8`, Vidaa siempre `[IAB12]`, OTTera/MovieArk `[IAB1]`, PML `[sports]`. Cubre 93k vacías de categoría y 172k de length. Se marca `app_default`.

## 3. Fuentes abiertas: qué se probó, qué da y con qué licencia

| Fuente | Qué aporta | Cobertura medida sobre nuestros títulos | Licencia / límite | Veredicto |
|---|---|---|---|---|
| **IMDb Non-Commercial Datasets** (`title.basics`, `title.akas`, `title.ratings`, `title.episode`; ~750 MB, refresco diario) | tipo (movie / tvSeries / short…), año, **runtime en minutos**, géneros IMDb, título canónico, títulos locales es/pt | **50.7% de las 14,122 claves = 63.1% de las filas con título = 67.3% de los requests**. Top-100 títulos: 92%; top-1000: 69%. | Solo uso **personal / no comercial**; prohíbe construir una base de datos de películas con ellos. Sin API key, offline. | La mejor relación cobertura/costo para *analizar*. Para un producto comercial hay que licenciar (IMDb Essential Metadata) o cambiar a TMDB Business. |
| **Wikidata** (SPARQL por IMDb id, P345) | idioma original (P364), duración (P2047), género (P136), clasificación (P3834) | De los títulos con IMDb: 58% están en Wikidata; **50% traen idioma original, 44% duración, 52% género; clasificación solo 2%** (pero en escala mexicana RTC: `B`, `B15`). | CC0, sin key, ~1 req/s con User-Agent. | Complemento gratis y comercialmente limpio para idioma y duración. Búsqueda por texto (sin IMDb id) da 30–32%. |
| **TVMaze** (`/search/shows`) | idioma, géneros, runtime, red — solo series | **12.5% (top) / 13% (aleatorio)**: el catálogo es mayoritariamente película. | CC BY-SA 4.0, sin key, 20 req/10 s; licencia comercial a pedido. | Útil solo para el ~15% de series; barato de mantener. |
| **TMDB** | géneros, runtime, idioma original, **content ratings por país** (MX/AR/CO…), episodios→serie, títulos alternos | No probado (requiere API key; cobertura esperada ≈ IMDb) | Gratis solo no comercial; **prohíbe uso en ML/AI**; "API for Business" con contrato. | La única abierta con clasificación por país. Vale pedir key para medir; para uso comercial, contrato. |
| **OMDb** | `Rated` (MPAA/TV), runtime, género, idioma (vía IMDb) | No probado (requiere key) | 1,000 req/día gratis; Patreon desde 1 USD/mes → 100k/día | Atajo práctico para `contentRating` si se acepta escala US. |
| **JustWatch** | disponibilidad por país/plataforma | — | Solo partners; el GraphQL público es no oficial | No para un pipeline estable. |
| **Catálogos de las apps** (Tubi, Pluto, Roku Channel, ViX) | metadata oficial del ítem que se está sirviendo | Tubi: solo navegación por categoría, sin búsqueda; Pluto: API con token de sesión; Roku: solo web. | ToS de cada uno; scraping. | Roku/Pluto/Tubi son justo los que **no mandan título** → no hay qué buscar. No compensa. |
| **OTTera / TCL** (MovieArk, Live TV, TCL Channel, BrowseHere) | son la plataforma detrás del **60% de las vacías** | Sin API pública. | — | El camino correcto es **pedirles el feed de catálogo** (MRSS/JSON): un solo proveedor cubre más que todas las fuentes abiertas juntas. |
| **Gracenote Content Connect** (Nielsen) | 50M+ títulos, IDs estándar, integrado en PubMatic / The Trade Desk | — | Comercial | La solución "de industria" si esto pasa de análisis a producto. |

**Precisión del match IMDb** (auditada a mano sobre muestras por nivel):

| Nivel | Regla | % de filas con título | Precisión estimada |
|---|---|---:|---:|
| A | candidato único y género compatible (o sin género en la fila) | 30.2% | ~90%+ |
| B | varios candidatos, elegido por coincidencia de género con `genero_normalizado` | 20.8% | ~75% (falla en títulos de una palabra: `broken`, `caribe`, `collider`) |
| C | candidato único pero género distinto | 3.1% | ~60% |
| D | varios candidatos sin apoyo de género (se elige por votos) | 9.0% | ~50% (`eve` → *All About Eve*) |

El pipeline usa por defecto solo A+B (`--confianza-min B`): **51% de las filas con título** con precisión ~85%. Todo match se reporta (`ext_imdb_id`, `ext_confianza`) aunque no se use.

**Qué es lo que IMDb no encuentra** (49% de las claves, 37% de las filas): catálogo indie/corto de OTTera sin ficha (`purple pin`, `sinners blood`), podcasts y shows (`joel osteen podcast`, `the daily show ears edition`, 6% de las filas sin match), canales FAST que llegan como título (`golden edge`, `goal tv`, `entrepreneur tv`), infantil tipo YouTube (`babybus`, `boonie bears`), y 1,843 claves que aparecen una sola vez. El % de match es parejo entre apps (58–64%) salvo Coolita Channel (38%).

## 4. Segunda sorpresa: dos columnas "vacías" no significan lo que parecen

Al cruzar los matches de IMDb con lo que las filas *sí* traen:

- **`contentLength` no es duración.** Sus valores son códigos 1–8 y, comparados con el runtime de IMDb del mismo título, **todos los códigos tienen mediana de 60–95 minutos** (código 4: mediana 89 min; código 8: 60 min; código 6: 93 min). Es un enum del reporte o del vendedor cuya definición no tenemos. Rellenarlo desde afuera sería inventar códigos. Lo que sí se puede entregar es **`ext_runtime_min` (minutos reales)** para el 45% de las filas con título — más útil que el código.
- **`contentIsLiveStream` declarado es siempre `1`.** El 100% de las filas que traen valor dicen `1`, incluidas 62,683 filas de títulos que IMDb clasifica como `movie`. Importante: la columna mide el **modo de entrega** (lineal/en vivo vs on-demand), no el tipo de contenido — una película vieja emitida en un canal lineal FAST va programada en horario y es legítimamente `livestream=1`. Así que el `1` masivo puede ser en parte real (mucho de este inventario es FAST lineal) y en parte default del vendedor; **con la metadata disponible no se pueden distinguir por fila**. La unidad correcta es la **app**: el modo de entrega es una propiedad del servicio, y se puede validar sin VPN con la ficha pública de cada app (la descripción de Google Play/Roku es global, no depende del país del catálogo). Esa validación vive en `cache-enriquecimiento/semantica_apps.csv` — bundle, veredicto (`lineal`/`vod`/`mixto`/`desconocido`), evidencia citada, fuente y columna `aplicar` para el visto bueno humano; el pipeline solo usa las filas con `aplicar=si` (lineal→`1`, vod→`0`, mixto/desconocido nunca rellenan). Ni la propagación del declarado ni la inferencia por tipo IMDb se usan por defecto (`--intra-livestream`, `--livestream-desde-tipo` las reactivan bajo responsabilidad del analista).

Consecuencia práctica: de las siete columnas con N/A alto, **cinco se rellenan de verdad** (category, language, rating, series, genre) y dos (**length, livestream**) primero hay que redefinirlas con el vendedor.

## 5. Resultado del pipeline sobre el consolidado v10–v15

Corrida completa (`--wikidata`, `--confianza-min B`, sin TVMaze): 14,073 títulos consultados, 7,124 con match IMDb (50.6%); 47.9% de las filas quedan con un IMDb id de nivel A o B y **41.5% con duración real en minutos** (`ext_runtime_min`).

**Global — % de filas con dato (y % de requests):**

| Columna | Antes (filas) | Después (filas) | Antes (requests) | Después (requests) | De dónde sale lo nuevo |
|---|---:|---:|---:|---:|---|
| contentCategory | 23.0% | **95.2%** | 32.3% | 86.9% | derivado del tipo IMDb 26.4 · derivado del género 25.7 · intra 12.0 · app 8.1 |
| contentLanguage | 77.2% | **97.4%** | 82.5% | 96.3% | intra 19.6 · app 0.3 · wikidata 0.2 |
| contentIsLiveStream | 28.7% | **48.9%** | 38.9% | 53.1% | semántica de la app (validada a mano) 19.7 · señales del vendedor en contentSeries 0.5 |
| contentRating | 83.9% | **90.5%** | 87.9% | 92.1% | intra 6.4 · app 0.2 |
| contentLength | 11.7% | 50.1% | 24.8% | 59.5% | intra 32.4 · app 6.0 — *solo el código del vendedor; ver §4* |
| contentSeries | 6.1% | 14.6% | 6.9% | 16.4% | imdb 6.6 (tipo tvSeries → título canónico) · intra 1.9 |
| contentGenre | 98.8% | 99.1% | 92.4% | 92.6% | app 0.2 · imdb 0.1 |

**Por país (% de filas con dato, antes → después):**

| Columna | México | Colombia | Chile | Argentina |
|---|---:|---:|---:|---:|
| contentCategory | 25.3 → **90.3** | 23.5 → **96.8** | 15.3 → **98.0** | 11.3 → **97.2** |
| contentLanguage | 75.9 → **96.6** | 62.2 → **96.7** | 73.1 → **97.5** | 72.8 → **97.9** |
| contentIsLiveStream | 26.3 → **43.7** | 26.3 → **50.4** | 17.0 → **49.5** | 29.4 → **51.1** |
| contentRating | 82.6 → 89.0 | 79.9 → 88.5 | 82.9 → 88.1 | 87.1 → 91.2 |
| contentLength | 17.0 → 52.3 | 10.1 → 54.1 | 7.7 → 44.5 | 4.9 → 39.1 |
| contentSeries | 7.0 → 17.4 | 6.1 → 13.7 | 5.0 → 12.4 | 2.9 → 11.3 |

Lectura por columna:

- **contentCategory y contentLanguage se resuelven casi por completo (95–97%)** y sin fuente externa dudosa: categoría se deriva del género que ya viene en el 99% de las filas (más el tipo IMDb para separar `[IAB1-5]` película de `[IAB1-7]` televisión), idioma se propaga del mismo título. Es el relleno de mayor confianza.
- **contentIsLiveStream pasa a 48.9%, con solo fuentes defendibles**: 0.5% por señales de entrega explícitas del vendedor (3,171 filas → `0` por `contentSeries=VOD`; 62 → `1` por `... Livestream`) y **19.7% por la semántica de la app validada a mano** (`cache-enriquecimiento/semantica_apps.csv`): las apps cuya ficha pública describe un servicio 100% lineal — "Live TV" de TCL ("300+ FAST channels", sin VOD) y Coolita Channel ("auto-play like traditional TV") — reciben `1` en sus filas vacías. Las mixtas (MovieArk, TCL Channel, ViX, Tubi, Roku…) no se rellenan: en una app con VOD y lineal conviviendo, ni el título ni la app determinan el modo de entrega. La propagación `intra_titulo` está **apagada para esta columna** (solo propagaría el `1` que el vendedor pone por defecto) igual que la inferencia por tipo IMDb (una película en canal lineal es `livestream=1`); ambas existen tras flags explícitos. El 51.1% que queda vacío está honestamente vacío: distinguirlo requiere el EPG/feed del vendedor, no metadata de contenido.
- **contentRating sube 6.6pp** (83.9 → 90.5%) solo con propagación interna. Las fuentes abiertas no ayudan: Wikidata trae clasificación en 2% de los títulos; para más hace falta TMDB (ratings por país) u OMDb (escala US).
- **contentSeries es la columna que menos se puede rellenar (14.6%)**: el catálogo es 67% película (`movie`/`tvMovie`/`short`), y una película no tiene serie. Sobre las filas que sí son series (tipo `tvSeries`/`tvMiniSeries`, ~9% del consolidado), el pipeline llena el nombre canónico. El 85% que queda vacío está *correctamente* vacío o no tiene título buscable.
- **contentLength llega a 50% solo propagando el código del propio vendedor** (mismo título → mismo código). No se toca desde fuentes externas porque el código no es duración (§4). Lo que sí sirve para análisis es `ext_runtime_min` en 41.5% de las filas.

Salida: `inventory-consolidado-v10-a-v15-relleno.csv` (mismas filas, +21 columnas: `titulo_clave`, `ext_imdb_id`, `ext_tipo`, `ext_anio`, `ext_runtime_min`, `ext_confianza` y `<col>_relleno` / `<col>_origen` para las siete columnas). Los `_origen` permiten filtrar en Looker por nivel de confianza (p. ej. solo `original` + `derivado_*` + `intra_titulo`).

## 6. El pipeline periódico

`scripts/enriquecer_externo.py` corre con el mismo comando en cada tanda:

```bash
python scripts/enriquecer_externo.py inventory-consolidado-vN-enriquecido.csv \
    inventory-consolidado-vN-relleno.csv reportes/.../reporte-relleno-vN.json \
    --cache-dir cache-enriquecimiento --wikidata [--tvmaze] [--confianza-min B]
```

Etapas, en orden (la primera que llena gana; cada valor sale con su columna `_origen`):

1. **Normalización del título** → `titulo_clave` (solo títulos "de verdad").
2. **`intra_titulo`**: mismo título con dato en otra fila (dominante ≥ 80%). En `contentSeries` no se propagan placeholders (`VOD`, `No Series`, `OTT Studios …`); en `contentIsLiveStream` está apagado por defecto (solo propagaría el `1` declarado).
3. **`app_default`**: la app manda un valor constante (≥ 95%, ≥ 200 filas). Livestream excluido.
4. **`imdb`**: match offline contra los datasets (se descargan a `cache-enriquecimiento/imdb/` si tienen > 7 días). Desambiguación por género y votos; niveles A–D.
5. **`wikidata`** (`--wikidata`): por IMDb id, en lotes de 150 → idioma, duración, clasificación.
6. **`tvmaze`** (`--tvmaze`): solo para series no resueltas; ~0.5 s por consulta.
7. **Derivados**: `contentCategory` desde el género (mapa a IAB 1.0 aprendido de las filas que traen ambos: deportes→`[IAB17]`, noticias→`[IAB12]`, música→`[IAB1-6]`, infantil/animación/telenovela/reality→`[IAB1-7]`, resto→`[IAB1]`) y del tipo IMDb (movie→`[IAB1-5]`, tvSeries→`[IAB1-7]`); `contentSeries` desde el tipo (tvSeries → título canónico); `contentIsLiveStream` solo desde `contentSeries` `VOD`/`Livestream` + la tabla de semántica por app validada a mano (`semantica_apps.csv`, ver §4).

**Incremental por diseño**: `cache-enriquecimiento/titulos.json` guarda el resultado de cada `titulo_clave`; en la tanda siguiente solo se consultan los títulos nuevos (en v15 entraron ~40k combinaciones nuevas pero pocos títulos nuevos: el catálogo es estable). Una tanda nueva tarda minutos, no horas. La primera corrida sobre 648k filas tomó ~10 min (IMDb) + ~2 min (Wikidata).

**Qué falta para que sea "de producción"**:

- **Licencia**: IMDb datasets y TMDB gratis son solo no comerciales. Para uso interno de análisis está bien; si el relleno alimenta targeting/venta, hay que pasar a TMDB Business, IMDb Essential Metadata o Gracenote.
- **Pedir el feed a OTTera/TCL**: MovieArk + Live TV + TCL Channel + BrowseHere concentran el 60% de las filas vacías y son un solo proveedor.
- **Clasificación por país**: la única fuente abierta con ratings MX/CO/CL es TMDB (`/movie/{id}/release_dates`); Wikidata solo trae 2% (RTC mexicana). Pedir key y medir.
- **Revisión humana del nivel B**: los ~1,600 títulos de nivel B con ≥ 100 filas se auditan una vez y quedan fijados en el caché.
