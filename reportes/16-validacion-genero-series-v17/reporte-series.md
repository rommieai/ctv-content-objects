# Reporte — contentSeries: correctitud básica y cuántas filas son serie sin decirlo

**Fuentes:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas, columna `contentSeries`); `inventory-consolidado-v10-a-v17-relleno.csv` (959,442 filas, columna `contentSeries_relleno`).  
**Generado con:** `scripts/validar_genero_series.py` + `scripts/generar_reporte_genero_series.py`. Corrida del 2026-09-09 16:03. Evidencia: tipo IMDb (movie / tvSeries / tvMiniSeries; match ≥ B), el título crudo ("season 2", "S01E03", "ep 4") y las demás rutas del mismo título (≥ 30 filas con serie y ≥ 2 publishers, como en el relleno).

**Convención:** "serie real" = un `contentSeries` que no es vacío, ni centinela, ni el hash MD5 de cadena vacía, ni un placeholder (`VOD`, `No Series`, `OTT Studios …`). En correctitud los % son sobre las filas con serie real; en completitud, sobre el total de filas.

---

## 1. Correctitud (básica)

Solo se juzga lo que IMDb puede juzgar: `coincide` = IMDb dice serie y la serie declarada es el título canónico o el título de la fila; `otro_nombre` = IMDb dice serie pero la serie declarada se llama distinto (episodio con nombre propio, o error; compatible); `contradice` = IMDb (A/B) dice película y el título no trae temporada/episodio; `no_evaluable` = sin match o tipo ambiguo (short, video, tvMovie).

| Dataset | Filas con serie real | coincide | otro_nombre | contradice | no_evaluable |
|---|---:|---:|---:|---:|---:|
| **consolidado** | 51,672 (5.4% del total; req 6.4%) | 1,276 (2.5%) · req 2.3% | 2,802 (5.4%) · req 6.3% | 1,252 (2.4%) · req 1.1% | 46,342 (89.7%) · req 90.3% |
| **relleno** | 124,281 (12.9% del total; req 15.5%) | 69,673 (56.1%) · req 57.0% | 2,934 (2.4%) · req 2.7% | 1,519 (1.2%) · req 0.8% | 50,155 (40.4%) · req 39.6% |

Qué trae la columna (% del total de filas): serie real vs placeholders:

| Contenido de contentSeries | consolidado | relleno |
|---|---:|---:|
| `placeholder:no series` | 985 (0.1%) · req 0.0% | 985 (0.1%) · req 0.0% |
| `placeholder:ott studios entertainment livestream` | 480 (0.1%) · req 0.0% | 480 (0.1%) · req 0.0% |
| `placeholder:ott studios entertainment on demand` | 1,985 (0.2%) · req 0.0% | 1,985 (0.2%) · req 0.0% |
| `placeholder:ott studios sports livestream` | 974 (0.1%) · req 0.1% | 974 (0.1%) · req 0.1% |
| `placeholder:research unit` | 686 (0.1%) · req 0.0% | 686 (0.1%) · req 0.0% |
| `placeholder:video chart` | 301 (0.0%) · req 0.0% | 301 (0.0%) · req 0.0% |
| `placeholder:vod` | 5,725 (0.6%) · req 0.3% | 5,725 (0.6%) · req 0.3% |
| `serie_real` | 51,672 (5.4%) · req 6.4% | 124,281 (12.9%) · req 15.5% |

### Por publisher — consolidado

|  | Filas | `coincide` | `otro_nombre` | `contradice` | `no_evaluable` |
|---|---:|---:|---:|---:|---:|
| OTTera.tv | 631 | 5.4% | 5.1% | 13.6% | 75.9% |
| iion Pty Ltd | 207 | 1.9% | 2.4% | 4.8% | 90.8% |
| TCL ADS - Springserve | 400 | 7.2% | 2.2% | 13.5% | 77.0% |
| TCL ADs (APAC) | 379 | 5.0% | 1.6% | 12.4% | 81.0% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 1,790 | 1.1% | 0.8% | 3.3% | 94.9% |
| PML Digital | 50 | 0.0% | 2.0% | 12.0% | 86.0% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 1,307 | 3.1% | 0.3% | 5.0% | 91.6% |
| AWG Media | 13,768 | 1.9% | 8.0% | 0.8% | 89.4% |
| Vidaa | 230 | 0.9% | 21.7% | 1.3% | 76.1% |
| Coocaa, a SKYWORTH company | 13,394 | 2.3% | 8.0% | 0.8% | 88.9% |
| Televisa Univision via SpringServe | 59 | 0.0% | 6.8% | 3.4% | 89.8% |

