# Reporte — Completitud de contentCategory: ¿se puede poner una categoría IAB más fina?

**Fuentes:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas, columna `contentCategory`); `inventory-consolidado-v10-a-v17-relleno.csv` (959,442 filas, columna `contentCategory_relleno`).  
**Generado con:** `scripts/validar_categorias.py` + `scripts/generar_reporte_validacion.py`. Corrida del 2026-09-09 15:31. Propuestas en IAB Content Taxonomy **2.2** (la última con géneros bajo Movies/Television y ~70 deportes) y su equivalente en **1.0** (la que usa la mayoría de las filas llenas).

**Convención:** aquí los % son **% del total de filas** del dataset (llenas y vacías), salvo en las tablas por grupo, donde son % de las filas del grupo. El **nivel** de granularidad cuenta atributos conocidos: 0 = nada; 1 = solo vertical (`[IAB1]`, `[IAB12]`, `[324]`); 2 = vertical + forma (`[IAB1-5]` Películas, `[640]` Televisión) o vertical + sub-deporte (`[IAB17-44]` Soccer); 3 = vertical + forma + género (`[333]` Drama Movies, `[651]` Reality TV). Es comparable entre taxonomías porque mide información, no profundidad del árbol.

---

## 1. Punto de partida

`vacia` = sin categoría útil; `contradicha` = trae categoría pero la evidencia la contradice (ver reporte de correctitud); `llena` = trae categoría y no está contradicha.

| Dataset | Filas | vacia | llena | contradicha |
|---|---:|---:|---:|---:|
| **consolidado** | 959,442 | 749,541 (78.1%) · req 67.5% | 183,742 (19.1%) · req 29.0% | 26,159 (2.7%) · req 3.4% |
| **relleno** | 959,442 | 54,571 (5.7%) · req 13.4% | 855,932 (89.2%) · req 78.7% | 48,939 (5.1%) · req 7.8% |

Nivel actual de las filas llenas o contradichas (% del total de filas):

| Estado · nivel actual | consolidado | relleno |
|---|---:|---:|
| `contradicha|1` | 15,750 (1.6%) · req 1.8% | 30,265 (3.1%) · req 5.8% |
| `contradicha|2` | 8,691 (0.9%) · req 1.6% | 16,886 (1.8%) · req 2.0% |
| `contradicha|3` | 1,718 (0.2%) · req 0.0% | 1,788 (0.2%) · req 0.0% |
| `llena|0` | 2,898 (0.3%) · req 0.2% | 2,934 (0.3%) · req 0.2% |
| `llena|1` | 116,850 (12.2%) · req 11.6% | 464,204 (48.4%) · req 39.9% |
| `llena|2` | 55,485 (5.8%) · req 16.9% | 380,244 (39.6%) · req 38.4% |
| `llena|3` | 8,509 (0.9%) · req 0.3% | 8,550 (0.9%) · req 0.3% |
| `vacia|0` | 749,541 (78.1%) · req 67.5% | 54,571 (5.7%) · req 13.4% |

## 2. Hasta dónde llega la evidencia

Para cada fila se calcula la categoría más fina que la evidencia permite. La **evidencia** es `externa` (tipo y géneros IMDb/Wikidata del título), `interna` (el género declarado en la fila), `serie` (solo `contentSeries` con nombre real → es TV) o `ninguna`. La **forma** (película/TV) sale, en orden, de: tipo IMDb > `contentSeries` real > lo ya declarado > género que la implica (telenovela, reality, talk show → TV).

Evidencia disponible por fila:

| Evidencia | consolidado | relleno |
|---|---:|---:|
| `externa` | 476,869 (49.7%) · req 35.4% | 476,869 (49.7%) · req 35.4% |
| `interna` | 326,895 (34.1%) · req 37.7% | 326,895 (34.1%) · req 37.7% |
| `ninguna` | 144,334 (15.0%) · req 25.4% | 144,334 (15.0%) · req 25.4% |
| `serie` | 11,344 (1.2%) · req 1.5% | 11,344 (1.2%) · req 1.5% |

De dónde sale la forma (película/TV):

