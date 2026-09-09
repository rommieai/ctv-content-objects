# Reporte — contentGenre: correctitud de lo declarado y géneros adicionales alcanzables

**Fuentes:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas, columna `contentGenre`); `inventory-consolidado-v10-a-v17-relleno.csv` (959,442 filas, columna `contentGenre_relleno`).  
**Generado con:** `scripts/validar_genero_series.py` + `scripts/generar_reporte_genero_series.py`. Corrida del 2026-09-09 16:03. Evidencia: géneros IMDb (match de confianza ≥ B) y géneros Wikidata (P136) de `cache-enriquecimiento/titulos.json` (14,686 títulos); cubre 476,869 filas (49.7%).

**Convención:** en la parte de correctitud los % son **% de las filas con género declarado**; en la de completitud, **% del total de filas**. Los géneros declarados se normalizan con el diccionario del proyecto y se colapsan a conceptos comparables con IMDb (thriller/misterio/crimen → crimen-misterio; acción/aventura/bélico → acción-aventura; anime → animación). Lo que IMDb no puede expresar (lifestyle, viajes, cocina, religión, educación, videojuegos, "entertainment", "other", "movies", "tv") no se juzga.

---

## 1. Correctitud

Por cada género comparable declarado: **acierta** si está entre los de IMDb/Wikidata del título; **afín** si no está pero es vecino (telenovela ~ drama/romance, thriller ~ terror, infantil ~ animación, documental ~ reality); **choca** si ni lo uno ni lo otro. Veredicto de la fila: `coincide` (todo acierta), `afin` (nada choca, nada acierta), `parcial` (aciertos y choques), `contradice` (choca y nada acierta), `no_evaluable` (sin match, o sin género comparable).

| Dataset | Con género | Evaluables | coincide | afin | parcial | contradice | Filas que contradicen |
|---|---:|---:|---:|---:|---:|---:|---:|
| **consolidado** | 898,453 (93.6% del total) | 438,511 (48.8%) | 84.8% · req 84.5% | 4.6% · req 6.0% | 7.9% · req 6.4% | 2.7% · req 3.1% | 11,833 |
| **relleno** | 940,125 (98.0% del total) | 456,409 (48.5%) | 85.3% · req 84.4% | 4.4% · req 5.7% | 7.6% · req 6.9% | 2.6% · req 3.0% | 11,833 |

Los % de coincide/afín/parcial/contradice son sobre las evaluables.

### 1.1 Formato de lo declarado

`mapeado` = al menos un token del valor está en el diccionario de géneros; `no_mapeado:*` = ninguno, clasificado por lo que es (tipo de contenido como "movies"/"live", idioma o región, tema que no es género, formato sucio).

| Formato | consolidado | relleno |
|---|---:|---:|
| `mapeado` | 833,061 (92.7%) · req 92.5% | 870,764 (92.6%) · req 92.3% |
| `no_mapeado:genero_en_formato_sucio` | 22,949 (2.5%) · req 2.5% | 23,004 (2.5%) · req 2.4% |
| `no_mapeado:idioma_o_region` | 2,271 (0.2%) · req 0.1% | 2,474 (0.3%) · req 0.1% |
| `no_mapeado:otros_no_reconocidos` | 19,215 (2.1%) · req 1.9% | 21,499 (2.3%) · req 2.1% |
| `no_mapeado:prefijo_tecnico` | 8,685 (1.0%) · req 2.1% | 8,685 (0.9%) · req 2.0% |
| `no_mapeado:tema_no_genero` | 3,718 (0.4%) · req 0.6% | 3,951 (0.4%) · req 0.6% |
| `no_mapeado:tipo_de_contenido` | 8,554 (0.9%) · req 0.4% | 9,748 (1.0%) · req 0.5% |

Cuántos géneros comparables declara cada fila (0 = solo genéricos como "entertainment"):

| Géneros comparables declarados | consolidado | relleno |
|---|---:|---:|
| `0` | 151,457 (16.9%) · req 20.1% | 173,151 (18.4%) · req 21.0% |
| `1` | 522,978 (58.2%) · req 63.0% | 530,216 (56.4%) · req 61.6% |
| `2` | 136,030 (15.1%) · req 9.8% | 143,656 (15.3%) · req 10.0% |
| `3` | 87,988 (9.8%) · req 7.0% | 93,102 (9.9%) · req 7.4% |