Series declaradas en títulos que IMDb dice que son película (consolidado; muestra en `validacion-consolidado-muestra-series-contradicciones.csv`):

| Título | Serie declarada | IMDb (película) | Conf. | Publisher (ej.) | Filas | Requests |
|---|---|---|---|---|---:|---:|
| `surfing favela` | `Action Documentaries` | tt0949774 Surfing favela | A | Coocaa, a SKYWORTH company | 110 | 41,580,080 |
| `news` | `Euronews News` | tt1604683 News | B | Coocaa, a SKYWORTH company | 110 | 41,420,480 |
| `jajaja` | `JAJAJA` | tt1452626 Hahaha | A | TCL ADS - Springserve | 88 | 40,140,640 |
| `adam jones` | `FMX Stars` | tt2503944 Burnt | A | Coocaa, a SKYWORTH company | 64 | 39,037,920 |
| `tour du faso` | `Tour du Faso` | tt3502760 Tour du Faso | A | OTTera.tv | 14 | 21,818,320 |
| `cuento de otoño` | `Cuento de Otoño` | tt0137439 Autumn Tale | A | Kivi via Springserve | 32 | 6,775,760 |
| `una rosa sobre el ring` | `Modern Marvels` | tt0323837 Una rosa sobre el ring | A | AWG Media | 8 | 3,710,000 |
| `origine inconnue` | `Origine Inconnue` | tt4575328 2036 Origin Unknown | A | OTTera.tv | 30 | 2,525,600 |
| `santo en el museo de cera` | `Modern Marvels` | tt0057471 Santo in the Wax Museum | A | AWG Media | 4 | 2,487,920 |
| `guitarras lloren guitarras` | `Cold Case Files Classic` | tt0280716 Guitarras lloren guitarras | A | AWG Media | 9 | 1,786,240 |
| `72 horas` | `La Cacería` | tt1458175 The Next Three Days | B | FreeTV via Springserve | 11 | 1,644,960 |
| `piloto` | `Hell on Wheels` | tt31593809 Biker | B | FreeTV via Springserve | 19 | 1,475,520 |
| `carrera contra el tiempo` | `POUND OF FLESH (ESP)` | tt3488328 Pound of Flesh | B | FUNKE Digital GmbH | Publica | 19 | 1,454,720 |
| `providence` | `Citas de Estados Unidos` | tt6060392 Providence Island | B | LG Ads EMEA - SS | 14 | 1,308,960 |
| `charlotte` | `Citas de Estados Unidos` | tt5806814 Charlotte | B | LG Ads EMEA - SS | 15 | 1,135,440 |

### Por publisher — relleno

|  | Filas | `coincide` | `otro_nombre` | `contradice` | `no_evaluable` |
|---|---:|---:|---:|---:|---:|
| OTTera.tv | 14,296 | 91.2% | 0.4% | 0.6% | 7.8% |
| iion Pty Ltd | 13,607 | 86.6% | 0.4% | 0.5% | 12.5% |
| TCL ADS - Springserve | 8,735 | 90.7% | 0.3% | 0.7% | 8.3% |
| TCL ADs (APAC) | 8,358 | 90.7% | 0.4% | 0.6% | 8.3% |
| Select Plus PTE LTD (CTV) | 4,632 | 94.9% | 0.0% | 0.0% | 5.1% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 7,079 | 74.0% | 0.2% | 1.2% | 24.6% |
| PML Digital | 1,559 | 89.2% | 0.3% | 1.0% | 9.4% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 4,039 | 66.2% | 0.2% | 2.0% | 31.5% |
| AWG Media | 13,981 | 3.2% | 7.8% | 0.9% | 88.1% |
| Vidaa | 4,246 | 92.1% | 1.2% | 1.3% | 5.4% |
| Coocaa, a SKYWORTH company | 13,449 | 2.7% | 8.0% | 0.8% | 88.6% |
| Televisa Univision via SpringServe | 5,701 | 98.4% | 0.1% | 0.5% | 1.1% |

