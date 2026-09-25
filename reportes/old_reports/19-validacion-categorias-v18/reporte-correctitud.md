# contentCategory, parte 1: las filas que traen categoría, ¿la traen bien?

**Fuentes:** `inventory-consolidado-v10-a-v18.csv` (1,071,840 filas, columna `contentCategory`); `inventory-consolidado-v10-a-v18-relleno.csv` (1,071,840 filas, columna `contentCategory_relleno`).  
**Generado con:** `scripts/validar_categorias.py` + `scripts/generar_reporte_validacion.py`. Corrida del 2026-09-15 09:42. Evidencia externa: IMDb (match de confianza ≥ B) y géneros de Wikidata, desde `cache-enriquecimiento/titulos.json` (15,267 títulos); taxonomías oficiales de IAB Tech Lab: 1.0 (392 códigos), 2.2 (1196) y 3.0 (703).

## Cómo leer este reporte

- **Fila**: cada fila del inventario es una combinación de país, publisher, app y metadata de contenido, no un programa ni un evento. **Requests** son las solicitudes de anuncio que trae esa fila; por eso cada cifra se da en filas y en requests.
- **Tal como llega (consolidado)** es el inventario tal como lo mandan los vendedores. **Después del relleno** es el mismo inventario después de que el pipeline de relleno (`enriquecer_externo.py`) completó las categorías vacías; se validan los dos para saber si el relleno acierta.
- **Categoría IAB**: el código de `contentCategory` (por ejemplo `[IAB1-5]` = Entretenimiento > Películas). Una categoría afirma hasta tres cosas: la **vertical** (entretenimiento, noticias, deportes…), la **forma** (película o televisión) y el **género** (drama, terror…).
- **Evidencia**: contra qué se compara la categoría. *IMDb / Wikidata*: el título de la fila se encontró en esas bases (un **match**), que dicen si es película o serie y qué géneros tiene; cubre 531,080 filas (49.5% del total). *Solo el género de la fila*: no hay match, pero el `contentGenre` de la misma fila permite juzgar (un drama no es Noticias). *Sin evidencia*: no hay contra qué comparar.
- **Confianza del match**: A = el título coincide sin ambigüedad; B = coincide pero podría ser otro título homónimo (acierta ~3 de cada 4). Se usan matches de confianza B o mejor.
- **Formato de las celdas**: `12,345 filas (12.3%) · 4.5% req` = cantidad de filas, % de filas y % de requests sobre la base que indica cada tabla.

**Base de los porcentajes en este reporte:** salvo que la tabla diga otra cosa, los % son sobre las **filas que traen categoría** (no sobre todo el inventario). "Evaluables" son las filas con categoría que además tienen evidencia para juzgarla.

---

## 1. Cuántas filas traen categoría y cuántas se pudieron evaluar

| Dataset | Filas totales | Filas con categoría (% del total) | % de requests con categoría | Filas cuyo título está en IMDb/Wikidata (% del total) | Con categoría y evidencia IMDb/Wikidata (% de las que traen categoría) | Con categoría y solo el género como evidencia | Con categoría y sin evidencia |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Tal como llega (consolidado)** | 1,071,840 | 234,298 (21.9%) | 30.8% | 531,080 (49.5%) | 80,495 filas (34.4%) · 16.7% req | 113,311 filas (48.4%) · 52.7% req | 40,492 filas (17.3%) · 30.6% req |
| **Después del relleno** | 1,071,840 | 1,008,550 (94.1%) | 88.1% | 531,080 (49.5%) | 530,584 filas (52.6%) · 41.6% req | 379,693 filas (37.6%) · 44.5% req | 98,273 filas (9.7%) · 13.9% req |

*Cómo leerla: las tres últimas columnas reparten las filas con categoría según qué se puede usar para juzgarla. Las de la última columna quedan como "no se pudo evaluar" en el resto del reporte.*

## 2. Cómo vienen escritos los valores

Antes de juzgar si la categoría es correcta se mira si el valor es un código válido. Un valor es un **código IAB válido** si todos sus códigos existen en IAB 1.0 (`IAB1-5`) o en 2.2/3.0 (`333`); es un **código inexistente** si tiene forma de código pero no está en ninguna taxonomía (`IAB1-22`, `IAB-7`); es **texto libre** si no es un código (`sports`, `Live`, `Entertainment`). Los códigos 1000+ de IAB 2.2 (`1070` = idioma español, `1004` = canal de juegos) existen pero no describen el contenido: se cuentan como **metadato**.