### 1.2 Qué género choca y con qué

**consolidado** — género declarado que choca (filas en veredicto parcial o contradice):

| Género declarado | Filas | Requests |
|---|---:|---:|
| `drama` | 14,576 | 4,390,787,840 |
| `accion-aventura` | 11,889 | 3,002,370,240 |
| `documental` | 4,483 | 1,611,345,440 |
| `comedia` | 3,875 | 544,248,880 |
| `infantil-familia` | 3,800 | 654,064,480 |
| `terror` | 3,111 | 503,002,560 |
| `fantasia` | 2,664 | 415,458,000 |
| `musica` | 2,569 | 954,118,000 |
| `crimen-misterio` | 2,286 | 631,225,360 |
| `deportes` | 2,092 | 899,132,560 |
| `romance` | 931 | 131,691,040 |
| `animacion` | 733 | 113,198,000 |

Confusiones más frecuentes (consolidado: declarado → lo que dice IMDb/Wikidata):

| Declarado → esperado | Filas | Requests |
|---|---:|---:|
| `drama -> comedia` | 5,078 | 1,707,694,880 |
| `accion-aventura -> drama` | 3,457 | 560,710,240 |
| `drama -> terror` | 2,984 | 1,572,919,600 |
| `drama -> infantil-familia` | 2,387 | 473,765,200 |
| `terror -> drama` | 2,067 | 341,695,360 |
| `accion-aventura -> documental` | 1,671 | 417,934,480 |
| `accion-aventura -> terror` | 1,599 | 256,857,520 |
| `infantil-familia -> drama` | 1,467 | 269,183,280 |
| `comedia -> drama` | 1,443 | 209,017,680 |
| `accion-aventura -> reality` | 1,320 | 242,829,280 |
| `accion-aventura -> comedia` | 1,061 | 302,782,800 |
| `drama -> sci-fi` | 1,041 | 162,970,640 |
| `documental -> comedia,drama` | 875 | 214,617,360 |
| `accion-aventura -> deportes,documental` | 840 | 209,172,160 |
| `crimen-misterio -> sci-fi` | 771 | 320,114,160 |

**relleno** — género declarado que choca (filas en veredicto parcial o contradice):

| Género declarado | Filas | Requests |
|---|---:|---:|
| `drama` | 14,591 | 4,392,233,840 |
| `accion-aventura` | 11,992 | 4,010,100,240 |
| `documental` | 4,519 | 2,588,710,160 |
| `comedia` | 3,884 | 545,058,560 |
| `infantil-familia` | 3,804 | 654,240,800 |
| `terror` | 3,112 | 503,054,880 |
| `fantasia` | 2,664 | 415,458,000 |
| `musica` | 2,569 | 954,118,000 |
| `crimen-misterio` | 2,287 | 631,285,360 |
| `deportes` | 2,102 | 900,008,000 |
| `romance` | 957 | 135,109,840 |
| `sci-fi` | 736 | 395,844,560 |

Confusiones más frecuentes (relleno: declarado → lo que dice IMDb/Wikidata):

| Declarado → esperado | Filas | Requests |
|---|---:|---:|
| `drama -> comedia` | 5,078 | 1,707,694,880 |
| `accion-aventura -> drama` | 3,460 | 560,900,240 |
| `drama -> terror` | 2,984 | 1,572,919,600 |
| `drama -> infantil-familia` | 2,387 | 473,765,200 |
| `terror -> drama` | 2,067 | 341,695,360 |
| `accion-aventura -> documental` | 1,672 | 417,975,760 |
| `accion-aventura -> terror` | 1,599 | 256,857,520 |
| `infantil-familia -> drama` | 1,467 | 269,183,280 |
| `comedia -> drama` | 1,444 | 209,107,120 |
| `accion-aventura -> reality` | 1,320 | 242,829,280 |
| `accion-aventura -> comedia` | 1,061 | 302,782,800 |
| `drama -> sci-fi` | 1,041 | 162,970,640 |
| `documental -> comedia,drama` | 875 | 214,617,360 |
| `accion-aventura -> deportes,documental` | 840 | 209,172,160 |
| `crimen-misterio -> sci-fi` | 771 | 320,114,160 |

