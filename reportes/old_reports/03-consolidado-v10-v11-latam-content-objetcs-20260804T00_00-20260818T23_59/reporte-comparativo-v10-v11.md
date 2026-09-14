# Reporte comparativo — v10 vs v11 (Content Objects CTV LATAM)

**Archivos comparados:**
- v10: `inventory-source-alcance-ctv-v10-latam-content-objetcs.csv` (512,000 filas)
- v11: `60333-inventory-source-alcance-ctv-v11-latam-content-objetcs-20260804T00_00-20260818T23_59.csv` (512,000 filas, ventana 4–18 ago 2026)

**Data del cruce:** `reporte-comparativo-v10-v11.json`
**Entregables nuevos:**
- `inventory-merged-v10-v11-sin-duplicados.csv` — unión de ambos, 525,178 registros únicos, con las métricas de cada archivo lado a lado y la columna `presente_en` (ambos / solo_v10 / solo_v11)
- `inventory-consolidado-v10-v11.csv` — el mismo universo en el formato original de 16 columnas (una sola métrica por fila, ver regla más abajo), listo para reutilizar
- `reporte-content-objects-detallado-unificado.md` + `.json` — la tercera tanda de reportes, sobre el universo unificado

---

## Respuesta corta a las preguntas

**¿Comparten filas?** Sí, masivamente. Definiendo la identidad de una fila por su **llave de 14 dimensiones** (todas las columnas menos las dos métricas, Total Requests y eCPM):

| Medida de solapamiento | Resultado |
|---|---:|
| Llaves compartidas entre ambos | **498,822 (97.43% de cada archivo)** |
| Llaves solo en v10 | 13,178 (2.57%) |
| Llaves solo en v11 | 13,178 (2.57%) |
| Filas 100% idénticas (las 16 columnas, métricas incluidas) | 39,929 (7.8%) |
| Universo total combinado | 525,178 llaves únicas |

Y el solapamiento pesa aún más en tráfico: **las llaves compartidas concentran el 99.83% de los requests de v10 y el 99.84% de v11**. Lo que está en un solo archivo es cola marginal (0.17% del volumen).

**¿Son completamente diferentes?** No — son **dos cortes del mismo reporte**, no dos periodos distintos. Tres evidencias:

1. En las llaves compartidas, **el eCPM es idéntico al decimal en el 94.5% de los casos** (471,421 de 498,822). Si fueran quincenas distintas, los precios no coincidirían al centavo.
2. Los requests de las llaves compartidas apenas se mueven: +1.07% neto en v11 (55.6% de llaves suben un poco, 36.4% bajan un poco, 8% quedan exactamente iguales). Es el patrón de un **refresh/actualización de la misma ventana** (v11 recalculado un poco después, con algo más de tráfico atribuido), no de un periodo nuevo.
3. Ambos archivos tienen **exactamente 512,000 filas** y un mínimo de Total Requests de ~29K: el reporte tiene un **límite de exportación de 512K filas** y un umbral de corte. El universo real es mayor (≥525,178) y cada exportación se queda con su top-512K.

**¿Se puede montar un solo CSV sin duplicar?** Sí, y ya está hecho (los dos archivos de arriba). La regla importante: como es la misma ventana, **las métricas NO se pueden sumar** (sería doble conteo). Para el consolidado se usó: si la llave está en ambos → métricas de v11 (el corte más fresco); si solo está en v10 → métricas de v10.

---

## Detalle del cruce

### Consistencia interna

Ninguno de los dos archivos tiene llaves duplicadas internamente (0 en ambos): dentro de cada CSV, la combinación de 14 dimensiones identifica una fila única. Eso valida usar esa llave para el cruce.

### Qué pasa con las métricas en las 498,822 llaves compartidas

| Métrica | Igual | Sube en v11 | Baja en v11 | Neto |
|---|---:|---:|---:|---|
| Total Requests | 40,052 (8.0%) | 277,228 (55.6%) | 181,542 (36.4%) | +4,499 millones (+1.07%) |
| eCPM | **471,421 (94.5%)** | 12,186 (2.4%) | 15,215 (3.1%) | media 0.855 → 0.857 (~0%) |

- Transiciones de monetización: 3,349 llaves pasaron de eCPM 0 a positivo y 2,113 de positivo a 0 — churn normal de subastas en un recálculo; 408,509 siguen en cero y 84,851 siguen positivas.
- El eCPM medio por país en las llaves compartidas es prácticamente idéntico entre archivos (México 0.52→0.50, Argentina 1.25→1.27, Chile 1.50→1.49...; tabla completa en el JSON, clave `ecpm_por_pais_llaves_compartidas`). **No hay ningún movimiento de precio real entre v10 y v11.**