| Tipo de valor | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Código IAB válido (`estandar`) | 194,535 filas (83.0%) · 93.8% req | 928,359 filas (92.0%) · 94.3% req |
| Código IAB válido + Código con forma IAB pero inexistente + Texto libre (no es un código) (`estandar;no_estandar;texto_libre`) | 2 filas (0.0%) · 0.0% req | 2 filas (0.0%) · 0.0% req |
| Código IAB válido + Texto libre (no es un código) (`estandar;texto_libre`) | 103 filas (0.0%) · 0.0% req | 103 filas (0.0%) · 0.0% req |
| Código con forma IAB pero inexistente (`no_estandar`) | 31,282 filas (13.3%) · 5.5% req | 58,955 filas (5.8%) · 4.1% req |
| Texto libre (no es un código) (`texto_libre`) | 8,376 filas (3.6%) · 0.6% req | 21,131 filas (2.1%) · 1.5% req |

Qué taxonomía IAB usan (un valor puede mezclar varias):

| Taxonomía | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| IAB 1.0 (`1.0`) | 208,007 filas (88.8%) · 97.9% req | 969,371 filas (96.1%) · 97.9% req |
| IAB 1.0 + ninguna (`1.0;ninguna`) | 96 filas (0.0%) · 0.0% req | 96 filas (0.0%) · 0.0% req |
| IAB 2.2 / 3.0 (`2.2`) | 17,810 filas (7.6%) · 1.5% req | 17,943 filas (1.8%) · 0.5% req |
| IAB 2.2 / 3.0 + ninguna (`2.2;ninguna`) | 9 filas (0.0%) · 0.0% req | 9 filas (0.0%) · 0.0% req |
| ninguna (`ninguna`) | 8,376 filas (3.6%) · 0.6% req | 21,131 filas (2.1%) · 1.5% req |

Los 20 valores más frecuentes en **Tal como llega (consolidado)** (sobre 234,298 filas con categoría):

| Valor tal como viene | Filas | % de filas con categoría | % de requests con categoría |
|---|---:|---:|---:|
| `[IAB1]` | 58,202 | 24.8% | 11.2% |
| `[IAB1-22]` | 30,688 | 13.1% | 4.8% |
| `[IAB12]` | 22,851 | 9.8% | 10.4% |
| `[IAB1-5]` | 17,795 | 7.6% | 4.9% |
| `[IAB1, IAB1-5]` | 11,196 | 4.8% | 2.3% |
| `[IAB17]` | 10,979 | 4.7% | 3.9% |
| `[IAB1-7]` | 10,643 | 4.5% | 18.4% |
| `[IAB1-5, IAB1-7]` | 6,773 | 2.9% | 14.3% |
| `[sports]` | 5,493 | 2.3% | 0.3% |
| `[IAB1-7, IAB17-12]` | 5,154 | 2.2% | 2.2% |
| `[IAB1-6]` | 4,165 | 1.8% | 1.7% |
| `[640]` | 3,478 | 1.5% | 0.2% |
| `[IAB1, IAB1-5, IAB1-7]` | 3,425 | 1.5% | 0.3% |
| `[IAB17-1]` | 2,873 | 1.2% | 1.2% |
| `[Live]` | 2,041 | 0.9% | 0.3% |
| `[IAB9-30]` | 1,851 | 0.8% | 0.2% |
| `[325]` | 1,658 | 0.7% | 0.1% |
| `[647]` | 1,552 | 0.7% | 0.1% |
| `[324]` | 1,512 | 0.7% | 0.1% |
| `[IAB20]` | 1,415 | 0.6% | 0.6% |

## 3. Veredicto: ¿la categoría es correcta?

Sobre las filas **evaluables**, cada una recibe un veredicto:

- **Correcta y precisa** (`coincide`): algún código acierta en lo más fino que declara (la forma o el género) y ninguno contradice la evidencia.
- **Correcta pero genérica** (`compatible`): no contradice nada, pero solo dice la vertical (`[IAB1]`) o las dos formas a la vez (`[IAB1-5, IAB1-7]`, "película o TV").
- **Incorrecta** (`contradice`): al menos un código choca con la evidencia.

| Dataset | Filas evaluables | Correcta y precisa | Correcta pero genérica | Incorrecta | Filas incorrectas |
|---|---:|---:|---:|---:|---:|
| **Tal como llega (consolidado)** | 193,806 (82.7% de las que traen categoría) | 24.5% · 26.8% req | 60.5% · 56.6% req | **14.9%** · 16.6% req | 28,964 |
| **Después del relleno** | 910,277 (90.3% de las que traen categoría) | 41.6% · 40.8% req | 52.5% · 48.8% req | **5.9%** · 10.4% req | 53,390 |

*Los % de las tres columnas de veredicto son sobre las filas evaluables (filas y requests).*

Lo mismo separado según la evidencia con que se juzgó (% de las filas con esa evidencia):

