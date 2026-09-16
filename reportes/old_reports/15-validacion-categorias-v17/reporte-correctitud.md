# Reporte — Correctitud de contentCategory: las filas llenas, ¿están bien llenadas?

**Fuentes:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas, columna `contentCategory`); `inventory-consolidado-v10-a-v17-relleno.csv` (959,442 filas, columna `contentCategory_relleno`).  
**Generado con:** `scripts/validar_categorias.py` (un JSON por dataset) + `scripts/generar_reporte_validacion.py`. Corrida del 2026-09-09 15:31. Evidencia externa: match IMDb de confianza ≥ B más géneros de Wikidata, desde `cache-enriquecimiento/titulos.json` (14,686 títulos); taxonomías IAB Content Taxonomy 1.0 (392 nodos), 2.2 (1196) y 3.0 (703) oficiales de IAB Tech Lab.

**Convención:** salvo que se diga otra cosa, los % son **% de las filas que traen categoría** (no del total del consolidado); cuando se dice "de las evaluables" es sobre las filas con categoría que además tienen evidencia para juzgarla. Cada tabla trae también el % de requests cuando aporta.

---

## 1. Universo: qué se pudo evaluar

Una fila solo se puede juzgar si hay contra qué. La evidencia **externa** (título real con match IMDb/Wikidata) prueba vertical, forma (película/TV) y género; la **interna** (el `contentGenre` de la misma fila) solo prueba lo que un género implica: que un drama no es noticias, que un talk show no es película. Sin ninguna de las dos, la fila queda `no_evaluable`.

| Dataset | Filas | Con categoría (% total) | % requests con categoría | Con match externo (% total) | Evidencia externa (de las llenas) | Evidencia interna | Sin evidencia |
|---|---:|---:|---:|---:|---:|---:|---:|
| **consolidado** | 959,442 | 209,901 (21.9%) | 32.5% | 476,869 (49.7%) | 71,531 (34.1%) · req 16.1% | 102,980 (49.1%) · req 54.5% | 35,390 (16.9%) · req 29.4% |
| **relleno** | 959,442 | 904,871 (94.3%) | 86.5% | 476,869 (49.7%) | 476,417 (52.6%) · req 40.9% | 341,926 (37.8%) · req 44.8% | 86,528 (9.6%) · req 14.3% |

## 2. Formato: qué taxonomía usan los valores declarados

Antes de juzgar el contenido, el continente: un valor cuenta como **estándar** si todos sus códigos existen en IAB 1.0 (`IAB1-5`) o en 2.2/3.0 (`333`); **no_estandar** si tiene la forma de un código pero no existe (`IAB1-22`, `IAB-7`, `IAB1-6-3`); **texto_libre** si no es un código (`sports`, `Live`, `Entertainment`). Los códigos 1000+ de 2.2 (`1070` = Content Language > Spanish, `1004` = Content Channel > Game) existen pero **no son categorías de contenido**: se reportan como metadato.

| Formato | consolidado | relleno |
|---|---:|---:|
| `estandar` | 176,018 (83.9%) · req 93.8% | 836,032 (92.4%) · req 94.1% |
| `estandar;no_estandar;texto_libre` | 1 (0.0%) · req 0.0% | 1 (0.0%) · req 0.0% |
| `estandar;texto_libre` | 99 (0.1%) · req 0.0% | 99 (0.0%) · req 0.0% |
| `no_estandar` | 26,437 (12.6%) · req 5.6% | 49,815 (5.5%) · req 4.4% |
| `texto_libre` | 7,346 (3.5%) · req 0.6% | 18,924 (2.1%) · req 1.5% |

Por taxonomía (un valor puede mezclar varias):

| Taxonomía | consolidado | relleno |
|---|---:|---:|
| `1.0` | 186,646 (88.9%) · req 98.0% | 869,921 (96.1%) · req 98.0% |
| `1.0;ninguna` | 91 (0.0%) · req 0.0% | 91 (0.0%) · req 0.0% |
| `2.2` | 15,809 (7.5%) · req 1.3% | 15,926 (1.8%) · req 0.5% |
| `2.2;ninguna` | 9 (0.0%) · req 0.0% | 9 (0.0%) · req 0.0% |
| `ninguna` | 7,346 (3.5%) · req 0.6% | 18,924 (2.1%) · req 1.5% |

