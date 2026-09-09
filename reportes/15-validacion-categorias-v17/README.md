# Validación de contentCategory con fuentes abiertas — correctitud y completitud (consolidado v10 a v17)

**Pregunta:** ¿hay forma de validar que el relleno de `contentCategory` sea correcto, tanto en el consolidado como en su versión enriquecida? ¿Y se pueden poner categorías IAB más finas?

**Fuentes:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas, 380,355,807,040 requests, métricas del corte v17) y `inventory-consolidado-v10-a-v17-relleno.csv` (la salida del pipeline de relleno, columna `contentCategory_relleno` + `_origen`). El `-enriquecido.csv` trae exactamente la misma `contentCategory` que el consolidado (verificado: misma distribución de valores), así que su validación es la del consolidado; lo que cambia la categoría es el **relleno**, y por eso es el segundo dataset.
**Generado con:** `scripts/validar_categorias.py` (un JSON + muestras por dataset) y `scripts/generar_reporte_validacion.py` (los dos markdown). Corrida del 9 sep 2026. Todo es repetible: los dos scripts se corren tras cada tanda con los mismos comandos (abajo).

| Reporte | Qué responde |
|---|---|
| [reporte-correctitud.md](reporte-correctitud.md) | **Parte 1.** Las filas que traen categoría, ¿la traen bien? Formato de los valores, veredicto por fila (coincide / compatible / contradice), quién se equivoca, consistencia entre rutas del mismo título, y de paso `contentGenre` contra IMDb. |
| [reporte-completitud.md](reporte-completitud.md) | **Parte 2.** ¿Se puede poner una categoría IAB más fina? Nivel de granularidad actual vs alcanzable con la evidencia, en IAB Content Taxonomy 2.2 (y su equivalente 1.0), fila a fila, por país, publisher y origen del relleno. |
| `validacion-{consolidado,relleno}.json` | Los agregados que respaldan cada tabla. |
| `validacion-*-muestra-contradicciones.csv` | 400 títulos contradictorios por dataset (uno por título, los de más tráfico primero) con lo declarado, lo esperado, el id IMDb y el motivo: para revisión manual. |
| `validacion-*-muestra-propuestas.csv` | 400 filas al azar por dataset con la categoría propuesta y de dónde salió. |
| `validacion-categorias-v17-{consolidado,relleno}-filas.csv` (raíz, no versionado) | Una fila por fila del consolidado con todas las columnas de diagnóstico: veredicto, detalle, evidencia, propuesta 2.2 y 1.0, nivel actual y propuesto. |

## Qué fuentes abiertas sirven para esto (y cuáles no)

- **IMDb Non-Commercial Datasets + Wikidata (P136)**, ya descargados y cacheados por el pipeline de relleno (`cache-enriquecimiento/titulos.json`, 14,686 títulos, 7,441 con match IMDb). Dan el **tipo** (película / serie) y los **géneros** de cada título. Son la única fuente que prueba las tres cosas que una categoría afirma: vertical (entretenimiento vs noticias vs deportes…), forma (película vs TV) y género. Cubren el 49.7% de las filas del consolidado (las que tienen título real con match de confianza A o B).
- **Las taxonomías oficiales de IAB Tech Lab** (Content Taxonomy 1.0, 2.2 y 3.0, del GitHub público), descargadas a `cache-enriquecimiento/iab/`. Dicen qué códigos existen y qué significan. Sin ellas no se puede saber que `[IAB1-22]` (12% de las filas llenas del consolidado) **no existe** en 1.0, que `[1070]` es "Content Language > Spanish" (un metadato, no una categoría) o que `[IAB19-29]` es "Technology & Computing > Entertainment".
- **El propio dataset** como evidencia interna: el `contentGenre` de la misma fila (un drama no es Noticias; un talk show no es Películas) y las demás rutas del mismo título (si Vidaa manda `[IAB12]` y OTTera `[IAB1]` para *la rosa de guadalupe*, al menos una está mal). No requiere nada externo y cubre lo que IMDb no alcanza.
- **No sirven (o no todavía):** TMDB exige API key y no se usó; TVMaze no aporta categoría. IMDb no registra *de qué trata* la no ficción (un documental de viajes es solo "Documentary"), así que las verticales temáticas (Viajes, Cocina, Tecnología) no se pueden validar ni proponer desde cero; para eso harían falta TMDB keywords o Wikidata P921 (main subject).

## Hallazgos — Parte 1: correctitud

**Sobre el consolidado (lo que mandan los vendedores):** de las 209,901 filas con categoría (21.9% del consolidado, 32.5% de los requests), el 83% se pudo evaluar. De esas, **15.0% contradicen la evidencia** (26,159 filas; 14.9% de los requests con categoría), 24.6% aciertan en lo más fino que declaran y 60.4% son compatibles pero genéricas (`[IAB1]` a secas, o `[IAB1-5, IAB1-7]` "película o TV"). Lo que se sabe de las contradicciones:

