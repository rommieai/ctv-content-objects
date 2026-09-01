# Reporte — Género normalizado y calidad real de contentTitle: México, Colombia y Chile (consolidado v10 a v14)

**Fuente:** `inventory-consolidado-v10-a-v14.csv` (607,878 filas; métricas de v14).
**Generado con:** `scripts/analizar_genero_titulo_paises.py` → `reporte-genero-titulo-paises.json`.

Dos análisis desglosados por país: (A) normalización de `contentGenre` con su auditoría de valores que no son un género, y (B) auditoría de `contentTitle` según lo que espera [OpenRTB 2.6](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent). En ambos: fill nominal como cota superior, **fill efectivo** como número honesto.

---

# PARTE A — Género normalizado por país

## Distribución (top por % de requests del país; multi-etiqueta)

### México

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 25.1% | 28.3% | 2.58 | 53.7% |
| comedia | 11.7% | 11.9% | 2.99 | 58.3% |
| entretenimiento | 4.6% | **11.6%** | **5.23** | **79.2%** |
| thriller | 8.8% | 9.7% | 2.74 | 39.5% |
| terror | 9.3% | 9.3% | 2.43 | 39.4% |
| accion | 8.9% | 8.4% | 4.17 | 49.7% |
| romance | 6.1% | 6.8% | 3.57 | 45.6% |
| documental | 9.2% | 5.4% | 2.73 | 34.8% |

### Colombia

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 30.9% | 30.2% | 4.82 | 18.9% |
| accion | 10.0% | 14.9% | **9.04** | 30.4% |
| terror | 11.7% | 14.5% | 6.05 | 19.5% |
| thriller | 10.6% | 13.3% | 5.22 | 25.3% |
| comedia | 12.3% | 12.1% | 6.45 | 22.5% |
| infantil-familia | 7.3% | 11.7% | 6.66 | 36.5% |
| documental | 11.5% | 9.2% | 4.60 | 18.6% |
| anime | 2.2% | **8.2%** | **11.00** | **37.3%** |

### Chile

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 30.7% | **39.0%** | 6.18 | 39.9% |
| thriller | 13.6% | 18.6% | 6.04 | 39.7% |
| terror | 12.6% | 16.6% | 6.27 | 38.8% |
| comedia | 13.8% | 15.1% | 6.17 | 38.5% |
| romance | 8.6% | 11.2% | 6.21 | 39.6% |
| accion | 10.2% | 10.2% | 6.81 | 38.5% |
| documental | 13.6% | 10.2% | 6.69 | 36.7% |
| infantil-familia | 7.5% | 6.5% | 6.26 | **45.9%** |

**Conclusiones — distribución:** la regla "el país fija el precio, el género la vendibilidad" cumple cinco cortes, pero **Colombia se está volviendo la excepción interesante: su anime pasó a 11.0 de eCPM con el 8.2% del tráfico del país** (y acción a 9.04) — precios de nicho superiores a cualquier cosa en Chile o México. La recuperación colombiana no es pareja: está concentrada en anime, acción y kids. Chile sigue plano (6.0–6.8) y en México nada le gana al EPG de Roku (11.6% del tráfico, 79% monetizado).

## Auditoría de contentGenre: lo "lleno" que no es un género

| Categoría | MX filas | MX reqs | CO filas | CO reqs | CL filas | CL reqs |
|---|---:|---:|---:|---:|---:|---:|
| Fill útil (nominal) | 99.1% | 94.5% | 98.5% | 94.3% | 99.5% | 97.1% |
| − prefijo_tecnico (`genre_*`) | 4.7% | **6.0%** | — | — | — | — |
| − genero_en_formato_sucio | 6.2% | 4.0% | 0.7% | 1.0% | 2.1% | 1.3% |
| − tipo_de_contenido | 1.4% | 0.3% | 1.8% | 0.6% | 1.2% | 0.5% |
| − idioma_o_region | 0.3% | 0.1% | 0.5% | 0.2% | 0.2% | 0.1% |
| − tema_no_genero | 0.4% | 0.3% | 0.4% | 0.8% | 0.2% | 0.7% |
| − otros_no_reconocidos | 4.0% | 1.7% | 2.1% | 2.8% | 1.3% | 2.3% |
| **Fill efectivo (género real)** | **82.0%** | **82.1%** | **92.9%** | **88.9%** | **94.5%** | **92.3%** |

Más ~7% de filas "mapeadas parciales" en los tres. El género efectivo mexicano por requests mejoró un poco (78.7% → 82.1%) — en parte porque el peso relativo de TV Azteca (el emisor del `genre_*`) viene cayendo. La fuga recuperable ("formato sucio": `western drama`, `drama%2cromance`) creció levemente en México (4.0% de requests) por el crecimiento de Vidaa, que usa ese vocabulario.

---

# PARTE B — contentTitle: del fill nominal al fill efectivo

**México:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil (nominal) | 83.0% | 67.1% |
| − placeholder (`roku`/`epg`/`vod`) | 0.4% | **10.7%** |
| − slug_tecnico (`*_trailer`) | 2.6% | 3.2% |
| − canal_no_programa (Televisa lineal) | 2.1% | 1.5% |
| − macro / sin_letras / muy_corto / encoding | 0.3% | 0.9% |
| **Fill efectivo (título real)** | **77.6%** | **50.9%** |

**Colombia:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil | 94.9% | 94.8% |
| − slug_tecnico | 4.8% | **7.4%** |
| − macro + resto | 0.4% | 0.2% |
| **Fill efectivo** | **89.7%** | **87.2%** |

**Chile:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil | 96.7% | 95.8% |
| − slug_tecnico | 4.3% | 6.1% |
| − encoding_roto | 0.2% | **1.7%** |
| − macro + resto | 0.2% | 0.2% |
| **Fill efectivo** | **91.9%** | **87.8%** |

**Conclusiones — título:**

1. **México cumple cinco cortes clavado en ~50% de tráfico con título real** (50.9%). Los placeholders de Roku suben marginalmente (10.7% de los requests) y los nombres de canal de Televisa crecieron a 2.1% de filas (el catálogo de canales lineales de ViX/Vidaa se expande — "golden edge" entró al top).
2. Colombia (87.2%) y Chile (87.8%) estables, con la fuga de siempre: slugs `*_trailer` (6–7% de requests) — apareció `monster_trailer` en el top chileno, el catálogo de trailers se renueva pero el formato sucio persiste.
3. El mojibake chileno inamovible en 1.7% de requests.
4. La conclusión operativa no cambia: **fill nominal ≠ usabilidad** — título real por requests: Chile 88% ≈ Colombia 87% ≫ México 51%.
