# Reporte — Normalización de género/rating y análisis del inventario monetizado (consolidado v10 a v17)

**Fuente:** `inventory-consolidado-v10-a-v17.csv` (959,442 filas, 380,355,807,040 requests; métricas de v17).
**Generado con:** `scripts/normalizar_monetizar.py` → `reporte-normalizacion-y-ecpm-v17-consolidado.json` e `inventory-consolidado-v10-a-v17-enriquecido.csv` (no versionado).

**Contexto:** octava versión del análisis. El eCPM ponderado global completa siete bajadas seguidas, ya casi plano (4.98 → 4.55 → 4.40 → 4.20 → 4.16 → 4.06 → **4.04**). **El tráfico monetizado retrocede a 50.7%** (52.9% en v15, 52.6% en v16): la salida de la banda 51±0.1 duró dos cortes.

**Cambio de formato en la fuente (segundo corte):** la escritura nueva (rating `All Ages`/`Teen`/`Teen Plus`/`Adults`/`Unrated`, género con mayúscula) ya es el 54% de las filas de v17. El diccionario de rating ampliado en v16 (equivalencias verificadas por cruce de títulos: `Teen` = `tv-pg`, `Teen Plus` = `tv-14`, `Adults` = `r`/`tv-ma`) la absorbe: "no mapeado" baja a 1.9%. Lo que sigue sin arreglo posible por diccionario es el vacío: "sin dato" de rating es el 25.7% de las filas (27.0% en v16, 16.1% antes del cambio) — mejora porque el formato nuevo ya trae rating en el 60% de sus filas (32% en v16).

**Advertencia sobre el consolidado:** el 10.6% de los requests del acumulado viene de llaves de cortes anteriores que ya no existen en v17 (duplicadas por el cambio de escritura), y entre ellas están los outliers peruanos de 194.3 y 135.3 que **v17 ya no trae**. Los precios de este reporte son los del consolidado; sobre v17 solo, el ponderado es 4.05 y el máximo 95.9.

---

# PARTE A — Género normalizado

86.8% de filas con al menos un género canónico (bajó de 88.0%: `Not Applicable` de género ya es el 6.3% de las filas, era 1.2% antes del cambio de formato); 261,228 multi-género. Distribución (multi-etiqueta; % sobre las filas con género útil):

| Género | % filas no vacías | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|
| drama | 29.3% | 3.56 | 45.5% |
| terror | 11.7% | 3.95 | 32.3% |
| comedia | 10.9% | 3.74 | 51.7% |
| documental | 10.8% | **5.88** | 40.3% |
| accion | 9.2% | 4.97 | 37.6% |
| thriller | 9.2% | 3.86 | 30.1% |
| romance | 6.3% | 4.25 | 42.0% |
| infantil-familia | 5.2% | 5.82 | 40.6% |
| otros/desconocido | 4.8% | 5.15 | 26.5% |
| crimen | 4.2% | 4.68 | 33.7% |
| aventura | 4.1% | 5.79 | 33.5% |
| entretenimiento | 4.1% | 4.74 | **64.3%** |
| deportes | 3.8% | **2.28** | **70.6%** |
| musica | 3.2% | 4.11 | 47.4% |
| misterio | 3.0% | 4.57 | 30.3% |
| sci-fi | 2.9% | 4.30 | 28.0% |
| fantasia | 2.7% | 4.14 | 25.3% |
| anime | 1.9% | **7.35** | 47.4% |
| noticias | 1.7% | 4.61 | 57.4% |
| reality | 1.4% | 5.29 | 50.7% |

**Conclusiones:** octava confirmación del patrón precio-plano / vendibilidad-dispersa, con un cambio en el podio: **anime rompe su racha de récords (6.16 → 7.49 → 7.84 → 8.05 → 7.35)** y **documental sube a 5.88** — es ahora el género con mejor yield entre los que tienen volumen (10.8% de las filas), por encima de infantil-familia (5.82) y aventura (5.79). Deportes sigue siendo el más barato con volumen (2.28) y a la vez el más fácil de vender (70.6%). El % de filas mapeables baja otro punto (88.0 → 86.8) por el vacío del formato nuevo, no por vocabulario: los `tokens_no_mapeados_top` son los de siempre (`short`, `tv series`, `culture`, `genre_*`).

