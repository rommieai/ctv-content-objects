# Reporte — Normalización de género/rating y análisis del inventario monetizado (consolidado v10 a v16)

**Fuente:** `inventory-consolidado-v10-a-v16.csv` (810,933 filas, 365,377,125,360 requests; métricas de v16).
**Generado con:** `scripts/normalizar_monetizar.py` → `reporte-normalizacion-y-ecpm-v16-consolidado.json` e `inventory-consolidado-v10-a-v16-enriquecido.csv` (no versionado).

**Contexto:** séptima versión del análisis. El eCPM ponderado global completa seis bajadas seguidas (4.98 → 4.55 → 4.40 → 4.20 → 4.16 → **4.06**) y aparece un outlier nuevo de 194.3 en Perú. **El tráfico monetizado se sostiene en 52.6%** (v15: 52.9%): la salida de la banda 51±0.1 no fue un accidente de un corte.

**Cambio de formato en la fuente (afecta a este reporte):** el 28% de las filas de v16 trae el rating en una escala nueva (`All Ages`, `Teen`, `Teen Plus`, `Adults`, `Unrated`) y el género con mayúscula inicial. El género se absorbe solo (la normalización ya ignoraba mayúsculas). Para el rating, **se amplió el diccionario** de `normalizar_monetizar.py` con la escala nueva: `All Ages` → todos, `Teen` → 10+, `Teen Plus` → 13-15, `Adults` → 18+ / adulto (`Unrated` ya mapeaba a "sin clasificar"). La equivalencia no se supuso por el nombre: se verificó cruzando, dentro de v16, los títulos que llegan en las dos escrituras — `Teen` convive con `tv-pg` (375 títulos, contra 43 con `tv-14`), `Teen Plus` con `tv-14`/`14`/`pg-13` (1,120 títulos), `Adults` con `r`/`tv-ma`/`nc-17`/`18` y `All Ages` con `g`/`tv-g`. Es decir, "Teen" en esta escala **no** es TV-14 sino TV-PG. Sin la ampliación, 42k filas (5%) habrían caído en "no mapeado". Lo que **no** se puede arreglar con diccionario: en esas filas nuevas el rating viene vacío en el 68% de los casos, por eso "sin dato" salta de 16.1% a 27.0% de las filas.

---

# PARTE A — Género normalizado

88.0% de filas con al menos un género canónico (bajó de 89.3%: el formato nuevo trae más filas con género vacío — `Not Applicable` pasó de 1.2% a 4.1% de las filas); 261,228 multi-género. Distribución (multi-etiqueta; % sobre las filas con género útil):

| Género | % filas no vacías | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|
| drama | 29.5% | 3.64 | 47.8% |
| terror | 11.8% | 3.96 | 34.3% |
| comedia | 11.6% | 3.84 | 52.0% |
| documental | 10.8% | 5.46 | 39.5% |
| thriller | 10.1% | 3.85 | 35.9% |
| accion | 9.5% | 4.85 | 40.6% |
| romance | 6.9% | 4.62 | 42.1% |
| infantil-familia | 5.7% | 5.78 | 46.7% |
| otros/desconocido | 5.6% | 4.39 | 30.4% |
| crimen | 4.6% | 4.82 | 38.6% |
| aventura | 4.4% | 6.18 | 36.8% |
| entretenimiento | 4.0% | 4.87 | **65.0%** |
| deportes | 3.9% | **2.38** | **68.3%** |
| musica | 3.7% | 3.94 | 56.3% |
| misterio | 3.4% | 4.30 | 36.3% |
| fantasia | 3.0% | 4.77 | 30.8% |
| sci-fi | 3.0% | 4.18 | 29.8% |
| anime | 2.0% | **8.05** | 44.0% |
| noticias | 1.7% | 4.65 | 61.1% |

