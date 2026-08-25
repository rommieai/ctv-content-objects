# Reporte — Normalización de género/rating y análisis del inventario monetizado (consolidado v10 a v13)

**Fuente:** `inventory-consolidado-v10-a-v13.csv` (579,679 filas, 403,522,711,360 requests; métricas de v13).
**Generado con:** `scripts/normalizar_monetizar.py` → `reporte-normalizacion-y-ecpm-v13-consolidado.json` (distribuciones completas, desglose por bundle/idioma/señales) y `inventory-consolidado-v10-a-v13-enriquecido.csv` (no versionado; se regenera con el script).

**Contexto del corte:** cuarta versión del reporte, mismos patrones estructurales, y otra ronda de recálculo de precios: el ponderado global baja a **4.40** (venía de 4.55), el máximo sube a **135.3** (nuevo outlier peruano) y el premium de WhaleLive terminó de desaparecer (≈3.0). Donde un recálculo cambia una conclusión, lo señalo.

---

# PARTE A — Género normalizado

92% de filas con al menos un género canónico (7,196 sin dato; 46,774 no mapeables — `genre_*`, "short", etc.); 240,126 filas multi-género (41%). Distribución (por % de requests):

| Género | % filas | % requests | eCPM pond. (>0) | % del tráfico del género que monetiza |
|---|---:|---:|---:|---:|
| drama | 29.5% | 30.1% | 4.17 | 44.8% |
| comedia | 12.9% | 12.1% | 4.10 | 47.2% |
| thriller | 11.9% | 11.5% | 4.35 | 37.6% |
| terror | 11.6% | 11.0% | 4.38 | 36.2% |
| accion | 10.1% | 8.8% | 5.16 | 43.4% |
| romance | 7.9% | 8.3% | 5.17 | 42.5% |
| entretenimiento (genérico) | 4.0% | 8.0% | 5.42 | **75.2%** |
| documental | 11.7% | 7.7% | 5.17 | 37.9% |
| infantil-familia | 6.5% | 5.6% | 5.32 | 47.2% |
| deportes | 3.8% | 4.9% | **3.00** | **71.4%** |
| crimen | 5.4% | 4.4% | 4.90 | 39.7% |
| aventura | 5.0% | 4.0% | 6.17 | 40.0% |
| misterio | 4.2% | 3.4% | 4.66 | 37.1% |
| noticias | 1.6% | 3.1% | 5.19 | **64.6%** |
| musica | 4.5% | 3.1% | 3.85 | 50.8% |
| anime | 2.3% | 2.3% | **7.22** | 46.0% |
| sci-fi | 3.2% | 2.3% | 4.18 | 32.5% |
| fantasia | 3.5% | 2.4% | 5.14 | 34.2% |
| película (genérico) | 2.4% | 1.4% | 6.56 | 52.1% |

**Conclusiones:** cuarta versión, mismos patrones — precio por género en banda estrecha (3.0–7.2) y facilidad de venta variando 2–3x a favor del contenido de canal (entretenimiento 75%, deportes 71%, noticias 65% vs terror/sci-fi 32–36%). **Anime se consolida como el género mejor pagado y hasta amplía su prima (7.22)**; deportes sigue siendo el más fácil de vender al peor precio (3.00). La estabilidad a través de 4 cortes hace que esta tabla ya sea confiable para decisiones de empaquetado.

# PARTE B — Rating en franjas de edad

| Franja | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| todos | 7.8% | 10.9% | 5.25 | **70.8%** |
| 7+ | 0.7% | 0.7% | 6.21 | 43.2% |
| 10+ | 10.2% | 11.1% | 4.77 | 52.8% |
| 13-15 | 24.8% | **32.1%** | 4.25 | 52.7% |
| 16-17 | 12.4% | 9.4% | 5.01 | **37.3%** |
| 18+ / adulto | 16.1% | 14.0% | 4.81 | **36.3%** |
| sin clasificar | 9.9% | 7.7% | 4.05 | 45.9% |
| sin dato | 15.3% | 11.1% | **2.98** | 57.5% |
| no mapeado | 2.8% | 3.1% | 3.98 | 61.0% |

**Conclusiones:** sin cambios estructurales — un tercio del tráfico es "teen", el 55% es apto para audiencias generales, y el contenido 16+/adulto se vende a la mitad de tasa sin pagar menos. **El castigo del inventario sin rating se profundizó otra vez: "sin dato" quedó en 2.98** (~35–40% por debajo del clasificado) — cada recálculo refuerza el argumento comercial de exigir clasificación.

