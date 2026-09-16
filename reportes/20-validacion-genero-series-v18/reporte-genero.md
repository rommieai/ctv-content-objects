# contentGenre: ¿el género declarado es correcto y se puede completar?

**Fuentes:** `inventory-consolidado-v10-a-v18.csv` (1,071,840 filas, columna `contentGenre`); `inventory-consolidado-v10-a-v18-relleno.csv` (1,071,840 filas, columna `contentGenre_relleno`).  
**Generado con:** `scripts/validar_genero_series.py` + `scripts/generar_reporte_genero_series.py`. Corrida del 2026-09-15 09:46. Evidencia: géneros de IMDb y de Wikidata desde `cache-enriquecimiento/titulos.json` (15,267 títulos).

## Cómo leer este reporte

- **Fila**: cada fila del inventario es una combinación de país, publisher, app y metadata de contenido, no un programa. **Requests** son las solicitudes de anuncio de esa fila; cada cifra se da en filas y en requests.
- **Tal como llega (consolidado)** es el inventario tal como lo mandan los vendedores. **Después del relleno** es el mismo inventario después de que el pipeline de relleno completó los valores vacíos.
- **Evidencia**: el título de la fila se busca en IMDb y Wikidata. Cuando se encuentra (un **match**), esas bases dicen si es película o serie y qué géneros tiene. Cubre 531,080 filas (49.5% del total). Confianza del match: A = sin ambigüedad; B = podría ser un título homónimo (acierta ~3 de cada 4). Se usan matches de confianza B o mejor.
- **Formato de las celdas**: `12,345 filas (12.3%) · 4.5% req` = cantidad de filas, % de filas y % de requests sobre la base que indica cada tabla.
- **Géneros comparables**: los géneros declarados se traducen al vocabulario del proyecto y se agrupan en conceptos que IMDb también usa (thriller, misterio y crimen → crimen-misterio; acción, aventura y bélico → acción-aventura; anime → animación). Lo que IMDb no maneja (lifestyle, viajes, cocina, religión, educación, videojuegos, "entertainment", "other", "movies", "tv") no se juzga.

**Base de los porcentajes:** en la parte 1 (correctitud) son sobre las **filas con género declarado**; en la parte 2 (completitud), sobre el **total de filas**.

---

## 1. Correctitud: ¿el género declarado coincide con IMDb/Wikidata?

Cada género comparable que declara la fila se compara con los del título en IMDb/Wikidata: **acierta** si está entre ellos; **es vecino** si no está pero es un género cercano (telenovela y drama/romance, thriller y terror, infantil y animación, documental y reality); **choca** si ni lo uno ni lo otro. El veredicto de la fila junta todos sus géneros:

- **Coincide** (`coincide`): todo lo declarado acierta.
- **Parecido** (`afin`): nada choca, pero tampoco acierta; son géneros vecinos.
- **Acierta en parte** (`parcial`): hay géneros que aciertan y otros que chocan.
- **Contradice** (`contradice`): choca y nada acierta.
- **No se pudo evaluar** (`no_evaluable`): sin match, o sin género comparable.

| Dataset | Filas con género | Evaluables (% de las con género) | Coincide | Parecido | Acierta en parte | Contradice | Filas que contradicen |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Tal como llega (consolidado)** | 990,646 (92.4% del total) | 485,450 (49.0%) | 84.9% · 83.2% req | 5.0% · 8.9% req | 7.2% · 3.1% req | 3.0% · 4.8% req | 14,681 |
| **Después del relleno** | 1,046,061 (97.6% del total) | 509,120 (48.7%) | 85.5% · 84.0% req | 4.7% · 8.4% req | 6.9% · 3.0% req | 2.9% · 4.6% req | 14,681 |

*Los % de las cuatro columnas de veredicto son sobre las filas evaluables.*

### 1.1 Cómo vienen escritos los géneros

Un valor cuenta como **género reconocido** si al menos una de sus palabras está en el diccionario de géneros del proyecto. Lo demás se clasifica según qué es:

