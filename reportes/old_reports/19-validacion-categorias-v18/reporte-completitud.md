# contentCategory, parte 2: ¿se puede poner una categoría más fina?

**Fuentes:** `inventory-consolidado-v10-a-v18.csv` (1,071,840 filas, columna `contentCategory`); `inventory-consolidado-v10-a-v18-relleno.csv` (1,071,840 filas, columna `contentCategory_relleno`).  
**Generado con:** `scripts/validar_categorias.py` + `scripts/generar_reporte_validacion.py`. Corrida del 2026-09-15 09:42. Las propuestas se escriben en IAB Content Taxonomy **2.2** (la última que tiene géneros bajo Películas/Televisión y unos 70 deportes) y traen su equivalente en **1.0** (la que usan casi todas las filas que ya vienen con categoría).

## Cómo leer este reporte

- **Fila**: cada fila del inventario es una combinación de país, publisher, app y metadata de contenido, no un programa ni un evento. **Requests** son las solicitudes de anuncio que trae esa fila; por eso cada cifra se da en filas y en requests.
- **Tal como llega (consolidado)** es el inventario tal como lo mandan los vendedores. **Después del relleno** es el mismo inventario después de que el pipeline de relleno (`enriquecer_externo.py`) completó las categorías vacías; se validan los dos para saber si el relleno acierta.
- **Categoría IAB**: el código de `contentCategory` (por ejemplo `[IAB1-5]` = Entretenimiento > Películas). Una categoría afirma hasta tres cosas: la **vertical** (entretenimiento, noticias, deportes…), la **forma** (película o televisión) y el **género** (drama, terror…).
- **Evidencia**: contra qué se compara la categoría. *IMDb / Wikidata*: el título de la fila se encontró en esas bases (un **match**), que dicen si es película o serie y qué géneros tiene; cubre 531,080 filas (49.5% del total). *Solo el género de la fila*: no hay match, pero el `contentGenre` de la misma fila permite juzgar (un drama no es Noticias). *Sin evidencia*: no hay contra qué comparar.
- **Confianza del match**: A = el título coincide sin ambigüedad; B = coincide pero podría ser otro título homónimo (acierta ~3 de cada 4). Se usan matches de confianza B o mejor.
- **Formato de las celdas**: `12,345 filas (12.3%) · 4.5% req` = cantidad de filas, % de filas y % de requests sobre la base que indica cada tabla.
- **Nivel de detalle** de una categoría: cuenta cuántas cosas dice. **Nivel 0** = nada. **Nivel 1** = solo la vertical (`[IAB1]` Entretenimiento, `[IAB12]` Noticias). **Nivel 2** = vertical + forma (`[IAB1-5]` Películas, `[640]` Televisión) o vertical + deporte concreto (`[IAB17-44]` Soccer). **Nivel 3** = vertical + forma + género (`[333]` Drama Movies, `[651]` Reality TV). Se mide así para poder comparar categorías escritas en distintas taxonomías.

**Base de los porcentajes en este reporte:** sobre el **total de filas** del dataset (con y sin categoría), salvo en las tablas por país, publisher u origen, donde son sobre las filas del grupo.

---

## 1. Punto de partida

Cada fila está en uno de tres estados: **sin categoría** (vacía o con basura como `[-7]`), **con categoría correcta o genérica**, o **con categoría incorrecta** (la evidencia la contradice; ver el reporte de la parte 1).

| Dataset | Filas totales | Sin categoría | Con categoría correcta o genérica | Con categoría incorrecta |
|---|---:|---:|---:|---:|
| **Tal como llega (consolidado)** | 1,071,840 | 837,542 filas (78.1%) · 69.2% req | 205,334 filas (19.2%) · 27.3% req | 28,964 filas (2.7%) · 3.5% req |
| **Después del relleno** | 1,071,840 | 63,290 filas (5.9%) · 11.9% req | 955,160 filas (89.1%) · 80.2% req | 53,390 filas (5.0%) · 7.9% req |

Qué nivel de detalle tienen hoy (% del total de filas):