Los 20 valores más frecuentes en **consolidado** (de 209,901 filas con categoría):

| Valor | Filas | % filas | % requests |
|---|---:|---:|---:|
| `[IAB1]` | 53,399 | 25.4% | 11.4% |
| `[IAB1-22]` | 25,883 | 12.3% | 5.0% |
| `[IAB12]` | 21,042 | 10.0% | 8.4% |
| `[IAB1-5]` | 15,819 | 7.5% | 4.7% |
| `[IAB17]` | 9,940 | 4.7% | 3.9% |
| `[IAB1-7]` | 9,872 | 4.7% | 19.1% |
| `[IAB1, IAB1-5]` | 9,413 | 4.5% | 2.0% |
| `[IAB1-5, IAB1-7]` | 5,820 | 2.8% | 14.9% |
| `[IAB1-7, IAB17-12]` | 4,990 | 2.4% | 2.5% |
| `[sports]` | 4,752 | 2.3% | 0.3% |
| `[IAB1-6]` | 3,724 | 1.8% | 1.7% |
| `[640]` | 3,106 | 1.5% | 0.2% |
| `[IAB1, IAB1-5, IAB1-7]` | 2,840 | 1.4% | 0.3% |
| `[IAB17-1]` | 2,776 | 1.3% | 1.4% |
| `[Live]` | 1,816 | 0.9% | 0.3% |
| `[IAB9-30]` | 1,676 | 0.8% | 0.2% |
| `[325]` | 1,472 | 0.7% | 0.1% |
| `[647]` | 1,373 | 0.7% | 0.1% |
| `[IAB20]` | 1,360 | 0.7% | 0.6% |
| `[324]` | 1,322 | 0.6% | 0.1% |

## 3. Veredicto

Sobre las filas **evaluables**: `coincide` = algún código declarado acierta en lo más fino que declara (la forma o el género) y ninguno contradice; `compatible` = no contradice pero es genérico (solo `[IAB1]`, o las dos formas a la vez `[IAB1-5, IAB1-7]`); `contradice` = al menos un código choca con la evidencia.

| Dataset | Evaluables | coincide | compatible | contradice | Filas que contradicen |
|---|---:|---:|---:|---:|---:|
| **consolidado** | 174,511 (83.1% de las llenas) | 24.6% · req 28.6% | 60.4% · req 56.5% | **15.0%** · req 14.9% | 26,159 |
| **relleno** | 818,343 (90.4% de las llenas) | 42.1% · req 40.5% | 52.0% · req 49.0% | **6.0%** · req 10.5% | 48,939 |

Desglosado por tipo de evidencia (% de las filas con esa evidencia):

| Dataset · evidencia | coincide | compatible | contradice | Filas |
|---|---:|---:|---:|---:|
| **consolidado** · externa | 17.3% | 63.8% | **18.8%** | 13,479 |
| **consolidado** · interna | 29.6% | 58.1% | **12.3%** | 12,680 |
| **relleno** · externa | 58.3% | 35.1% | **6.6%** | 31,559 |
| **relleno** · interna | 19.4% | 75.5% | **5.1%** | 17,380 |

### 3.1 En qué contradicen

`vertical` = la categoría nombra otra vertical (Noticias, Deportes, Tecnología…) para un contenido que la evidencia dice que es ficción de entretenimiento, o una vertical fuerte distinta de la que dice el género; `forma` = dice Películas y es serie (o al revés); `genero` = el código nombra un género (Drama Movies, Horror…) que la evidencia no trae; `sub` = el código nombra un deporte concreto (`IAB17-1` Auto Racing) y el género declarado nombra otro (Soccer). Un programa de no ficción (documental, reality) **no** se contradice por vertical temática: IMDb no registra de qué trata.