| Tipo de valor | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Género reconocido (`mapeado`) | 923,866 filas (93.3%) · 95.9% req | 974,438 filas (93.2%) · 95.6% req |
| Género mal escrito o mal codificado (`no_mapeado:genero_en_formato_sucio`) | 22,949 filas (2.3%) · 1.0% req | 23,013 filas (2.2%) · 1.0% req |
| Idioma o región, no género (`no_mapeado:idioma_o_region`) | 2,271 filas (0.2%) · 0.1% req | 2,560 filas (0.2%) · 0.1% req |
| Texto que no es un género conocido (`no_mapeado:otros_no_reconocidos`) | 20,186 filas (2.0%) · 1.5% req | 22,912 filas (2.2%) · 1.8% req |
| Etiqueta técnica del vendedor (genre_…) (`no_mapeado:prefijo_tecnico`) | 8,685 filas (0.9%) · 0.7% req | 8,685 filas (0.8%) · 0.6% req |
| Tema de interés, no género (outdoors, arts) (`no_mapeado:tema_no_genero`) | 4,135 filas (0.4%) · 0.6% req | 4,382 filas (0.4%) · 0.6% req |
| Dice el tipo de contenido (movies, live), no el género (`no_mapeado:tipo_de_contenido`) | 8,554 filas (0.9%) · 0.2% req | 10,071 filas (1.0%) · 0.3% req |

Cuántos géneros comparables declara cada fila (0 = solo valores genéricos como "entertainment"):

| Géneros comparables por fila | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| 0 géneros | 163,297 filas (16.5%) · 16.5% req | 192,162 filas (18.4%) · 18.0% req |
| 1 género | 603,331 filas (60.9%) · 75.4% req | 613,063 filas (58.6%) · 72.7% req |
| 2 géneros | 136,030 filas (13.7%) · 4.8% req | 146,181 filas (14.0%) · 5.3% req |
| 3 géneros | 87,988 filas (8.9%) · 3.4% req | 94,655 filas (9.1%) · 4.0% req |

### 1.2 Qué género choca y con qué se confunde

**Tal como llega (consolidado)** — género declarado que choca con la evidencia (filas con veredicto "acierta en parte" o "contradice"):

| Género declarado | Filas | Requests |
|---|---:|---:|
| `drama` | 15,782 | 4,739,554,880 |
| `accion-aventura` | 12,919 | 2,932,357,520 |
| `documental` | 4,687 | 1,528,064,160 |
| `comedia` | 3,925 | 393,387,840 |
| `infantil-familia` | 3,914 | 516,057,360 |
| `terror` | 3,223 | 462,922,960 |
| `fantasia` | 2,664 | 248,804,160 |
| `musica` | 2,569 | 453,863,360 |
| `crimen-misterio` | 2,289 | 319,644,160 |
| `deportes` | 2,164 | 743,978,080 |
| `romance` | 942 | 96,827,600 |
| `animacion` | 739 | 68,492,480 |

Confusiones más frecuentes en Tal como llega (consolidado) (género declarado → lo que dice IMDb/Wikidata):

| Declarado → lo que dice la evidencia | Filas | Requests |
|---|---:|---:|
| `drama -> comedia` | 5,634 | 1,761,372,320 |
| `accion-aventura -> drama` | 3,790 | 611,974,720 |
| `drama -> terror` | 3,159 | 1,768,581,200 |
| `drama -> infantil-familia` | 2,652 | 635,707,680 |
| `terror -> drama` | 2,169 | 315,532,640 |
| `accion-aventura -> documental` | 1,760 | 437,041,200 |
| `accion-aventura -> terror` | 1,746 | 297,210,240 |
| `accion-aventura -> reality` | 1,468 | 302,123,200 |
| `infantil-familia -> drama` | 1,467 | 146,463,920 |
| `comedia -> drama` | 1,443 | 127,211,600 |
| `accion-aventura -> comedia` | 1,184 | 356,270,400 |
| `drama -> sci-fi` | 1,084 | 147,618,160 |
| `documental -> comedia,drama` | 876 | 131,836,000 |
| `accion-aventura -> deportes,documental` | 847 | 114,587,520 |
| `crimen-misterio -> sci-fi` | 771 | 153,314,800 |

**Después del relleno** — género declarado que choca con la evidencia (filas con veredicto "acierta en parte" o "contradice"):

| Género declarado | Filas | Requests |
|---|---:|---:|
| `drama` | 15,815 | 4,743,453,520 |
| `accion-aventura` | 13,018 | 2,945,070,800 |
| `documental` | 4,711 | 1,530,026,000 |
| `infantil-familia` | 3,952 | 518,902,320 |
| `comedia` | 3,941 | 395,440,320 |
| `terror` | 3,224 | 462,975,280 |
| `fantasia` | 2,664 | 248,804,160 |
| `musica` | 2,569 | 453,863,360 |
| `crimen-misterio` | 2,300 | 320,464,080 |
| `deportes` | 2,183 | 746,252,640 |
| `romance` | 1,000 | 104,561,840 |
| `sci-fi` | 739 | 207,056,640 |