En el relleno, `imdb` se valida contra sí mismo (circular): su `coincide` solo prueba consistencia.

### Por origen del valor — relleno

|  | Filas | `coincide` | `otro_nombre` | `contradice` | `no_evaluable` |
|---|---:|---:|---:|---:|---:|
| imdb | 66,219 | 100.0% | 0.0% | 0.0% | 0.0% |
| intra_titulo | 6,390 | 34.1% | 2.1% | 4.2% | 59.7% |
| original | 51,672 | 2.5% | 5.4% | 2.4% | 89.7% |

Series declaradas en títulos que IMDb dice que son película (relleno; muestra en `validacion-relleno-muestra-series-contradicciones.csv`):

| Título | Serie declarada | IMDb (película) | Conf. | Publisher (ej.) | Filas | Requests |
|---|---|---|---|---|---:|---:|
| `jajaja` | `JAJAJA` | tt1452626 Hahaha | A | Vidaa | 332 | 258,652,960 |
| `surfing favela` | `Action Documentaries` | tt0949774 Surfing favela | A | Coocaa, a SKYWORTH company | 110 | 41,580,080 |
| `news` | `Euronews News` | tt1604683 News | B | Coocaa, a SKYWORTH company | 110 | 41,420,480 |
| `adam jones` | `FMX Stars` | tt2503944 Burnt | A | Coocaa, a SKYWORTH company | 64 | 39,037,920 |
| `tour du faso` | `Tour du Faso` | tt3502760 Tour du Faso | A | OTTera.tv | 14 | 21,818,320 |
| `cuento de otoño` | `Cuento de Otoño` | tt0137439 Autumn Tale | A | Kivi via Springserve | 32 | 6,775,760 |
| `origine inconnue` | `Origine Inconnue` | tt4575328 2036 Origin Unknown | A | OTTera.tv | 53 | 4,495,200 |
| `una rosa sobre el ring` | `Modern Marvels` | tt0323837 Una rosa sobre el ring | A | AWG Media | 8 | 3,710,000 |
| `santo en el museo de cera` | `Modern Marvels` | tt0057471 Santo in the Wax Museum | A | AWG Media | 4 | 2,487,920 |
| `guitarras lloren guitarras` | `Cold Case Files Classic` | tt0280716 Guitarras lloren guitarras | A | AWG Media | 9 | 1,786,240 |
| `72 horas` | `La Cacería` | tt1458175 The Next Three Days | B | FreeTV via Springserve | 11 | 1,644,960 |
| `piloto` | `Hell on Wheels` | tt31593809 Biker | B | FreeTV via Springserve | 19 | 1,475,520 |
| `carrera contra el tiempo` | `POUND OF FLESH (ESP)` | tt3488328 Pound of Flesh | B | FUNKE Digital GmbH | Publica | 19 | 1,454,720 |
| `providence` | `Citas de Estados Unidos` | tt6060392 Providence Island | B | LG Ads EMEA - SS | 14 | 1,308,960 |
| `charlotte` | `Citas de Estados Unidos` | tt5806814 Charlotte | B | LG Ads EMEA - SS | 15 | 1,135,440 |

## 2. Completitud: qué ES cada fila y qué se le puede poner

Para todas las filas se decide si el contenido es **serie**, **película**, **ambiguo** o **desconocido**, y con qué evidencia: `titulo` (trae temporada/episodio), `imdb` (tipo), `intra_titulo` (otras rutas nombran la serie), `declarado` (solo lo dice el vendedor). Para las series sin nombre se propone `serie_propuesta` (el título de la fila sin sufijos de temporada/episodio; si no, el nombre que traen las otras rutas; si no, el título canónico IMDb).

Qué es cada fila (% del total):

