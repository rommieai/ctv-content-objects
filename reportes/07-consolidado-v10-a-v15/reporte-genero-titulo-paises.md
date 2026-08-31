# Reporte — Género normalizado y calidad real de contentTitle: México, Colombia y Chile (consolidado v10 a v15)

**Fuente:** `inventory-consolidado-v10-a-v15.csv` (648,589 filas; métricas de v15).
**Generado con:** `scripts/analizar_genero_titulo_paises.py` → `reporte-genero-titulo-paises.json`.

Dos análisis desglosados por país: (A) normalización de `contentGenre` con su auditoría de valores que no son un género, y (B) auditoría de `contentTitle` según lo que espera [OpenRTB 2.6](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent). En ambos: fill nominal como cota superior, **fill efectivo** como número honesto.

---

# PARTE A — Género normalizado por país

## Distribución (top por % de requests del país; multi-etiqueta)

### México

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 24.9% | 27.3% | 2.43 | 54.2% |
| entretenimiento (genérico) | 4.6% | **12.2%** | **4.92** | **76.1%** |
| comedia | 11.7% | 11.7% | 2.81 | 58.2% |
| thriller | 8.8% | 8.8% | 2.31 | 39.2% |
| terror | 9.3% | 8.4% | 2.00 | 38.0% |
| accion | 8.9% | 8.2% | 3.70 | 46.7% |
| romance | 6.0% | 6.5% | 3.38 | 45.2% |
| deportes | 3.8% | 5.7% | **2.18** | **81.0%** |

### Colombia

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 30.9% | 28.7% | 5.26 | 24.7% |
| accion | 10.0% | 14.8% | **9.10** | 35.7% |
| terror | 11.8% | 13.7% | 7.04 | 26.7% |
| thriller | 10.7% | 12.8% | 5.87 | 32.2% |
| infantil-familia | 7.4% | 12.0% | 7.19 | **41.9%** |
| comedia | 12.3% | 11.9% | 7.03 | 28.4% |
| documental | 11.4% | 8.9% | 6.13 | 25.3% |
| anime | 2.3% | **8.4%** | **11.04** | 41.3% |

### Chile

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 30.3% | **38.0%** | 5.94 | 38.1% |
| thriller | 13.5% | 18.2% | 5.83 | 38.0% |
| terror | 12.5% | 16.2% | 6.06 | 36.6% |
| comedia | 13.6% | 14.7% | 5.92 | 37.3% |
| romance | 8.5% | 10.9% | 5.99 | 38.5% |
| accion | 10.0% | 9.9% | 6.29 | 37.9% |
| documental | 13.3% | 9.9% | 6.39 | 36.5% |
| infantil-familia | 7.5% | 6.5% | 5.71 | **45.0%** |

**Conclusiones — distribución:** la regla "el país fija el precio, el género la vendibilidad" cumple seis cortes, y **Colombia consolida su nicho premium: anime a 11.04 de eCPM con el 8.4% del tráfico del país, aventura a 10.18 (7.7% del tráfico) y acción a 9.10** — precios que ningún género alcanza en Chile o México. La recuperación colombiana sigue concentrada, no es pareja. Chile sigue plano (5.8–6.4) y en México el patrón de liquidez barata se acentúa: el EPG de Roku (12.2% del tráfico, 76% monetizado) y ahora también deportes (81% monetizado a 2.18 — lo más líquido y más barato del país).

## Auditoría de contentGenre: lo "lleno" que no es un género

| Categoría | MX filas | MX reqs | CO filas | CO reqs | CL filas | CL reqs |
|---|---:|---:|---:|---:|---:|---:|
| Fill útil (nominal) | 99.1% | 93.8% | 98.5% | 93.1% | 99.5% | 96.0% |
| − prefijo_tecnico (`genre_*`) | 4.5% | **6.3%** | — | — | — | — |
| − genero_en_formato_sucio | 6.5% | 4.6% | 0.8% | 1.1% | 2.9% | 1.8% |
| − tipo_de_contenido | 1.6% | 0.3% | 1.8% | 0.6% | 1.2% | 0.5% |
| − idioma_o_region | 0.3% | 0.1% | 0.5% | 0.2% | 0.2% | 0.1% |
| − tema_no_genero | 0.4% | 0.4% | 0.4% | 0.9% | 0.3% | 0.7% |
| − otros_no_reconocidos | 4.1% | 1.7% | 2.2% | 3.4% | 1.5% | 2.5% |
| **Fill efectivo (género real)** | **81.7%** | **80.5%** | **92.8%** | **86.9%** | **93.4%** | **90.4%** |

Más ~7% de filas "mapeadas parciales" en los tres. **Los tres países retrocedieron 1–2pp de fill efectivo por requests** (MX 82.1 → 80.5, CO 88.9 → 86.9, CL 92.3 → 90.4): el vocabulario que entró con v15 cayó sobre todo en `otros_no_reconocidos` — mismo síntoma que el 89.3% global de filas mapeables (venía de 91.9%). El `genre_*` de TV Azteca volvió a subir de peso en México (6.3% de requests) con el rebote del publisher.

---

# PARTE B — contentTitle: del fill nominal al fill efectivo

**México:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil (nominal) | 83.7% | 64.9% |
| − placeholder (`roku`/`epg`/`vod`) | 0.4% | **11.2%** |
| − slug_tecnico (`*_trailer`) | 2.6% | 2.9% |
| − canal_no_programa (Televisa lineal) | 2.1% | 1.4% |
| − macro / sin_letras / muy_corto / encoding | 0.3% | 1.0% |
| **Fill efectivo (título real)** | **78.3%** | **48.2%** |

**Colombia:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil | 94.9% | 93.6% |
| − slug_tecnico | 4.7% | **7.2%** |
| − macro + resto | 0.4% | 0.2% |
| **Fill efectivo** | **89.8%** | **86.2%** |

**Chile:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil | 96.7% | 94.6% |
| − slug_tecnico | 4.3% | 6.0% |
| − encoding_roto | 0.2% | **1.5%** |
| − macro + resto | 0.2% | 0.2% |
| **Fill efectivo** | **91.9%** | **86.9%** |

**Conclusiones — título:**

1. **México cayó por primera vez bajo el 50% de tráfico con título real (48.2%)**, tras cinco cortes clavado en ~50–51%. La explicación está repartida entre los placeholders de Roku (11.2% de los requests, que crecen con el peso de Roku) y los canales lineales de Televisa/Vidaa (2.1% de filas — "golden edge" y "golden multiplex" ya en el top del país).
2. Colombia (86.2%) y Chile (86.9%) estables con deriva leve a la baja, y la fuga de siempre: slugs `*_trailer` (6–7% de requests) — el catálogo de trailers se renueva (`monster_trailer`, `the hanji box_trailer`) pero el formato sucio persiste.
3. El mojibake chileno inamovible en 1.5% de requests (`catalunya über alles!` sigue siendo el título más visto del país).
4. La conclusión operativa se refuerza: **fill nominal ≠ usabilidad** — título real por requests: Chile 87% ≈ Colombia 86% ≫ **México 48%**.