**Conclusiones:** séptima confirmación del patrón precio-plano / vendibilidad-dispersa. **Anime marca nuevo récord (8.05; la serie va 6.16 → 7.49 → 7.84 → 8.05)** y ya más que triplica al género más barato con volumen (deportes 2.38, que a la vez sigue siendo el más fácil de vender: 68.3%). Aventura (6.18) mantiene el segundo puesto de yield e infantil-familia (5.78) el tercero. Drama, el género con más filas, es de los más baratos (3.64). Ojo metodológico: el % de filas mapeables bajó otro punto (89.3 → 88.0) pero esta vez la causa es el vacío del formato nuevo, no vocabulario sin mapear (los `tokens_no_mapeados_top` del JSON son los de siempre: `short`, `tv series`, `culture`, `genre_*`).

# PARTE B — Rating en franjas de edad

| Franja | % filas | % filas no vacías | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| todos | 6.8% | 9.3% | 4.80 | **63.1%** |
| 7+ | 0.6% | 0.8% | 6.90 | 47.9% |
| 10+ | 9.1% | 12.4% | 4.47 | 50.9% |
| 13-15 | 21.9% | **30.0%** | 3.77 | 55.0% |
| 16-17 | 9.7% | 13.2% | 4.96 | 38.4% |
| 18+ / adulto | 14.5% | 19.9% | 4.46 | **36.4%** |
| sin clasificar | 8.3% | 11.3% | 3.81 | 45.3% |
| sin dato | **27.0%** | — | **3.62** | 57.2% |
| no mapeado | 2.2% | 3.1% | 3.76 | 65.9% |

*Aquí se conservan ambas columnas porque no son intercambiables: la distribución incluye la fila vacía ("sin dato", 27.0% de las filas — venía de 16.1%; la diferencia es el formato nuevo). "% filas no vacías" renormaliza sobre el 73.0% restante — "sin clasificar" (`nr`, `Unrated`) y "no mapeado" sí son dato presente. La escala nueva ya está mapeada: `Teen Plus` y `Adults` empujaron a 13-15 (29.7% → 30.0%) y 18+ (18.6% → 19.9%); 16-17 bajó (14.4% → 13.2%) porque la escala nueva no tiene un escalón equivalente a `r`/`16`.*

**Conclusiones:** invariantes de siempre — teen (13-15) sigue siendo la franja más grande y la clasificada más barata (3.77), y el adulto se vende a poco más de la mitad de tasa que el family-safe (36% vs 63%). El "sin dato" vuelve a ser el más castigado (3.62, venía de 3.25 pero ahora incluye mucho inventario que antes sí venía clasificado): clasificar contenido sigue valiendo ~+25–30% frente a no hacerlo. El "no mapeado" que queda (2.2%) es el residuo de siempre: `dv-t`/`dv-g`/`dv-ma` de Televisa OB y Zeasn, `mpaa_r`, `movie-pg-13`.

# PARTE C — El inventario que monetiza (eCPM > 0)

**138,331 filas (17.1%) concentran el 52.6% del tráfico** — segundo corte fuera de la banda 51±0.1 en la que vivió el dataset durante cinco cortes. La partición vendido/muerto se movió y se quedó.

## Por país

| País | % tráfico monetizado | % filas monetizadas | eCPM pond. |
|---|---:|---:|---:|
| México | 59.4% | 18.9% | 3.21 |
| Argentina | 56.0% | 19.5% | 6.12 |
| Costa Rica | 40.6% | **29.8%** | 6.38 |
| Puerto Rico | 40.5% | 10.4% | **8.10** |
| Chile | 40.1% | 23.0% | 5.96 |
| Colombia | 32.5% | 14.2% | **5.60** |
| Perú | 30.2% | 13.9% | 4.66 |
| Rep. Dominicana | 18.9% | 6.2% | 4.96 |
| Ecuador | 17.3% | 6.0% | 5.73 |

**Colombia encadena cuatro cortes subiendo de precio** (4.51 → 4.97 → 5.36 → 5.60), aunque esta vez con la tasa plana (32.8% → 32.5%). **Chile completa cuatro bajadas (6.92 → 6.52 → 6.19 → 5.96) y cede el segundo puesto a Argentina** (6.12). México baja un poco en sell-through (60.2% → 59.4%) y sigue siendo el precio más bajo (3.21). Costa Rica y Puerto Rico pierden ~8pp de sell-through cada uno. Puerto Rico se mantiene como el precio top (8.10).

