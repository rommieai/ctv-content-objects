# Género normalizado y calidad real de contentTitle: México, Colombia y Chile (consolidado v10 a v17)

**Fuente:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas; métricas de v17).
**Generado con:** `scripts/analizar_genero_titulo_paises.py` → `reporte-genero-titulo-paises.json`.

Dos números por columna: **% de filas no vacías** (la celda trae algo) y **% de filas con dato de verdad** (lo que trae sirve: un género reconocible o el título de un programa, no un placeholder ni basura técnica).

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
| entretenimiento | 4.8% | 4.68 |
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
| accion | 9.4% | 9.09 |
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

## Auditoría de contentGenre: lo "lleno" que no es un género

La tabla parte de las filas no vacías y les resta lo que trae texto pero no es un género usable tal cual. Significado de cada descuento:

- **prefijo_tecnico** — etiqueta interna de sistema en vez del género limpio: `genre_drama`, `genre_action`.
- **genero_en_formato_sucio** — es un género, pero mal escrito o mal codificado: `soapdrama`, `drama%2cromance`, `western drama`.
- **tipo_de_contenido** — dice el formato y no el género: `tv series`, `feature film`, `videos`, `live`.
- **idioma_o_region** — dice el idioma o la procedencia (`en español`, `foreign`, `hindi & regional`); ese dato va en `contentLanguage`.
- **tema_no_genero** — tema de interés que no es un género de entretenimiento: `outdoors`, `arts`, `business & finance`, `relaxing`.
- **otros_no_reconocidos** — texto que no se pudo mapear a ningún género conocido (`game`, `se`, `bingeworthy`).

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

---

# PARTE B — contentTitle: de "la celda trae algo" a "trae un título de verdad"

Las tablas parten de las filas no vacías y les restan lo que trae texto pero no es el título del programa. Significado de cada descuento:

- **placeholder** — palabra de relleno genérica (`roku`, `epg`, `vod`) que describe la plataforma o el tipo de contenido, no el programa.
- **slug_tecnico** — nombre interno de archivo o de sistema en vez del título comercial: `devils prey_trailer`.
- **canal_no_programa** — nombre del canal (`las estrellas`, `canal 5`) y no del programa emitido.
- **macro / macro_sin_reemplazar** — plantilla tipo `{{content_title}}` que el sistema del vendedor no sustituyó por el título real.
- **sin_letras** — solo números o símbolos (`41`, `8.0`).
- **muy_corto** — una o dos letras (`n`, `fx`).
- **encoding_roto** — título con caracteres dañados por mala codificación (`catalunya �ber alles!` en vez de "über").

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

**Tráfico (requests) con título de verdad:**

| País | % requests con título real |
|---|---:|
| México | 43.6% |
| Colombia | 85.5% |
| Chile | 84.9% |