### 1.3 Quién acierta y quién no

### Por país — consolidado

|  | Filas | `coincide` | `afin` | `parcial` | `contradice` | `no_evaluable` |
|---|---:|---:|---:|---:|---:|---:|
| Mexico | 280,281 | 37.1% | 1.8% | 2.6% | 1.1% | 57.4% |
| Colombia | 94,434 | 44.5% | 3.1% | 4.3% | 1.9% | 46.2% |
| Chile | 101,462 | 44.4% | 2.6% | 4.3% | 1.5% | 47.2% |

### Por publisher — consolidado

|  | Filas | `coincide` | `afin` | `parcial` | `contradice` | `no_evaluable` |
|---|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 189,926 | 45.0% | 1.8% | 5.6% | 1.0% | 46.7% |
| iion Pty Ltd | 164,841 | 47.0% | 2.9% | 4.5% | 1.7% | 43.8% |
| TCL ADS - Springserve | 111,800 | 46.5% | 2.3% | 5.2% | 1.2% | 44.8% |
| TCL ADs (APAC) | 106,872 | 47.9% | 2.4% | 5.7% | 1.2% | 42.7% |
| Select Plus PTE LTD (CTV) | 78,987 | 48.9% | 6.3% | 0.0% | 3.9% | 40.9% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 23,080 | 42.0% | 0.8% | 2.0% | 0.5% | 54.6% |
| PML Digital | 22,214 | 47.5% | 2.0% | 5.9% | 1.0% | 43.6% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 21,127 | 49.7% | 2.1% | 4.6% | 0.9% | 42.7% |
| AWG Media | 17,718 | 10.9% | 0.3% | 0.5% | 0.9% | 87.4% |
| Vidaa | 16,935 | 28.8% | 0.1% | 0.0% | 0.3% | 70.8% |
| Coocaa, a SKYWORTH company | 14,028 | 9.7% | 0.3% | 0.2% | 1.0% | 88.9% |
| Televisa Univision via SpringServe | 13,954 | 49.3% | 0.1% | 0.0% | 0.8% | 49.8% |

### Por país — relleno

|  | Filas | `coincide` | `afin` | `parcial` | `contradice` | `no_evaluable` |
|---|---:|---:|---:|---:|---:|---:|
| Mexico | 296,152 | 37.8% | 1.7% | 2.5% | 1.0% | 57.0% |
| Colombia | 99,619 | 43.6% | 2.9% | 4.1% | 1.8% | 47.6% |
| Chile | 105,883 | 44.1% | 2.5% | 4.1% | 1.4% | 47.9% |

### Por publisher — relleno

|  | Filas | `coincide` | `afin` | `parcial` | `contradice` | `no_evaluable` |
|---|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 197,788 | 45.1% | 1.7% | 5.4% | 0.9% | 46.8% |
| iion Pty Ltd | 179,156 | 46.4% | 2.7% | 4.2% | 1.6% | 45.1% |
| TCL ADS - Springserve | 118,059 | 46.6% | 2.1% | 4.9% | 1.2% | 45.2% |
| TCL ADs (APAC) | 111,588 | 47.9% | 2.3% | 5.5% | 1.2% | 43.1% |
| Select Plus PTE LTD (CTV) | 82,691 | 47.8% | 6.0% | 0.0% | 3.7% | 42.5% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 23,159 | 42.0% | 0.8% | 2.0% | 0.5% | 54.6% |
| PML Digital | 22,928 | 47.0% | 1.9% | 5.8% | 1.0% | 44.3% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 21,492 | 49.7% | 2.0% | 4.5% | 0.9% | 42.8% |
| AWG Media | 18,600 | 11.4% | 0.3% | 0.5% | 0.8% | 87.0% |
| Vidaa | 17,035 | 28.9% | 0.1% | 0.0% | 0.3% | 70.7% |
| Coocaa, a SKYWORTH company | 14,867 | 10.3% | 0.3% | 0.1% | 0.9% | 88.4% |
| Televisa Univision via SpringServe | 13,969 | 49.4% | 0.1% | 0.0% | 0.8% | 49.8% |