| Origen de la forma | consolidado | relleno |
|---|---:|---:|
| `contentSeries` | 43,747 (4.6%) · req 5.5% | 43,747 (4.6%) · req 5.5% |
| `declarado` | 27,286 (2.8%) · req 8.5% | 94,274 (9.8%) · req 12.7% |
| `genero` | 24,634 (2.6%) · req 1.5% | 10,427 (1.1%) · req 0.6% |
| `imdb` | 388,179 (40.5%) · req 29.5% | 388,179 (40.5%) · req 29.5% |
| `sin_forma` | 434,393 (45.3%) · req 52.0% | 381,612 (39.8%) · req 48.7% |
| `titulo` | 41,203 (4.3%) · req 3.0% | 41,203 (4.3%) · req 3.0% |

Nivel propuesto (% del total de filas). En las filas ya llenas que no se contradicen y cuyo nivel actual iguala o supera al alcanzable, se **mantiene** lo declarado (el nivel propuesto es el actual):

| Nivel propuesto | consolidado | relleno |
|---|---:|---:|
| nivel `0` | 65,888 (6.9%) · req 14.2% | 52,527 (5.5%) · req 13.3% |
| nivel `1` | 138,222 (14.4%) · req 13.4% | 147,564 (15.4%) · req 14.1% |
| nivel `2` | 318,005 (33.1%) · req 36.3% | 270,582 (28.2%) · req 33.3% |
| nivel `3` | 437,327 (45.6%) · req 36.0% | 488,769 (50.9%) · req 39.3% |

## 3. Qué cambia fila a fila

`rellena` = estaba vacía y hay propuesta; `sube` = estaba llena y la propuesta es más fina; `mantiene` = estaba llena y ya es igual o más fina que lo alcanzable; `corrige` = estaba contradicha y hay propuesta que la reemplaza; `sin_propuesta` = vacía sin evidencia.

| Mejora | consolidado | relleno |
|---|---:|---:|
| `rellena` | 684,124 (71.3%) · req 53.4% | 2,517 (0.3%) · req 0.1% |
| `sube` | 109,936 (11.5%) · req 11.2% | 660,372 (68.8%) · req 51.8% |
| `mantiene` | 73,806 (7.7%) · req 17.8% | 195,560 (20.4%) · req 26.9% |
| `corrige` | 26,159 (2.7%) · req 3.4% | 48,939 (5.1%) · req 7.8% |
| `sin_propuesta` | 65,417 (6.8%) · req 14.2% | 52,054 (5.4%) · req 13.3% |

Matriz estado actual · nivel actual → nivel propuesto (% del total de filas; solo celdas con ≥ 0.5%):

**consolidado**:

| estado · actual → propuesto | Filas | % filas | % requests |
|---|---:|---:|---:|
| `vacia|0->3` | 345,813 | 36.0% | 26.5% |
| `vacia|0->2` | 241,153 | 25.1% | 19.5% |
| `vacia|0->1` | 97,158 | 10.1% | 7.4% |
| `vacia|0->0` | 65,417 | 6.8% | 14.2% |
| `llena|1->2` | 39,072 | 4.1% | 3.4% |
| `llena|1->1` | 38,999 | 4.1% | 5.8% |
| `llena|1->3` | 38,779 | 4.0% | 2.4% |
| `llena|2->3` | 29,658 | 3.1% | 5.2% |
| `llena|2->2` | 25,827 | 2.7% | 11.7% |
| `contradicha|1->3` | 9,255 | 1.0% | 1.1% |
| `llena|3->3` | 8,509 | 0.9% | 0.3% |
| `contradicha|1->2` | 5,894 | 0.6% | 0.6% |

**relleno**:

| estado · actual → propuesto | Filas | % filas | % requests |
|---|---:|---:|---:|
| `llena|2->3` | 338,376 | 35.3% | 25.6% |
| `llena|1->2` | 208,975 | 21.8% | 17.8% |
| `llena|1->1` | 144,669 | 15.1% | 13.8% |
| `llena|1->3` | 110,560 | 11.5% | 8.2% |
| `vacia|0->0` | 52,054 | 5.4% | 13.3% |
| `llena|2->2` | 41,868 | 4.4% | 12.8% |
| `contradicha|1->3` | 18,153 | 1.9% | 4.4% |
| `contradicha|2->3` | 12,219 | 1.3% | 0.8% |
| `contradicha|1->2` | 11,062 | 1.1% | 1.3% |
| `llena|3->3` | 8,550 | 0.9% | 0.3% |

## 4. Por país, publisher y origen

Cada fila de estas tablas es un grupo; los % son sobre las filas del grupo.