Confusiones más frecuentes en Después del relleno (género declarado → lo que dice IMDb/Wikidata):

| Declarado → lo que dice la evidencia | Filas | Requests |
|---|---:|---:|
| `drama -> comedia` | 5,634 | 1,761,372,320 |
| `accion-aventura -> drama` | 3,796 | 612,453,200 |
| `drama -> terror` | 3,159 | 1,768,581,200 |
| `drama -> infantil-familia` | 2,652 | 635,707,680 |
| `terror -> drama` | 2,169 | 315,532,640 |
| `accion-aventura -> documental` | 1,760 | 437,041,200 |
| `accion-aventura -> terror` | 1,746 | 297,210,240 |
| `infantil-familia -> drama` | 1,473 | 146,870,320 |
| `accion-aventura -> reality` | 1,468 | 302,123,200 |
| `comedia -> drama` | 1,445 | 127,478,480 |
| `accion-aventura -> comedia` | 1,184 | 356,270,400 |
| `drama -> sci-fi` | 1,084 | 147,618,160 |
| `documental -> comedia,drama` | 876 | 131,836,000 |
| `accion-aventura -> deportes,documental` | 847 | 114,587,520 |
| `crimen-misterio -> sci-fi` | 771 | 153,314,800 |

### 1.3 Quién acierta y quién no

Los % son sobre las filas con género de cada grupo.

### Por país — Tal como llega (consolidado)

| País | Filas | Coincide | Parecido (género vecino) | Acierta en parte | Contradice | No se pudo evaluar |
|---|---:|---:|---:|---:|---:|---:|
| Mexico | 299,990 | 37.1% | 1.9% | 2.5% | 1.2% | 57.4% |
| Colombia | 105,126 | 44.5% | 3.1% | 3.9% | 2.1% | 46.4% |
| Chile | 113,652 | 44.1% | 2.7% | 3.8% | 1.6% | 47.8% |

### Por publisher — Tal como llega (consolidado)

| Publisher | Filas | Coincide | Parecido (género vecino) | Acierta en parte | Contradice | No se pudo evaluar |
|---|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 206,852 | 45.2% | 2.0% | 5.1% | 1.2% | 46.5% |
| iion Pty Ltd | 184,262 | 46.8% | 3.0% | 4.0% | 1.9% | 44.3% |
| TCL ADS - Springserve | 122,639 | 46.6% | 2.6% | 4.7% | 1.5% | 44.6% |
| TCL ADs (APAC) | 117,739 | 48.1% | 2.8% | 5.2% | 1.5% | 42.4% |
| Select Plus PTE LTD (CTV) | 89,816 | 49.2% | 6.1% | 0.0% | 3.9% | 40.8% |
| PML Digital | 24,860 | 47.5% | 2.0% | 5.3% | 1.2% | 44.0% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 24,557 | 50.4% | 2.5% | 3.9% | 1.3% | 41.8% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 25,016 | 41.6% | 0.8% | 1.9% | 0.5% | 55.2% |
| AWG Media | 19,280 | 10.9% | 0.3% | 0.5% | 0.9% | 87.4% |
| Vidaa | 18,879 | 29.1% | 0.1% | 0.0% | 0.3% | 70.5% |
| Televisa Univision via SpringServe | 15,093 | 49.8% | 0.1% | 0.0% | 0.8% | 49.3% |
| Coocaa, a SKYWORTH company | 14,646 | 9.4% | 0.3% | 0.2% | 1.0% | 89.1% |

### Por país — Después del relleno

| País | Filas | Coincide | Parecido (género vecino) | Acierta en parte | Contradice | No se pudo evaluar |
|---|---:|---:|---:|---:|---:|---:|
| Mexico | 318,005 | 37.8% | 1.8% | 2.3% | 1.1% | 57.0% |
| Colombia | 111,771 | 43.5% | 3.0% | 3.7% | 2.0% | 47.9% |
| Chile | 120,778 | 44.0% | 2.5% | 3.6% | 1.5% | 48.4% |

### Por publisher — Después del relleno