| Estado · nivel de detalle actual | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Con categoría incorrecta · Nivel 1 · solo la vertical (`contradicha|1`) | 17,636 filas (1.6%) · 2.0% req | 33,614 filas (3.1%) · 6.1% req |
| Con categoría incorrecta · Nivel 2 · vertical + película/TV (o deporte) (`contradicha|2`) | 9,428 filas (0.9%) · 1.5% req | 17,799 filas (1.7%) · 1.8% req |
| Con categoría incorrecta · Nivel 3 · vertical + película/TV + género (`contradicha|3`) | 1,900 filas (0.2%) · 0.0% req | 1,977 filas (0.2%) · 0.0% req |
| Con categoría (correcta o genérica) · Nivel 0 · nada (`llena|0`) | 3,236 filas (0.3%) · 0.2% req | 3,298 filas (0.3%) · 0.2% req |
| Con categoría (correcta o genérica) · Nivel 1 · solo la vertical (`llena|1`) | 129,836 filas (12.1%) · 11.1% req | 519,677 filas (48.5%) · 40.8% req |
| Con categoría (correcta o genérica) · Nivel 2 · vertical + película/TV (o deporte) (`llena|2`) | 62,662 filas (5.8%) · 15.6% req | 422,535 filas (39.4%) · 38.9% req |
| Con categoría (correcta o genérica) · Nivel 3 · vertical + película/TV + género (`llena|3`) | 9,600 filas (0.9%) · 0.3% req | 9,650 filas (0.9%) · 0.3% req |
| Sin categoría · Nivel 0 · nada (`vacia|0`) | 837,542 filas (78.1%) · 69.2% req | 63,290 filas (5.9%) · 11.9% req |

## 2. Hasta dónde llega la evidencia

Para cada fila se calcula la categoría más detallada que la evidencia permite justificar. Primero, qué evidencia hay:

| Evidencia disponible para la fila | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| IMDb / Wikidata (`externa`) | 531,080 filas (49.5%) · 36.7% req | 531,080 filas (49.5%) · 36.7% req |
| Solo el género de la fila (`interna`) | 362,578 filas (33.8%) · 38.2% req | 362,578 filas (33.8%) · 38.2% req |
| Sin evidencia (`ninguna`) | 165,569 filas (15.4%) · 23.7% req | 165,569 filas (15.4%) · 23.7% req |
| Solo el nombre de serie (`serie`) | 12,613 filas (1.2%) · 1.4% req | 12,613 filas (1.2%) · 1.4% req |

Segundo, de dónde sale la **forma** (película o TV), que es lo que separa el nivel 1 del 2. Se toma la primera fuente disponible en este orden: el tipo que da IMDb, un nombre de serie real en la fila, lo que ya decía la categoría, un género que la implica, o temporada/episodio en el título.

| De dónde sale la forma | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Trae nombre de serie → TV (`contentSeries`) | 47,287 filas (4.4%) · 4.9% req | 47,287 filas (4.4%) · 4.9% req |
| Ya lo decía la categoría (`declarado`) | 30,905 filas (2.9%) · 8.0% req | 104,804 filas (9.8%) · 12.2% req |
| Lo implica el género (telenovela, reality → TV) (`genero`) | 26,824 filas (2.5%) · 1.3% req | 11,922 filas (1.1%) · 0.5% req |
| El tipo de IMDb (`imdb`) | 431,142 filas (40.2%) · 30.6% req | 431,142 filas (40.2%) · 30.6% req |
| No se sabe (`sin_forma`) | 488,222 filas (45.5%) · 52.2% req | 429,225 filas (40.0%) · 48.8% req |
| El título trae temporada/episodio → TV (`titulo`) | 47,460 filas (4.4%) · 3.1% req | 47,460 filas (4.4%) · 3.1% req |

Tercero, el nivel de detalle que se podría alcanzar (% del total de filas). Si una fila ya trae una categoría correcta con nivel igual o mejor que el alcanzable, se conserva lo que trae:

