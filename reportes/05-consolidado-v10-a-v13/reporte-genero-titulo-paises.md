# Reporte — Género normalizado y calidad real de contentTitle: México, Colombia y Chile (consolidado v10 a v13)

**Fuente:** `inventory-consolidado-v10-a-v13.csv` (579,679 filas; métricas de v13).
**Generado con:** `scripts/analizar_genero_titulo_paises.py` → `reporte-genero-titulo-paises.json` (distribuciones completas y ejemplos por categoría).

Dos análisis desglosados por país: (A) la normalización de `contentGenre` con su auditoría de valores que no son un género, y (B) la auditoría de `contentTitle` — dentro de lo "lleno", cuánto no es realmente un título según [OpenRTB 2.6](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent). En ambos campos: el fill nominal es una cota superior; aquí se calcula el **fill efectivo**.

---

# PARTE A — Género normalizado por país

## Distribución (top por % de requests del país; multi-etiqueta)

### México

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 25.1% | 27.4% | 2.82 | 52.2% |
| comedia | 11.8% | 11.6% | 3.25 | 56.1% |
| entretenimiento (genérico) | 4.7% | **11.3%** | **5.32** | **79.8%** |
| thriller | 9.1% | 9.9% | 3.11 | 41.6% |
| terror | 9.6% | 9.5% | 2.85 | 40.8% |
| accion | 9.1% | 8.5% | 4.37 | 50.7% |
| romance | 6.2% | 6.9% | 3.85 | 46.0% |
| documental | 9.4% | 5.5% | 3.28 | 37.3% |

### Colombia

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 30.9% | 31.4% | 4.16 | 15.7% |
| terror | 11.7% | 15.3% | 4.68 | 15.6% |
| accion | 10.0% | 14.5% | **8.65** | 27.5% |
| thriller | 10.6% | 14.0% | 4.10 | 20.2% |
| comedia | 12.4% | 12.3% | 5.64 | 19.3% |
| infantil-familia | 7.3% | 11.3% | 6.26 | **33.4%** |
| documental | 11.6% | 9.7% | 3.62 | 15.4% |
| otros/desconocido | 8.7% | 8.2% | 3.11 | 12.8% |

### Chile

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 31.2% | **39.5%** | 6.48 | 39.0% |
| thriller | 13.9% | 18.9% | 6.36 | 38.9% |
| terror | 12.8% | 16.8% | 6.57 | 37.9% |
| comedia | 14.0% | 15.2% | 6.49 | 38.1% |
| romance | 8.8% | 11.3% | 6.44 | 39.4% |
| documental | 13.8% | 10.5% | 7.12 | 36.2% |
| accion | 10.3% | 10.3% | 6.99 | 38.1% |
| infantil-familia | 7.5% | 6.6% | 6.69 | **45.3%** |

**Conclusiones — distribución:** se sostiene la regla de los cortes anteriores — el país fija el precio, el género fija la vendibilidad — con dos novedades del recálculo v13: **en Colombia la acción saltó a 8.65 de eCPM** (el género más caro de los tres países, señal de la demanda nueva que le subió el precio al mercado) y el kids/familia colombiano pesa 11.3% del tráfico con la mejor tasa local (33%). Chile sigue plano (6.4–7.1: prima de mercado, no de contenido) y en México el EPG de Roku ("entretenimiento genérico") sigue siendo el mejor negocio: 11.3% del tráfico, 80% monetizado.

## Auditoría de contentGenre: lo "lleno" que no es un género

| Categoría | MX filas | MX reqs | CO filas | CO reqs | CL filas | CL reqs |
|---|---:|---:|---:|---:|---:|---:|
| Fill útil (nominal) | 99.0% | 94.0% | 98.5% | 94.9% | 99.5% | 97.6% |
| − prefijo_tecnico (`genre_*`) | 5.0% | **7.5%** | — | — | — | — |
| − genero_en_formato_sucio | 5.7% | 3.5% | 0.7% | 0.9% | 1.2% | 1.0% |
| − tipo_de_contenido | 1.3% | 0.3% | 1.8% | 0.6% | 1.1% | 0.5% |
| − idioma_o_region | 0.3% | 0.1% | 0.5% | 0.2% | 0.2% | 0.1% |
| − tema_no_genero | 0.3% | 0.3% | 0.4% | 0.8% | 0.3% | 0.6% |
| − otros_no_reconocidos | 3.6% | 1.9% | 2.0% | 2.5% | 1.3% | 2.2% |
| **Fill efectivo (género real)** | **82.7%** | **80.4%** | **93.1%** | **89.9%** | **95.4%** | **93.2%** |

Más un ~7% de filas "mapeadas parciales" en los tres países (género válido + tokens basura). Sin cambios de diagnóstico: la fuga mexicana sigue siendo el prefijo `genre_*` de TV Azteca (7.5% del tráfico del país, inexistente en CO/CL), y la categoría recuperable ("género en formato sucio": `western drama`, `drama%2cromance`) sigue siendo la segunda.

---

# PARTE B — contentTitle: del fill nominal al fill efectivo

Mismas 8 categorías de sospecha de los cortes anteriores (placeholder, canal_no_programa, slug_tecnico, macro, encoding_roto, sin_letras, muy_corto, hash).

**México:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil (nominal) | 83.0% | 65.6% |
| − placeholder (`roku`/`epg`/`vod`) | 0.4% | **10.4%** |
| − slug_tecnico (`*_trailer`) | 2.7% | 3.2% |
| − canal_no_programa (Televisa lineal) | 1.7% | 1.1% |
| − macro / sin_letras / muy_corto / encoding | 0.3% | 0.7% |
| **Fill efectivo (título real)** | **77.8%** | **50.2%** |

**Colombia:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil | 95.0% | 95.3% |
| − slug_tecnico | 4.9% | **7.4%** |
| − macro + resto | 0.4% | 0.2% |
| **Fill efectivo** | **89.7%** | **87.7%** |

**Chile:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil | 96.7% | 96.4% |
| − slug_tecnico | 4.2% | 6.2% |
| − encoding_roto | 0.2% | **1.7%** |
| − macro + resto | 0.2% | 0.2% |
| **Fill efectivo** | **92.0%** | **88.4%** |

**Conclusiones — título:**

1. **México sigue con la mitad del tráfico sin título utilizable (50.2%)** — y el hueco de los placeholders de Roku incluso creció un poco (10.4% de los requests del país). Cuatro cortes con el mismo número: esto no es ruido de ventana, es estructural.
2. Colombia (87.7%) y Chile (88.4%) siguen sanos, con la misma única fuga: los slugs `*_trailer` (6–7% de los requests), un fix de formato en una sola fuente.
3. El mojibake chileno se mantiene en 1.7% de los requests (el catálogo catalán de alto volumen).
4. Regla que ya quedó demostrada con cuatro versiones del reporte: **fill nominal ≠ usabilidad** — para título, la utilidad real por requests es Chile 88% ≈ Colombia 88% ≫ México 50%.