- **Son errores del vendedor, no del match.** En el 93.6% de las contradicciones con evidencia externa el género declarado por el propio vendedor coincide con los géneros IMDb del match, es decir, el match es creíble y la categoría es la que no cuadra. El choque dominante es de **vertical** (10,131 filas externas + 8,576 internas), no de forma ni de género.
- **Cuatro rutas concentran el problema**, y son sistemáticas, no ruido: **Vidaa** (58.9% de sus filas evaluables contradicen; 46.6% de sus requests) manda `[IAB12]` Noticias en las telenovelas y comedias de Televisa (*la rosa de guadalupe*, *40 y 20*, *mi corazón es tuyo*…). **PML Digital** (78.7%; 64.2% de requests) manda `[sports]` en películas de drama y `[IAB17-1]` Auto Racing en fútbol y artes marciales. **Equativ** (44.2%; 33.5%) y **METAX** (18.5%; 29.7%) mandan `[IAB1, IAB1-5]` Películas en series (las mismas telenovelas, otra ruta). Coocaa manda `[IAB1-7, IAB19-29]` (Televisión + *Technology & Computing > Entertainment*) en *Transplant* y `[IAB1-1]` Books & Literature en podcasts de comedia. OTTera, con 74k filas llenas, contradice el 0.8%: su `[IAB1]` genérico casi nunca está mal, pero tampoco dice nada.
- **El formato ya delata parte:** 12.6% de las filas llenas usan un código que no existe (`[IAB1-22]`, `[IAB-7]`, `[IAB1-6-3]`), 3.5% texto libre (`[sports]`, `[Live]`, `[Entertainment]`) y 7.5% la taxonomía numérica 2.2 (`[640]`, `[325]`, `[330, 646]`), conviviendo con el 89% en 1.0. `[IAB1-7, IAB17-12]` (4,990 filas de animación) es Televisión + *Football* (americano). `[Live]` y `[1070]` no son categorías de contenido.
- **Entre rutas:** 27% de los 9,777 títulos con categoría reciben verticales distintas según la ruta; las filas minoritarias (las que dicen algo distinto de la mayoría de su título) son el 5.3% de las llenas. `transplant` es Tecnología × 641 y Entretenimiento × 641; `golden edge` es Noticias × 437 (Vidaa/Equativ) y Entretenimiento × 35.
- **El género declarado sí es fiable:** el 92.6% de las 431k filas comparables coincide con IMDb (Select Plus es la excepción con 82.7%; Vidaa y Televisa 99%+). Esto importa porque el género es el insumo del relleno de categoría.

**Sobre el relleno (lo que hizo el pipeline de `enriquecer_externo.py`):** la contradicción baja al **6.0% de las 818k filas evaluables** (48,939 filas) y `coincide` sube de 24.6% a 42.1%: el relleno, en conjunto, mejora la columna. Pero el desglose por origen del valor muestra dónde amplifica errores:

| Origen | Filas | contradice (de evaluables) | % de los requests del grupo | Lectura |
|---|---:|---:|---:|---|
| `original` | 209,901 | 15.0% | 10.5% | Lo que venía; es la Parte 1. |
| `intra_titulo` | 93,404 | 8.0% | **47.9%** | Copia el valor dominante del título a las rutas vacías. Cuando el dominante es el `[IAB12]` de Vidaa, **propaga el error a las demás rutas**: *lo que la vida me robó* lleva `[IAB12]` en 530 filas del relleno (2.5 mil millones de requests); 150 son las de Vidaa que ya venían así y 380 son filas de EXTE, Televisa, Equativ, VGI o LG Ads que estaban vacías y lo heredaron. Es el origen que más tráfico contamina. |
| `app_default` | 83,934 | 9.9% | 10.1% | El `[sports]` de PML → Live TV se copia a todo el catálogo de esa app, incluidas películas de drama (824 filas). |
| `derivado_genero` | 226,590 | 4.4% | 2.0% | Género → IAB. Casi siempre `[IAB1]`: rara vez está mal porque rara vez dice algo. |
| `derivado_tipo` | 291,042 | 0.1% | 0.1% | Tipo IMDb → `[IAB1-5]`/`[IAB1-7]`. **Ojo: es circular** — la validación usa el mismo tipo IMDb como evidencia, así que aquí solo se prueba consistencia, no verdad. Su precisión real es la del match (A ~90%, B ~75%). |

Lo mismo vale, en menor grado, para `derivado_genero` frente a la evidencia interna: se valida contra el género que lo generó. Las cifras defendibles del relleno son las de `intra_titulo` y `app_default`, que sí se contrastan con algo independiente.

## Hallazgos — Parte 2: completitud

Se mide en **nivel de granularidad** (atributos conocidos): 0 = nada, 1 = solo vertical (`[IAB1]`), 2 = vertical + forma (`[IAB1-5]`) o + sub-deporte (`[IAB17-44]`), 3 = vertical + forma + género (`[333]` Drama Movies). Es comparable entre taxonomías.

