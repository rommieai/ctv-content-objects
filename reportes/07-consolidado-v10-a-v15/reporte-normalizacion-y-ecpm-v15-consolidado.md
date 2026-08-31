# Reporte — Normalización de género/rating y análisis del inventario monetizado (consolidado v10 a v15)

**Fuente:** `inventory-consolidado-v10-a-v15.csv` (648,589 filas, 385,830,361,280 requests; métricas de v15).
**Generado con:** `scripts/normalizar_monetizar.py` → `reporte-normalizacion-y-ecpm-v15-consolidado.json` e `inventory-consolidado-v10-a-v15-enriquecido.csv` (no versionado).

**Contexto:** sexta versión del análisis. El eCPM ponderado global completa cinco bajadas seguidas, aunque moderándose (4.98 → 4.55 → 4.40 → 4.20 → **4.16**), y el outlier peruano de 135.3 persiste. **La novedad estructural: el tráfico monetizado subió a 52.9%** — primera salida de la banda 51±0.1 en seis cortes.

---

# PARTE A — Género normalizado

89.3% de filas con al menos un género canónico (bajó de 91.9% — el vocabulario nuevo de v15 entró sin mapear); 261,068 multi-género. Distribución (por % de requests):

| Género | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| drama | 28.8% | 28.7% | 3.77 | 46.0% |
| comedia | 12.5% | 12.2% | 3.92 | 49.0% |
| thriller | 11.5% | 10.3% | 3.88 | 36.1% |
| terror | 11.3% | 9.9% | 4.06 | 34.8% |
| entretenimiento (genérico) | 4.0% | 8.5% | 5.03 | **72.1%** |
| accion | 9.8% | 8.3% | 4.80 | 41.3% |
| romance | 7.6% | 7.8% | 4.90 | 42.0% |
| documental | 11.3% | 7.7% | 5.19 | 38.0% |
| infantil-familia | 6.5% | 5.7% | 5.61 | 47.1% |
| deportes | 4.0% | 5.6% | **2.77** | **73.6%** |
| crimen | 5.2% | 4.3% | 4.77 | 38.6% |
| aventura | 4.9% | 3.8% | 6.04 | 38.4% |
| noticias | 1.7% | 3.2% | 4.76 | **64.9%** |
| musica | 4.5% | 3.2% | 3.95 | 55.8% |
| misterio | 4.0% | 3.1% | 4.40 | 36.7% |
| anime | 2.3% | 2.3% | **7.84** | 44.4% |
| fantasia | 3.4% | 2.2% | 4.95 | 33.3% |
| sci-fi | 3.1% | 2.1% | 4.01 | 30.1% |

**Conclusiones:** sexta confirmación del patrón precio-plano / vendibilidad-dispersa. **Anime marca nuevo récord (7.84; la serie va 6.16 → 7.49 → 7.84)** y ya casi triplica al género más barato con volumen (deportes 2.77, que a la vez sigue siendo de los más fáciles de vender: 73.6%). Aventura (6.04) mantiene el segundo puesto de yield. Ojo metodológico: el % de filas mapeables bajó ~2.6pp — conviene revisar los `tokens_no_mapeados_top` del JSON para ampliar el diccionario en la próxima tanda.

# PARTE B — Rating en franjas de edad

| Franja | % filas | % requests | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| todos | 7.9% | 11.3% | 4.99 | **66.3%** |
| 7+ | 0.7% | 0.8% | 6.69 | 45.9% |
| 10+ | 10.3% | 11.8% | 4.51 | 54.0% |
| 13-15 | 25.0% | **31.9%** | 3.88 | 54.0% |
| 16-17 | 12.1% | 8.9% | 4.98 | 38.0% |
| 18+ / adulto | 15.6% | 12.9% | 4.52 | **36.8%** |
| sin clasificar | 9.7% | 7.6% | 3.68 | 48.9% |
| sin dato | 16.1% | 11.9% | **3.25** | 64.3% |
| no mapeado | 2.8% | 3.0% | 3.87 | 66.3% |

**Conclusiones:** invariantes de siempre — teen (13-15) sigue siendo un tercio del tráfico y la franja clasificada más barata (3.88), y el adulto se vende a la mitad de tasa que el family-safe. El "sin dato" recuperó algo de precio (2.87 → 3.25) pero sigue siendo el más castigado: clasificar contenido sigue valiendo ~+30–35%.

# PARTE C — El inventario que monetiza (eCPM > 0)

