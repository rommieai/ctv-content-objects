# Qué se puede completar de cada content object (consolidado v10 a v25) — solo tablas

Contexto, fuentes, métodos y límites: `recursos/reporte-completitud-content-objects-v25-completo.md`.

## contentCategory

**Tras el relleno:** 91.8% de las filas (de 22.4%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 20.5% |
| Derivado del género (`derivado_genero`) | 29.6% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 39.8% |
| Venía del vendedor y se corrigió con IMDb (match A) (`corregido_imdb`) | 0.7% |
| Venía del vendedor y se corrigió con el género de la fila (`corregido_genero`) | 1.1% |
| Sigue vacío (`sin_dato`) | 8.2% |

**Qué más se puede afinar (validación del consolidado contra IMDb / Wikidata / taxonomías IAB):**

| Mejora posible | % filas | % requests |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 69.9% | 57.0% |
| Se puede afinar (estaba llena, pero genérica) (`sube`) | 11.2% | 10.7% |
| Se puede corregir (estaba incorrecta) (`corrige`) | 2.8% | 3.4% |
| Se queda igual (ya está bien) (`mantiene`) | 8.4% | 17.7% |
| Sin propuesta (vacía y sin evidencia) (`sin_propuesta`) | 7.7% | 11.3% |

| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |
|---|---:|---:|
| Nivel 0 · nada | 78.0% | 7.8% |
| Nivel 1 · solo la vertical | 13.5% | 13.5% |
| Nivel 2 · vertical + película/TV (o deporte) | 7.2% | 34.1% |
| Nivel 3 · vertical + película/TV + género | 1.4% | 44.6% |

**Confiabilidad de lo que trae y de lo que se llena (filas con categoría, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide con la evidencia (`coincide`) | 19.9% | 62.6% |
| Compatible (genérica, no contradice) (`compatible`) | 49.4% | 19.7% |
| Contradice la evidencia (`contradice`) | 12.4% | 9.2% |
| No se pudo evaluar (`no_evaluable`) | 18.4% | 8.6% |

## contentGenre

**Tras el relleno:** 93.1% de las filas (de 90.4%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 89.3% |
| IMDb (`imdb`) | 2.8% |
| Venía del vendedor y se corrigió con IMDb (match A) (`corregido_imdb`) | 1.0% |
| Sigue vacío (`sin_dato`) | 6.9% |

**Qué más se puede afinar (validación del consolidado):**

| Mejora posible | % filas | % requests |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 2.8% | 1.6% |
| Se pueden agregar géneros o uno más preciso (`sube`) | 23.7% | 21.5% |
| Se puede corregir (contradecía) (`corrige`) | 1.6% | 1.8% |
| Se corrige en parte (acertaba en parte) (`corrige_parcial`) | 2.4% | 0.8% |
| Se queda igual (ya está bien) (`mantiene`) | 62.7% | 62.0% |
| Sin propuesta (sin evidencia) (`sin_propuesta`) | 6.9% | 12.2% |

| Nivel de detalle | Hoy (% filas) | Alcanzable (% filas) |
|---|---:|---:|
| Nivel 0 · vacío | 9.7% | 6.9% |
| Nivel 1 · sin género comparable (solo "entertainment", "other"…) | 14.7% | 12.9% |
| Nivel 2 · un género | 60.1% | 42.1% |
| Nivel 3 · dos o más géneros | 15.5% | 38.1% |

**Confiabilidad (filas con género comparable, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 40.9% | 43.6% |
| Parecido (género vecino) (`afin`) | 2.7% | 2.6% |
| Acierta en parte (`parcial`) | 2.7% | 2.6% |
| Contradice (`contradice`) | 1.7% | 0.6% |
| No se pudo evaluar (`no_evaluable`) | 52.0% | 50.6% |

## contentSeries

**Tras el relleno:** 14.3% de las filas (de 7.2%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 7.2% |
| IMDb (`imdb`) | 7.1% |
| Sigue vacío (`sin_dato`) | 85.7% |

**Qué es cada fila según la evidencia (consolidado):**

| Qué es | % filas |
|---|---:|
| Serie | 15.8% |
| Película | 32.9% |
| Ambiguo (corto, tv movie, video, especial) | 7.4% |
| Desconocido (sin evidencia) | 43.9% |

**Qué se puede hacer con cada fila:**

| Situación | % filas | % requests |
|---|---:|---:|
| Serie con nombre (`ya_nombrada`) | 5.6% | 6.2% |
| Serie sin nombre, con nombre proponible (`serie_sin_nombre_recuperable`) | 10.2% | 9.4% |
| Película: el vacío es correcto (`pelicula_vacio_correcto`) | 32.8% | 22.5% |
| Película con serie declarada (contradicción) (`pelicula_con_serie_declarada`) | 0.2% | 0.0% |
| Contradicha (`contradicha`) | 0.0% | 0.0% |
| Con nombre, sin evidencia para juzgar (`nombrada_sin_evidencia`) | 0.1% | 0.0% |
| Sin evidencia (`sin_evidencia`) | 51.2% | 61.8% |

**Temporada / episodio que trae el título** (candidatos a `content.season` / `content.episode`):

| El título trae | % filas |
|---|---:|
| Temporada y episodio (`temporada+episodio`) | 0.1% |
| Solo temporada (`solo_temporada`) | 3.7% |
| Solo episodio (`solo_episodio`) | 0.8% |
| Nada (`nada`) | 95.3% |

**Confiabilidad de las series declaradas (filas con nombre de serie real, % sobre esas filas):**

| Veredicto | Consolidado (tal como llega) | Relleno (tras el pipeline) |
|---|---:|---:|
| Coincide (`coincide`) | 2.4% | 56.0% |
| Es serie, pero con otro nombre (compatible) (`otro_nombre`) | 4.3% | 1.9% |
| IMDb dice que es película (`contradice`) | 3.5% | 1.6% |
| No se pudo evaluar (`no_evaluable`) | 89.8% | 40.5% |

## contentLength

**Tras el relleno:** 13.4% de las filas (de 13.4%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 13.4% |
| Sigue vacío (`sin_dato`) | 86.6% |

## contentLanguage

**No se rellena.** No hay forma de asumir el idioma en el que se emite un programa en ninguna circunstancia: el mismo título puede ir con pistas de audio distintas por ruta, y el idioma original de la obra (IMDb / Wikidata) no dice en cuál se sirvió. Solo vale lo que declara el vendedor.

## contentIsLiveStream

**Tras el relleno:** 48.8% de las filas (de 30.0%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 30.0% |
| Semántica de la app (curada a mano) (`app_semantica`) | 18.9% |
| Sigue vacío (`sin_dato`) | 51.2% |

## contentRating

**Tras el relleno:** 75.8% de las filas (de 75.7%). Origen del valor final, sobre todas las filas del consolidado:

| Origen | % filas |
|---|---:|
| Venía del vendedor (`original`) | 75.7% |
| Wikidata (`wikidata`) | 0.1% |
| Sigue vacío (`sin_dato`) | 24.2% |

## contentTitle

No se rellena.