| Qué es · evidencia | consolidado | relleno |
|---|---:|---:|
| `ambiguo|imdb:short` | 40,933 (4.3%) · req 2.4% | 40,933 (4.3%) · req 2.4% |
| `ambiguo|imdb:tvMovie` | 17,589 (1.8%) · req 1.2% | 17,589 (1.8%) · req 1.2% |
| `ambiguo|imdb:tvSpecial` | 703 (0.1%) · req 0.0% | 703 (0.1%) · req 0.0% |
| `ambiguo|imdb:video` | 12,191 (1.3%) · req 0.8% | 12,191 (1.3%) · req 0.8% |
| `ambiguo|placeholder_vod` | 1,342 (0.1%) · req 0.1% | 1,342 (0.1%) · req 0.1% |
| `desconocido|-` | 410,439 (42.8%) · req 57.1% | 410,439 (42.8%) · req 57.1% |
| `pelicula|imdb` | 330,068 (34.4%) · req 21.4% | 330,068 (34.4%) · req 21.4% |
| `serie|declarado` | 21,398 (2.2%) · req 2.4% | 21,398 (2.2%) · req 2.4% |
| `serie|imdb` | 57,245 (6.0%) · req 8.0% | 57,245 (6.0%) · req 8.0% |
| `serie|intra_titulo` | 26,331 (2.7%) · req 3.5% | 26,331 (2.7%) · req 3.5% |
| `serie|titulo` | 41,203 (4.3%) · req 3.0% | 41,203 (4.3%) · req 3.0% |

Qué implica para la columna: `pelicula_vacio_correcto` (no hay nada que llenar), `ya_nombrada`, `serie_sin_nombre_recuperable` (es serie y hay nombre para proponer), `serie_sin_nombre` (es serie pero no hay nombre), `pelicula_con_serie_declarada` (contradicción), `nombrada_sin_evidencia`, `sin_evidencia`:

| Situación | consolidado | relleno |
|---|---:|---:|
| `ya_nombrada` | 50,113 (5.2%) · req 6.3% | 122,455 (12.8%) · req 15.3% |
| `serie_sin_nombre_recuperable` | 95,740 (10.0%) · req 10.5% | 23,131 (2.4%) · req 1.4% |
| `pelicula_vacio_correcto` | 329,140 (34.3%) · req 21.4% | 329,140 (34.3%) · req 21.4% |
| `pelicula_con_serie_declarada` | 928 (0.1%) · req 0.0% | 928 (0.1%) · req 0.0% |
| `contradicha` | 324 (0.0%) · req 0.0% | 591 (0.1%) · req 0.1% |
| `nombrada_sin_evidencia` | 307 (0.0%) · req 0.0% | 307 (0.0%) · req 0.0% |
| `sin_evidencia` | 482,890 (50.3%) · req 61.7% | 482,890 (50.3%) · req 61.7% |

**Temporada y episodio.** OpenRTB tiene `content.season` y `content.episode`, que el reporte no expone; pero el título sí los trae a veces ("animacars season 2", "transplant s4 ep 7"). Filas donde el título permite extraerlos (% del total):

| En el título | consolidado | relleno |
|---|---:|---:|
| `temporada+episodio` | 1,646 (0.2%) · req 0.2% | 1,646 (0.2%) · req 0.2% |
| `solo_temporada` | 33,040 (3.4%) · req 2.2% | 33,040 (3.4%) · req 2.2% |
| `solo_episodio` | 7,039 (0.7%) · req 0.5% | 7,039 (0.7%) · req 0.5% |
| `nada` | 917,717 (95.7%) · req 97.1% | 917,717 (95.7%) · req 97.1% |

### Por país — consolidado

|  | Filas | `ya_nombrada` | `serie_sin_nombre_recuperable` | `pelicula_vacio_correcto` | `sin_evidencia` |
|---|---:|---:|---:|---:|---:|
| Mexico | 304,329 | 4.9% | 11.4% | 29.2% | 54.4% |
| Colombia | 101,514 | 5.2% | 8.7% | 38.2% | 47.8% |
| Chile | 107,269 | 4.8% | 8.8% | 38.5% | 47.8% |

### Por publisher — consolidado

