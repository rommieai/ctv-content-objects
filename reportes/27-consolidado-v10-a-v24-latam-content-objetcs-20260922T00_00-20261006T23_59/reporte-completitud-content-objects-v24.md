# Qué se puede completar de cada content object (consolidado v10 a v24) — solo tablas

Contexto, fuentes, métodos y límites: `recursos/reporte-completitud-content-objects-v24-completo.md`.

## contentCategory

**Tras el relleno:** 91.8% de las filas (de 22.1%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 20.3% |
| Derivado del género (`derivado_genero`) | 29.7% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 40.0% |
| Venía del vendedor y se corrigió con IMDb (match A) (`corregido_imdb`) | 0.7% |
| Venía del vendedor y se corrigió con el género de la fila (`corregido_genero`) | 1.1% |
| Sigue vacío (`sin_dato`) | 8.2% |

**Qué más se puede afinar (validación del consolidado contra IMDb / Wikidata / taxonomías IAB):**

| Mejora posible | % filas | % requests |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 70.2% | 58.2% |
| Se puede afinar (estaba llena, pero genérica) (`sube`) | 11.2% | 10.4% |
| Se puede corregir (estaba incorrecta) (`corrige`) | 2.8% | 3.4% |
| Se queda igual (ya está bien) (`mantiene`) | 8.2% | 16.6% |
| Sin propuesta (vacía y sin evidencia) (`sin_propuesta`) | 7.7% | 11.4% |

| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |
|---|---:|---:|
| Nivel 0 · nada | 78.2% | 7.7% |
| Nivel 1 · solo la vertical | 13.5% | 13.6% |
| Nivel 2 · vertical + película/TV (o deporte) | 7.0% | 33.9% |
| Nivel 3 · vertical + película/TV + género | 1.3% | 44.8% |

**Confiabilidad de lo que trae y de lo que se llena (filas con categoría, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide con la evidencia (`coincide`) | 19.8% | 62.7% |
| Compatible (genérica, no contradice) (`compatible`) | 49.7% | 19.6% |
| Contradice la evidencia (`contradice`) | 12.4% | 9.3% |
| No se pudo evaluar (`no_evaluable`) | 18.1% | 8.5% |

## contentGenre

**Tras el relleno:** 93.3% de las filas (de 90.6%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 89.5% |
| IMDb (`imdb`) | 2.7% |
| Venía del vendedor y se corrigió con IMDb (match A) (`corregido_imdb`) | 1.0% |
| Sigue vacío (`sin_dato`) | 6.7% |

**Qué más se puede afinar (validación del consolidado):**

| Mejora posible | % filas | % requests |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 2.7% | 1.8% |
| Se pueden agregar géneros o uno más preciso (`sube`) | 23.6% | 22.6% |
| Se puede corregir (contradecía) (`corrige`) | 1.6% | 2.0% |
| Se corrige en parte (acertaba en parte) (`corrige_parcial`) | 2.5% | 0.8% |
| Se queda igual (ya está bien) (`mantiene`) | 62.9% | 60.5% |
| Sin propuesta (sin evidencia) (`sin_propuesta`) | 6.7% | 12.4% |

| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |
|---|---:|---:|
| Nivel 0 · vacío | 9.4% | 6.7% |
| Nivel 1 · sin género comparable (solo "entertainment", "other"…) | 14.8% | 12.9% |
| Nivel 2 · un género | 59.8% | 41.9% |
| Nivel 3 · dos o más géneros | 16.0% | 38.5% |

**Confiabilidad (filas con género comparable, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 41.0% | 43.7% |
| Parecido (género vecino) (`afin`) | 2.7% | 2.6% |
| Acierta en parte (`parcial`) | 2.8% | 2.7% |
| Contradice (`contradice`) | 1.7% | 0.6% |
| No se pudo evaluar (`no_evaluable`) | 51.8% | 50.4% |

## contentSeries

**Tras el relleno:** 14.0% de las filas (de 6.8%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 6.8% |
| IMDb (`imdb`) | 7.1% |
| Sigue vacío (`sin_dato`) | 86.0% |

**Qué es cada fila según la evidencia (consolidado):**

| Qué es | % filas |
|---|---:|
| Serie | 15.7% |
| Película | 33.1% |
| Ambiguo (corto, tv movie, video, especial) | 7.4% |
| Desconocido (sin evidencia) | 43.8% |

**Qué se puede hacer con cada fila:**

| Situación | % filas | % requests |
|---|---:|---:|
| Serie con nombre (`ya_nombrada`) | 5.3% | 5.3% |
| Serie sin nombre, con nombre proponible (`serie_sin_nombre_recuperable`) | 10.3% | 9.6% |
| Película: el vacío es correcto (`pelicula_vacio_correcto`) | 33.0% | 23.7% |
| Película con serie declarada (contradicción) (`pelicula_con_serie_declarada`) | 0.1% | 0.0% |
| Contradicha (`contradicha`) | 0.0% | 0.0% |
| Con nombre, sin evidencia para juzgar (`nombrada_sin_evidencia`) | 0.0% | 0.0% |
| Sin evidencia (`sin_evidencia`) | 51.2% | 61.3% |

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
| Coincide (`coincide`) | 2.4% | 57.5% |
| Es serie, pero con otro nombre (compatible) (`otro_nombre`) | 4.5% | 2.0% |
| IMDb dice que es película (`contradice`) | 2.9% | 1.3% |
| No se pudo evaluar (`no_evaluable`) | 90.1% | 39.3% |

## contentLength

**Tras el relleno:** 13.1% de las filas (de 13.1%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 13.1% |
| Sigue vacío (`sin_dato`) | 86.9% |

## contentLanguage

**No se rellena.** No hay forma de asumir el idioma en el que se emite un programa en ninguna circunstancia: el mismo título puede ir con pistas de audio distintas por ruta, y el idioma original de la obra (IMDb / Wikidata) no dice en cuál se sirvió. Solo vale lo que declara el vendedor.

## contentIsLiveStream

**Tras el relleno:** 48.9% de las filas (de 29.8%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 29.8% |
| Semántica de la app (curada a mano) (`app_semantica`) | 19.1% |
| Sigue vacío (`sin_dato`) | 51.1% |

## contentRating

**Tras el relleno:** 75.6% de las filas (de 75.5%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 75.5% |
| Wikidata (`wikidata`) | 0.1% |
| Sigue vacío (`sin_dato`) | 24.4% |

## contentTitle

No se rellena.