### Qué hay en un archivo y no en el otro (el 2.6% de churn)

Primero la advertencia: como ambos archivos están **truncados a 512,000 filas con umbral de ~29K requests**, la mayor parte de este churn no es inventario que "apareció" o "desapareció" — son combinaciones pequeñas que bailan alrededor del corte de exportación. Con 0.17% del volumen, no cambian ninguna conclusión.

Dicho eso, lo que se ve:

| | Solo en v10 | Solo en v11 |
|---|---|---|
| Llaves | 13,178 | 13,178 |
| Requests | 733M (0.17% de v10) | 673M (0.16% de v11) |
| Top publishers (por filas) | Select Plus (1,998), TCL APAC (1,685), iion (1,272), TCL SS (1,144), OTTera (1,090) | OTTera (4,201), iion (2,345), TCL SS (1,713), TCL APAC (1,135), Select Plus (766) |
| Top países (por filas) | México (4,498), Argentina (1,795), Perú (1,336) | Argentina (3,012), México (2,973), Chile (1,483) |

- **Publishers que solo están en v10 (10, todos pequeños):** AETN, Connatix, GustoTV, Hearst News CTV, NEWRY Global Media, OnDemandKorea, Opera (Admob OB), Outdoor America, VIZIO V-AMPLIFY, Xumo. Son sellers de cola (mayormente perfil US) que quedaron por debajo del corte en v11.
- **Publishers que solo están en v11 (3):** Herring Networks, Kivi via ORTB (Kivi ya estaba vía Springserve — es una ruta nueva, no un publisher nuevo), Volantis Digital Media.
- **219 publishers están en ambos**, y concentran esencialmente todo el volumen.
- Bundles (pageURL): 631 en ambos, 30 solo en v10, 7 solo en v11 — mismo patrón de cola.
- Detalle curioso: en el churn de v11 aparece "Vidaa APAC Hisense Headquarter" (con doble espacio), una variante de nombre de la cuenta "Vidaa" — otra inconsistencia de naming a normalizar.

### Comparación de calidad de metadata v10 vs v11

Los fill rates por columna son **estadísticamente idénticos** entre archivos (ninguna diferencia supera 0.4 puntos):

| Campo | Fill filas v10 | Fill filas v11 |
|---|---:|---:|
| contentGenre | 98.71% | 98.73% |
| contentTitle | 91.54% | 91.74% |
| contentRating | 84.74% | 84.89% |
| contentLanguage | 79.85% | 79.98% |
| contentIsLiveStream | 29.13% | 28.90% |
| contentCategory | 21.98% | 21.99% |
| contentLength | 11.33% | 10.94% |
| contentSeries | 5.52% | 5.33% |

Todos los problemas de calidad detectados persisten sin cambio en ambos: `[-7]` (78% en los dos), hash MD5 vacío, macros `{{CONTENT_SERIES}}`/`{{content_title}}`, buckets 1–8 en length, livestream sin ceros, mojibake en títulos. **Entre v10 y v11 nadie arregló nada** — las prioridades de limpieza de los reportes anteriores siguen vigentes tal cual.

La única diferencia de métrica reseñable: el eCPM máximo pasa de 104.5 (v10) a **200.0 exacto (v11)** — ese 200.0 entra como outlier nuevo y sospechoso en el refresh.

---

## Conclusiones del comparativo

1. **v10 y v11 no son dos quincenas: son dos versiones del mismo corte.** Usar los dos como si fueran periodos distintos (p. ej. para medir tendencia) sería un error — no hay tendencia que medir con estos dos archivos.
2. **Para trabajar, usar el consolidado** (`inventory-consolidado-v10-v11.csv`): recupera las 13,178 combinaciones de v10 que el corte de exportación dejó fuera de v11, quedando con el universo más completo disponible (525,178 filas) y las métricas más frescas.
3. **El límite de exportación de 512K filas es un hallazgo operativo importante**: ningún archivo individual contiene el universo completo. Si se pueden pedir exportaciones segmentadas (por país o por publisher), se recuperaría la cola que hoy queda cortada.
4. El churn de sellers es cosmético (0.17% del volumen), pero confirma que la cola del reporte es inestable entre cortes: cualquier análisis de "publishers pequeños" debería hacerse sobre el consolidado, no sobre un archivo suelto.

---

# La tercera tanda (universo unificado)

El análisis detallado completo del universo consolidado (525,178 filas) está en:
- **`reporte-content-objects-detallado-unificado.md`** — reporte
- **`reporte-content-objects-detallado-unificado.json`** — distribuciones completas por columna y por país, mismo formato que las tandas anteriores