|  | Filas | `ya_nombrada` | `serie_sin_nombre_recuperable` | `pelicula_vacio_correcto` | `sin_evidencia` |
|---|---:|---:|---:|---:|---:|
| OTTera.tv | 200,221 | 0.3% | 10.3% | 39.2% | 50.2% |
| iion Pty Ltd | 183,090 | 0.1% | 10.4% | 40.1% | 49.4% |
| TCL ADS - Springserve | 120,000 | 0.3% | 10.0% | 40.2% | 49.4% |
| TCL ADs (APAC) | 112,769 | 0.3% | 10.0% | 42.2% | 47.5% |
| Select Plus PTE LTD (CTV) | 83,294 | 0.0% | 8.0% | 43.9% | 48.1% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 23,608 | 7.3% | 22.6% | 20.4% | 49.4% |
| PML Digital | 23,147 | 0.2% | 9.5% | 41.3% | 49.0% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 21,859 | 5.6% | 13.8% | 37.5% | 42.7% |
| AWG Media | 18,736 | 72.9% | 1.2% | 5.1% | 20.1% |
| Vidaa | 17,233 | 1.3% | 23.3% | 8.8% | 66.6% |
| Coocaa, a SKYWORTH company | 14,978 | 88.7% | 0.4% | 3.2% | 7.0% |
| Televisa Univision via SpringServe | 14,464 | 0.4% | 39.0% | 8.0% | 52.6% |

Series propuestas con más filas (consolidado; nombre [evidencia]; muestra aleatoria en `validacion-consolidado-muestra-series-propuestas.csv`):

| Serie propuesta | Filas | % filas | % requests |
|---|---:|---:|---:|
| `chicken stew [titulo]` | 3,644 | 0.4% | 0.3% |
| `forest frenzy of boonie bears [titulo]` | 2,034 | 0.2% | 0.2% |
| `something scary [titulo]` | 1,724 | 0.2% | 0.1% |
| `cain [imdb]` | 1,453 | 0.1% | 0.1% |
| `the baddest bad boy [imdb]` | 1,425 | 0.1% | 0.2% |
| `haus of horror [imdb]` | 1,410 | 0.1% | 0.2% |
| `breathe [imdb]` | 1,065 | 0.1% | 0.1% |
| `notorious [imdb]` | 907 | 0.1% | 0.0% |
| `northwest passage [imdb]` | 903 | 0.1% | 0.0% |
| `andor [titulo]` | 881 | 0.1% | 0.0% |
| `continuum [imdb]` | 863 | 0.1% | 0.0% |
| `duck camp dinners [titulo]` | 854 | 0.1% | 0.0% |
| `dread the unsolved [imdb]` | 810 | 0.1% | 0.2% |
| `real stories with christ [titulo]` | 805 | 0.1% | 0.1% |
| `chronic horror [imdb]` | 795 | 0.1% | 0.1% |
| `thrillbillies [imdb]` | 689 | 0.1% | 0.0% |
| `guilt [imdb]` | 653 | 0.1% | 0.0% |
| `bbc news [imdb]` | 611 | 0.1% | 0.0% |
| `the adventures of danny & the dingo [imdb]` | 570 | 0.1% | 0.0% |
| `naruto shippuden [titulo]` | 557 | 0.1% | 0.0% |
| `babybus canciones infantiles [titulo]` | 555 | 0.1% | 0.1% |
| `la rosa de guadalupe [imdb]` | 538 | 0.1% | 0.2% |
| `judas [imdb]` | 532 | 0.1% | 0.0% |
| `wanted [imdb]` | 531 | 0.1% | 0.0% |
| `melody [imdb]` | 526 | 0.1% | 0.0% |

### Por país — relleno

|  | Filas | `ya_nombrada` | `serie_sin_nombre_recuperable` | `pelicula_vacio_correcto` | `sin_evidencia` |
|---|---:|---:|---:|---:|---:|
| Mexico | 304,329 | 14.0% | 2.2% | 29.2% | 54.4% |
| Colombia | 101,514 | 11.7% | 2.2% | 38.2% | 47.8% |
| Chile | 107,269 | 11.1% | 2.6% | 38.5% | 47.8% |

### Por publisher — relleno

