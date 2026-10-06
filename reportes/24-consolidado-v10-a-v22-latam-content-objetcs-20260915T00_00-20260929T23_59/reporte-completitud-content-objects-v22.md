# Qué se puede completar de cada content object (consolidado v10 a v22) — solo tablas

Contexto, fuentes, métodos y límites: `recursos/reporte-completitud-content-objects-v22-completo.md`.

## contentCategory

**Tras el relleno:** 91.8% de las filas (de 21.9%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 21.9% |
| Derivado del género (`derivado_genero`) | 29.8% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 40.1% |
| Sigue vacío (`sin_dato`) | 8.2% |

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
| Coincide con la evidencia (`coincide`) | 19.5% | 60.7% |
| Compatible (genérica, no contradice) (`compatible`) | 50.1% | 19.4% |
| Contradice la evidencia (`contradice`) | 12.5% | 11.5% |
| No se pudo evaluar (`no_evaluable`) | 18.0% | 8.4% |

## contentGenre

**Tras el relleno:** 93.4% de las filas (de 90.8%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 90.8% |
| IMDb (`imdb`) | 2.6% |
| Sigue vacío (`sin_dato`) | 6.6% |

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
| Coincide (`coincide`) | 41.2% | 42.9% |
| Parecido (género vecino) (`afin`) | 2.6% | 2.6% |
| Acierta en parte (`parcial`) | 2.8% | 2.7% |
| Contradice (`contradice`) | 1.7% | 1.8% |
| No se pudo evaluar (`no_evaluable`) | 51.6% | 50.1% |

## contentSeries

**Tras el relleno:** 13.8% de las filas (de 6.6%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 6.6% |
| IMDb (`imdb`) | 7.2% |
| Sigue vacío (`sin_dato`) | 86.2% |

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
| Coincide (`coincide`) | 2.4% | 58.4% |
| Es serie, pero con otro nombre (compatible) (`otro_nombre`) | 4.7% | 2.3% |
| IMDb dice que es película (`contradice`) | 2.7% | 1.3% |
| No se pudo evaluar (`no_evaluable`) | 90.2% | 38.0% |

## contentLength

**Tras el relleno:** 12.6% de las filas (de 12.6%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 12.6% |
| Sigue vacío (`sin_dato`) | 87.4% |

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

**Tras el relleno:** 75.3% de las filas (de 75.1%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 75.1% |
| Wikidata (`wikidata`) | 0.1% |
| Sigue vacío (`sin_dato`) | 24.7% |

## contentTitle

No se rellena.