# PARTE B — Rating en franjas de edad

| Franja | % filas | % filas no vacías | eCPM pond. (>0) | % monetizado |
|---|---:|---:|---:|---:|
| todos | 6.8% | 9.2% | 4.64 | **63.7%** |
| 7+ | 0.5% | 0.6% | 7.01 | 44.3% |
| 10+ | 9.6% | 12.9% | 4.66 | 50.5% |
| 13-15 | 22.0% | **29.7%** | 3.72 | 50.7% |
| 16-17 | 8.2% | 11.0% | 5.24 | 32.0% |
| 18+ / adulto | 16.7% | 22.5% | 4.35 | **34.9%** |
| sin clasificar | 8.7% | 11.7% | 3.73 | 44.7% |
| sin dato | **25.7%** | — | **3.64** | 56.4% |
| no mapeado | 1.9% | 2.5% | 3.16 | 61.9% |

*Aquí se conservan ambas columnas porque no son intercambiables: la distribución incluye la fila vacía ("sin dato", 25.7% de las filas). "% filas no vacías" renormaliza sobre el 74.3% restante — "sin clasificar" (`nr`, `Unrated`) y "no mapeado" sí son dato presente. La escala nueva ya pesa: `Adults` empuja el 18+ de 19.9% a 22.5% de las no vacías y `Teen Plus` sostiene el 13-15 en 29.7%; 16-17 sigue bajando (13.2% → 11.0%) porque la escala nueva no tiene escalón equivalente a `r`/`16`.*

**Conclusiones:** invariantes de siempre — teen (13-15) sigue siendo la franja más grande y la clasificada más barata (3.72), y el adulto se vende a poco más de la mitad de tasa que el family-safe (35% vs 64%). El "sin dato" sigue siendo el más castigado (3.64): clasificar contenido sigue valiendo ~+20–30%. El residuo "no mapeado" (1.9%) es el de siempre: `dv-t`/`dv-g`/`dv-ma` de Televisa OB y Zeasn, `mpaa_r`, `movie-pg-13`.

# PARTE C — El inventario que monetiza (eCPM > 0)

**167,986 filas (17.5%) concentran el 50.7% del tráfico** — de vuelta a la banda de 51 tras dos cortes en 52.6–52.9%. Parte de la bajada es aritmética del consolidado (las llaves viejas duplicadas pesan 10.6% de los requests y monetizan menos), pero sobre v17 solo la tasa también cae. La partición vendido/muerto no se movió de forma estructural.

## Por país

| País | % tráfico monetizado | % filas monetizadas | eCPM pond. |
|---|---:|---:|---:|
| México | 57.5% | 20.5% | 3.11 |
| Guatemala | 56.7% | 29.1% | 5.92 |
| Argentina | 55.3% | 19.0% | **6.25** |
| Costa Rica | 42.2% | **32.0%** | 6.20 |
| Chile | 35.9% | 22.9% | 6.10 |
| Perú | 31.5% | 15.0% | 4.88 |
| Colombia | 28.8% | 14.3% | **5.85** |
| Panamá | 24.8% | 7.5% | 2.12 |
| Ecuador | 15.1% | 5.3% | 6.15 |

**Colombia encadena cinco cortes subiendo de precio** (4.51 → 4.97 → 5.36 → 5.60 → 5.85), pero su sell-through en tráfico cae (32.5% → 28.8%): vende menos y más caro. **Chile rebota en precio (5.96 → 6.10) tras cuatro bajadas** pero también vende menos (40.1% → 35.9%). **Argentina toma el liderato de precio (6.25)** con el sell-through estable (56.0% → 55.3%). México baja sell-through (59.4% → 57.5%) y precio (3.21 → 3.11). Puerto Rico salió del top 9 por tráfico vendido; Guatemala entra con 56.7% de sell-through.