| Publisher | Filas | Coincide | Parecido (género vecino) | Acierta en parte | Contradice | No se pudo evaluar |
|---|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 217,399 | 45.3% | 1.9% | 4.9% | 1.1% | 46.7% |
| iion Pty Ltd | 202,016 | 46.2% | 2.8% | 3.7% | 1.7% | 45.5% |
| TCL ADS - Springserve | 130,788 | 46.6% | 2.4% | 4.5% | 1.4% | 45.1% |
| TCL ADs (APAC) | 124,435 | 48.0% | 2.6% | 4.9% | 1.4% | 43.0% |
| Select Plus PTE LTD (CTV) | 95,712 | 48.0% | 5.8% | 0.0% | 3.6% | 42.6% |
| PML Digital | 25,939 | 46.8% | 2.0% | 5.1% | 1.2% | 45.0% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 25,319 | 50.1% | 2.4% | 3.8% | 1.2% | 42.4% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 25,177 | 41.6% | 0.8% | 1.9% | 0.5% | 55.2% |
| AWG Media | 20,255 | 11.5% | 0.3% | 0.5% | 0.8% | 87.0% |
| Vidaa | 18,999 | 29.4% | 0.1% | 0.0% | 0.3% | 70.3% |
| Televisa Univision via SpringServe | 15,109 | 49.8% | 0.1% | 0.0% | 0.8% | 49.3% |
| Coocaa, a SKYWORTH company | 15,529 | 10.0% | 0.3% | 0.1% | 1.0% | 88.6% |

En el dataset rellenado, el **origen** dice de dónde salió el género. El origen IMDb se juzga contra la misma fuente que lo generó, así que su acierto solo prueba consistencia.

### Por origen del valor — Después del relleno

| Origen del valor | Filas | Coincide | Parecido (género vecino) | Acierta en parte | Contradice | No se pudo evaluar |
|---|---:|---:|---:|---:|---:|---:|
| Valor habitual de la app (`app_default`) | 1,846 | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% |
| IMDb (`imdb`) | 22,371 | 98.5% | 0.0% | 0.0% | 0.0% | 1.5% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 31,198 | 4.4% | 0.1% | 0.8% | 0.0% | 94.8% |
| Venía del vendedor (`original`) | 990,646 | 41.6% | 2.4% | 3.5% | 1.5% | 51.0% |

### 1.4 Las contradicciones con más tráfico

**Tal como llega (consolidado)** (un título por fila; lista completa en `validacion-consolidado-muestra-genero-contradicciones.csv`):

| Título | Género declarado | Géneros IMDb | Extra de Wikidata | Match IMDb | Confianza | Publisher (ejemplo) | Filas | Requests |
|---|---|---|---|---|---|---|---:|---:|
| `penance lane` | `Drama` | Horror |  | tt1964995 Penance Lane | A | OTTera.tv | 1,283 | 1,408,919,040 |
| `rollers: trailer` | `Drama` | Comedy |  | tt9124868 Rollers | B | OTTera.tv | 707 | 713,742,640 |
| `formentera` | `Documentary` | Drama |  | tt1990232 Formentera | A | TCL ADS - Springserve | 69 | 442,072,560 |
| `lost in the maze` | `Adventure` | Documentary |  | tt29602142 Lost in the Maze | A | OTTera.tv | 500 | 270,701,600 |
| `the buddy cop` | `Action` | Comedy |  | tt20412912 The Buddy Cop | A | OTTera.tv | 504 | 269,798,080 |
| `tennis+` | `Sports` | Comedy,Drama,Sci-Fi |  | tt2281489 Tennis | B | OTTera.tv | 71 | 263,912,000 |
| `the secret handshake` | `Drama` | Family |  | tt3519936 The Secret Handshake | B | OTTera.tv | 265 | 242,553,440 |
| `a royal christmas on ice` | `Documentary` | Comedy,Drama,Romance |  | tt19408396 A Royal Christmas on Ice | A | OTTera.tv | 18 | 178,267,600 |
| `machotaildrop` | `Sports` | Action,Comedy,Fantasy |  | tt1315388 Machotaildrop | A | TCL ADS - Springserve | 222 | 170,185,920 |
| `we three kings` | `Drama` | Family |  | tt13091334 We Three Kings | B | OTTera.tv | 411 | 152,655,440 |
| `13 score` | `Action` | Horror |  | tt3168890 13 Score | A | OTTera.tv | 521 | 142,118,080 |
| `duck camp dinners season 2` | `Adventure` | Reality-TV |  | tt35146256 Duck Camp Dinners | A | OTTera.tv | 500 | 138,832,800 |
| `grumpy grannies` | `Drama` | Comedy |  | tt19306948 Grumpy Grannies | A | OTTera.tv | 303 | 114,558,800 |
| `dino the dinosaur season 1` | `Adventure` | Animation,Family |  | tt7818384 Dino the Dinosaur | A | iion Pty Ltd | 26 | 101,908,160 |
| `7 years` | `Horror` | Drama |  | tt5517438 7 Years | B | OTTera.tv | 296 | 95,528,400 |
| `displaced` | `Family` | Drama,Short | documental | tt14717664 Displaced | B | OTTera.tv | 291 | 95,315,920 |
| `friends only` | `Family` | Drama,Romance |  | tt15680876 Friends Only | A | OTTera.tv | 290 | 94,634,720 |
| `stray` | `Drama` | Documentary |  | tt11905922 Stray | B | OTTera.tv | 285 | 93,424,560 |
| `sin's kitchen: trailer` | `Adventure` | Drama |  | tt0203912 Sin's Kitchen | A | OTTera.tv | 433 | 87,862,800 |
| `crack` | `Documentary` | Comedy,Crime,Drama |  | tt4424356 Crack | B | OTTera.tv | 23 | 81,974,880 |