|  | Filas | `ya_nombrada` | `serie_sin_nombre_recuperable` | `pelicula_vacio_correcto` | `sin_evidencia` |
|---|---:|---:|---:|---:|---:|
| OTTera.tv | 200,221 | 7.1% | 3.4% | 39.2% | 50.2% |
| iion Pty Ltd | 183,090 | 7.4% | 3.1% | 40.1% | 49.4% |
| TCL ADS - Springserve | 120,000 | 7.2% | 3.1% | 40.2% | 49.4% |
| TCL ADs (APAC) | 112,769 | 7.4% | 2.9% | 42.2% | 47.5% |
| Select Plus PTE LTD (CTV) | 83,294 | 5.6% | 2.4% | 43.9% | 48.1% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 23,608 | 29.6% | 0.2% | 20.4% | 49.4% |
| PML Digital | 23,147 | 6.7% | 3.0% | 41.3% | 49.0% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 21,859 | 18.0% | 1.3% | 37.5% | 42.7% |
| AWG Media | 18,736 | 73.9% | 0.1% | 5.1% | 20.1% |
| Vidaa | 17,233 | 24.3% | 0.0% | 8.8% | 66.6% |
| Coocaa, a SKYWORTH company | 14,978 | 89.1% | 0.0% | 3.2% | 7.0% |
| Televisa Univision via SpringServe | 14,464 | 39.2% | 0.0% | 8.0% | 52.6% |

### Por origen del valor — relleno

|  | Filas | `ya_nombrada` | `serie_sin_nombre_recuperable` | `pelicula_vacio_correcto` | `sin_evidencia` |
|---|---:|---:|---:|---:|---:|
| imdb | 66,219 | 100.0% | 0.0% | 0.0% | 0.0% |
| intra_titulo | 6,390 | 95.8% | 0.0% | 0.0% | 0.0% |
| original | 62,808 | 79.8% | 1.4% | 6.3% | 10.1% |

Series propuestas con más filas (relleno; nombre [evidencia]; muestra aleatoria en `validacion-relleno-muestra-series-propuestas.csv`):

| Serie propuesta | Filas | % filas | % requests |
|---|---:|---:|---:|
| `forest frenzy of boonie bears [titulo]` | 2,034 | 0.2% | 0.2% |
| `andor [titulo]` | 881 | 0.1% | 0.0% |
| `real stories with christ [titulo]` | 805 | 0.1% | 0.1% |
| `babybus canciones infantiles [titulo]` | 555 | 0.1% | 0.1% |
| `animacars [titulo]` | 508 | 0.1% | 0.2% |
| `overwatch 2 - official [titulo]` | 421 | 0.0% | 0.0% |
| `the sandman [titulo]` | 421 | 0.0% | 0.0% |
| `shark academy nursery rhymes [titulo]` | 256 | 0.0% | 0.0% |
| `increditales [titulo]` | 244 | 0.0% | 0.0% |
| `spy penguin [titulo]` | 229 | 0.0% | 0.0% |
| `three rabbits [titulo]` | 221 | 0.0% | 0.0% |
| `american hidden story [titulo]` | 214 | 0.0% | 0.0% |
| `future chicken - music videos [titulo]` | 209 | 0.0% | 0.0% |
| `minituns - en [titulo]` | 206 | 0.0% | 0.0% |
| `rob the ranger [titulo]` | 205 | 0.0% | 0.0% |
| `super abby [titulo]` | 205 | 0.0% | 0.0% |
| `yoyo [titulo]` | 204 | 0.0% | 0.1% |
| `kong kong land [titulo]` | 201 | 0.0% | 0.0% |
| `htdt [titulo]` | 201 | 0.0% | 0.0% |
| `chai chai [titulo]` | 200 | 0.0% | 0.0% |
| `sindbad and the seven galaxies [titulo]` | 198 | 0.0% | 0.0% |
| `saari [titulo]` | 196 | 0.0% | 0.0% |
| `lucky fred [titulo]` | 195 | 0.0% | 0.1% |
| `purple devil [titulo]` | 195 | 0.0% | 0.0% |
| `the supers [titulo]` | 194 | 0.0% | 0.0% |

## 3. Límites

- La correctitud es deliberadamente básica: IMDb solo sabe si el título es serie o película, no cómo se llama la serie de un episodio con nombre propio; por eso `otro_nombre` es compatible y no error.
- Un match B que cae en una película homónima convierte una serie en `contradice`; el título con temporada/episodio manda sobre IMDb para evitarlo, pero no todos lo traen.
- `serie_propuesta` toma el título de la fila (en su idioma) antes que el canónico IMDb (a veces en inglés: *True Love* por *amores verdaderos*).
- Temporada/episodio salen de patrones en el título; "season two" en letras no se detecta.