En el relleno, `original` es lo que venía; `imdb` se validaría contra sí mismo (circular) y por eso su `coincide` no prueba nada.

### Por origen del valor — relleno

|  | Filas | `coincide` | `afin` | `parcial` | `contradice` | `no_evaluable` |
|---|---:|---:|---:|---:|---:|---:|
| app_default | 1,644 | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% |
| imdb | 17,028 | 98.5% | 0.0% | 0.0% | 0.0% | 1.5% |
| intra_titulo | 23,000 | 4.2% | 0.1% | 0.7% | 0.0% | 95.1% |
| original | 898,453 | 41.4% | 2.2% | 3.9% | 1.3% | 51.2% |

### 1.4 Las contradicciones con más tráfico

**consolidado** (un título por fila; muestra completa en `validacion-consolidado-muestra-genero-contradicciones.csv`):

| Título | Declarado | IMDb | Wikidata extra | Match | Conf. | Publisher (ej.) | Filas | Requests |
|---|---|---|---|---|---|---|---:|---:|
| `penance lane` | `Drama` | Horror |  | tt1964995 Penance Lane | A | OTTera.tv | 1,108 | 802,499,680 |
| `rollers: trailer` | `Drama` | Comedy |  | tt9124868 Rollers | B | OTTera.tv | 601 | 410,249,840 |
| `formentera` | `Documentary` | Drama |  | tt1990232 Formentera | A | TCL ADS - Springserve | 58 | 252,371,680 |
| `tennis+` | `sports` | Comedy,Drama,Sci-Fi |  | tt2281489 Tennis | B | OTTera.tv | 69 | 215,773,280 |
| `lost in the maze` | `Adventure` | Documentary |  | tt29602142 Lost in the Maze | A | OTTera.tv | 423 | 152,450,560 |
| `the buddy cop` | `Action` | Comedy |  | tt20412912 The Buddy Cop | A | OTTera.tv | 421 | 151,549,120 |
| `machotaildrop` | `Sports` | Action,Comedy,Fantasy |  | tt1315388 Machotaildrop | A | TCL ADS - Springserve | 173 | 149,687,440 |
| `the secret handshake` | `Drama` | Family |  | tt3519936 The Secret Handshake | B | TCL ADS - Springserve | 209 | 95,906,320 |
| `we three kings` | `Drama` | Family |  | tt13091334 We Three Kings | B | OTTera.tv | 339 | 86,420,240 |
| `13 score: trailer` | `Action` | Horror |  | tt3168890 13 Score | A | OTTera.tv | 411 | 79,454,160 |
| `duck camp dinners season 2` | `Adventure` | Reality-TV |  | tt35146256 Duck Camp Dinners | A | OTTera.tv | 398 | 75,600,640 |
| `sin's kitchen: trailer` | `adventure,mystery` | Drama |  | tt0203912 Sin's Kitchen | A | OTTera.tv | 397 | 75,257,600 |
| `grumpy grannies` | `Drama` | Comedy |  | tt19306948 Grumpy Grannies | A | TCL ADS - Springserve | 246 | 71,612,880 |
| `7 years` | `Horror` | Drama |  | tt5517438 7 Years | B | OTTera.tv | 239 | 52,723,120 |
| `displaced` | `Family` | Drama,Short | documental | tt14717664 Displaced | B | OTTera.tv | 233 | 52,366,800 |
| `stray` | `Drama` | Documentary |  | tt11905922 Stray | B | OTTera.tv | 236 | 52,344,640 |
| `friends only` | `Family` | Drama,Romance |  | tt15680876 Friends Only | A | OTTera.tv | 234 | 52,197,280 |
| `should've put a ring on it` | `Drama` | Comedy |  | tt1941648 Should've Put a Ring on I | A | TCL ADS - Springserve | 209 | 44,291,600 |
| `bitter sky` | `Adventure` | Drama,Short |  | tt11418166 Bitter Sky | A | OTTera.tv | 212 | 40,432,880 |
| `craig's pathetic freakout` | `Drama` | Comedy,Short |  | tt12115180 Craig's Pathetic Freakout | A | OTTera.tv | 211 | 40,380,400 |

