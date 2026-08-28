# Reporte — Normalización de género/rating y análisis del inventario monetizado (consolidado v10 a v14)

**Fuente:** `inventory-consolidado-v10-a-v14.csv` (607,878 filas, 396,370,107,200 requests; métricas de v14).
**Generado con:** `scripts/normalizar_monetizar.py` → `reporte-normalizacion-y-ecpm-v14-consolidado.json` e `inventory-consolidado-v10-a-v14-enriquecido.csv` (no versionado).

**Contexto:** quinta versión del análisis. El eCPM ponderado global completa cuatro bajadas seguidas (4.98 → 4.55 → 4.40 → **4.20**) y el outlier peruano de 135.3 persiste. Lo estructural, intacto.

---

# PARTE A — Género normalizado

91.9% de filas con al menos un género canónico; 247,363 multi-género. Distribución (por % de requests):

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 29.3% | 30.2% | 3.91 | 45.8% |
| comedia | 12.7% | 12.2% | 3.88 | 48.6% |
| thriller | 11.6% | 11.2% | 4.10 | 36.6% |
| terror | 11.4% | 10.8% | 4.14 | 35.5% |
| accion | 9.9% | 8.6% | 5.04 | 42.8% |
| entretenimiento (genérico) | 4.0% | 8.1% | 5.30 | **74.7%** |
| romance | 7.7% | 8.1% | 4.95 | 41.9% |
| documental | 11.5% | 7.7% | 4.99 | 37.0% |
| infantil-familia | 6.5% | 5.8% | 5.46 | 46.9% |
| deportes | 3.8% | 5.2% | **2.93** | **72.4%** |
| crimen | 5.3% | 4.4% | 4.83 | 39.4% |
| aventura | 4.9% | 3.9% | 6.23 | 37.4% |
| misterio | 4.1% | 3.3% | 4.47 | 36.8% |
| noticias | 1.6% | 3.3% | 5.06 | **63.1%** |
| musica | 4.5% | 3.1% | 3.84 | 54.2% |
| anime | 2.3% | 2.5% | **7.49** | 45.7% |
| fantasia | 3.5% | 2.4% | 5.06 | 33.7% |
| sci-fi | 3.1% | 2.2% | 3.95 | 32.2% |
| película (genérico) | 2.4% | 1.4% | 6.22 | 50.8% |

**Conclusiones:** quinta confirmación del patrón precio-plano / vendibilidad-dispersa. **Anime sigue subiendo (7.49, era 6.16 dos cortes atrás)** y ya saca 2.5x al género más barato con volumen (deportes 2.93, que a la vez es el segundo más fácil de vender: 72%). Aventura (6.23) y película genérica (6.22) completan el podio de yield.

# PARTE B — Rating en franjas de edad

| Franja | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| todos | 7.7% | 11.1% | 5.21 | **70.4%** |
| 7+ | 0.7% | 0.8% | 6.49 | 42.9% |
| 10+ | 10.3% | 11.2% | 4.68 | 51.7% |
| 13-15 | 25.0% | **31.7%** | 3.98 | 51.9% |
| 16-17 | 12.3% | 9.3% | 4.86 | 37.0% |
| 18+ / adulto | 15.9% | 13.6% | 4.55 | **35.0%** |
| sin clasificar | 9.8% | 7.8% | 3.91 | 46.3% |
| sin dato | 15.6% | 11.7% | **2.87** | 61.3% |
| no mapeado | 2.8% | 2.9% | 3.67 | 61.9% |

**Conclusiones:** invariantes de siempre (teen un tercio del tráfico, adulto vendiéndose a la mitad de tasa) y el castigo del "sin dato" profundizándose otro poco (2.87 — ya es ~35–40% bajo el clasificado). Un matiz nuevo: la franja 13-15, la más grande, quedó como la clasificada más barata (3.98) — ahí cae el volumen masivo de Televisa/ViX.

