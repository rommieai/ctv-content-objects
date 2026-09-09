# Reporte — Género normalizado y calidad real de contentTitle: México, Colombia y Chile (consolidado v10 a v16)

**Fuente:** `inventory-consolidado-v10-a-v16.csv` (810,933 filas; métricas de v16).
**Generado con:** `scripts/analizar_genero_titulo_paises.py` → `reporte-genero-titulo-paises.json`.

Dos análisis desglosados por país: (A) normalización de `contentGenre` con su auditoría de valores que no son un género, y (B) auditoría de `contentTitle` según lo que espera [OpenRTB 2.6](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent). En ambos separamos dos números: el **% de filas no vacías** (la celda trae algo) y el **% de filas con dato de verdad** (lo que trae realmente sirve: un género reconocible o el título de un programa — no un placeholder ni basura técnica). El primero es la cota superior; el segundo, el número honesto.

**Nota del corte v16:** el 28% de las filas del corte llega con el género escrito con mayúscula inicial (`Drama`, `Horror`) y, en una de cada cuatro de esas filas, con género vacío. La normalización absorbe la mayúscula sin problema (`Drama` y `drama` cuentan como el mismo género), pero el vacío nuevo baja el "% de filas no vacías" de género entre 3 y 5 puntos en los tres países. La auditoría de título no se ve afectada: el formato nuevo trae el título igual o mejor poblado.

---

# PARTE A — Género normalizado por país

### México

| País | % de filas | Total filas | % filas no vacías | # filas no vacías |
|---|---:|---:|---:|---:|
| México | 33.0% | 267,688 | 93.9% | 251,472 |

| Género | Distribución vs # filas no vacías | eCPM pond. (>0) |
|---|---:|---:|
| drama | 26.7% | 2.63 |
| comedia | 10.8% | 2.80 |
| terror | 10.2% | 2.02 |
| documental | 9.2% | 2.66 |
| accion | 8.5% | 3.80 |
| thriller | 7.7% | 2.36 |
| romance | 5.2% | 3.29 |
| entretenimiento | 4.4% | **4.76** |
| crimen | 4.0% | 3.45 |
| aventura | 3.9% | 2.96 |

### Colombia

| País | % de filas | Total filas | % filas no vacías | # filas no vacías |
|---|---:|---:|---:|---:|
| Colombia | 10.1% | 82,085 | 95.7% | 78,573 |

| Género | Distribución vs # filas no vacías | eCPM pond. (>0) |
|---|---:|---:|
| drama | 31.3% | 5.55 |
| terror | 12.7% | 7.35 |
| comedia | 10.8% | 7.46 |
| documental | 10.8% | 7.18 |
| accion | 9.8% | **9.01** |
| thriller | 9.2% | 6.11 |
| romance | 7.2% | 4.62 |
| otros/desconocido | 7.0% | 6.33 |
| infantil-familia | 6.3% | 7.80 |
| crimen | 4.4% | 5.86 |

### Chile

| País | % de filas | Total filas | % filas no vacías | # filas no vacías |
|---|---:|---:|---:|---:|
| Chile | 11.1% | 89,663 | 96.9% | 86,853 |

| Género | Distribución vs # filas no vacías | eCPM pond. (>0) |
|---|---:|---:|
| drama | 30.8% | 5.57 |
| terror | 13.1% | 5.76 |
| comedia | 12.1% | 5.64 |
| documental | 12.1% | 5.78 |
| thriller | 11.5% | 5.44 |
| accion | 9.7% | 5.87 |
| romance | 7.5% | 5.64 |
| infantil-familia | 6.3% | 5.55 |
| otros/desconocido | 6.0% | 5.52 |
| aventura | 4.7% | 6.31 |