**Después del relleno** (un título por fila; lista completa en `validacion-relleno-muestra-genero-contradicciones.csv`):

| Título | Género declarado | Géneros IMDb | Extra de Wikidata | Match IMDb | Confianza | Publisher (ejemplo) | Filas | Requests |
|---|---|---|---|---|---|---|---:|---:|
| `penance lane` | `Drama` | Horror |  | tt1964995 Penance Lane | A | OTTera.tv | 1,283 | 1,408,919,040 |
| `rollers: trailer` | `Drama` | Comedy |  | tt9124868 Rollers | B | OTTera.tv | 707 | 713,742,640 |
| `formentera` | `Documentary` | Drama |  | tt1990232 Formentera | A | TCL ADS - Springserve | 69 | 442,072,560 |
| `lost in the maze` | `Adventure` | Documentary |  | tt29602142 Lost in the Maze | A | OTTera.tv | 500 | 270,701,600 |
| `the buddy cop` | `Action` | Comedy |  | tt20412912 The Buddy Cop | A | OTTera.tv | 504 | 269,798,080 |
| `tennis+` | `Sports` | Comedy,Drama,Sci-Fi |  | tt2281489 Tennis | B | OTTera.tv | 71 | 263,912,000 |
| `the secret handshake` | `Drama` | Family |  | tt3519936 The Secret Handshake | B | OTTera.tv | 265 | 242,553,440 |
| `a royal christmas on ice` | `Documentary` | Comedy,Drama,Romance |  | tt19408396 A Royal Christmas on Ice | A | OTTera.tv | 18 | 178,267,600 |
| `machotaildrop` | `Sports` | Action,Comedy,Fantasy |  | tt1315388 Machotaildrop | A | TCL ADS - Springserve | 222 | 170,185,920 |
| `we three kings` | `Drama` | Family |  | tt13091334 We Three Kings | B | OTTera.tv | 411 | 152,655,440 |
| `13 score` | `Action` | Horror |  | tt3168890 13 Score | A | OTTera.tv | 521 | 142,118,080 |
| `duck camp dinners season 2` | `Adventure` | Reality-TV |  | tt35146256 Duck Camp Dinners | A | OTTera.tv | 500 | 138,832,800 |
| `grumpy grannies` | `Drama` | Comedy |  | tt19306948 Grumpy Grannies | A | OTTera.tv | 303 | 114,558,800 |
| `dino the dinosaur season 1` | `Adventure` | Animation,Family |  | tt7818384 Dino the Dinosaur | A | iion Pty Ltd | 26 | 101,908,160 |
| `7 years` | `Horror` | Drama |  | tt5517438 7 Years | B | OTTera.tv | 296 | 95,528,400 |
| `displaced` | `Family` | Drama,Short | documental | tt14717664 Displaced | B | OTTera.tv | 291 | 95,315,920 |
| `friends only` | `Family` | Drama,Romance |  | tt15680876 Friends Only | A | OTTera.tv | 290 | 94,634,720 |
| `stray` | `Drama` | Documentary |  | tt11905922 Stray | B | OTTera.tv | 285 | 93,424,560 |
| `sin's kitchen: trailer` | `Adventure` | Drama |  | tt0203912 Sin's Kitchen | A | OTTera.tv | 433 | 87,862,800 |
| `crack` | `Documentary` | Comedy,Crime,Drama |  | tt4424356 Crack | B | OTTera.tv | 23 | 81,974,880 |

## 2. Completitud: ¿se pueden agregar géneros?