| Dataset · evidencia usada | Correcta y precisa | Correcta pero genérica | Incorrecta | Filas incorrectas |
|---|---:|---:|---:|---:|
| **Tal como llega (consolidado)** · IMDb / Wikidata | 17.6% | 63.6% | **18.7%** | 15,074 |
| **Tal como llega (consolidado)** · Solo el género de la fila | 29.4% | 58.3% | **12.3%** | 13,890 |
| **Después del relleno** · IMDb / Wikidata | 58.0% | 35.5% | **6.5%** | 34,442 |
| **Después del relleno** · Solo el género de la fila | 18.7% | 76.3% | **5.0%** | 18,948 |

### 3.1 En qué se equivocan las incorrectas

Qué parte de la categoría choca con la evidencia: **la vertical** (dice Noticias, Deportes o Tecnología para algo que es ficción, o una vertical distinta de la que implica el género), **película vs serie** (dice Películas y es una serie, o al revés), **el género** (el código nombra un género que ninguna fuente trae) o **el sub-deporte** (dice Auto Racing y el género dice fútbol). Un documental o reality no se marca incorrecto por su tema: IMDb no registra de qué trata.

| Evidencia · qué choca | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| IMDb / Wikidata · choca en película vs serie (`externa|forma`) | 3,347 filas (1.4%) · 1.2% req | 11,666 filas (1.2%) · 0.7% req |
| IMDb / Wikidata · choca en el género (`externa|genero`) | 224 filas (0.1%) · 0.0% req | 301 filas (0.0%) · 0.0% req |
| IMDb / Wikidata · choca en el sub-deporte (`externa|sub`) | 131 filas (0.1%) · 0.1% req | 131 filas (0.0%) · 0.0% req |
| IMDb / Wikidata · choca en la vertical (Noticias, Deportes… para ficción) (`externa|vertical`) | 11,372 filas (4.8%) · 4.6% req | 22,344 filas (2.2%) · 5.5% req |
| Solo el género de la fila · choca en película vs serie (`interna|forma`) | 1,322 filas (0.6%) · 0.4% req | 1,374 filas (0.1%) · 0.1% req |
| Solo el género de la fila · choca en el género (`interna|genero`) | 1,438 filas (0.6%) · 0.1% req | 1,438 filas (0.1%) · 0.0% req |
| Solo el género de la fila · choca en el sub-deporte (`interna|sub`) | 1,670 filas (0.7%) · 0.6% req | 1,670 filas (0.2%) · 0.2% req |
| Solo el género de la fila · choca en la vertical (Noticias, Deportes… para ficción) (`interna|vertical`) | 9,460 filas (4.0%) · 4.5% req | 14,466 filas (1.4%) · 2.4% req |

### 3.2 ¿Se equivocó el vendedor o el match de IMDb?

Solo para las incorrectas juzgadas con IMDb/Wikidata. Un match de confianza B acierta unas 3 de cada 4 veces, así que parte de estas contradicciones puede ser un match equivocado. Para separarlas se mira si el género que declara el propio vendedor coincide con los géneros IMDb del título encontrado: si coincide, el match es creíble y la categoría es la que está mal.

| Filas incorrectas con evidencia IMDb/Wikidata, según… | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| El género declarado coincide con IMDb → el match es creíble, la categoría es error del vendedor (`coincide`) | 13,963 (92.6%) | 31,526 (91.5%) |
| El género declarado no coincide con IMDb → sospechar del match (`no_coincide`) | 289 (1.9%) | 1,454 (4.2%) |
| El género declarado la fila no declara género (`sin_genero_declarado`) | 822 (5.5%) | 1,462 (4.2%) |
| El género declarado el género declarado no es comparable (`no_comparable`) | 0 (0.0%) | 0 (0.0%) |

## 4. Quién acierta y quién no

Cada fila de estas tablas es un grupo (país, publisher u origen del valor). Los % de veredicto son sobre las filas evaluables del grupo; la última columna dice qué parte de **todos** los requests del grupo cae en filas con categoría incorrecta.

### Por país — Tal como llega (consolidado)

| País | Filas con categoría | % evaluables | Correcta y precisa | Correcta pero genérica | Incorrecta | Filas incorrectas | % de los requests del grupo en filas incorrectas |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mexico | 78,652 | 81.4% | 23.8% | 54.6% | **21.6%** | 13,813 | 13.1% |
| Colombia | 25,351 | 85.2% | 28.5% | 58.5% | **13.0%** | 2,806 | 8.9% |
| Chile | 19,084 | 82.7% | 27.2% | 65.5% | **7.3%** | 1,157 | 5.4% |

### Por publisher (los 12 con más filas) — Tal como llega (consolidado)

