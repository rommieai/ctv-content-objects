# Qué se puede completar de cada content object (consolidado v10 a v19) — solo tablas

Contexto, fuentes, métodos y límites: `recursos/reporte-completitud-content-objects-v19-completo.md`.

## contentCategory

**Tras el relleno:** 93.2% de las filas (de 21.7%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 21.7% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 11.1% |
| Derivado del género (`derivado_genero`) | 26.0% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 34.4% |
| Sigue vacío (`sin_dato`) | 6.8% |

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

**Confiabilidad de lo que trae y de lo que se llena (filas con categoría, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide con la evidencia (`coincide`) | 20.2% | 42.2% |
| Compatible (genérica, no contradice) (`compatible`) | 49.8% | 44.0% |
| Contradice la evidencia (`contradice`) | 12.4% | 4.7% |
| No se pudo evaluar (`no_evaluable`) | 17.5% | 9.1% |

## contentGenre

**Tras el relleno:** 97.2% de las filas (de 91.7%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 91.7% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 3.2% |
| IMDb (`imdb`) | 2.2% |
| Sigue vacío (`sin_dato`) | 2.8% |

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

**Confiabilidad (filas con género comparable, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 41.6% | 41.7% |
| Parecido (género vecino) (`afin`) | 2.5% | 2.4% |
| Acierta en parte (`parcial`) | 3.3% | 3.1% |
| Contradice (`contradice`) | 1.6% | 1.5% |
| No se pudo evaluar (`no_evaluable`) | 51.1% | 51.4% |

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

**Confiabilidad de las series declaradas (filas con nombre de serie real, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 2.5% | 57.1% |
| Es serie, pero con otro nombre (compatible) (`otro_nombre`) | 5.2% | 2.2% |
| IMDb dice que es película (`contradice`) | 2.5% | 1.2% |
| No se pudo evaluar (`no_evaluable`) | 89.8% | 39.5% |

## contentLength

**Tras el relleno:** 47.8% de las filas (de 11.9%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 11.9% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 35.9% |
| Sigue vacío (`sin_dato`) | 52.2% |

## contentLanguage

**No se rellena.** No hay forma de asumir el idioma en el que se emite un programa en ninguna circunstancia: el mismo título puede ir con pistas de audio distintas por ruta, y el idioma original de la obra (IMDb / Wikidata) no dice en cuál se sirvió. Solo vale lo que declara el vendedor.

## contentIsLiveStream

**Tras el relleno:** 48.9% de las filas (de 29.2%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 29.2% |
| Semántica de la app (curada a mano) (`app_semantica`) | 19.7% |
| Sigue vacío (`sin_dato`) | 51.1% |

## contentRating

**Tras el relleno:** 82.7% de las filas (de 74.3%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 74.3% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 8.4% |
| Wikidata (`wikidata`) | 0.1% |
| Sigue vacío (`sin_dato`) | 17.3% |

## contentTitle

No se rellena.