**Conclusiones — distribución:** la regla "el país fija el precio" cumple siete cortes: en Chile todos los géneros viven en la banda 5.4–6.3 y en México en 2.0–3.8, con el EPG de Roku (entretenimiento, 12.4% del tráfico mexicano) como lo mejor pagado del país a 4.76 y deportes como lo más barato (1.81). **Colombia consolida su nicho premium: anime a 10.94 de eCPM con el 6.9% del tráfico del país, aventura a 9.80 y acción a 9.01** — precios que ningún género alcanza en Chile o México. El drama colombiano, en cambio, es el peor pagado del país (5.55) y el que menos se vende (25% de sus requests). Movimiento del corte: en Colombia terror (7.35) y comedia (7.46) subieron con fuerza (venían de ~7.0) mientras Chile se aplanó aún más (5.4–5.9, venía de 5.8–6.4).

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
| Filas no vacías | 93.9% | 95.7% | 96.9% |
| − prefijo_tecnico (`genre_*`) | 3.2% | — | — |
| − genero_en_formato_sucio | 4.8% | 0.6% | 2.2% |
| − tipo_de_contenido | 1.2% | 1.4% | 0.9% |
| − idioma_o_region | 0.2% | 0.4% | 0.2% |
| − tema_no_genero | 0.4% | 0.4% | 0.3% |
| − otros_no_reconocidos | 3.2% | 1.9% | 1.3% |
| **Filas con un género de verdad** | **81.0%** | **91.1%** | **91.9%** |

Más ~5% de filas "mapeadas parciales" en los tres. El **% de filas con un género de verdad bajó ~1–2pp en los tres países** (MX 81.7 → 81.0, CO 92.8 → 91.1, CL 93.4 → 91.9), pero esta vez no por vocabulario nuevo: los descuentos de basura *bajaron* (en México `genre_*` pasó de 4.5% a 3.2% y `otros_no_reconocidos` de 4.1% a 3.2%); lo que subió es el vacío puro del formato nuevo. En requests, México cae menos (80.5 → 79.3) porque el `genre_*` de TV Azteca, aunque pesa menos en filas, sigue siendo el 5.3% del tráfico del país.

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

**México — 267,688 filas:**

| Métrica | % filas |
|---|---:|
| Filas no vacías | 86.5% |
| − placeholder (`roku`/`epg`/`vod`) | 0.4% |
| − slug_tecnico (`*_trailer`) | 3.1% |
| − canal_no_programa (Televisa lineal) | 1.7% |
| − macro / sin_letras / muy_corto / encoding | 0.3% |
| **Filas con un título de verdad** | **80.9%** |

**Colombia — 82,085 filas:**

| Métrica | % filas |
|---|---:|
| Filas no vacías | 95.4% |
| − slug_tecnico | 5.4% |
| − macro + resto | 0.3% |
| **Filas con un título de verdad** | **89.6%** |

**Chile — 89,663 filas:**

| Métrica | % filas |
|---|---:|
| Filas no vacías | 96.9% |
| − slug_tecnico | 4.9% |
| − encoding_roto | 0.2% |
| − macro + resto | 0.2% |
| **Filas con un título de verdad** | **91.5%** |

**Conclusiones — título:**

1. **En filas, México mejoró (78.3% → 80.9% con título real)** porque el formato nuevo trae el título mejor poblado; **en tráfico, empeoró: 48.2% → 43.4%**, segundo corte seguido bajo el 50%. La explicación sigue siendo la misma y se agrava: los placeholders de Roku ya son el **11.8% de los requests mexicanos** (crecen con el peso de Roku, que subió a 16.6% del tráfico total) y los canales lineales de Televisa/Vidaa suman otro 1.6%.
2. Colombia (85.1%) y Chile (85.2%) estables con deriva leve a la baja, y la fuga de siempre: slugs `*_trailer` (7.2% y 5.8% de requests, respectivamente) — el catálogo de trailers de OTTera/TCL se renueva (`alfaaz_trailer`, `the hanji box_trailer`, `monster_trailer`) pero el formato sucio persiste.
3. El mojibake chileno inamovible en 1.4% de requests (`catalunya über alles!` sigue siendo el título más visto del país).
4. La conclusión operativa se refuerza: **que la celda venga llena no significa que traiga un título usable** — tráfico con título de verdad: Chile 85% ≈ Colombia 85% ≫ **México 43%**.