**115,242 filas (17.8%) concentran el 52.9% del tráfico** — tras cinco cortes clavado en 51±0.1%, la partición vendido/muerto se movió por primera vez (+1.8pp). La mitad vendida del dataset está creciendo.

## Por país

| País | % tráfico monetizado | % filas monetizadas | eCPM pond. |
|---|---:|---:|---:|
| México | 60.2% | 19.0% | 3.25 |
| Argentina | 55.2% | 20.6% | 6.19 |
| Costa Rica | 48.4% | **34.0%** | 6.49 |
| Puerto Rico | 47.7% | 11.6% | **8.20** |
| Chile | 40.9% | 24.3% | 6.19 |
| Perú | 33.0% | 15.9% | 4.72 |
| Colombia | 32.8% | 15.1% | **5.36** |
| Ecuador | 18.1% | 6.8% | 5.43 |

**Colombia encadena tres cortes mejorando en tasa y precio** (23.9% → 27.1% → 32.8% de sell-through; 4.51 → 4.97 → 5.36). México también subió su sell-through (57.4% → 60.2%) aunque al precio más bajo. **Perú se desinfló: 5.95 → 4.72** — sus outliers siguen ahí pero pesan cada vez menos. Puerto Rico se mantiene como el precio top (8.20).

## Por publisher (share del tráfico monetizado)

| Publisher | Share | % propio monetizado | eCPM pond. |
|---|---:|---:|---:|
| Roku - oRTB | **17.1%** | 60.4% | 5.44 |
| TCL ADS - Springserve | 16.9% | 84.8% | 5.06 |
| TCL ADs (APAC) | 8.9% | 79.5% | 5.51 |
| Coocaa (SKYWORTH) | 8.1% | 92.4% | 3.01 |
| iion Pty Ltd | 7.8% | 41.0% | 4.99 |
| Televisa Univision via SpringServe | 7.8% | 90.1% | 2.44 |
| Equativ | 7.6% | 84.0% | 2.58 |
| TV Azteca - Springserve | **5.2%** | 74.9% | 5.46 |
| Televisa Univision via OB | 4.8% | **97.3%** | 1.44 |
| Vidaa | 4.0% | 84.2% | **1.40** |
| Zeasn (WhaleLive) | 3.6% | 93.2% | 3.11 |
| PML Digital | 1.9% | 73.4% | 2.44 |

Roku mantiene el #1 del tráfico monetizado, con TCL Springserve pegado (17.1% vs 16.9%). **La sorpresa es TV Azteca: rebotó de 2.9% a 5.2% del tráfico vendido** (y su % propio monetizado saltó de 48.7% a 74.9%) — la predicción de que "se estaba apagando" no aguantó ni un corte. Vidaa se enfrió (4.8% → 4.0%) y sigue siendo el volumen más barato del top (1.40).

## Señales sobre el tráfico monetizado

- **Idioma:** español 50.4% del tráfico vendido a **4.69** vs inglés 26.1% a 3.42 — **prima del +37%**, estable en máximos. El "sin dato" (19.3% del vendido) paga 3.95.
- **Live:** 48.4% del vendido, con prima (4.35 vs 3.98).
- **Título:** la prima del título prácticamente desapareció (4.16 con título vs 4.14 sin) — venía de 4.24 vs 4.10.
- **Outliers:** top 5 íntegramente peruano y por primera vez **100% de TCL APAC / MovieArk** (135.3, 102.9, 100.6, 100.3, 99.2). La recomendación de excluir eCPM > ~30 en Perú sigue en pie.

---

## Síntesis

1. **Primera grieta en la estructura**: tras cinco cortes con el 51.1±0.1% del tráfico monetizado, v15 lo sube a **52.9%**. Si el próximo corte confirma la dirección, la mitad vendida del inventario está creciendo de verdad.
2. Los precios completan la quinta bajada global pero moderándose (4.20 → 4.16), con dos historias en contra: **Colombia (tercer corte subiendo: 5.36)** y el rebote de TV Azteca en el tráfico vendido.
3. Argumentos comerciales vigentes: español **+37%** sobre inglés, clasificar contenido vale ~+30–35%, family-safe el más líquido (66% sell-through), y el paquete de yield es anime (7.84, récord) + aventura (6.04). La prima por título, en cambio, se esfumó en este corte.
4. Nada de esto es utilizable para serie temporal sin fijar versión: los eCPM se recalculan en cada corte. La cifra "oficial" de cada métrica debe llevar la etiqueta del consolidado del que salió (este: v10-a-v15).
