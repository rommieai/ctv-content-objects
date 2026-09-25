# Validación de contentGenre y contentSeries con fuentes abiertas (consolidado v10 a v18)

**Pregunta:** el género que declaran los vendedores, ¿coincide con IMDb y Wikidata, y se puede completar? Y las filas que son series, ¿lo dicen, con qué nombre, y traen temporada y episodio en el título?

**Fuentes:** `inventory-consolidado-v10-a-v18.csv` (1,071,840 filas, métricas del corte v18) y `inventory-consolidado-v10-a-v18-relleno.csv` (paquete 18). Evidencia: `cache-enriquecimiento/titulos.json` (15,267 títulos; match IMDb de confianza A o B en 531,080 filas, 49.5%), el título crudo y las demás rutas del mismo título.  
**Generado con:** `scripts/validar_genero_series.py` y `scripts/generar_reporte_genero_series.py`. Corrida del 2026-09-15 09:46. Misma metodología que el paquete 16 (v17); los reportes traen ahora un apartado "Cómo leer este reporte" y etiquetas en lenguaje claro con la clave técnica entre paréntesis.

| Archivo | Qué contiene |
|---|---|
| [reporte-genero.md](reporte-genero.md) | **contentGenre.** Correctitud: cómo vienen escritos los géneros, si coinciden con IMDb/Wikidata, qué se confunde con qué, por país, publisher y origen. Completitud: cuántos géneros se podrían agregar, telenovela como género propio, propuestas. |
| [reporte-series.md](reporte-series.md) | **contentSeries.** Correctitud básica: la serie declarada contra el tipo de IMDb. Completitud: qué es cada fila (serie, película, ambiguo, desconocido), series sin nombre a las que se les puede proponer uno, temporada y episodio extraíbles del título. |
| `validacion-{consolidado,relleno}.json` | Los agregados de cada tabla. |
| `validacion-*-muestra-genero-contradicciones.csv` | 400 títulos cuyo género declarado choca con IMDb/Wikidata, con géneros IMDb, id y confianza del match. |
| `validacion-*-muestra-series-contradicciones.csv` | Series declaradas en títulos que IMDb dice que son película. |
| `validacion-*-muestra-series-propuestas.csv` | Muestra aleatoria de filas que son serie sin nombre, con el nombre propuesto y la evidencia. |
| `validacion-genero-series-v18-{consolidado,relleno}-filas.csv` (raíz, no versionado) | Una fila por fila con todas las columnas de diagnóstico. |

## Cifras clave: v17 vs v18

| | v17 tal como llega | v17 después del relleno | v18 tal como llega | v18 después del relleno |
|---|---:|---:|---:|---:|
| Filas con género (% del total) | 93.6% | 98.0% | 92.4% | 97.6% |
| Género coincide con IMDb/Wikidata (% de las evaluables) | 84.8% | 85.3% | 84.9% | 85.5% |
| Género contradice (% de las evaluables) | 2.7% | 2.6% | 3.0% | 2.9% |
| Filas a las que se pueden agregar géneros | 22.2% | 22.5% | 22.8% | 23.2% |
| Filas de títulos que Wikidata marca como telenovela y no lo declaran | 16,087 | 16,087 | 17,710 | 17,710 |
| Filas con nombre de serie real (% del total) | 5.4% | 12.9% | 5.2% | 12.8% |
| Serie con nombre (% del total) | 5.2% | 12.8% | 5.0% | 12.7% |
| Serie sin nombre, con nombre proponible | 10.0% | 2.4% | 10.2% | 2.5% |
| Película: el vacío es correcto | 34.3% | 34.3% | 34.1% | 34.1% |
| Sin evidencia para saber si es serie | 50.3% | 50.3% | 50.6% | 50.6% |

## Cómo repetirlo

```bash
PYTHONIOENCODING=utf-8 python scripts/validar_genero_series.py inventory-consolidado-v10-a-v18.csv reportes/20-validacion-genero-series-v18/validacion-consolidado --nombre consolidado --filas validacion-genero-series-v18-consolidado-filas.csv
PYTHONIOENCODING=utf-8 python scripts/validar_genero_series.py inventory-consolidado-v10-a-v18-relleno.csv reportes/20-validacion-genero-series-v18/validacion-relleno --nombre relleno --filas validacion-genero-series-v18-relleno-filas.csv
python scripts/generar_reporte_genero_series.py reportes/20-validacion-genero-series-v18 consolidado=reportes/20-validacion-genero-series-v18/validacion-consolidado.json relleno=reportes/20-validacion-genero-series-v18/validacion-relleno.json
```

Opciones: `--confianza-min A`, `--min-filas-serie` / `--min-rutas-serie` (candado de las series por otras rutas, igual que en el relleno), `--paises`, `--top-publishers`. Los límites del método están al final de cada reporte.