| Evidencia · tipo de choque | consolidado | relleno |
|---|---:|---:|
| `externa|forma` | 3,007 (1.4%) · req 1.0% | 11,150 (1.2%) · req 0.8% |
| `externa|genero` | 214 (0.1%) · req 0.0% | 284 (0.0%) · req 0.0% |
| `externa|sub` | 127 (0.1%) · req 0.1% | 127 (0.0%) · req 0.0% |
| `externa|vertical` | 10,131 (4.8%) · req 3.8% | 19,998 (2.2%) · req 5.3% |
| `interna|forma` | 1,225 (0.6%) · req 0.3% | 1,277 (0.1%) · req 0.1% |
| `interna|genero` | 1,252 (0.6%) · req 0.1% | 1,252 (0.1%) · req 0.0% |
| `interna|sub` | 1,627 (0.8%) · req 0.8% | 1,627 (0.2%) · req 0.3% |
| `interna|vertical` | 8,576 (4.1%) · req 4.4% | 13,224 (1.5%) · req 2.4% |

### 3.2 ¿Es error del vendedor o del match? (solo evidencia externa)

Un match IMDb de confianza B acierta ~75%: parte de las contradicciones externas son matches equivocados. Para separarlas, se mira si el `contentGenre` declarado coincide con los géneros IMDb del match: si coincide, el match es creíble y la categoría contradictoria es muy probablemente un error del vendedor; si tampoco coincide, sospechar del match.

| Contradicciones externas según… | consolidado | relleno |
|---|---:|---:|
| género declarado `coincide` con IMDb | 12,521 (92.9%) | 29,034 (92.0%) |
| género declarado `no_coincide` con IMDb | 219 (1.6%) | 1,200 (3.8%) |
| género declarado `sin_genero_declarado` con IMDb | 739 (5.5%) | 1,325 (4.2%) |
| género declarado `no_comparable` con IMDb | 0 (0.0%) | 0 (0.0%) |

## 4. Quién acierta y quién no

### Por país — consolidado

|  | Filas con categoría | % evaluables | coincide (de evaluables) | compatible | contradice | Filas que contradicen | % req del grupo que contradice |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mexico | 70,386 | 81.7% | 23.8% | 54.1% | **22.1%** | 12,714 | 11.7% |
| Colombia | 22,132 | 85.5% | 28.0% | 60.5% | **11.5%** | 2,183 | 8.6% |
| Chile | 17,287 | 83.7% | 27.8% | 64.8% | **7.3%** | 1,062 | 5.4% |

### Por publisher (top 12 por filas) — consolidado

|  | Filas con categoría | % evaluables | coincide (de evaluables) | compatible | contradice | Filas que contradicen | % req del grupo que contradice |
|---|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 74,350 | 90.0% | 4.8% | 94.3% | **0.8%** | 568 | 0.4% |
| iion Pty Ltd | 1,126 | 40.0% | 19.3% | 68.9% | **11.8%** | 53 | 0.6% |
| TCL ADS - Springserve | 872 | 24.2% | 28.9% | 65.9% | **5.2%** | 11 | 0.8% |
| TCL ADs (APAC) | 967 | 26.4% | 33.7% | 56.5% | **9.8%** | 25 | 1.4% |
| Select Plus PTE LTD (CTV) | 6 | 66.7% | 50.0% | 50.0% | **0.0%** | 0 | 0.0% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 5,669 | 78.6% | 22.8% | 32.9% | **44.2%** | 1,972 | 33.5% |
| PML Digital | 5,180 | 88.7% | 5.8% | 15.6% | **78.7%** | 3,615 | 64.2% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 15,655 | 92.7% | 33.2% | 48.3% | **18.5%** | 2,679 | 29.7% |
| AWG Media | 17,682 | 81.3% | 45.6% | 42.9% | **11.5%** | 1,652 | 7.6% |
| Vidaa | 14,836 | 76.9% | 12.1% | 29.0% | **58.9%** | 6,718 | 46.6% |
| Coocaa, a SKYWORTH company | 14,978 | 79.3% | 50.9% | 37.2% | **11.9%** | 1,419 | 10.5% |

### Por país — relleno

|  | Filas con categoría | % evaluables | coincide (de evaluables) | compatible | contradice | Filas que contradicen | % req del grupo que contradice |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mexico | 275,868 | 89.4% | 44.1% | 47.6% | **8.3%** | 20,517 | 11.4% |
| Colombia | 95,856 | 90.7% | 46.7% | 49.2% | **4.1%** | 3,547 | 3.2% |
| Chile | 103,286 | 91.8% | 44.5% | 49.9% | **5.6%** | 5,317 | 9.8% |