| Nivel de detalle alcanzable | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Nivel 0 · nada | 77,776 filas (7.3%) · 12.7% req | 60,945 filas (5.7%) · 11.8% req |
| Nivel 1 · solo la vertical | 150,181 filas (14.0%) · 13.3% req | 162,467 filas (15.2%) · 14.0% req |
| Nivel 2 · vertical + película/TV (o deporte) | 356,913 filas (33.3%) · 36.9% req | 304,105 filas (28.4%) · 33.6% req |
| Nivel 3 · vertical + película/TV + género | 486,970 filas (45.4%) · 37.1% req | 544,323 filas (50.8%) · 40.5% req |

## 3. Qué cambiaría fila a fila

Comparando lo que trae cada fila con lo que la evidencia permite:

| Qué pasa con la fila | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 760,337 filas (70.9%) · 56.5% req | 2,920 filas (0.3%) · 0.1% req |
| Se puede afinar (estaba llena) (`sube`) | 122,833 filas (11.5%) · 10.5% req | 738,712 filas (68.9%) · 54.5% req |
| Se queda igual (ya está bien) (`mantiene`) | 82,501 filas (7.7%) · 16.8% req | 216,448 filas (20.2%) · 25.7% req |
| Se puede corregir (estaba incorrecta) (`corrige`) | 28,964 filas (2.7%) · 3.5% req | 53,390 filas (5.0%) · 7.9% req |
| Sin propuesta (vacía y sin evidencia) (`sin_propuesta`) | 77,205 filas (7.2%) · 12.7% req | 60,370 filas (5.6%) · 11.8% req |

Detalle de los movimientos de nivel: estado actual y nivel actual → nivel alcanzable (% del total de filas; solo combinaciones con al menos 0.5%):

**Tal como llega (consolidado)**:

| Movimiento | Filas | % de filas | % de requests |
|---|---:|---:|---:|
| Sin categoría, nivel 0 → nivel 3 (`vacia|0->3`) | 384,439 | 35.9% | 27.9% |
| Sin categoría, nivel 0 → nivel 2 (`vacia|0->2`) | 271,099 | 25.3% | 21.3% |
| Sin categoría, nivel 0 → nivel 1 (`vacia|0->1`) | 104,799 | 9.8% | 7.3% |
| Sin categoría, nivel 0 → nivel 0 (`vacia|0->0`) | 77,205 | 7.2% | 12.7% |
| Con categoría (correcta o genérica), nivel 1 → nivel 2 (`llena|1->2`) | 43,482 | 4.1% | 3.1% |
| Con categoría (correcta o genérica), nivel 1 → nivel 3 (`llena|1->3`) | 43,224 | 4.0% | 2.2% |
| Con categoría (correcta o genérica), nivel 1 → nivel 1 (`llena|1->1`) | 43,130 | 4.0% | 5.8% |
| Con categoría (correcta o genérica), nivel 2 → nivel 3 (`llena|2->3`) | 33,462 | 3.1% | 5.0% |
| Con categoría (correcta o genérica), nivel 2 → nivel 2 (`llena|2->2`) | 29,200 | 2.7% | 10.7% |
| Con categoría incorrecta, nivel 1 → nivel 3 (`contradicha|1->3`) | 10,397 | 1.0% | 1.3% |
| Con categoría (correcta o genérica), nivel 3 → nivel 3 (`llena|3->3`) | 9,600 | 0.9% | 0.3% |
| Con categoría incorrecta, nivel 1 → nivel 2 (`contradicha|1->2`) | 6,592 | 0.6% | 0.7% |

**Después del relleno**:

| Movimiento | Filas | % de filas | % de requests |
|---|---:|---:|---:|
| Con categoría (correcta o genérica), nivel 2 → nivel 3 (`llena|2->3`) | 375,658 | 35.0% | 27.3% |
| Con categoría (correcta o genérica), nivel 1 → nivel 2 (`llena|1->2`) | 235,515 | 22.0% | 19.4% |
| Con categoría (correcta o genérica), nivel 1 → nivel 1 (`llena|1->1`) | 159,346 | 14.9% | 13.8% |
| Con categoría (correcta o genérica), nivel 1 → nivel 3 (`llena|1->3`) | 124,816 | 11.7% | 7.6% |
| Sin categoría, nivel 0 → nivel 0 (`vacia|0->0`) | 60,370 | 5.6% | 11.8% |
| Con categoría (correcta o genérica), nivel 2 → nivel 2 (`llena|2->2`) | 46,877 | 4.4% | 11.6% |
| Con categoría incorrecta, nivel 1 → nivel 3 (`contradicha|1->3`) | 20,282 | 1.9% | 4.6% |
| Con categoría incorrecta, nivel 2 → nivel 3 (`contradicha|2->3`) | 12,956 | 1.2% | 0.7% |
| Con categoría incorrecta, nivel 1 → nivel 2 (`contradicha|1->2`) | 12,221 | 1.1% | 1.4% |
| Con categoría (correcta o genérica), nivel 3 → nivel 3 (`llena|3->3`) | 9,650 | 0.9% | 0.3% |

## 4. Por país, publisher y origen

Cada fila de estas tablas es un grupo; los % son sobre las filas del grupo. Las columnas son los mismos movimientos de la sección 3.

### Por país — Tal como llega (consolidado)

| País | Filas | Se puede llenar (estaba vacía) | Se puede afinar (estaba llena) | Se queda igual (ya está bien) | Se puede corregir (estaba incorrecta) | Sin propuesta (vacía y sin evidencia) |
|---|---:|---:|---:|---:|---:|---:|
| Mexico | 328,845 | 65.3% | 11.0% | 8.7% | 4.2% | 10.8% |
| Colombia | 114,223 | 71.1% | 12.2% | 7.6% | 2.5% | 6.7% |
| Chile | 122,923 | 78.8% | 9.0% | 5.6% | 0.9% | 5.7% |

### Por publisher — Tal como llega (consolidado)

| Publisher | Filas | Se puede llenar (estaba vacía) | Se puede afinar (estaba llena) | Se queda igual (ya está bien) | Se puede corregir (estaba incorrecta) | Sin propuesta (vacía y sin evidencia) |
|---|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 220,835 | 57.9% | 30.2% | 7.2% | 0.3% | 4.3% |
| iion Pty Ltd | 207,466 | 90.2% | 0.3% | 0.3% | 0.0% | 9.2% |
| TCL ADS - Springserve | 133,483 | 92.5% | 0.5% | 0.2% | 0.0% | 6.8% |
| TCL ADs (APAC) | 126,143 | 93.8% | 0.6% | 0.3% | 0.0% | 5.4% |
| Select Plus PTE LTD (CTV) | 96,962 | 93.0% | 0.0% | 0.0% | 0.0% | 7.0% |
| PML Digital | 26,250 | 73.4% | 4.1% | 2.9% | 15.7% | 3.9% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 25,773 | 26.1% | 44.8% | 15.6% | 11.7% | 1.9% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 25,730 | 66.8% | 7.0% | 9.6% | 8.3% | 8.3% |
| AWG Media | 20,424 | 5.3% | 48.2% | 37.7% | 8.7% | 0.1% |
| Vidaa | 19,325 | 9.0% | 15.6% | 32.3% | 38.4% | 4.7% |
| Televisa Univision via SpringServe | 15,690 | 84.1% | 0.0% | 0.0% | 0.0% | 15.9% |
| Coocaa, a SKYWORTH company | 15,655 | 0.0% | 49.1% | 41.8% | 9.1% | 0.0% |

### Por país — Después del relleno

| País | Filas | Se puede llenar (estaba vacía) | Se puede afinar (estaba llena) | Se queda igual (ya está bien) | Se puede corregir (estaba incorrecta) | Sin propuesta (vacía y sin evidencia) |
|---|---:|---:|---:|---:|---:|---:|
| Mexico | 328,845 | 0.4% | 62.1% | 22.0% | 6.9% | 8.6% |
| Colombia | 114,223 | 0.3% | 70.1% | 20.3% | 3.7% | 5.6% |
| Chile | 122,923 | 0.2% | 72.3% | 18.7% | 4.5% | 4.3% |