### Por país — consolidado

|  | Filas | `rellena` | `sube` | `mantiene` | `corrige` | `sin_propuesta` |
|---|---:|---:|---:|---:|---:|---:|
| Mexico | 304,329 | 66.1% | 10.4% | 8.5% | 4.2% | 10.8% |
| Colombia | 101,514 | 71.8% | 12.2% | 7.5% | 2.2% | 6.4% |
| Chile | 107,269 | 79.2% | 9.4% | 5.7% | 1.0% | 4.7% |

### Por publisher — consolidado

|  | Filas | `rellena` | `sube` | `mantiene` | `corrige` | `sin_propuesta` |
|---|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 200,221 | 58.9% | 29.8% | 7.1% | 0.3% | 4.0% |
| iion Pty Ltd | 183,090 | 90.7% | 0.3% | 0.3% | 0.0% | 8.6% |
| TCL ADS - Springserve | 120,000 | 93.2% | 0.5% | 0.2% | 0.0% | 6.1% |
| TCL ADs (APAC) | 112,769 | 94.6% | 0.6% | 0.2% | 0.0% | 4.5% |
| Select Plus PTE LTD (CTV) | 83,294 | 94.1% | 0.0% | 0.0% | 0.0% | 5.9% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 23,608 | 67.3% | 6.5% | 9.2% | 8.4% | 8.7% |
| PML Digital | 23,147 | 74.1% | 4.0% | 2.8% | 15.6% | 3.5% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 21,859 | 27.2% | 43.5% | 15.8% | 12.3% | 1.2% |
| AWG Media | 18,736 | 5.5% | 48.0% | 37.6% | 8.8% | 0.1% |
| Vidaa | 17,233 | 8.9% | 15.4% | 31.7% | 39.0% | 5.0% |
| Coocaa, a SKYWORTH company | 14,978 | 0.0% | 49.4% | 41.2% | 9.5% | 0.0% |
| Televisa Univision via SpringServe | 14,464 | 83.5% | 0.0% | 0.0% | 0.0% | 16.5% |

### Por país — relleno

|  | Filas | `rellena` | `sube` | `mantiene` | `corrige` | `sin_propuesta` |
|---|---:|---:|---:|---:|---:|---:|
| Mexico | 304,329 | 0.4% | 62.3% | 21.6% | 6.7% | 8.9% |
| Colombia | 101,514 | 0.3% | 70.5% | 20.4% | 3.5% | 5.3% |
| Chile | 107,269 | 0.2% | 72.4% | 18.9% | 5.0% | 3.6% |

### Por publisher — relleno

|  | Filas | `rellena` | `sube` | `mantiene` | `corrige` | `sin_propuesta` |
|---|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 200,221 | 0.0% | 77.8% | 21.0% | 0.7% | 0.4% |
| iion Pty Ltd | 183,090 | 0.2% | 75.2% | 15.5% | 1.4% | 7.7% |
| TCL ADS - Springserve | 120,000 | 0.2% | 76.6% | 16.2% | 1.8% | 5.3% |
| TCL ADs (APAC) | 112,769 | 0.1% | 78.3% | 15.6% | 1.9% | 4.1% |
| Select Plus PTE LTD (CTV) | 83,294 | 0.2% | 81.1% | 13.1% | 0.4% | 5.3% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 23,608 | 0.5% | 57.2% | 18.7% | 17.0% | 6.6% |
| PML Digital | 23,147 | 0.0% | 36.2% | 16.5% | 47.1% | 0.2% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 21,859 | 0.0% | 64.6% | 21.0% | 13.2% | 1.2% |
| AWG Media | 18,736 | 0.0% | 52.0% | 39.1% | 8.8% | 0.1% |
| Vidaa | 17,233 | 0.6% | 21.7% | 34.9% | 39.1% | 3.8% |
| Coocaa, a SKYWORTH company | 14,978 | 0.0% | 49.4% | 41.2% | 9.5% | 0.0% |
| Televisa Univision via SpringServe | 14,464 | 0.0% | 51.3% | 13.7% | 24.2% | 10.8% |

En el relleno, el origen dice de dónde salió el valor actual de la categoría; interesa sobre todo `derivado_genero` y `app_default`, que llenan con `[IAB1]` genérico (nivel 1) y son los que más pueden subir.

### Por origen del valor actual — relleno