| Publisher | Filas con categoría | % evaluables | Correcta y precisa | Correcta pero genérica | Incorrecta | Filas incorrectas | % de los requests del grupo en filas incorrectas |
|---|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 83,368 | 89.4% | 5.0% | 94.1% | **0.9%** | 677 | 0.4% |
| iion Pty Ltd | 1,253 | 42.1% | 22.2% | 66.7% | **11.2%** | 59 | 0.3% |
| TCL ADS - Springserve | 951 | 24.4% | 28.0% | 66.4% | **5.6%** | 13 | 0.5% |
| TCL ADs (APAC) | 1,095 | 25.2% | 32.2% | 58.0% | **9.8%** | 27 | 0.8% |
| Select Plus PTE LTD (CTV) | 6 | 66.7% | 50.0% | 50.0% | **0.0%** | 0 | 0.0% |
| PML Digital | 5,953 | 87.8% | 5.3% | 16.0% | **78.7%** | 4,113 | 65.5% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 18,558 | 92.5% | 33.5% | 49.0% | **17.5%** | 3,008 | 30.4% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 6,396 | 77.6% | 23.2% | 33.8% | **43.0%** | 2,137 | 29.8% |
| AWG Media | 19,313 | 80.6% | 45.1% | 43.5% | **11.4%** | 1,768 | 7.1% |
| Vidaa | 16,669 | 76.7% | 12.7% | 29.3% | **58.0%** | 7,416 | 45.0% |
| Coocaa, a SKYWORTH company | 15,655 | 78.9% | 51.4% | 37.1% | **11.5%** | 1,419 | 10.4% |

### Por país — Después del relleno

| País | Filas con categoría | % evaluables | Correcta y precisa | Correcta pero genérica | Incorrecta | Filas incorrectas | % de los requests del grupo en filas incorrectas |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mexico | 299,163 | 88.7% | 42.9% | 48.5% | **8.5%** | 22,614 | 11.6% |
| Colombia | 107,493 | 90.6% | 46.2% | 49.5% | **4.3%** | 4,233 | 2.8% |
| Chile | 117,396 | 91.5% | 43.8% | 51.0% | **5.2%** | 5,555 | 10.5% |

### Por publisher (los 12 con más filas) — Después del relleno

| Publisher | Filas con categoría | % evaluables | Correcta y precisa | Correcta pero genérica | Incorrecta | Filas incorrectas | % de los requests del grupo en filas incorrectas |
|---|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 219,626 | 88.7% | 11.7% | 87.4% | **0.8%** | 1,601 | 0.3% |
| iion Pty Ltd | 190,536 | 93.3% | 53.0% | 45.5% | **1.5%** | 2,649 | 0.7% |
| TCL ADS - Springserve | 125,679 | 93.2% | 52.2% | 45.9% | **1.9%** | 2,178 | 1.1% |
| TCL ADs (APAC) | 119,838 | 93.6% | 53.8% | 44.3% | **1.9%** | 2,127 | 1.1% |
| Select Plus PTE LTD (CTV) | 90,609 | 93.3% | 57.0% | 42.6% | **0.4%** | 362 | 0.4% |
| PML Digital | 26,200 | 89.0% | 15.1% | 33.1% | **51.8%** | 12,070 | 67.1% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 25,268 | 91.5% | 41.2% | 44.8% | **14.0%** | 3,227 | 26.7% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 23,996 | 89.4% | 48.4% | 31.1% | **20.4%** | 4,384 | 43.8% |
| AWG Media | 20,398 | 80.9% | 43.4% | 45.8% | **10.7%** | 1,768 | 4.4% |
| Vidaa | 18,591 | 77.5% | 17.3% | 31.1% | **51.6%** | 7,431 | 44.2% |
| Televisa Univision via SpringServe | 14,039 | 93.2% | 46.2% | 24.2% | **29.7%** | 3,881 | 21.7% |
| Coocaa, a SKYWORTH company | 15,655 | 78.9% | 51.4% | 37.1% | **11.5%** | 1,419 | 10.4% |

En el dataset rellenado, el **origen** dice de dónde salió cada categoría: las que venían del vendedor son las mismas del consolidado; las demás las puso el pipeline de relleno. Ojo: las derivadas de IMDb se juzgan contra la misma fuente que las generó, así que su acierto solo prueba consistencia.

### Por origen del valor — Después del relleno

| Origen del valor | Filas con categoría | % evaluables | Correcta y precisa | Correcta pero genérica | Incorrecta | Filas incorrectas | % de los requests del grupo en filas incorrectas |
|---|---:|---:|---:|---:|---:|---:|---:|
| Valor habitual de la app (`app_default`) | 89,387 | 86.4% | 0.5% | 89.4% | **10.1%** | 7,824 | 12.0% |
| Derivado del género (`derivado_genero`) | 245,173 | 87.7% | 25.6% | 70.3% | **4.1%** | 8,922 | 1.3% |
| Derivado del tipo IMDb (película / serie) (`derivado_tipo`) | 323,918 | 100.0% | 84.4% | 15.5% | **0.1%** | 266 | 0.1% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 115,774 | 86.5% | 2.4% | 90.2% | **7.4%** | 7,414 | 46.3% |
| Venía del vendedor (`original`) | 234,298 | 82.7% | 24.5% | 60.5% | **14.9%** | 28,964 | 11.5% |

