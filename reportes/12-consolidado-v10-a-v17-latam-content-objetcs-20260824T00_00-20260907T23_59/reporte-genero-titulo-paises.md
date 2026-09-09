# Reporte — Género normalizado y calidad real de contentTitle: México, Colombia y Chile (consolidado v10 a v17)

**Fuente:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas; métricas de v17).
**Generado con:** `scripts/analizar_genero_titulo_paises.py` → `reporte-genero-titulo-paises.json`.

Dos análisis desglosados por país: (A) normalización de `contentGenre` con su auditoría de valores que no son un género, y (B) auditoría de `contentTitle` según lo que espera [OpenRTB 2.6](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent). En ambos separamos dos números: el **% de filas no vacías** (la celda trae algo) y el **% de filas con dato de verdad** (lo que trae realmente sirve: un género reconocible o el título de un programa — no un placeholder ni basura técnica). El primero es la cota superior; el segundo, el número honesto.

**Nota del corte v17:** la escritura nueva del reporte (género con mayúscula inicial) ya es mayoritaria (54% de las filas de v17) y trae género vacío en una de cada nueve filas. La normalización absorbe la mayúscula (`Drama` = `drama`), pero el vacío baja el "% de filas no vacías" de género otros 2 puntos por país respecto a v16 (y 5–7 respecto a v15). La auditoría de título no se ve afectada.

---

# PARTE A — Género normalizado por país

### México

| País | % de filas | Total filas | % filas no vacías | # filas no vacías |
|---|---:|---:|---:|---:|
| México | 31.7% | 304,329 | 92.1% | 280,285 |

| Género | Distribución vs # filas no vacías | eCPM pond. (>0) |
|---|---:|---:|
| drama | 26.0% | 2.60 |
| comedia | 10.5% | 2.87 |
| terror | 9.9% | 2.17 |
| documental | 9.6% | 2.84 |
| accion | 8.2% | 3.85 |
| thriller | 7.1% | 2.30 |
| romance | 4.9% | 3.24 |
| entretenimiento | 4.8% | **4.68** |
| infantil-familia | 3.9% | 2.24 |
| crimen | 3.8% | 3.01 |

### Colombia

| País | % de filas | Total filas | % filas no vacías | # filas no vacías |
|---|---:|---:|---:|---:|
| Colombia | 10.6% | 101,514 | 93.0% | 94,434 |

| Género | Distribución vs # filas no vacías | eCPM pond. (>0) |
|---|---:|---:|
| drama | 31.3% | 5.66 |
| terror | 12.4% | 7.52 |
| documental | 10.9% | 7.40 |
| comedia | 9.9% | 7.70 |
| accion | 9.4% | **9.09** |
| thriller | 8.2% | 6.32 |
| romance | 6.5% | 4.40 |
| otros/desconocido | 5.8% | 7.05 |
| infantil-familia | 5.6% | 8.41 |
| deportes | 4.0% | 3.63 |

### Chile

| País | % de filas | Total filas | % filas no vacías | # filas no vacías |
|---|---:|---:|---:|---:|
| Chile | 11.2% | 107,269 | 94.6% | 101,463 |

| Género | Distribución vs # filas no vacías | eCPM pond. (>0) |
|---|---:|---:|
| drama | 30.7% | 5.91 |
| terror | 13.0% | 6.07 |
| documental | 11.8% | 6.13 |
| comedia | 11.2% | 5.87 |
| thriller | 10.4% | 5.80 |
| accion | 9.5% | 6.22 |
| romance | 6.9% | 5.78 |
| infantil-familia | 5.7% | 6.00 |
| otros/desconocido | 5.1% | 5.76 |
| aventura | 4.3% | 6.76 |

**Conclusiones — distribución:** la regla "el país fija el precio" cumple ocho cortes: en Chile todos los géneros viven en la banda 5.6–6.8 (con un leve rebote general respecto a v16) y en México en 2.2–3.9, con el EPG de Roku (entretenimiento, 12.1% del tráfico mexicano) como lo mejor pagado del país a 4.68 y deportes como lo más barato (1.68). **Colombia mantiene su nicho premium — anime 10.27, aventura 9.56, acción 9.09, infantil-familia 8.41 — pero anime se enfrió** (10.94 → 10.27) y pesa menos en el tráfico del país (6.9% → 4.1%). El drama colombiano sigue siendo el peor pagado (5.66) y el que menos se vende (20% de sus requests). Novedad de México: infantil-familia (2.24) es ahora de lo más barato del país, por debajo de terror.

## Auditoría de contentGenre: lo "lleno" que no es un género

La tabla parte de las filas no vacías y les resta lo que trae texto pero **no es un género usable tal cual**. Qué significa cada descuento:

- **prefijo_tecnico** — el vendedor manda su etiqueta interna de sistema en vez del género limpio: `genre_drama`, `genre_action` (marca de la casa de TV Azteca). El género real está ahí, pero envuelto en formato técnico.
- **genero_en_formato_sucio** — sí es un género, pero mal escrito o mal codificado: palabras pegadas (`soapdrama`), codificación de URL sin resolver (`drama%2cromance`, que debía ser "drama, romance") o combos no estándar (`western drama`). También recuperable con limpieza.
- **tipo_de_contenido** — dice el *formato* y no el género: `tv series`, `feature film`, `videos`, `live`. Saber que es una serie no dice si es comedia o terror.
- **idioma_o_region** — dice el idioma o la procedencia (`en español`, `foreign`, `hindi & regional`): ese dato va en `contentLanguage`, no aquí.
- **tema_no_genero** — un tema de interés que no es un género de entretenimiento: `outdoors`, `arts`, `business & finance`, `relaxing`.
- **otros_no_reconocidos** — texto que no se pudo mapear a ningún género conocido (`game`, `se`, `bingeworthy`): vocabulario propio de cada app.

