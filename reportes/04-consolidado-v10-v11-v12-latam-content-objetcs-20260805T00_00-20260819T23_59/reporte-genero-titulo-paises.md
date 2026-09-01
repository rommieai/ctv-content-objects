# Reporte — Género normalizado y calidad real de contentTitle: México, Colombia y Chile

**Fuente:** `inventory-consolidado-v10-v11-v12.csv` (539,190 filas; métricas de v12).
**Generado con:** `scripts/analizar_genero_titulo_paises.py` → `reporte-genero-titulo-paises.json` (distribuciones completas y ejemplos por categoría).

Dos análisis en uno, ambos desglosados por país: (A) la normalización de `contentGenre` (mismo diccionario de sinónimos de la tanda anterior, ahora con porcentajes por país) con su propia auditoría de **valores que no son un género**, y (B) una auditoría de `contentTitle` que va un paso más allá del fill: dentro de lo que cuenta como "lleno", cuánto **no es realmente un título de contenido** según lo que espera [OpenRTB 2.6](https://github.com/InteractiveAdvertisingBureau/openrtb2.x/blob/main/2.6.md#objectcontent). En ambos campos la lógica es la misma: el fill nominal es una cota superior; aquí se calcula el **fill efectivo**.

---

# PARTE A — Género normalizado por país

Cobertura del mapeo (filas que quedaron con al menos un género canónico):

| | México | Colombia | Chile |
|---|---:|---:|---:|
| % filas con género canónico | **84.3%** | 93.2% | 95.9% |
| Filas con género no mapeable | 22,692 (14.7%) | 2,745 (5.3%) | 2,195 (3.6%) |
| Filas multi-género | 52,377 | 20,896 | 29,344 |

México es el país con peor mapeo, y no por catálogo raro: ahí viven los dos vocabularios sucios ya identificados — los prefijos `genre_*` de TV Azteca y el "movies & tv" de Roku. Con esos dos fixes, México subiría a ~95% como los otros.

## Distribución por género (top por % de requests del país; multi-etiqueta, suman >100)

### México

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 25.9% | 26.9% | 3.11 | 50.5% |
| comedia | 12.1% | 11.3% | 3.52 | 54.9% |
| entretenimiento | 4.8% | **10.6%** | **5.51** | **78.3%** |
| thriller | 9.4% | 10.2% | 3.48 | 42.7% |
| terror | 9.7% | 9.9% | 3.26 | 41.4% |
| accion | 9.3% | 8.4% | 4.55 | 49.2% |
| romance | 6.5% | 6.9% | 4.07 | 48.6% |
| documental | 9.8% | 5.7% | 3.57 | 39.8% |
| deportes | 3.7% | 4.4% | **1.98** | 73.5% |
| crimen | 5.1% | 3.9% | 4.20 | 42.8% |
| noticias | 2.4% | 3.8% | 4.86 | 67.2% |
| aventura | 4.8% | 3.0% | 4.45 | 40.5% |
| infantil-familia | 5.0% | 2.8% | 3.00 | 41.8% |

### Colombia

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 30.9% | 33.6% | 2.61 | 15.8% |
| terror | 11.3% | **16.5%** | 2.42 | 15.2% |
| thriller | 10.4% | 14.6% | 2.35 | 20.1% |
| accion | 9.6% | 12.8% | 3.43 | 21.6% |
| comedia | 12.3% | 12.4% | 3.13 | 17.9% |
| documental | 11.6% | 10.3% | 2.90 | 18.0% |
| infantil-familia | 7.4% | 9.7% | 3.22 | 29.6% |
| romance | 8.2% | 8.6% | 2.71 | 17.2% |
| aventura | 4.5% | 6.4% | 2.84 | 22.9% |
| anime | 2.2% | **5.8%** | **3.99** | 26.1% |
| crimen | 5.0% | 4.8% | 2.24 | 20.7% |
| deportes | 4.3% | 4.4% | 2.88 | **47.6%** |

### Chile

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 31.7% | **40.5%** | 7.84 | 31.8% |
| thriller | 14.0% | 19.4% | 7.72 | 31.7% |
| terror | 12.6% | 17.3% | 7.91 | 30.6% |
| comedia | 14.3% | 15.7% | 7.79 | 31.4% |
| romance | 8.9% | 11.6% | 7.82 | 32.4% |
| documental | 13.9% | 10.8% | 8.55 | 29.6% |
| accion | 10.2% | 10.7% | 8.32 | 32.8% |
| infantil-familia | 7.6% | 6.8% | 8.11 | 40.7% |
| misterio | 5.4% | 6.3% | 7.61 | 30.4% |
| crimen | 5.6% | 6.0% | 7.72 | 31.6% |
| aventura | 5.5% | 4.8% | **9.30** | 33.6% |
| deportes | 3.7% | 4.8% | 7.73 | **56.4%** |
| musica | 5.7% | 3.8% | 8.09 | 33.6% |

## Conclusiones — género

1. **El país fija el precio; el género fija la vendibilidad.** El mismo drama paga 3.11 en México, 2.61 en Colombia y 7.84 en Chile — pero el patrón de sell-through se repite en los tres: deportes, entretenimiento y noticias monetizan al doble de tasa que el catálogo de películas (terror, thriller, documental). El hallazgo global se confirma mercado por mercado.
2. **Chile es notablemente plano en precio** (7.6–9.3 en todos los géneros): su prima es de mercado, no de contenido. Contrasta con México, donde sí hay dispersión (deportes 1.98 vs entretenimiento 5.51).
3. **Colombia monetiza mal en todos los géneros** (15–30%, contra 40–78% de México): la enfermedad colombiana es transversal a todo el catálogo — es demanda, no mix de contenido.
4. Particularidades: en México el "entretenimiento" (el EPG de Roku) es el 10.6% del tráfico y lo mejor monetizado (78%); en Colombia el **anime pesa 5.8% del tráfico** (el triple que en los otros) y es su género mejor pagado (3.99); en Chile drama solo ya es el 40% del tráfico.

## Auditoría de contentGenre: lo "lleno" que no es un género

Misma lógica que la auditoría de título: dentro del fill útil (que ya excluye centinelas), se clasifican las filas cuyo valor **no corresponde a un género** según lo que espera la spec (`content.genre` = "género que mejor describe el contenido"):

| Categoría | Qué es | Ejemplos reales |
|---|---|---|
| prefijo_tecnico | la variable con prefijo en vez del valor | `genre_drama`, `genre_action` |
| genero_en_formato_sucio | sí es un género, pero en formato no estándar | `western drama`, `drama%2cromance` (coma URL-encoded), `music audio` |
| tipo_de_contenido | formato del asset, no género | `tv series`, `videos`, `feature film`, `live` |
| idioma_o_region | idioma/región metido como género | `en español`, `foreign`, `international` |
| tema_no_genero | tema editorial, no género | `business & finance`, `relaxing`, `arts` |
| otros_no_reconocidos | vocabulario propio no interpretable | `bingeworthy`, `classic`, `arcade`, `se` |

Resultados (% sobre filas y requests de cada país):

| Categoría | MX filas | MX reqs | CO filas | CO reqs | CL filas | CL reqs |
|---|---:|---:|---:|---:|---:|---:|
| Fill útil (nominal) | 99.0% | 93.4% | 98.5% | 96.0% | 99.5% | 98.6% |
| − prefijo_tecnico | 5.4% | **8.7%** | — | — | — | — |
| − genero_en_formato_sucio | 4.2% | 2.9% | 0.7% | 0.8% | 0.8% | 0.8% |
| − tipo_de_contenido | 1.2% | 0.3% | 1.9% | 0.6% | 1.1% | 0.5% |
| − idioma_o_region | 0.3% | 0.1% | 0.6% | 0.2% | 0.2% | 0.1% |
| − tema_no_genero | 0.3% | 0.3% | 0.4% | 0.7% | 0.3% | 0.6% |
| − otros_no_reconocidos | 3.3% | 2.5% | 1.8% | 2.2% | 1.2% | 2.1% |
| **Fill efectivo (género real)** | **84.3%** | **78.7%** | **93.2%** | **91.6%** | **95.9%** | **94.6%** |

Aparte, en los tres países hay un ~7–8% adicional de filas "mapeadas parciales": traen un género canónico válido pero acompañado de tokens basura (usables, pero delatan el mismo desorden de vocabulario).

**Conclusiones — auditoría de género:**

1. **Otra vez México es donde el fill más engaña**: del 93.4% nominal por requests, el género real queda en 78.7%. Y la mitad de la fuga es un solo responsable: el prefijo `genre_*` de TV Azteca, que él solo es el **8.7% del tráfico del país** — las otras dos plazas no lo tienen en absoluto. Colombia (91.6%) y Chile (94.6%) quedan sanos.
2. Buena noticia dentro de lo sucio: la categoría más grande después del prefijo es "género en formato sucio" — valores que **sí son géneros** (`western drama`, `drama%2cromance`) y se recuperarían con ~20 sinónimos más en el diccionario, incluyendo el hallazgo nuevo de esta pasada: comas URL-encoded (`%2c`) sin decodificar, otra variante de pipeline roto.
3. Lo verdaderamente irrecuperable (tipos de contenido, idiomas, temas, vocabulario propio) ronda apenas el 3–5% del tráfico en los tres países: el género, bien normalizado, es y sigue siendo la mejor señal contextual del dataset.

---

# PARTE B — contentTitle: del fill nominal al fill efectivo

## Método

El fill "útil" de contentTitle ya excluye los vacíos disfrazados (`Not Applicable`, etc.). Pero dentro de lo lleno quedan valores que **no cumplen la práctica que espera la spec** (un título de contenido identificable). Se clasificó cada título en 8 categorías de sospecha; lo que no cae en ninguna se considera título aparentemente válido:

| Categoría | Qué es | Ejemplos reales del dataset |
|---|---|---|
| placeholder | valor de plataforma, no de contenido | `roku`, `epg`, `vod` |
| canal_no_programa | nombre del canal/feed lineal, no del programa | las estrellas, canal 5, golden, red bull tv |
| slug_tecnico | identificador con guion bajo | `devils prey_trailer`, `alfaaz_trailer` |
| macro_sin_reemplazar | variable de ad server sin resolver | `{{content_title}}` |
| encoding_roto | mojibake (U+FFFD) | `catalunya �ber alles!` |
| sin_letras | solo dígitos/símbolos | `8.0`, `41`, `199` |
| muy_corto | 1–2 caracteres | `n`, `c`, `fx` |
| hash | 32 hexadecimales | (no apareció en títulos de estos países) |

## Resultados por país

**México** — el caso grave:

| Métrica | % filas del país | % requests del país |
|---|---:|---:|
| Fill útil (lo que reportábamos) | 82.5% | 65.1% |
| − placeholder (`roku`/`epg`/`vod`) | 0.4% | **9.7%** |
| − slug_tecnico (`*_trailer`) | 2.7% | 3.4% |
| − canal_no_programa (Televisa lineal) | 1.5% | 0.9% |
| − macro / sin_letras / muy_corto / encoding | 0.4% | 0.6% |
| **Fill efectivo (título real)** | **77.5%** | **50.5%** |

**Colombia:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil | 94.9% | 96.1% |
| − slug_tecnico | 4.8% | **7.7%** |
| − macro + resto | 0.4% | 0.2% |
| **Fill efectivo** | **89.7%** | **88.2%** |

**Chile:**

| Métrica | % filas | % requests |
|---|---:|---:|
| Fill útil | 96.6% | 97.6% |
| − slug_tecnico | 4.3% | 6.4% |
| − encoding_roto | 0.2% | **1.7%** |
| − macro + resto | 0.2% | 0.2% |
| **Fill efectivo** | **91.9%** | **89.4%** |

## Conclusiones — contentTitle

1. **En México, el título utilizable de verdad cubre solo la mitad del tráfico (50.5%)**, no el 65% que sugiere el fill nominal. La diferencia la explican sobre todo los placeholders de Roku (`roku`/`epg`/`vod` = 9.7% de los requests del país, en solo 657 filas gigantes) y los nombres de canal de Televisa en vez del programa. Cualquier producto de content targeting en México debe descontar esto.
2. **Colombia y Chile están mucho más sanos (~88–89% efectivo)**, y su única fuga relevante es común: los **slugs `*_trailer`** (4–5% de filas, 6–8% de requests) — el catálogo de trailers de OTT Studios/TCL que manda el identificador del asset con guion bajo en vez del título limpio. Es un solo fix de formato en una sola fuente.
3. En Chile el mojibake no es anecdótico: el título con encoding roto concentra el **1.7% de los requests** del país (el catálogo catalán de alto volumen). En los otros dos países es residual.
4. Regla práctica que deja este análisis: **el "fill" de un content object es una cota superior, no una medida de usabilidad**. Para título, la utilidad real por requests es: Chile 89% > Colombia 88% ≫ México 50%.