## 5. El mismo título con categorías distintas según la ruta

No necesita fuentes externas: si el mismo título llega con `[IAB12]` Noticias por una ruta de venta y con `[IAB1]` Entretenimiento por otra, al menos una está mal. Un título tiene **conflicto de vertical** cuando sus filas declaran verticales distintas, y **conflicto de forma** cuando unas dicen solo Películas y otras solo Televisión. Las **filas minoritarias** son las que dicen algo distinto de la mayoría de las filas de ese título: son las candidatas a estar mal.

| Dataset | Títulos con categoría | Títulos con conflicto de vertical | Filas en esos títulos | Filas minoritarias de vertical (% de las que traen categoría) | Títulos con conflicto de forma | Filas en esos títulos | Filas minoritarias de forma | Minoritarias en ambas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Tal como llega (consolidado)** | 10,281 | 2,849 (27.7%) | 104,106 | 12,634 filas (5.4%) · 3.0% req | 177 (1.7%) | 2,265 | 405 filas (0.2%) · 0.0% req | 2 filas (0.0%) · 0.0% req |
| **Después del relleno** | 14,770 | 3,745 (25.4%) | 707,263 | 47,745 filas (4.7%) · 3.4% req | 613 (4.2%) | 71,892 | 9,838 filas (1.0%) · 0.4% req | 34 filas (0.0%) · 0.0% req |

Ejemplos de conflicto de vertical en **Tal como llega (consolidado)** (título → cuántas filas declaran cada vertical):

- `transplant` → Entretenimiento ×662, tecnologia ×662
- `chicken stew` → Entretenimiento ×497, familia ×79, Deportes ×24
- `golden edge` → Noticias ×443, Entretenimiento ×39
- `goal tv` → Deportes ×390, Entretenimiento ×26
- `brooklyn love stories` → Entretenimiento ×350, Deportes ×47
- `american apocalypse` → Entretenimiento ×351, Deportes ×39
- `eve` → Entretenimiento ×307, Deportes ×51, Noticias ×18
- `corona` → Entretenimiento ×312, Deportes ×41
- `forest frenzy of boonie bears` → Entretenimiento ×277, familia ×49, Deportes ×17
- `hatchback` → Entretenimiento ×301, Deportes ×40
- `penance lane` → Entretenimiento ×258, Deportes ×41
- `your local and world news` → Noticias ×221, finanzas ×33, Entretenimiento ×12, tecnologia ×3, ciencia ×1

Ejemplos de conflicto de forma (título → cuántas filas dicen película y cuántas TV):

- `live news` → TV ×166, película ×12
- `grandes parejas` → TV ×153, película ×6
- `como dice el dicho` → TV ×100, película ×17
- `super mario bros wonder` → TV ×116, película ×1
- `las 3 marias` → TV ×111, película ×6
- `rebelde` → TV ×101, película ×5
- `jajaja` → TV ×92, película ×12
- `galanes` → TV ×90, película ×11
- `descendientes del sol` → TV ×47, película ×1
- `freetv clasico` → película ×43, TV ×1
- `freetv sureno` → película ×39, TV ×1
- `el peso del amor` → película ×22, TV ×14

## 6. Las categorías incorrectas con más tráfico

Un título por fila, ordenados por los requests de sus filas incorrectas. "Declarado" es la categoría que manda el vendedor; "Esperado" es lo que dice la evidencia; "Género vs IMDb" indica si el género declarado respalda el match (ver 3.2).

**Tal como llega (consolidado)** (lista completa en `validacion-consolidado-muestra-contradicciones.csv`):

