# Validación de contentGenre y contentSeries con fuentes abiertas (consolidado v10 a v17)

**Pregunta:** tras validar `contentCategory` (paquete 15), ¿qué otras columnas admiten el mismo análisis? Las dos con evidencia externa suficiente son `contentGenre` (IMDb y Wikidata traen géneros para la mitad de las filas) y `contentSeries` (IMDb dice si un título es serie o película). Este paquete las cubre: género con correctitud y completitud completas; series con correctitud **básica** (lo que IMDb puede juzgar) y el peso puesto en la completitud (qué filas son serie sin decirlo, con qué nombre, y qué temporada/episodio trae el título).

**Fuentes:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas, métricas del corte v17) y `inventory-consolidado-v10-a-v17-relleno.csv` (columnas `contentGenre_relleno` / `contentSeries_relleno` + `_origen`). Evidencia: `cache-enriquecimiento/titulos.json` (14,686 títulos; match IMDb de confianza A/B en 476,869 filas, 49.7%), el título crudo y las demás rutas del mismo título.
**Generado con:** `scripts/validar_genero_series.py` (JSON + muestras por dataset) y `scripts/generar_reporte_genero_series.py` (los dos markdown). Corrida del 9 sep 2026, ~45 s por dataset, solo stdlib. Misma estructura y convenciones que el paquete 15.

| Reporte | Qué responde |
|---|---|
| [reporte-genero.md](reporte-genero.md) | **contentGenre.** Correctitud: formato de lo declarado, veredicto por fila (coincide / afín / parcial / contradice), qué género choca con qué, por país, publisher y origen; títulos con más tráfico. Completitud: nivel actual vs alcanzable, qué cambia fila a fila, telenovela como género propio, propuestas. |
| [reporte-series.md](reporte-series.md) | **contentSeries.** Correctitud básica: serie declarada vs tipo IMDb (coincide / otro nombre / contradice). Completitud: qué ES cada fila (serie, película, ambiguo, desconocido) y con qué evidencia; series sin nombre recuperables y nombre propuesto; temporada/episodio extraíbles del título. |
| `validacion-{consolidado,relleno}.json` | Los agregados de cada tabla. |
| `validacion-*-muestra-genero-contradicciones.csv` | 400 títulos cuyo género declarado choca con IMDb/Wikidata (uno por título, más tráfico primero), con géneros IMDb, id y confianza del match. |
| `validacion-*-muestra-series-contradicciones.csv` | Series declaradas en títulos que IMDb dice que son película. |
| `validacion-*-muestra-series-propuestas.csv` | Muestra aleatoria de filas que son serie sin nombre, con el nombre propuesto, la evidencia y temporada/episodio. |
| `validacion-genero-series-v17-{consolidado,relleno}-filas.csv` (raíz, no versionado) | Una fila por fila con todas las columnas de diagnóstico de las dos columnas. |

## Hallazgos — contentGenre

**Correctitud.** De las 898,453 filas con género (93.6% del consolidado), el 48.8% tiene evidencia externa. De esas, **84.8% coincide** con IMDb/Wikidata, 4.6% es afín (telenovela donde IMDb dice drama/romance, thriller donde dice terror), 7.9% acierta en un género y falla en otro, y **2.7% contradice** de plano (11,833 filas). El género es la columna mejor llenada del dataset y la más fiable: con esto queda justificado que el relleno de categoría se apoye en ella.

- **Lo que contradice es ruido de catálogo, no un vendedor.** Ningún publisher grande pasa del 2% de contradicción salvo Select Plus (3.9%). Los casos son títulos concretos con género fijo en toda la ruta: *penance lane* declarado Drama y es Horror (1,108 filas de OTTera, 800M requests), *rollers* Drama y es Comedy, *lost in the maze* Adventure y es Documentary. La confusión más frecuente es **drama por comedia** (5,078 filas), seguida de acción por drama y drama por terror.
- **El formato explica otro 7%:** 2.5% de las filas traen géneros con formato sucio ("drama, medical drama, hos…"), 1% prefijos técnicos (`genre_…`), 0.9% tipos de contenido en vez de género (`movies`, `live`) y 2.1% valores no reconocidos. No se juzgan, pero tampoco sirven.
- **AWG y Coocaa no se pueden evaluar** (87-89% sin match): son catálogos de podcasts y programas brasileños que IMDb no cubre.
- **En el relleno nada cambia**: el pipeline solo llenó el 4.4% de filas vacías (con `intra_titulo` e `imdb`) y no tocó lo declarado, así que las 11,833 contradicciones siguen ahí. El origen `imdb` coincide al 98.5% por construcción (circular).

**Completitud.** El 58% de las filas declara un solo género comparable y IMDb trae hasta tres: el **22.2% de las filas puede recibir más géneros o uno más preciso** (212,692 filas; 18.4% de los requests), otro 4.8% se corrige total o parcialmente y el 1.9% se rellena desde vacío. El nivel 3 (dos o más géneros) pasaría del 23.4% al 42.2% de las filas. El caso concreto de "más preciso" es **telenovela**: Wikidata la marca como género propio en títulos que los vendedores declaran solo "Drama"; son 16,087 filas proponibles contra 56 que ya la declaran. La propuesta conserva lo declarado que no choca y agrega lo externo (`drama` → `drama, romance, telenovela`).

## Hallazgos — contentSeries