### Por publisher (top 12 por filas) — relleno

|  | Filas con categoría | % evaluables | coincide (de evaluables) | compatible | contradice | Filas que contradicen | % req del grupo que contradice |
|---|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 199,360 | 89.1% | 11.7% | 87.5% | **0.8%** | 1,473 | 0.4% |
| iion Pty Ltd | 168,576 | 93.7% | 54.5% | 43.8% | **1.6%** | 2,579 | 1.3% |
| TCL ADS - Springserve | 113,441 | 93.3% | 53.0% | 45.0% | **2.0%** | 2,136 | 1.6% |
| TCL ADs (APAC) | 107,953 | 93.5% | 54.2% | 43.7% | **2.1%** | 2,090 | 1.6% |
| Select Plus PTE LTD (CTV) | 78,780 | 93.1% | 57.4% | 42.2% | **0.4%** | 319 | 0.4% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 21,948 | 89.8% | 48.7% | 30.9% | **20.4%** | 4,023 | 42.1% |
| PML Digital | 23,101 | 89.6% | 16.9% | 30.5% | **52.7%** | 10,903 | 66.4% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 21,591 | 91.2% | 41.3% | 44.1% | **14.7%** | 2,887 | 26.2% |
| AWG Media | 18,711 | 81.6% | 43.7% | 45.5% | **10.8%** | 1,652 | 4.8% |
| Vidaa | 16,483 | 77.8% | 17.3% | 30.2% | **52.5%** | 6,733 | 45.6% |
| Coocaa, a SKYWORTH company | 14,978 | 79.3% | 50.9% | 37.2% | **11.9%** | 1,419 | 10.5% |
| Televisa Univision via SpringServe | 12,894 | 92.8% | 46.2% | 24.6% | **29.2%** | 3,494 | 23.3% |

En el relleno, `original` son las filas que ya traían categoría (las mismas del consolidado); las demás son las que el pipeline de relleno llenó y de dónde las sacó.

### Por origen del valor — relleno

|  | Filas con categoría | % evaluables | coincide (de evaluables) | compatible | contradice | Filas que contradicen | % req del grupo que contradice |
|---|---:|---:|---:|---:|---:|---:|---:|
| app_default | 83,934 | 86.5% | 0.5% | 89.6% | **9.9%** | 7,158 | 10.1% |
| derivado_genero | 226,590 | 87.2% | 26.4% | 69.2% | **4.4%** | 8,664 | 2.0% |
| derivado_tipo | 291,042 | 100.0% | 84.6% | 15.3% | **0.1%** | 324 | 0.1% |
| intra_titulo | 93,404 | 88.3% | 3.0% | 89.0% | **8.0%** | 6,634 | 47.9% |
| original | 209,901 | 83.1% | 24.6% | 60.4% | **15.0%** | 26,159 | 10.5% |

## 5. Consistencia entre rutas: el mismo título con categorías distintas

No requiere fuentes externas: si el mismo título (normalizado) llega con `[IAB12]` por una ruta y `[IAB1]` por otra, al menos una está mal. Un título tiene conflicto de **vertical** cuando sus filas declaran verticales distintas, y de **forma** cuando unas dicen solo Películas y otras solo Televisión. Las **filas minoritarias** son las que declaran algo distinto de lo que declara la mayoría de las filas de ese título: son las candidatas a estar mal (sin decidir aquí quién tiene razón).

| Dataset | Títulos con categoría | Títulos con conflicto de vertical | Filas en esos títulos | Filas minoritarias de vertical (de las llenas) | Títulos con conflicto de forma | Filas en esos títulos | Filas minoritarias de forma | …ambas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **consolidado** | 9,777 | 2,643 (27.0%) | 91,776 | 11,178 (5.3%) · req 2.8% | 168 (1.7%) | 1,901 | 354 (0.2%) · req 0.0% | 2 (0.0%) · req 0.0% |
| **relleno** | 14,204 | 3,624 (25.5%) | 641,680 | 44,502 (4.9%) · req 3.9% | 586 (4.1%) | 64,065 | 9,337 (1.0%) · req 0.9% | 39 (0.0%) · req 0.0% |