# PARTE C — El inventario que monetiza (eCPM > 0)

**108,274 filas (17.8%) concentran el 51.1% del tráfico** — quinta vez que el número cae en 51±0.1%: la partición vendido/muerto del inventario es estructural.

## Por país

| País | % tráfico monetizado | % filas monetizadas | eCPM pond. |
|---|---:|---:|---:|
| México | 57.4% | 18.3% | 3.33 |
| Costa Rica | 57.2% | **37.6%** | 6.05 |
| Argentina | 54.8% | 20.9% | 5.97 |
| Puerto Rico | 50.9% | 11.4% | **8.05** |
| Chile | 42.1% | 23.7% | 6.52 |
| Perú | 33.8% | 18.0% | 5.95 |
| Colombia | 27.1% | 13.4% | **4.97** |
| Ecuador | 19.2% | 7.2% | 5.41 |

**Colombia suma dos cortes seguidos mejorando en tasa y precio** (21.5% → 23.9% → 27.1% de sell-through; 3.01 → 4.51 → 4.97) — es la única historia de crecimiento del dataset. Chile sigue cediendo premium; Puerto Rico se mantiene como el precio top.

## Por publisher (share del tráfico monetizado)

| Publisher | Share | % propio monetizado | eCPM pond. |
|---|---:|---:|---:|
| Roku - oRTB | **18.0%** | 64.1% | 5.81 |
| TCL ADS - Springserve | 17.9% | 83.3% | 4.91 |
| TCL ADs (APAC) | 9.7% | 78.7% | 5.57 |
| Coocaa (SKYWORTH) | 8.4% | 94.8% | 3.22 |
| iion Pty Ltd | 8.0% | 43.0% | 4.47 |
| Televisa Univision via SpringServe | 7.6% | 89.8% | 2.66 |
| Equativ | 6.9% | 83.0% | 2.66 |
| Vidaa | 4.8% | 84.3% | **1.38** |
| Televisa Univision via OB | 4.8% | **97.4%** | 1.50 |
| Zeasn (WhaleLive) | 3.4% | 93.2% | 2.97 |
| TV Azteca - Springserve | 2.9% | 48.7% | 5.67 |

Roku recuperó el #1 del tráfico monetizado por una nariz sobre TCL Springserve. TV Azteca sigue cayendo (2.9%, era 8.1% dos consolidados atrás). Vidaa ya es el 4.8% del tráfico vendido — al peor precio del top (1.38): volumen ViX barato.

## Señales sobre el tráfico monetizado

- **Idioma:** español 49.0% del tráfico vendido a **4.86** vs inglés 27.7% a 3.51 — **prima del +38%**, la más alta registrada. El "sin dato" (18.9% del vendido) paga 3.67.
- **Live:** 49.5% del vendido, con prima (4.58 vs 3.83).
- **Título:** con título paga más (4.24 vs 4.10) — estable desde el recálculo de v12.
- **Outliers:** top 5 íntegramente peruano (135.3, 100.3, 95.9, 93.3, 92.5 — cuatro de TCL APAC, uno de iion). La recomendación de excluir eCPM > ~30 en Perú sigue en pie.

---

## Síntesis

1. Cinco cortes: **la estructura no se mueve** (51.1% monetizado exacto, mismos modelos de publisher, mismo sell-through por género/franja) **y los precios solo bajan** (4.98 → 4.20 global), salvo Colombia, que sube dos cortes seguidos.
2. Argumentos comerciales vigentes y reforzados: español **+38%** sobre inglés, clasificar contenido vale +35–40%, family-safe el más líquido (70% sell-through), y el paquete de yield es anime (7.49) + aventura + película genérica.
3. Nada de esto es utilizable para serie temporal sin fijar versión: los eCPM se recalculan en cada corte. La cifra "oficial" de cada métrica debe llevar la etiqueta del consolidado del que salió (este: v10-a-v14).