### Por publisher — Después del relleno

| Publisher | Filas | Se puede llenar (estaba vacía) | Se puede afinar (estaba llena) | Se queda igual (ya está bien) | Se puede corregir (estaba incorrecta) | Sin propuesta (vacía y sin evidencia) |
|---|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 220,835 | 0.0% | 77.8% | 20.9% | 0.7% | 0.5% |
| iion Pty Ltd | 207,466 | 0.2% | 75.1% | 15.5% | 1.3% | 8.0% |
| TCL ADS - Springserve | 133,483 | 0.2% | 76.6% | 15.9% | 1.6% | 5.7% |
| TCL ADs (APAC) | 126,143 | 0.2% | 78.3% | 15.0% | 1.7% | 4.8% |
| Select Plus PTE LTD (CTV) | 96,962 | 0.2% | 80.4% | 12.7% | 0.4% | 6.4% |
| PML Digital | 26,250 | 0.0% | 37.2% | 16.6% | 46.0% | 0.2% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 25,773 | 0.0% | 65.5% | 20.1% | 12.5% | 1.9% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 25,730 | 0.5% | 57.2% | 19.0% | 17.0% | 6.3% |
| AWG Media | 20,424 | 0.0% | 52.0% | 39.2% | 8.7% | 0.1% |
| Vidaa | 19,325 | 0.5% | 21.9% | 35.9% | 38.5% | 3.3% |
| Televisa Univision via SpringServe | 15,690 | 0.0% | 51.2% | 13.5% | 24.7% | 10.5% |
| Coocaa, a SKYWORTH company | 15,655 | 0.0% | 49.1% | 41.8% | 9.1% | 0.0% |

En el dataset rellenado, el **origen** dice de dónde salió la categoría actual. Los orígenes que llenan con una vertical genérica (`[IAB1]`, nivel 1) son los que más pueden subir.

### Por origen del valor actual — Después del relleno

| Origen del valor | Filas | Se puede llenar (estaba vacía) | Se puede afinar (estaba llena) | Se queda igual (ya está bien) | Se puede corregir (estaba incorrecta) | Sin propuesta (vacía y sin evidencia) |
|---|---:|---:|---:|---:|---:|---:|
| Valor habitual de la app (`app_default`) | 89,387 | 0.0% | 70.6% | 20.7% | 8.8% | 0.0% |
| Derivado del género (`derivado_genero`) | 245,173 | 0.0% | 65.0% | 31.3% | 3.6% | 0.0% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 323,918 | 0.0% | 98.2% | 1.7% | 0.1% | 0.0% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 115,774 | 0.0% | 65.0% | 28.6% | 6.4% | 0.0% |
| Venía del vendedor (`original`) | 234,298 | 0.0% | 52.4% | 35.2% | 12.4% | 0.0% |

## 5. Qué categorías se propondrían

Cuando aparecen dos rutas separadas por `|` (por ejemplo `Movies > Drama Movies | Television > Drama TV`) es porque no se sabe si la fila es película o TV y se propone el par del mismo género.

**Tal como llega (consolidado)** — las 25 propuestas más frecuentes (IAB 2.2; % del total de filas):