Ejemplos de conflicto de vertical en **consolidado** (título → filas por vertical):

- `transplant` → tecnologia ×641, entretenimiento ×641
- `chicken stew` → entretenimiento ×448, familia ×76, deportes ×24
- `golden edge` → noticias ×437, entretenimiento ×35
- `goal tv` → deportes ×367, entretenimiento ×22
- `brooklyn love stories` → entretenimiento ×330, deportes ×47
- `american apocalypse` → entretenimiento ×327, deportes ×39
- `eve` → entretenimiento ×290, deportes ×51, noticias ×17
- `corona` → entretenimiento ×291, deportes ×41
- `forest frenzy of boonie bears` → entretenimiento ×251, familia ×49, deportes ×16
- `hatchback` → entretenimiento ×275, deportes ×40
- `penance lane` → entretenimiento ×239, deportes ×41
- `dw espanol` → noticias ×192, entretenimiento ×55, deportes ×5

Ejemplos de conflicto de forma:

- `live news` → tv ×148, pelicula ×11
- `grandes parejas` → tv ×143, pelicula ×6
- `las 3 marias` → tv ×108, pelicula ×5
- `como dice el dicho` → tv ×94, pelicula ×16
- `rebelde` → tv ×99, pelicula ×5
- `super mario bros wonder` → tv ×101, pelicula ×1
- `jajaja` → tv ×88, pelicula ×11
- `galanes` → tv ×87, pelicula ×8
- `hi vida` → pelicula ×27, tv ×7
- `el peso del amor` → pelicula ×19, tv ×14
- `freetv sureno` → pelicula ×30, tv ×1
- `freetv clasico` → pelicula ×27, tv ×1

## 6. Las contradicciones con más tráfico

**consolidado** — un título por fila, ordenados por requests de las filas que contradicen (muestra completa en `validacion-consolidado-muestra-contradicciones.csv`):