| Título | Declarado | Esperado (forma / géneros) | Match IMDb | Género declarado | Género vs IMDb | Qué choca | Publisher (ejemplo) | Filas (todas las rutas) | Requests |
|---|---|---|---|---|---|---|---|---:|---:|
| `lo que la vida me robo` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt3223004 Lo que la vida me robó | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 210 | 692,736,240 |
| `transplant s4 ep 9 who is mags?` | `[IAB1-7, IAB19-29]` | tv/drama | tt10936342 Transplant | Not Applicable | sin_genero_declarado | vertical:tecnologia | Coocaa, a SKYWORTH company | 662 | 374,057,600 |
| `mi corazon es tuyo` | `[IAB1, IAB1-5]` | tv/comedia,romance,telenovela | tt3825904 Mi corazón es tuyo | Comedy | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 162 | 349,122,320 |
| `la rosa de guadalupe` | `[IAB12]` | tv/drama,telenovela | tt1192302 The Rose of Guadalupe | Drama | coincide | vertical:noticias | Vidaa | 258 | 327,208,000 |
| `amores verdaderos` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt2320524 True Love | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 178 | 296,639,680 |
| `la fea mas bella` | `[IAB1, IAB1-5]` | tv/comedia,drama,romance | tt0497152 La fea más bella | Comedy | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 97 | 278,045,840 |
| `destilando amor` | `[IAB1, IAB1-5]` | tv/drama,telenovela | tt0940629 Destilando amor | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 138 | 173,211,440 |
| `la familia p luche` | `[IAB1, IAB1-5]` | tv/comedia | tt1244672 La familia P. Luche | Comedy | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 87 | 168,518,880 |
| `rubi 2005` | `[IAB12]` | genero:drama |  | Drama | no_comparable | vertical:noticias | Vidaa | 93 | 167,486,880 |
| `jajaja` | `[IAB1-7]` | pelicula/comedia,drama,romance | tt1452626 Hahaha | Comedy | coincide | forma:tv!=pelicula | Vidaa | 119 | 154,176,880 |
| `soy tu duena` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt1630269 Soy tu dueña | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 98 | 136,898,240 |
| `porque el amor manda` | `[IAB12]` | tv/comedia,drama,telenovela | tt2401754 Porque el amor manda | Comedy | coincide | vertical:noticias | Vidaa | 101 | 133,487,200 |
| `la vecina` | `[IAB12]` | tv/comedia,drama,romance | tt4696338 La vecina | Comedy | coincide | vertical:noticias | Vidaa | 95 | 130,428,320 |
| `amor real` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt0341281 Amor real | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 113 | 130,416,160 |
| `corazon indomable` | `[IAB12]` | pelicula/comedia,drama,romance | tt0108451 Untamed Heart | Drama | coincide | vertical:noticias | Vidaa | 105 | 129,880,800 |
| `la que no podia amar` | `[IAB12]` | tv/drama,romance,telenovela | tt2012381 The One Who Couldn't Love | Drama | coincide | vertical:noticias | Vidaa | 112 | 129,347,440 |
| `hasta que el dinero nos separe` | `[IAB12]` | tv/comedia,drama,romance | tt0815736 Until Money Do Us Part | Comedy | coincide | vertical:noticias | Vidaa | 100 | 125,594,960 |
| `nosotros los guapos` | `[IAB1, IAB1-5]` | tv/comedia | tt7112114 Nosotros los guapos | Comedy | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 99 | 116,433,360 |
| `vecinos` | `[IAB12]` | ?/comedia,romance | tt0011508 Neighbors | Comedy | coincide | vertical:noticias | Vidaa | 104 | 110,656,720 |
| `rebelde hd` | `[IAB12]` | genero:drama |  | Drama | no_comparable | vertical:noticias | Vidaa | 117 | 102,497,040 |
| `40 y 20` | `[IAB12]` | tv/comedia | tt5711512 40 and 20 | Comedy | coincide | vertical:noticias | Vidaa | 96 | 102,094,160 |
| `fuego en la sangre` | `[IAB12]` | ?/drama | tt0117005 Masseuse | Drama | coincide | vertical:noticias | Vidaa | 41 | 98,683,760 |
| `sortilegio` | `[IAB1, IAB1-5]` | tv/drama,romance,telenovela | tt1439031 Sortilegio | Drama | coincide | forma:pelicula!=tv | METAX SOFTWARE PTE. LTD. (Exch | 140 | 97,039,920 |
| `para volver a amar` | `[IAB12]` | tv/drama,telenovela | tt1699171 Para volver a amar | Drama | coincide | vertical:noticias | Vidaa | 109 | 94,819,680 |
| `atrevete a sonar` | `[IAB12]` | tv/drama,romance,telenovela | tt1364356 Atrévete a soñar | Drama | coincide | vertical:noticias | Vidaa | 53 | 90,862,800 |

Pares "declarado → esperado" más frecuentes (Tal como llega (consolidado)):

| Declarado → esperado | Filas | Requests |
|---|---:|---:|
| `[IAB12] -> tv/drama,romance,telenovela` | 1,892 | 1,749,471,600 |
| `[IAB12] -> genero:drama` | 1,681 | 1,123,651,520 |
| `[IAB17-1] -> genero:deportes` | 1,490 | 786,656,960 |
| `[IAB12] -> tv/drama,telenovela` | 1,406 | 863,119,840 |
| `[IAB12] -> genero:comedia` | 788 | 366,626,720 |
| `[IAB1-7, IAB19-29] -> tv/drama` | 662 | 374,057,600 |
| `[IAB12] -> tv/comedia,drama,romance` | 616 | 544,590,400 |
| `[IAB1, IAB1-5] -> tv/drama,romance,telenovela` | 538 | 474,393,040 |
| `[IAB1-5] -> genero:talk show` | 529 | 365,553,280 |
| `[IAB9-30] -> genero:deportes` | 433 | 66,449,040 |
| `[IAB1, IAB1-4, IAB16] -> genero:comedia` | 427 | 19,939,120 |
| `[IAB1, IAB1-5] -> tv/drama,telenovela` | 389 | 202,208,880 |
| `[647] -> genero:crimen-misterio` | 387 | 26,482,240 |
| `[IAB12] -> genero:accion-aventura` | 366 | 125,464,320 |
| `[IAB12] -> tv/comedia` | 351 | 377,032,320 |

**Después del relleno** (lista completa en `validacion-relleno-muestra-contradicciones.csv`):

| Título | Declarado | Esperado (forma / géneros) | Match IMDb | Género declarado | Género vs IMDb | Qué choca | Publisher (ejemplo) | Filas (todas las rutas) | Requests |
|---|---|---|---|---|---|---|---|---:|---:|
| `lo que la vida me robo` | `[IAB12]` | tv/drama,romance,telenovela | tt3223004 Lo que la vida me robó | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 592 | 2,742,826,000 |
| `mi corazon es tuyo` | `[IAB12]` | tv/comedia,romance,telenovela | tt3825904 Mi corazón es tuyo | Comedy | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 342 | 1,383,090,640 |
| `amores verdaderos` | `[IAB12]` | tv/drama,romance,telenovela | tt2320524 True Love | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 373 | 1,266,537,680 |
| `la fea mas bella` | `[IAB12]` | tv/comedia,drama,romance | tt0497152 La fea más bella | Comedy | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 233 | 1,136,678,880 |
| `la rosa de guadalupe` | `[IAB12]` | tv/drama,telenovela | tt1192302 The Rose of Guadalupe | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 564 | 974,544,240 |
| `rubi 2005` | `[IAB12]` | genero:drama |  | Drama | no_comparable | vertical:noticias | Equativ (Formerly SMART AdServ | 260 | 955,526,640 |
| `destilando amor` | `[IAB12]` | tv/drama,telenovela | tt0940629 Destilando amor | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 339 | 652,781,680 |
| `corazon indomable` | `[IAB12]` | pelicula/comedia,drama,romance | tt0108451 Untamed Heart | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 232 | 635,949,120 |
| `soy tu duena` | `[IAB12]` | tv/drama,romance,telenovela | tt1630269 Soy tu dueña | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 200 | 572,510,240 |
| `porque el amor manda` | `[IAB12]` | tv/comedia,drama,telenovela | tt2401754 Porque el amor manda | Comedy | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 218 | 482,906,560 |
| `la que no podia amar` | `[IAB12]` | tv/drama,romance,telenovela | tt2012381 The One Who Couldn't Love | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 241 | 478,478,320 |
| `amor real` | `[IAB12]` | tv/drama,romance,telenovela | tt0341281 Amor real | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 271 | 473,298,560 |
| `la vecina` | `[IAB12]` | tv/comedia,drama,romance | tt4696338 La vecina | Comedy | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 182 | 464,533,840 |
| `rebelde hd` | `[IAB12]` | genero:drama |  | Drama | no_comparable | vertical:noticias | Equativ (Formerly SMART AdServ | 253 | 424,924,240 |
| `transplant s4 ep 9 who is mags?` | `[IAB1-7, IAB19-29]` | tv/drama | tt10936342 Transplant | Not Applicable | sin_genero_declarado | vertical:tecnologia | Coocaa, a SKYWORTH company | 662 | 374,057,600 |
| `sortilegio` | `[IAB12]` | tv/drama,romance,telenovela | tt1439031 Sortilegio | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 310 | 364,299,840 |
| `abismo de pasion` | `[IAB12]` | pelicula/drama | tt0034946 Kings Row | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 189 | 356,900,640 |
| `para volver a amar` | `[IAB12]` | tv/drama,telenovela | tt1699171 Para volver a amar | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 257 | 330,714,000 |
| `true beauty` | `[IAB12]` | tv/comedia,drama,romance | tt13274038 True Beauty | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 233 | 321,758,240 |
| `manana es para siempre` | `[IAB12]` | pelicula/accion-aventura,crimen-misterio,drama | tt0039041 Tomorrow Is Forever | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 210 | 315,642,720 |
| `la gata` | `[IAB12]` | tv/accion-aventura,drama,infantil-familia | tt3596316 The Stray Cat | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 156 | 291,950,000 |
| `cuando me enamoro se detiene el tiempo` | `[IAB12]` | genero:drama |  | Drama | no_comparable | vertical:noticias | Equativ (Formerly SMART AdServ | 205 | 269,261,840 |
| `40 y 20` | `[IAB12]` | tv/comedia | tt5711512 40 and 20 | Comedy | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 237 | 266,230,880 |
| `por amar sin ley` | `[IAB12]` | tv/drama,telenovela | tt7907384 Laws of Love | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 165 | 212,010,320 |
| `las hijas de la senora garcia` | `[IAB12]` | tv/drama,telenovela | tt32872848 Mrs. Garcia and Her Daughters | Drama | coincide | vertical:noticias | Equativ (Formerly SMART AdServ | 176 | 211,673,200 |

Pares "declarado → esperado" más frecuentes (Después del relleno):

| Declarado → esperado | Filas | Requests |
|---|---:|---:|
| `[IAB12] -> tv/drama,romance,telenovela` | 3,455 | 6,559,950,320 |
| `[IAB12] -> genero:drama` | 2,788 | 2,678,106,560 |
| `[IAB12] -> tv/drama,telenovela` | 2,702 | 2,833,159,840 |
| `[IAB17-1] -> genero:deportes` | 1,490 | 786,656,960 |
| `[IAB9-30] -> genero:deportes` | 1,415 | 238,709,120 |
| `[IAB12] -> genero:comedia` | 1,067 | 430,027,840 |
| `[IAB12] -> tv/comedia,drama,romance` | 1,058 | 2,067,781,840 |
| `[IAB1-7] -> pelicula/comedia,drama,infantil-familia` | 1,036 | 204,556,720 |
| `[sports] -> pelicula/drama` | 917 | 302,950,320 |
| `[sports] -> genero:drama` | 866 | 439,727,840 |
| `[IAB1-7] -> pelicula/accion-aventura,fantasia,infantil-familia` | 744 | 55,106,560 |
| `[IAB1-7] -> pelicula/infantil-familia` | 729 | 62,093,520 |
| `[IAB1-7] -> pelicula/comedia` | 708 | 196,469,520 |
| `[IAB1-7, IAB19-29] -> tv/drama` | 662 | 374,057,600 |
| `[IAB1-7] -> pelicula/comedia,infantil-familia` | 656 | 128,148,560 |

## 7. De paso: ¿el género declarado coincide con IMDb?

La misma evidencia sirve para validar `contentGenre`, que es el insumo del relleno de categoría. Sobre las filas con match y con género declarado: **coincide** = al menos un género declarado está entre los de IMDb/Wikidata; **no coincide** = ninguno.

| Dataset | Filas con match IMDb/Wikidata | …de las cuales declaran género | Coincide (% de las comparables) | No coincide | Sin género declarado (% de las con match) |
|---|---:|---:|---:|---:|---:|
| **Tal como llega (consolidado)** | 531,080 | 477,941 | 91.9% | 8.1% | 10.0% |
| **Después del relleno** | 531,080 | 477,941 | 91.9% | 8.1% | 10.0% |

Por publisher (Tal como llega (consolidado)):

| Publisher | Filas comparables | Coincide | No coincide |
|---|---:|---:|---:|
| OTTera.tv | 108,968 | 93.8% | 6.2% |
| iion Pty Ltd | 101,221 | 90.9% | 9.1% |
| TCL ADS - Springserve | 66,990 | 92.5% | 7.5% |
| TCL ADs (APAC) | 66,897 | 92.4% | 7.6% |
| Select Plus PTE LTD (CTV) | 52,584 | 83.0% | 17.0% |
| PML Digital | 13,746 | 94.0% | 6.0% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 14,155 | 93.5% | 6.5% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 11,033 | 97.6% | 2.4% |
| AWG Media | 2,129 | 96.3% | 3.7% |
| Vidaa | 5,391 | 99.7% | 0.3% |
| Televisa Univision via SpringServe | 7,509 | 99.5% | 0.5% |
| Coocaa, a SKYWORTH company | 1,330 | 96.5% | 3.5% |

## 8. Límites del método

- **Solo se puede juzgar lo que tiene título real y match.** El catálogo con títulos de relleno (`epg`, `roku`) o nombres de canal no está en IMDb; para esas filas solo queda el género de la fila o la comparación entre rutas.
- **Un match de confianza B falla 1 de cada 4 veces.** Por eso las incorrectas con evidencia externa se separan según si el género declarado respalda el match (3.2); la cifra defendible es la de "género coincide". Con `--confianza-min A` el método es más estricto (menos cobertura, más precisión).
- **IMDb no dice de qué trata la no ficción**: un documental etiquetado Viajes o Tecnología queda como "correcta pero genérica", no como "correcta y precisa". Para validar esas verticales haría falta TMDB (keywords) o Wikidata P921 (tema principal).
- **El género es opinable**: IMDb trae hasta 3 géneros y Wikidata los suyos. El choque de género solo se declara si el código nombra un género que ninguna fuente trae; es el choque más débil y por eso se reporta aparte.
