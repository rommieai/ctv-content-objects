# contentSeries: ¿la serie declarada es correcta y cuántas filas son serie sin decirlo?

**Fuentes:** `inventory-consolidado-v10-a-v18.csv` (1,071,840 filas, columna `contentSeries`); `inventory-consolidado-v10-a-v18-relleno.csv` (1,071,840 filas, columna `contentSeries_relleno`).  
**Generado con:** `scripts/validar_genero_series.py` + `scripts/generar_reporte_genero_series.py`. Corrida del 2026-09-15 09:46. Evidencia: el tipo que da IMDb (película, serie, miniserie), el título crudo ("season 2", "S01E03", "ep 4") y las demás rutas del mismo título (se exige que al menos 30 filas y 2 publishers nombren la serie, igual que en el relleno).

## Cómo leer este reporte

- **Fila**: cada fila del inventario es una combinación de país, publisher, app y metadata de contenido, no un programa. **Requests** son las solicitudes de anuncio de esa fila; cada cifra se da en filas y en requests.
- **Tal como llega (consolidado)** es el inventario tal como lo mandan los vendedores. **Después del relleno** es el mismo inventario después de que el pipeline de relleno completó los valores vacíos.
- **Evidencia**: el título de la fila se busca en IMDb y Wikidata. Cuando se encuentra (un **match**), esas bases dicen si es película o serie y qué géneros tiene. Cubre 531,080 filas (49.5% del total). Confianza del match: A = sin ambigüedad; B = podría ser un título homónimo (acierta ~3 de cada 4). Se usan matches de confianza B o mejor.
- **Formato de las celdas**: `12,345 filas (12.3%) · 4.5% req` = cantidad de filas, % de filas y % de requests sobre la base que indica cada tabla.
- **Nombre de serie real**: un `contentSeries` que no está vacío, ni es un centinela, ni el hash MD5 de cadena vacía, ni un relleno como `VOD` o `No Series`.

**Base de los porcentajes:** en la parte 1 (correctitud) sobre las **filas con nombre de serie real**; en la parte 2 (completitud) sobre el **total de filas**.

---

## 1. Correctitud (básica): ¿lo que dice ser serie lo es?

Solo se juzga lo que IMDb puede juzgar:

- **Coincide** (`coincide`): IMDb dice que es serie y el nombre declarado es el título canónico o el título de la fila.
- **Es serie, pero con otro nombre** (`otro_nombre`): IMDb dice que es serie, pero la serie declarada se llama distinto (un episodio con nombre propio, o un error). Se considera compatible.
- **IMDb dice que es película** (`contradice`): el título es una película según IMDb (confianza A o B) y no trae temporada ni episodio.
- **No se pudo evaluar** (`no_evaluable`): sin match, o el tipo es ambiguo (corto, video, película para TV).

| Dataset | Filas con nombre de serie real | Coincide | Es serie con otro nombre | IMDb dice que es película | No se pudo evaluar |
|---|---:|---:|---:|---:|---:|
| **Tal como llega (consolidado)** | 55,853 (5.2% del total; 5.6% req) | 1,403 filas (2.5%) · 2.3% req | 2,918 filas (5.2%) · 6.2% req | 1,363 filas (2.4%) · 1.1% req | 50,169 filas (89.8%) · 90.5% req |
| **Después del relleno** | 137,657 (12.8% del total; 15.0% req) | 78,516 filas (57.0%) · 60.7% req | 3,065 filas (2.2%) · 2.4% req | 1,674 filas (1.2%) · 0.8% req | 54,402 filas (39.5%) · 36.2% req |

Qué trae la columna (% del total de filas): nombres reales frente a rellenos:

| Contenido de contentSeries | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Relleno "no series" (no es una serie) (`placeholder:no series`) | 1,124 filas (0.1%) · 0.0% req | 1,124 filas (0.1%) · 0.0% req |
| Relleno "ott studios entertainment livestream" (no es una serie) (`placeholder:ott studios entertainment livestream`) | 487 filas (0.1%) · 0.0% req | 487 filas (0.1%) · 0.0% req |
| Relleno "ott studios entertainment on demand" (no es una serie) (`placeholder:ott studios entertainment on demand`) | 2,057 filas (0.2%) · 0.0% req | 2,057 filas (0.2%) · 0.0% req |
| Relleno "ott studios sports livestream" (no es una serie) (`placeholder:ott studios sports livestream`) | 1,041 filas (0.1%) · 0.1% req | 1,041 filas (0.1%) · 0.1% req |
| Relleno "research unit" (no es una serie) (`placeholder:research unit`) | 840 filas (0.1%) · 0.0% req | 840 filas (0.1%) · 0.0% req |
| Relleno "video chart" (no es una serie) (`placeholder:video chart`) | 341 filas (0.0%) · 0.0% req | 341 filas (0.0%) · 0.0% req |
| Relleno "vod" (no es una serie) (`placeholder:vod`) | 6,548 filas (0.6%) · 0.3% req | 6,548 filas (0.6%) · 0.3% req |
| Nombre de serie real (`serie_real`) | 55,853 filas (5.2%) · 5.6% req | 137,657 filas (12.8%) · 15.0% req |

Por grupo (% sobre las filas con nombre de serie real del grupo):

### Por publisher — Tal como llega (consolidado)

| Publisher | Filas | Coincide | Es serie, pero con otro nombre (compatible) | IMDb dice que es película | No se pudo evaluar |
|---|---:|---:|---:|---:|---:|
| OTTera.tv | 655 | 5.8% | 5.5% | 13.3% | 75.4% |
| iion Pty Ltd | 257 | 1.6% | 2.7% | 3.9% | 91.8% |
| TCL ADS - Springserve | 434 | 7.4% | 2.1% | 12.7% | 77.9% |
| TCL ADs (APAC) | 388 | 5.4% | 1.5% | 12.1% | 80.9% |
| PML Digital | 50 | 0.0% | 2.0% | 12.0% | 86.0% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 1,485 | 2.8% | 0.3% | 4.9% | 92.0% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 2,230 | 0.9% | 0.6% | 3.0% | 95.5% |
| AWG Media | 14,799 | 1.9% | 7.9% | 0.8% | 89.4% |
| Vidaa | 235 | 0.9% | 21.3% | 1.3% | 76.6% |
| Televisa Univision via SpringServe | 75 | 0.0% | 10.7% | 5.3% | 84.0% |
| Coocaa, a SKYWORTH company | 14,033 | 2.4% | 7.7% | 0.8% | 89.1% |

Series declaradas en títulos que IMDb dice que son película (Tal como llega (consolidado); lista completa en `validacion-consolidado-muestra-series-contradicciones.csv`):