## Por publisher (share del tráfico monetizado)

| Publisher | Share | % propio monetizado | eCPM pond. |
|---|---:|---:|---:|
| Roku - oRTB | **15.8%** | 50.0% | 5.40 |
| TCL ADS - Springserve | 14.5% | 80.2% | 5.13 |
| Equativ | 8.9% | 82.9% | 2.59 |
| Televisa Univision via SpringServe | 8.2% | 83.9% | 2.26 |
| iion Pty Ltd | 8.0% | 37.7% | 5.49 |
| TCL ADs (APAC) | 7.7% | 75.2% | 5.58 |
| Coocaa (SKYWORTH) | 7.5% | 81.7% | 2.79 |
| TV Azteca - Springserve | **6.3%** | 73.4% | **5.83** |
| Televisa Univision via OB | 5.9% | **92.3%** | **1.27** |
| Vidaa | 4.4% | 83.4% | **1.35** |
| Zeasn (WhaleLive) | 4.0% | 94.5% | 3.06 |
| PML Digital | 2.0% | 70.3% | 2.39 |

Roku mantiene el #1 del tráfico monetizado, pero **su sell-through propio cayó de 60.4% a 50.0%** (su volumen crece más rápido que lo que vende). TCL Springserve sigue #2 con distancia. **Equativ sube al #3 (7.6% → 8.9%)** y **TV Azteca confirma el rebote (5.2% → 6.3%)** con el mejor precio con volumen del top (5.83). Las rutas Televisa (SpringServe + OB) suman 14.1% del tráfico vendido a 1.3–2.3 de eCPM: mucho volumen, poco cobro.

## Señales sobre el tráfico monetizado

- **Idioma:** español 43.7% del tráfico vendido a **4.49** vs inglés 19.8% a 3.37 — **prima del +34%**, estable (venía de +37%). Novedad: el "sin dato" saltó de 19.3% a **30.6% del tráfico vendido** (paga 4.06): es el idioma vaciado por el formato nuevo. Sumando la escritura nueva, español (`es` + `Spanish`) = 45.2%.
- **Live:** 48.2% del vendido — y **la prima del live desapareció** (4.03 vs 4.09 sin dato; venía de 4.35 vs 3.98).
- **Título:** la prima del título se invirtió (4.03 con título vs 4.12 sin) — el inventario sin título de Roku/ViX/Tubi es el que mejor se vende en México.
- **Outliers:** **nuevo máximo histórico: 194.3** ("blink and friends", TCL APAC / MovieArk Perú), seguido de los de siempre (135.3, 102.9, 100.3, 99.7, 99.2 — todos TCL APAC / MovieArk Perú) y un séptimo de iion (95.9, también Perú). La recomendación de excluir eCPM > ~30 en Perú sigue en pie y se refuerza.

---

## Síntesis

1. **La partición vendido/muerto se movió de verdad**: tras cinco cortes en 51.1±0.1%, v15 subió a 52.9% y v16 lo sostiene en **52.6%**. La mitad vendida del inventario creció, aunque el precio al que se vende sigue bajando (4.06, sexta bajada).
2. Dos historias en contra de la tendencia: **Colombia (cuarto corte subiendo: 5.60)** y **TV Azteca (6.3% del tráfico vendido a 5.83)**. Y una a favor: **Chile ya no es el mercado premium** — cuatro bajadas seguidas lo dejan detrás de Argentina.
3. Argumentos comerciales vigentes: español **+34%** sobre inglés, clasificar contenido vale ~+25–30%, family-safe el más líquido (63% sell-through), y el paquete de yield es anime (8.05, récord) + aventura (6.18) + infantil-familia (5.78). Las primas por live y por título, en cambio, desaparecieron en este corte.
4. **Este corte no sirve para serie temporal de rating ni de idioma** hasta aclarar el cambio de formato con la plataforma: el 27% de "sin rating" y el 31% de tráfico vendido "sin idioma" son artefactos del reporte, no del inventario. La cifra "oficial" de cada métrica debe llevar la etiqueta del consolidado del que salió (este: v10-a-v16).