- **Consolidado:** hoy el 78.1% de las filas está vacío, el 12.2% en nivel 1 y solo el 0.9% en nivel 3. Con la evidencia disponible, el **45.6% de las filas podría llevar nivel 3** y otro 33.1% nivel 2; queda sin propuesta el 6.9% (14.2% de los requests: catálogo sin título real ni género). Fila a fila: 71.3% se rellena desde vacío, 11.5% sube de nivel, 7.7% se mantiene (ya está igual o mejor), 2.7% se corrige (estaba contradicha).
- **Relleno:** el pipeline ya lo dejó en 94% lleno pero **casi todo en nivel 1–2** (48.4% y 39.6%). El 68.8% de las filas puede subir de nivel: las 291k de `derivado_tipo` pasarían de `[IAB1-5]` a `[333]`/`[336]`/`[331]` (Drama/Horror/Crime Movies) con los géneros IMDb que ya están en el caché, y las de `derivado_genero`/`app_default` pasarían de `[IAB1]` al par película+TV del género (`[333, 647]`) cuando la forma no se conoce.
- **De dónde sale la forma** (lo que separa nivel 2 de nivel 3): tipo IMDb en el 40.5% de las filas, el propio título en 4.3% ("season 2", "S01E03" → serie, y manda sobre el match cuando IMDb cayó en una película homónima), `contentSeries` real en 4.6%. El 45% no tiene forma conocida: es el techo del método sin datos del vendedor.
- **Propuestas más frecuentes** (2.2): Drama Movies, Horror Movies, Crime and Mystery Movies, Documentary Movies / Factual TV, Comedy Movies, Drama TV, Soap Opera TV, Reality TV, Sports > Soccer/Boxing/Baseball cuando el género lo nombra. Como el 89% de las filas llenas usa IAB 1.0 (que no tiene géneros bajo Movies/Television), **subir de nivel implica cambiar de taxonomía**: la propuesta trae siempre el equivalente 1.0 (`prop_iab10`) para no perder compatibilidad.

## Qué hacer con esto

1. **Corregir en el relleno, no solo rellenar.** Las 26k filas contradichas del consolidado son un insumo directo para `enriquecer_externo.py`: hoy respeta lo `original` a ciegas. Con `veredicto = contradice` y `genero_vs_imdb = coincide` se pueden reemplazar (columna `prop_iab22`/`prop_iab10`) y, sobre todo, **impedir que `intra_titulo` propague un valor contradicho** (el 47.9% de los requests de ese origen).
2. **Hablar con tres vendedores** con evidencia en la mano (`validacion-consolidado-muestra-contradicciones.csv`): Vidaa (`[IAB12]` en telenovelas), PML Digital (`[sports]` y `[IAB17-1]` como default), Equativ/METAX (`[IAB1-5]` en series). Son mapeos por defecto mal puestos, no errores por título.
3. **Adoptar 2.2 (o 3.0) para ganar granularidad.** IAB 1.0 no puede expresar "drama de TV"; con el caché actual el 45% del consolidado ya tiene evidencia para nivel 3.

## Límites

- La evidencia externa cubre lo que tiene título real y match; el catálogo con placeholders (`epg`, `roku`) queda a merced del género declarado.
- Un match B se equivoca 1 de cada 4 veces y, cuando falla, suele caer en una película vieja de título homónimo (*abismo de pasión* → *Kings Row* 1942): la contradicción de vertical sigue siendo válida (Noticias no es), pero la de forma no. Por eso las cifras de forma se reportan aparte y `--confianza-min A` está disponible.
- Verticales temáticas de la no ficción: ni se contradicen ni se proponen (ver arriba).
- "Football" se mapea a fútbol americano como manda IAB 1.0 (`IAB17-12`); si el vendedor lo usa como fútbol, es una decisión de negocio corregirlo.

## Cómo repetirlo

```bash
# requiere el cache de titulos del paso 4 del pipeline (enriquecer_externo.py) ya corrido
PYTHONIOENCODING=utf-8 python scripts/validar_categorias.py inventory-consolidado-v10-a-v17.csv \
    reportes/15-validacion-categorias-v17/validacion-consolidado --nombre consolidado \
    --filas validacion-categorias-v17-consolidado-filas.csv
PYTHONIOENCODING=utf-8 python scripts/validar_categorias.py inventory-consolidado-v10-a-v17-relleno.csv \
    reportes/15-validacion-categorias-v17/validacion-relleno --nombre relleno \
    --filas validacion-categorias-v17-relleno-filas.csv
python scripts/generar_reporte_validacion.py reportes/15-validacion-categorias-v17 \
    consolidado=reportes/15-validacion-categorias-v17/validacion-consolidado.json \
    relleno=reportes/15-validacion-categorias-v17/validacion-relleno.json
```

Cada corrida tarda ~2 min por dataset (solo stdlib). Opciones útiles: `--confianza-min A` (solo matches unívocos), `--columna contentCategory` (validar la columna original dentro del relleno), `--paises`, `--top-publishers`. Las taxonomías IAB se descargan una vez a `cache-enriquecimiento/iab/` (el CDN de GitHub a veces responde 503: el script reintenta).
