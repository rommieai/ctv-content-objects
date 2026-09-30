# Qué se puede completar de cada content object (consolidado v10 a v22) — solo tablas

Contexto, fuentes, métodos y límites: `recursos/reporte-completitud-content-objects-v22-completo.md`.

## contentCategory

**Tras el relleno:** 93.0% de las filas (de 21.9%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 21.9% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 11.6% |
| Derivado del género (`derivado_genero`) | 26.0% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 33.6% |
| Sigue vacío (`sin_dato`) | 7.0% |

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

**Confiabilidad de lo que trae y de lo que se llena (filas con categoría, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide con la evidencia (`coincide`) | 19.5% | 41.3% |
| Compatible (genérica, no contradice) (`compatible`) | 50.1% | 44.6% |
| Contradice la evidencia (`contradice`) | 12.5% | 4.7% |
| No se pudo evaluar (`no_evaluable`) | 18.0% | 9.4% |

## contentGenre

**Tras el relleno:** 96.8% de las filas (de 90.8%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 90.8% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 3.6% |
| IMDb (`imdb`) | 2.3% |
| Sigue vacío (`sin_dato`) | 3.2% |

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

**Confiabilidad (filas con género comparable, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 41.2% | 41.3% |
| Parecido (género vecino) (`afin`) | 2.6% | 2.5% |
| Acierta en parte (`parcial`) | 2.8% | 2.7% |
| Contradice (`contradice`) | 1.7% | 1.6% |
| No se pudo evaluar (`no_evaluable`) | 51.6% | 51.9% |

## contentSeries

**Tras el relleno:** 14.2% de las filas (de 6.6%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 6.6% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 0.7% |
| IMDb (`imdb`) | 6.9% |
| Sigue vacío (`sin_dato`) | 85.8% |

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

**Confiabilidad de las series declaradas (filas con nombre de serie real, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 2.4% | 56.3% |
| Es serie, pero con otro nombre (compatible) (`otro_nombre`) | 4.7% | 2.0% |
| IMDb dice que es película (`contradice`) | 2.7% | 1.3% |
| No se pudo evaluar (`no_evaluable`) | 90.2% | 40.3% |

## contentLength

**Tras el relleno:** 49.4% de las filas (de 12.6%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 12.6% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 36.8% |
| Sigue vacío (`sin_dato`) | 50.6% |

## contentLanguage

**No se rellena.** No hay forma de asumir el idioma en el que se emite un programa en ninguna circunstancia: el mismo título puede ir con pistas de audio distintas por ruta, y el idioma original de la obra (IMDb / Wikidata) no dice en cuál se sirvió. Solo vale lo que declara el vendedor.

## contentIsLiveStream

**Tras el relleno:** 48.7% de las filas (de 29.5%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 29.5% |
| Semántica de la app (curada a mano) (`app_semantica`) | 19.2% |
| Sigue vacío (`sin_dato`) | 51.3% |

## contentRating

**Tras el relleno:** 82.2% de las filas (de 75.1%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 75.1% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 7.0% |
| Wikidata (`wikidata`) | 0.1% |
| Sigue vacío (`sin_dato`) | 17.8% |

## contentTitle

No se rellena.