|  | Filas | `rellena` | `sube` | `mantiene` | `corrige` | `sin_propuesta` |
|---|---:|---:|---:|---:|---:|---:|
| app_default | 83,934 | 0.0% | 70.5% | 21.0% | 8.5% | 0.0% |
| derivado_genero | 226,590 | 0.0% | 63.8% | 32.3% | 3.8% | 0.0% |
| derivado_tipo | 291,042 | 0.0% | 98.3% | 1.6% | 0.1% | 0.0% |
| intra_titulo | 93,404 | 0.0% | 64.9% | 28.0% | 7.1% | 0.0% |
| original | 209,901 | 0.0% | 52.4% | 35.2% | 12.5% | 0.0% |

## 5. Qué categorías se propondrían

**consolidado** — las 25 propuestas más frecuentes (IAB 2.2; % del total de filas):

| Propuesta (ruta 2.2) | Filas | % filas | % requests |
|---|---:|---:|---:|
| `Movies > Drama Movies | Television > Drama TV` | 48,860 | 5.1% | 5.3% |
| `Movies > Drama Movies` | 48,615 | 5.1% | 2.9% |
| `Movies > Horror Movies` | 37,539 | 3.9% | 2.8% |
| `Movies > Crime and Mystery Movies` | 32,589 | 3.4% | 2.3% |
| `Movies > Documentary Movies | Television > Factual TV` | 32,452 | 3.4% | 2.5% |
| `Television` | 28,981 | 3.0% | 2.5% |
| `Movies > Documentary Movies` | 22,900 | 2.4% | 1.4% |
| `Music and Audio` | 21,946 | 2.3% | 1.0% |
| `Movies > Comedy Movies` | 17,819 | 1.9% | 1.4% |
| `Television > Drama TV` | 17,393 | 1.8% | 2.6% |
| `Movies > Action and Adventure Movies` | 15,902 | 1.7% | 1.9% |
| `Sports` | 15,565 | 1.6% | 3.0% |
| `Movies > Comedy Movies | Television > Comedy TV` | 14,828 | 1.6% | 1.3% |
| `Movies > Horror Movies | Movies > Crime and Mystery Movies` | 14,077 | 1.5% | 0.8% |
| `Movies > Crime and Mystery Movies | Movies > Drama Movies` | 13,471 | 1.4% | 1.0% |
| `Movies > Drama Movies | Movies > Crime and Mystery Movies` | 13,387 | 1.4% | 1.3% |
| `Television > Drama TV | Television > Soap Opera TV` | 12,754 | 1.3% | 3.3% |
| `Movies` | 12,434 | 1.3% | 0.8% |
| `Movies > Drama Movies | Movies > Romance Movies` | 11,759 | 1.2% | 1.0% |
| `Television > Animation TV` | 10,291 | 1.1% | 0.8% |
| `Movies > Comedy Movies | Movies > Drama Movies` | 10,005 | 1.0% | 0.8% |
| `Television > Comedy TV` | 9,550 | 1.0% | 1.6% |
| `Television > Reality TV` | 9,366 | 1.0% | 1.1% |
| `Movies > Documentary Movies | Movies > Drama Movies` | 8,536 | 0.9% | 0.5% |
| `News and Politics` | 8,407 | 0.9% | 0.8% |

**relleno** — las 25 propuestas más frecuentes (IAB 2.2; % del total de filas):