**relleno** (un título por fila; muestra completa en `validacion-relleno-muestra-genero-contradicciones.csv`):

| Título | Declarado | IMDb | Wikidata extra | Match | Conf. | Publisher (ej.) | Filas | Requests |
|---|---|---|---|---|---|---|---:|---:|
| `penance lane` | `Drama` | Horror |  | tt1964995 Penance Lane | A | OTTera.tv | 1,108 | 802,499,680 |
| `rollers: trailer` | `Drama` | Comedy |  | tt9124868 Rollers | B | OTTera.tv | 601 | 410,249,840 |
| `formentera` | `Documentary` | Drama |  | tt1990232 Formentera | A | TCL ADS - Springserve | 58 | 252,371,680 |
| `tennis+` | `sports` | Comedy,Drama,Sci-Fi |  | tt2281489 Tennis | B | OTTera.tv | 69 | 215,773,280 |
| `lost in the maze` | `Adventure` | Documentary |  | tt29602142 Lost in the Maze | A | OTTera.tv | 423 | 152,450,560 |
| `the buddy cop` | `Action` | Comedy |  | tt20412912 The Buddy Cop | A | OTTera.tv | 421 | 151,549,120 |
| `machotaildrop` | `Sports` | Action,Comedy,Fantasy |  | tt1315388 Machotaildrop | A | TCL ADS - Springserve | 173 | 149,687,440 |
| `the secret handshake` | `Drama` | Family |  | tt3519936 The Secret Handshake | B | TCL ADS - Springserve | 209 | 95,906,320 |
| `we three kings` | `Drama` | Family |  | tt13091334 We Three Kings | B | OTTera.tv | 339 | 86,420,240 |
| `13 score: trailer` | `Action` | Horror |  | tt3168890 13 Score | A | OTTera.tv | 411 | 79,454,160 |
| `duck camp dinners season 2` | `Adventure` | Reality-TV |  | tt35146256 Duck Camp Dinners | A | OTTera.tv | 398 | 75,600,640 |
| `sin's kitchen: trailer` | `adventure,mystery` | Drama |  | tt0203912 Sin's Kitchen | A | OTTera.tv | 397 | 75,257,600 |
| `grumpy grannies` | `Drama` | Comedy |  | tt19306948 Grumpy Grannies | A | TCL ADS - Springserve | 246 | 71,612,880 |
| `7 years` | `Horror` | Drama |  | tt5517438 7 Years | B | OTTera.tv | 239 | 52,723,120 |
| `displaced` | `Family` | Drama,Short | documental | tt14717664 Displaced | B | OTTera.tv | 233 | 52,366,800 |
| `stray` | `Drama` | Documentary |  | tt11905922 Stray | B | OTTera.tv | 236 | 52,344,640 |
| `friends only` | `Family` | Drama,Romance |  | tt15680876 Friends Only | A | OTTera.tv | 234 | 52,197,280 |
| `should've put a ring on it` | `Drama` | Comedy |  | tt1941648 Should've Put a Ring on I | A | TCL ADS - Springserve | 209 | 44,291,600 |
| `bitter sky` | `Adventure` | Drama,Short |  | tt11418166 Bitter Sky | A | OTTera.tv | 212 | 40,432,880 |
| `craig's pathetic freakout` | `Drama` | Comedy,Short |  | tt12115180 Craig's Pathetic Freakout | A | OTTera.tv | 211 | 40,380,400 |

## 2. Completitud

Nivel de granularidad: 0 = vacío; 1 = sin género comparable (solo "entertainment"/"other"/tipo de contenido); 2 = un género comparable; 3 = dos o más. La **propuesta** conserva lo declarado que no choca (incluido lo no comparable) y agrega los géneros IMDb (hasta 3) y los extra de Wikidata (telenovela, holiday, indie…) en el vocabulario canónico del proyecto.