Nivel de detalle del género: **nivel 0** = vacío; **nivel 1** = sin género comparable (solo "entertainment", "other" o un tipo de contenido); **nivel 2** = un género; **nivel 3** = dos o más. La **propuesta** conserva lo declarado que no choca y agrega los géneros de IMDb (hasta 3) y los extra de Wikidata (telenovela, holiday, indie…), en el vocabulario del proyecto.

Punto de partida (% del total de filas):

| Estado | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Sin género (`vacia`) | 81,194 filas (7.6%) · 15.5% req | 25,779 filas (2.4%) · 11.3% req |
| Con género que no contradice (`llena`) | 975,965 filas (91.1%) · 82.8% req | 1,031,380 filas (96.2%) · 87.0% req |
| Con género que contradice (`contradicha`) | 14,681 filas (1.4%) · 1.6% req | 14,681 filas (1.4%) · 1.6% req |

Nivel de detalle actual y nivel alcanzable (% del total de filas):

| Nivel | Tal como llega (consolidado) · hoy | Tal como llega (consolidado) · alcanzable | Después del relleno · hoy | Después del relleno · alcanzable |
|---|---:|---:|---:|---:|
| Nivel 0 · vacío | 81,194 filas (7.6%) · 15.5% req | 56,772 filas (5.3%) · 13.6% req | 25,779 filas (2.4%) · 11.3% req | 25,779 filas (2.4%) · 11.3% req |
| Nivel 1 · sin género comparable (solo "entertainment", "other"…) | 163,297 filas (15.2%) · 13.9% req | 142,129 filas (13.3%) · 13.3% req | 192,162 filas (17.9%) · 16.0% req | 170,242 filas (15.9%) · 15.3% req |
| Nivel 2 · un género | 603,331 filas (56.3%) · 63.7% req | 431,703 filas (40.3%) · 44.2% req | 613,063 filas (57.2%) · 64.4% req | 434,223 filas (40.5%) · 44.4% req |
| Nivel 3 · dos o más géneros | 224,018 filas (20.9%) · 6.9% req | 441,236 filas (41.2%) · 29.0% req | 240,836 filas (22.5%) · 8.3% req | 441,596 filas (41.2%) · 29.0% req |

Qué cambiaría fila a fila:

| Qué pasa con la fila | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Se puede llenar (estaba vacía) (`rellena`) | 24,422 filas (2.3%) · 1.9% req | — |
| Se pueden agregar géneros o uno más preciso (`sube`) | 244,354 filas (22.8%) · 21.8% req | 248,951 filas (23.2%) · 22.0% req |
| Se puede corregir (contradecía) (`corrige`) | 14,681 filas (1.4%) · 1.6% req | 14,681 filas (1.4%) · 1.6% req |
| Se corrige en parte (acertaba en parte) (`corrige_parcial`) | 34,739 filas (3.2%) · 1.1% req | 34,975 filas (3.3%) · 1.1% req |
| Se queda igual (ya está bien) (`mantiene`) | 696,872 filas (65.0%) · 60.0% req | 747,454 filas (69.7%) · 63.9% req |
| Sin propuesta (sin evidencia) (`sin_propuesta`) | 56,772 filas (5.3%) · 13.6% req | 25,779 filas (2.4%) · 11.3% req |

**Telenovela** es el caso concreto de "un género más preciso": Wikidata la marca como género propio y los vendedores declaran solo "drama". Filas de títulos que Wikidata clasifica como telenovela:

| Telenovela según Wikidata | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Se puede proponer telenovela (`propuesta`) | 17,710 filas (1.6%) · 4.6% req | 17,710 filas (1.6%) · 4.6% req |
| Ya declarada como telenovela (`ya_declarada`) | 56 filas (0.0%) · 0.0% req | 56 filas (0.0%) · 0.0% req |

Por grupo (% sobre las filas del grupo):

### Por país — Tal como llega (consolidado)

| País | Filas | Se puede llenar (estaba vacía) | Se pueden agregar géneros o uno más preciso | Se puede corregir (contradecía) | Se corrige en parte (acertaba en parte) | Se queda igual (ya está bien) | Sin propuesta (sin evidencia) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mexico | 328,845 | 2.8% | 22.8% | 1.1% | 2.2% | 65.1% | 6.0% |
| Colombia | 114,223 | 1.7% | 22.9% | 1.9% | 3.6% | 63.7% | 6.2% |
| Chile | 122,923 | 2.5% | 23.2% | 1.5% | 3.5% | 64.3% | 5.1% |

### Por publisher — Tal como llega (consolidado)