| Categoría propuesta (ruta IAB 2.2) | Filas | % de filas | % de requests |
|---|---:|---:|---:|
| `Movies > Drama Movies | Television > Drama TV` | 55,474 | 5.2% | 6.2% |
| `Movies > Drama Movies` | 54,413 | 5.1% | 3.1% |
| `Movies > Horror Movies` | 41,499 | 3.9% | 3.1% |
| `Movies > Documentary Movies | Television > Factual TV` | 38,123 | 3.6% | 2.8% |
| `Movies > Crime and Mystery Movies` | 36,169 | 3.4% | 2.4% |
| `Television` | 32,646 | 3.0% | 2.4% |
| `Movies > Documentary Movies` | 26,153 | 2.4% | 1.6% |
| `Music and Audio` | 22,454 | 2.1% | 0.6% |
| `Movies > Comedy Movies` | 19,872 | 1.9% | 1.4% |
| `Television > Drama TV` | 19,031 | 1.8% | 2.4% |
| `Movies > Action and Adventure Movies` | 18,904 | 1.8% | 2.3% |
| `Movies > Comedy Movies | Television > Comedy TV` | 16,960 | 1.6% | 1.5% |
| `Sports` | 16,861 | 1.6% | 3.3% |
| `Movies > Horror Movies | Movies > Crime and Mystery Movies` | 15,616 | 1.5% | 0.9% |
| `Movies > Crime and Mystery Movies | Movies > Drama Movies` | 14,764 | 1.4% | 1.1% |
| `Movies > Drama Movies | Movies > Crime and Mystery Movies` | 14,657 | 1.4% | 1.4% |
| `Television > Drama TV | Television > Soap Opera TV` | 14,009 | 1.3% | 3.2% |
| `Movies` | 13,967 | 1.3% | 0.7% |
| `Movies > Drama Movies | Movies > Romance Movies` | 12,930 | 1.2% | 1.0% |
| `Television > Animation TV` | 11,973 | 1.1% | 1.1% |
| `Movies > Comedy Movies | Movies > Drama Movies` | 11,244 | 1.1% | 0.8% |
| `Television > Comedy TV` | 10,620 | 1.0% | 1.6% |
| `Television > Reality TV` | 10,361 | 1.0% | 1.2% |
| `Movies > Documentary Movies | Movies > Drama Movies` | 9,659 | 0.9% | 0.6% |
| `News and Politics` | 9,145 | 0.8% | 0.8% |

**Después del relleno** — las 25 propuestas más frecuentes (IAB 2.2; % del total de filas):

| Categoría propuesta (ruta IAB 2.2) | Filas | % de filas | % de requests |
|---|---:|---:|---:|
| `Movies > Drama Movies` | 62,938 | 5.9% | 3.5% |
| `Movies > Drama Movies | Television > Drama TV` | 46,905 | 4.4% | 5.8% |
| `Movies > Horror Movies` | 41,499 | 3.9% | 3.1% |
| `Movies > Crime and Mystery Movies` | 36,163 | 3.4% | 2.4% |
| `Movies > Documentary Movies | Television > Factual TV` | 35,288 | 3.3% | 2.4% |
| `Movies > Documentary Movies` | 28,976 | 2.7% | 1.9% |
| `Television` | 28,193 | 2.6% | 2.1% |
| `Movies > Comedy Movies` | 22,935 | 2.1% | 1.5% |
| `Television > Drama TV` | 19,042 | 1.8% | 2.4% |
| `Movies > Action and Adventure Movies` | 18,902 | 1.8% | 2.3% |
| `Movies > Drama Movies | Movies > Crime and Mystery Movies` | 16,355 | 1.5% | 1.4% |
| `Movies > Horror Movies | Movies > Crime and Mystery Movies` | 15,616 | 1.5% | 0.9% |
| `Movies > Crime and Mystery Movies | Movies > Drama Movies` | 15,294 | 1.4% | 1.1% |
| `Movies > Drama Movies | Movies > Romance Movies` | 14,688 | 1.4% | 1.1% |
| `Movies > Comedy Movies | Movies > Drama Movies` | 14,667 | 1.4% | 1.1% |
| `Television > Drama TV | Television > Soap Opera TV` | 14,009 | 1.3% | 3.2% |
| `Movies > Comedy Movies | Television > Comedy TV` | 13,897 | 1.3% | 1.4% |
| `Television > Animation TV` | 12,311 | 1.1% | 1.1% |
| `Television > Comedy TV` | 10,628 | 1.0% | 1.6% |
| `Television > Reality TV` | 10,361 | 1.0% | 1.2% |
| `Movies > Documentary Movies | Movies > Drama Movies` | 9,967 | 0.9% | 0.6% |
| `Movies > Comedy Movies | Movies > Drama Movies | Movies > Romance Movies` | 9,931 | 0.9% | 0.5% |
| `Movies > Action and Adventure Movies | Movies > Crime and Mystery Movies` | 8,880 | 0.8% | 0.4% |
| `Movies > Romance Movies` | 8,340 | 0.8% | 0.9% |
| `Movies > Drama Movies | Movies > Horror Movies | Movies > Crime and Mystery Movies` | 8,297 | 0.8% | 0.4% |

