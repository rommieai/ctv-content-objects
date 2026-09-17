# Análisis exploratorio — Inventario CTV LATAM (content objects + eCPM)

Análisis de las exportaciones del reporte de *inventory source* (v10, v11 y v12) sobre
inventario CTV en LATAM: cobertura y calidad de los content objects de OpenRTB
(género, categoría, serie, título, rating, idioma, duración, livestream) y
comportamiento del eCPM, global, por país y por publisher.

Los CSV de origen **no se versionan** (100+ MB cada uno, ver `.gitignore`); los reportes
y la data agregada en JSON sí.

## Estructura

```
scripts/                          codigo que genera los consolidados y los JSON
  consolidar.py                   une N exportaciones en un CSV sin duplicados
  analizar.py                     analisis por columna + desglose por dimension -> JSON
  normalizar_monetizar.py         normaliza genero/rating y analiza el eCPM > 0
  analizar_genero_titulo_paises.py genero normalizado + auditoria de contentTitle por pais
  generar_visual_paises.py        SVG con las tablas de paises lado a lado
  requests_ecpm_por_vacio.py      por pais y columna: requests y eCPM ponderado de las filas
                                  con dato util vs vacias (tablas por pais del detallado)
  generar_graficos_ecpm_vacio.py  SVG (sin dependencias): scatter eCPM llenas vs vacias por
                                  columna con recta OLS y R2, scatter completitud vs eCPM, y
                                  pies del reparto del gasto; a partir del JSON anterior
  generar_scatter_completitud_ecpm.py  scatter fila a fila (SVG): campos llenos (0-8) vs eCPM en
                                  escala log, un punto por registro vendido (tamano = requests)
                                  y el eCPM ponderado de cada nivel; reemplaza al heatmap
                                  (generar_heatmap_completitud_ecpm.py, ya fuera del pipeline)
  generar_graficos_drivers_ecpm.py  SVG de lo que mueve el eCPM ponderado: heatmap publisher x
                                  pais y scatter % vendido vs eCPM por publisher (+ JSON)
  generar_barras_app_completitud.py  barras por app (top 12): eCPM ponderado segun campos llenos
                                  (0-8) del registro, con % de requests vendidos por nivel (+ JSON)
  generar_tabla_pageurl_titulos.py  por titulo: en cuantos pageURL, publishers, emisores (pageURL
                                  agrupados por App Name) y paises aparece; tabla pageURL -> emisor
  generar_reporte_vacios.py       markdown "content objects cuando X esta vacio" a partir del
                                  JSON de analizar.py --solo-vacios-en X y del JSON completo
  generar_reporte_detallado.py    markdown del detallado por pais (solo tablas) desde los JSON de
                                  analizar.py y requests_ecpm_por_vacio.py
  generar_reporte_graficos.py     markdown del reporte de graficas desde los JSON de R2 y heatmap
  generar_reporte_completitud.py  markdown "que se puede completar de cada content object:
                                  metodos y fuentes" desde el JSON del relleno y las validaciones
  enriquecer_externo.py           rellena content objects vacios: intra-titulo, IMDb offline,
                                  Wikidata/TVMaze (cache incremental). Sin defaults por app ni
                                  relleno de contentLanguage desde 2026-09-17
  validar_categorias.py           valida contentCategory contra IMDb/Wikidata (cache) y las
                                  taxonomias IAB oficiales: correctitud de lo lleno y
                                  categoria mas fina alcanzable por fila
  generar_reporte_validacion.py   los dos markdown (correctitud, completitud) desde los JSON
  validar_genero_series.py        lo mismo para contentGenre (correctitud + completitud) y
                                  contentSeries (correctitud basica + que filas son serie sin
                                  decirlo, nombre propuesto, temporada/episodio del titulo)
  generar_reporte_genero_series.py  sus dos markdown (genero, series)

reportes/
  old_reports/                    tandas hasta v17 (v10 a v17), archivadas para no hacer ruido:
    01-v10/                         primera exploracion (v10): resumen y detallado 18 paises
    02-v11/                         detallado de v11 (18 paises)
    03-consolidado-v10-v11/         comparativo v10 vs v11, unificado y normalizacion
    04-consolidado-v10-v11-v12/     tanda sobre el consolidado v10+v11+v12
    05-consolidado-v10-a-v13/       tanda sobre el consolidado v10 a v13
    06-consolidado-v10-a-v14/         tanda sobre el consolidado v10 a v14
    07-consolidado-v10-a-v15/         tanda sobre el consolidado v10 a v15
    08-enriquecimiento-externo/     investigacion (sobre v10-a-v15): que columnas vacias se
                                    pueden rellenar con fuentes abiertas, en que %, y el
                                    pipeline periodico
    09-vix-televisa/                ViX/Televisa en Mexico: completitud antes/despues del
                                    relleno, requests, eCPM y rutas de venta (publishers)
    10-consolidado-v10-a-v16/         tanda sobre el consolidado v10 a v16 (primer corte con
                                    el cambio de formato en la fuente)
    11-enriquecimiento-externo-v16/ relleno de content objects sobre el consolidado v10-a-v16
    12-consolidado-v10-a-v17/       tanda sobre el consolidado v10 a v17: detallado por pais
                                    (MX/CO/CL), publishers, normalizacion+eCPM y genero/titulo
                                    (el formato nuevo ya era el 54% del corte)
    13-enriquecimiento-externo-v17/ relleno de content objects sobre el consolidado v10-a-v17
    14-content-objects-vacios-v17/  un reporte por content object con la distribucion de las
                                    DEMAS columnas en las filas donde ese viene vacio
    15-validacion-categorias-v17/   validacion de contentCategory sobre v10-a-v17
    16-validacion-genero-series-v17/  lo mismo para contentGenre y contentSeries
  17-consolidado-v10-a-v18/         tanda anterior (v10 a v18, solo tablas): detallado por pais
                                  (MX/CO/CL), publishers, normalizacion+eCPM, genero/titulo y
                                  reporte-graficos-ecpm-vacio.md (scatter con R2, pies, heatmap)
  18-enriquecimiento-externo-v18/ relleno de content objects sobre v10-a-v18 (tanda anterior)
  19-validacion-categorias-v18/   validacion de contentCategory sobre v10-a-v18 (tanda anterior)
  20-validacion-genero-series-v18/  lo mismo para contentGenre y contentSeries (tanda anterior)
  21-consolidado-v10-a-v19/         la version vigente, tres reportes md: detallado por pais
                                  (MX/CO/CL) con requests y eCPM ponderado lleno/vacio por
                                  columna; graficas del eCPM lleno/vacio y heatmap; y "que se
                                  puede completar de cada content object" (solo tablas);
                                  recursos/ trae los JSON, SVG, muestras CSV y la version
                                  completa del reporte de completitud (metodos y fuentes)

ejecutivo/                        resumenes en PDF para stakeholders
```