| Publisher | Filas | Se puede llenar (estaba vacía) | Se pueden agregar géneros o uno más preciso | Se puede corregir (contradecía) | Se corrige en parte (acertaba en parte) | Se queda igual (ya está bien) | Sin propuesta (sin evidencia) |
|---|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 220,835 | 2.3% | 21.2% | 1.1% | 4.8% | 66.6% | 4.0% |
| iion Pty Ltd | 207,466 | 3.6% | 23.8% | 1.7% | 3.6% | 59.7% | 7.6% |
| TCL ADS - Springserve | 133,483 | 3.0% | 22.9% | 1.4% | 4.3% | 63.3% | 5.2% |
| TCL ADs (APAC) | 126,143 | 2.5% | 23.0% | 1.4% | 4.9% | 64.1% | 4.2% |
| Select Plus PTE LTD (CTV) | 96,962 | 1.8% | 36.5% | 3.6% | 0.0% | 52.6% | 5.5% |
| PML Digital | 26,250 | 1.4% | 21.0% | 1.2% | 5.0% | 67.6% | 3.9% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 25,773 | 1.2% | 28.7% | 1.2% | 3.8% | 61.6% | 3.5% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 25,730 | 0.5% | 31.2% | 0.5% | 1.8% | 63.6% | 2.3% |
| AWG Media | 20,424 | 1.3% | 9.2% | 0.8% | 0.5% | 83.9% | 4.3% |
| Vidaa | 19,325 | 0.5% | 29.9% | 0.3% | 0.0% | 67.5% | 1.8% |
| Televisa Univision via SpringServe | 15,690 | 0.1% | 43.3% | 0.8% | 0.0% | 52.1% | 3.7% |
| Coocaa, a SKYWORTH company | 15,655 | 1.4% | 8.1% | 1.0% | 0.1% | 84.4% | 5.0% |

Propuestas más frecuentes en Tal como llega (consolidado) (% del total de filas):

| Géneros propuestos | Filas | % de filas | % de requests |
|---|---:|---:|---:|
| `drama` | 10,261 | 1.0% | 0.6% |
| `drama,romance` | 9,999 | 0.9% | 0.8% |
| `drama,comedia` | 8,256 | 0.8% | 0.8% |
| `terror,thriller` | 8,068 | 0.8% | 0.7% |
| `comedia` | 7,286 | 0.7% | 0.6% |
| `drama,romance,telenovela` | 7,221 | 0.7% | 2.1% |
| `drama,thriller` | 6,980 | 0.7% | 0.8% |
| `drama,crimen` | 6,280 | 0.6% | 0.4% |
| `drama,comedia,romance` | 5,822 | 0.5% | 0.5% |
| `terror,misterio` | 5,604 | 0.5% | 0.4% |
| `documental` | 5,208 | 0.5% | 0.3% |
| `terror,comedia` | 5,039 | 0.5% | 0.5% |
| `drama,telenovela` | 4,634 | 0.4% | 0.9% |
| `western,drama` | 4,033 | 0.4% | 0.2% |
| `crimen,drama` | 3,635 | 0.3% | 0.2% |
| `thriller,drama` | 3,504 | 0.3% | 0.2% |
| `accion,crimen,drama` | 3,503 | 0.3% | 0.3% |
| `drama,documental` | 3,379 | 0.3% | 0.4% |
| `documental,deportes` | 3,057 | 0.3% | 0.3% |
| `terror` | 3,048 | 0.3% | 0.4% |

### Por país — Después del relleno

| País | Filas | Se puede llenar (estaba vacía) | Se pueden agregar géneros o uno más preciso | Se puede corregir (contradecía) | Se corrige en parte (acertaba en parte) | Se queda igual (ya está bien) | Sin propuesta (sin evidencia) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mexico | 328,845 | 0.0% | 23.3% | 1.1% | 2.2% | 70.1% | 3.3% |
| Colombia | 114,223 | 0.0% | 23.3% | 1.9% | 3.6% | 69.1% | 2.1% |
| Chile | 122,923 | 0.0% | 23.6% | 1.5% | 3.5% | 69.7% | 1.7% |

### Por publisher — Después del relleno

