# Género normalizado y calidad real de contentTitle: México, Colombia y Chile (consolidado v10 a v18)

**Fuente:** `inventory-consolidado-v10-a-v18.csv` (1,071,840 filas; métricas de v18).
**Generado con:** `scripts/analizar_genero_titulo_paises.py` → `reporte-genero-titulo-paises.json`.

Dos números por columna: **% de filas llenas** (la celda trae algo) y **% de filas con dato de verdad** (lo que trae sirve: un género reconocible o el título de un programa, no un placeholder ni basura técnica).

---

# PARTE A — Género normalizado por país

### México

| País | % de filas | Total filas | % filas llenas | # filas llenas |
|---|---:|---:|---:|---:|
| México | 30.7% | 328,845 | 91.2% | 299,994 |

| Género | Distribución vs # filas llenas | eCPM pond. (>0) |
|---|---:|---:|
| drama | 25.7% | $2.58 |
| comedia | 10.3% | $2.87 |
| documental | 9.8% | $3.16 |
| terror | 9.7% | $2.36 |
| accion | 8.1% | $4.01 |
| thriller | 6.8% | $2.38 |
| entretenimiento | 5.0% | $4.75 |
| romance | 4.7% | $3.08 |
| infantil-familia | 3.8% | $2.21 |
| crimen | 3.7% | $3.54 |

### Colombia

| País | % de filas | Total filas | % filas llenas | # filas llenas |
|---|---:|---:|---:|---:|
| Colombia | 10.7% | 114,223 | 92.0% | 105,126 |

| Género | Distribución vs # filas llenas | eCPM pond. (>0) |
|---|---:|---:|
| drama | 30.5% | $5.03 |
| terror | 12.1% | $6.50 |
| documental | 11.1% | $5.64 |
| comedia | 9.5% | $5.45 |
| accion | 9.3% | $6.93 |
| thriller | 7.6% | $4.53 |
| romance | 6.0% | $3.40 |
| infantil-familia | 5.3% | $5.82 |
| otros/desconocido | 5.2% | $4.35 |
| deportes | 3.9% | $4.21 |

### Chile

| País | % de filas | Total filas | % filas llenas | # filas llenas |
|---|---:|---:|---:|---:|
| Chile | 11.5% | 122,923 | 92.5% | 113,653 |

| Género | Distribución vs # filas llenas | eCPM pond. (>0) |
|---|---:|---:|
| drama | 29.7% | $5.83 |
| terror | 12.4% | $5.89 |
| documental | 12.4% | $6.22 |
| comedia | 10.7% | $6.04 |
| thriller | 9.6% | $6.29 |
| accion | 9.2% | $6.04 |
| romance | 6.3% | $5.85 |
| infantil-familia | 5.3% | $6.90 |
| otros/desconocido | 4.6% | $6.17 |
| entretenimiento | 4.3% | $5.51 |

## Auditoría de contentGenre: lo "lleno" que no es un género

La tabla parte de las filas llenas y les resta lo que trae texto pero no es un género usable tal cual. Significado de cada descuento:

- **prefijo_tecnico** — etiqueta interna de sistema en vez del género limpio: `genre_drama`, `genre_action`.
- **genero_en_formato_sucio** — es un género, pero mal escrito o mal codificado: `soapdrama`, `drama%2cromance`, `western drama`.
- **tipo_de_contenido** — dice el formato y no el género: `tv series`, `feature film`, `videos`, `live`.
- **idioma_o_region** — dice el idioma o la procedencia (`en español`, `foreign`, `hindi & regional`); ese dato va en `contentLanguage`.
- **tema_no_genero** — tema de interés que no es un género de entretenimiento: `outdoors`, `arts`, `business & finance`, `relaxing`.
- **otros_no_reconocidos** — texto que no se pudo mapear a ningún género conocido (`game`, `se`, `bingeworthy`).

| Categoría (% de filas del país) | México | Colombia | Chile |
|---|---:|---:|---:|
| Filas llenas | 91.2% | 92.0% | 92.5% |
| − prefijo_tecnico (`genre_*`) | 2.6% | — | — |
| − genero_en_formato_sucio | 3.9% | 0.4% | 1.6% |
| − tipo_de_contenido | 0.9% | 1.0% | 0.7% |
| − idioma_o_region | 0.2% | 0.3% | 0.1% |
| − tema_no_genero | 0.4% | 0.4% | 0.3% |
| − otros_no_reconocidos | 3.0% | 1.5% | 1.1% |
| **Filas con un género de verdad** | **80.2%** | **88.5%** | **88.7%** |

*Adicionalmente, México 4.3%, Colombia 4.0%, Chile 3.9% de filas "mapeadas parciales" (multi-género donde solo parte de los tokens se reconoce; se cuentan como género de verdad).*

---

# PARTE B — contentTitle: de "la celda trae algo" a "trae un título de verdad"

Las tablas parten de las filas llenas y les restan lo que trae texto pero no es el título del programa. Significado de cada descuento:

- **placeholder** — palabra de relleno genérica (`roku`, `epg`, `vod`) que describe la plataforma o el tipo de contenido, no el programa.
- **slug_tecnico** — nombre interno de archivo o de sistema en vez del título comercial: `devils prey_trailer`.
- **canal_no_programa** — nombre del canal (`las estrellas`, `canal 5`) y no del programa emitido.
- **macro / macro_sin_reemplazar** — plantilla tipo `{{content_title}}` que el sistema del vendedor no sustituyó por el título real.
- **sin_letras** — solo números o símbolos (`41`, `8.0`).
- **muy_corto** — una o dos letras (`n`, `fx`).
- **encoding_roto** — título con caracteres dañados por mala codificación (`catalunya �ber alles!` en vez de "über").

**México — 328,845 filas:**

| Métrica | % filas |
|---|---:|
| Filas llenas | 87.3% |
| − placeholder (`roku`/`epg`/`vod`) | 0.4% |
| − slug_tecnico (`*_trailer`) | 3.0% |
| − canal_no_programa | 1.6% |
| − macro_sin_reemplazar | 0.2% |
| − sin_letras | 0.1% |
| − resto (< 0.05% cada uno) | 0.03% |
| **Filas con un título de verdad** | **81.9%** |

**Colombia — 114,223 filas:**

| Métrica | % filas |
|---|---:|
| Filas llenas | 95.5% |
| − slug_tecnico (`*_trailer`) | 5.1% |
| − canal_no_programa | 0.1% |
| − macro_sin_reemplazar | 0.2% |
| − sin_letras | 0.2% |
| **Filas con un título de verdad** | **90.0%** |

**Chile — 122,923 filas:**

| Métrica | % filas |
|---|---:|
| Filas llenas | 97.1% |
| − slug_tecnico (`*_trailer`) | 4.8% |
| − canal_no_programa | 0.1% |
| − macro_sin_reemplazar | 0.1% |
| − encoding_roto | 0.2% |
| − sin_letras | 0.1% |
| **Filas con un título de verdad** | **91.8%** |

**Tráfico (requests) con título de verdad:**

| País | % requests llenos | % requests con título real |
|---|---:|---:|
| México | 61.0% | 44.9% |
| Colombia | 93.0% | 85.8% |
| Chile | 92.7% | 85.2% |