Estado de partida (% del total de filas):

| Estado | consolidado | relleno |
|---|---:|---:|
| `vacia` | 60,989 (6.4%) · req 13.9% | 19,317 (2.0%) · req 10.9% |
| `llena` | 886,620 (92.4%) · req 85.1% | 928,292 (96.8%) · req 88.0% |
| `contradicha` | 11,833 (1.2%) · req 1.0% | 11,833 (1.2%) · req 1.0% |

Distribución del nivel actual y del nivel propuesto (% del total de filas):

| Nivel | consolidado · actual | consolidado · propuesto | relleno · actual | relleno · propuesto |
|---|---:|---:|---:|---:|
| nivel `0` | 60,989 (6.4%) · req 13.9% | 42,574 (4.4%) · req 12.4% | 19,317 (2.0%) · req 10.9% | 19,317 (2.0%) · req 10.9% |
| nivel `1` | 151,457 (15.8%) · req 17.3% | 131,537 (13.7%) · req 16.3% | 173,151 (18.1%) · req 18.7% | 152,714 (15.9%) · req 17.6% |
| nivel `2` | 522,978 (54.5%) · req 54.3% | 380,394 (39.6%) · req 39.9% | 530,216 (55.3%) · req 54.8% | 382,252 (39.8%) · req 40.0% |
| nivel `3` | 224,018 (23.4%) · req 14.5% | 404,937 (42.2%) · req 31.5% | 236,758 (24.7%) · req 15.5% | 405,159 (42.2%) · req 31.5% |

Qué cambia fila a fila: `rellena` (vacía con propuesta), `sube` (más géneros o uno más preciso), `corrige` / `corrige_parcial` (estaba contradicha o parcial), `mantiene` (ya está igual o mejor), `sin_propuesta` (sin evidencia):

| Mejora | consolidado | relleno |
|---|---:|---:|
| `rellena` | 18,415 (1.9%) · req 1.5% | — |
| `sube` | 212,692 (22.2%) · req 18.4% | 215,837 (22.5%) · req 18.6% |
| `corrige` | 11,833 (1.2%) · req 1.0% | 11,833 (1.2%) · req 1.0% |
| `corrige_parcial` | 34,739 (3.6%) · req 2.1% | 34,897 (3.6%) · req 2.4% |
| `mantiene` | 639,189 (66.6%) · req 64.6% | 677,558 (70.6%) · req 67.1% |
| `sin_propuesta` | 42,574 (4.4%) · req 12.4% | 19,317 (2.0%) · req 10.9% |

**Telenovela** es el caso concreto de "género más preciso": Wikidata lo marca como género propio y ningún vendedor lo declara así. Filas de títulos que Wikidata clasifica como telenovela:

| Telenovela según Wikidata | consolidado | relleno |
|---|---:|---:|
| `propuesta` | 16,087 (1.7%) · req 4.6% | 16,087 (1.7%) · req 4.6% |
| `ya_declarada` | 56 (0.0%) · req 0.0% | 56 (0.0%) · req 0.0% |

### Por país — consolidado

|  | Filas | `rellena` | `sube` | `corrige` | `corrige_parcial` | `mantiene` | `sin_propuesta` |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mexico | 304,329 | 2.7% | 22.5% | 1.0% | 2.4% | 66.1% | 5.2% |
| Colombia | 101,514 | 1.4% | 22.2% | 1.8% | 4.0% | 65.0% | 5.6% |
| Chile | 107,269 | 1.6% | 23.0% | 1.4% | 4.1% | 66.2% | 3.9% |

### Por publisher — consolidado