# PARTE C — El inventario que monetiza (eCPM > 0)

**103,017 filas (17.8%) concentran el 51.1% del tráfico.** La foto de siempre: la mitad del volumen se vende, el resto es catálogo de cola de los agregadores (OTTera y Select Plus siguen monetizando ~0.1% de sus filas).

## Por país

| País | % tráfico monetizado | % filas monetizadas | eCPM pond. |
|---|---:|---:|---:|
| Costa Rica | 59.0% | **38.2%** | 5.99 |
| México | 57.2% | 18.4% | 3.60 |
| Argentina | 55.9% | 21.0% | 6.03 |
| Puerto Rico | 50.7% | 11.2% | **8.01** |
| Chile | 41.6% | 23.2% | 6.92 |
| Perú | 33.4% | 18.4% | 5.99 |
| Colombia | 23.9% | 12.1% | **4.51** |
| Ecuador | 20.2% | 7.2% | 5.87 |

Novedades del corte: **Colombia recuperó precio (3.01 → 4.51)** aunque sigue última en tasa junto a Ecuador; Chile cedió premium (8.17 → 6.92) pero mejoró su sell-through (35% → 42%); Puerto Rico queda como el mejor precio del dataset.

## Por publisher (share del tráfico monetizado)

| Publisher | Share | % propio monetizado | eCPM pond. |
|---|---:|---:|---:|
| TCL ADS - Springserve | **18.5%** | 82.6% | 5.08 |
| Roku - oRTB | 18.0% | 64.2% | 5.95 |
| TCL ADs (APAC) | 11.0% | 78.4% | 5.77 |
| Coocaa (SKYWORTH) | 8.3% | 94.9% | 3.30 |
| Televisa Univision via SpringServe | 7.3% | 85.9% | 2.65 |
| iion Pty Ltd | 7.1% | 40.8% | 4.21 |
| Equativ | 6.3% | 81.8% | 2.69 |
| Televisa Univision via OB | 4.9% | **97.6%** | 1.46 |
| TV Azteca - Springserve | 4.9% | 61.0% | 5.53 |
| Zeasn (WhaleLive) | 3.3% | 91.6% | **3.02** |
| Vidaa | 3.2% | 84.5% | 1.41 |

Los tres modelos se sostienen (broadcasters full-fill baratos, OEMs medios, agregadores muertos), con dos movimientos: **TCL Springserve destronó a Roku** como primer vendedor del tráfico monetizado, y el que era el publisher "premium" por request (Zeasn/WhaleLive, 10.7 en los primeros cortes) quedó en 3.02 — aquel premium era en buena parte un artefacto de precios que los recálculos fueron corrigiendo.

## Señales sobre el tráfico monetizado

- **Idioma**: el español es el 49.3% del tráfico vendido a **5.13**, vs inglés 28.9% a 3.80 — **la prima del español se amplió a +35%** (era +19%). El tráfico sin idioma paga 3.49.
- **Live**: mitad y mitad, con prima leve del live (4.69 vs 4.12).
- **Título**: se mantiene la relación sana post-recálculos — con título paga más (4.46 vs 4.23).
- **Outliers**: el top de precios sigue siendo peruano y ahora más extremo — máximo **135.3** (TCL/MovieArk), y 4 de los 5 más caros son de TCL APAC en Perú con volúmenes chicos. La recomendación sigue: excluir eCPM > ~30 de los promedios de Perú hasta validar esa integración.

---

## Síntesis

1. Con cuatro cortes, lo estructural ya es ley: sell-through por género y franja, los tres modelos de publisher, el catálogo muerto de los agregadores, y la paradoja español/inglés (que además se acentúa: +35% de prima).
2. Los precios siguen sin ser comparables entre cortes: ponderado global 4.98 → 4.55 → 4.40, Chile perdiendo premium, Colombia recuperando, WhaleLive desinflado, y un outlier nuevo de 135.3. **Toda cifra de precio debe citar la versión del reporte.**
3. Los argumentos comerciales, actualizados: español +35%, clasificar contenido vale +35-40%, el inventario family-safe sigue siendo el más líquido (71% de sell-through) y anime/aventura/película-genérica son los géneros a empaquetar por yield (6.2–7.2).
