# Relleno de content objects sobre el consolidado v10 a v18

**Fuente:** `inventory-consolidado-v10-a-v18-enriquecido.csv` (1,071,840 filas). **Salida:** `inventory-consolidado-v10-a-v18-relleno.csv` (no versionado; cargable a BigQuery con `scripts/bigquery/schema-relleno.json`). Generado con `scripts/enriquecer_externo.py --wikidata`, corrida del 2026-09-15 09:35.

Títulos distintos: 15,267; consultados por primera vez en esta corrida: 581; con match en IMDb: 7,689.

## Cómo leer este reporte

- Cada columna vacía se intenta llenar con fuentes internas (otras filas del mismo título, el valor habitual de la app) y abiertas (IMDb, Wikidata). El **origen** dice de dónde salió el valor final de cada fila; "Venía del vendedor" son las filas que ya lo traían y no se tocan.
- Los % son sobre el total de filas del consolidado. "Antes" es el % de filas con dato útil tal como llega; "Después" es el % tras el relleno.

## Qué se llenó, columna por columna

| Columna | Antes | Después | Venía del vendedor | Copiado de otra ruta del mismo título | Valor habitual de la app | IMDb | Wikidata | Derivado del género | Derivado del tipo IMDb (película / serie) | Semántica de la app (curada a mano) | Sigue vacío |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| contentCategory | 21.9% | 94.1% | 21.9% | 10.8% | 8.3% | — | — | 22.9% | 30.2% | — | 5.9% |
| contentSeries | 6.4% | 14.0% | 6.4% | 0.7% | — | 7.0% | — | — | — | — | 86.0% |
| contentLength | 11.9% | 49.8% | 11.9% | 35.3% | 2.7% | — | — | — | — | — | 50.2% |
| contentLanguage | 66.2% | 96.1% | 66.2% | 29.1% | 0.5% | — | 0.3% | — | — | — | 3.9% |
| contentIsLiveStream | 28.9% | 49.3% | 28.9% | — | — | — | — | — | 0.5% | 19.9% | 50.7% |
| contentRating | 74.9% | 82.8% | 74.9% | 7.8% | 0.0% | — | 0.1% | — | — | — | 17.2% |
| contentGenre | 92.4% | 97.6% | 92.4% | 2.9% | 0.2% | 2.1% | — | — | — | — | 2.4% |

*Las columnas de origen suman 100% por fila: reparten todas las filas del consolidado según de dónde salió el valor final, incluidas las que siguen vacías.*

*Reglas heredadas de la tanda v17: el rating se canoniza al aprender (la escala nueva `Teen Plus` cuenta como `tv-14`) y la propagación de series por título exige al menos 30 filas y 2 publishers. contentIsLiveStream no se propaga por título ni por app porque MovieArk marca 1 todo su catálogo; solo se usa la semántica de app curada a mano y las señales del vendedor.*