Cada reporte `.md` es el análisis narrado; su `.json` homónimo trae la data completa
que lo respalda (distribuciones, tops, estadísticos).

## Pipeline

```bash
# 1. Consolidar las exportaciones (la mas reciente primero: sus metricas ganan)
python scripts/consolidar.py inventory-consolidado.csv v12.csv v11.csv v10.csv

# 2. Analisis por columna + desglose por dimension (JSON + digests para redactar)
python scripts/analizar.py inventory-consolidado.csv reportes/NN/recursos/reporte-paises.json \
    --grupos "Mexico,Colombia,Chile" --digest ./digests          # por pais (default)
python scripts/generar_reporte_detallado.py reportes/NN 19 "31 ago-14 sep 2026" \
    --corte <v19 crudo>.csv --prev-filas <filas del consolidado anterior>   # md del detallado
# (desde v19 los JSON, SVG y muestras CSV de la tanda van en reportes/NN/recursos/; los md en reportes/NN/)
python scripts/analizar.py inventory-consolidado.csv reporte-publishers.json \
    --por Publisher --top-grupos 12                              # por publisher
python scripts/analizar.py inventory-consolidado.csv vacios-contentRating.json \
    --grupos "Mexico,Colombia,Chile" --solo-vacios-en contentRating   # solo filas sin rating
python scripts/generar_reporte_vacios.py vacios-contentRating.json reporte-paises.json \
    reporte-vacios-contentRating.md --visual visual.svg [--notas conclusiones.md]

# 3. Normalizacion de genero/rating + analisis del inventario monetizado
python scripts/normalizar_monetizar.py inventory-consolidado.csv \
    inventory-enriquecido.csv reporte-normalizacion.json
python scripts/requests_ecpm_por_vacio.py inventory-consolidado.csv \
    reportes/NN/recursos/reporte-requests-ecpm-por-vacio.json --paises "Mexico,Colombia,Chile"
python scripts/generar_graficos_ecpm_vacio.py reportes/NN/recursos/reporte-requests-ecpm-por-vacio.json reportes/NN/recursos
python scripts/generar_scatter_completitud_ecpm.py inventory-consolidado.csv reportes/NN/recursos
python scripts/generar_graficos_drivers_ecpm.py inventory-consolidado.csv reportes/NN/recursos  # publisher x pais
python scripts/generar_barras_app_completitud.py inventory-consolidado.csv reportes/NN/recursos  # por app
python scripts/generar_tabla_pageurl_titulos.py inventory-relleno.csv reportes/NN/recursos       # titulos por pageURL (paso 4 antes)
python scripts/generar_reporte_graficos.py reportes/NN 19                   # md de las graficas

# 4. (opcional) Relleno de content objects vacios con fuentes internas + abiertas
python scripts/enriquecer_externo.py inventory-enriquecido.csv \
    inventory-relleno.csv reporte-relleno.json \
    --cache-dir cache-enriquecimiento --wikidata [--tvmaze]

# 5. Validacion de contentCategory (correctitud + completitud), sobre el consolidado y el
#    relleno. Usa el cache de titulos del paso 4 y descarga las taxonomias IAB oficiales a
#    cache-enriquecimiento/iab/ la primera vez. El CSV fila a fila (--filas) es grande:
#    dejarlo en la raiz; los JSON y las muestras van al paquete de reportes.
python scripts/validar_categorias.py inventory-consolidado.csv reportes/NN/validacion-consolidado \
    --nombre consolidado --filas validacion-consolidado-filas.csv
python scripts/validar_categorias.py inventory-relleno.csv reportes/NN/validacion-relleno \
    --nombre relleno --filas validacion-relleno-filas.csv
python scripts/generar_reporte_validacion.py reportes/NN \
    consolidado=reportes/NN/validacion-consolidado.json relleno=reportes/NN/validacion-relleno.json

# 6. Lo mismo para contentGenre y contentSeries (mismo cache, mismas opciones)
python scripts/validar_genero_series.py inventory-consolidado.csv reportes/MM/validacion-consolidado \
    --nombre consolidado --filas validacion-genero-series-consolidado-filas.csv
python scripts/validar_genero_series.py inventory-relleno.csv reportes/MM/validacion-relleno \
    --nombre relleno --filas validacion-genero-series-relleno-filas.csv
python scripts/generar_reporte_genero_series.py reportes/MM \
    consolidado=reportes/MM/validacion-consolidado.json relleno=reportes/MM/validacion-relleno.json

# 7. (desde v19) un solo md "que se puede completar de cada content object: metodos y fuentes"
#    con el JSON del relleno (paso 4) y las cuatro validaciones (pasos 5 y 6) de la misma tanda
python scripts/generar_reporte_completitud.py reportes/NN 19 \
    --detallado reportes/NN/recursos/reporte-content-objects-detallado-v19-consolidado.json \
    --vacio reportes/NN/recursos/reporte-requests-ecpm-por-vacio-v19.json \
    --relleno reportes/NN/recursos/reporte-relleno-v19.json \
    --cat-consolidado reportes/NN/recursos/validacion-categorias-consolidado.json \
    --cat-relleno reportes/NN/recursos/validacion-categorias-relleno.json \
    --gs-consolidado reportes/NN/recursos/validacion-genero-series-consolidado.json \
    --gs-relleno reportes/NN/recursos/validacion-genero-series-relleno.json
```

