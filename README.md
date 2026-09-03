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
  enriquecer_externo.py           rellena content objects vacios: intra-dataset, defaults
                                  por app, IMDb offline, Wikidata/TVMaze (cache incremental)

reportes/
  01-v10/                         primera exploracion (v10): resumen y detallado 18 paises
  02-v11/                         detallado de v11 (18 paises)
  03-consolidado-v10-v11/         comparativo v10 vs v11, unificado y normalizacion
  04-consolidado-v10-v11-v12/     tanda sobre el consolidado v10+v11+v12
  05-consolidado-v10-a-v13/       tanda sobre el consolidado v10 a v13
  06-consolidado-v10-a-v14/         tanda sobre el consolidado v10 a v14
  07-consolidado-v10-a-v15/         la version vigente: detallado por pais (MX/CO/CL),
                                  publishers, normalizacion+eCPM y genero/titulo
  08-enriquecimiento-externo/     investigacion: que columnas vacias se pueden rellenar
                                  con fuentes abiertas, en que %, y el pipeline periodico
  09-vix-televisa/                ViX/Televisa en Mexico: completitud antes/despues del
                                  relleno, requests, eCPM y rutas de venta (publishers)

ejecutivo/                        resumenes en PDF para stakeholders
```

Cada reporte `.md` es el análisis narrado; su `.json` homónimo trae la data completa
que lo respalda (distribuciones, tops, estadísticos).

## Pipeline

```bash
# 1. Consolidar las exportaciones (la mas reciente primero: sus metricas ganan)
python scripts/consolidar.py inventory-consolidado.csv v12.csv v11.csv v10.csv

# 2. Analisis por columna + desglose por dimension (JSON + digests para redactar)
python scripts/analizar.py inventory-consolidado.csv reporte-paises.json \
    --grupos "Mexico,Colombia,Chile" --digest ./digests          # por pais (default)
python scripts/analizar.py inventory-consolidado.csv reporte-publishers.json \
    --por Publisher --top-grupos 12                              # por publisher

# 3. Normalizacion de genero/rating + analisis del inventario monetizado
python scripts/normalizar_monetizar.py inventory-consolidado.csv \
    inventory-enriquecido.csv reporte-normalizacion.json
```

# 4. (opcional) Relleno de content objects vacios con fuentes internas + abiertas
python scripts/enriquecer_externo.py inventory-enriquecido.csv \
    inventory-relleno.csv reporte-relleno.json \
    --cache-dir cache-enriquecimiento --wikidata [--tvmaze]
```

Solo requiere Python 3.9+ (stdlib, sin dependencias). El paso 4 usa `requests` si esta
instalado (para Wikidata/TVMaze) y descarga los IMDb Non-Commercial Datasets (~750 MB) a
`cache-enriquecimiento/` la primera vez; despues solo consulta los titulos nuevos de cada
tanda (cache en `cache-enriquecimiento/titulos.json`). Ver `reportes/08-.../` para el
detalle de fuentes, licencias y cobertura medida.

```bash

El consolidado enriquecido tambien vive en **BigQuery** para consultarlo desde Looker Studio:
tabla `tudia-tagscreen.ctv_inventory.consolidado_v10_a_v14` (nombre historico de la primera
carga; contiene siempre el consolidado vigente). Tras cada tanda se recarga con
`bq load --source_format=CSV --skip_leading_rows=1 --allow_quoted_newlines --replace`.

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
| `reportes/09-vix-televisa/reporte-vix-televisa.md` | **Nuevo:** ViX/TelevisaUnivision en Mexico sobre el consolidado tal como viene — completitud por columna (filas y requests), eCPM ponderado por requests, y las 28 rutas de venta del inventario (Equativ, SpringServe, OB, Vidaa...) |
| `reportes/08-enriquecimiento-externo/reporte-relleno-por-columna.md` | **Nuevo:** que se hizo columna por columna para rellenar los content objects vacios: las corridas de cada origen (intra-titulo, default por app, IMDb, Wikidata, derivados, semantica por app) con el % de filas que aporto cada una; hallazgos: contentLength es un codigo 1-8 (no duracion) y el contentIsLiveStream declarado es siempre 1 |
| `reportes/07-.../reporte-content-objects-detallado-v15-consolidado.md` | **Vigente:** content objects por pais (MX/CO/CL) sobre el consolidado v10 a v15, con comparativo de % de filas no vacias y visual SVG |
| `reportes/07-.../reporte-publishers-v15-consolidado.md` | **Vigente:** desglose por publisher (top 12; el rebote de TV Azteca y el default [IAB12] de Vidaa) |
| `reportes/07-.../reporte-normalizacion-y-ecpm-v15-consolidado.md` | **Vigente:** genero/rating normalizados + inventario monetizado (52.9% del trafico, primera salida de la banda 51±0.1) |
| `reportes/07-.../reporte-genero-titulo-paises.md` | **Vigente:** genero por pais + cuantas filas traen un genero/titulo de verdad (no vacio no siempre es util) |
| `reportes/06-.../` | Tanda anterior (consolidado v10 a v14), misma estructura |
| `reportes/05-.../` | Consolidado v10 a v13, misma estructura |
| `reportes/04-.../reporte-genero-titulo-paises.md` | Género normalizado por país (MX/CO/CL) + fill efectivo de contentTitle: qué parte de lo "lleno" no es un título real |
| `reportes/04-.../reporte-publishers-v12-consolidado.md` | Desglose por publisher (top 12): quién manda qué metadata, quién rompe qué y cómo monetiza cada ruta |
| `reportes/04-.../reporte-timeline-emision-programas.md` | Timeline de emisión de los programas que aparecen como contentTitle (4–19 ago 2026): qué es evento real (LCDLFM4, Survivor, MasterChef, telenovelas, Liga MX) y qué es FAST de catálogo en loop |
| `reportes/04-.../reporte-normalizacion-y-ecpm-v12-consolidado.md` | Género/rating normalizados + inventario monetizado; documenta el recálculo de eCPM de v12 |
| `reportes/04-.../reporte-content-objects-detallado-v12-consolidado.md` | Content objects por país (México/Colombia/Chile) sobre el consolidado v10+v11+v12, con comparativo de fill por columna |
| `reportes/03-.../reporte-normalizacion-y-ecpm.md` | Normalización y monetización sobre v10+v11 |
| `reportes/03-.../reporte-comparativo-v10-v11.md` | Cruce entre exportaciones y justificación del método de consolidación |
| `reportes/03-.../reporte-content-objects-detallado-unificado.md` | Detallado del consolidado v10+v11 (18 países) |
| `reportes/02-v11/reporte-content-objects-detallado-v11.md` | Detallado de v11 (18 países) |
| `reportes/01-v10/reporte-content-objects-detallado.md` | Detallado de v10 (18 países) |
| `reportes/01-v10/reporte-content-objects.md` | Primera exploración |
| `ejecutivo/resumen-ejecutivo.pdf` | Resumen para stakeholders (LaTeX) |
