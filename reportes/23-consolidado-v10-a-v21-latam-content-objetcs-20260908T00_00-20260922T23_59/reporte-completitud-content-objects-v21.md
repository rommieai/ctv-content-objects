# Qué se puede completar de cada content object (consolidado v10 a v21) — solo tablas

Contexto, fuentes, métodos y límites: `recursos/reporte-completitud-content-objects-v21-completo.md`.

## contentCategory

**Tras el relleno:** 93.0% de las filas (de 21.5%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 21.5% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 11.6% |
| Derivado del género (`derivado_genero`) | 26.0% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 33.9% |
| Sigue vacío (`sin_dato`) | 7.0% |

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

**Confiabilidad de lo que trae y de lo que se llena (filas con categoría, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide con la evidencia (`coincide`) | 19.8% | 41.5% |
| Compatible (genérica, no contradice) (`compatible`) | 49.7% | 44.4% |
| Contradice la evidencia (`contradice`) | 12.7% | 4.7% |
| No se pudo evaluar (`no_evaluable`) | 17.9% | 9.3% |

## contentGenre

**Tras el relleno:** 96.9% de las filas (de 91.0%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 91.0% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 3.6% |
| IMDb (`imdb`) | 2.3% |
| Sigue vacío (`sin_dato`) | 3.1% |

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

**Confiabilidad (filas con género comparable, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 41.4% | 41.5% |
| Parecido (género vecino) (`afin`) | 2.6% | 2.5% |
| Acierta en parte (`parcial`) | 2.9% | 2.8% |
| Contradice (`contradice`) | 1.7% | 1.6% |
| No se pudo evaluar (`no_evaluable`) | 51.3% | 51.7% |

## contentSeries

**Tras el relleno:** 14.0% de las filas (de 6.4%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 6.4% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 0.7% |
| IMDb (`imdb`) | 7.0% |
| Sigue vacío (`sin_dato`) | 86.0% |

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

**Confiabilidad de las series declaradas (filas con nombre de serie real, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 2.5% | 57.3% |
| Es serie, pero con otro nombre (compatible) (`otro_nombre`) | 4.9% | 2.1% |
| IMDb dice que es película (`contradice`) | 2.6% | 1.2% |
| No se pudo evaluar (`no_evaluable`) | 90.1% | 39.4% |

## contentLength

**Tras el relleno:** 49.0% de las filas (de 12.2%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 12.2% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 36.8% |
| Sigue vacío (`sin_dato`) | 51.0% |

## contentLanguage

**No se rellena.** No hay forma de asumir el idioma en el que se emite un programa en ninguna circunstancia: el mismo título puede ir con pistas de audio distintas por ruta, y el idioma original de la obra (IMDb / Wikidata) no dice en cuál se sirvió. Solo vale lo que declara el vendedor.

## contentIsLiveStream

**Tras el relleno:** 48.7% de las filas (de 29.3%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 29.3% |
| Semántica de la app (curada a mano) (`app_semantica`) | 19.4% |
| Sigue vacío (`sin_dato`) | 51.3% |

## contentRating

**Tras el relleno:** 82.1% de las filas (de 74.9%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 74.9% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 7.2% |
| Wikidata (`wikidata`) | 0.1% |
| Sigue vacío (`sin_dato`) | 17.9% |

## contentTitle

No se rellena.