| Publisher | Filas | Se puede llenar (estaba vacía) | Se pueden agregar géneros o uno más preciso | Se puede corregir (contradecía) | Se corrige en parte (acertaba en parte) | Se queda igual (ya está bien) | Sin propuesta (sin evidencia) |
|---|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 220,835 | 0.0% | 21.6% | 1.1% | 4.8% | 71.0% | 1.6% |
| iion Pty Ltd | 207,466 | 0.0% | 24.5% | 1.7% | 3.6% | 67.6% | 2.6% |
| TCL ADS - Springserve | 133,483 | 0.0% | 23.4% | 1.4% | 4.4% | 68.9% | 2.0% |
| TCL ADs (APAC) | 126,143 | 0.0% | 23.5% | 1.4% | 4.9% | 68.9% | 1.4% |
| Select Plus PTE LTD (CTV) | 96,962 | 0.0% | 36.7% | 3.6% | 0.0% | 58.4% | 1.3% |
| PML Digital | 26,250 | 0.0% | 21.3% | 1.2% | 5.0% | 71.3% | 1.2% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 25,773 | 0.0% | 29.2% | 1.2% | 3.8% | 64.0% | 1.8% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 25,730 | 0.0% | 31.5% | 0.5% | 1.8% | 64.0% | 2.1% |
| AWG Media | 20,424 | 0.0% | 9.5% | 0.8% | 0.5% | 88.4% | 0.8% |
| Vidaa | 19,325 | 0.0% | 30.0% | 0.3% | 0.0% | 68.0% | 1.7% |
| Televisa Univision via SpringServe | 15,690 | 0.0% | 43.3% | 0.8% | 0.0% | 52.2% | 3.7% |
| Coocaa, a SKYWORTH company | 15,655 | 0.0% | 8.4% | 1.0% | 0.1% | 89.7% | 0.8% |

### Por origen del valor — Después del relleno

| Origen del valor | Filas | Se puede llenar (estaba vacía) | Se pueden agregar géneros o uno más preciso | Se puede corregir (contradecía) | Se corrige en parte (acertaba en parte) | Se queda igual (ya está bien) | Sin propuesta (sin evidencia) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Valor habitual de la app (`app_default`) | 1,846 | 0.0% | 2.0% | 0.0% | 0.0% | 98.0% | 0.0% |
| IMDb (`imdb`) | 22,371 | 0.0% | 15.8% | 0.0% | 0.0% | 84.2% | 0.0% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 31,198 | 0.0% | 3.3% | 0.0% | 0.8% | 96.0% | 0.0% |
| Venía del vendedor (`original`) | 990,646 | 0.0% | 24.7% | 1.5% | 3.5% | 70.3% | 0.0% |

Propuestas más frecuentes en Después del relleno (% del total de filas):

| Géneros propuestos | Filas | % de filas | % de requests |
|---|---:|---:|---:|
| `drama,romance` | 9,546 | 0.9% | 0.8% |
| `drama,comedia` | 8,256 | 0.8% | 0.8% |
| `drama` | 8,077 | 0.8% | 0.4% |
| `terror,thriller` | 7,692 | 0.7% | 0.7% |
| `drama,romance,telenovela` | 7,221 | 0.7% | 2.1% |
| `comedia` | 6,531 | 0.6% | 0.5% |
| `drama,crimen` | 6,285 | 0.6% | 0.4% |
| `drama,thriller` | 6,222 | 0.6% | 0.7% |
| `drama,comedia,romance` | 5,850 | 0.6% | 0.5% |
| `terror,comedia` | 5,039 | 0.5% | 0.5% |
| `terror,misterio` | 4,946 | 0.5% | 0.4% |
| `drama,telenovela` | 4,634 | 0.4% | 0.9% |
| `documental` | 4,423 | 0.4% | 0.2% |
| `western,drama` | 4,036 | 0.4% | 0.2% |
| `thriller,drama` | 3,504 | 0.3% | 0.2% |
| `drama,documental` | 3,095 | 0.3% | 0.4% |
| `accion,crimen,drama` | 2,970 | 0.3% | 0.2% |
| `romance,comedia` | 2,936 | 0.3% | 0.4% |
| `crimen,drama` | 2,924 | 0.3% | 0.2% |
| `documental,deportes` | 2,826 | 0.3% | 0.3% |

## 3. Límites

- El género es opinable y IMDb trae hasta tres: por eso existe "parecido" y la cifra dura es "contradice" (nada de lo declarado cabe).
- Un match de confianza B falla 1 de cada 4 veces; una contradicción con confianza B puede ser culpa del match. La muestra trae la confianza para filtrar.
- Lo no comparable (lifestyle, viajes, cocina, religión, videojuegos) no se valida ni se propone: IMDb no lo registra.
- En el dataset rellenado, el origen IMDb del género se valida contra la misma fuente: su acierto es circular.