Los dos primeros son recuperables normalizando (el género real viene, mal empacado); el resto es el campo usado para otra cosa. Nada de esto le sirve tal cual a un comprador que quiera segmentar por género.

| Categoría (% de filas del país) | México | Colombia | Chile |
|---|---:|---:|---:|
| Filas no vacías | 92.1% | 93.0% | 94.6% |
| − prefijo_tecnico (`genre_*`) | 2.8% | — | — |
| − genero_en_formato_sucio | 4.2% | 0.5% | 1.9% |
| − tipo_de_contenido | 1.0% | 1.1% | 0.8% |
| − idioma_o_region | 0.2% | 0.3% | 0.2% |
| − tema_no_genero | 0.4% | 0.4% | 0.3% |
| − otros_no_reconocidos | 3.0% | 1.6% | 1.2% |
| **Filas con un género de verdad** | **80.4%** | **89.1%** | **90.3%** |

Más ~4.5% de filas "mapeadas parciales" en los tres. El **% de filas con un género de verdad bajó otro punto o dos** (MX 81.0 → 80.4, CO 91.1 → 89.1, CL 91.9 → 90.3) y, como en v16, la causa es el vacío del formato nuevo, no la basura: todos los descuentos bajan en proporción. Vocabulario nuevo a vigilar: `Soap-Opera` (424 filas en México, ya el primer "no reconocido" del país) y `Outdoors`/`Business & Finance` con mayúscula — la escritura nueva también capitaliza los temas; conviene añadir `soap-opera` → telenovela al diccionario en la próxima tanda.

---

# PARTE B — contentTitle: de "la celda trae algo" a "trae un título de verdad"

Las tablas parten de las filas no vacías y les restan todo lo que técnicamente trae texto pero **no es el título del programa que alguien está viendo**. Qué significa cada descuento:

- **placeholder** — la celda trae una palabra de relleno genérica (`roku`, `epg`, `vod`) que describe la plataforma o el tipo de contenido, no el programa. Es como si en "título del libro" alguien escribiera "libro".
- **slug_tecnico** — llega el nombre interno de archivo o de sistema en vez del título comercial: `devils prey_trailer`, con guiones bajos y sufijos técnicos. Delata que el vendedor manda su identificador de catálogo, no el título.
- **canal_no_programa** — trae el nombre del canal (`las estrellas`, `canal 5`) y no el del programa emitido. Sirve para saber dónde, pero no qué se está viendo, que es lo que pide OpenRTB.
- **macro / macro_sin_reemplazar** — el sistema del vendedor debía sustituir una plantilla tipo `{{content_title}}` por el título real y falló: llega la plantilla literal, escrita tal cual.
- **sin_letras** — solo números o símbolos (`41`, `8.0`): no identifican ningún contenido.
- **muy_corto** — una o dos letras (`n`, `fx`): imposible saber qué programa es.
- **encoding_roto** — sí hay un título, pero llegó con los caracteres dañados por una mala codificación de texto (`catalunya �ber alles!` en vez de "über"): un sistema intermedio lo corrompió.

Nada de esto cuenta como título útil porque un comprador (o un algoritmo de brand safety) no puede saber con eso qué contenido está comprando.

**México — 304,329 filas:**

| Métrica | % filas |
|---|---:|
| Filas no vacías | 87.0% |
| − placeholder (`roku`/`epg`/`vod`) | 0.4% |
| − slug_tecnico (`*_trailer`) | 3.1% |
| − canal_no_programa (Televisa lineal) | 1.7% |
| − macro / sin_letras / muy_corto / encoding | 0.3% |
| **Filas con un título de verdad** | **81.6%** |

**Colombia — 101,514 filas:**

| Métrica | % filas |
|---|---:|
| Filas no vacías | 95.6% |
| − slug_tecnico | 5.3% |
| − macro + resto | 0.3% |
| **Filas con un título de verdad** | **89.9%** |

**Chile — 107,269 filas:**

| Métrica | % filas |
|---|---:|
| Filas no vacías | 97.1% |
| − slug_tecnico | 5.0% |
| − encoding_roto | 0.2% |
| − macro + resto | 0.2% |
| **Filas con un título de verdad** | **91.5%** |

**Conclusiones — título:**

1. **México estable en lo malo: 43.6% del tráfico con título real** (43.4% en v16), tercer corte seguido bajo el 50%. En filas sigue mejorando (80.9% → 81.6%) porque la escritura nueva trae el título bien poblado; el problema es de tráfico, no de catálogo: los placeholders de Roku son el **11.6% de los requests mexicanos** y, con Roku ya #1 del dataset, no van a bajar solos. Los canales lineales de Televisa/Vidaa suman otro 1.6%.
2. Colombia (85.5%) y Chile (84.9%) estables, con la fuga de siempre: slugs `*_trailer` (7.2% y 6.0% de requests) — el catálogo de trailers de OTTera/TCL se renueva pero el formato sucio persiste. En Colombia la macro `{{content_title}}` ya es el cuarto "título" más frecuente del país.
3. El mojibake chileno inamovible en 1.4% de requests (`catalunya über alles!` sigue siendo el título más visto del país, ocho cortes seguidos).
4. La conclusión operativa se refuerza: **que la celda venga llena no significa que traiga un título usable** — tráfico con título de verdad: Colombia 85% ≈ Chile 85% ≫ **México 44%**.