|  | Filas | `rellena` | `sube` | `corrige` | `corrige_parcial` | `mantiene` | `sin_propuesta` |
|---|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 200,221 | 2.0% | 20.2% | 0.9% | 5.3% | 68.4% | 3.1% |
| iion Pty Ltd | 183,090 | 3.2% | 23.3% | 1.6% | 4.1% | 61.1% | 6.8% |
| TCL ADS - Springserve | 120,000 | 2.6% | 22.0% | 1.2% | 4.8% | 65.1% | 4.3% |
| TCL ADs (APAC) | 112,769 | 2.1% | 21.9% | 1.2% | 5.4% | 66.3% | 3.2% |
| Select Plus PTE LTD (CTV) | 83,294 | 1.1% | 37.5% | 3.7% | 0.0% | 53.7% | 4.1% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 23,608 | 0.2% | 31.5% | 0.5% | 2.0% | 63.8% | 2.0% |
| PML Digital | 23,147 | 1.1% | 20.0% | 1.0% | 5.7% | 69.2% | 3.0% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 21,859 | 0.8% | 27.4% | 0.9% | 4.4% | 63.9% | 2.5% |
| AWG Media | 18,736 | 1.2% | 9.1% | 0.8% | 0.5% | 84.1% | 4.2% |
| Vidaa | 17,233 | 0.4% | 29.9% | 0.3% | 0.0% | 68.0% | 1.4% |
| Coocaa, a SKYWORTH company | 14,978 | 1.4% | 8.3% | 0.9% | 0.1% | 84.3% | 4.9% |
| Televisa Univision via SpringServe | 14,464 | 0.1% | 43.1% | 0.8% | 0.0% | 52.6% | 3.4% |

Propuestas más frecuentes (consolidado, % del total de filas):

| Propuesta | Filas | % filas | % requests |
|---|---:|---:|---:|
| `drama` | 9,362 | 1.0% | 0.5% |
| `drama,romance` | 8,536 | 0.9% | 0.6% |
| `drama,comedia` | 7,235 | 0.8% | 0.7% |
| `terror,thriller` | 7,075 | 0.7% | 0.6% |
| `drama,romance,telenovela` | 6,587 | 0.7% | 2.1% |
| `comedia` | 6,422 | 0.7% | 0.6% |
| `drama,thriller` | 5,820 | 0.6% | 0.6% |
| `drama,crimen` | 5,393 | 0.6% | 0.3% |
| `drama,comedia,romance` | 4,879 | 0.5% | 0.4% |
| `documental` | 4,749 | 0.5% | 0.3% |
| `terror,misterio` | 4,709 | 0.5% | 0.3% |
| `terror,comedia` | 4,308 | 0.5% | 0.3% |
| `drama,telenovela` | 4,208 | 0.4% | 0.9% |
| `western,drama` | 3,478 | 0.4% | 0.2% |
| `thriller,drama` | 3,141 | 0.3% | 0.2% |
| `crimen,drama` | 3,112 | 0.3% | 0.2% |
| `accion,crimen,drama` | 2,888 | 0.3% | 0.2% |
| `drama,documental` | 2,815 | 0.3% | 0.3% |
| `documental,deportes` | 2,638 | 0.3% | 0.2% |
| `terror` | 2,579 | 0.3% | 0.3% |

### Por país — relleno

|  | Filas | `rellena` | `sube` | `corrige` | `corrige_parcial` | `mantiene` | `sin_propuesta` |
|---|---:|---:|---:|---:|---:|---:|---:|
| Mexico | 304,329 | 0.0% | 23.0% | 1.0% | 2.4% | 70.9% | 2.7% |
| Colombia | 101,514 | 0.0% | 22.5% | 1.8% | 4.0% | 69.7% | 1.9% |
| Chile | 107,269 | 0.0% | 23.2% | 1.4% | 4.1% | 70.1% | 1.3% |

### Por publisher — relleno

