# Validación de contentCategory con fuentes abiertas (consolidado v10 a v18)

**Pregunta:** las filas que traen categoría IAB, ¿la traen bien? Y a las que no la traen o la traen genérica, ¿se les puede poner una más fina con la evidencia disponible?

**Fuentes:** `inventory-consolidado-v10-a-v18.csv` (1,071,840 filas, 426,223,575,360 requests, métricas del corte v18) y `inventory-consolidado-v10-a-v18-relleno.csv` (la salida del pipeline de relleno, paquete 18). Evidencia: IMDb y Wikidata desde `cache-enriquecimiento/titulos.json` (15,267 títulos; match de confianza A o B en 49.5% de las filas) y las taxonomías oficiales de IAB Tech Lab.  
**Generado con:** `scripts/validar_categorias.py` (un JSON + muestras por dataset) y `scripts/generar_reporte_validacion.py` (los dos markdown). Corrida del 2026-09-15 09:42. Misma metodología que el paquete 15 (v17); los reportes traen ahora un apartado "Cómo leer este reporte" y etiquetas en lenguaje claro con la clave técnica entre paréntesis.

| Archivo | Qué contiene |
|---|---|
| [reporte-correctitud.md](reporte-correctitud.md) | **Parte 1.** Las filas con categoría: cómo vienen escritas, si son correctas, genéricas o incorrectas, quién se equivoca, el mismo título con categorías distintas según la ruta, y de paso el género contra IMDb. |
| [reporte-completitud.md](reporte-completitud.md) | **Parte 2.** Qué nivel de detalle tienen hoy las categorías y hasta cuál se podría llegar con la evidencia, fila a fila, por país, publisher y origen; qué categorías se propondrían. |
| `validacion-{consolidado,relleno}.json` | Los agregados que respaldan cada tabla. |
| `validacion-*-muestra-contradicciones.csv` | 400 títulos con categoría incorrecta por dataset (los de más tráfico primero) con lo declarado, lo esperado, el id IMDb y el motivo. |
| `validacion-*-muestra-propuestas.csv` | 400 filas al azar por dataset con la categoría propuesta y de dónde salió. |
| `validacion-categorias-v18-{consolidado,relleno}-filas.csv` (raíz, no versionado) | Una fila por fila del consolidado con todas las columnas de diagnóstico. |

## Cifras clave: v17 vs v18

| | v17 tal como llega | v17 después del relleno | v18 tal como llega | v18 después del relleno |
|---|---:|---:|---:|---:|
| Filas con categoría (% del total) | 21.9% | 94.3% | 21.9% | 94.1% |
| Categoría incorrecta (% de las evaluables) | 15.0% | 6.0% | 14.9% | 5.9% |
| Categoría correcta y precisa (% de las evaluables) | 24.6% | 42.1% | 24.5% | 41.6% |
| Filas que podrían llegar a nivel 3 (vertical + forma + género) | 45.6% | 50.9% | 45.4% | 50.8% |
| Filas sin propuesta posible (nivel 0) | 6.9% | 5.5% | 7.3% | 5.7% |
| Se puede llenar desde vacío | 71.3% | 0.3% | 70.9% | 0.3% |
| Se puede afinar | 11.5% | 68.8% | 11.5% | 68.9% |
| Se puede corregir | 2.7% | 5.1% | 2.7% | 5.0% |

## Cómo repetirlo

```bash
# requiere el cache de titulos del pipeline de relleno (enriquecer_externo.py) ya corrido
PYTHONIOENCODING=utf-8 python scripts/validar_categorias.py inventory-consolidado-v10-a-v18.csv reportes/19-validacion-categorias-v18/validacion-consolidado --nombre consolidado --filas validacion-categorias-v18-consolidado-filas.csv
PYTHONIOENCODING=utf-8 python scripts/validar_categorias.py inventory-consolidado-v10-a-v18-relleno.csv reportes/19-validacion-categorias-v18/validacion-relleno --nombre relleno --filas validacion-categorias-v18-relleno-filas.csv
python scripts/generar_reporte_validacion.py reportes/19-validacion-categorias-v18 consolidado=reportes/19-validacion-categorias-v18/validacion-consolidado.json relleno=reportes/19-validacion-categorias-v18/validacion-relleno.json
```

Opciones: `--confianza-min A` (solo matches sin ambigüedad), `--columna contentCategory` (validar la columna original dentro del relleno), `--paises`, `--top-publishers`. Los límites del método están al final de cada reporte.