| Título | Declarado | Esperado (forma/géneros) | IMDb | Género declarado | Género vs IMDb | Choque | Publisher (ej.) | Filas (todas las rutas) | Requests |
|---|---|---|---|---|---|---|---|---:|---:|
| `lo que la vida me robo` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt3223004 Lo que la vida me robó | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 193 | 532,814,480 |
| `transplant s4 ep 1 crete` | `[IAB1-7, IAB19-29]` | tv/drama | tt10936342 Transplant | drama, medical drama, hos | coincide | vertical:tecnologia | Coocaa, a SKYWORTH company | 641 | 390,821,440 |
| `mi corazon es tuyo` | `[IAB1, IAB1-5]` | tv/comedia,romance,telenovela | tt3825904 Mi corazón es tuyo | Comedy | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 144 | 276,928,400 |
| `la rosa de guadalupe` | `[IAB12]` | tv/drama,telenovela | tt1192302 The Rose of Guadalupe | Drama | coincide | vertical:noticias | Vidaa | 238 | 258,834,400 |
| `amores verdaderos` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt2320524 True Love | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 158 | 229,714,880 |
| `la fea mas bella` | `[IAB1, IAB1-5]` | tv/comedia,drama,romance | tt0497152 La fea más bella | Comedy | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 86 | 213,027,920 |
| `destilando amor` | `[IAB12]` | tv/drama,telenovela | tt0940629 Destilando amor | Drama | coincide | vertical:noticias | Vidaa | 128 | 138,651,600 |
| `la familia p luche` | `[IAB1, IAB1-5]` | tv/comedia | tt1244672 La familia P. Luche | Comedy | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 80 | 133,984,880 |
| `jajaja` | `[IAB1-7]` | pelicula/comedia,drama,romance | tt1452626 Hahaha | comedy | coincide | forma:tv!=pelicula | Vidaa | 113 | 129,629,280 |
| `rubi 2005` | `[IAB12]` | genero:drama |  | Drama | no_comparable | vertical:noticias | Vidaa | 87 | 117,459,440 |
| `soy tu duena` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt1630269 Soy tu dueña | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 90 | 102,358,160 |
| `porque el amor manda` | `[IAB1, IAB1-5]` | tv/comedia,drama,telenovela | tt2401754 Porque el amor manda | Comedy | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 88 | 101,782,560 |
| `la vecina` | `[IAB1, IAB1-5]` | tv/comedia,drama,romance | tt4696338 La vecina | Comedy | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 82 | 100,875,840 |
| `amor real` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt0341281 Amor real | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 101 | 99,676,480 |
| `corazon indomable` | `[IAB12]` | pelicula/comedia,drama,romance | tt0108451 Untamed Heart | Drama | coincide | vertical:noticias | Vidaa | 93 | 98,487,760 |
| `la que no podia amar` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt2012381 The One Who Couldn't Love | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 104 | 97,375,040 |
| `hasta que el dinero nos separe` | `[IAB12]` | tv/comedia,drama,romance | tt0815736 Until Money Do Us Part | Comedy | coincide | vertical:noticias | Vidaa | 86 | 94,082,400 |
| `nosotros los guapos` | `[IAB1, IAB1-5]` | tv/comedia | tt7112114 Nosotros los guapos | Comedy | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 94 | 93,234,800 |
| `vecinos` | `[IAB12]` | ?/comedia,romance | tt0011508 Neighbors | Comedy | coincide | vertical:noticias | Vidaa | 92 | 91,281,360 |
| `40 y 20` | `[IAB12]` | tv/comedia | tt5711512 40 and 20 | Comedy | coincide | vertical:noticias | Vidaa | 90 | 83,665,360 |
| `rebelde hd` | `[IAB12]` | genero:drama |  | Drama | no_comparable | vertical:noticias | Vidaa | 102 | 78,141,680 |
| `sortilegio` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt1439031 Sortilegio | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 121 | 75,410,080 |
| `fuego en la sangre` | `[IAB12]` | ?/drama | tt0117005 Masseuse | Drama | coincide | vertical:noticias | Vidaa | 36 | 72,812,000 |
| `para volver a amar` | `[IAB1, IAB1-5]` | tv/drama,telenovela | tt1699171 Para volver a amar | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 97 | 70,916,880 |
| `atrevete a sonar` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt1364356 Atrévete a soñar | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 52 | 70,287,520 |

Pares declarado → esperado más frecuentes (consolidado):

| Declarado → esperado | Filas | Requests |
|---|---:|---:|
| `[IAB12] -> tv/drama,romance,telenovela` | 1,708 | 1,318,832,880 |
| `[IAB12] -> genero:drama` | 1,490 | 823,066,320 |
| `[IAB17-1] -> genero:deportes` | 1,447 | 893,092,800 |
| `[IAB12] -> tv/drama,telenovela` | 1,271 | 655,582,560 |
| `[IAB12] -> genero:comedia` | 715 | 282,659,840 |
| `[IAB1-7, IAB19-29] -> tv/drama` | 641 | 390,821,440 |
| `[IAB12] -> tv/comedia,drama,romance` | 537 | 410,944,480 |
| `[IAB1-5] -> genero:talk show` | 506 | 299,456,640 |
| `[IAB1, IAB1-5] -> tv/drama,romance,telenovela` | 494 | 363,086,400 |
| `[IAB1, IAB1-4, IAB16] -> genero:comedia` | 427 | 20,116,560 |
| `[IAB9-30] -> genero:deportes` | 383 | 58,704,880 |
| `[IAB1, IAB1-5] -> tv/drama,telenovela` | 350 | 154,206,240 |
| `[647] -> genero:crimen-misterio` | 335 | 21,112,000 |
| `[IAB12] -> genero:accion-aventura` | 334 | 93,152,480 |
| `[IAB12] -> tv/comedia` | 327 | 294,843,440 |

**relleno** — un título por fila, ordenados por requests de las filas que contradicen (muestra completa en `validacion-relleno-muestra-contradicciones.csv`):