Solo requiere Python 3.9+ (stdlib, sin dependencias). En Windows conviene correr los
scripts con `PYTHONIOENCODING=utf-8` (algunos titulos traen U+FFFD y la consola cp1252
falla al imprimirlos; el JSON se escribe igual). El paso 4 usa `requests` si esta
instalado (para Wikidata/TVMaze) y descarga los IMDb Non-Commercial Datasets (~750 MB) a
`cache-enriquecimiento/` la primera vez; despues solo consulta los titulos nuevos de cada
tanda (cache en `cache-enriquecimiento/titulos.json`). Ver `reportes/old_reports/08-.../` para el
detalle de fuentes, licencias y cobertura medida. Los pasos 5 y 6 no consultan nada online
salvo las taxonomias IAB (~100 KB, GitHub de IAB Tech Lab); ver `reportes/19-.../README.md`
y `reportes/20-.../README.md`.

El inventario tambien vive en **BigQuery** (proyecto `tudia-tagscreen`, dataset `ctv_inventory`,
location US) para consultarlo desde Looker Studio. Dos tablas (esquemas en `scripts/bigquery/`):

- `consolidado_v10_a_v14` (nombre historico de la primera carga): contiene **solo el corte
  vigente** (desde 2026-09-14, v18: 512,000 filas), enriquecido con `genero_normalizado` y
  `rating_franja` via `normalizar_monetizar.py` sobre el CSV crudo, mas dos columnas para Looker:
  `cal_total_cost` = total_requests * ecpm / 1000 (eCPM ponderado en Looker =
  SUM(cal_total_cost) / SUM(total_requests) * 1000) y `fecha_reporte` (DATE, dia en que se
  genero el reporte en PubMatic). Ya no es un consolidado.