|  | Filas | `rellena` | `sube` | `corrige` | `corrige_parcial` | `mantiene` | `sin_propuesta` |
|---|---:|---:|---:|---:|---:|---:|---:|
| OTTera.tv | 200,221 | 0.0% | 20.5% | 0.9% | 5.3% | 72.0% | 1.2% |
| iion Pty Ltd | 183,090 | 0.0% | 23.9% | 1.6% | 4.1% | 68.3% | 2.1% |
| TCL ADS - Springserve | 120,000 | 0.0% | 22.4% | 1.2% | 4.9% | 69.9% | 1.6% |
| TCL ADs (APAC) | 112,769 | 0.0% | 22.2% | 1.2% | 5.4% | 70.1% | 1.0% |
| Select Plus PTE LTD (CTV) | 83,294 | 0.0% | 37.6% | 3.7% | 0.0% | 58.0% | 0.7% |
| Equativ (Formerly SMART AdServer) - oRTB CTV | 23,608 | 0.0% | 31.6% | 0.5% | 2.0% | 64.0% | 1.9% |
| PML Digital | 23,147 | 0.0% | 20.3% | 1.0% | 5.7% | 72.1% | 0.9% |
| METAX SOFTWARE PTE. LTD. (Exchange) | 21,859 | 0.0% | 27.7% | 0.9% | 4.5% | 65.3% | 1.7% |
| AWG Media | 18,736 | 0.0% | 9.4% | 0.8% | 0.5% | 88.6% | 0.7% |
| Vidaa | 17,233 | 0.0% | 30.0% | 0.3% | 0.0% | 68.5% | 1.1% |
| Coocaa, a SKYWORTH company | 14,978 | 0.0% | 8.5% | 0.9% | 0.1% | 89.7% | 0.7% |
| Televisa Univision via SpringServe | 14,464 | 0.0% | 43.1% | 0.8% | 0.0% | 52.7% | 3.4% |

### Por origen del valor — relleno

|  | Filas | `rellena` | `sube` | `corrige` | `corrige_parcial` | `mantiene` | `sin_propuesta` |
|---|---:|---:|---:|---:|---:|---:|---:|
| app_default | 1,644 | 0.0% | 1.7% | 0.0% | 0.0% | 98.3% | 0.0% |
| imdb | 17,028 | 0.0% | 14.5% | 0.0% | 0.0% | 85.5% | 0.0% |
| intra_titulo | 23,000 | 0.0% | 2.8% | 0.0% | 0.7% | 96.5% | 0.0% |
| original | 898,453 | 0.0% | 23.7% | 1.3% | 3.9% | 71.1% | 0.0% |

Propuestas más frecuentes (relleno, % del total de filas):

| Propuesta | Filas | % filas | % requests |
|---|---:|---:|---:|
| `drama,romance` | 8,201 | 0.8% | 0.6% |
| `drama` | 7,592 | 0.8% | 0.4% |
| `drama,comedia` | 7,235 | 0.8% | 0.7% |
| `terror,thriller` | 6,754 | 0.7% | 0.6% |
| `drama,romance,telenovela` | 6,587 | 0.7% | 2.1% |
| `comedia` | 5,819 | 0.6% | 0.5% |
| `drama,crimen` | 5,394 | 0.6% | 0.3% |
| `drama,thriller` | 5,184 | 0.5% | 0.5% |
| `drama,comedia,romance` | 4,901 | 0.5% | 0.4% |
| `terror,comedia` | 4,308 | 0.5% | 0.3% |
| `drama,telenovela` | 4,208 | 0.4% | 0.9% |
| `documental` | 4,206 | 0.4% | 0.3% |
| `terror,misterio` | 4,157 | 0.4% | 0.3% |
| `western,drama` | 3,478 | 0.4% | 0.2% |
| `thriller,drama` | 3,141 | 0.3% | 0.2% |
| `crimen,drama` | 2,575 | 0.3% | 0.2% |
| `drama,documental` | 2,572 | 0.3% | 0.3% |
| `accion,crimen,drama` | 2,498 | 0.3% | 0.2% |
| `documental,deportes` | 2,476 | 0.3% | 0.2% |
| `romance,comedia` | 2,463 | 0.3% | 0.3% |

## 3. Límites

- El género es opinable y IMDb trae hasta tres: por eso hay una categoría `afin` y la cifra dura es `contradice` (nada de lo declarado cabe).
- Un match B falla 1 de cada 4 veces; una contradicción de género con confianza B puede ser el match. La muestra trae la confianza para filtrar.
- Lo no comparable (lifestyle, viajes, cocina, religión, videojuegos) no se valida ni se propone: IMDb no lo registra.
- En el relleno, el origen `imdb` de contentGenre se valida contra la misma fuente: su `coincide` es circular.