| Título | Declarado | Esperado (forma/géneros) | IMDb | Género declarado | Género vs IMDb | Choque | Publisher (ej.) | Filas (todas las rutas) | Requests |
|---|---|---|---|---|---|---|---|---:|---:|
| `lo que la vida me robo` | `[IAB12]` | tv/drama,romance,telenovela | tt3223004 Lo que la vida me robó | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 549 | 2,506,900,080 |
| `mi corazon es tuyo` | `[IAB12]` | tv/comedia,romance,telenovela | tt3825904 Mi corazón es tuyo | comedy | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 316 | 1,343,138,080 |
| `amores verdaderos` | `[IAB12]` | tv/drama,romance,telenovela | tt2320524 True Love | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 340 | 1,140,296,960 |
| `la fea mas bella` | `[IAB12]` | tv/comedia,drama,romance | tt0497152 La fea más bella | comedy | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 215 | 1,029,284,160 |
| `la rosa de guadalupe` | `[IAB12]` | tv/drama,telenovela | tt1192302 The Rose of Guadalupe | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 526 | 890,593,440 |
| `rubi 2005` | `[IAB12]` | genero:drama |  | Drama | no_comparable | vertical:noticias | Equativ (Formerly SMART AdServ | 242 | 770,446,000 |
| `corazon indomable` | `[IAB12]` | pelicula/comedia,drama,romance | tt0108451 Untamed Heart | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 212 | 594,814,160 |
| `soy tu duena` | `[IAB12]` | tv/drama,romance,telenovela | tt1630269 Soy tu dueña | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 185 | 517,803,440 |
| `la vecina` | `[IAB12]` | tv/comedia,drama,romance | tt4696338 La vecina | comedy | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 164 | 434,588,160 |
| `la que no podia amar` | `[IAB12]` | tv/drama,romance,telenovela | tt2012381 The One Who Couldn't Love | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 224 | 430,482,240 |
| `amor real` | `[IAB12]` | tv/drama,romance,telenovela | tt0341281 Amor real | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 251 | 418,873,600 |
| `rebelde hd` | `[IAB12]` | genero:drama |  | drama | no_comparable | vertical:noticias | Equativ (Formerly SMART AdServ | 229 | 398,524,080 |
| `transplant s4 ep 1 crete` | `[IAB1-7, IAB19-29]` | tv/drama | tt10936342 Transplant | drama, medical drama, hos | coincide | vertical:tecnologia | Coocaa, a SKYWORTH company | 641 | 390,821,440 |
| `sortilegio` | `[IAB12]` | tv/drama,romance,telenovela | tt1439031 Sortilegio | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 278 | 335,470,400 |
| `abismo de pasion` | `[IAB12]` | pelicula/drama | tt0034946 Kings Row | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 173 | 325,994,240 |
| `true beauty` | `[IAB12]` | tv/comedia,drama,romance | tt13274038 True Beauty | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 211 | 315,232,880 |
| `manana es para siempre` | `[IAB12]` | pelicula/accion-aventura,crimen-misterio,drama | tt0039041 Tomorrow Is Forever | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 195 | 287,359,280 |
| `para volver a amar` | `[IAB12]` | tv/drama,telenovela | tt1699171 Para volver a amar | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 235 | 280,037,680 |
| `la gata` | `[IAB12]` | tv/accion-aventura,drama,infantil-familia | tt3596316 The Stray Cat | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 145 | 267,997,680 |
| `40 y 20` | `[IAB12]` | tv/comedia | tt5711512 40 and 20 | comedy | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 218 | 254,874,240 |
| `cuando me enamoro se detiene el tiempo` | `[IAB12]` | genero:drama |  | drama | no_comparable | vertical:noticias | Equativ (Formerly SMART AdServ | 188 | 243,874,240 |
| `las hijas de la senora garcia` | `[IAB12]` | tv/drama,telenovela | tt32872848 Mrs. Garcia and Her Daughters | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 164 | 188,977,760 |
| `por amar sin ley` | `[IAB12]` | tv/drama,telenovela | tt7907384 Laws of Love | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 148 | 186,411,840 |
| `amor bravio` | `[IAB12]` | tv/drama,romance,telenovela | tt2266983 Valiant Love | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 211 | 165,734,480 |
| `maria la del barrio` | `[IAB12]` | tv/drama,romance,telenovela | tt0163464 Humble Maria | drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 144 | 161,599,920 |

Pares declarado → esperado más frecuentes (relleno):

| Declarado → esperado | Filas | Requests |
|---|---:|---:|
| `[IAB12] -> tv/drama,romance,telenovela` | 3,129 | 5,888,838,320 |
| `[IAB12] -> genero:drama` | 2,467 | 2,209,126,080 |
| `[IAB12] -> tv/drama,telenovela` | 2,267 | 1,962,936,160 |
| `[IAB17-1] -> genero:deportes` | 1,447 | 893,092,800 |
| `[IAB9-30] -> genero:deportes` | 1,298 | 273,282,320 |
| `[IAB1-7] -> pelicula/comedia,drama,infantil-familia` | 1,034 | 299,941,600 |
| `[IAB12] -> genero:comedia` | 1,023 | 349,445,520 |
| `[IAB12] -> tv/comedia,drama,romance` | 990 | 1,916,131,600 |
| `[sports] -> pelicula/drama` | 824 | 249,086,800 |
| `[sports] -> genero:drama` | 780 | 332,419,520 |
| `[IAB1-7] -> pelicula/accion-aventura,fantasia,infantil-familia` | 744 | 88,984,560 |
| `[IAB1-7] -> pelicula/infantil-familia` | 729 | 93,370,480 |
| `[IAB1-7] -> pelicula/comedia` | 657 | 173,037,920 |
| `[IAB1-7, IAB19-29] -> tv/drama` | 641 | 390,821,440 |
| `[IAB1-7] -> pelicula/drama` | 624 | 133,749,840 |

## 7. De paso: contentGenre contra IMDb

La misma evidencia externa permite validar el género declarado (que es el insumo del relleno de categoría). Sobre las filas con match externo y género declarado: `coincide` = al menos un género declarado está entre los de IMDb/Wikidata; `no_coincide` = ninguno.

| Dataset | Filas con match externo | …y con género declarado | coincide (de las comparables) | no_coincide | sin género declarado (de las con match) |
|---|---:|---:|---:|---:|---:|
| **consolidado** | 476,869 | 431,578 | 92.6% | 7.4% | 9.5% |
| **relleno** | 476,869 | 431,578 | 92.6% | 7.4% | 9.5% |

Por publisher (consolidado):

| Publisher | Filas comparables | coincide | no_coincide |
|---|---:|---:|---:|
| OTTera.tv | 99,547 | 94.5% | 5.5% |
| iion Pty Ltd | 91,270 | 91.5% | 8.5% |
| TCL ADS - Springserve | 60,797 | 93.4% | 6.6% |
| TCL ADs (APAC) | 60,419 | 93.4% | 6.6% |
| Select Plus PTE LTD (CTV) | 46,165 | 82.7% | 17.3% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 10,318 | 97.6% | 2.4% |
| PML Digital | 12,370 | 94.4% | 5.6% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 11,999 | 94.7% | 5.3% |
| AWG Media | 1,961 | 96.4% | 3.6% |
| Vidaa | 4,777 | 99.7% | 0.3% |
| Coocaa, a SKYWORTH company | 1,330 | 96.5% | 3.5% |
| Televisa Univision via SpringServe | 6,885 | 99.5% | 0.5% |

## 8. Límites del método

- **La evidencia externa cubre lo que tiene título real y match**: el catálogo FAST con títulos placeholder (`epg`, `roku`) o de canal no se puede juzgar contra IMDb; para esas filas solo queda la evidencia interna o la consistencia entre rutas.
- **Un match B se equivoca 1 de cada 4 veces.** Por eso las contradicciones externas se parten según si el género declarado respalda el match (§3.2); la cifra defendible es la de "género coincide". Con `--confianza-min A` el pipeline se vuelve más estricto (menos cobertura, más precisión).
- **IMDb no dice de qué trata la no ficción**: un documental etiquetado Viajes o Tecnología queda `compatible`, no `coincide`. Para validar verticales temáticas haría falta TMDB (keywords) o Wikidata P921 (main subject), no incluidos en esta corrida.
- **El género es opinable**: IMDb trae hasta 3 géneros y Wikidata los suyos; el choque de `genero` se declara solo si el código nombra un género que ninguna de las dos fuentes trae. Es el choque más débil de los tres y por eso se reporta aparte.