| Título | Serie declarada | Película según IMDb | Confianza | Publisher (ejemplo) | Filas | Requests |
|---|---|---|---|---|---:|---:|
| `news` | `Euronews News` | tt1604683 News | B | Coocaa, a SKYWORTH company | 126 | 43,945,440 |
| `surfing favela` | `Action Documentaries` | tt0949774 Surfing favela | A | Coocaa, a SKYWORTH company | 112 | 39,742,160 |
| `adam jones` | `FMX Stars` | tt2503944 Burnt | A | Coocaa, a SKYWORTH company | 66 | 37,309,280 |
| `jajaja` | `JAJAJA` | tt1452626 Hahaha | A | TCL ADS - Springserve | 90 | 32,638,560 |
| `tour du faso` | `Tour du Faso` | tt3502760 Tour du Faso | A | OTTera.tv | 14 | 21,818,320 |
| `cuento de otoño` | `Cuento de Otoño` | tt0137439 Autumn Tale | A | Kivi via Springserve | 35 | 7,020,400 |
| `una rosa sobre el ring` | `Modern Marvels` | tt0323837 Una rosa sobre el ring | A | AWG Media | 8 | 3,710,000 |
| `santo en el museo de cera` | `Modern Marvels` | tt0057471 Santo in the Wax Museum | A | AWG Media | 4 | 2,487,920 |
| `origine inconnue` | `Origine Inconnue` | tt4575328 2036 Origin Unknown | A | TCL ADS - Springserve | 32 | 2,163,600 |
| `carrera contra el tiempo` | `POUND OF FLESH (ESP)` | tt3488328 Pound of Flesh | B | FUNKE Digital GmbH | Publica | 20 | 1,641,040 |
| `providence` | `Citas de Estados Unidos` | tt6060392 Providence Island | B | LG Ads EMEA - SS | 14 | 1,508,240 |
| `charlotte` | `Citas de Estados Unidos` | tt5806814 Charlotte | B | LG Ads EMEA - SS | 16 | 1,399,360 |
| `72 horas` | `La Cacería` | tt1458175 The Next Three Days | B | FreeTV via Springserve | 11 | 1,340,160 |
| `piloto` | `Hell on Wheels` | tt31593809 Biker | B | FreeTV via Springserve | 19 | 1,330,080 |
| `the reunion` | `Pastewka` | tt1792543 The Reunion | B | METAX SOFTWARE PTE. LTD. (Ex | 12 | 1,127,680 |

### Por publisher — Después del relleno

| Publisher | Filas | Coincide | Es serie, pero con otro nombre (compatible) | IMDb dice que es película | No se pudo evaluar |
|---|---:|---:|---:|---:|---:|
| OTTera.tv | 15,923 | 91.5% | 0.4% | 0.6% | 7.6% |
| iion Pty Ltd | 15,792 | 87.1% | 0.4% | 0.5% | 12.0% |
| TCL ADS - Springserve | 9,838 | 90.9% | 0.3% | 0.7% | 8.2% |
| TCL ADs (APAC) | 9,424 | 91.0% | 0.4% | 0.6% | 8.0% |
| Select Plus PTE LTD (CTV) | 5,445 | 94.8% | 0.0% | 0.0% | 5.2% |
| PML Digital | 1,798 | 89.8% | 0.3% | 0.9% | 9.0% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 4,559 | 66.1% | 0.2% | 2.0% | 31.7% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 7,943 | 71.2% | 0.2% | 1.2% | 27.4% |
| AWG Media | 15,029 | 3.1% | 7.8% | 0.9% | 88.2% |
| Vidaa | 4,701 | 92.4% | 1.1% | 1.3% | 5.2% |
| Televisa Univision via SpringServe | 6,243 | 98.2% | 0.1% | 0.5% | 1.2% |
| Coocaa, a SKYWORTH company | 14,088 | 2.8% | 7.7% | 0.8% | 88.7% |

En el dataset rellenado, el origen IMDb se juzga contra la misma fuente que lo generó: su acierto solo prueba consistencia.

### Por origen del valor — Después del relleno

| Origen del valor | Filas | Coincide | Es serie, pero con otro nombre (compatible) | IMDb dice que es película | No se pudo evaluar |
|---|---:|---:|---:|---:|---:|
| IMDb (`imdb`) | 74,656 | 100.0% | 0.0% | 0.0% | 0.0% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 7,148 | 34.4% | 2.1% | 4.4% | 59.2% |
| Venía del vendedor (`original`) | 55,853 | 2.5% | 5.2% | 2.4% | 89.8% |

Series declaradas en títulos que IMDb dice que son película (Después del relleno; lista completa en `validacion-relleno-muestra-series-contradicciones.csv`):

| Título | Serie declarada | Película según IMDb | Confianza | Publisher (ejemplo) | Filas | Requests |
|---|---|---|---|---|---:|---:|
| `jajaja` | `JAJAJA` | tt1452626 Hahaha | A | Vidaa | 369 | 281,263,440 |
| `news` | `Euronews News` | tt1604683 News | B | Coocaa, a SKYWORTH company | 127 | 44,002,240 |
| `surfing favela` | `Action Documentaries` | tt0949774 Surfing favela | A | Coocaa, a SKYWORTH company | 112 | 39,742,160 |
| `adam jones` | `FMX Stars` | tt2503944 Burnt | A | Coocaa, a SKYWORTH company | 66 | 37,309,280 |
| `tour du faso` | `Tour du Faso` | tt3502760 Tour du Faso | A | OTTera.tv | 14 | 21,818,320 |
| `cuento de otoño` | `Cuento de Otoño` | tt0137439 Autumn Tale | A | Kivi via Springserve | 35 | 7,020,400 |
| `origine inconnue` | `Origine Inconnue` | tt4575328 2036 Origin Unknown | A | TCL ADS - Springserve | 63 | 5,846,000 |
| `una rosa sobre el ring` | `Modern Marvels` | tt0323837 Una rosa sobre el ring | A | AWG Media | 8 | 3,710,000 |
| `santo en el museo de cera` | `Modern Marvels` | tt0057471 Santo in the Wax Museum | A | AWG Media | 4 | 2,487,920 |
| `carrera contra el tiempo` | `POUND OF FLESH (ESP)` | tt3488328 Pound of Flesh | B | FUNKE Digital GmbH | Publica | 20 | 1,641,040 |
| `providence` | `Citas de Estados Unidos` | tt6060392 Providence Island | B | LG Ads EMEA - SS | 14 | 1,508,240 |
| `charlotte` | `Citas de Estados Unidos` | tt5806814 Charlotte | B | LG Ads EMEA - SS | 16 | 1,399,360 |
| `72 horas` | `La Cacería` | tt1458175 The Next Three Days | B | FreeTV via Springserve | 11 | 1,340,160 |
| `piloto` | `Hell on Wheels` | tt31593809 Biker | B | FreeTV via Springserve | 19 | 1,330,080 |
| `the reunion` | `Pastewka` | tt1792543 The Reunion | B | METAX SOFTWARE PTE. LTD. (Ex | 12 | 1,127,680 |

## 2. Completitud: qué es cada fila y qué se le puede poner

Para todas las filas se decide si el contenido es **serie**, **película**, **ambiguo** o **desconocido**, y con qué evidencia: el título trae temporada/episodio, el tipo de IMDb, otras rutas del mismo título nombran la serie, o solo lo dice el vendedor. Para las series sin nombre se propone uno: el título de la fila sin los sufijos de temporada/episodio; si no, el nombre que traen las otras rutas; si no, el título canónico de IMDb.

Qué es cada fila (% del total):

| Qué es · con qué evidencia | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Ambiguo · corto según IMDb (`ambiguo|imdb:short`) | 46,135 filas (4.3%) · 2.5% req | 46,135 filas (4.3%) · 2.5% req |
| Ambiguo · película para TV según IMDb (`ambiguo|imdb:tvMovie`) | 19,913 filas (1.9%) · 1.2% req | 19,913 filas (1.9%) · 1.2% req |
| Ambiguo · especial de TV según IMDb (`ambiguo|imdb:tvSpecial`) | 794 filas (0.1%) · 0.0% req | 794 filas (0.1%) · 0.0% req |
| Ambiguo · video según IMDb (`ambiguo|imdb:video`) | 13,382 filas (1.2%) · 0.8% req | 13,382 filas (1.2%) · 0.8% req |
| Ambiguo · trae el relleno "VOD" (`ambiguo|placeholder_vod`) | 1,544 filas (0.1%) · 0.1% req | 1,544 filas (0.1%) · 0.1% req |
| Desconocido · sin evidencia (`desconocido|-`) | 460,712 filas (43.0%) · 56.5% req | 460,712 filas (43.0%) · 56.5% req |
| Película · según IMDb (`pelicula|imdb`) | 366,097 filas (34.2%) · 22.4% req | 366,097 filas (34.2%) · 22.4% req |
| Serie · solo lo dice el vendedor (`serie|declarado`) | 23,427 filas (2.2%) · 2.2% req | 23,427 filas (2.2%) · 2.2% req |
| Serie · según IMDb (`serie|imdb`) | 64,075 filas (6.0%) · 8.1% req | 64,075 filas (6.0%) · 8.1% req |
| Serie · otras rutas nombran la serie (`serie|intra_titulo`) | 28,301 filas (2.6%) · 3.1% req | 28,301 filas (2.6%) · 3.1% req |
| Serie · el título trae temporada/episodio (`serie|titulo`) | 47,460 filas (4.4%) · 3.1% req | 47,460 filas (4.4%) · 3.1% req |

Qué implica eso para la columna contentSeries (% del total):

| Situación de la fila | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Serie con nombre (`ya_nombrada`) | 54,168 filas (5.0%) · 5.6% req | 135,661 filas (12.7%) · 14.9% req |
| Serie sin nombre, con nombre proponible (`serie_sin_nombre_recuperable`) | 108,746 filas (10.2%) · 10.8% req | 26,942 filas (2.5%) · 1.5% req |
| Película: el vacío es correcto (`pelicula_vacio_correcto`) | 365,083 filas (34.1%) · 22.3% req | 365,083 filas (34.1%) · 22.3% req |
| Película con serie declarada (contradicción) (`pelicula_con_serie_declarada`) | 1,014 filas (0.1%) · 0.0% req | 1,014 filas (0.1%) · 0.0% req |
| Contradicha (`contradicha`) | 349 filas (0.0%) · 0.0% req | 660 filas (0.1%) · 0.1% req |
| Con nombre, sin evidencia para juzgar (`nombrada_sin_evidencia`) | 322 filas (0.0%) · 0.0% req | 322 filas (0.0%) · 0.0% req |
| Sin evidencia (`sin_evidencia`) | 542,158 filas (50.6%) · 61.2% req | 542,158 filas (50.6%) · 61.2% req |

**Temporada y episodio.** OpenRTB tiene los campos `content.season` y `content.episode`, que el reporte de inventario no expone; pero a veces el título los trae ("animacars season 2", "transplant s4 ep 7"). Filas donde se pueden extraer del título (% del total):

| Qué trae el título | Tal como llega (consolidado) | Después del relleno |
|---|---:|---:|
| Temporada y episodio (`temporada+episodio`) | 1,765 filas (0.2%) · 0.2% req | 1,765 filas (0.2%) · 0.2% req |
| Solo temporada (`solo_temporada`) | 38,434 filas (3.6%) · 2.3% req | 38,434 filas (3.6%) · 2.3% req |
| Solo episodio (`solo_episodio`) | 8,050 filas (0.8%) · 0.5% req | 8,050 filas (0.8%) · 0.5% req |
| Nada (`nada`) | 1,023,591 filas (95.5%) · 97.0% req | 1,023,591 filas (95.5%) · 97.0% req |

Por grupo (% sobre las filas del grupo):

### Por país — Tal como llega (consolidado)

| País | Filas | Serie con nombre | Serie sin nombre, con nombre proponible | Película: el vacío es correcto | Sin evidencia |
|---|---:|---:|---:|---:|---:|
| Mexico | 328,845 | 5.0% | 11.6% | 28.8% | 54.5% |
| Colombia | 114,223 | 4.8% | 9.0% | 37.7% | 48.4% |
| Chile | 122,923 | 4.4% | 9.3% | 37.5% | 48.8% |

### Por publisher — Tal como llega (consolidado)

| Publisher | Filas | Serie con nombre | Serie sin nombre, con nombre proponible | Película: el vacío es correcto | Sin evidencia |
|---|---:|---:|---:|---:|---:|
| OTTera.tv | 220,835 | 0.3% | 10.4% | 38.9% | 50.4% |
| iion Pty Ltd | 207,466 | 0.1% | 10.8% | 39.1% | 50.0% |
| TCL ADS - Springserve | 133,483 | 0.3% | 10.2% | 39.8% | 49.6% |
| TCL ADs (APAC) | 126,143 | 0.3% | 10.1% | 41.9% | 47.7% |
| Select Plus PTE LTD (CTV) | 96,962 | 0.0% | 8.1% | 43.3% | 48.6% |
| PML Digital | 26,250 | 0.2% | 10.1% | 40.3% | 49.4% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 25,773 | 5.4% | 13.1% | 38.3% | 42.8% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 25,730 | 8.4% | 22.4% | 20.1% | 48.8% |
| AWG Media | 20,424 | 71.9% | 1.2% | 5.3% | 21.1% |
| Vidaa | 19,325 | 1.2% | 23.1% | 9.0% | 66.7% |
| Televisa Univision via SpringServe | 15,690 | 0.4% | 39.3% | 8.0% | 52.2% |
| Coocaa, a SKYWORTH company | 15,655 | 88.9% | 0.4% | 3.1% | 6.9% |

Series propuestas con más filas en Tal como llega (consolidado) (nombre propuesto y, entre corchetes, de dónde salió; muestra aleatoria en `validacion-consolidado-muestra-series-propuestas.csv`):

| Serie propuesta [evidencia] | Filas | % de filas | % de requests |
|---|---:|---:|---:|
| `chicken stew [titulo]` | 4,322 | 0.4% | 0.4% |
| `forest frenzy of boonie bears [titulo]` | 2,410 | 0.2% | 0.2% |
| `something scary [titulo]` | 1,901 | 0.2% | 0.1% |
| `cain [imdb]` | 1,587 | 0.1% | 0.1% |
| `the baddest bad boy [imdb]` | 1,518 | 0.1% | 0.2% |
| `haus of horror [imdb]` | 1,505 | 0.1% | 0.2% |
| `breathe [imdb]` | 1,215 | 0.1% | 0.1% |
| `notorious [imdb]` | 999 | 0.1% | 0.1% |
| `northwest passage [imdb]` | 988 | 0.1% | 0.0% |
| `andor [titulo]` | 979 | 0.1% | 0.0% |
| `continuum [imdb]` | 953 | 0.1% | 0.0% |
| `duck camp dinners [titulo]` | 943 | 0.1% | 0.0% |
| `dread the unsolved [imdb]` | 866 | 0.1% | 0.1% |
| `real stories with christ [titulo]` | 859 | 0.1% | 0.1% |
| `chronic horror [imdb]` | 849 | 0.1% | 0.1% |
| `thrillbillies [imdb]` | 771 | 0.1% | 0.0% |
| `guilt [imdb]` | 736 | 0.1% | 0.0% |
| `bbc news [imdb]` | 686 | 0.1% | 0.0% |
| `naruto shippuden [titulo]` | 671 | 0.1% | 0.0% |
| `babybus canciones infantiles [titulo]` | 641 | 0.1% | 0.2% |
| `caronte [imdb]` | 620 | 0.1% | 0.0% |
| `the adventures of danny & the dingo [imdb]` | 613 | 0.1% | 0.0% |
| `judas [imdb]` | 592 | 0.1% | 0.0% |
| `animacars [titulo]` | 584 | 0.1% | 0.1% |
| `wanted [imdb]` | 580 | 0.1% | 0.0% |

### Por país — Después del relleno

| País | Filas | Serie con nombre | Serie sin nombre, con nombre proponible | Película: el vacío es correcto | Sin evidencia |
|---|---:|---:|---:|---:|---:|
| Mexico | 328,845 | 14.2% | 2.3% | 28.8% | 54.5% |
| Colombia | 114,223 | 11.4% | 2.4% | 37.7% | 48.4% |
| Chile | 122,923 | 10.7% | 2.9% | 37.5% | 48.8% |

### Por publisher — Después del relleno

| Publisher | Filas | Serie con nombre | Serie sin nombre, con nombre proponible | Película: el vacío es correcto | Sin evidencia |
|---|---:|---:|---:|---:|---:|
| OTTera.tv | 220,835 | 7.2% | 3.5% | 38.9% | 50.4% |
| iion Pty Ltd | 207,466 | 7.6% | 3.3% | 39.1% | 50.0% |
| TCL ADS - Springserve | 133,483 | 7.3% | 3.2% | 39.8% | 49.6% |
| TCL ADs (APAC) | 126,143 | 7.4% | 3.0% | 41.9% | 47.7% |
| Select Plus PTE LTD (CTV) | 96,962 | 5.6% | 2.5% | 43.3% | 48.6% |
| PML Digital | 26,250 | 6.8% | 3.5% | 40.3% | 49.4% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 25,773 | 17.3% | 1.2% | 38.3% | 42.8% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 25,730 | 30.4% | 0.2% | 20.1% | 48.8% |
| AWG Media | 20,424 | 72.9% | 0.1% | 5.3% | 21.1% |
| Vidaa | 19,325 | 24.0% | 0.0% | 9.0% | 66.7% |
| Televisa Univision via SpringServe | 15,690 | 39.6% | 0.0% | 8.0% | 52.2% |
| Coocaa, a SKYWORTH company | 15,655 | 89.3% | 0.0% | 3.1% | 6.9% |

### Por origen del valor — Después del relleno

| Origen del valor | Filas | Serie con nombre | Serie sin nombre, con nombre proponible | Película: el vacío es correcto | Sin evidencia |
|---|---:|---:|---:|---:|---:|
| IMDb (`imdb`) | 74,656 | 100.0% | 0.0% | 0.0% | 0.0% |
| Copiado de otra ruta del mismo título (`intra_titulo`) | 7,148 | 95.6% | 0.0% | 0.0% | 0.0% |
| Venía del vendedor (`original`) | 68,291 | 79.3% | 1.4% | 6.5% | 10.3% |

Series propuestas con más filas en Después del relleno (nombre propuesto y, entre corchetes, de dónde salió; muestra aleatoria en `validacion-relleno-muestra-series-propuestas.csv`):

| Serie propuesta [evidencia] | Filas | % de filas | % de requests |
|---|---:|---:|---:|
| `forest frenzy of boonie bears [titulo]` | 2,410 | 0.2% | 0.2% |
| `andor [titulo]` | 979 | 0.1% | 0.0% |
| `real stories with christ [titulo]` | 859 | 0.1% | 0.1% |
| `babybus canciones infantiles [titulo]` | 641 | 0.1% | 0.2% |
| `animacars [titulo]` | 584 | 0.1% | 0.1% |
| `the sandman [titulo]` | 467 | 0.0% | 0.0% |
| `overwatch 2 - official [titulo]` | 466 | 0.0% | 0.0% |
| `shark academy nursery rhymes [titulo]` | 290 | 0.0% | 0.0% |
| `increditales [titulo]` | 280 | 0.0% | 0.0% |
| `spy penguin [titulo]` | 260 | 0.0% | 0.0% |
| `american hidden story [titulo]` | 257 | 0.0% | 0.1% |
| `three rabbits [titulo]` | 256 | 0.0% | 0.0% |
| `minituns - en [titulo]` | 243 | 0.0% | 0.0% |
| `chai chai [titulo]` | 242 | 0.0% | 0.0% |
| `future chicken - music videos [titulo]` | 241 | 0.0% | 0.0% |
| `kong kong land [titulo]` | 238 | 0.0% | 0.0% |
| `super abby [titulo]` | 238 | 0.0% | 0.0% |
| `vitaminix [titulo]` | 236 | 0.0% | 0.0% |
| `htdt [titulo]` | 236 | 0.0% | 0.0% |
| `sindbad and the seven galaxies [titulo]` | 235 | 0.0% | 0.0% |
| `yoyo [titulo]` | 234 | 0.0% | 0.1% |
| `eggroy [titulo]` | 233 | 0.0% | 0.0% |
| `rob the ranger [titulo]` | 232 | 0.0% | 0.0% |
| `gunnie season [titulo]` | 232 | 0.0% | 0.0% |
| `watchcar [titulo]` | 231 | 0.0% | 0.0% |

## 3. Límites

- La correctitud es deliberadamente básica: IMDb solo sabe si el título es serie o película, no cómo se llama la serie de un episodio con nombre propio; por eso "es serie con otro nombre" cuenta como compatible y no como error.
- Un match B que cae en una película homónima convierte una serie en "IMDb dice que es película"; para evitarlo, el título con temporada/episodio manda sobre IMDb, pero no todos lo traen.
- El nombre propuesto toma el título de la fila (en su idioma) antes que el canónico de IMDb (a veces en inglés: *True Love* por *amores verdaderos*).
- Temporada y episodio salen de patrones en el título; "season two" en letras no se detecta.