- `consolidado_v10_a_v17_relleno`: el consolidado v10-a-v17 relleno completo
  (`inventory-consolidado-v10-a-v17-relleno.csv`, 959,442 filas, 38 columnas con
  `*_relleno` / `*_origen` y `ext_*`).

Recarga (reemplaza la tabla completa):

```
python scripts/normalizar_monetizar.py <vN crudo>.csv vN-enriquecido-base.csv vN.json
# agregar cal_total_cost y fecha_reporte (ver scripts/bigquery/agregar_columnas_looker.py)
python scripts/bigquery/agregar_columnas_looker.py vN-enriquecido-base.csv vN-enriquecido.csv 2026-09-14
bq load --source_format=CSV --skip_leading_rows=1 --allow_quoted_newlines --replace   ctv_inventory.consolidado_v10_a_v14 vN-enriquecido.csv scripts/bigquery/schema-enriquecido.json
bq load --source_format=CSV --skip_leading_rows=1 --allow_quoted_newlines --replace   ctv_inventory.consolidado_v10_a_v17_relleno inventory-consolidado-v10-a-v17-relleno.csv scripts/bigquery/schema-relleno.json
```

Validar siempre `COUNT(*)` y `SUM(total_requests)` contra el CSV. Los campos vacios del CSV
quedan como NULL en BigQuery.

## Notas metodológicas clave

- Cada fila de los CSV es una **combinación agregada** de 14 dimensiones + 2 métricas
  (`Total Requests`, `eCPM`), no un evento. Los análisis siempre separan **% de filas**
  (variedad de catálogo) y **% de requests** (tráfico real): el 1% de las filas
  concentra ~50% de los requests.
- Las exportaciones vienen **truncadas a 512,000 filas** y son cortes casi idénticos de
  la misma ventana (~97% de llaves compartidas entre versiones). Por eso se consolidan
  por unión de llaves (sin sumar métricas, que sería doble conteo) conservando las
  métricas del corte más reciente.
- Un valor se considera vacío si es centinela (`Not Available`, `Not Applicable`,
  `Unknown`...) o basura equivalente: `[-7]` en contentCategory, el hash MD5 de la
  cadena vacía en contentSeries, macros sin reemplazar (`{{CONTENT_SERIES}}`).
- Los content objects son estables entre versiones del reporte; **los eCPM se
  recalculan** (entre v11 y v12 desapareció un outlier de 200.0 y el ponderado global
  bajó de ~4.98 a 4.55). Fijar la versión antes de comparar precios.