| Propuesta (ruta 2.2) | Filas | % filas | % requests |
|---|---:|---:|---:|
| `Movies > Drama Movies` | 56,229 | 5.9% | 3.3% |
| `Movies > Drama Movies | Television > Drama TV` | 41,202 | 4.3% | 4.9% |
| `Movies > Horror Movies` | 37,539 | 3.9% | 2.8% |
| `Movies > Crime and Mystery Movies` | 32,584 | 3.4% | 2.3% |
| `Movies > Documentary Movies | Television > Factual TV` | 29,967 | 3.1% | 2.2% |
| `Movies > Documentary Movies` | 25,362 | 2.6% | 1.7% |
| `Television` | 25,003 | 2.6% | 2.1% |
| `Movies > Comedy Movies` | 20,572 | 2.1% | 1.5% |
| `Television > Drama TV` | 17,403 | 1.8% | 2.6% |
| `Movies > Action and Adventure Movies` | 15,900 | 1.7% | 1.9% |
| `Movies > Drama Movies | Movies > Crime and Mystery Movies` | 14,873 | 1.6% | 1.4% |
| `Movies > Horror Movies | Movies > Crime and Mystery Movies` | 14,077 | 1.5% | 0.8% |
| `Movies > Crime and Mystery Movies | Movies > Drama Movies` | 13,934 | 1.4% | 1.1% |
| `Movies > Drama Movies | Movies > Romance Movies` | 13,341 | 1.4% | 1.0% |
| `Movies > Comedy Movies | Movies > Drama Movies` | 13,089 | 1.4% | 1.1% |
| `Television > Drama TV | Television > Soap Opera TV` | 12,754 | 1.3% | 3.3% |
| `Movies > Comedy Movies | Television > Comedy TV` | 12,075 | 1.3% | 1.2% |
| `Television > Animation TV` | 10,583 | 1.1% | 0.8% |
| `Television > Comedy TV` | 9,558 | 1.0% | 1.6% |
| `Television > Reality TV` | 9,366 | 1.0% | 1.1% |
| `Movies > Comedy Movies | Movies > Drama Movies | Movies > Romance Movies` | 8,999 | 0.9% | 0.5% |
| `Movies > Documentary Movies | Movies > Drama Movies` | 8,789 | 0.9% | 0.5% |
| `Movies > Action and Adventure Movies | Movies > Crime and Mystery Movies` | 8,126 | 0.8% | 0.5% |
| `Movies > Drama Movies | Movies > Horror Movies | Movies > Crime and Mystery Movies` | 7,547 | 0.8% | 0.4% |
| `Movies > Romance Movies` | 7,248 | 0.8% | 0.7% |

Reglas que generaron las propuestas en **consolidado** (evidencia · vertical · forma · origen de la forma):

| Regla | Filas | % filas |
|---|---:|---:|
| `externa|entretenimiento|pelicula|imdb` | 320,482 | 33.4% |
| `interna|entretenimiento|-|-` | 178,298 | 18.6% |
| `externa|entretenimiento|-|-` | 63,260 | 6.6% |
| `externa|entretenimiento|tv|imdb` | 52,312 | 5.5% |
| `interna|entretenimiento|tv|titulo` | 17,857 | 1.9% |
| `externa|entretenimiento|tv|titulo` | 17,165 | 1.8% |
| `interna|entretenimiento|tv|contentSeries` | 14,870 | 1.6% |
| `interna|musica|-|-` | 13,236 | 1.4% |
| `interna|deportes|-|-` | 12,867 | 1.3% |
| `ninguna|entretenimiento|pelicula|genero` | 9,897 | 1.0% |
| `serie|entretenimiento|tv|contentSeries` | 9,816 | 1.0% |
| `interna|entretenimiento|tv|genero` | 8,223 | 0.9% |
| `interna|entretenimiento|pelicula|declarado` | 6,477 | 0.7% |
| `interna|noticias|-|-` | 6,366 | 0.7% |
| `externa|deportes|pelicula|imdb` | 4,758 | 0.5% |
| `ninguna|entretenimiento|tv|titulo` | 4,013 | 0.4% |
| `interna|viajes|-|-` | 3,949 | 0.4% |
| `externa|musica|pelicula|imdb` | 3,601 | 0.4% |
| `externa|musica|-|-` | 3,481 | 0.4% |
| `interna|deportes|tv|contentSeries` | 3,101 | 0.3% |

## 6. Qué haría falta para llegar más lejos

- **Las filas sin título real** (placeholders `epg`/`roku`, canales, macros) solo pueden subir por el género declarado: a nivel 2 (par película+TV del género) o 1. La forma real de esas filas solo la sabe el vendedor.
- **Sub-deporte**: se detecta por palabra en el género o el título (`soccer`, `boxeo`, `NBA`…). "Football" se mapea a fútbol americano como manda IAB 1.0 (`IAB17-12`); si el vendedor lo usa como fútbol, corregirlo aquí es una decisión de negocio, no de dato.
- **Verticales temáticas de la no ficción** (viajes, cocina, tecnología): no salen de IMDb. Se conservan cuando el vendedor las declara; para proponerlas desde cero haría falta TMDB keywords o Wikidata P921.
- **IAB 3.0** separa forma y género en ramas distintas (`Entertainment > Movies` + `Genres > Drama`); la propuesta 2.2 se traduce directo (`333` → `324` + `647`) si el comprador la pide.