## Por publisher (share del tráfico monetizado)

| Publisher | Share | % propio monetizado | eCPM pond. |
|---|---:|---:|---:|
| Roku - oRTB | **15.7%** | 48.9% | 5.32 |
| TCL ADS - Springserve | 14.2% | 77.4% | 5.04 |
| iion Pty Ltd | **10.5%** | 38.3% | 5.66 |
| Televisa Univision via SpringServe | 8.4% | 82.9% | 2.24 |
| Equativ | 8.2% | 80.7% | 2.57 |
| TCL ADs (APAC) | 7.7% | 72.5% | 5.62 |
| Coocaa (SKYWORTH) | 6.7% | 78.5% | 2.89 |
| Televisa Univision via OB | 6.2% | **97.1%** | **1.10** |
| Zeasn (WhaleLive) | 4.7% | 96.6% | 2.81 |
| TV Azteca - Springserve | 4.4% | **51.6%** | **5.92** |
| Vidaa | 4.3% | 81.9% | **1.42** |
| PML Digital | 1.9% | 68.8% | 2.33 |

Roku mantiene el #1 del tráfico monetizado con el sell-through propio cayendo por segundo corte (60.4% → 50.0% → 48.9%). **iion sube al #3 (8.0% → 10.5%)** desplazando a Equativ. **TV Azteca se apaga otra vez** (6.3% → 4.4%; sell-through propio 73.4% → 51.6%). Las rutas Televisa (SpringServe + OB) suman 14.6% del tráfico vendido a 1.1–2.2 de eCPM.

## Señales sobre el tráfico monetizado

- **Idioma:** sumando las dos escrituras, español (`es` + `Spanish`) es el 43.7% del tráfico vendido a **~4.37** vs inglés (`en` + `English`) 20.3% a ~3.14 — **prima del +39%**, la más alta de la serie. El "sin dato" ya es el 33.1% del tráfico vendido (paga 4.23) — el idioma vaciado por el formato nuevo.
- **Live:** 49.6% del vendido, sin prima por segundo corte (3.96 vs 4.12 sin dato).
- **Título:** la prima del título reaparece tímida (4.08 con título vs 3.98 sin, +2.5%).
- **Outliers:** el consolidado sigue mostrando 194.3, 135.3, 102.9… (TCL APAC / MovieArk Perú), pero **ninguno está en v17**: son llaves viejas. En v17 el máximo es 95.9 (iion, Perú, "best mountains views") y el mayor de TCL APAC es 82.8 (México, "chicken stew season 1"). La recomendación de excluir eCPM > ~30 en Perú sigue en pie.

---

## Síntesis

1. **La partición vendido/muerto volvió a la banda de 51** (50.7%): la subida de v15–v16 no era estructural. El precio global está ya prácticamente plano (4.06 → 4.04).
2. Tres historias de precio: **Colombia quinto corte subiendo (5.85)**, **Chile rebota (6.10)** tras cuatro bajadas y **Argentina toma el liderato (6.25)**. Todas con el sell-through en tráfico cayendo: se vende menos y más caro fuera de México.
3. Argumentos comerciales vigentes: español **+39%** sobre inglés (máximo de la serie), clasificar contenido vale ~+20–30%, family-safe el más líquido (64% sell-through), y el paquete de yield cambia de cara: **documental (5.88) e infantil-familia (5.82) al frente con volumen; anime (7.35) sigue siendo el más caro pero perdió el récord**.
4. **Leer tráfico y precio sobre el corte, no sobre el acumulado**: el 10.6% de requests de llaves viejas (y los outliers de 3 dígitos) ya no describen la ventana v17. La cifra "oficial" de cada métrica debe llevar la etiqueta del consolidado del que salió (este: v10-a-v17) y, para tráfico, preferir v17 solo.