## Reportes (el más reciente primero)

| Reporte | Contenido |
|---|---|
| `reportes/21-.../reporte-content-objects-detallado-v19-consolidado.md` | **Vigente:** content objects por pais (MX/CO/CL) sobre el consolidado v10 a v19 (1,158,509 filas; v19 aporto 86,669 combinaciones nuevas). Tablas por pais con % de filas llenas, top 3 referencias, si se puede aumentar el % de filas llenas y el aumento estimado (ganancia del relleno) por columna |
| `reportes/21-.../reporte-graficos-ecpm-vacio.md` | **Vigente:** graficos SVG sobre v10-a-v19: pies del reparto del gasto entre filas llenas y vacias por columna, scatter fila a fila de campos llenos vs eCPM (log), los drivers del eCPM ponderado (heatmap publisher x pais, scatter % vendido vs eCPM por publisher: la ruta de venta explica ~2/3 de la variacion, los content objects poco) barras por app del eCPM ponderado segun campos llenos (dentro de una app el llenado casi no mueve el precio), y titulos emitidos por mas de un pageURL / emisor |
| `reportes/21-.../reporte-completitud-content-objects-v19.md` | **Vigente:** que se puede completar de cada content object, solo tablas por columna: origen del valor tras el relleno, que mas se puede afinar segun la validacion contra IMDb/Wikidata/IAB y que tan confiable es lo declarado y lo llenado. La version completa (contexto, fuentes con licencias y limites, metodos con candados) esta en `recursos/reporte-completitud-content-objects-v19-completo.md` |
| `reportes/20-validacion-genero-series-v18/README.md` | (v10-a-v18) validacion de contentGenre y contentSeries sobre v10-a-v18 (consolidado y relleno), con glosario y etiquetas en lenguaje claro; cifras clave v17 vs v18 en el README |
| `reportes/19-validacion-categorias-v18/README.md` | (v10-a-v18) validacion de contentCategory sobre v10-a-v18 (correctitud y completitud), mismo formato claro; cifras clave v17 vs v18 en el README |
| `reportes/18-enriquecimiento-externo-v18/reporte-relleno-por-columna.md` | (v10-a-v18) el pipeline de relleno corrido sobre v10-a-v18: % antes/despues y origen del valor por columna |
| `reportes/old_reports/16-validacion-genero-series-v17/README.md` | (v10-a-v17) lo mismo para contentGenre (el 85% de lo evaluable coincide con IMDb/Wikidata y solo 2.7% contradice; el 22% de las filas puede recibir mas generos o uno mas preciso, p. ej. telenovela en 16k filas) y contentSeries (correctitud basica: 2.4% de las series declaradas son peliculas segun IMDb; completitud: 10% del consolidado es serie sin nombre y se le puede proponer uno, 4.2% trae temporada/episodio en el titulo) |
| `reportes/old_reports/15-validacion-categorias-v17/README.md` | (v10-a-v17) ¿la contentCategory declarada esta bien? (correctitud: 15% de las filas evaluables del consolidado contradicen la evidencia IMDb/Wikidata o su propio genero, casi todo mapeos por defecto de Vidaa, PML, Equativ y METAX; el relleno baja a 6% pero `intra_titulo` propaga el `[IAB12]` de Vidaa al 48% de sus requests) y ¿se puede afinar? (completitud: el 79% de las filas del consolidado puede recibir una categoria IAB 2.2 con forma y/o genero; el relleno esta casi todo en nivel 1-2 y el 69% puede subir) |
| `reportes/old_reports/14-content-objects-vacios-v17/README.md` | ocho reportes (uno por content object) con la distribucion de las demas columnas en las filas donde ese content object viene vacio, MX/CO/CL, comparado con todo el dataset; el titulo vacio es el 7% de las filas pero el 29.5% de los requests |
| `reportes/17-.../reporte-content-objects-detallado-v18-consolidado.md` | (v10-a-v18) content objects por pais (MX/CO/CL) sobre el consolidado v10 a v18 (1,071,840 filas; 13.0% de requests de llaves viejas; la escritura nueva ya es el 67% del corte). Tablas por pais con requests y eCPM ponderado de las filas llenas vs vacias por columna |
| `reportes/17-.../reporte-publishers-v18-consolidado.md` | (v10-a-v18) tabla comparativa por publisher (top 12, con % filas y % requests) |
| `reportes/17-.../reporte-normalizacion-y-ecpm-v18-consolidado.md` | (v10-a-v18) genero/rating normalizados + inventario monetizado (53.3% del trafico; eCPM 4.04), misma estructura que v17 |
| `reportes/17-.../reporte-genero-titulo-paises.md` | (v10-a-v18) genero por pais + cuantas filas traen un genero/titulo de verdad (tablas) |
| `reportes/17-.../reporte-graficos-ecpm-vacio.md` | (v10-a-v18) graficos SVG del eCPM de filas llenas vs vacias por columna (scatter con OLS y R2, completitud vs eCPM, pies del reparto del gasto, heatmap fila a fila de campos llenos vs eCPM) |
| `reportes/old_reports/12-.../reporte-content-objects-detallado-v17-consolidado.md` | (v10-a-v17) content objects por pais (MX/CO/CL) sobre el consolidado v10 a v17. La escritura nueva del reporte ya es el 54% del corte y viene mejor poblada (rating 60%, idioma 48% de sus filas); el consolidado por llave ya no deduplica (959k filas, 10.6% de requests de llaves viejas): leer trafico y precio sobre el corte |
| `reportes/old_reports/12-.../reporte-publishers-v17-consolidado.md` | (v10-a-v17) desglose por publisher (top 12; Roku supera a OTTera como #1 en requests, iion #3, TV Azteca se apaga otra vez, Select Plus vuelve a 12.6 de vitrina) |
| `reportes/old_reports/12-.../reporte-normalizacion-y-ecpm-v17-consolidado.md` | (v10-a-v17) genero/rating normalizados + inventario monetizado (50.7% del trafico, de vuelta a la banda de 51; eCPM 4.04; Colombia 5.85 quinto corte subiendo; Chile rebota a 6.10; Argentina lidera con 6.25; documental 5.88 al frente del yield con volumen) |
| `reportes/old_reports/12-.../reporte-genero-titulo-paises.md` | (v10-a-v17) genero por pais + cuantas filas traen un genero/titulo de verdad (Mexico: 44% del trafico con titulo real) |
| `reportes/old_reports/13-enriquecimiento-externo-v17/reporte-relleno-por-columna.md` | (v10-a-v17) el pipeline de relleno corrido sobre v10-a-v17 |
| `reportes/old_reports/10-.../reporte-content-objects-detallado-v16-consolidado.md` | (v10-a-v16) content objects por pais (MX/CO/CL) sobre el consolidado v10 a v16. **v16 cambia de formato a mitad de ventana** (genero con mayuscula, rating en escala nueva, idioma como nombre; rating e idioma vacios en 2 de cada 3 filas nuevas): 162k llaves "nuevas" que son el mismo contenido reescrito, y caidas de 10-13pp en rating/idioma que son del reporte, no de los vendedores |
| `reportes/old_reports/10-.../reporte-publishers-v16-consolidado.md` | (v10-a-v16) desglose por publisher (top 12; Roku casi empata a OTTera, iion sube al #3, Zeasn entra y Select Plus sale) |
| `reportes/old_reports/10-.../reporte-normalizacion-y-ecpm-v16-consolidado.md` | (v10-a-v16) genero/rating normalizados (diccionario ampliado con la escala nueva) + inventario monetizado (52.6% del trafico; eCPM 4.06, sexta bajada; Colombia 5.60 cuarto corte subiendo; Chile ya detras de Argentina) |
| `reportes/old_reports/10-.../reporte-genero-titulo-paises.md` | (v10-a-v16) genero por pais + cuantas filas traen un genero/titulo de verdad (Mexico: 43% del trafico con titulo real) |
| `reportes/old_reports/11-enriquecimiento-externo-v16/reporte-relleno-por-columna.md` | (v10-a-v16) el pipeline de relleno corrido sobre v10-a-v16: recupera casi todo el idioma y buena parte del rating que el formato nuevo dejo vacios (idioma 66.9 -> 95.9%, rating 72.9 -> 85.4%) |
| `reportes/old_reports/09-vix-televisa/reporte-vix-televisa.md` | ViX/TelevisaUnivision en Mexico (sobre v10-a-v15) sobre el consolidado tal como viene — completitud por columna (filas y requests), eCPM ponderado por requests, y las 28 rutas de venta del inventario (Equativ, SpringServe, OB, Vidaa...) |
| `reportes/old_reports/08-enriquecimiento-externo/reporte-relleno-por-columna.md` | (sobre v10-a-v15) que se hizo columna por columna para rellenar los content objects vacios: las corridas de cada origen (intra-titulo, default por app, IMDb, Wikidata, derivados, semantica por app) con el % de filas que aporto cada una; hallazgos: contentLength es un codigo 1-8 (no duracion) y el contentIsLiveStream declarado es siempre 1 |
| `reportes/old_reports/07-.../reporte-content-objects-detallado-v15-consolidado.md` | (v10-a-v15) content objects por pais (MX/CO/CL) sobre el consolidado v10 a v15, con comparativo de % de filas no vacias y visual SVG |
| `reportes/old_reports/07-.../reporte-publishers-v15-consolidado.md` | (v10-a-v15) desglose por publisher (top 12; el rebote de TV Azteca y el default [IAB12] de Vidaa) |
| `reportes/old_reports/07-.../reporte-normalizacion-y-ecpm-v15-consolidado.md` | (v10-a-v15) genero/rating normalizados + inventario monetizado (52.9% del trafico, primera salida de la banda 51±0.1) |
| `reportes/old_reports/07-.../reporte-genero-titulo-paises.md` | (v10-a-v15) genero por pais + cuantas filas traen un genero/titulo de verdad (no vacio no siempre es util) |
| `reportes/old_reports/06-.../` | Tanda anterior (consolidado v10 a v14), misma estructura |
| `reportes/old_reports/05-.../` | Consolidado v10 a v13, misma estructura |
| `reportes/old_reports/04-.../reporte-genero-titulo-paises.md` | Género normalizado por país (MX/CO/CL) + fill efectivo de contentTitle: qué parte de lo "lleno" no es un título real |
| `reportes/old_reports/04-.../reporte-publishers-v12-consolidado.md` | Desglose por publisher (top 12): quién manda qué metadata, quién rompe qué y cómo monetiza cada ruta |
| `reportes/old_reports/04-.../reporte-timeline-emision-programas.md` | Timeline de emisión de los programas que aparecen como contentTitle (4–19 ago 2026): qué es evento real (LCDLFM4, Survivor, MasterChef, telenovelas, Liga MX) y qué es FAST de catálogo en loop |
| `reportes/old_reports/04-.../reporte-normalizacion-y-ecpm-v12-consolidado.md` | Género/rating normalizados + inventario monetizado; documenta el recálculo de eCPM de v12 |
| `reportes/old_reports/04-.../reporte-content-objects-detallado-v12-consolidado.md` | Content objects por país (México/Colombia/Chile) sobre el consolidado v10+v11+v12, con comparativo de fill por columna |
| `reportes/old_reports/03-.../reporte-normalizacion-y-ecpm.md` | Normalización y monetización sobre v10+v11 |
| `reportes/old_reports/03-.../reporte-comparativo-v10-v11.md` | Cruce entre exportaciones y justificación del método de consolidación |
| `reportes/old_reports/03-.../reporte-content-objects-detallado-unificado.md` | Detallado del consolidado v10+v11 (18 países) |
| `reportes/old_reports/02-v11/reporte-content-objects-detallado-v11.md` | Detallado de v11 (18 países) |
| `reportes/old_reports/01-v10/reporte-content-objects-detallado.md` | Detallado de v10 (18 países) |
| `reportes/old_reports/01-v10/reporte-content-objects.md` | Primera exploración |
| `ejecutivo/resumen-ejecutivo.pdf` | Resumen para stakeholders (LaTeX) |