**Correctitud (básica).** Solo 51,672 filas (5.4%) traen una serie real; otras 11,136 traen placeholders (`VOD` 5,725, `OTT Studios …`, `No Series`, `Research Unit`). El 89.7% de las series reales no se puede juzgar (AWG y Coocaa, sin match). De lo evaluable, **1,252 filas (2.4%) declaran serie en un título que IMDb dice que es película**, y al mirarlas resultan de dos tipos: (a) el "nombre de serie" es en realidad una **colección o canal** (*Modern Marvels* y *Cold Case Files Classic* en películas mexicanas de AWG, *Action Documentaries*, *Citas de Estados Unidos*), y (b) **matches equivocados** por título homónimo (*jajaja* → *Hahaha*, película coreana; *adam jones* → *Burnt*). Por eso la correctitud se deja en este nivel: IMDb no sabe cómo se llama la serie de un episodio con nombre propio (`otro_nombre`, 5.4%, es compatible).

**Completitud (lo que interesa).** Sobre el total de filas:

| Qué es la fila | Filas | % | % requests | Evidencia |
|---|---:|---:|---:|---|
| Película → el vacío es correcto | 330,068 | 34.4% | 21.4% | tipo IMDb |
| Serie | 146,177 | 15.2% | 16.9% | IMDb 6.0% · título con temporada/episodio 4.3% · otras rutas 2.7% · solo declarado 2.2% |
| Ambiguo (short, tvMovie, video, tvSpecial, placeholder `VOD`) | 72,758 | 7.6% | 4.6% | tipo IMDb |
| Desconocido | 410,439 | 42.8% | 57.1% | sin match ni marca en el título |

- **95,740 filas (10.0%; 10.5% de los requests) son serie y no traen nombre, y hay nombre que proponerles**: el propio título sin sufijos (*chicken stew season 6* → *chicken stew*), el que traen las otras rutas, o el canónico IMDb. Televisa (39% de sus filas), Vidaa (23%) y Equativ (23%) son quienes más series sin nombre mandan. En el relleno quedan 23,131 (2.4%): el paso `imdb` del pipeline ya nombró 66,219 y `intra_titulo` 6,390.
- **El título corrige a IMDb.** 41,203 filas traen "season N", "S01E03" o "ep N" en el título. Varias son títulos que IMDb había casado con una **película** homónima y que el vendedor sirve por temporadas: *chicken stew* (season 1 a 7, 3,644 filas), *forest frenzy of boonie bears* (season 1 a 4), *something scary*. Esto tiene consecuencia en el paquete 15: el relleno les asignó `[IAB1-5]` Películas por `derivado_tipo`, y son series. La regla "título con temporada manda sobre IMDb" ya está en los dos validadores; falta llevarla a `enriquecer_externo.py`.
- **Temporada y episodio existen en OpenRTB (`content.season`, `content.episode`) y el reporte no los expone**, pero el título permite extraerlos en 41,725 filas (4.3%): 33,040 con temporada, 7,039 con episodio, 1,646 con ambos. Quedan en `temporada` / `episodio` del CSV fila a fila como candidatos.
- **El 42.8% desconocido concentra el 57% de los requests**: es el catálogo sin título real (`epg`, `roku`, canales) y los títulos sin match. Ahí no hay fuente abierta que diga si es serie; solo el vendedor.

## Qué hacer con esto

1. **Género:** las 11,833 filas contradichas y las 34,739 parciales tienen propuesta (`gen_propuesta`) y muestra para revisar; la mayor ganancia es agregar géneros, no corregirlos: 212k filas pasan a dos o más, y 16k reciben `telenovela`.
2. **Series:** incorporar al relleno la evidencia del título (temporada/episodio → serie, nombre = título sin sufijos), que hoy no usa, y proponer `content.season` / `content.episode` como campos nuevos al equipo de datos.
3. **Cruce con el paquete 15:** recalcular `derivado_tipo` de contentCategory con el título por delante de IMDb (afecta a las series servidas por temporadas que hoy figuran como película).

## Límites

- El género es opinable: por eso hay `afin` y la cifra dura es `contradice`. Un match B puede ser el error; la muestra trae la confianza.
- Lo no comparable con IMDb (lifestyle, viajes, cocina, religión, videojuegos) no se valida ni se propone.
- En series, `serie_propuesta` prefiere el título de la fila (en su idioma) al canónico IMDb, que a veces está en inglés. "Season two" en letras se limpia del nombre pero no se extrae como número.
- El origen `imdb` del relleno (género y series) se valida contra la misma fuente: su `coincide` es consistencia, no verdad.

## Cómo repetirlo

```bash
PYTHONIOENCODING=utf-8 python scripts/validar_genero_series.py inventory-consolidado-v10-a-v17.csv \
    reportes/16-validacion-genero-series-v17/validacion-consolidado --nombre consolidado \
    --filas validacion-genero-series-v17-consolidado-filas.csv
PYTHONIOENCODING=utf-8 python scripts/validar_genero_series.py inventory-consolidado-v10-a-v17-relleno.csv \
    reportes/16-validacion-genero-series-v17/validacion-relleno --nombre relleno \
    --filas validacion-genero-series-v17-relleno-filas.csv
python scripts/generar_reporte_genero_series.py reportes/16-validacion-genero-series-v17 \
    consolidado=reportes/16-validacion-genero-series-v17/validacion-consolidado.json \
    relleno=reportes/16-validacion-genero-series-v17/validacion-relleno.json
```

Opciones: `--confianza-min A`, `--min-filas-serie` / `--min-rutas-serie` (candado de las series por otras rutas, igual que en el relleno), `--paises`, `--top-publishers`.
