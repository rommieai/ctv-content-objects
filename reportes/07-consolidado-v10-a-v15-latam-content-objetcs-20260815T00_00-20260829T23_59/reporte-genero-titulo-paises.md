# Reporte — Género normalizado y calidad real de contentTitle: México, Colombia y Chile (consolidado v10 a v15)

**Fuente:** `inventory-consolidado-v10-a-v15.csv` (648,589 filas; métricas de v15).
**Generado con:** `scripts/analizar_genero_titulo_paises.py` → `reporte-genero-titulo-paises.json`.

Dos análisis desglosados por país: (A) normalización de `contentGenre` con su auditoría de valores que no son un género, y (B) auditoría de `contentTitle` según lo que espera [OpenRTB 2.6](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent). En ambos separamos dos números: el **% de filas no vacías** (la celda trae algo) y el **% de filas con dato de verdad** (lo que trae realmente sirve: un género reconocible o el título de un programa — no un placeholder ni basura técnica). El primero es la cota superior; el segundo, el número honesto.

---

# PARTE A — Género normalizado por país

### México

| País | Total filas | % de filas | # filas no vacías |
|---|---:|---:|---:|
| México | 193,264 | 29.8% | 191,462 |

| Género | Distribución vs # filas no vacías | eCPM pond. (>0) |
|---|---:|---:|
| drama | 25.2% | 2.43 |
| comedia | 11.8% | 2.81 |
| terror | 9.4% | 2.00 |
| documental | 9.2% | 2.46 |
| accion | 9.0% | 3.70 |
| thriller | 8.9% | 2.31 |
| romance | 6.1% | 3.38 |
| infantil-familia | 4.8% | 2.15 |
| crimen | 4.7% | 3.19 |
| entretenimiento | 4.7% | **4.92** |

### Colombia

| País | Total filas | % de filas | # filas no vacías |
|---|---:|---:|---:|
| Colombia | 63,163 | 9.7% | 62,203 |

| Género | Distribución vs # filas no vacías | eCPM pond. (>0) |
|---|---:|---:|
| drama | 31.3% | 5.26 |
| comedia | 12.5% | 7.03 |
| terror | 12.0% | 7.04 |
| documental | 11.6% | 6.13 |
| thriller | 10.8% | 5.87 |
| accion | 10.2% | **9.10** |
| romance | 8.2% | 4.50 |
| infantil-familia | 7.5% | 7.19 |
| musica | 5.3% | 3.80 |
| crimen | 5.2% | 5.61 |

### Chile

| País | Total filas | % de filas | # filas no vacías |
|---|---:|---:|---:|
| Chile | 70,326 | 10.8% | 69,946 |

| Género | Distribución vs # filas no vacías | eCPM pond. (>0) |
|---|---:|---:|
| drama | 30.5% | 5.94 |
| comedia | 13.6% | 5.92 |
| thriller | 13.5% | 5.83 |
| documental | 13.3% | 6.39 |
| terror | 12.6% | 6.06 |
| accion | 10.1% | 6.29 |
| romance | 8.5% | 5.99 |
| infantil-familia | 7.5% | 5.71 |
| musica | 5.7% | 5.76 |
| crimen | 5.3% | 5.63 |

**Conclusiones — distribución:** la regla "el país fija el precio" cumple seis cortes, y **Colombia consolida su nicho premium: anime a 11.04 de eCPM con el 8.4% del tráfico del país, aventura a 10.18 (7.7% del tráfico) y acción a 9.10** — precios que ningún género alcanza en Chile o México. La recuperación colombiana sigue concentrada, no es pareja. Chile sigue plano (5.8–6.4) y en México el patrón de precio bajo se acentúa: el EPG de Roku (12.2% del tráfico) es lo mejor pagado del país a 4.92, mientras deportes queda en 2.18, lo más barato.

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
| Filas no vacías | 99.1% | 98.5% | 99.5% |
| − prefijo_tecnico (`genre_*`) | 4.5% | — | — |
| − genero_en_formato_sucio | 6.5% | 0.8% | 2.9% |
| − tipo_de_contenido | 1.6% | 1.8% | 1.2% |
| − idioma_o_region | 0.3% | 0.5% | 0.2% |
| − tema_no_genero | 0.4% | 0.4% | 0.3% |
| − otros_no_reconocidos | 4.1% | 2.2% | 1.5% |
| **Filas con un género de verdad** | **81.7%** | **92.8%** | **93.4%** |

Más ~7% de filas "mapeadas parciales" en los tres. **En los tres países el tráfico con un género de verdad retrocedió 1–2pp** (MX 82.1 → 80.5, CO 88.9 → 86.9, CL 92.3 → 90.4): el vocabulario que entró con v15 cayó sobre todo en `otros_no_reconocidos` — mismo síntoma que el 89.3% global de filas mapeables (venía de 91.9%). El `genre_*` de TV Azteca volvió a subir de peso en México (6.3% de requests) con el rebote del publisher.

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

**México — 193,264 filas:**

| Métrica | % filas |
|---|---:|
| Filas no vacías | 83.7% |
| − placeholder (`roku`/`epg`/`vod`) | 0.4% |
| − slug_tecnico (`*_trailer`) | 2.6% |
| − canal_no_programa (Televisa lineal) | 2.1% |
| − macro / sin_letras / muy_corto / encoding | 0.3% |
| **Filas con un título de verdad** | **78.3%** |

**Colombia — 63,163 filas:**

| Métrica | % filas |
|---|---:|
| Filas no vacías | 94.9% |
| − slug_tecnico | 4.7% |
| − macro + resto | 0.4% |
| **Filas con un título de verdad** | **89.8%** |

**Chile — 70,326 filas:**

| Métrica | % filas |
|---|---:|
| Filas no vacías | 96.7% |
| − slug_tecnico | 4.3% |
| − encoding_roto | 0.2% |
| − macro + resto | 0.2% |
| **Filas con un título de verdad** | **91.9%** |

**Conclusiones — título:**

1. **México cayó por primera vez bajo el 50% de tráfico con título real (48.2%)**, tras cinco cortes clavado en ~50–51%. La explicación está repartida entre los placeholders de Roku (11.2% de los requests, que crecen con el peso de Roku) y los canales lineales de Televisa/Vidaa (2.1% de filas — "golden edge" y "golden multiplex" ya en el top del país).
2. Colombia (86.2%) y Chile (86.9%) estables con deriva leve a la baja, y la fuga de siempre: slugs `*_trailer` (6–7% de requests) — el catálogo de trailers se renueva (`monster_trailer`, `the hanji box_trailer`) pero el formato sucio persiste.
3. El mojibake chileno inamovible en 1.5% de requests (`catalunya über alles!` sigue siendo el título más visto del país).
4. La conclusión operativa se refuerza: **que la celda venga llena no significa que traiga un título usable** — tráfico con título de verdad: Chile 87% ≈ Colombia 86% ≫ **México 48%**.