Con qué evidencia se generaron las propuestas en **Tal como llega (consolidado)**. Cada regla dice: qué evidencia se usó, qué vertical se propuso, qué forma (película / TV / sin forma) y de dónde salió esa forma:

| Evidencia | Vertical propuesta | Forma | De dónde sale la forma | Filas | % de filas |
|---|---|---|---|---:|---:|
| IMDb / Wikidata | Entretenimiento | película | El tipo de IMDb | 356,193 | 33.2% |
| Solo el género de la fila | Entretenimiento | sin forma | — | 200,167 | 18.7% |
| IMDb / Wikidata | Entretenimiento | sin forma | — | 71,242 | 6.7% |
| IMDb / Wikidata | Entretenimiento | TV | El tipo de IMDb | 58,626 | 5.5% |
| Solo el género de la fila | Entretenimiento | TV | El título trae temporada/episodio → TV | 20,777 | 1.9% |
| IMDb / Wikidata | Entretenimiento | TV | El título trae temporada/episodio → TV | 19,604 | 1.8% |
| Solo el género de la fila | Entretenimiento | TV | Trae nombre de serie → TV | 15,974 | 1.5% |
| Solo el género de la fila | Deportes | sin forma | — | 14,014 | 1.3% |
| Solo el género de la fila | Música | sin forma | — | 13,236 | 1.2% |
| Sin evidencia | Entretenimiento | película | Lo implica el género (telenovela, reality → TV) | 11,221 | 1.1% |
| Solo el nombre de serie | Entretenimiento | TV | Trae nombre de serie → TV | 10,731 | 1.0% |
| Solo el género de la fila | Entretenimiento | TV | Lo implica el género (telenovela, reality → TV) | 9,017 | 0.8% |
| Solo el género de la fila | Entretenimiento | película | Ya lo decía la categoría | 7,418 | 0.7% |
| Solo el género de la fila | Noticias | sin forma | — | 6,918 | 0.7% |
| IMDb / Wikidata | Deportes | película | El tipo de IMDb | 4,940 | 0.5% |
| Sin evidencia | Entretenimiento | TV | El título trae temporada/episodio → TV | 4,734 | 0.4% |
| Solo el género de la fila | Viajes | sin forma | — | 3,949 | 0.4% |
| IMDb / Wikidata | Música | sin forma | — | 3,781 | 0.3% |
| IMDb / Wikidata | Música | película | El tipo de IMDb | 3,741 | 0.3% |
| Solo el género de la fila | Deportes | TV | Trae nombre de serie → TV | 3,260 | 0.3% |

## 6. Qué haría falta para llegar más lejos

- **Las filas sin título real** (rellenos como `epg` o `roku`, nombres de canal, macros) solo pueden subir por el género declarado: a nivel 2 (el par película + TV del género) o a nivel 1. Si son película o TV solo lo sabe el vendedor.
- **Deporte concreto**: se detecta por palabras en el género o el título (`soccer`, `boxeo`, `NBA`…). "Football" se mapea a fútbol americano como manda IAB 1.0 (`IAB17-12`); si el vendedor lo usa como fútbol, corregirlo es una decisión de negocio, no de dato.
- **Temas de la no ficción** (viajes, cocina, tecnología): IMDb no los registra. Se conservan cuando el vendedor los declara; para proponerlos desde cero haría falta TMDB (keywords) o Wikidata P921.
- **IAB 3.0** separa forma y género en ramas distintas (`Entertainment > Movies` + `Genres > Drama`); la propuesta 2.2 se traduce directo (`333` → `324` + `647`) si un comprador la pide.
